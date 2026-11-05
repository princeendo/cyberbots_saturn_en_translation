"""EXP-0048: the END-011 rule on every roster ending, as a dry run.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/check_all.py \\
        local/ref003/cybotsu-maincpu.bin [--out research/experiments/EXP-0048/rule.json]

For each list 0-5, applies ``tools.text.ending_timing.retime`` to a copy of
the untouched `END.BIN` with that list's pairing (rows and codes are not
built: the rule needs only the English glyph cells and the script). It
reports, numbers only:

- every cued box's window, typing and hold, and the smallest hold;
- every box that ends on waits or on the scene end: its Japanese and
  English frames to the next event, and whether the difference is absorbed
  by the run before it (``absorbs``) or left over (which moves the next
  scene and its music by that much).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.reference.cybots_text import decode, long, read_record
from tools.text import dialogue, ending, ending_timing

NAMES = ["jin", "santana", "mary", "arieta", "gawaine", "baomao"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us = args.us.read_bytes()
    untouched = bytes(dialogue.checked("END.BIN"))
    lines = ending.end_lines()
    box_lines = ending.record_lines(untouched, lines)
    jp_codes = set(kanji.read_code_table(untouched, ending.CODE_TABLE)) - {
        dialogue.SPACE_CODE
    }
    japanese = {
        box: sum(
            1
            for k in box_lines[box]
            for i in range(0, lines[k][1] - 1, 2)
            if int.from_bytes(untouched[lines[k][0] + i : lines[k][0] + i + 2], "big")
            in jp_codes
        )
        for box in range(ending.BOXES)
        if box_lines[box]
    }
    surfaces = json.loads(ending.SURFACES.read_text())["lists"]
    report: list[dict[str, Any]] = []
    for n, name in enumerate(NAMES):
        pairing = json.loads(
            Path(f"data/translations/{name}_ending_pairing.json").read_text()
        )
        cells = {}
        for u in pairing["units"]:
            slot = u.get("arcade_slot")
            if slot is None:
                continue
            text = decode(read_record(us, long(us, dialogue.EN_TABLE + 4 * slot)).codes)
            cells[u["box"]] = dialogue.cells_of(dialogue.wrap(text))
        end = bytearray(untouched)
        try:
            out = ending_timing.retime(end, n, surfaces[n], cells, japanese)
        except ValueError as error:
            report.append({"list": n, "error": str(error)})
            print(n, "ERROR", error)
            continue
        holds = [b["hold"] for b in out.boxes if b["hold"] is not None]
        absorbed = {b["box"] for b in out.boxes if b.get("absorbs")}
        left = []
        for w in out.waits:
            diff = w["japanese_frames"] - w["english_frames"]
            if diff:
                left.append({"box": w["box"], "difference": diff})
        entry = {
            "list": n,
            "cued_boxes": out.boxes,
            "waits": out.waits,
            "smallest_hold": min(holds) if holds else None,
            "runs_absorbing": sorted(absorbed),
            "differences": left,
            "changes": len(out.changes),
        }
        report.append(entry)
        print(
            n,
            "smallest hold",
            entry["smallest_hold"],
            "differences",
            left,
            "absorbed by runs ending",
            sorted(absorbed),
        )
    if args.out:
        args.out.write_text(json.dumps({"lists": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
