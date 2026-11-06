"""EXP-0056: load a state, write RAM, run, and take screenshots (no keys).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0056/poke.py OUT --state STATE \\
        [--write ADDR=HEX ...] [--every-frame] [--frames 120] [--shots 30,60,120] \\
        [--cue CUE] [--vdp1-at FRAME]

A debug harness; it never ships. It starts the patched build (D-007) in the
silent home with CUE (default: the untouched image), loads STATE, makes the
writes (bus addresses in work RAM; once, or after every 10-frame step with
``--every-frame``), runs ``--frames`` frames in 10-frame steps and takes a
screenshot at each frame of ``--shots`` (relative to the load), plus VDP1
VRAM at ``--vdp1-at``. Writes ``OUT/poke.json`` with what was written and
the screenshots' hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--write", action="append", default=[])
    parser.add_argument("--every-frame", action="store_true")
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--shots", default="30,60,120")
    parser.add_argument("--cue", type=Path, default=IMAGE)
    parser.add_argument("--vdp1-at", type=int)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    writes = [
        (int(a, 16), bytes.fromhex(d)) for a, d in (w.split("=") for w in args.write)
    ]
    shots = sorted(int(s) for s in args.shots.split(",") if s)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    record: dict[str, object] = {
        "state": str(args.state),
        "state_sha256": hashlib.sha256(args.state.read_bytes()).hexdigest(),
        "cue": str(args.cue),
        "writes": args.write,
        "every_frame": args.every_frame,
    }
    taken: dict[str, str] = {}
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
                    time.sleep(0.2)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.pause()
            before = {f"0x{a:08X}": agent.bus_read(a, len(d)).hex() for a, d in writes}
            record["before"] = before
            for a, d in writes:
                agent.bus_write(a, d)
            done = 0
            while done < args.frames:
                agent.frames(10)
                agent.wait_halted(30.0)
                done += 10
                if args.every_frame:
                    for a, d in writes:
                        agent.bus_write(a, d)
                if done in shots:
                    path = out / f"s{done:04d}.png"
                    agent.screenshot(path.resolve())
                    taken[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
                if args.vdp1_at == done:
                    (out / f"vdp1_{done:04d}.bin").write_bytes(
                        agent.read("vdp1vram", 0, 0x80000)
                    )
        finally:
            process.terminate()
            process.wait(timeout=30)
    record["shots"] = taken
    (out / "poke.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
