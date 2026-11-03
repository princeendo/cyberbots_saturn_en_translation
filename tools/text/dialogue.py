"""Compile a pilot's story boxes into English pair glyphs; build the image (`RE-003`).

Run from the repository root:

    ./invenv.sh python -m tools.text.dialogue \\
        --pairing data/translations/jin_pairing.json \\
        --font local/layout001/font/arcade_font.json \\
        --driver local/mame_src/cps2.cpp --rompath local/arcade \\
        --out build/re003/jin [--record data/translations/jin_story.json]

The policy and route are in `docs/localization_policy.md`: the official US arcade
English, as paired (D-022), unchanged, drawn as pair glyphs (D-024).

1. **English.** Read at build time from the `cybotsu` program, built from the ROM
   zips (`tools.reference.cybots_text`). The English table is at ``0x0B33AA``
   (D-009). The text is never written to the repository (`AGENTS.md` rule 21).
2. **Rows.** Each box's record is re-flowed into rows of at most 32 characters.
   The compiler fails if a box needs more than 3 rows (records hold 3 lines in
   place, D-023) or more than 60 glyph cells (D-020).
3. **Codes.** Each distinct pair (``tools.font.pairs``), in order of first use,
   gets a table code. First come the codes no Japanese line uses (D-023), in
   table order. Then come new codes in the table's last row, up to one before
   its end, because the lookup scans to a 0 word (``0x0606E9E8``). Last, by the
   user's decision (2026-11-02), the codes of the least-used Japanese
   characters (fewest lines, then table order), never one used by a line that
   stays.
4. **Text room** in `STG0AS.BIN`: the pilot's own lines, except lines shared
   with another box, then ``--dead`` lines (Jin's ending lines, dead in this
   copy, EXP-0024). Rows are NUL-terminated and 4-byte aligned. A pair of
   spaces is ``0x8140`` (no glyph).
5. **Records.** Each box's entries are rewritten as (row pointer, ``0xFFFF`` or
   0, 0).
6. **Image.** `KANJI.BIN` and `STG0AS.BIN` go through `tools.disc.patch_image`
   into ``OUT/image``.

Also writes ``OUT/prediction.json``: per box, the SHA-256 of each predicted
glyph cell in drawing order, for live checks. ``--record`` writes the
committed provenance record: per box its slot, the English record's address
and SHA-256, rows, cells and pairs; the codes and glyph slots used; and the
sacrificed Japanese codes. It holds no text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc import patch_image
from tools.font import kanji, pairs
from tools.reference.cybots_text import build_program, decode, long, read_record
from tools.reference.mame_audit import parse_driver

BASE = 0x06060000
RECORDS = 0x060A5684
EN_TABLE = 0x0B33AA
ROW_CHARS = 32
MAX_ROWS = 3
MAX_CELLS = 60
SPACE_CODE = 0x8140
NEW_CODE_FIRST = 0xF040  # user-defined Shift-JIS area: never a table code here
FILES = Path("local/extracted/saturn_jp")
LISTING = Path("references/saturn_jp/iso_listing.json")
SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
CENSUS = Path("data/text/script_census.json")
JIN_DEAD_LINES = [*range(752, 778), 897, 898, 953]  # EXP-0024


@dataclass(frozen=True)
class Box:
    box: int
    slot: int
    lines: tuple[int, ...]
    rows: tuple[str, ...]


def wrap(text: str) -> list[str]:
    """Re-flow an arcade record (``\\n`` line breaks) into rows."""
    flat = " ".join(part.strip() for part in text.split("\n") if part.strip())
    return textwrap.wrap(flat, ROW_CHARS) or [""]


def cells_of(rows: Sequence[str]) -> int:
    return sum(1 for row in rows for p in pairs.split_pairs(row) if p != "  ")


def allocate_codes(
    wanted: Sequence[str],
    unused: Sequence[int],
    new_slots: int,
    rare: Sequence[int],
) -> tuple[dict[str, int], list[int], list[int]]:
    """(pair -> code, new table codes, sacrificed Japanese codes)."""
    codes: dict[str, int] = {}
    new: list[int] = []
    sacrificed: list[int] = []
    pool = list(unused)
    for pair in wanted:
        if pool:
            codes[pair] = pool.pop(0)
        elif len(new) < new_slots:
            code = NEW_CODE_FIRST + len(new)
            new.append(code)
            codes[pair] = code
        elif len(sacrificed) < len(rare):
            code = rare[len(sacrificed)]
            sacrificed.append(code)
            codes[pair] = code
        else:
            raise ValueError(f"no code left for pair {pair!r}")
    return codes, new, sacrificed


def place(rows: Sequence[bytes], room: Sequence[tuple[int, int]]) -> list[int]:
    """First-fit file offsets for each row in the free ranges ``[start, end)``."""
    free = [list(r) for r in room]
    offsets = []
    for data in rows:
        for span in free:
            if span[1] - span[0] >= len(data):
                offsets.append(span[0])
                span[0] += len(data)
                break
        else:
            raise ValueError("the rows do not fit in the text room")
    return offsets


def row_bytes(row: str, codes: dict[str, int]) -> bytes:
    data = b"".join(
        (SPACE_CODE if p == "  " else codes[p]).to_bytes(2, "big")
        for p in pairs.split_pairs(row)
    )
    data += b"\0"
    return data + bytes(-len(data) % 4)


def record_entries(pointers: Sequence[int]) -> bytes:
    out = b""
    for n, pointer in enumerate(pointers):
        word = 0xFFFF if n < len(pointers) - 1 else 0
        out += pointer.to_bytes(4, "big") + word.to_bytes(2, "big") + bytes(2)
    return out


def checked(name: str) -> bytearray:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == f"{name};1")
    data = (FILES / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{name} does not match the listing")
    return bytearray(data)


def line_table() -> list[tuple[int, int]]:
    census = json.loads(CENSUS.read_text())
    stg = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")
    return [(off, n) for off, n, _, _ in stg["blocks"][0]["table"]]


def text_lines() -> list[bytes]:
    census = json.loads(CENSUS.read_text())
    out = []
    for f in census["files"]:
        data = (FILES / f["file"]).read_bytes()
        for block in f["blocks"]:
            out += [data[off : off + n] for off, n, _, _ in block["table"]]
    return out


def codes_in(text: bytes) -> set[int]:
    found, i = set(), 0
    while i < len(text) - 1:
        if text[i] == 0x0A:
            i += 1
            continue
        found.add(int.from_bytes(text[i : i + 2], "big"))
        i += 2
    return found


def build(args: argparse.Namespace) -> int:
    pairing = json.loads(args.pairing.read_text())
    driver = args.driver.read_text(encoding="latin-1")
    romset = parse_driver(driver)["cybotsu"]
    archives = [args.rompath / "cybotsu.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    program = build_program([p for p in archives if p.exists()], romset)
    font = pairs.load_arcade_font(args.font)
    stg, kan = checked("STG0AS.BIN"), checked("KANJI.BIN")

    def u16(a: int) -> int:
        return int.from_bytes(stg[a - BASE : a - BASE + 2], "big")

    def u32(a: int) -> int:
        return int.from_bytes(stg[a - BASE : a - BASE + 4], "big")

    boxes: list[Box] = []
    english_records = {}
    for p in pairing["pairs"]:
        slot = p["arcade_slot"]
        record = read_record(program, long(program, EN_TABLE + 4 * slot))
        english_records[slot] = record
        rows = wrap(decode(record.codes))
        if len(rows) > MAX_ROWS or cells_of(rows) > MAX_CELLS:
            raise SystemExit(
                f"box {p['box']}: {len(rows)} rows, {cells_of(rows)} cells"
            )
        boxes.append(Box(p["box"], slot, tuple(p["saturn_lines"]), tuple(rows)))

    # Which lines stay: any line a box outside this set also points at.
    ours = {b.box for b in boxes}
    lines = line_table()
    address_line = {BASE + off: i for i, (off, _) in enumerate(lines)}
    users: dict[int, set[int]] = {}
    for box in range(1074):
        entry = u32(RECORDS + 4 * box) + 8
        while True:
            line = address_line.get(u32(entry))
            if line is not None:
                users.setdefault(line, set()).add(box)
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
    own_lines = sorted({n for b in boxes for n in b.lines})
    kept = [n for n in own_lines if users.get(n, set()) - ours]
    ending_boxes = {*range(408, 423), 493, 550}  # Jin's ending boxes (EXP-0024)
    dead = [n for n in JIN_DEAD_LINES if not users.get(n, set()) - ending_boxes]
    free_lines = [n for n in own_lines if n not in kept] + dead
    room: list[list[int]] = []
    for n in sorted(set(free_lines)):
        off, length = lines[n]
        span = [off, off + ((length + 1 + 3) & ~3)]
        if room and room[-1][1] == span[0]:
            room[-1][1] = span[1]
        else:
            room.append(span)

    table = kanji.read_code_table(bytes(stg))
    texts = text_lines()
    kept_codes: set[int] = set()
    for n in kept:
        kept_codes |= codes_in(bytes(stg[lines[n][0] : lines[n][0] + lines[n][1]]))
    unused = pairs.unused_codes(table, texts)
    line_counts: Counter[int] = Counter()
    for text in texts:
        line_counts.update(codes_in(text) & set(table))
    rare = sorted(
        (
            c
            for c in table
            if c not in unused and c not in kept_codes and c != SPACE_CODE
        ),
        key=lambda c: (line_counts[c], table.index(c)),
    )
    wanted = list(
        dict.fromkeys(
            p
            for b in boxes
            for row in b.rows
            for p in pairs.split_pairs(row)
            if p != "  "
        )
    )
    last_row = kanji.TABLE_ROWS - 1
    last_row_used = len(table) - last_row * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1  # keep a 0 terminator
    codes, new, sacrificed = allocate_codes(wanted, unused, new_slots, rare)

    # Table: new codes after the last row's codes.
    row_start = kanji.TABLE_OFFSET + last_row * kanji.TABLE_ROW_CODES * 2
    for k, code in enumerate(new):
        at = row_start + 2 * (last_row_used + k)
        stg[at : at + 2] = code.to_bytes(2, "big")
    table = kanji.read_code_table(bytes(stg))
    cells = kanji.decode(bytes(kan))
    for pair, code in codes.items():
        cells[table.index(code)] = pairs.render_pair(font, pair)
    kan[:] = kanji.encode(cells)

    # Rows and records.
    all_rows = [row_bytes(r, codes) for b in boxes for r in b.rows]
    offsets = iter(place(all_rows, [(r[0], r[1]) for r in room]))
    data_rows = iter(all_rows)
    prediction = []
    record_out = []
    for b in boxes:
        pointers = []
        for _ in b.rows:
            off, data = next(offsets), next(data_rows)
            stg[off : off + len(data)] = data
            pointers.append(BASE + off)
        rec = u32(RECORDS + 4 * b.box)
        entries = record_entries(pointers)
        stg[rec - BASE + 8 : rec - BASE + 8 + 24] = entries + bytes(24 - len(entries))
        drawn = [
            cells[table.index(codes[p])]
            for r in b.rows
            for p in pairs.split_pairs(r)
            if p != "  "
        ]
        prediction.append(
            {"box": b.box, "cells": [hashlib.sha256(c).hexdigest() for c in drawn]}
        )
        en = english_records[b.slot]
        record_out.append(
            {
                "box": b.box,
                "slot": b.slot,
                "saturn_lines": list(b.lines),
                "english_record": f"0x{en.address:06X}",
                "english_sha256": hashlib.sha256(en.codes).hexdigest(),
                "rows": len(b.rows),
                "cells": len(drawn),
                "row_addresses": [f"0x{p:08X}" for p in pointers],
            }
        )

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    (out / "STG0AS.BIN").write_bytes(stg)
    (out / "KANJI.BIN").write_bytes(kan)
    (out / "prediction.json").write_text(json.dumps(prediction, indent=1) + "\n")
    summary = {
        "boxes": len(boxes),
        "rows": len(all_rows),
        "pairs": len(wanted),
        "unused_codes_used": min(len(wanted), len(unused)),
        "new_codes": len(new),
        "sacrificed": [
            {"code": f"0x{c:04X}", "glyph": table.index(c), "lines": line_counts[c]}
            for c in sacrificed
        ],
        "kept_lines": kept,
        "text_bytes": sum(len(r) for r in all_rows),
        "room_bytes": sum(e - s for s, e in room),
    }
    if args.record:
        args.record.write_text(
            json.dumps(
                {
                    "task": "RE-003",
                    "policy": (
                        "official US arcade English, as paired (D-022), unchanged;"
                        " pair glyphs (D-024)"
                    ),
                    "sources": {
                        "program_sha256": hashlib.sha256(program).hexdigest(),
                        "english_table": f"0x{EN_TABLE:06X}",
                        "pairing": str(args.pairing),
                        "font_capture_sha256": hashlib.sha256(
                            args.font.read_bytes()
                        ).hexdigest(),
                    },
                    "codes": {
                        pair_id: f"0x{code:04X}"
                        for pair_id, code in enumerate(codes.values())
                    },
                    "summary": summary,
                    "boxes": record_out,
                },
                indent=1,
            )
            + "\n"
        )
    print(json.dumps(summary))
    return patch_image.main(
        [
            "--source-dir",
            str(SOURCE_DIR),
            "--manifest",
            str(MANIFEST),
            "--track",
            TRACK,
            "--file",
            "STG0AS.BIN;1",
            "--data",
            str(out / "STG0AS.BIN"),
            "--file",
            "KANJI.BIN;1",
            "--data",
            str(out / "KANJI.BIN"),
            "--out-dir",
            str(out / "image"),
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pairing", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--record", type=Path)
    return build(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
