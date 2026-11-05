"""EXP-0049: what all six roster endings' English needs, together (END-022).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0049/capacity_all.py \\
        local/ref003/cybotsu-maincpu.bin [--out OUT.json]

Static; numbers only. Extends ``EXP-0041/capacity.py`` from Jin's ending to
lists 0-5 at once, as one build would place them:

- **Units.** Every box with an arcade slot in the six pairing files, once
  (boxes shared by two endings have one record). Box 608 is measured with
  either choice the gate has: the slot at the same place (615) or the slot
  with the same Japanese (617).
- **Rows and cells.** Each slot's `cybotsu` English wrapped as the
  compiler does; limits 3 rows and 60 glyph cells a box; each row against
  the widest Saturn line of the same kind of box (``surface_of``).
- **Pairs and codes.** The distinct pairs of all rows (as is, and with the
  half-cell indent across all of them), against `END.BIN`'s code table:
  - codes no line uses (the story's rule) plus the new codes the table's
    last row holds;
  - codes no line that stays Japanese on screen uses. The lines that stay
    are those of every box lists 6-8 are seen to open
    (``data/text/ending_surfaces_others.json``), less the boxes this build
    translates.
- **Room.** The row bytes against the free lines:
  - own: lines only English boxes (or never-shown boxes) point to;
  - unshown: lines no box any of lists 0-8 is seen to open points to.

  The unshown room is split by whether `EXP-0042`'s marker test covered
  it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji, pairs
from tools.reference.cybots_text import decode, long, read_record
from tools.text import dialogue, ending
from tools.text.ending_pairing import surface_of

NAMES = ["jin", "santana", "mary", "arieta", "gawaine", "baomao"]
SURFACES = Path("data/text/ending_surfaces.json")
OTHERS = Path("data/text/ending_surfaces_others.json")
ROOM_TESTED = Path("research/experiments/EXP-0042/room.json")
BOX_608 = {"place (615)": 615, "same Japanese (617)": 617}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us = args.us.read_bytes()
    end = bytes(dialogue.checked("END.BIN"))
    lines = ending.end_lines()
    text = [end[off : off + n] for off, n in lines]
    box_lines = ending.record_lines(end, lines)

    def header(box: int) -> bytes:
        rec = int.from_bytes(
            end[
                ending.RECORDS - ending.BASE + 4 * box : ending.RECORDS
                - ending.BASE
                + 4 * box
                + 4
            ],
            "big",
        )
        return end[rec - ending.BASE : rec - ending.BASE + 8]

    roster = json.loads(SURFACES.read_text())["lists"]
    others = json.loads(OTHERS.read_text())["lists"]
    shown_roster = {o["box"] for e in roster for o in e["openings"]}
    shown_others = {o["box"] for e in others for o in e["openings"]}

    slot_of: dict[int, int] = {}
    lists_of: dict[int, set[int]] = {}
    for n, name in enumerate(NAMES):
        pairing = json.loads(
            Path(f"data/translations/{name}_ending_pairing.json").read_text()
        )
        for u in pairing["units"]:
            if u.get("arcade_slot") is None:
                continue
            if slot_of.setdefault(u["box"], u["arcade_slot"]) != u["arcade_slot"]:
                raise SystemExit(f"box {u['box']}: two slots")
            lists_of.setdefault(u["box"], set()).add(n)
    ours = set(slot_of)

    # Widest Saturn line per kind of box, over the roster's shown boxes.
    widest: dict[str, int] = {}
    for box in shown_roster:
        kind = surface_of(header(box))
        for k in box_lines[box]:
            widest[kind] = max(widest.get(kind, 0), len(text[k]) // 2)

    table = kanji.read_code_table(end, ending.CODE_TABLE)
    texts = dialogue.text_lines()
    unused = pairs.unused_codes(table, texts)
    last_row_used = len(table) - (kanji.TABLE_ROWS - 1) * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1
    staying_boxes = (shown_others - ours) | {1072}
    staying_lines = {k for b in staying_boxes for k in box_lines.get(b, [])}
    used_staying: set[int] = set()
    for k in staying_lines:
        used_staying |= dialogue.codes_in(text[k])
    free_staying = [
        c for c in table if c not in used_staying and c != dialogue.SPACE_CODE
    ]

    # Room.
    shown_any = shown_roster | shown_others
    own, unshown = ending.free_lines(box_lines, shown_any, ours)
    tested = json.loads(ROOM_TESTED.read_text())["spans"]
    tested_spans = [(int(s, 16), int(e, 16)) for s, e in tested]

    def size(k: int) -> int:
        return (lines[k][1] + 1 + 3) & ~3

    unshown_tested = sum(
        size(k) for k in unshown if any(s <= lines[k][0] < e for s, e in tested_spans)
    )
    room = {
        "own_lines": len(own),
        "own_bytes": sum(size(k) for k in own),
        "unshown_lines": len(unshown),
        "unshown_bytes": sum(size(k) for k in unshown),
        "unshown_bytes_marker_tested": unshown_tested,
        "lines_shown_by_lists_6_8": len(
            {k for b in shown_others for k in box_lines.get(b, [])}
        ),
        "exp0042_room_lines_now_seen_shown": sorted(
            k
            for k in {k for b in shown_any for k in box_lines.get(b, [])}
            if any(s <= lines[k][0] < e for s, e in tested_spans)
        ),
    }

    variants: dict[str, Any] = {}
    for label, slot608 in BOX_608.items():
        slots = dict(slot_of)
        if 608 in slots:
            slots[608] = slot608
        boxes = []
        for box in sorted(slots, key=lambda b: (min(lists_of[b]), b)):
            record = read_record(us, long(us, dialogue.EN_TABLE + 4 * slots[box]))
            rows = dialogue.wrap(decode(record.codes))
            boxes.append(
                dialogue.Box(box, slots[box], tuple(box_lines[box]), tuple(rows))
            )

        def layout(group: list[dialogue.Box]) -> dict[str, Any]:
            per_box = []
            for b in group:
                kind = surface_of(header(b.box))
                cells = [len(pairs.split_pairs(r)) for r in b.rows]
                per_box.append(
                    {
                        "box": b.box,
                        "lists": sorted(lists_of[b.box]),
                        "kind": kind,
                        "rows": len(b.rows),
                        "row_cells": cells,
                        "glyph_cells": dialogue.cells_of(b.rows),
                        "widest_saturn_line": widest.get(kind),
                        "rows_wider": sum(c > widest.get(kind, 0) for c in cells),
                    }
                )
            wanted = dialogue.wanted_pairs(group)
            return {
                "boxes": per_box,
                "max_rows": max(p["rows"] for p in per_box),
                "max_glyph_cells": max(p["glyph_cells"] for p in per_box),
                "over_limits": [
                    p["box"]
                    for p in per_box
                    if p["rows"] > dialogue.MAX_ROWS
                    or p["glyph_cells"] > dialogue.MAX_CELLS
                ],
                "boxes_with_wider_rows": [p["box"] for p in per_box if p["rows_wider"]],
                "pairs": len(wanted),
                "row_bytes": sum(
                    len(dialogue.row_bytes(r, dict.fromkeys(wanted, 1)))
                    for b in group
                    for r in b.rows
                ),
            }

        plain = layout(boxes)
        shifted = iter(dialogue.shift_rows([r for b in boxes for r in b.rows]))
        indented = layout(
            [
                dialogue.Box(
                    b.box, b.slot, b.lines, tuple(next(shifted) for _ in b.rows)
                )
                for b in boxes
            ]
        )
        variants[label] = {"as_is": plain, "indent": indented}

    result: dict[str, Any] = {
        "sources": {
            "cybotsu_program_sha256": hashlib.sha256(us).hexdigest(),
            "END.BIN": hashlib.sha256(end).hexdigest(),
            "ending_surfaces_sha256": hashlib.sha256(SURFACES.read_bytes()).hexdigest(),
            "ending_surfaces_others_sha256": hashlib.sha256(
                OTHERS.read_bytes()
            ).hexdigest(),
        },
        "english_boxes": len(ours),
        "boxes_in_more_than_one_list": sorted(b for b in ours if len(lists_of[b]) > 1),
        "widest_saturn_line": widest,
        "codes": {
            "table": len(table),
            "unused_by_any_line": len(unused),
            "new_in_last_row": new_slots,
            "story_rule_total": len(unused) + new_slots,
            "staying_boxes": sorted(staying_boxes),
            "free_of_staying_lines": len(free_staying),
            "free_of_staying_lines_plus_new": len(free_staying) + new_slots,
        },
        "room": room,
        "variants_608": variants,
    }
    summary = {k: v for k, v in result.items() if k not in ("variants_608",)} | {
        label: {
            mode: {k: v for k, v in m.items() if k != "boxes"} for mode, m in v.items()
        }
        for label, v in variants.items()
    }
    summary.pop("codes")
    print(
        json.dumps(
            summary
            | {
                "codes": {
                    k: v for k, v in result["codes"].items() if k != "staying_boxes"
                }
            },
            indent=1,
        )
    )
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
