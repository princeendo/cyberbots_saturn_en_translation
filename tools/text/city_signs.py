"""The ruined-city signs: blank and English art in `ST00_FNT.BIN` (UI-006).

The signs are NBG2 blocks of `ST00_FNT.BIN` (D-061; the store front's block
map: ``research/experiments/EXP-0072/store_blocks.json``, 16 x 16 pixels, 128 bytes a
block, 4 bpp cells in VDP2 order). The user's choice (``docs/
localization_policy.md``, "UI Text and Art, Decided";
``data/translations/signs_switch.json``): ``BLANK`` (the default, on the
disc), ``ENGLISH`` and ``JAPANESE`` (the original art).

- **Blank.** The red banner's and the white banner's writing colours become
  their base colour inside each banner; the slanted sale sign is filled
  with its interior colour 6 between its top and bottom border lines,
  fitted to the interior's first and last rows where no writing touches
  them.
- **English.** The blank art plus the approved words: stacked arcade
  capitals (``tools.font.pairs`` letters, ink only) on the banners, in the
  signs' writing colours; `FIX.BIN`'s small capitals (ink colour 5) along
  the sale sign's slope, fitted to the original writing.

``SLICE`` is the file range that holds every sign block (VRAM ``0x28D00``-
``0x3867F``); the switch's tail files are that slice of the English and of
the original art, loaded over the stage tiles (``tools.text.names_switch``).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.font import pairs

SIGN_MAP = Path("research/experiments/EXP-0072/store_blocks.json")
VRAM_BASE = 0x19000  # ST00_FNT.BIN's load address in VDP2 VRAM (D-061)
SLICE = (0x0FD00, 0x1F680)  # file offsets: VRAM 0x28D00-0x3867F

# Plane-pixel boxes (inclusive), writing colours, base colour, ink, words.
BANNERS: list[dict[str, Any]] = [
    {
        "sign": "red banner",
        "box": (449, 461, 250, 329),
        "text": {6, 7, 8, 9, 0xB},
        "base": 0xA,
        "ink": 7,
        "word": "red banner",
    },
    {
        "sign": "white banner",
        "box": (478, 492, 240, 335),
        "text": {3, 4, 5, 6, 9, 0xA, 0xB},
        "base": 7,
        "ink": 9,
        "word": "white banner",
    },
]
SALE: dict[str, Any] = {
    "columns": (418, 493),
    "rows": (400, 431),
    "interior": 6,
    "text": {0xA, 0xB},
    "ink": 0xA,
    "word": "facade sale sign",
}


@dataclass
class Art:
    blank: bytes  # the whole file, signs blank (for the disc)
    english: bytes  # the whole file, English signs
    changed_blocks: list[int]  # file offsets of blocks that differ from the source


class Sheet:
    """Pixel access to the sign blocks of a ``ST00_FNT.BIN`` copy."""

    def __init__(self, data: bytes, sign_map: Mapping[str, Any]) -> None:
        self.data = bytearray(data)
        self.blocks = {
            tuple(b["plane_block"]): int(b["file_offset"], 16)
            for s in sign_map["signs"]
            for b in s["blocks"]
        }

    def _at(self, x: int, y: int) -> tuple[int, bool]:
        off = self.blocks[(x // 16, y // 16)]
        sx, sy = x % 16, y % 16
        return off + ((sy // 8) * 2 + sx // 8) * 32 + (sy % 8) * 4 + (
            sx % 8
        ) // 2, sx % 2 == 0

    def has(self, x: int, y: int) -> bool:
        return (x // 16, y // 16) in self.blocks

    def get(self, x: int, y: int) -> int:
        a, high = self._at(x, y)
        return self.data[a] >> 4 if high else self.data[a] & 15

    def put(self, x: int, y: int, v: int) -> None:
        a, high = self._at(x, y)
        b = self.data[a]
        self.data[a] = (v << 4 | b & 15) if high else (b & 0xF0 | v)


def _robust_line(points: list[tuple[int, int]]) -> tuple[float, float]:
    """Least-squares y = a + b x, refitted without points over a pixel off."""

    def fit(pts: list[tuple[int, int]]) -> tuple[float, float]:
        n = len(pts)
        mx = sum(p[0] for p in pts) / n
        my = sum(p[1] for p in pts) / n
        b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sum(
            (p[0] - mx) ** 2 for p in pts
        )
        return my - b * mx, b

    a, b = fit(points)
    kept = [p for p in points if abs(p[1] - (a + b * p[0])) <= 1.0]
    return fit(kept)


def blank(sheet: Sheet) -> tuple[float, float, float]:
    """Blank every sign in place; return the sale sign's centre line as
    (a, 0, b), y = a + b x, for the English lettering."""
    for banner in BANNERS:
        x0, x1, y0, y1 = banner["box"]
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if sheet.get(x, y) in banner["text"]:
                    sheet.put(x, y, banner["base"])
    c0, c1 = SALE["columns"]
    r0, r1 = SALE["rows"]
    ink = [
        (x, y)
        for x in range(c0, c1 + 1)
        for y in range(r0, r1 + 1)
        if sheet.has(x, y) and sheet.get(x, y) in SALE["text"]
    ]
    mx = sum(p[0] for p in ink) / len(ink)
    my = sum(p[1] for p in ink) / len(ink)
    slope = sum((p[0] - mx) * (p[1] - my) for p in ink) / sum(
        (p[0] - mx) ** 2 for p in ink
    )
    # The sign's border rows lie just outside its interior colour: fit a
    # line to the topmost and one to the bottommost interior row of each
    # column (twice, dropping columns more than a pixel off the first fit,
    # where writing touches a border), then fill strictly between them.
    tops: list[tuple[int, int]] = []
    bottoms: list[tuple[int, int]] = []
    for x in range(c0, c1 + 1):
        centre = round(my + slope * (x - mx))
        inside = [
            y
            for y in range(centre - 7, centre + 8)
            if sheet.has(x, y) and sheet.get(x, y) == SALE["interior"]
        ]
        if len(inside) >= 3:
            tops.append((x, min(inside)))
            bottoms.append((x, max(inside)))
    top, bottom = _robust_line(tops), _robust_line(bottoms)
    for x in range(c0, c1 + 1):
        y0 = round(top[0] + top[1] * x)
        y1 = round(bottom[0] + bottom[1] * x)
        for y in range(y0, y1 + 1):
            if sheet.has(x, y):
                sheet.put(x, y, SALE["interior"])
    mid = ((top[0] + bottom[0]) / 2, (top[1] + bottom[1]) / 2)
    return mid[0], 0.0, mid[1]


def letter(
    sheet: Sheet,
    english: Mapping[str, str],
    font: Mapping[str, pairs.Glyph],
    fix: bytes,
    fit: tuple[float, float, float],
) -> None:
    """Draw the approved English words on blank signs."""
    for banner in BANNERS:
        x0, x1, y0, _ = banner["box"]
        for n, ch in enumerate(english[banner["word"]]):
            glyph = font[ch]
            ox = x0 + (x1 - x0 + 1 - 7) // 2
            oy = y0 + n * 14
            for gy, row in enumerate(glyph.rows):
                for gx, v in enumerate(row):
                    if v and v != pairs.SHADOW:
                        sheet.put(ox + glyph.left + gx, oy + gy, banner["ink"])
    line_a, _, line_b = fit
    c0, _ = SALE["columns"]
    for n, ch in enumerate(english[SALE["word"]]):
        if ch == " ":
            continue
        ox = c0 + 1 + n * 6
        oy = round(line_a + line_b * (ox + 3)) - 3
        tile = fix[32 * ord(ch) : 32 * ord(ch) + 32]
        for ty in range(8):
            for tx in range(8):
                b = tile[ty * 4 + tx // 2]
                if (b >> 4 if tx % 2 == 0 else b & 15) == 5:
                    sheet.put(ox + tx, oy + ty, SALE["ink"])


def build(
    source: bytes,
    approved: Mapping[str, Any],
    font: Mapping[str, pairs.Glyph],
    fix: bytes,
    sign_map: Mapping[str, Any] | None = None,
) -> Art:
    sign_map = sign_map or json.loads(SIGN_MAP.read_text())
    sheet = Sheet(source, sign_map)
    fit = blank(sheet)
    blank_data = bytes(sheet.data)
    letter(sheet, approved["english"], font, fix, fit)
    english = bytes(sheet.data)
    changed = sorted(
        off
        for off in set(sheet.blocks.values())
        if blank_data[off : off + 128] != source[off : off + 128]
        or english[off : off + 128] != source[off : off + 128]
    )
    for off in changed:
        if not SLICE[0] <= off < SLICE[1]:
            raise ValueError(f"block 0x{off:05X} outside the tail slice")
    return Art(blank_data, english, changed)
