"""EXP-0076: a pilot's story route forced from REF-005 state 4138 (no key).

Run from the repository root (offline; the silent home, patched build D-007):

    ./invenv.sh python research/experiments/EXP-0076/route.py OUT PILOT \\
        [--frames 3000] [--shots 300] [--write ADDR=HEX ...] [--cue CUE]

State 4138 is the machine select after Jin and BLODIA were chosen in the
REF-005 session, before the story's first post. Loaded and halted in one
exchange (`EXP-0070`), then player 1's pilot bytes are set to PILOT: the
fighter record's ``+0x2D2`` (``0x060D02B2``) and the select cursor
``+0x2E2`` (``0x060D02BE``, `STG0A.BIN` ``0x060621B6``). The run logs every
scene post (`STG0AS.BIN` ``0x0606DBEA``, R4 the list, R5 the scene) and
reads the stage byte ``0x060CFF88`` at the end; a screenshot every
``--shots`` frames. ``--write`` adds bus writes made with the pilot bytes
(for example the body type ``0x060D02BD`` and mech ``0x060D02C1``, player 1's
record ``0x060CFFDC`` + ``0x2E1``/``0x2E5``). Writes ``OUT/route.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
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

STATE = Path("local/ref005/session/states/f00004138.mcs")
PILOT_BYTES = (0x060D02B2, 0x060D02BE)
POST = "0606DBEA"
STAGE = 0x060CFF88
FIELD = re.compile(r"frame=(\d+).*?R4=([0-9A-F]+) R5=([0-9A-F]+)")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("pilot", type=int)
    p.add_argument("--frames", type=int, default=3000)
    p.add_argument("--shots", type=int, default=300)
    p.add_argument("--write", action="append", default=[])
    p.add_argument("--cue", type=Path, default=session.UNTOUCHED)
    a = p.parse_args()
    out: Path = a.out
    session.launch(STATE, out, a.cue)
    agent = session.agent_of(out)
    report: dict[str, Any] = {"state": str(STATE), "pilot": a.pilot}
    try:
        agent.run()
        agent.command(f"loadstate {STATE.resolve()}", "pause")
        agent.wait_halted(30.0)
        report["before"] = [agent.bus_read(x, 1)[0] for x in PILOT_BYTES]
        for x in PILOT_BYTES:
            agent.bus_write(x, bytes([a.pilot]))
        writes = [w.split("=") for w in a.write]
        report["writes"] = a.write
        report["before_writes"] = {
            w: agent.bus_read(int(x, 16), len(bytes.fromhex(v))).hex()
            for w, (x, v) in zip(a.write, writes, strict=True)
        }
        for x, v in writes:
            agent.bus_write(int(x, 16), bytes.fromhex(v))
        agent.clear_events()
        agent.bpmode("log")
        agent.breakpoints("pc", [POST])
        shots = []
        for n in range(0, a.frames, a.shots):
            agent.frames(a.shots)
            agent.wait_halted(300.0)
            path = (out / f"f{n + a.shots:05d}.png").resolve()
            agent.screenshot(path)
            shots.append(
                {
                    "after": n + a.shots,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        agent.breakpoints("pc", [])
        posts = []
        for e in agent.events():
            if (m := FIELD.search(e)) and f"PC={POST}" in e:
                posts.append(
                    {
                        "frame": int(m.group(1)),
                        "list": int(m.group(2), 16),
                        "scene": int(m.group(3), 16),
                    }
                )
        report["posts"] = posts
        report["stage_byte"] = agent.bus_read(STAGE, 1)[0]
        report["shots"] = shots
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "route.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "shots"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
