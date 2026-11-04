"""EXP-0032: pair the versus win quotes by both games' selection logic.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0032/pair_quotes.py \\
        local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \\
        local/win002/mame/cybotsu-0-c0000.asm \\
        --out data/translations/win_quotes_pairing.json

Inputs:
- ``VICTORY.BIN`` (``local/extracted/saturn_jp``), loaded at ``0x06060000``:
  the quote table ``0x0606FAA0`` (9 pilots x 8 entries of (scene, byte)),
  the per-pilot scene lists ``0x0607DB3C`` (list 9 holds the quotes) and the
  box table ``0x0607849C``; and ``STG0AS.BIN``'s caption table
  ``0x0609CC22`` (9 pilots x 10 stage words).
- The arcade program (``cybotsu``): scene scripts ``0x12150`` (list 6 holds
  the quotes), the Japanese table ``0x0A30F6`` of ``cybotsj`` and the US
  table ``0x0B33AA``. Its quote table at ``0x630CE`` (6 pilots x 8) is read
  through the 68000's program space (PC-relative), which CPS-2 decrypts, so
  it is taken from MAME's disassembly listing (debugger ``dasm``).

For each pilot and entry: the scene each game posts, the box (Saturn) and
slot (arcade) its script shows, the Saturn lines of the box, whether the
arcade Japanese record of the slot has the same text (``exact``, through
``data/text/arcade_jp_map.json``; ``unmapped`` when a code is not in the map;
``differs`` otherwise), and the US English record. Also the boxes no entry
reaches, the Saturn-only pilots' quotes, and the caption boxes. Writes
numbers, labels and hashes only (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0028"))
from pair_pilot import arcade_scenes  # type: ignore[import-not-found]

from tools.reference.cybots_text import long
from tools.text.arcade_pairing import read_jp_record

BASE = 0x06060000
SAT_QUOTES = 0x0606FAA0
SAT_LISTS = 0x0607DB3C
SAT_BOXES = 0x0607849C
SAT_CAPTIONS = 0x0609CC22
SAT_QUOTE_LIST = 9
ARC_QUOTES = 0x630CE
ARC_QUOTE_LIST = 6
JP_TABLE, EN_TABLE = 0x0A30F6, 0x0B33AA
ARCADE_PILOTS, SATURN_PILOTS, ENTRIES = 6, 9, 8
VICTORY = Path("local/extracted/saturn_jp/VICTORY.BIN")
STG0AS = Path("local/extracted/saturn_jp/STG0AS.BIN")
PILOT_NAMES = ["Jin", "Santana", "Mary", "Arieta", "Gawaine", "Bao and Mao"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def u16(data: bytes, address: int) -> int:
    return int.from_bytes(data[address - BASE : address - BASE + 2], "big")


def u32(data: bytes, address: int) -> int:
    return int.from_bytes(data[address - BASE : address - BASE + 4], "big")


def listing_bytes(path: Path, first: int, count: int) -> bytes:
    """Bytes of the decrypted program space, from a MAME ``dasm`` listing."""
    words: dict[int, int] = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^([0-9A-F]{6}): ((?:[0-9A-F]{4} ?)+)", line)
        if m:
            at = int(m.group(1), 16)
            for i, w in enumerate(m.group(2).split()):
                words[at + 2 * i] = int(w, 16)
    return b"".join(words[a].to_bytes(2, "big") for a in range(first, first + count, 2))


def saturn_list(data: bytes, pilot: int) -> list[list[int]]:
    lists = [u32(data, SAT_LISTS + 4 * p) for p in range(11)]
    start = lists[pilot]
    end = min([a for a in lists if a > start] + [SAT_LISTS])
    scenes = []
    for k in range((end - start) // 4):
        a, boxes = u32(data, start + 4 * k), []
        while (w := u16(data, a)) != 0xE000:
            if w < 0x8000:
                boxes.append(w)
            a += 2
        scenes.append(boxes)
    return scenes


def box_lines(data: bytes, line_of: dict[int, int], box: int) -> list[int]:
    entry, lines = u32(data, SAT_BOXES + 4 * box) + 8, []
    while True:
        lines.append(line_of[u32(data, entry)])
        if u16(data, entry + 4) != 0xFFFF:
            return lines
        entry += 8


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("jp", type=Path)
    parser.add_argument("listing", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us, jp = args.us.read_bytes(), args.jp.read_bytes()
    victory, stg = VICTORY.read_bytes(), STG0AS.read_bytes()
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "VICTORY.BIN")
    offsets = table["blocks"][0]["table"]
    line_of = {BASE + off: n for n, (off, *_rest) in enumerate(offsets)}
    texts = [victory[off : off + length] for off, length, *_rest in offsets]
    by_text: dict[bytes, list[int]] = {}
    for n, text in enumerate(texts):
        by_text.setdefault(text, []).append(n)
    code_map = {
        int(k, 16): bytes.fromhex(v)
        for k, v in json.loads(Path("data/text/arcade_jp_map.json").read_text()).items()
    }
    jp_scripts = jp.find(us[0x12150 : 0x12150 + 64])

    sat_scenes = saturn_list(victory, SAT_QUOTE_LIST)
    arc_scenes = arcade_scenes(us, ARC_QUOTE_LIST)
    import pair_pilot

    pair_pilot.SCRIPTS = jp_scripts
    arc_scenes_jp = arcade_scenes(jp, ARC_QUOTE_LIST)
    pair_pilot.SCRIPTS = 0x12150
    arc_table = listing_bytes(args.listing, ARC_QUOTES, ARCADE_PILOTS * ENTRIES * 2)

    en_record = {k: long(us, EN_TABLE + 4 * k) for k in range(624)}
    shared: dict[int, list[int]] = {}
    for k, address in en_record.items():
        shared.setdefault(address, []).append(k)

    def jp_label(slot: int, lines: list[int]) -> str:
        record = read_jp_record(jp, long(jp, JP_TABLE + 4 * slot))
        if any(c not in code_map for codes in record for c in codes):
            return "unmapped"
        decoded = [b"".join(code_map[c] for c in codes) for codes in record]
        return "exact" if decoded == [texts[n] for n in lines] else "differs"

    def box_record(box: int) -> dict[str, Any]:
        lines = box_lines(victory, line_of, box)
        return {
            "box": box,
            "saturn_lines": lines,
            "saturn_line_bytes": [len(texts[n]) for n in lines],
            "arcade_slot": box,
            "arcade_japanese": jp_label(box, lines),
            "arcade_japanese_line_lengths": [
                len(c) for c in read_jp_record(jp, long(jp, JP_TABLE + 4 * box))
            ],
            "us_record": f"0x{en_record[box]:06X}",
            "us_record_slots": shared[en_record[box]],
        }

    entries: list[dict[str, Any]] = []
    for pilot in range(SATURN_PILOTS):
        for entry in range(ENTRIES):
            at = SAT_QUOTES - BASE + 16 * pilot + 2 * entry
            scene, byte = victory[at], victory[at + 1]
            row: dict[str, Any] = {
                "pilot": pilot,
                "entry": entry,
                "saturn_scene": scene,
                "saturn_byte": byte,
                "saturn_boxes": sat_scenes[scene],
            }
            if pilot < ARCADE_PILOTS:
                a_scene = arc_table[16 * pilot + 2 * entry]
                row.update(
                    {
                        "arcade_scene": a_scene,
                        "arcade_byte": arc_table[16 * pilot + 2 * entry + 1],
                        "arcade_slots": arc_scenes[a_scene],
                        "arcade_level": entry // 2,
                        "arcade_low_bit": entry % 2,
                    }
                )
            entries.append(row)

    reached = sorted({b for e in entries for b in e["saturn_boxes"]})
    roster = sorted(
        {b for e in entries if e["pilot"] < ARCADE_PILOTS for b in e["saturn_boxes"]}
    )
    quote_boxes = sorted({b for s in sat_scenes for b in s})
    caption_words = [u16(stg, SAT_CAPTIONS + 2 * k) for k in range(SATURN_PILOTS * 10)]
    captions = {
        p: [w for w in caption_words[10 * p : 10 * p + 10] if w]
        for p in range(SATURN_PILOTS)
    }
    roster_boxes = [box_record(b) for b in roster]
    saturn_only = [
        {"box": b, "saturn_lines": box_lines(victory, line_of, b)}
        for b in sorted(set(reached) - set(roster))
    ]
    labels = [r["arcade_japanese"] for r in roster_boxes]
    counts = {
        "roster_quote_boxes": len(roster),
        "roster_quote_lines": len({n for r in roster_boxes for n in r["saturn_lines"]}),
        "arcade_japanese": {k: labels.count(k) for k in sorted(set(labels))},
        "us_records_for_roster_boxes": len({r["us_record"] for r in roster_boxes}),
        "saturn_only_quote_boxes": len(saturn_only),
    }
    scripts = {
        "saturn_list_9_scenes": len(sat_scenes),
        "arcade_list_6_scenes": len(arc_scenes),
        "first_48_identical": sat_scenes[:48] == arc_scenes,
        "cybotsj_list_6_equals_cybotsu": arc_scenes_jp == arc_scenes,
    }
    tables = {
        "saturn_equals_arcade_scenes_pilots_0_5": all(
            e["saturn_scene"] == e["arcade_scene"]
            for e in entries
            if e["pilot"] < ARCADE_PILOTS
        ),
    }
    result = {
        "sources": {
            "VICTORY.BIN": sha(VICTORY),
            "STG0AS.BIN": sha(STG0AS),
            "cybotsu": sha(args.us),
            "cybotsj": sha(args.jp),
            "arcade_listing": sha(args.listing),
        },
        "selection": {
            "saturn": "VICTORY.BIN 0x06060B46-0x06060BF8: scene = table "
            "0x0606FAA0[winner pilot][random & 7]; posts list 9 (0x14000009)",
            "arcade": "cybotsu 0x6301C-0x630C8: scene = table 0x630CE[winner pilot]"
            "[2 * level + (A5+0x1D & 1)]; posts list 6 (0x14000006)",
        },
        "scripts": scripts,
        "tables": tables,
        "entries": entries,
        "roster_quote_boxes": roster_boxes,
        "quote_boxes_no_entry_reaches": [b for b in quote_boxes if b not in reached],
        "saturn_only_quote_boxes": saturn_only,
        "caption_boxes": {
            str(p): [
                {"box": b, "saturn_lines": box_lines(victory, line_of, b)}
                for b in captions[p]
            ]
            for p in range(SATURN_PILOTS)
        },
        "counts": counts,
    }
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({**scripts, **tables, **counts}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
