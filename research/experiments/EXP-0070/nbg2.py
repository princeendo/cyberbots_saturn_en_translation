"""EXP-0070: render one VDP2 tile layer of a saved state, offline, with a grid.

    ./invenv.sh python research/experiments/EXP-0070/nbg2.py STATE OUT.png OUT.json \\
        [--layer 2] [--scale 3]

From the state's VDP2 registers (``RawRegs``), VRAM and CRAM (extracted with
``tools.memory.mcs_extract``): the layer's map (2-word pattern names; the
registers in this state: NBG1 1x1 cells at ``0x70000``, NBG2 2x2 cells at
``0x7A000``, NBG3 2x2 cells at ``0x78000``, planes 2x1, every plane the same),
scroll (integer part only), 16-colour cells, CRAM mode 1 (15-bit colours).
Transparent pixels (index 0) are magenta. A grid line marks every block.
``OUT.json`` maps each screen block (column, row) to its pattern name words
and the character data address (character number x 0x20). Covers the
352 x 240 screen, or with ``--plane`` the whole 1024 x 512 plane. Checked
against the state's preview by the agent.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.memory.mcs_extract import encode_png, parse_state

LAYERS = {  # base, cell pixels, scroll X/Y register offsets
    1: (0x70000, 8, 0x80, 0x84),
    2: (0x7A000, 16, 0x90, 0x92),
    3: (0x78000, 16, 0x94, 0x96),
}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("state", type=Path)
    p.add_argument("png", type=Path)
    p.add_argument("json", type=Path)
    p.add_argument("--layer", type=int, default=2)
    p.add_argument("--scale", type=int, default=3)
    p.add_argument(
        "--plane", action="store_true", help="the whole 1024 x 512 plane, no scroll"
    )
    a = p.parse_args()
    vdp2 = parse_state(a.state.read_bytes()).sections["VDP2"]
    regs, vram, cram = vdp2["RawRegs"], vdp2["VRAM"], vdp2["CRAM"]

    def reg(o: int) -> int:
        return int(struct.unpack_from("<H", regs, o)[0])

    def vword(addr: int) -> int:
        # the state stores VRAM as 16-bit words in host (little-endian) order
        return int(struct.unpack_from("<H", vram, addr)[0])

    def colour(index: int) -> tuple[int, int, int]:
        c = int(struct.unpack_from("<H", cram, 2 * index)[0])
        return ((c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8)

    base, cell, rx, ry = LAYERS[a.layer]
    scx, scy = reg(rx) & 0x7FF, reg(ry) & 0x7FF
    per = 512 // cell
    page_bytes = per * per * 4
    width, height, s = 352, 240, a.scale
    if a.plane:
        width, height, scx, scy = 1024, 512, 0, 0
    img = bytearray(width * s * height * s * 3)
    blocks: dict[str, object] = {}
    for sy in range(height):
        for sx in range(width):
            x, y = (scx + sx) % 1024, (scy + sy) % 512
            page, cx, cy = x // 512, (x % 512) // cell, y // cell
            entry = base + page * page_bytes + (cy * per + cx) * 4
            w0, w1 = vword(entry), vword(entry + 2)
            char = w1 & 0x7FFF
            px, py = (x % cell), (y % cell)
            if w0 & 0x4000:
                px = cell - 1 - px
            if w0 & 0x8000:
                py = cell - 1 - py
            sub = (py // 8) * 2 + (px // 8) if cell == 16 else 0
            addr = (char + sub) * 0x20 + (py % 8) * 4 + (px % 8) // 2
            byte = vword(addr & ~1) >> (0 if addr & 1 else 8) & 0xFF
            index = byte >> 4 if px % 2 == 0 else byte & 15
            rgb = (255, 0, 255) if index == 0 else colour((w0 & 0x7F) * 16 + index)
            grid = (
                sx % cell == (cell - (scx % cell)) % cell
                or sy % cell == (cell - (scy % cell)) % cell
            )
            for dy in range(s):
                for dx in range(s):
                    o = (((sy * s + dy) * width * s) + sx * s + dx) * 3
                    edge = grid and (
                        dx == 0 if sx % cell == (cell - scx % cell) % cell else dy == 0
                    )
                    img[o : o + 3] = bytes((0, 255, 0) if edge else rgb)
            key = f"{(sx + scx % cell) // cell},{(sy + scy % cell) // cell}"
            blocks.setdefault(
                key, {"w0": f"0x{w0:04X}", "char_addr": f"0x{char * 0x20:05X}"}
            )
    a.png.write_bytes(encode_png(width * s, height * s, bytes(img)))
    a.json.write_text(
        json.dumps({"layer": a.layer, "scroll": [scx, scy], "blocks": blocks}, indent=1)
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
