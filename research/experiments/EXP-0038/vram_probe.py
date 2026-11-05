"""EXP-0038: one controlled VRAM (or RAM) change from a saved state, with screenshots.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/vram_probe.py STATE OUT \\
        [--fill SPACE:OFFSET:LENGTH:BYTE ...] [--shots 2,30,120] \\
        [--dump SPACE:OFFSET:LENGTH ...]

A debug harness; it never ships. It loads ``STATE`` with the untouched image
mounted in the silent home, halts, reads every ``--dump`` region to
``OUT/<space>_<offset>.bin``, applies every ``--fill`` (``LENGTH`` bytes of
``BYTE`` at ``OFFSET`` in the agent address space ``SPACE``: ``vdp1vram``,
``vdp2vram``, ``workraml``, ``workramh``), logging the bytes it replaces,
then runs and takes a screenshot after each ``--shots`` frame count
(``OUT/aNNNN.png``) and reads the filled ranges back at the last one. With no
``--fill`` it is the control. ``--write-bp`` logs write hits (frame, PC,
PR, R4-R6) on those bus ranges while it runs. Writes ``OUT/probe.json``.
"""

from __future__ import annotations

import argparse
import hashlib
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


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    parser.add_argument("--fill", action="append", default=[])
    parser.add_argument("--dump", action="append", default=[])
    parser.add_argument("--shots", default="2,30,120")
    parser.add_argument("--write-bp", help="comma-separated hex bus ranges A-B")
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    fills = []
    for f in args.fill:
        space, offset, length, byte = f.split(":")
        fills.append((space, int(offset, 16), int(length, 16), int(byte, 16)))
    shots = sorted(int(x) for x in args.shots.split(","))
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {
        "state": str(args.state),
        "state_sha256": sha256(args.state.read_bytes()),
        "cue": str(args.cue),
    }
    log_fills, log_shots, log_dumps = [], [], []
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
            agent.pause()
            agent.wait_halted(30.0)
            start = int(agent.status()["frame"])
            if args.write_bp:
                agent.clear_events()
                agent.bpmode("log")
                agent.breakpoints("write", args.write_bp.split(","))
            for d in args.dump:
                space, offset, length = d.split(":")
                data = agent.read(space, int(offset, 16), int(length, 16))
                path = out / f"{space}_{offset}.bin"
                path.write_bytes(data)
                log_dumps.append({"file": path.name, "sha256": sha256(data)})
            for space, offset, length, byte in fills:
                before = agent.read(space, offset, length)
                agent.write(space, offset, bytes([byte]) * length)
                log_fills.append(
                    {
                        "space": space,
                        "offset": f"0x{offset:05X}",
                        "length": length,
                        "byte": f"0x{byte:02X}",
                        "before_sha256": sha256(before),
                        "before_distinct": len(set(before)),
                    }
                )
            done = 0
            for n in shots:
                agent.frames(n - done)
                agent.wait_halted(60.0)
                done = n
                agent.screenshot(out / f"a{n:04d}.png")
                log_shots.append(
                    {"after": n, "frame": int(agent.status()["frame"]) - start}
                )
            hits = [
                dict(re.findall(r"(\w+)=([0-9A-Fa-f]+)", e)) for e in agent.events()
            ]
            result["write_hits"] = [
                {k: h[k] for k in ("frame", "PC", "PR", "R4", "R5", "R6") if k in h}
                for h in hits
            ]
            for item, (space, offset, length, byte) in zip(
                log_fills, fills, strict=True
            ):
                back = agent.read(space, offset, length)
                item["still_filled_at_last_shot"] = back == bytes([byte]) * length
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    result |= {"fills": log_fills, "shots": log_shots, "dumps": log_dumps}
    (out / "probe.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
