"""EXP-0064: RAM bytes that hold one value in every saved state.

Run from the repository root (no key; the silent home):

    ./invenv.sh python research/experiments/EXP-0064/census.py OUT \\
        [--states DIR ...] [--extra STATE ...] [--min 256] [--out-json PATH]

One Mednafen process (the patched build, D-007) on the untouched image loads
each state in turn (default: every state in ``local/ref005/session/states``,
plus ``--extra`` states) and reads WRAM-H (``0x06000000``, 1 MiB) and WRAM-L
(``0x00200000``, 1 MiB). A byte is constant if it has the same value in
every state. Writes the runs of constant bytes of at least ``--min`` bytes:
start, end, length, and whether all zero (else the most common value), to
``OUT/census.json``. A constant run is only a candidate: the states are
snapshots, so a range used between them can still look constant.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)

REGIONS = {"wramh": (0x06000000, 0x100000), "wraml": (0x00200000, 0x100000)}


def runs(first: bytes, changed: bytes, base: int, minimum: int) -> list[dict]:
    out = []
    i, n = 0, len(first)
    while i < n:
        if changed[i]:
            i += 1
            continue
        j = i
        while j < n and not changed[j]:
            j += 1
        if j - i >= minimum:
            piece = first[i:j]
            common, count = Counter(piece).most_common(1)[0]
            out.append(
                {
                    "start": f"0x{base + i:08X}",
                    "end": f"0x{base + j:08X}",
                    "length": j - i,
                    "all_zero": count == len(piece) and common == 0,
                    "common_byte": f"0x{common:02X}",
                    "common_share": round(count / len(piece), 3),
                }
            )
        i = j
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--states", type=Path, action="append")
    parser.add_argument("--extra", type=Path, action="append", default=[])
    parser.add_argument("--min", type=int, default=256)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    dirs = args.states or [Path("local/ref005/session/states")]
    states = [p for d in dirs for p in sorted(d.glob("*.mcs"))] + args.extra
    session.launch(states[0], args.out, session.UNTOUCHED)
    agent = session.agent_of(args.out)
    first: dict[str, bytes] = {}
    diff = {k: 0 for k in REGIONS}
    try:
        for state in states:
            agent.run()
            agent.loadstate(state.resolve())
            agent.pause()
            for key, (base, size) in REGIONS.items():
                data = agent.bus_read(base, size)
                if key not in first:
                    first[key] = data
                    continue
                now = int.from_bytes(data, "big")
                diff[key] |= now ^ int.from_bytes(first[key], "big")
            print(state.name, flush=True)
    finally:
        os.kill(json.loads((args.out / "run.json").read_text())["pid"], 15)
    changed = {
        key: diff[key].to_bytes(size, "big") for key, (_, size) in REGIONS.items()
    }
    report = {
        "states": [str(s) for s in states],
        "min": args.min,
        "regions": {
            key: runs(first[key], changed[key], base, args.min)
            for key, (base, _) in REGIONS.items()
        },
    }
    text = json.dumps(report, indent=1)
    (args.out / "census.json").write_text(text + "\n")
    if args.out_json:
        args.out_json.write_text(text + "\n")
    for key, rows in report["regions"].items():
        rows = sorted(rows, key=lambda r: -r["length"])
        print(key, len(rows), "runs; largest:")
        for r in rows[:12]:
            print("  ", r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
