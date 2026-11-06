"""EXP-0052: draw each WARNINGn.PIX back out and compare it with its screen.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0052/decode.py \\
        [--out research/experiments/EXP-0052/decode.json] [--png-dir DIR]

Static apart from the screenshots of `EXP-0051` (``local/boot001/<case>/
w01457.png``). The format tested (HYPOTHESIS until it matches):

- 512 bytes a row, one byte a pixel, values 0-15;
- colour = entry ``value`` of the 16-colour table at ``0x06053AAC`` in
  `CYBER.BIN` (the loader's ``0x0600F334`` call), RGB555, expanded to 8
  bits as ``(c << 3) | (c >> 2)``;
- screen pixel (x, y) = file pixel (x + DX, y + DY), searched over small
  offsets.

For each picture: the best offset, the pixels that differ there, the rows
and columns the picture's non-background pixels use, and the colours used.
Numbers only; ``--png-dir`` writes the decoded pictures (ignored path).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.memory.mcs_extract import encode_png

_spec = importlib.util.spec_from_file_location(
    "exp0038_compare", Path("research/experiments/EXP-0038/compare_runs.py")
)
assert _spec and _spec.loader
_cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cmp)
read_png = _cmp.read_png

EXTRACTED = Path("local/extracted/saturn_jp")
CYBER_BASE, PALETTE = 0x0600D000, 0x06053AAC
WIDTH = 512
BLACK = (0, 0, 0)
CASES = {0: "damaged", 1: "zero", 2: "cart-zero", 3: "both-zero", 4: "free4"}


def palette() -> list[tuple[int, int, int]]:
    cyber = (EXTRACTED / "CYBER.BIN").read_bytes()
    off = PALETTE - CYBER_BASE
    out = []
    for i in range(16):
        c = int.from_bytes(cyber[off + 2 * i : off + 2 * i + 2], "big")
        r, g, b = c & 31, (c >> 5) & 31, (c >> 10) & 31
        out.append(tuple(v << 3 for v in (r, g, b)))
    return out  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    pal = palette()
    report: list[dict[str, Any]] = []
    for n, case in CASES.items():
        data = (EXTRACTED / f"WARNING{n}.PIX").read_bytes()
        rows = len(data) // WIDTH
        w, h, bpp, shot = read_png(Path("local/boot001") / case / "w01457.png")
        screen = [
            tuple(shot[(y * w + x) * bpp : (y * w + x) * bpp + 3])
            for y in range(h)
            for x in range(w)
        ]
        best: tuple[int, int, int] | None = None
        for dy in range(-8, 9):
            for dx in range(-8, 9):
                diff = 0
                for y in range(h):
                    fy = y + dy
                    for x in range(w):
                        fx = x + dx
                        if 0 <= fy < rows and 0 <= fx < WIDTH and data[fy * WIDTH + fx]:
                            want = pal[data[fy * WIDTH + fx]]
                        else:
                            want = BLACK
                        diff += want != screen[y * w + x]
                    if best and diff >= best[0]:
                        break
                if best is None or diff < best[0]:
                    best = (diff, dx, dy)
        assert best
        diff, dx, dy = best
        background = max(set(data), key=data.count)
        used = [
            (x, y)
            for y in range(rows)
            for x in range(WIDTH)
            if data[y * WIDTH + x] not in (background, 0)
        ]
        entry = {
            "picture": f"WARNING{n}.PIX",
            "bytes": len(data),
            "rows": rows,
            "screen": [w, h],
            "offset_dx_dy": [dx, dy],
            "pixels_differing": diff,
            "values_used": sorted(set(data)),
            "background_value": background,
            "value_0_on_screen": sum(
                1
                for y in range(max(0, -dy), min(h, rows - dy))
                for x in range(w)
                if data[(y + dy) * WIDTH + x + dx] == 0
            ),
            "file_rows_on_screen": [max(0, dy), min(rows, h + dy) - 1],
            "text_box_x": [min(p[0] for p in used), max(p[0] for p in used)],
            "text_box_y": [min(p[1] for p in used), max(p[1] for p in used)],
        }
        report.append(entry)
        print(entry)
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            rgb = bytes(
                v
                for y in range(h)
                for x in range(w)
                for v in (
                    pal[data[(y + dy) * WIDTH + x + dx]]
                    if 0 <= y + dy < rows and data[(y + dy) * WIDTH + x + dx]
                    else BLACK
                )
            )
            (args.png_dir / f"WARNING{n}.png").write_bytes(encode_png(w, h, rgb))
    palette_out = [f"0x{b >> 3 << 10 | g >> 3 << 5 | r >> 3:04X}" for r, g, b in pal]
    if args.out:
        args.out.write_text(
            json.dumps({"palette_rgb555": palette_out, "pictures": report}, indent=1)
            + "\n"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
