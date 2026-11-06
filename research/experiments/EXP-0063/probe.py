"""EXP-0063: probes for where the name art is loaded and where it could live.

Run from the repository root (no key; the silent home; session states in
``local/ref005/session/states``):

    ./invenv.sh python research/experiments/EXP-0063/probe.py loads OUT STATE FRAMES
    ./invenv.sh python research/experiments/EXP-0063/probe.py stack OUT STATE RANGE
    ./invenv.sh python research/experiments/EXP-0063/probe.py tailimage OUT_DIR
    ./invenv.sh python research/experiments/EXP-0063/probe.py tail OUT CUE [--move]
    ./invenv.sh python research/experiments/EXP-0063/probe.py slack OUT STATE

- ``loads``: log-mode PC breakpoints on the named loader ``0x060385A0`` and
  its open ``0x06038E40``; each hit with the name at R4, R5 (destination),
  R6 (maximum) and PR.
- ``stack``: halt at the first write to RANGE; the registers and the code
  addresses on the stack.
- ``tailimage``: the untouched image with a copy of ``M3CB00A.BIN`` in Track
  01's last 150 sectors (from LSN 43,643), EDC/ECC regenerated; other tracks
  linked.
- ``tail``: from state 6448, optionally (``--move``) the game's directory
  entry for ``M3CB00A.BIN`` (index 133) pointed at LSN 43,643; RAM at
  ``0x06070800`` compared with the file at frames 425-441.
- ``slack``: ``0xAA`` written over the 288 bytes after ``PL3F_0.BIN``'s end
  in WRAM-L before its load (state 6448); what is there 200 frames later.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc.patch_image import replace_files

_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
STATES = Path("local/ref005/session/states")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
TAIL = 43643
M3 = Path("local/extracted/saturn_jp/M3CB00A.BIN")


def stop(out: Path) -> None:
    os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
    time.sleep(3)


def hits(agent) -> list[dict[str, str]]:  # type: ignore[no-untyped-def]
    found = [dict(FIELD.findall(e)) for e in agent.events()]
    return [f for f in found if "PC" in f]


def loads(out: Path, state: Path, frames: int) -> object:
    session.launch(state, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    try:
        agent.bpmode("log")
        agent.breakpoints("pc", ["060385A0", "06038E40"])
        agent.clear_events()
        agent.frames(frames)
        agent.wait_halted(200.0)
        rows = []
        for f in hits(agent):
            name = agent.bus_read(int(f["R4"], 16), 16).split(b"\0")[0]
            rows.append([f["frame"], f["PC"], name.decode(), f["R5"], f["R6"], f["PR"]])
        return rows
    finally:
        stop(out)


def stack(out: Path, state: Path, watch: str) -> object:
    session.launch(state, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    try:
        agent.bpmode("halt")
        agent.breakpoints("write", [watch])
        agent.frames(120)
        agent.wait_halted(200.0)
        regs = agent.regs()
        raw = agent.bus_read(regs["R15"], 256)
        words = [struct.unpack_from(">I", raw, i)[0] for i in range(0, 256, 4)]
        agent.breakpoints("write", [])
        return {
            "frame": agent.status()["frame"],
            "PC": hex(regs["PC"]),
            "PR": hex(regs["PR"]),
            "stack_code": [hex(w) for w in words if 0x06004000 <= w < 0x06080000],
        }
    finally:
        stop(out)


def tailimage(out_dir: Path) -> object:
    source = session.UNTOUCHED.parent
    out_dir.mkdir(parents=True, exist_ok=False)
    data = M3.read_bytes()
    changed = replace_files(source / TRACK, out_dir / TRACK, [(TAIL, len(data), data)])
    for p in source.iterdir():
        if p.name != TRACK:
            if p.suffix == ".cue":
                shutil.copy(p, out_dir / p.name)
            else:
                os.symlink(p.resolve(), out_dir / p.name)
    digest = hashlib.sha256((out_dir / TRACK).read_bytes()).hexdigest()
    return {"sectors_changed": len(changed), "track01_sha256": digest}


def tail(out: Path, cue: Path, move: bool) -> object:
    data = M3.read_bytes()
    session.launch(STATES / "f00006448.mcs", out, cue)
    agent = session.agent_of(out)
    try:
        entry = 0x060DCB68 + 24 * 133
        if move:
            agent.bus_write(entry, (TAIL + 150).to_bytes(4, "big"))
        rows, done = [], 0
        for frame in (425, 430, 436, 441):
            agent.frames(frame - done)
            agent.wait_halted(200.0)
            done = frame
            ram = agent.bus_read(0x06070800, len(data))
            same = sum(
                1
                for i in range(0, len(data), 2048)
                if ram[i : i + 2048] == data[i : i + 2048]
            )
            rows.append([frame, ram == data, same])
        return rows
    finally:
        stop(out)


def slack(out: Path, state: Path) -> object:
    session.launch(state, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    try:
        end = 0x00200000 + 333536
        agent.bus_write(end, b"\xaa" * (288 + 16))
        agent.frames(200)
        agent.wait_halted(200.0)
        after = agent.bus_read(end, 288 + 16)
        return {"aa_kept": after.count(0xAA), "of": len(after)}
    finally:
        stop(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=["loads", "stack", "tailimage", "tail", "slack"]
    )
    parser.add_argument("args", nargs="+")
    parser.add_argument("--move", action="store_true")
    a = parser.parse_args()
    out = Path(a.args[0])
    if a.command == "loads":
        result = loads(out, Path(a.args[1]), int(a.args[2]))
    elif a.command == "stack":
        result = stack(out, Path(a.args[1]), a.args[2])
    elif a.command == "tailimage":
        result = tailimage(out)
    elif a.command == "tail":
        result = tail(out, Path(a.args[1]), a.move)
    else:
        result = slack(out, Path(a.args[1]))
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
