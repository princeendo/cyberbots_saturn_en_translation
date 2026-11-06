"""EXP-0050: the Saturn-only endings (lists 6-8) on the M8 image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/check_others.py BUILD

Lists 6-8 draw their ending text with `KANJI.BIN`, not `SE.DAT` (EXP-0050).
So each box they open is expected to draw, cell for cell:

- a box the build translated (601, 605): the build's predicted cells;
- any other box: for each code of its lines in `END.BIN`'s table (less the
  full-width space), that code's glyph in the built `KANJI.BIN`.

It reports, per list, the boxes drawn in full and, for every box, how many
of its codes are story sacrifices (M5's 152 and the 153rd from END-023),
whose glyphs the gates approved replacing. Numbers only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.text import dialogue, ending

TABLE = "0x060817B4"
ASCII_SPACES = 0x2020  # two half-width spaces: drawn as no glyph (EXP-0050)


def main(build: Path) -> int:
    end = bytes(dialogue.checked("END.BIN"))
    codes = kanji.read_code_table(end, ending.CODE_TABLE)
    font = kanji.decode((build / "KANJI.BIN").read_bytes())
    lines = ending.end_lines()
    box_lines = ending.record_lines(end, lines)
    pred = {
        p["box"]: p["cells"]
        for p in json.loads((build / "ending_prediction.json").read_text())
    }
    sacrificed = {
        int(s["code"], 16)
        for s in json.loads((build.parent / "rec-a" / "jin_ending.json").read_text())[
            "kanji_sacrificed"
        ]
    }
    for name in ("jin", "santana", "mary", "arieta", "gawaine", "baomao"):
        record = json.loads(Path(f"data/translations/{name}_story.json").read_text())
        sacrificed |= {int(s["code"], 16) for s in record["summary"]["sacrificed"]}

    def want(box: int) -> tuple[list[str], int]:
        if box in pred:
            return list(pred[box]), 0
        out, hit = [], 0
        for k in box_lines[box]:
            off, n = lines[k]
            for i in range(0, n - 1, 2):
                code = int.from_bytes(end[off + i : off + i + 2], "big")
                if code in codes and code not in (dialogue.SPACE_CODE, ASCII_SPACES):
                    out.append(hashlib.sha256(font[codes.index(code)]).hexdigest())
                    hit += code in sacrificed
        return out, hit

    report: list[dict[str, Any]] = []
    for n in (6, 7, 8):
        run = Path(f"local/end023/list{n}")
        route = json.loads((run / "route.json").read_text())
        events = [
            (b["frame"], int(b["word"], 16))
            for b in route["boxes"]
            if b["table"] == TABLE
        ]
        dumps = sorted((int(p.stem[1:]), p) for p in run.glob("c*.bin"))
        last = dumps[-1][0] if dumps else 0
        boxes = []
        for i, (frame, word) in enumerate(events):
            if word & 0x8000:
                continue
            close = next((f for f, w in events[i + 1 :] if w == (word | 0x8000)), None)
            stop = close or frame + 600
            if frame > last:
                continue
            cells, hit = want(word)
            top = 0
            for f, path in dumps:
                if not frame < f < stop:
                    continue
                data = path.read_bytes()
                have = [
                    hashlib.sha256(data[k * 128 : (k + 1) * 128]).hexdigest()
                    for k in range(60)
                ]
                for s in range(60):
                    m = 0
                    while m < len(cells) and s + m < 60 and have[s + m] == cells[m]:
                        m += 1
                    top = max(top, m)
            boxes.append(
                {
                    "box": word,
                    "open": frame,
                    "translated": word in pred,
                    "cells": len(cells),
                    "matched": top,
                    "sacrificed_codes": hit,
                }
            )
        report.append(
            {
                "list": n,
                "boxes_in_dumps": len(boxes),
                "full": sum(b["matched"] == b["cells"] for b in boxes),
                "short": [b["box"] for b in boxes if b["matched"] < b["cells"]],
                "with_sacrificed_codes": [
                    b["box"] for b in boxes if b["sacrificed_codes"]
                ],
                "boxes": boxes,
            }
        )
        print(n, {k: v for k, v in report[-1].items() if k != "boxes"})
    print(json.dumps({"lists": report}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
