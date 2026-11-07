"""EXP-0068: render the game's font and art stores for the inventory (UI-001 part 2).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0068/render.py OUT

Writes grey-scale PNGs (local only; game art is never committed):

- **4 bpp tile stores** (8x8 tiles, 32 bytes each, as `FIX.BIN`'s menu font,
  `EXP-0068`): `FIX.BIN` and `ST00_FNT.BIN`-`ST0A_FNT.BIN`, 64 tiles a row,
  each tile's index = its byte offset / 32;
- **`KANJI.BIN`** with ``tools.font.kanji`` (D-019), the untouched file and
  the current image's (``--build``);
- **512-wide 8 bpp bitmaps** (as `WARNINGn.PIX` and `QSD.PIX`, D-049,
  D-035): `CAPCOM.PIX`, `OPS00.PIX`, `OPS10.PIX`, `RANKBG.PIX`.

``OUT/render.json`` lists each output with its source's SHA-256 and size.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.memory.mcs_extract import encode_png

SRC = Path("local/extracted/saturn_jp")


def grey(values: bytes, scale: int) -> bytes:
    return b"".join(bytes([min(255, v * scale)] * 3) for v in values)


def tiles4(data: bytes, columns: int = 64) -> tuple[int, int, bytes]:
    count = len(data) // 32
    rows = (count + columns - 1) // columns
    width, height = columns * 8, rows * 8
    pix = bytearray(width * height)
    for t in range(count):
        tile = data[32 * t : 32 * t + 32]
        tx, ty = (t % columns) * 8, (t // columns) * 8
        for y in range(8):
            for x in range(8):
                b = tile[y * 4 + x // 2]
                v = b >> 4 if x % 2 == 0 else b & 15
                pix[(ty + y) * width + tx + x] = v
    return width, height, bytes(pix)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--build", type=Path, default=Path("build/opt005/a"))
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    names = ["FIX.BIN"] + [f"ST0{c}_FNT.BIN" for c in "0123456789A"]
    for name in names:
        data = (SRC / name).read_bytes()
        w, h, pix = tiles4(data)
        (out / f"{name}.png").write_bytes(encode_png(w, h, grey(pix, 17)))
        report[name] = {
            "kind": "4bpp tiles",
            "tiles": len(data) // 32,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    for label, path in (
        ("KANJI.BIN", SRC / "KANJI.BIN"),
        ("KANJI.BIN-current", args.build / "KANJI.BIN"),
    ):
        data = path.read_bytes()
        cells = kanji.decode(data)
        w, h, pix = kanji.sheet(cells)
        (out / f"{label}.png").write_bytes(encode_png(w, h, pix))
        report[label] = {
            "kind": "kanji glyphs (D-019)",
            "glyphs": len(cells),
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    for name in ("CAPCOM.PIX", "OPS00.PIX", "OPS10.PIX", "RANKBG.PIX"):
        data = (SRC / name).read_bytes()
        h = len(data) // 512
        (out / f"{name}.png").write_bytes(encode_png(512, h, grey(data[: 512 * h], 1)))
        report[name] = {
            "kind": "512-wide 8bpp bitmap (tried)",
            "rows": h,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    (out / "render.json").write_text(json.dumps(report, indent=1) + "\n")
    print(
        json.dumps(
            {
                k: (v["size"], v.get("tiles") or v.get("glyphs") or v.get("rows"))
                for k, v in report.items()
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
