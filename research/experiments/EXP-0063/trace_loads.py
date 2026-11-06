"""EXP-0063: log the file requests made after a saved state (no key).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0063/trace_loads.py OUT STATE FRAMES \\
        [--pc 06032E38 ...] [--cue CUE]

Log-mode PC breakpoints (default: the request routine ``0x06032E38``) over
FRAMES frames after STATE in the silent home; each hit's frame, R4-R7 and
PR, with the file name for R4 from the game's directory copy
(``0x060DCB68``, 24-byte entries, name at +12). Writes ``OUT/loads.json``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("state", type=Path)
    parser.add_argument("frames", type=int)
    parser.add_argument("--pc", action="append", default=[])
    parser.add_argument("--cue", type=Path, default=session.UNTOUCHED)
    args = parser.parse_args()
    session.launch(args.state, args.out, args.cue)
    agent = session.agent_of(args.out)
    try:
        table = agent.bus_read(0x060DCB68, 24 * 384)
        names = {
            i: table[24 * i + 12 : 24 * i + 24].split(b"\0")[0].decode("latin-1")
            for i in range(384)
        }
        agent.bpmode("log")
        agent.breakpoints("pc", args.pc or ["06032E38"])
        agent.clear_events()
        agent.frames(args.frames)
        agent.wait_halted(120.0)
        hits = []
        for e in agent.events():
            f = dict(FIELD.findall(e))
            if "PC" not in f:
                continue
            r4 = int(f.get("R4", "0"), 16)
            hits.append(
                {
                    "frame": int(f["frame"]),
                    "PC": f["PC"],
                    "R4": f.get("R4"),
                    "R5": f.get("R5"),
                    "R6": f.get("R6"),
                    "R7": f.get("R7"),
                    "PR": f.get("PR"),
                    "name": names.get(r4, ""),
                }
            )
    finally:
        session.main.__globals__["os"].kill(
            json.loads((args.out / "run.json").read_text())["pid"], 15
        )
    (args.out / "loads.json").write_text(json.dumps(hits, indent=1) + "\n")
    for h in hits:
        print(h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
