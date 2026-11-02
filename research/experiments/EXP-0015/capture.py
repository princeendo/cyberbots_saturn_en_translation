"""EXP-0015: save named checkpoints around the M1 box from one session state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0015/capture.py STATE OUT

Launches the patched build (agent interface, D-007) in the silent home, loads
``STATE``, and for each checkpoint runs to its frame offset (``frames``
halts), takes a screenshot, resumes, and saves a state immediately (the agent
refuses ``savestate`` while halted), then takes a second screenshot. Writes
``OUT/<name>.mcs``, ``OUT/<name>-halt.png``, ``OUT/<name>-saved.png`` and
``OUT/capture.json`` with the frame numbers. Mednafen is closed afterwards.
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
# (name, frames after the load): box open and empty, box complete, reply.
CHECKPOINTS = (("a-box-open", 10), ("b-box-complete", 200), ("c-after-box", 420))


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


def main(state: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    record: dict[str, object] = {"state": str(state), "checkpoints": []}
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
            loaded = int(agent.status()["frame"])
            done = 0
            for name, offset in CHECKPOINTS:
                agent.frames(offset - done)
                halted = agent.wait_halted(30.0)
                agent.screenshot(out / f"{name}-halt.png")
                agent.run()
                agent.savestate(out / f"{name}.mcs")
                saved = agent.status()
                agent.screenshot(out / f"{name}-saved.png")
                done = offset
                record["checkpoints"].append(  # type: ignore[attr-defined]
                    {
                        "name": name,
                        "offset": offset,
                        "loaded_frame": loaded,
                        "halted_frame": int(halted["frame"]),
                        "saved_frame": int(saved["frame"]),
                    }
                )
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "capture.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
