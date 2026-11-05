"""EXP-0039: did each `END.BIN` box opened in a run draw its predicted cells?

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0039/check_cells.py RUN

A debug harness; it never ships. It prints JSON with no game text. For
every `END.BIN` box opened in ``RUN`` (``ending_probe.py`` output, record
table ``0x060817B4``), the predicted cells are one per character with a code
in `END.BIN`'s code table (file offset ``0x26EAC``), except the full-width
space, from the font `SE.DAT` loads (its copy of `KANJI.BIN`, D-035). The
longest run of predicted cells found at any starting cell in a cell dump
taken while the box is open is reported (``EXP-0037/m5_glyphs.py``'s
method).
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
CENSUS = Path("data/text/script_census.json")
BASE = 0x06060000
TABLE = 0x060817B4
CODE_TABLE = 0x26EAC
CELL = 0x80


def main(run: Path) -> int:
    end = (FILES / "END.BIN").read_bytes()
    codes = kanji.read_code_table(end, CODE_TABLE)
    font = kanji.decode((FILES / "SE.DAT").read_bytes()[0x40000:0x68000])
    census = json.loads(CENSUS.read_text())
    table = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0][
        "table"
    ]
    by_offset = {BASE + row[0]: n for n, row in enumerate(table)}

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    def box_lines(box: int) -> list[int]:
        found, entry = [], u32(TABLE + 4 * box) + 8
        while True:
            found.append(by_offset[u32(entry)])
            if end[entry + 4 - BASE : entry + 6 - BASE] != b"\xff\xff":
                return found
            entry += 8

    def want(box: int) -> list[bytes]:
        cells = []
        for line in box_lines(box):
            off, n = table[line][0], table[line][1]
            text = end[off : off + n]
            for k in range(0, n - 1, 2):
                code = int.from_bytes(text[k : k + 2], "big")
                if code in codes and code != SPACE_CODE:
                    cells.append(font[codes.index(code)])
        return cells

    dumps = sorted((int(p.stem[1:]), p) for p in run.glob("c*.bin"))
    route = json.loads((run / "route.json").read_text())
    opened: dict[int, int] = {}
    windows: list[tuple[int, int, int]] = []
    for b in route["boxes"]:
        if b["table"] != f"0x{TABLE:08X}":
            continue
        word, frame = int(b["word"], 16), b["frame"]
        if word & 0x8000:
            if word & 0x7FFF in opened:
                windows.append((word & 0x7FFF, opened.pop(word & 0x7FFF), frame))
        else:
            opened[word] = frame
    windows += [(b, f, 1 << 30) for b, f in opened.items()]
    report: list[dict[str, Any]] = []
    for box, start, stop in sorted(windows, key=lambda w: w[1]):
        cells = want(box)
        top = 0
        for frame, path in dumps:
            if not start < frame < stop:
                continue
            data = path.read_bytes()
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
        report.append(
            {
                "box": box,
                "open": start,
                "lines": box_lines(box),
                "cells": len(cells),
                "matched": top,
            }
        )
    summary = {
        "boxes": len(report),
        "full": sum(r["matched"] == r["cells"] for r in report),
        "short": [r["box"] for r in report if r["matched"] < r["cells"]],
    }
    print(json.dumps({"summary": summary, "boxes": report}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
