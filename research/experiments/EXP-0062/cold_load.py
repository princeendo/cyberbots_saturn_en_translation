"""EXP-0062: cold-boot the untouched image with a given internal save (no key).

Run from the repository root (a cold boot: ask the user first):

    ./invenv.sh python research/experiments/EXP-0062/cold_load.py OUT BKR [--until 2000]

A scratch copy of the silent home with BKR as its internal backup memory;
the patched build (D-007) cold-boots the untouched image with no state.
Log-mode PC breakpoints at the save check ``0x06036C3E``, the warning
picture ``0x06036DA8`` and the accepted path ``0x06037064``. At frame
``--until``: ``0x060D9290``-``9F`` and a screenshot. Writes
``OUT/cold.json``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError

_spec = importlib.util.spec_from_file_location(
    "save_test", Path("research/experiments/EXP-0062/save_test.py")
)
assert _spec and _spec.loader
save_test = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(save_test)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("bkr", type=Path)
    parser.add_argument("--until", type=int, default=2000)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    home = save_test.scratch_home(out / "home")
    target = next((home / "sav").glob("*.bkr"))
    shutil.copyfile(args.bkr, target)
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(save_test.BINARY), str(save_test.UNTOUCHED)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    agent = Agent((out / "agent").resolve(), timeout=20.0)
    deadline = time.monotonic() + 30
    while True:
        try:
            agent.status()
            break
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.2)
    agent.bpmode("log")
    agent.breakpoints("pc", ["06036C3E", "06036DA8", "06037064"])
    agent.clear_events()
    if agent.halted():
        agent.run()
    while int(agent.status()["frame"]) < args.until:
        time.sleep(0.5)
    agent.pause()
    hits = []
    for e in agent.events():
        f = dict(FIELD.findall(e))
        if "PC" in f:
            hits.append({"PC": f["PC"], "R4": f.get("R4"), "frame": f.get("frame")})
    settings = agent.bus_read(0x060D9290, 16)
    agent.screenshot((out / "after.png").resolve())
    frame = int(agent.status()["frame"])
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=30)
    report = {
        "bkr": str(args.bkr),
        "frame": frame,
        "hits": hits[:12],
        "settings_ram": settings.hex(),
    }
    (out / "cold.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
