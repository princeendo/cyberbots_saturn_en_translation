"""EXP-0069: where a VS caption is stored, and how much room its box has.

Run from the repository root (no key):

    ./invenv.sh python research/experiments/EXP-0069/caption_room.py OUT \\
        [--frames 345]

The patched build (D-007) in the silent home with the untouched image. For
each variant, session state 6448 (before a VS screen, `EXP-0067`) is loaded,
pilot 0 and stage 0 are set in both player blocks (``0x060CFFDC`` + ``0x2D2``
and + ``0x2E3``; the second block at + ``0x2F4``), so the reader
``0x0606CAE8`` shows box 496 (``0x0609CC22``), and one change is written to
`STG0AS.BIN`'s RAM copy (loaded at ``0x06060000``):

- ``control``: nothing;
- ``cell``: the caption line's first code replaced by its second;
- ``wide``: the line replaced by 16 copies of its first code;
- ``rows2``, ``rows4``: the box record given 2 or 4 entries (each the
  original line), the earlier entries' words set to ``0xFFFF`` (D-020).

A log-mode PC breakpoint at ``0x0606E6E0`` records the boxes drawn. After
FRAMES frames: a screenshot. Writes ``OUT/caption_room.json`` (the line and
record addresses, the bytes written, each shot's SHA-256).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
STATE = Path("local/ref005/session/states/f00006448.mcs")
STG = Path("local/extracted/saturn_jp/STG0AS.BIN")
BASE, RECORDS, CAPTIONS, BLOCK = 0x06060000, 0x060A5684, 0x0609CC22, 0x060CFFDC
BOX = 496


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, default=345)
    args = parser.parse_args()
    out: Path = args.out
    stg = STG.read_bytes()

    def u32(a: int) -> int:
        return int(struct.unpack_from(">I", stg, a - BASE)[0])

    def u16(a: int) -> int:
        return int(struct.unpack_from(">H", stg, a - BASE)[0])

    assert u16(CAPTIONS) == BOX
    record = u32(RECORDS + 4 * BOX)
    entry = stg[record + 8 - BASE : record + 16 - BASE]
    line = int.from_bytes(entry[0:4], "big")
    text = stg[line - BASE :].split(b"\0")[0]
    more = entry[:4] + b"\xff\xff" + entry[6:]
    variants: dict[str, list[tuple[int, bytes]]] = {
        "control": [],
        "cell": [(line, text[2:4])],
        "wide": [(line, text[0:2] * 16 + b"\0\0")],
        "rows2": [(record + 8, more + entry)],
        "rows4": [(record + 8, more * 3 + entry)],
    }
    rows = []
    session.launch(STATE, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    try:
        for name, writes in variants.items():
            agent.run()
            agent.loadstate(STATE.resolve())
            agent.pause()
            for base in (BLOCK, BLOCK + 0x2F4):
                agent.bus_write(base + 0x2D2, bytes([0]))
                agent.bus_write(base + 0x2E3, bytes([0]))
            for address, data in writes:
                agent.bus_write(address, data)
            agent.bpmode("log")
            agent.breakpoints("pc", ["0606E6E0"])
            agent.clear_events()
            agent.frames(args.frames)
            agent.wait_halted(120.0)
            drawn = [
                int(dict(FIELD.findall(e)).get("R4", "0"), 16)
                for e in agent.events()
                if "PC=0606E6E0" in e
            ]
            agent.breakpoints("pc", [])
            path = (out / f"{name}.png").resolve()
            agent.screenshot(path)
            rows.append(
                {
                    "variant": name,
                    "writes": [
                        {
                            "address": f"0x{a:08X}",
                            "length": len(d),
                            "sha256": hashlib.sha256(d).hexdigest(),
                        }
                        for a, d in writes
                    ],
                    "boxes_drawn": {str(b): drawn.count(b) for b in sorted(set(drawn))},
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
            print(name, drawn, flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    report = {
        "state": str(STATE),
        "box": BOX,
        "record": f"0x{record:08X}",
        "record_header": stg[record - BASE : record + 8 - BASE].hex(),
        "line": f"0x{line:08X}",
        "line_file_offset": f"0x{line - BASE:05X}",
        "line_cells": len(text) // 2,
        "frames": args.frames,
        "variants": rows,
    }
    (out / "caption_room.json").write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
