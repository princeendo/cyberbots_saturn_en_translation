"""EXP-0056: log PC breakpoint hits (all registers) from a state (no keys).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0056/trace.py OUT --state STATE \\
        --pc ADDR[,ADDR...] [--frames 2] [--read-bp A-B] [--write-bp A-B] \\
    [--write ADDR=HEX ...]

A debug harness; it never ships. Loads STATE in the silent home (patched
build, D-007, untouched image), makes the ``--write`` RAM writes, sets
log-mode PC (and optionally read or write) breakpoints, runs ``--frames``
frames and writes every hit's fields to ``OUT/hits.jsonl``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--pc", default="")
    parser.add_argument("--read-bp")
    parser.add_argument("--write-bp")
    parser.add_argument("--frames", type=int, default=2)
    parser.add_argument("--write", action="append", default=[], help="ADDR=HEX")
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    count = 0
    with (
        (out / "mednafen.log").open("wb") as log,
        (out / "hits.jsonl").open("w") as hits,
    ):
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.2)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.pause()
            for item in args.write:
                address, data = item.split("=")
                agent.bus_write(int(address, 16), bytes.fromhex(data))
            agent.bpmode("log")
            if args.pc:
                agent.breakpoints("pc", args.pc.split(","))
            if args.read_bp:
                agent.breakpoints("read", args.read_bp.split(","))
            if args.write_bp:
                agent.breakpoints("write", args.write_bp.split(","))
            agent.clear_events()
            agent.frames(args.frames)
            agent.wait_halted(60.0)
            for e in agent.events():
                f = dict(FIELD.findall(e))
                if "PC" in f:
                    hits.write(json.dumps(f) + "\n")
                    count += 1
        finally:
            process.terminate()
            process.wait(timeout=30)
    print(out, "hits", count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
