"""EXP-0025: replay a state on an image and save the glyph cells at each step.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/replay_cells.py \\
        CUE STATE OUT [STEPS]

Like ``research/experiments/EXP-0022/force_scene.py`` without forcing. It
loads ``STATE`` with ``CUE`` mounted (patched build, silent home), runs STEPS
(default 40) x 25 frames, and after each step saves a screenshot and the 60
glyph cells of the WRAM-H shadow (``0x060FE200``, D-020) to
``OUT/cells-NN.bin``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
CELLS = 0x060FE200


def main(cue: Path, state: Path, out: Path, steps: int) -> int:
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
            agent.loadstate(state.resolve())
            for step in range(1, steps + 1):
                agent.frames(25)
                agent.wait_halted(30.0)
                agent.screenshot(out / f"step{step:02d}.png")
                (out / f"cells-{step:02d}.bin").write_bytes(
                    agent.bus_read(CELLS, 60 * 0x80)
                )
                agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    raise SystemExit(
        main(
            Path(args[0]),
            Path(args[1]),
            Path(args[2]),
            int(args[3]) if len(args) > 3 else 40,
        )
    )
