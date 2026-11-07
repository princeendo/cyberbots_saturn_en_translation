"""EXP-0068: enlarged crops of a 4 bpp tile store with a tile grid.

    ./invenv.sh python research/experiments/EXP-0068/grid.py \\
        NAME FIRST ROWS OUT.png [--half 0|1]

Crops tile rows FIRST..FIRST+ROWS-1 (64 tiles a row) of
``local/extracted/saturn_jp/NAME``, half 0 = tiles 0-31 of each row, half 1 =
tiles 32-63, scaled 4x. Red lines mark every tile boundary; a brighter red line
marks every 8th column and every 4th row, so a tile's index is
``64 * row + column``. Local only: game art is never committed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
from render import SRC, tiles4

from tools.memory.mcs_extract import encode_png


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("first", type=int)
    p.add_argument("rows", type=int)
    p.add_argument("out", type=Path)
    p.add_argument("--half", type=int, default=0)
    a = p.parse_args()
    w, _h, pix = tiles4((SRC / a.name).read_bytes())
    s = 4
    cw, ch = 32 * 8 * s, a.rows * 8 * s
    out = bytearray(cw * ch * 3)
    for y in range(ch):
        sy = a.first * 8 + y // s
        for x in range(cw):
            sx = a.half * 256 + x // s
            v = pix[sy * w + sx] * 17 if sy * w + sx < len(pix) else 0
            r = g = b = v
            tx, ty = x % (8 * s), y % (8 * s)
            if tx == 0 or ty == 0:
                column = (x // (8 * s)) % 8 == 0 and tx == 0
                row = (y // (8 * s)) % 4 == 0 and ty == 0
                major = column or row
                r, g, b = (255, 0, 0) if major else (110, 0, 0)
            i = (y * cw + x) * 3
            out[i : i + 3] = bytes((r, g, b))
    a.out.write_bytes(encode_png(cw, ch, bytes(out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
