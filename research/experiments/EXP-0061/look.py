"""EXP-0061: classify the name art on the screen of a running game.

Run from the repository root while ``EXP-0019/drive.py`` has the game
running (or any agent directory):

    ./invenv.sh python research/experiments/EXP-0061/look.py AGENT_DIR OUT NAME \\
        [--build build/loc005/a]

Pauses the game, saves ``OUT/NAME.png``, reads VDP1 VRAM and lists every
4 bpp sprite whose pixels (not blank) are, in this order:

- ``built-vs``: a decoded name record of the built `PL3F_0.BIN`;
- ``katakana-vs``: a decoded name record of the untouched file only;
- ``built-select``: inside the built `SELECT.VAD` name block;
- ``katakana-select``: inside the untouched block.

A VS sprite whose pattern sits at VDP1 VRAM ``0x10000``-``0x1FFFF`` is read
from its WRAM-H mirror (``0x060E0000`` + its address, D-053). Then lets the
game run again. Writes ``OUT/NAME.json``; prints a summary line.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent
from tools.memory import vdp1_sprites
from tools.text import dialogue, name_art, pattern_t2

BLOCK = (0x17840, 0x19B20)


def vs_patterns(pl: bytes, table: bytes) -> set[bytes]:
    out = set()
    for frame in [*name_art.VS_PILOTS, *name_art.VS_MECHS]:
        for p in name_art.frame_parts(
            table, name_art.VS_FRAME_TABLE, name_art.VS_FRAMES, frame
        ):
            w1, w2 = struct.unpack_from(">2H", pl, 6 * p + 2)
            offset = (((w1 & 1) << 16) | w2) * 4
            if pl[offset] >> 4 == 2:
                data = pattern_t2.decode(pl[offset:])
                if len(set(data)) > 1:
                    out.add(data)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("agent_dir", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("name")
    parser.add_argument("--build", type=Path, default=Path("build/loc005/a"))
    args = parser.parse_args()
    table = bytes(dialogue.checked("STG0AS.BIN"))
    lo, hi = BLOCK
    sel_built = (args.build / "SELECT.VAD").read_bytes()[lo:hi]
    sel_orig = bytes(dialogue.checked("SELECT.VAD"))[lo:hi]
    vs_built = vs_patterns((args.build / "PL3F_0.BIN").read_bytes(), table)
    vs_orig = vs_patterns(bytes(dialogue.checked("PL3F_0.BIN")), table) - vs_built

    agent = Agent(args.agent_dir.resolve(), timeout=20.0)
    agent.pause()
    try:
        frame = int(agent.status()["frame"])
        png = (args.out / f"{args.name}.png").resolve()
        agent.screenshot(png)
        vram = agent.read("vdp1vram", 0, 0x80000)
        found: list[dict[str, Any]] = []
        for sp in vdp1_sprites.sprites(vram):
            if sp.color_mode > 1:
                continue
            size = sp.width * sp.height // 2
            data = vdp1_sprites.pixel_bytes(vram, sp)
            mirror = (
                agent.bus_read(0x060E0000 + sp.source, size)
                if 0x10000 <= sp.source < 0x20000
                else data
            )
            if len(set(data)) <= 1 and len(set(mirror)) <= 1:
                continue
            kind = None
            # VS first: the VS pilot names have the select art's pixels.
            if data in vs_built or mirror in vs_built:
                kind = "built-vs"
            elif data in vs_orig or mirror in vs_orig:
                kind = "katakana-vs"
            elif data in sel_built:
                kind = "built-select"
            elif data in sel_orig:
                kind = "katakana-select"
            if kind:
                found.append(
                    {"kind": kind, "x": sp.x, "y": sp.y, "w": sp.width, "h": sp.height}
                )
    finally:
        agent.run()
    counts = {
        k: sum(f["kind"] == k for f in found)
        for k in ("built-select", "katakana-select", "built-vs", "katakana-vs")
    }
    report = {
        "name": args.name,
        "frame": frame,
        "screenshot_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
        "counts": counts,
        "parts": found,
    }
    (args.out / f"{args.name}.json").write_text(json.dumps(report, indent=1) + "\n")
    print(args.name, frame, counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
