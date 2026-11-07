"""EXP-0081: codes, room and ending timing for the whole English script.

Run from the repository root (offline; reads the arcade ROM for the roster's
official English, as the build does):

    ./invenv.sh python research/experiments/EXP-0081/capacity.py \\
        [--build build/ui006/b] [--out research/experiments/EXP-0081/capacity.json]

What goes on the disc once lists 6-8 (`SPECIAL-013`-`015`) join the current
image (``data/regression/ui007_ui_text.json``):

1. **Pairs.** The roster's rows are made exactly as ``tools.text.dialogue``
   makes them (``--roster data/text/m5_roster.json --indent``): official
   records wrapped, then ``shift_rows`` over story and quotes. Control: 487
   pairs, the build's own count. The captions' rows as
   ``tools.text.vs_captions`` (control: 23 new pairs). The ending speaker
   names 601/605 (slots 610/614). Then every new box of lists 6-8 wrapped,
   each row indented by half a cell when that adds fewer new pairs (the
   roster's rows held fixed), and the new captions centred as the others.
2. **Codes in the story font** (`KANJI.BIN`, table `STG0AS.BIN`
   ``0x4AD7C``; `VICTORY.BIN` and `END.BIN` read it too, D-030, D-047):
   codes no line uses, slots left in the table's last row, and the codes of
   lines that would still show Japanese through this font (story scenes of
   lists 0-8, picked win quotes, all captions; lists 6-8's endings).
3. **`END.BIN`'s table** against the story's: lists 6-8's endings draw the
   story font through `END.BIN`'s codes (D-047), so each code they use must
   sit at the same index in both tables.
4. **Room** (bytes): rows (``dialogue.row_bytes``) against each file's line
   spans no Japanese shown line keeps; the roster's ending rows from the
   current build's ``ending_changes.json``.
5. **Timing.** ``tools.text.ending_timing.retime`` on a scratch `END.BIN`
   for lists 6-8 with the English cells (`END-011`'s rule, as the roster);
   it raises if a box would hold its line under ``MIN_HOLD``.

Writes counts and code numbers only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
import tools.text.dialogue as dl
from tools.font import kanji, pairs
from tools.reference.cybots_text import build_program, decode, long, read_record
from tools.reference.mame_audit import parse_driver
from tools.text import ending, ending_timing, vs_captions

SRC = Path("local/extracted/saturn_jp")
SPECIAL = {
    6: Path("data/translations/special_list6.json"),
    7: Path("data/translations/special_list7.json"),
    8: Path("data/translations/special_list8.json"),
}
QUOTE_TABLE = 0x0606FAA0  # VICTORY.BIN, D-030
NAME_SLOTS = {601: 610, 605: 614}  # END-005, D-047


def ps(row: str) -> set[str]:
    return {p for p in pairs.split_pairs(row) if p != "  "}


def indent_fixed(rows: list[str], fixed: set[str]) -> list[str]:
    """``dialogue.shift_rows`` for new rows, with ``fixed`` pairs already paid."""
    variants = [[r, " " + r if len(r) < dl.ROW_CHARS else r] for r in rows]
    choice = [0] * len(rows)
    count: Counter[str] = Counter()
    for v in variants:
        count.update(ps(v[0]))
    while True:
        changed = 0
        for i, v in enumerate(variants):
            count.subtract(ps(v[choice[i]]))
            cost = [
                sum(1 for p in ps(x) if p not in fixed and count[p] <= 0) for x in v
            ]
            new = 0 if cost[0] <= cost[1] else 1
            changed += new != choice[i]
            choice[i] = new
            count.update(ps(v[new]))
        if not changed:
            return [v[c] for v, c in zip(variants, choice, strict=True)]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--build", type=Path, default=Path("build/ui006/b"))
    p.add_argument("--driver", type=Path, default=Path("local/mame_src/cps2.cpp"))
    p.add_argument("--rompath", type=Path, default=Path("local/arcade"))
    p.add_argument(
        "--out", type=Path, default=Path("research/experiments/EXP-0081/capacity.json")
    )
    a = p.parse_args()
    report: dict[str, Any] = {"task": "SPECIAL-016"}

    # 1. The roster's rows, as the build makes them.
    romset = parse_driver(a.driver.read_text(encoding="latin-1"))["cybotsu"]
    archives = [a.rompath / "cybotsu.zip"]
    if romset.parent:
        archives.append(a.rompath / f"{romset.parent}.zip")
    program = build_program([x for x in archives if x.exists()], romset)
    pairings, quotes_path = dl.roster_inputs(Path("data/text/m5_roster.json"))
    specs = [dl.pilot_spec(x) for x in pairings]

    def english(slot: int) -> list[str]:
        return dl.wrap(
            decode(read_record(program, long(program, dl.EN_TABLE + 4 * slot)).codes)
        )

    roster_story = [english(x["arcade_slot"]) for sp in specs for x in sp[0]["pairs"]]  # type: ignore[attr-defined]
    qdoc = json.loads(quotes_path.read_text())
    roster_quotes = [english(q["arcade_slot"]) for q in qdoc["roster_quote_boxes"]]
    flat = [r for rows in roster_story + roster_quotes for r in rows]
    shifted = dl.shift_rows(flat)
    roster_pairs = set(dl.wanted_pairs([dl.Box(0, 0, (), tuple(shifted))]))
    approved_caps = json.loads(Path("data/translations/vs_captions.json").read_text())
    story_map = dict.fromkeys(roster_pairs, 0)
    cap_rows = vs_captions.caption_rows(approved_caps, story_map)
    cap_new = vs_captions.new_pairs(cap_rows, story_map)
    name_rows = [r for s in NAME_SLOTS.values() for r in english(s)]
    existing = roster_pairs | set(cap_new) | {x for r in name_rows for x in ps(r)}
    report["controls"] = {
        "roster_pairs": len(roster_pairs),
        "roster_pairs_build": 487,
        "roster_rows": len(shifted),
        "roster_rows_build": 851 + 46,
        "caption_new_pairs": len(cap_new),
        "caption_new_pairs_build": 23,
        "name_pairs_not_in_story": sorted(
            {x for r in name_rows for x in ps(r)} - roster_pairs - set(cap_new)
        ).__len__(),
    }

    # The new English.
    new_rows: dict[str, list[str]] = {"story": [], "win_quotes": [], "ending": []}
    new_caps: list[dict[str, Any]] = []
    per_list: dict[str, Any] = {}
    box_rows: dict[tuple[int, str, int], list[str]] = {}
    for n, path in SPECIAL.items():
        doc = json.loads(path.read_text())
        for b in doc["boxes"]:
            if b.get("official_slot") is not None or not b["english"]:
                continue
            if b["section"] == "captions":
                new_caps.append({"box": b["box"], "english": b["english"]})
            else:
                rows = dl.wrap(b["english"])
                box_rows[(n, b["section"], b["box"])] = rows
                new_rows[b["section"]].extend(rows)
    order = [k for k in box_rows]
    flat_new = [r for k in order for r in box_rows[k]]
    shifted_new = iter(indent_fixed(flat_new, existing))
    for k in order:
        box_rows[k] = [next(shifted_new) for _ in box_rows[k]]
    new_story_pairs = {x for rows in box_rows.values() for r in rows for x in ps(r)}
    cap_rows_new = vs_captions.caption_rows(
        {"captions": new_caps}, dict.fromkeys(existing | new_story_pairs, 0)
    )
    all_pairs = (
        existing | new_story_pairs | {x for r in cap_rows_new.values() for x in ps(r)}
    )
    ending_pairs = {
        x
        for (_, sec, _), rows in box_rows.items()
        if sec == "ending"
        for r in rows
        for x in ps(r)
    } | {x for r in name_rows for x in ps(r)}
    for n in SPECIAL:
        mine = {k: v for k, v in box_rows.items() if k[0] == n}
        per_list[str(n)] = {
            "boxes": len(mine),
            "rows": sum(len(v) for v in mine.values()),
            "pairs": len({x for v in mine.values() for r in v for x in ps(r)}),
            "pairs_new_to_disc": len(
                {x for v in mine.values() for r in v for x in ps(r)} - existing
            ),
            "max_cells": max(dl.cells_of(v) for v in mine.values()),
        }
    report["new"] = {
        "per_list": per_list,
        "captions": len(cap_rows_new),
        "pairs_new_to_disc": len(all_pairs - existing),
        "pairs_total_on_disc": len(all_pairs),
        "ending_pairs_6_8": len(ending_pairs),
    }

    # 2. Codes in the story font.
    stg = (SRC / "STG0AS.BIN").read_bytes()
    table = kanji.read_code_table(stg)
    texts = dl.text_lines()
    unused = pairs.unused_codes(table, texts)
    last_row = kanji.TABLE_ROWS - 1
    last_row_used = len(table) - last_row * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1
    lines = dl.line_table()
    base = dl.BASE

    def u32(x: int) -> int:
        return int.from_bytes(stg[x - base : x - base + 4], "big")

    def u16(x: int) -> int:
        return int.from_bytes(stg[x - base : x - base + 2], "big")

    address_line = {base + off: i for i, (off, _) in enumerate(lines)}
    box_lines: dict[int, list[int]] = {}
    for box in range(1074):
        e = u32(dl.RECORDS + 4 * box) + 8
        while True:
            ln = address_line.get(u32(e))
            if ln is not None:
                box_lines.setdefault(box, []).append(ln)
            if u16(e + 4) != 0xFFFF:
                break
            e += 8
    reach = json.loads(Path("data/text/reachability.json").read_text())
    scene_boxes = {
        (int(x["list"]), int(s["scene"])): list(s["boxes"])
        for x in reach["lists"]
        for s in x["scene_boxes"]
    }
    census = {
        int(x["list"]): x
        for x in json.loads(Path("data/text/pilot_census.json").read_text())["lists"]
    }
    vic = (SRC / "VICTORY.BIN").read_bytes()
    picked = {
        vic[QUOTE_TABLE - base + 16 * pilot + 2 * k]
        for pilot in range(9)
        for k in range(8)
    }
    shown_boxes = (
        {
            b
            for n in range(9)
            for s in census[n]["story_scenes"]
            for b in scene_boxes[(n, s)]
        }
        | {b for s in picked for b in scene_boxes[(9, s)]}
        | set(reach["box_classes"]["caption"])
    )
    english_boxes = (
        {x["box"] for sp in specs for x in sp[0]["pairs"]}  # type: ignore[attr-defined]
        | {q["box"] for q in qdoc["roster_quote_boxes"]}
        | {int(c["box"]) for c in approved_caps["captions"]}
        | {k[2] for k in box_rows if k[1] != "ending"}
        | {int(c["box"]) for c in new_caps}
    )
    staying_boxes = sorted(shown_boxes - english_boxes)
    staying_lines = sorted({n for b in staying_boxes for n in box_lines.get(b, [])})
    kept_codes: set[int] = set()
    for n in staying_lines:
        off, length = lines[n]
        kept_codes |= dl.codes_in(stg[off : off + length]) & set(table)
    usable = [c for c in table if c != dl.SPACE_CODE and c not in kept_codes]
    report["story_font"] = {
        "table_codes": len(table),
        "unused_codes": len(unused),
        "new_slots": new_slots,
        "shown_boxes_staying_japanese": staying_boxes,
        "their_lines": staying_lines,
        "codes_they_keep": len(kept_codes),
        "codes_usable": len(usable) + new_slots,
        "pairs_needed": len(all_pairs),
        "spare": len(usable) + new_slots - len(all_pairs),
        "sacrifice_needed": max(0, len(all_pairs) - len(unused) - new_slots),
        "sacrifice_now_on_disc": 152 + 1 + 13,
    }

    # 3. END.BIN's table against the story's.
    end = (SRC / "END.BIN").read_bytes()
    end_table = kanji.read_code_table(end, ending.CODE_TABLE)
    built_end = (a.build / "END.BIN").read_bytes()
    built_stg = (a.build / "STG0AS.BIN").read_bytes()
    bt_end = kanji.read_code_table(built_end, ending.CODE_TABLE)
    bt_stg = kanji.read_code_table(built_stg)
    report["end_table"] = {
        "untouched_equal": end_table == table,
        "built_lengths": [len(bt_stg), len(bt_end)],
        "built_common_prefix": next(
            (i for i, (x, y) in enumerate(zip(bt_stg, bt_end, strict=False)) if x != y),
            min(len(bt_stg), len(bt_end)),
        ),
    }

    # 4. Room.
    def spans(offsets: list[tuple[int, int]], delta: int = 0) -> int:
        out: list[list[int]] = []
        for off, length in sorted(offsets):
            span = [off + delta, off + delta + ((length + 1 + 3) & ~3)]
            if out and out[-1][1] == span[0]:
                out[-1][1] = span[1]
            else:
                out.append(span)
        return sum(e - s for s, e in out)

    def rows_bytes(rows: list[str]) -> int:
        return sum(len(dl.row_bytes(r, dict.fromkeys(ps(r) | {"  "}, 1))) for r in rows)

    stg_free = [lines[n] for n in range(len(lines)) if n not in set(staying_lines)]
    cap_bytes = rows_bytes(list(cap_rows.values()) + list(cap_rows_new.values()))
    roster_story_rows = shifted[: sum(len(x) for x in roster_story)]
    roster_quote_rows = shifted[sum(len(x) for x in roster_story) :]
    new_story_rows = [r for k, v in box_rows.items() if k[1] == "story" for r in v]
    new_quote_rows = [r for k, v in box_rows.items() if k[1] == "win_quotes" for r in v]
    new_end_rows = [r for k, v in box_rows.items() if k[1] == "ending" for r in v]
    census_files = json.loads(dl.CENSUS.read_text())["files"]
    vic_first = next(f for f in census_files if f["file"] == "VICTORY.BIN")
    delta = vic_first["blocks"][0]["table"][0][0] - lines[0][0]
    quote_555 = set(box_lines.get(555, []))
    vic_free = [lines[n] for n in range(len(lines)) if n not in quote_555]
    end_lines = ending.end_lines()
    built_end_rows = json.loads((a.build / "ending_changes.json").read_text())["ranges"]
    roster_end_bytes = sum(
        r["end"] - r["start"]
        for r in built_end_rows
        if r["file"] == "END.BIN" and r["what"].endswith(" row")
    )
    report["room"] = {
        "STG0AS.BIN": {
            "room": spans(stg_free),
            "roster_story": rows_bytes(roster_story_rows),
            "captions": cap_bytes,
            "new_story": rows_bytes(new_story_rows),
        },
        "VICTORY.BIN": {
            "room": spans(vic_free, delta),
            "roster_quotes": rows_bytes(roster_quote_rows),
            "new_quotes": rows_bytes(new_quote_rows),
        },
        "END.BIN": {
            "room": spans(list(end_lines)),
            "roster_endings_built": roster_end_bytes,
            "new_endings": rows_bytes(new_end_rows),
        },
    }
    for f in report["room"].values():
        f["spare"] = f["room"] - sum(v for k, v in f.items() if k != "room")

    # 5. Timing.
    surfaces = {
        int(x["list"]): x
        for x in json.loads(Path("data/text/ending_surfaces_others.json").read_text())[
            "lists"
        ]
    }
    end_box_lines = ending.record_lines(end, end_lines)
    jp_codes = set(end_table)
    japanese = {
        box: sum(
            1
            for k in ls
            for i in range(0, end_lines[k][1] - 1, 2)
            if int.from_bytes(end[end_lines[k][0] + i : end_lines[k][0] + i + 2], "big")
            in jp_codes
        )
        for box, ls in end_box_lines.items()
        if ls
    }
    timing: dict[str, Any] = {}
    for n in SPECIAL:
        cells = {
            k[2]: sum(len(pairs.split_pairs(r)) for r in v)
            for k, v in box_rows.items()
            if k[0] == n and k[1] == "ending"
        }
        scratch = bytearray(end)
        try:
            out = ending_timing.retime(scratch, n, surfaces[n], cells, japanese)
            holds = [x["hold"] for x in out.boxes if x.get("hold") is not None]
            timing[str(n)] = {
                "ok": True,
                "boxes_timed": len(out.boxes) + len(out.waits),
                "min_hold_frames": min(holds) if holds else None,
                "slowed": [x["box"] for x in out.waits if x.get("slowed")],
                "changes": len(out.changes),
            }
        except ValueError as e:
            timing[str(n)] = {"ok": False, "error": str(e)}
    report["timing"] = timing

    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "story_font"}, indent=1))
    sf = dict(report["story_font"])
    sf["their_lines"] = len(sf["their_lines"])
    print(json.dumps(sf, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
