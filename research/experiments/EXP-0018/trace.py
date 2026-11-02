"""EXP-0018: catch the writes that put the M1 box's text into WRAM-H.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0018/trace.py STATE OUT [--frames N]

Loads ``STATE`` in the patched build's silent home with no input, sets a
halt-mode write breakpoint on M1 line 4 and line 5 (WRAM-H
``0x0606F09C``-``0x0606F0D3`` and its cache-through mirror ``0x2606…``) and runs
up to ``N`` frames (default 400) in 50-frame steps with a screenshot per step.
On the first hit it saves the registers, the stack, both work RAMs and a
screenshot, then switches to log mode and runs the remaining frames, so every
later hit is logged with its PC and registers (``events.log``). The trial
starts before the load (machine select, whose timer picks a machine with no
input); the control starts after the load and expects no hit. Outputs go to
the ignored OUT; ``result.json`` summarizes.

``--extra RANGE`` (repeatable) adds write-breakpoint ranges, for example the CD
block command registers ``25890018-25890027``; ``--log`` logs every hit from the
start instead of halting on the first.
"""

from __future__ import annotations

import argparse
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
TEXT = ("0606F09C-0606F0D3", "2606F09C-2606F0D3")  # lines 4-5 (D-015)
STEP = 50


def connect(agent: Agent, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            agent.status()
            return
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def dump(agent: Agent, out: Path, result: dict[str, object]) -> None:
    regs = agent.regs()
    result["regs"] = {k: f"{v:08X}" for k, v in regs.items()}
    result["stack"] = agent.bus_read(regs["R15"], 64).hex()
    for space in ("workraml", "workramh"):
        agent.command(f"read {space} 0 {1 << 20} {(out / space).resolve()}.bin")
    agent.screenshot(out / "halt.png")


def main(state: Path, out: Path, frames: int, extra: list[str], log_only: bool) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(state), "steps": []}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            connect(agent)
            time.sleep(3)  # let the boot settle before replacing the machine state
            if agent.halted():
                agent.run()
            agent.loadstate(state.resolve())
            result["loaded_frame"] = int(agent.status()["frame"])
            agent.clear_events()
            agent.bpmode("log" if log_only else "halt")
            agent.breakpoints("write", [*TEXT, *extra])
            done = 0
            first_hit = log_only
            while done < frames:
                agent.frames(STEP)
                status = agent.wait_halted(60.0)
                if not first_hit and agent.events():
                    # Halted by the breakpoint, not by the frame count.
                    first_hit = True
                    result["first_hit_status"] = status
                    dump(agent, out, result)
                    agent.bpmode("log")
                    agent.run()
                    continue
                done += STEP
                frame = int(status["frame"])
                agent.screenshot(out / f"f{frame:05d}.png")
                result["steps"].append(frame)  # type: ignore[attr-defined]
            agent.breakpoints("write")
            result["text"] = agent.bus_read(0x0606F09C, 56).hex()
            result["events"] = agent.events()
            agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    events = result.get("events", [])
    print(
        json.dumps(
            {
                "loaded_frame": result.get("loaded_frame"),
                "hits": len(events),  # type: ignore[arg-type]
                "first": events[:3],  # type: ignore[index]
                "first_hit_status": result.get("first_hit_status"),
                "text": result.get("text"),
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, default=400)
    parser.add_argument("--extra", action="append", default=[])
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.state, args.out, args.frames, args.extra, args.log))
