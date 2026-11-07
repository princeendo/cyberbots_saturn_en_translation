"""EXP-0072: every built English VS caption, drawn by the game (UI-006).

Run from the repository root (no key, no cold boot):

    ./invenv.sh python research/experiments/EXP-0072/check_captions.py OUT \\
        [--build build/ui006/a] [--frames 345]

The patched build (D-007), silent home, untouched image. For each caption box
of the build (``OUT``'s ``caption_changes.json``): session state 6448 (before
a VS screen) is loaded and halted in one agent exchange (`EXP-0070`); the
build's `KANJI.BIN` is written to VDP2 VRAM ``0x40000``, its code table
(``0x060AAD7C``, with the story's new codes) and every
`STG0AS.BIN` range of ``caption_changes.json`` (rows and row pointers) to
its RAM copy (``0x06060000`` + offset), since the state holds the untouched
ones; the pilot and stage bytes of both player blocks are set from the
caption table (``0x0609CC22``). A log-mode PC breakpoint at ``0x0606E6E0``
records the box drawn. After FRAMES frames: a screenshot and the 60 glyph
cells (WRAM-H ``0x060FE200``, D-035). The box passes when its predicted
cells (``caption_changes.json`` ``prediction``) are the leading cells.
Writes ``OUT/check.json``.
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
from typing import Any

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
STATE = Path("local/ref005/session/states/f00006448.mcs")
BLOCK = 0x060CFFDC
BASE, CAPTIONS, CELLS = 0x06060000, 0x0609CC22, 0x060FE200
TABLE = 0x060AAD7C  # the code table, 39 rows of 32 words (D-019)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--build", type=Path, default=Path("build/ui006/a"))
    p.add_argument("--frames", type=int, default=345)
    a = p.parse_args()
    out: Path = a.out
    stg = (a.build / "STG0AS.BIN").read_bytes()
    font = (a.build / "KANJI.BIN").read_bytes()
    changes = json.loads((a.build / "caption_changes.json").read_text())
    prediction = {int(x["box"]): x["cells"] for x in changes["prediction"]}
    ranges = [r for r in changes["ranges"] if r["file"] == "STG0AS.BIN"]
    where: dict[int, tuple[int, int]] = {}
    for k in range(90):
        box = int(struct.unpack_from(">H", stg, CAPTIONS - BASE + 2 * k)[0])
        if box in prediction:
            where[box] = (k // 10, k % 10)
    rows: list[dict[str, Any]] = []
    session.launch(STATE, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    try:
        for box in sorted(prediction):
            pilot, stage = where[box]
            agent.run()
            agent.command(f"loadstate {STATE.resolve()}", "pause")
            agent.wait_halted(30.0)
            agent.write("vdp2vram", 0x40000, font)
            agent.bus_write(TABLE, stg[TABLE - BASE : TABLE - BASE + 2 * 1248])
            for r in ranges:
                agent.bus_write(BASE + r["start"], stg[r["start"] : r["end"]])
            for base in (BLOCK, BLOCK + 0x2F4):
                agent.bus_write(base + 0x2D2, bytes([pilot]))
                agent.bus_write(base + 0x2E3, bytes([stage]))
            agent.bpmode("log")
            agent.breakpoints("pc", ["0606E6E0"])
            agent.clear_events()
            agent.frames(a.frames)
            agent.wait_halted(120.0)
            drawn = sorted(
                {
                    int(dict(FIELD.findall(e)).get("R4", "0"), 16)
                    for e in agent.events()
                    if "PC=0606E6E0" in e
                }
            )
            agent.breakpoints("pc", [])
            cells = agent.bus_read(CELLS, 60 * 0x80)
            got = [
                hashlib.sha256(cells[0x80 * i : 0x80 * (i + 1)]).hexdigest()
                for i in range(len(prediction[box]))
            ]
            shot = (out / f"cap-{box}.png").resolve()
            agent.screenshot(shot)
            ok = got == prediction[box] and drawn == [box]
            rows.append(
                {
                    "box": box,
                    "pilot": pilot,
                    "stage": stage,
                    "boxes_drawn": drawn,
                    "cells_predicted": len(prediction[box]),
                    "cells_matched": sum(
                        x == y for x, y in zip(got, prediction[box], strict=True)
                    ),
                    "ok": ok,
                    "shot_sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                }
            )
            print(box, ok, flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    report = {
        "build_stg0as_sha256": hashlib.sha256(stg).hexdigest(),
        "build_kanji_sha256": hashlib.sha256(font).hexdigest(),
        "state": str(STATE),
        "frames": a.frames,
        "passed": sum(r["ok"] for r in rows),
        "boxes": rows,
    }
    (out / "check.json").write_text(json.dumps(report, indent=1) + "\n")
    print(report["passed"], "of", len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
