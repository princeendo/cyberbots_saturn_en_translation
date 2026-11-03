"""EXP-0026: show another pilot's story scene on an image, to check its Japanese.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/other_pilot.py CUE OUT PILOT SCENE

A debug harness; it never ships. It loads REF-005 state 4138 (machine select,
before `STG0AS.BIN` loads) with ``CUE`` mounted, in the scratch home
``local/mednafen_fight``. After 450 frames (the load is done; the first scene
is not posted until about frame 600 after the load), it points pilot 0's
entry in the per-pilot scene-list table (``0x060AAD24``, D-021) at
``PILOT``'s list. It forces the next scene to ``SCENE`` as
``force_check.py`` does, then runs 150 x 25 frames, saving a screenshot and
the 60 glyph cells (WRAM-H ``0x060FE200``) after each step.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from fight_dump import BINARY, scratch_home

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import configure

STATE = Path("local/ref005/session/states/f00004138.mcs")
PILOT_LISTS = 0x060AAD24
SCENE_BYTE = 0x0600828B


def main(cue: Path, out: Path, pilot: int, scene: int) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(scratch_home().resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.loadstate(STATE.resolve())
            agent.frames(450)
            agent.wait_halted(30.0)
            target = agent.bus_read(PILOT_LISTS + 4 * pilot, 4)
            agent.bus_write(PILOT_LISTS, target)
            agent.bpmode("log")
            agent.breakpoints("write", ["0600828B-0600828B", "2600828B-2600828B"])
            agent.onhit_write(None, SCENE_BYTE, bytes([scene]))
            agent.run()
            for step in range(1, 151):
                agent.frames(25)
                agent.wait_halted(30.0)
                agent.screenshot(out / f"step{step:03d}.png")
                (out / f"cells-{step:03d}.bin").write_bytes(
                    agent.bus_read(0x060FE200, 60 * 0x80)
                )
                agent.run()
            (out / "events.txt").write_text("\n".join(agent.events()) + "\n")
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), int(a[2]), int(a[3])))
