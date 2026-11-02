"""EXP-0018: find when the dialogue script is resident in WRAM-H.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/scan_states.py STATES_DIR FILES_DIR

For every ``*.mcs`` in ``STATES_DIR`` (frame order), extracts WRAM-H with the
validated extractor (D-006) and prints, per state: the 26 bytes at
``0x0606F09C`` (M1 line 4) as ``line4``/``other``/``zero``, and for each of
``STG0AS.BIN``, ``VICTORY.BIN`` and ``END.BIN`` (read from ``FILES_DIR``) the
number of bytes that differ from WRAM-H at ``0x06060000`` over the file's
length. Prints JSON lines; nothing is written.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.memory.mcs_extract import REGIONS, extract_region, parse_state

BASE = 0x06060000 - 0x06000000  # offset of the script load base in WRAM-H
LINE4 = 0x0606F09C - 0x06000000
ORIGINAL = bytes.fromhex("8e9f82cd83548343837b815b834f95ba82a98145814581458142")
COPIES = ("STG0AS.BIN", "VICTORY.BIN", "END.BIN")


def main(states: Path, files: Path) -> int:
    copies = {name: (files / name).read_bytes() for name in COPIES}
    for path in sorted(states.glob("*.mcs")):
        wram = extract_region(
            parse_state(path.read_bytes()), REGIONS["wram_h"], "saturn"
        )
        text = wram[LINE4 : LINE4 + len(ORIGINAL)]
        kind = "line4" if text == ORIGINAL else ("zero" if not any(text) else "other")
        diffs = {
            name: sum(
                a != b for a, b in zip(data, wram[BASE : BASE + len(data)], strict=True)
            )
            for name, data in copies.items()
        }
        print(json.dumps({"state": path.name, "line4": kind, **diffs}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
