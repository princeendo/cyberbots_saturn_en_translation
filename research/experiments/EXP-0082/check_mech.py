"""EXP-0082: the unlock mech's VS name on the built image, both NAMES settings.

Run from the repository root (no key, no cold boot):

    ./invenv.sh python research/experiments/EXP-0082/check_mech.py OUT \\
        --build build/sp017/a [--frames 3000] [--shots 100]

As ``EXP-0072/check_signs.py`` (the built image in the silent home, each
state loaded and halted in one agent exchange):

1. **Boot** (REF-005 state 384): 1,400 frames, then the game's directory
   entries 326-330 and count are read (they list the tail files).
2. For NAMES = 0 (ENGLISH) and 1 (JAPANESE): REF-005 state 4138 (machine
   select with Jin, before `STG0AS.BIN` loads) is loaded; every `CYBER.BIN`
   change of ``names_switch_changes.json``, the directory entries and count
   are written (the state holds the untouched ones); then the NAMES byte
   ``0x060D9295``, player 1's body ``0x060D02BD`` = 8 and mech
   ``0x060D02C1`` = 16 (`EXP-0076`). The run goes on to the VS screen; a
   screenshot every ``--shots`` frames.

Writes ``OUT/mech.json`` (the screenshots' hashes); the screens are
reviewed by the agent.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)

STATES = Path("local/ref005/session/states")
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
TABLE, ENTRY, COUNT = 0x060DCB68, 24, 0x060DBC58
NAMES = 0x060D9295
WRITES = {0x060D02BD: 8, 0x060D02C1: 16}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--build", type=Path, required=True)
    p.add_argument("--frames", type=int, default=3000)
    p.add_argument("--shots", type=int, default=100)
    a = p.parse_args()
    out: Path = a.out
    build: Path = a.build
    sw = json.loads((build / "names_switch_changes.json").read_text())
    cyber = [c for c in sw["changes"] if c["file"] == "CYBER.BIN"]
    session.launch(STATES / "f00000384.mcs", out, build / CUE)
    agent = session.agent_of(out)
    report: dict[str, Any] = {"build": str(build)}
    try:
        agent.frames(1400)
        agent.wait_halted(300.0)
        raw = agent.bus_read(TABLE + ENTRY * 326, ENTRY * 5)
        count = agent.bus_read(COUNT, 4)
        report["directory"] = [
            raw[ENTRY * k + 12 : ENTRY * (k + 1)].split(b"\0")[0].decode()
            for k in range(5)
        ]
        for names in (0, 1):
            agent.run()
            agent.command(f"loadstate {(STATES / 'f00004138.mcs').resolve()}", "pause")
            agent.wait_halted(30.0)
            for c in cyber:
                agent.bus_write(int(c["address"], 16), bytes.fromhex(c["new"]))
            agent.bus_write(TABLE + ENTRY * 326, raw)
            agent.bus_write(COUNT, count)
            agent.bus_write(NAMES, bytes([names]))
            for addr, value in WRITES.items():
                agent.bus_write(addr, bytes([value]))
            shots = []
            for n in range(a.shots, a.frames + 1, a.shots):
                agent.frames(a.shots)
                agent.wait_halted(300.0)
                path = (out / f"names{names}-{n:05d}.png").resolve()
                agent.screenshot(path)
                shots.append(
                    {
                        "after": n,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
            report[f"names_{names}"] = shots
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "mech.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report["directory"]))
    for names in (0, 1):
        print(names, [(s["after"], s["sha256"][:8]) for s in report[f"names_{names}"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
