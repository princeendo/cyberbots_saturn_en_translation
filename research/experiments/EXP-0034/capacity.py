"""EXP-0034: what the M5 roster needs in codes and room, under each option.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0034/capacity.py \\
        --pairing data/translations/jin_pairing.json \\
        --pairing data/translations/santana_pairing.json \\
        --pairing local/cap001/pairing/mary_pairing.json ... \\
        --quotes data/translations/win_quotes_pairing.json \\
        --kept 1 2 3 --out local/cap001/capacity.json

A measurement; it builds nothing. The story boxes and their English rows are
made as ``tools.text.dialogue`` makes them (``pilot_spec``, ``wrap``); the
win quotes' rows likewise from their arcade slots (D-030). All pairs share
one code pool (one ``KANJI.BIN``).

For each option it counts the codes to sacrifice and lists the Japanese
lines that would show a pair glyph: lines that stay Japanese, that some box
shows, and that use a sacrificed code. Each such line is grouped by whose
it is (a line can be in more than one group):

- ``roster_endings``: a box of a roster list's scene that is not a story
  scene (posted from ``END.BIN``);
- ``saturn_only``: a box of lists 6-8, or a quote of quote-table rows 6-8;
- ``captions``: a VS caption box (``0x0609CC22``, EXP-0032);
- ``kept``: a roster story line some other box also uses (``--kept``, from
  ``dialogue.py --budget``);
- ``other``: any other box (list 10's name labels and the like).

Options:
- ``a``: the compiler's rule: fewest lines (in all three copies), then
  table order;
- ``b``: fewest lines that stay Japanese and are shown, then rule a;
- ``c``: rule a with 33 more codes, if the table could reach the glyphs no
  code reaches (an upper bound; whether it can is an experiment);
- ``c+b``: both.

Writes numbers and line numbers only (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji, pairs
from tools.reference.cybots_text import build_program, decode, long, read_record
from tools.reference.mame_audit import parse_driver
from tools.text import dialogue as d

CAPTIONS = 0x0609CC22
LISTS = 11
ROSTER = range(6)
SATURN_ONLY = range(6, 9)
EXTRA_GLYPHS = 33  # 1280 glyphs, 39 x 32 table slots, the last one a 0 (D-019)


def u16(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - d.BASE : a - d.BASE + 2], "big")


def u32(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - d.BASE : a - d.BASE + 4], "big")


def scenes_of(stg: bytes) -> dict[tuple[int, int], list[int]]:
    """(list, scene) -> boxes, each script read up to 0xE000."""
    heads = [u32(stg, d.PILOT_LISTS + 4 * p) for p in range(LISTS)]
    out = {}
    for p, head in enumerate(heads):
        end = min([h for h in heads if h > head] + [d.PILOT_LISTS])
        for k in range((end - head) // 4):
            a, boxes = u32(stg, head + 4 * k), []
            while (w := u16(stg, a)) != 0xE000:
                if w < 0xC000 and w != 0xFFFF and (w & 0x7FFF) not in boxes:
                    boxes.append(w & 0x7FFF)
                a += 2
            out[(p, k)] = boxes
    return out


def shift_rows(rows: list[str]) -> list[str]:
    """Option d: indent some rows by one space (half a cell) to share pairs.

    Greedy passes: each row of at most 31 characters takes the variant that
    adds fewer pairs not already used by the other rows, until no row
    changes. The words are unchanged.
    """
    variants = [[r, " " + r if len(r) < d.ROW_CHARS else r] for r in rows]
    choice = [0] * len(rows)
    count: Counter[str] = Counter()

    def ps(row: str) -> set[str]:
        return {p for p in pairs.split_pairs(row) if p != "  "}

    for v in variants:
        count.update(ps(v[0]))
    while True:
        changed = 0
        for i, v in enumerate(variants):
            count.subtract(ps(v[choice[i]]))
            cost = [sum(1 for p in ps(x) if count[p] <= 0) for x in v]
            new = 0 if cost[0] <= cost[1] else 1
            changed += new != choice[i]
            choice[i] = new
            count.update(ps(v[new]))
        if not changed:
            return [v[c] for v, c in zip(variants, choice, strict=True)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairing", type=Path, action="append", required=True)
    parser.add_argument("--quotes", type=Path, required=True)
    parser.add_argument("--kept", type=int, nargs="*", default=[])
    parser.add_argument(
        "--font", type=Path, default=Path("local/layout001/font/arcade_font.json")
    )
    parser.add_argument("--driver", type=Path, default=Path("local/mame_src/cps2.cpp"))
    parser.add_argument("--rompath", type=Path, default=Path("local/arcade"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    romset = parse_driver(args.driver.read_text(encoding="latin-1"))["cybotsu"]
    archives = [args.rompath / "cybotsu.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    program = build_program([p for p in archives if p.exists()], romset)

    def rows_of(slot: int) -> list[str]:
        return d.wrap(
            decode(read_record(program, long(program, d.EN_TABLE + 4 * slot)).codes)
        )

    specs = [d.pilot_spec(p) for p in args.pairing]
    story: list[d.Box] = []
    story_scenes: dict[int, list[int]] = {}
    for pairing, box_list, scenes in specs:
        story_scenes[int(box_list["pilot"])] = scenes  # type: ignore[call-overload]
        for p in pairing["pairs"]:  # type: ignore[attr-defined]
            rows = rows_of(p["arcade_slot"])
            story.append(
                d.Box(p["box"], p["arcade_slot"], tuple(p["saturn_lines"]), tuple(rows))
            )
    quotes_doc = json.loads(args.quotes.read_text())
    quotes = [
        d.Box(
            q["box"],
            q["arcade_slot"],
            tuple(q["saturn_lines"]),
            tuple(rows_of(q["arcade_slot"])),
        )
        for q in quotes_doc["roster_quote_boxes"]
    ]
    story_pairs = d.wanted_pairs(story)
    all_pairs = d.wanted_pairs(story + quotes)
    all_rows = [r for b in story + quotes for r in b.rows]
    shifted = shift_rows(all_rows)
    shifted_pairs = {p for r in shifted for p in pairs.split_pairs(r) if p != "  "}
    capital_pairs = {
        p
        for b in story + quotes
        for r in d.wrap(" ".join(b.rows).upper())
        for p in pairs.split_pairs(r)
        if p != "  "
    }

    stg = bytes(d.checked("STG0AS.BIN"))
    table = kanji.read_code_table(bytes(stg))
    lines = d.line_table()
    address_line = {d.BASE + off: i for i, (off, _) in enumerate(lines)}
    box_lines: dict[int, list[int]] = {}
    for box in range(1074):
        entry = u32(stg, d.RECORDS + 4 * box) + 8
        while True:
            n = address_line.get(u32(stg, entry))
            if n is not None:
                box_lines.setdefault(box, []).append(n)
            if u16(stg, entry + 4) != 0xFFFF:
                break
            entry += 8

    # Who shows each line.
    groups: dict[int, set[str]] = {}

    def mark(box: int, group: str) -> None:
        for n in box_lines.get(box, []):
            groups.setdefault(n, set()).add(group)

    for (p, k), boxes in scenes_of(bytes(stg)).items():
        for b in boxes:
            if p in ROSTER:
                mark(
                    b,
                    "roster_story"
                    if k in story_scenes.get(p, [])
                    else "roster_endings",
                )
            elif p in SATURN_ONLY:
                mark(b, "saturn_only")
            elif p != 9:
                mark(b, "other")
    for e in quotes_doc["entries"]:
        for b in e["saturn_boxes"]:
            mark(b, "roster_quotes" if e["pilot"] in ROSTER else "saturn_only")
    for k in range(9 * 10):
        if b := u16(bytes(stg), CAPTIONS + 2 * k):
            mark(b, "captions")
    replaced = {n for b in story + quotes for n in b.lines} - set(args.kept)
    for n in args.kept:
        groups.setdefault(n, set()).add("kept")
    staying = {
        n: g - {"roster_story", "roster_quotes"}
        for n, g in groups.items()
        if n not in replaced and g - {"roster_story", "roster_quotes"}
    }

    texts = d.text_lines()
    unused = pairs.unused_codes(table, texts)
    counts: Counter[int] = Counter()
    for text in texts:
        counts.update(d.codes_in(text) & set(table))
    line_codes = {
        n: d.codes_in(bytes(stg[off : off + ln])) for n, (off, ln) in enumerate(lines)
    }
    kept_codes = (
        set().union(*(line_codes[n] for n in args.kept)) if args.kept else set()
    )
    staying_counts: Counter[int] = Counter()
    for n in staying:
        staying_counts.update(line_codes[n])
    candidates = [
        c
        for c in table
        if c not in unused and c not in kept_codes and c != d.SPACE_CODE
    ]
    rule_a = sorted(candidates, key=lambda c: (counts[c], table.index(c)))
    rule_b = sorted(
        candidates, key=lambda c: (staying_counts[c], counts[c], table.index(c))
    )
    last_row_used = len(table) - (kanji.TABLE_ROWS - 1) * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1

    def measure(wanted: int, rare: list[int], extra: int) -> dict[str, Any]:
        needed = max(0, wanted - len(unused) - new_slots - extra)
        gone = set(rare[:needed])
        touched = sorted(n for n in staying if line_codes[n] & gone)
        by_group = {
            g: sorted(n for n in touched if g in staying[n])
            for g in ("roster_endings", "saturn_only", "captions", "kept", "other")
        }
        return {
            "sacrifice": needed,
            "touched_lines": len(touched),
            "by_group": {g: len(v) for g, v in by_group.items()},
            "touched": touched,
            "groups": by_group,
        }

    options = {}
    for label, wanted in (
        ("story", len(story_pairs)),
        ("story_and_quotes", len(all_pairs)),
        ("d_half_cell_indent", len(shifted_pairs)),
        ("d_capitals", len(capital_pairs)),
    ):
        options[label] = {
            "pairs": wanted,
            "a": measure(wanted, rule_a, 0),
            "b": measure(wanted, rule_b, 0),
            "c": measure(wanted, rule_a, EXTRA_GLYPHS),
            "c+b": measure(wanted, rule_b, EXTRA_GLYPHS),
        }
    result_rows = {
        "rows": len(all_rows),
        "rows_indented": sum(
            1 for a, b in zip(all_rows, shifted, strict=True) if a != b
        ),
        "capitals_max_rows": max(
            len(d.wrap(" ".join(b.rows).upper())) for b in story + quotes
        ),
    }
    quote_rows = [len(b.rows) for b in quotes]
    quote_bytes = sum(
        len(d.row_bytes(r, dict.fromkeys(all_pairs, 1))) for b in quotes for r in b.rows
    )
    quote_room = sum(
        (lines[n][1] + 1 + 3) & ~3 for n in {n for b in quotes for n in b.lines}
    )
    result = {
        "estimate": (
            "story pairings of pilots 2-5 are slot for slot (pair_pilot.py),"
            " before PAIR-003"
        ),
        "pilots": [str(p) for p in args.pairing],
        "story_boxes": len(story),
        "quote_boxes": len(quotes),
        "pairs": {
            "story": len(story_pairs),
            "story_and_quotes": len(all_pairs),
            "quotes_only": len(all_pairs) - len(story_pairs),
        },
        "rows": result_rows,
        "codes": {
            "unused": len(unused),
            "new_slots": new_slots,
            "extra_if_c": EXTRA_GLYPHS,
        },
        "staying_shown_lines": len(staying),
        "staying_by_group": {
            g: sum(1 for v in staying.values() if g in v)
            for g in ("roster_endings", "saturn_only", "captions", "kept", "other")
        },
        "quotes": {
            "max_rows": max(quote_rows),
            "boxes_over_1_row": sum(r > 1 for r in quote_rows),
            "max_cells": max(d.cells_of(b.rows) for b in quotes),
            "text_bytes": quote_bytes,
            "own_line_bytes_in_victory": quote_room,
        },
        "options": options,
    }
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    summary = {k: v for k, v in result.items() if k != "options"}
    summary["options"] = {
        label: {
            o: {
                k: v
                for k, v in m.items()
                if k in ("sacrifice", "touched_lines", "by_group")
            }
            if isinstance(m, dict)
            else m
            for o, m in opts.items()
        }
        for label, opts in options.items()
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
