"""EXP-0044: log every register at PC breakpoints from a saved state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0044/trace.py STATE OUT \\
        --pc 060114B0,06011654 [--frames 1] [--cue CUE] [--dump SPACE:OFF:LEN]

A debug harness; it never ships. It loads ``STATE`` (default image mounted,
or ``CUE``) in the silent home with log-mode PC breakpoints, runs
``--frames``, and writes every hit's full register line to
``OUT/hits.jsonl``, plus each ``--dump`` region read when the run ends
(``OUT/<space>_<off>.bin``). Built from ``EXP-0038/vram_probe.py``'s
start-up (commit ``865b649``).
"""

from __future__ import annotations

import argparse
import importlib.util
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

_spec = importlib.util.spec_from_file_location(
    "exp0031_loads", Path("research/experiments/EXP-0031/loads.py")
)
assert _spec and _spec.loader
_loads = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_loads)
BINARY, IMAGE = _loads.BINARY, _loads.IMAGE
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--pc", required=True)
    parser.add_argument("--frames", type=int, default=1)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    parser.add_argument("--dump", action="append", default=[])
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
    with (out / "mednafen.log").open("wb") as log:
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
                    time.sleep(0.5)
            time.sleep(3)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("pc", args.pc.split(","))
            agent.frames(args.frames)
            agent.wait_halted(60.0)
            with (out / "hits.jsonl").open("w") as f:
                for e in agent.events():
                    if "PC=" in e:
                        f.write(json.dumps(dict(FIELD.findall(e))) + "\n")
            for item in args.dump:
                space, off, length = item.split(":")
                (out / f"{space}_{off}.bin").write_bytes(
                    agent.read(space, int(off, 16), int(length, 16))
                )
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
