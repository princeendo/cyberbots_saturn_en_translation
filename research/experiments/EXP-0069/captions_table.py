"""EXP-0069: every VS caption's storage, and the US arcade's slots for them.

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0069/captions_table.py \\
        --driver local/mame_src/cps2.cpp --rompath local/arcade \\
        --out research/experiments/EXP-0069/captions_table.json

For each caption box of the table ``0x0609CC22`` (`STG0AS.BIN`, pilot x 10 +
stage; boxes 496-549 and 1045-1071) and boxes 494-495: its record
(``0x060A5684`` + 4N), the record's header, the line's address and file
offset, and its cells (two bytes each, D-020). For slots 494-551: the
`cybotsu` and `cybotsj` English-table pointers (D-009) and each record's
line lengths. Numbers only; no text is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import build_program, decode, long, read_record
from tools.reference.mame_audit import parse_driver

STG = Path("local/extracted/saturn_jp/STG0AS.BIN")
BASE, RECORDS, CAPTIONS = 0x06060000, 0x060A5684, 0x0609CC22
EN_TABLES = {"cybotsu": 0x0B33AA, "cybotsj": 0x0B3396}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    stg = STG.read_bytes()

    def u32(a: int) -> int:
        return int(struct.unpack_from(">I", stg, a - BASE)[0])

    def u16(a: int) -> int:
        return int(struct.unpack_from(">H", stg, a - BASE)[0])

    where: dict[int, tuple[int, int]] = {}
    for pilot in range(9):
        for stage in range(10):
            box = u16(CAPTIONS + 2 * (pilot * 10 + stage))
            if box:
                where[box] = (pilot, stage)
    boxes = []
    for box in sorted({494, 495, *where}):
        record = u32(RECORDS + 4 * box)
        entry, lines = record + 8, []
        while True:
            line = u32(entry)
            cells = len(stg[line - BASE :].split(b"\0")[0]) // 2
            lines.append(
                {
                    "address": f"0x{line:08X}",
                    "file_offset": f"0x{line - BASE:05X}",
                    "cells": cells,
                }
            )
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
        place = where.get(box)
        boxes.append(
            {
                "box": box,
                "pilot": place[0] if place else None,
                "stage": place[1] if place else None,
                "record": f"0x{record:08X}",
                "header": stg[record - BASE : record + 8 - BASE].hex(),
                "lines": lines,
            }
        )
    driver = args.driver.read_text(encoding="latin-1")
    arcade = {}
    for name, table in EN_TABLES.items():
        romset = parse_driver(driver)[name]
        archives = [args.rompath / f"{name}.zip"]
        if romset.parent:
            archives.append(args.rompath / f"{romset.parent}.zip")
        program = build_program([p for p in archives if p.exists()], romset)
        pointers = {s: long(program, table + 4 * s) for s in range(494, 552)}
        records = {}
        for address in sorted(set(pointers.values())):
            found = read_record(program, address)
            text = decode(found.codes)
            records[f"0x{address:06X}"] = {
                "header": list(found.header),
                "line_lengths": [len(x) for x in text.split("\n")],
                "codes_sha256": hashlib.sha256(found.codes).hexdigest(),
                "slots_pointing_here": sum(
                    long(program, table + 4 * s) == address for s in range(624)
                ),
            }
        arcade[name] = {
            "english_table": f"0x{table:06X}",
            "slots_494_551": {str(s): f"0x{p:06X}" for s, p in pointers.items()},
            "records": records,
        }
    report = {
        "stg0as_sha256": hashlib.sha256(stg).hexdigest(),
        "boxes": boxes,
        "arcade_english": arcade,
    }
    args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(len(boxes), "boxes;", {k: v["records"] for k, v in arcade.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
