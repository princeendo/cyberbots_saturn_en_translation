"""EXP-0062: a paused Mednafen session from a saved state, for probing.

Run from the repository root (no key; the silent home):

    ./invenv.sh python research/experiments/EXP-0062/session.py launch STATE OUT \\
        [--cue CUE]
    ./invenv.sh python research/experiments/EXP-0062/session.py stop OUT

``launch`` starts the patched build (D-007) on CUE (default: the untouched
image) in the silent home with ``MEDNAFEN_AGENT_DIR=OUT/agent``, loads STATE
and pauses; the PID goes to ``OUT/run.json``. Other scripts then drive
``Agent(OUT/agent)``. ``stop`` ends it.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
UNTOUCHED = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)


def agent_of(out: Path) -> Agent:
    agent = Agent((out / "agent").resolve(), timeout=20.0)
    deadline = time.monotonic() + 30
    while True:
        try:
            agent.status()
            return agent
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.2)


def launch(state: Path, out: Path, cue: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(json.dumps({"pid": process.pid, "cue": str(cue)}))
    agent = agent_of(out)
    if agent.halted():
        agent.run()
    agent.loadstate(state.resolve())
    agent.pause()
    print(agent.status())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["launch", "stop"])
    parser.add_argument("args", nargs="+")
    parser.add_argument("--cue", type=Path, default=UNTOUCHED)
    a = parser.parse_args()
    if a.command == "launch":
        launch(Path(a.args[0]), Path(a.args[1]), a.cue)
    else:
        out = Path(a.args[0])
        os.kill(json.loads((out / "run.json").read_text())["pid"], signal.SIGTERM)
        configure()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
