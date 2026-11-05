"""EXP-0037: which ending characters the M5 image draws with a replaced glyph.

Run from the repository root, after ``ending_route.py`` has run the route on
the untouched image (``UNTOUCHED``) and on the M5 image (``M5``):

    ./invenv.sh python research/experiments/EXP-0037/m5_glyphs.py \\
        UNTOUCHED M5 build/re008/roster

A debug harness; it never ships. It prints JSON and holds no game text.

- **Prediction:** for every `END.BIN` box the untouched run opened (record
  table ``0x060817B4``), each line's characters are looked up in
  `END.BIN`'s code table (file offset ``0x26EAC``, the same 1,222 codes as
  `STG0AS.BIN`'s original table). A character whose glyph index is one of
  the build's ``kanji_glyphs`` (``changes.json``: the `KANJI.BIN` cells it
  replaced with pair glyphs) is predicted to look different on the M5 image.
- **Observation:** each run's glyph-cell dumps (``cNNNNN.bin``, 60 cells at
  ``0x060FE200``) taken while the box was open are compared with the box's
  predicted cells: one cell per character with a table code, except the
  full-width space ``0x8140`` (``EXP-0030/japanese_check.py``), from that
  image's `KANJI.BIN` (untouched, or the build's). The best run of matching
  cells at any starting cell is reported (a speaker-name box can hold the
  first cells). Boxes are matched by order of opening, not by frame: the M5
  image's English story scenes before the fight change the timing.
- **Control:** the M5 run is also matched against the untouched cells; only
  the boxes with predicted characters should fall short there.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.text.dialogue import SPACE_CODE

FILES = Path("local/extracted/saturn_jp")
END = FILES / "END.BIN"
CENSUS = Path("data/text/script_census.json")
BASE = 0x06060000
TABLE = 0x060817B4
CODE_TABLE = 0x26EAC
CELL = 0x80


def opened(run: Path) -> list[dict[str, int]]:
    """Each END.BIN box with the frames it was opened and closed."""
    boxes = json.loads((run / "route.json").read_text())["boxes"]
    out: list[dict[str, int]] = []
    open_at: dict[int, int] = {}
    for b in boxes:
        if b["table"] != f"0x{TABLE:08X}":
            continue
        word, frame = int(b["word"], 16), b["frame"]
        if word & 0x8000:
            box = word & 0x7FFF
            if box in open_at:
                out.append({"box": box, "open": open_at.pop(box), "close": frame})
        else:
            open_at[word] = frame
    out += [{"box": b, "open": f, "close": 1 << 30} for b, f in open_at.items()]
    return sorted(out, key=lambda x: (x["open"], x["box"]))


def main(untouched: Path, m5: Path, build: Path) -> int:
    end = END.read_bytes()
    codes = kanji.read_code_table(end, CODE_TABLE)
    replaced = set(json.loads((build / "changes.json").read_text())["kanji_glyphs"])
    census = json.loads(CENSUS.read_text())
    lines = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0][
        "table"
    ]
    by_offset = {BASE + off: i for i, (off, *_rest) in enumerate(lines)}

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    def box_lines(box: int) -> list[int]:
        found, entry = [], u32(TABLE + 4 * box) + 8
        while True:
            found.append(by_offset[u32(entry)])
            if (
                int.from_bytes(end[entry + 4 - BASE : entry + 6 - BASE], "big")
                != 0xFFFF
            ):
                return found
            entry += 8

    original = kanji.decode((FILES / "KANJI.BIN").read_bytes())
    built = kanji.decode((build / "KANJI.BIN").read_bytes())

    def want(box: int, font: list[bytes]) -> list[bytes]:
        cells = []
        for line in box_lines(box):
            off, n = lines[line][0], lines[line][1]
            text = end[off : off + n]
            for k in range(0, n - 1, 2):
                code = int.from_bytes(text[k : k + 2], "big")
                if code in codes and code != SPACE_CODE:
                    cells.append(font[codes.index(code)])
        return cells

    def best(run: Path, start: int, stop: int, cells: list[bytes]) -> int:
        top = 0
        for p in run.glob("c*.bin"):
            if not start < int(p.stem[1:]) < stop:
                continue
            data = p.read_bytes()
            have = [data[i * CELL : (i + 1) * CELL] for i in range(len(data) // CELL)]
            for first in range(len(have)):
                n = 0
                while (
                    n < len(cells)
                    and first + n < len(have)
                    and have[first + n] == cells[n]
                ):
                    n += 1
                top = max(top, n)
        return top

    a, b = opened(untouched), opened(m5)
    report: list[dict[str, Any]] = []
    for x, y in zip(a, b, strict=False):
        predicted = []
        for line in box_lines(x["box"]):
            off, n = lines[line][0], lines[line][1]
            text = end[off : off + n]
            for k in range(0, n - 1, 2):
                code = int.from_bytes(text[k : k + 2], "big")
                if code in codes and codes.index(code) in replaced:
                    predicted.append({"line": line, "char": k // 2})
        mine, theirs = want(x["box"], original), want(x["box"], built)
        report.append(
            {
                "box": x["box"],
                "same_box_in_m5_run": x["box"] == y["box"],
                "lines": box_lines(x["box"]),
                "cells": len(mine),
                "predicted": predicted,
                "untouched_run": best(untouched, x["open"], x["close"], mine),
                "m5_run": best(m5, y["open"], y["close"], theirs),
                "m5_run_vs_untouched_cells": best(m5, y["open"], y["close"], mine),
            }
        )
    summary = {
        "boxes": len(report),
        "boxes_m5_run": len(b),
        "predicted_chars": sum(len(r["predicted"]) for r in report),
        "untouched_full": sum(r["untouched_run"] == r["cells"] for r in report),
        "m5_full": sum(r["m5_run"] == r["cells"] for r in report),
        "m5_short_of_untouched_cells": [
            r["box"] for r in report if r["m5_run_vs_untouched_cells"] < r["cells"]
        ],
    }
    print(json.dumps({"summary": summary, "boxes": report}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
