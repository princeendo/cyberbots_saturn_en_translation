"""EXP-0067: the attract loop run long from a saved state (no key).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/attract_long.py OUT \\
        [--state STATE] [--frames 48000] [--every 60]

The patched build (D-007) in the silent home with the untouched image (the
attract loop's files and stage art are unchanged in every build; see
`EXP-0067` README), from an attract state, with no input: a screenshot every
EVERY frames to ``OUT/fNNNNNN.png`` and ``OUT/shots.json`` (frame,
SHA-256). Used to see more cycles than the cold boot's five.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument(
        "--state", type=Path, default=Path("local/ref005/session/states/f00025772.mcs")
    )
    parser.add_argument("--frames", type=int, default=48000)
    parser.add_argument("--every", type=int, default=60)
    args = parser.parse_args()
    out: Path = args.out
    session.launch(args.state, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    shots = []
    try:
        for k in range(1, args.frames // args.every + 1):
            agent.frames(args.every)
            agent.wait_halted(60.0)
            path = (out / f"f{k * args.every:06d}.png").resolve()
            agent.screenshot(path)
            shots.append(
                [k * args.every, hashlib.sha256(path.read_bytes()).hexdigest()]
            )
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "shots.json").write_text(json.dumps(shots) + "\n")
    print(len(shots), "screenshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
