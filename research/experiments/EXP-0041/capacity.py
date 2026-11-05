"""EXP-0041: what Jin's ending English needs in rows, cells, codes and room.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0041/capacity.py \\
        local/ref003/cybotsu-maincpu.bin \\
        [--out research/experiments/EXP-0041/capacity.json]

Static; numbers only. CAP-001's measures (``EXP-0034``), for the dialogue
units of ``data/translations/jin_ending_pairing.json``, against what
END-002 and END-003 found for the ending (D-035, D-036):

- **Rows and cells.** Each slot's `cybotsu` English, re-flowed as the
  compiler does (``tools.text.dialogue.wrap``: rows of at most 32
  characters), as is and with the half-cell indent (``shift_rows``, the
  user's CAP-001 choice). Limits: 3 rows a record, 60 glyph cells a box
  (D-020, D-023; the ending draws through the same cells at ``0x060FE200``,
  D-035). Each row's cells are also compared with the widest Saturn line
  that surface shows (story box, narration, caption), the width known to
  fit on screen.
- **Codes.** The pairs the English needs (``wanted_pairs``), against
  `END.BIN`'s code table (file ``0x26EAC``; the ending's font is `SE.DAT`'s
  copy of `KANJI.BIN`, D-035, so the story's codes and glyphs are not
  shared). Free codes are counted two ways: codes no line of the shared
  table uses (the story's rule, D-023), and codes no line `END.BIN` shows
  uses (the boxes of every list's posted scenes, ``ending_posts.json``).
  New codes fit in the table's last row as in the compiler.
- **Room.** The row bytes (``row_bytes``: 2 bytes a cell, NUL, 4-byte
  aligned) against the bytes of lines in `END.BIN`'s copy that no ending
  box shows.
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
from tools.text.dialogue import (
    MAX_CELLS,
    MAX_ROWS,
    SPACE_CODE,
    Box,
    cells_of,
    codes_in,
    shift_rows,
    wanted_pairs,
    wrap,
)

EN_TABLE = 0x0B33AA
END_TABLE = 0x26EAC  # END.BIN's code table (D-035)
FILES = Path("local/extracted/saturn_jp")
PAIRING = Path("data/translations/jin_ending_pairing.json")
POSTS = Path("data/text/ending_posts.json")
CENSUS = Path("data/text/script_census.json")


def row_cells(row: str) -> int:
    return len(pairs.split_pairs(row))


def row_size(row: str) -> int:
    n = 2 * row_cells(row) + 1
    return n + (-n % 4)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us = args.us.read_bytes()
    end = (FILES / "END.BIN").read_bytes()
    stg = (FILES / "STG0AS.BIN").read_bytes()
    census = json.loads(CENSUS.read_text())
    table = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0][
        "table"
    ]
    lines = [end[off : off + n] for off, n, *_ in table]
    pairing = json.loads(PAIRING.read_text())
    units = [u for u in pairing["units"] if u.get("arcade_slot") is not None]

    boxes: list[Box] = []
    surface_of: dict[int, str] = {}
    for u in units:
        record = read_record(us, long(us, EN_TABLE + 4 * u["arcade_slot"]))
        rows = wrap(decode(record.codes))
        boxes.append(
            Box(u["box"], u["arcade_slot"], tuple(u["saturn_lines"]), tuple(rows))
        )
        surface_of[u["box"]] = u["surface"]
    widest: dict[str, int] = {}
    for u in units:
        for n in u["saturn_lines"]:
            widest[u["surface"]] = max(widest.get(u["surface"], 0), len(lines[n]) // 2)

    def layout(group: list[Box]) -> dict[str, Any]:
        per_box: list[dict[str, Any]] = []
        for b in group:
            cells = [row_cells(r) for r in b.rows]
            per_box.append(
                {
                    "box": b.box,
                    "surface": surface_of[b.box],
                    "rows": len(b.rows),
                    "row_cells": cells,
                    "glyph_cells": cells_of(b.rows),
                    "widest_saturn_line_cells": widest[surface_of[b.box]],
                    "rows_wider_than_saturn": sum(
                        c > widest[surface_of[b.box]] for c in cells
                    ),
                }
            )
        wanted = wanted_pairs(group)
        return {
            "boxes": per_box,
            "max_rows": max(p["rows"] for p in per_box),
            "max_glyph_cells": max(p["glyph_cells"] for p in per_box),
            "over_limits": [
                p["box"]
                for p in per_box
                if p["rows"] > MAX_ROWS or p["glyph_cells"] > MAX_CELLS
            ],
            "rows_wider_than_saturn": [
                p["box"] for p in per_box if p["rows_wider_than_saturn"]
            ],
            "pairs": len(wanted),
            "row_bytes": sum(row_size(r) for b in group for r in b.rows),
        }

    plain = layout(boxes)
    shifted_rows = iter(shift_rows([r for b in boxes for r in b.rows]))
    indented = layout(
        [
            Box(b.box, b.slot, b.lines, tuple(next(shifted_rows) for _ in b.rows))
            for b in boxes
        ]
    )

    end_codes = kanji.read_code_table(end, END_TABLE)
    story_codes = kanji.read_code_table(stg)
    posts = json.loads(POSTS.read_text())
    shown: set[int] = set()
    jin: set[int] = set()
    for lst in posts["lists"]:
        for post in lst["posts"]:
            for b in post["boxes"]:
                shown |= set(b["lines"])
                if lst["list"] == 0:
                    jin |= set(b["lines"])
    used_any: set[int] = set()
    for text in lines:
        used_any |= codes_in(text)
    used_shown: set[int] = set()
    for n in shown:
        used_shown |= codes_in(lines[n])
    used_others: set[int] = set()
    for n in shown - jin:
        used_others |= codes_in(lines[n])
    free_story_rule = [c for c in end_codes if c not in used_any]
    free_ending = [c for c in end_codes if c not in used_shown]
    free_after_jin = [c for c in end_codes if c not in used_others and c != SPACE_CODE]
    last_row_used = len(end_codes) - (kanji.TABLE_ROWS - 1) * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1

    room = 0
    for n, (_off, length, *_) in enumerate(table):
        if n not in shown:
            room += (length + 1 + 3) & ~3
    others = shown - jin
    jin_room = sum(
        (table[n][1] + 1 + 3) & ~3
        for n in jin
        if n not in others and lines[n] != b"\x81\x40"
    )
    se = (FILES / "SE.DAT").read_bytes()
    result: dict[str, Any] = {
        "sources": {
            "cybotsu_program_sha256": hashlib.sha256(us).hexdigest(),
            "END.BIN": hashlib.sha256(end).hexdigest(),
            "SE.DAT": hashlib.sha256(se).hexdigest(),
            "pairing": str(PAIRING),
        },
        "font": {
            "se_dat_copy_equals_kanji_bin": se[0x40000:0x68000]
            == (FILES / "KANJI.BIN").read_bytes(),
            "end_table_codes": len(end_codes),
            "end_table_equals_stg0as_table": end_codes == story_codes,
            "free_by_story_rule": len(free_story_rule),
            "free_not_used_by_any_ending_line": len(free_ending),
            "free_if_only_other_endings_stay_japanese": len(free_after_jin),
            "new_codes_in_last_row": new_slots,
            "ending_lines_shown": len(shown),
            "jin_ending_lines": len(jin),
        },
        "as_is": plain,
        "indent": indented,
        "room": {
            "bytes_of_lines_no_ending_box_shows": room,
            "bytes_of_jin_ending_lines_no_other_ending_shows": jin_room,
            "needed_as_is": plain["row_bytes"],
            "needed_indent": indented["row_bytes"],
        },
    }
    summary = {k: v for k, v in result.items() if k in ("font", "room")} | {
        mode: {k: v for k, v in result[mode].items() if k != "boxes"}
        for mode in ("as_is", "indent")
    }
    print(json.dumps(summary, indent=1))
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
