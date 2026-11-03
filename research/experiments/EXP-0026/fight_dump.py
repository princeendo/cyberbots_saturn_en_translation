"""EXP-0026: dump work RAM through a fight with no input, to find vitality.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/fight_dump.py STATE OUT [STEPS]

Loads ``STATE`` (a REF-005 state during a fight) on the untouched image in the
patched build's silent home, then runs STEPS (default 40) x 30 frames with no
input. After each step it saves a screenshot and both work RAMs to ``OUT``.
It uses a scratch copy of the silent home (``local/mednafen_fight``).
"""

from __future__ import annotations

import os
import shutil
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


def scratch_home() -> Path:
    """A copy of the silent home, so this can run beside another silent-home run."""
    home = Path("local/mednafen_fight")
    if not home.exists():
        home.mkdir(parents=True)
        shutil.copyfile(QUIET_HOME / "mednafen.cfg", home / "mednafen.cfg")
        (home / "firmware").symlink_to(Path("..") / "mednafen_quiet" / "firmware")
    return home


def main(state: Path, out: Path, steps: int) -> int:
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
            for step in range(1, steps + 1):
                agent.frames(30)
                agent.wait_halted(30.0)
                agent.screenshot(out / f"step{step:02d}.png")
                for space in ("workraml", "workramh"):
                    target = (out / f"{space}-{step:02d}.bin").resolve()
                    agent.command(f"read {space} 0 {1 << 20} {target}")
                agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    raise SystemExit(main(Path(a[0]), Path(a[1]), int(a[2]) if len(a) > 2 else 40))
