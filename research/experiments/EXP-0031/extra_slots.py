"""EXP-0031: match the arcade dialogue table's slots past 493 to Saturn lines.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0031/extra_slots.py \\
        local/ref003/cybotsj-maincpu.bin local/ref003/cybotsu-maincpu.bin

The Japanese table at ``0x0A30F6`` (D-009) runs to 624 pointers, not the
494 that ``tools.text.arcade_pairing.find_tables`` stops at. For slots
494-623 it decodes each record's lines with ``data/text/arcade_jp_map.json``
and looks for the same bytes among `STG0AS.BIN`'s lines. It also counts the
slots with an English record in the US table at ``0x0B33AA``. Prints counts
and line numbers only, no text.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import decode, long, read_record
from tools.text.arcade_pairing import record_lines

JP_TABLE, EN_TABLE = 0x0A30F6, 0x0B33AA
FIRST, SLOTS = 494, 624


def main(jp_path: Path, us_path: Path) -> int:
    jp, us = jp_path.read_bytes(), us_path.read_bytes()
    run = 0
    while 0x0A0000 <= long(jp, JP_TABLE + 4 * run) < 0x0C0000:
        run += 1
    mapping = {
        int(k, 16): bytes.fromhex(v)
        for k, v in json.loads(Path("data/text/arcade_jp_map.json").read_text()).items()
    }
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    stg = Path("local/extracted/saturn_jp/STG0AS.BIN").read_bytes()
    saturn: dict[bytes, list[int]] = {}
    for n, (off, length, _, _) in enumerate(table):
        saturn.setdefault(stg[off : off + length], []).append(n)
    exact: list[tuple[int, int]] = []
    unmapped = other = 0
    lines = [r for r in record_lines(jp, JP_TABLE, SLOTS) if r[0] >= FIRST]
    for slot, _, codes in lines:
        if any(c not in mapping for c in codes):
            unmapped += 1
            continue
        found = saturn.get(b"".join(mapping[c] for c in codes))
        if found:
            exact += [(slot, n) for n in found]
        else:
            other += 1
    english = sum(
        1
        for k in range(FIRST, SLOTS)
        if decode(read_record(us, long(us, EN_TABLE + 4 * k)).codes).strip()
    )
    print(
        json.dumps(
            {
                "jp_table_pointers": run,
                "record_lines_494_623": len(lines),
                "exact_saturn_matches": len(exact),
                "unmapped_codes": unmapped,
                "no_exact_match": other,
                "saturn_lines": sorted({n for _, n in exact}),
                "slots": sorted({s for s, _ in exact}),
                "us_slots_with_english_494_623": english,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
