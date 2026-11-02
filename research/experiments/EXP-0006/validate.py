"""EXP-0006: validate the patched agent interface on Cyberbots (V1 smoke, V2-V4).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0006/validate.py OUT_DIR

Launches the patched build in the silent home with a fresh agent directory,
runs the checks, writes ``OUT_DIR/result.json``, and stops Mednafen with
SIGTERM. Outputs (dumps, state, screenshot, log) stay under the ignored
OUT_DIR. V1's stock-equivalence half is a separate `cold_boot` run.

Copied from the XvSF repository, ``research/experiments/EXP-0006/validate.py``
at commit ``a1c82ba``. Changed: the image, the title frame, the V4 ranges
(Cyberbots WRAM-H bytes that changed between two title freezes, ``EXP-0004``
run A2 and ``EXP-0005`` run H), and the V4 report (hits per range, PCs).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError, parse_pairs

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
HOME = Path("local/mednafen_quiet")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
TITLE_FRAME = 3700  # about 62 s: the title with PRESS START (EXP-0001, 062-067)
WRITE_OFFSET = 0xF0000  # WRAM-H offset used by EXP-0004's write test
PATTERN = b"EMU-021 WRITE OK"
# WRAM-H bytes outside the stack that differ between the EXP-0004 A2 and
# EXP-0005 H title freezes, with their cache-through mirrors.
BP_RANGES = (
    "060CFED0-060CFEFF",
    "060D3150-060D3153",
    "060DF7E0-060DF7EB",
    "260CFED0-260CFEFF",
    "260D3150-260D3153",
    "260DF7E0-260DF7EB",
)
V4_FRAMES = 1800  # 30 s from about 62 s: title, then the attract loop
WRAMH_RANGES = ("06000000-060FFFFF", "26000000-260FFFFF")


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


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    for stale in (HOME / "sav").glob("*"):
        stale.unlink()
    result: dict[str, object] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            connect(agent)
            # V1 smoke.
            result["v1"] = {
                "status": agent.status(),
                "spaces": agent.spaces(),
                "regs": {k: f"{v:08X}" for k, v in agent.regs().items()},
            }
            # Run to the title by frame count.
            frame0 = int(agent.status()["frame"])
            agent.frames(TITLE_FRAME - frame0)
            halted = agent.wait_halted(120.0)
            agent.run()
            # V2: reads, state and screenshot in one poll (one instant).
            names = {"workraml": "wram_l", "workramh": "wram_h"}
            names |= {"vdp1vram": "vdp1_vram", "vdp2vram": "vdp2_vram"}
            spaces = set(result["v1"]["spaces"])  # type: ignore[index]
            reads = [
                f"read {space} 0 {0x100000 if space.startswith('work') else 0x80000}"
                f" {(out / (name + '.bin')).resolve()}"
                for space, name in names.items()
                if space in spaces
            ]
            replies = agent.command(
                *reads,
                f"savestate {(out / 'v2.mc0').resolve()}",
                f"screenshot {(out / 'v2.png').resolve()}",
                "status",
            )
            result["v2"] = {"halted_at": halted, "replies": replies}
            # V3: paused write round trip and halt control.
            agent.pause()
            before = agent.read("workramh", WRITE_OFFSET, len(PATTERN))
            agent.write("workramh", WRITE_OFFSET, PATTERN)
            written = agent.read("workramh", WRITE_OFFSET, len(PATTERN))
            agent.write("workramh", WRITE_OFFSET, before)
            restored = agent.read("workramh", WRITE_OFFSET, len(PATTERN))
            paused = agent.status()
            agent.step()
            stepped = agent.status()
            agent.run()
            running = agent.status()
            start = int(agent.status()["frame"])
            agent.frames(30)
            after = agent.wait_halted(30.0)
            try:
                agent.savestate(out / "refused.mc0")
                refused = "accepted"
            except AgentError as error:
                refused = str(error)
            result["v3"] = {
                "before": before.hex(),
                "written": written.hex(),
                "restored": restored.hex(),
                "round_trip": written == PATTERN and restored == before,
                "paused": paused,
                "stepped": stepped,
                "running": running,
                "frames_start": start,
                "frames_halted": after,
                "savestate_while_halted": refused,
            }
            # V4: breakpoint log, continuing.
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", BP_RANGES)
            agent.run()
            agent.frames(V4_FRAMES)
            agent.wait_halted(60.0)
            agent.breakpoints("write")
            agent.bpmode("halt")
            hits = [line for line in agent.events() if line.startswith("hit")]
            result["v4"] = {
                "ranges": BP_RANGES,
                "hits": len(hits),
                "first_hits": hits[:5],
                "last_hits": hits[-3:],
                "pcs": sorted({parse_pairs(h).get("PC", "") for h in hits}),
            }
            # V4b: halt mode on all of WRAM-H, as EXP-0004 run F did by hand.
            agent.clear_events()
            agent.breakpoints("write", WRAMH_RANGES)
            agent.run()
            stop = agent.wait_halted(30.0)
            regs = agent.regs()
            agent.breakpoints("write")
            result["v4b"] = {
                "ranges": WRAMH_RANGES,
                "status": stop,
                "events": agent.events()[:3],
                "regs": {k: f"{v:08X}" for k, v in regs.items()},
            }
        finally:
            process.send_signal(signal.SIGTERM)
            result["exit_code"] = process.wait(timeout=30)
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
