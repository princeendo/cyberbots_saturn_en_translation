"""EXP-0057: every pattern the select screen's bank 56 can draw, rendered.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0057/bank56.py OUT_DIR \\
        [--out research/experiments/EXP-0057/bank56.json]

Static, from the select-screen state's WRAM-H (``EXP-0056``,
``local/loc001/ram3070/wram_h.bin``) and `SELECT.VAD`. Bank 56 is one of the
sprite-part routine's special banks (``0x060113AC``: 8-byte parts, pattern
data in VDP1 VRAM from ``0x20000``, where `SELECT.VAD` is loaded raw):

- bank header ``[0x06047D50 + 4 * 56]``; +4 the frame table (one word per
  frame: the frame's first part index), +8 the parts;
- part (8 bytes) word 1 bit 0 and word 2: pattern offset / 4 (in
  `SELECT.VAD`); word 3: size, width ``(w & 0x0F00) >> 5`` pixels, height
  ``w & 0x7F``.

It lists every frame's parts (up to the next frame's first part) and
renders each distinct pattern as a grey 4 bpp picture (``OUT_DIR/pNNNNN
.png``, ignored path) and one contact sheet (``OUT_DIR/sheet.png``).
Numbers only in the JSON.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.memory.mcs_extract import encode_png

RAM = Path("local/loc001/ram3070/wram_h.bin")
VAD = Path("local/extracted/saturn_jp/SELECT.VAD")
BANK = 56


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    ram, vad = RAM.read_bytes(), VAD.read_bytes()

    def long(a: int) -> int:
        return int(struct.unpack_from(">I", ram, a - 0x06000000)[0])

    def word(a: int) -> int:
        return int(struct.unpack_from(">H", ram, a - 0x06000000)[0])

    header = long(0x06047D50 + 4 * BANK)
    table, parts = long(header + 4), long(header + 8)
    count = (parts - table) // 2
    starts = [word(table + 2 * f) for f in range(count)]
    frames: list[dict[str, Any]] = []
    patterns: dict[tuple[int, int, int], int] = {}
    for f in range(count):
        first = starts[f]
        last = starts[f + 1] if f + 1 < count else first + 1
        items = []
        for p in range(first, max(first + 1, last)):
            a = parts + 8 * p
            w1, w2, w3 = word(a + 2), word(a + 4), word(a + 6)
            offset = (((w1 & 1) << 16) | w2) * 4
            width, height = (w3 & 0x0F00) >> 5, w3 & 0x7F
            if not width or not height or offset + width * height // 2 > len(vad):
                continue
            key = (offset, width, height)
            patterns.setdefault(key, len(patterns))
            items.append({"offset": f"0x{offset:05X}", "size": [width, height]})
        frames.append({"frame": f"0x{f + 1:02X}", "parts": items})
    args.out_dir.mkdir(parents=True, exist_ok=True)
    tiles = []
    for (offset, width, height), n in patterns.items():
        data = vad[offset : offset + width * height // 2]
        rgb = bytearray()
        for y in range(height):
            for x in range(width):
                b = data[(y * width + x) // 2]
                v = (b >> 4 if x % 2 == 0 else b & 15) * 17
                rgb += bytes((v, v, v))
        tiles.append((width, height, rgb))
        (args.out_dir / f"p{n:05d}.png").write_bytes(
            encode_png(width, height, bytes(rgb))
        )
    cell_w, cell_h, cols = 128, 72, 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = bytearray(bytes((40, 0, 40)) * (cols * cell_w) * (rows * cell_h))
    for n, (width, height, rgb) in enumerate(tiles):
        ox, oy = (n % cols) * cell_w, (n // cols) * cell_h
        for y in range(min(height, cell_h)):
            for x in range(min(width, cell_w)):
                o = ((oy + y) * cols * cell_w + ox + x) * 3
                i = (y * width + x) * 3
                sheet[o : o + 3] = rgb[i : i + 3]
    (args.out_dir / "sheet.png").write_bytes(
        encode_png(cols * cell_w, rows * cell_h, bytes(sheet))
    )
    report = {
        "bank": BANK,
        "header": f"0x{header:08X}",
        "frame_table": f"0x{table:08X}",
        "parts": f"0x{parts:08X}",
        "frames": len(frames),
        "patterns": len(patterns),
        "by_frame": frames,
    }
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    print(len(frames), "frames", len(patterns), "patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
