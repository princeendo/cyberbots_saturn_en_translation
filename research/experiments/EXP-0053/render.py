"""EXP-0053: render draft English boot warnings as they would show (samples).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0053/render.py OUT_DIR \\
        [--drafts research/experiments/EXP-0053/drafts.json] [--font arcade|fix] \\
        [--out-json FIT.json]

Draws each screen's lines in the room D-049 measured: 352 x 224 pixels,
the 16 colours of `CYBER.BIN`'s table (0x06053AAC), on value 15 (black).
Writes, under the ignored ``OUT_DIR``, one 352 x 224 PNG per picture and a
sheet of all five, and prints (and writes to ``--out-json``) the fit:
widest line, last row used, and any line or row outside the room.

Fonts (both game-derived, read from ignored paths, never committed):

- ``arcade``: the arcade's dialogue letters (``local/layout001/font/
  arcade_font.json``, `EXP-0025`), as the story English uses them, 16 rows
  tall at an 8-pixel advance, not narrowed;
- ``fix``: `FIX.BIN`'s 8 x 8 ASCII cells (the credits' small font, D-035),
  value 5 the letter and 15 its shadow, at an 8-pixel advance.

Colours: body white, title yellow, ``{...}`` cyan, ``[...]`` red, each as a
ramp of the table (white 7/6/5/4, yellow 12/12/11/10, cyan 14/14/13/13,
red 9/9/8/8 for the arcade's four letter shades); shadows value 1.
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

CYBER = Path("local/extracted/saturn_jp/CYBER.BIN")
CYBER_BASE, PALETTE = 0x0600D000, 0x06053AAC
ARCADE = Path("local/layout001/font/arcade_font.json")
FIX = Path("local/extracted/saturn_jp/FIX.BIN")
W, H, BG, SHADOW = 352, 224, 15, 1
CASES = {
    "WARNING0.PIX": "damaged",
    "WARNING1.PIX": "zero",
    "WARNING2.PIX": "cart-zero",
    "WARNING3.PIX": "both-zero",
    "WARNING4.PIX": "free4",
}
RAMPS = {
    "white": (7, 6, 5, 4),
    "yellow": (12, 12, 11, 10),
    "cyan": (14, 14, 13, 13),
    "red": (9, 9, 8, 8),
}
# arcade palette colour -> shade index (0 brightest) or "shadow"
ARCADE_SHADES = {"ffffff": 0, "dddddd": 1, "aaaaaa": 2, "555555": 3, "111111": "shadow"}

Glyph = list[tuple[int, int, Any]]  # (x, y, shade index or "shadow")


def palette() -> list[tuple[int, int, int]]:
    cyber = CYBER.read_bytes()
    off = PALETTE - CYBER_BASE
    out = []
    for i in range(16):
        c = int.from_bytes(cyber[off + 2 * i : off + 2 * i + 2], "big")
        out.append(((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3))
    return out


def arcade_font() -> tuple[dict[str, Glyph], int]:
    font = json.loads(ARCADE.read_text())
    colours = font["palette"]
    out: dict[str, Glyph] = {}
    for code in sorted(font["glyphs"], key=lambda c: int(c, 16)):
        entry = font["glyphs"][code]
        ch = entry["char"]
        if not ch or (ch in out and not (ch == "." and code == "14")):
            continue
        pixels: Glyph = []
        for y, row in enumerate(entry["rows"]):
            for x, v in enumerate(row):
                shade = ARCADE_SHADES.get(colours[v])
                if shade is not None:
                    pixels.append((x + entry["left"], y, shade))
        out[ch] = pixels
    return out, 16


def fix_font() -> tuple[dict[str, Glyph], int]:
    data = FIX.read_bytes()
    out: dict[str, Glyph] = {}
    for code in range(0x20, 0x7F):
        cell = data[code * 32 : code * 32 + 32]
        pixels: Glyph = []
        for y in range(8):
            for x in range(8):
                byte = cell[y * 4 + x // 2]
                v = byte >> 4 if x % 2 == 0 else byte & 15
                if v == 15:
                    pixels.append((x, y, "shadow"))
                elif v:
                    pixels.append((x, y, 0 if v == 5 else 1))
        out[chr(code)] = pixels
    return out, 8


def spans(line: str) -> list[tuple[str, str]]:
    """Split a line into (text, colour) by {cyan} and [red] marks."""
    out, colour, buf = [], "white", ""
    for ch in line:
        if ch in "{[":
            out.append((buf, colour))
            buf, colour = "", "cyan" if ch == "{" else "red"
        elif ch in "}]":
            out.append((buf, colour))
            buf, colour = "", "white"
        else:
            buf += ch
    out.append((buf, colour))
    return [s for s in out if s[0]]


def plain(line: str) -> str:
    return "".join(t for t, _ in spans(line))


def draw(
    canvas: list[list[int]],
    font: dict[str, Glyph],
    text: str,
    x: int,
    y: int,
    colour: str,
    missing: set[str],
) -> int:
    ramp = RAMPS[colour]
    for ch in text:
        if ch != " ":
            if ch not in font:
                missing.add(ch)
            for gx, gy, shade in font.get(ch, []):
                px, py = x + gx, y + gy
                if 0 <= px < W and 0 <= py < H:
                    if shade == "shadow":
                        if canvas[py][px] == BG:
                            canvas[py][px] = SHADOW
                    else:
                        canvas[py][px] = ramp[shade]
        x += 8
    return x


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument(
        "--drafts", type=Path, default=Path(__file__).with_name("drafts.json")
    )
    parser.add_argument("--font", choices=("arcade", "fix"), default="arcade")
    parser.add_argument("--out-json", type=Path)
    parser.add_argument(
        "--beside", action="store_true", help="Japanese | English sheet"
    )
    args = parser.parse_args()
    drafts = json.loads(args.drafts.read_text())
    font, height = arcade_font() if args.font == "arcade" else fix_font()
    line_pitch = height + 2 if args.font == "arcade" else 12
    pal = palette()
    args.out.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "font": args.font,
        "line_pitch": line_pitch,
        "screens": {},
    }
    pictures: list[list[list[int]]] = []
    for name, screen in drafts["screens"].items():
        canvas = [[BG] * W for _ in range(H)]
        missing: set[str] = set()
        title = drafts["title"]
        y = 16
        draw(canvas, font, title, (W - 8 * len(title)) // 2, y, "yellow", missing)
        y += line_pitch + line_pitch // 2
        body = sum(line_pitch if line else line_pitch // 2 for line in screen["lines"])
        y = max(y, y + (H - 8 - y - body) // 2)
        widest = 0
        for line in screen["lines"]:
            if not line:
                y += line_pitch // 2
                continue
            width = 8 * len(plain(line))
            widest = max(widest, width)
            x = (W - width) // 2
            for text, colour in spans(line):
                x = draw(canvas, font, text, x, y, colour, missing)
            y += line_pitch
        used = [r for r in range(H) if any(v != BG for v in canvas[r])]
        report["screens"][name] = {
            "lines": len([line for line in screen["lines"] if line]),
            "widest_line_px": widest,
            "last_row_used": max(used),
            "text_bottom_px": y,
            "fits": widest <= W - 16 and y <= H - 8,
            "missing_characters": sorted(missing),
        }
        rgb = bytes(v for row in canvas for value in row for v in pal[value])
        (args.out / f"{name}.png").write_bytes(encode_png(W, H, rgb))
        pictures.append(canvas)
    # sheet: 2 columns x 3 rows with 8-pixel grey gutters
    gutter = 8
    sw, sh = 2 * W + 3 * gutter, 3 * H + 4 * gutter
    sheet = bytearray(bytes((96, 96, 96)) * sw * sh)
    for i, canvas in enumerate(pictures):
        ox = gutter + (i % 2) * (W + gutter)
        oy = gutter + (i // 2) * (H + gutter)
        for y in range(H):
            for x in range(W):
                o = ((oy + y) * sw + ox + x) * 3
                sheet[o : o + 3] = bytes(pal[canvas[y][x]])
    (args.out / "sheet.png").write_bytes(encode_png(sw, sh, bytes(sheet)))
    if args.beside:
        # Japanese screen (rows 8-231 of EXP-0051's screenshot) beside each English
        bw, bh = 2 * W + 3 * gutter, 5 * H + 6 * gutter
        side = bytearray(bytes((96, 96, 96)) * bw * bh)
        for i, (name, canvas) in enumerate(
            zip(drafts["screens"], pictures, strict=True)
        ):
            case = CASES[name]
            w, _h, bpp, raw = read_png(Path("local/boot001") / case / "w01457.png")
            oy = gutter + i * (H + gutter)
            for y in range(H):
                for x in range(W):
                    o = ((oy + y) * bw + gutter + x) * 3
                    k = ((y + 8) * w + x) * bpp
                    side[o : o + 3] = raw[k : k + 3]
                    o = ((oy + y) * bw + 2 * gutter + W + x) * 3
                    side[o : o + 3] = bytes(pal[canvas[y][x]])
        (args.out / "beside.png").write_bytes(encode_png(bw, bh, bytes(side)))
    print(json.dumps(report, indent=1))
    if args.out_json:
        args.out_json.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
