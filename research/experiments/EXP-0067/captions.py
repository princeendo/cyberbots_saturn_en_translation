"""EXP-0067: every VS chapter caption, drawn as the current image draws it.

Run from the repository root (no key):

    ./invenv.sh python research/experiments/EXP-0067/captions.py OUT \\
        [--build build/opt005/a] [--frames 345]

The patched build (D-007) in the silent home with the current image. For
each pilot 0-8 and stage 0-8 of the caption table (``0x0609CC22``, words,
pilot x 10 + stage; `STG0AS.BIN`): session state 6448 (before a VS screen)
is loaded; the current image's font (`KANJI.BIN`, to VDP2 VRAM ``0x40000``,
D-019) and its code table (`STG0AS.BIN` ``0x4AD7C``, 1,222 words, to
``0x060AAD7C``) are written in, since the state holds the untouched ones;
the pilot and stage bytes of both player blocks (``0x060CFFDC`` + ``0x2D2``
and + ``0x2E3``, and the second block at + ``0x2F4``) are set. A log-mode PC
breakpoint at ``0x0606E6E0`` (called by the reader ``0x0606CAE8`` with R4 =
the box) records the box drawn. After FRAMES frames: a screenshot. Writes
``OUT/captions.json``.
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
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
STATE = Path("local/ref005/session/states/f00006448.mcs")
BLOCK = 0x060CFFDC
TABLE_OFFSET, TABLE_WORDS = 0x4AD7C, 1222


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--build", type=Path, default=Path("build/opt005/a"))
    parser.add_argument("--frames", type=int, default=345)
    args = parser.parse_args()
    out: Path = args.out
    stg = (args.build / "STG0AS.BIN").read_bytes()
    font = (args.build / "KANJI.BIN").read_bytes()
    table = stg[TABLE_OFFSET : TABLE_OFFSET + 2 * TABLE_WORDS]
    o = 0x0609CC22 - 0x06060000
    captions = [struct.unpack_from(">H", stg, o + 2 * i)[0] for i in range(90)]
    rows = []
    session.launch(STATE, out, args.build / CUE)
    agent = session.agent_of(out)
    try:
        for pilot in range(9):
            for stage in range(9):
                box = captions[pilot * 10 + stage]
                agent.run()
                agent.loadstate(STATE.resolve())
                agent.pause()
                agent.write("vdp2vram", 0x40000, font)
                agent.bus_write(0x060AAD7C, table)
                for base in (BLOCK, BLOCK + 0x2F4):
                    agent.bus_write(base + 0x2D2, bytes([pilot]))
                    agent.bus_write(base + 0x2E3, bytes([stage]))
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
                name = f"cap-p{pilot}-s{stage}"
                path = (out / f"{name}.png").resolve()
                agent.screenshot(path)
                rows.append(
                    {
                        "pilot": pilot,
                        "stage": stage,
                        "table_box": box,
                        "boxes_drawn": drawn,
                        "screenshot": name,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
                print(name, box, drawn, flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "captions.json").write_text(json.dumps(rows, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
