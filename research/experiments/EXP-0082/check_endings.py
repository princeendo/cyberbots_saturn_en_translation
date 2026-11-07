"""EXP-0082: the Saturn-only endings (lists 6-8) drawn by the built image.

Copied from ``research/experiments/EXP-0050/check_others.py`` (commit
``04c6709``) with the build and the runs as arguments and the sacrifice count
left out. Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0082/check_endings.py BUILD \\
        RUNS [--out OUT.json]

``RUNS/listN`` (N = 6, 7, 8, or ``--lists``) are ``EXP-0042/probe.py`` runs of the built
image from the END-001 checkpoint with the ending number set to N, cells
dumped every 5 frames. Lists 6-8 draw their ending text with `KANJI.BIN`
(EXP-0050), so each box they open is expected to draw, cell for cell:

- a box the build wrote (the new translation, and the names 601/605): its
  predicted cells (``ending_prediction.json``); for lists 0-5 (drawn with
  `SE.DAT`) every box is the build's, so the same check applies;
- any other box: for each code of its lines in `END.BIN`'s table (less the
  full-width space and two ASCII spaces), that code's glyph in the built
  `KANJI.BIN`.

A box passes when its cells lead some dump between its opening and the later
of its close word and the next box's opening (``EXP-0050`` used the close
word only, which can come before the last cells are typed). Numbers only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.text import dialogue, ending

TABLE = "0x060817B4"
ASCII_SPACES = 0x2020


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("build", type=Path)
    p.add_argument("runs", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--lists", type=int, nargs="+", default=[6, 7, 8])
    a = p.parse_args()
    end = bytes(dialogue.checked("END.BIN"))
    codes = kanji.read_code_table(end, ending.CODE_TABLE)
    font = kanji.decode((a.build / "KANJI.BIN").read_bytes())
    lines = ending.end_lines()
    box_lines = ending.record_lines(end, lines)
    pred = {
        q["box"]: q["cells"]
        for q in json.loads((a.build / "ending_prediction.json").read_text())
    }

    def want(box: int) -> list[str]:
        if box in pred:
            return list(pred[box])
        out = []
        for k in box_lines[box]:
            off, n = lines[k]
            for i in range(0, n - 1, 2):
                code = int.from_bytes(end[off + i : off + i + 2], "big")
                if code in codes and code not in (dialogue.SPACE_CODE, ASCII_SPACES):
                    out.append(hashlib.sha256(font[codes.index(code)]).hexdigest())
        return out

    report: list[dict[str, Any]] = []
    for n in a.lists:
        run = a.runs / f"list{n}"
        route = json.loads((run / "route.json").read_text())
        events = [
            (b["frame"], int(b["word"], 16))
            for b in route["boxes"]
            if b["table"] == TABLE
        ]
        dumps = sorted((int(q.stem[1:]), q) for q in run.glob("c*.bin"))
        last = dumps[-1][0] if dumps else 0
        boxes = []
        for i, (frame, word) in enumerate(events):
            if word & 0x8000 or frame > last:
                continue
            # The window ends at the later of the box's close word and the next
            # box's opening: a close word can come before the last cells are
            # typed (box 879, EXP-0082), and a speaker name's next box opens
            # while the name is still drawn (601, 605). With no close word,
            # 600 frames (as EXP-0050).
            close = next((f for f, w in events[i + 1 :] if w == (word | 0x8000)), None)
            nxt = next((f for f, w in events[i + 1 :] if not w & 0x8000), None)
            stop = max(close or frame + 600, nxt or 0)
            cells = want(word)
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
                    "built": word in pred,
                    "cells": len(cells),
                    "matched": top,
                }
            )
        report.append(
            {
                "list": n,
                "boxes_opened": len(boxes),
                "full": sum(b["matched"] == b["cells"] for b in boxes),
                "short": [b["box"] for b in boxes if b["matched"] < b["cells"]],
                "not_built": sorted({b["box"] for b in boxes if not b["built"]}),
                "boxes": boxes,
            }
        )
        print(n, {k: v for k, v in report[-1].items() if k != "boxes"})
    if a.out:
        a.out.write_text(json.dumps({"lists": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
