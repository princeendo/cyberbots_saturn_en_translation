"""EXP-0026: test candidate opponent-vitality words by setting them to 0 in a fight.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/ko_test.py \\
        STATE OUT ADDR [ADDR ...]

Loads ``STATE`` on the untouched image (scratch home ``local/mednafen_fight``),
runs 900 frames into the fight with no input, writes 0 to each 16-bit word at
``ADDR``, then runs 40 x 30 frames, with a screenshot after each.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from fight_dump import BINARY, IMAGE, scratch_home

from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import configure


def main(state: Path, out: Path, addresses: list[int]) -> int:
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
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.frames(900)
            agent.wait_halted(60.0)
            agent.screenshot(out / "before.png")
            for address in addresses:
                agent.bus_write(address, bytes(2))
            agent.run()
            for step in range(1, 41):
                agent.frames(30)
                agent.wait_halted(30.0)
                agent.screenshot(out / f"step{step:02d}.png")
                agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), [int(x, 16) for x in a[2:]]))
