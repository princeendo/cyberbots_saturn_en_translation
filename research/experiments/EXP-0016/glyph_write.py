"""EXP-0016: zero one glyph cell of the M1 box in VDP1 VRAM and look.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0016/glyph_write.py STATE OUT

Loads ``STATE`` (checkpoint B, box complete) in the patched build's silent
home, runs 30 frames, screenshots (``before.png``), then, halted, reads and
zeroes the 128 bytes of the first glyph cell at VDP1 VRAM ``0x1E200``, runs
2 frames (``after-2.png``) and 60 more (``after-62.png``), then restores the
original bytes and runs 2 frames (``restored.png``). ``result.json`` records
the bytes read before and after each write.
"""

from __future__ import annotations

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
CELL = 0x1E200  # first glyph cell of the box text (EXP-0016)
CELL_BYTES = 128  # 16 x 16 pixels at 4 bpp


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


def advance(agent: Agent, frames: int, shot: Path) -> int:
    agent.frames(frames)
    status = agent.wait_halted(30.0)
    agent.screenshot(shot)
    return int(status["frame"])


def main(state: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(state), "cell": f"0x{CELL:05X}"}
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
            result["before_frame"] = advance(agent, 30, out / "before.png")
            original = agent.read("vdp1vram", CELL, CELL_BYTES)
            agent.write("vdp1vram", CELL, bytes(CELL_BYTES))
            result["original"] = original.hex()
            result["written_readback"] = agent.read("vdp1vram", CELL, CELL_BYTES).hex()
            result["after_2_frame"] = advance(agent, 2, out / "after-2.png")
            result["after_2_readback"] = agent.read("vdp1vram", CELL, CELL_BYTES).hex()
            result["after_62_frame"] = advance(agent, 60, out / "after-62.png")
            result["after_62_readback"] = agent.read("vdp1vram", CELL, CELL_BYTES).hex()
            agent.write("vdp1vram", CELL, original)
            result["restored_frame"] = advance(agent, 2, out / "restored.png")
            agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if "readback" not in k and k != "original"
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
