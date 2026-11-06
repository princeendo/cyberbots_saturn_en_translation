"""EXP-0059: Latin name banners for the select and VS screens (samples).

Library and CLI. Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0059/banner.py NAME --kind pilot|mech \\
        --style banner|white --out FILE.bin [--width 120]

Writes 4 bpp pixel data (width x 16, two pixels a byte, high nibble left),
the layout of the name parts (D-052). Letters are the arcade's dialogue
letters (``local/layout001/font/arcade_font.json``, `EXP-0025`; 16 rows, an
8-pixel advance), centred. Background, by kind:

- ``pilot``: the red bar (index 6) as the Saturn draws it under a name, a
  parallelogram on rows 3-11 slanting one pixel a row, across the width;
- ``mech``: the same bar (index 6 is blue in the mech palette).

``flip`` stores the letters upside down (the bar unchanged), for parts the
VDP1 draws vertically flipped (the select names).

Two glyphs the arcade letters lack are added as new art, built from the
arcade period: ``·`` (the period raised five rows) and ``&`` (a 7 x 7 mask,
rows doubled, white with the letters' shadow).

Colours (indices of the banner's own palette, ``EXP-0059`` README):

- ``banner``: pilot letters gold/orange on red (arcade white, light, mid,
  dark shades to 15, 1, 2, 3; shadow 5); mech letters in the blue ramp
  (15, 1, 2, 3; shadow 5);
- ``white``: the US arcade's look, white letters (pilot 15 is pale yellow,
  so mech palette 15 is white; pilot letters 15/15/1/2, shadow 5).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

FONT = Path("local/layout001/font/arcade_font.json")
HEIGHT = 16
SHADES = {"ffffff": 0, "dddddd": 1, "aaaaaa": 2, "555555": 3, "111111": "shadow"}
STYLES = {
    ("pilot", "banner"): ((15, 1, 2, 3), 5),
    ("pilot", "white"): ((15, 15, 1, 2), 5),
    ("mech", "banner"): ((15, 1, 2, 3), 5),
    ("mech", "white"): ((15, 15, 15, 1), 5),
}


def load_font() -> dict[str, list[tuple[int, int, object]]]:
    font = json.loads(FONT.read_text())
    out: dict[str, list[tuple[int, int, object]]] = {}
    for code in sorted(font["glyphs"], key=lambda c: int(c, 16)):
        entry = font["glyphs"][code]
        ch = entry["char"]
        if not ch or ch in out:
            continue
        pixels = []
        for y, row in enumerate(entry["rows"]):
            for x, v in enumerate(row):
                shade = SHADES.get(font["palette"][v])
                if shade is not None:
                    pixels.append((x + entry["left"], y, shade))
        out[ch] = pixels
    out["·"] = [(x, y - 5, s) for x, y, s in out["."]]
    amp = [" XX    ", "X  X   ", "X  X   ", " XX  X ", "X  XX  ", "X   X  ", " XXX X "]
    glyph: list[tuple[int, int, object]] = []
    for r, line in enumerate(amp):
        for c, ch in enumerate(line):
            if ch == "X":
                for y in (2 + 2 * r, 3 + 2 * r):
                    glyph.append((c, y, 0))
                    glyph.append((c + 1, y, "shadow"))
    out["&"] = glyph
    return out


def render(
    name: str, kind: str, style: str, width: int = 120, flip: bool = False
) -> list[list[int]]:
    font = load_font()
    ramp, shadow = STYLES[(kind, style)]
    grid = [[0] * width for _ in range(HEIGHT)]
    if kind in ("pilot", "mech"):
        for y in range(3, 12):
            for x in range(max(0, 11 - y), width - (y - 3)):
                grid[y][x] = 6
    x = (width - 8 * len(name)) // 2
    for ch in name:
        if ch != " ":
            if ch not in font:
                raise SystemExit(f"no arcade letter for {ch!r}")
            for gx, gy, shade in font[ch]:
                px, py = x + gx, (HEIGHT - 1 - gy) if flip else gy
                if 0 <= px < width and 0 <= py < HEIGHT:
                    if shade == "shadow":
                        if grid[py][px] in (0, 6):
                            grid[py][px] = shadow
                    else:
                        assert isinstance(shade, int)
                        grid[py][px] = ramp[shade]
        x += 8
    return grid


def pack(grid: list[list[int]]) -> bytes:
    out = bytearray()
    for row in grid:
        for x in range(0, len(row), 2):
            out.append((row[x] << 4) | row[x + 1])
    return bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--kind", choices=("pilot", "mech"), required=True)
    parser.add_argument("--style", choices=("banner", "white"), required=True)
    parser.add_argument("--width", type=int, default=120)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.write_bytes(pack(render(args.name, args.kind, args.style, args.width)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
