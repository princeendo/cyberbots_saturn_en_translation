"""Pair glyphs: two arcade English characters in one Saturn 16 x 16 font cell.

The route chosen in `LAYOUT-001` (`docs/localization_policy.md`, 2026-11-02):
English is drawn two characters per glyph of the dialogue font `KANJI.BIN`
(D-019). The Saturn draws a cell every 14 pixels (D-020), so placing a pair's
second character 7 pixels after its first keeps a steady 7-pixel advance.

The letters are the arcade's own (`EXP-0025`): glyphs cut from MAME code
sheets into ``arcade_font.json`` (an ignored path; never committed). Each
arcade glyph is a letter in shades ``#FFFFFF``/``#DDDDDD``/``#AAAAAA``/``#555555``
with a 1-pixel ``#111111`` shadow, at an 8-pixel advance. Those shades map one
to one onto the Saturn font's values 9, 10, 11, 12 and 13, which the Saturn
draws as ``#F0F0F0``, ``#D0D0D0``, ``#A0A0A0``, ``#707070`` and ``#101010``
(`EXP-0025`). Where two characters overlap, a letter pixel wins over a shadow
pixel.

``load_arcade_font`` narrows each letter to 7 columns, shadow included
(``narrow``). ``split_pairs`` cuts a row of text into pairs, and
``render_pair`` makes the
128-byte cell (16 rows of 8 bytes, high nibble left, the layout of
``tools.font.kanji.decode``).
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

ADVANCE = 7  # pixels per character inside and across pair cells
FIRST_X = 0  # the first character's cell origin inside the pair cell
SHADOW = 13
# arcade RGB -> Saturn glyph value (EXP-0025)
ARCADE_TO_SATURN = {
    "666666": 0,
    "ffffff": 9,
    "dddddd": 10,
    "aaaaaa": 11,
    "555555": 12,
    "111111": 13,
}


@dataclass(frozen=True)
class Glyph:
    left: int  # first inked column relative to the character's origin
    rows: tuple[tuple[int, ...], ...]  # 16 rows of Saturn values


def load_arcade_font(path: Path) -> dict[str, Glyph]:
    """Characters of ``arcade_font.json`` as Saturn-valued glyphs.

    Codes that decode to the same character keep the first one in code order,
    except that ``.`` is taken from ``0x14`` (the dialogue period).
    """
    font = json.loads(path.read_text())
    palette = [ARCADE_TO_SATURN.get(c) for c in font["palette"]]
    out: dict[str, Glyph] = {}
    for code in sorted(font["glyphs"], key=lambda c: int(c, 16)):
        entry = font["glyphs"][code]
        char = entry["char"]
        if not char or (char in out and not (char == "." and code == "14")):
            continue
        rows = []
        for row in entry["rows"]:
            values = [palette[i] for i in row]
            if any(v is None for v in values):
                break
            rows.append(tuple(v for v in values if v is not None))
        else:
            out[char] = narrow(Glyph(entry["left"], tuple(rows)))
    return out


def narrow(glyph: Glyph, width: int = ADVANCE) -> Glyph:
    """Remove the columns most like their right neighbours until ``width`` is left.

    The arcade's letters are 7 pixels wide plus a 1-pixel shadow, at an
    8-pixel advance. At a 7-pixel advance, wide letters would touch. Their
    stems are 2 pixels thick, so removing one column of a doubled stem keeps
    the letter's shape and leaves a 1-pixel gap. The shadow column (the last)
    is kept.
    """
    columns = [tuple(row[x] for row in glyph.rows) for x in range(len(glyph.rows[0]))]
    while len(columns) > width:
        body = range(len(columns) - 2)
        i = min(
            body,
            key=lambda k: sum(
                a != b for a, b in zip(columns[k], columns[k + 1], strict=True)
            ),
        )
        del columns[i + 1]
    rows = tuple(tuple(col[y] for col in columns) for y in range(len(glyph.rows)))
    return Glyph(glyph.left, rows)


def split_pairs(row: str) -> list[str]:
    """Two characters per cell; an odd row ends with a space."""
    padded = row + " " * (len(row) % 2)
    return [padded[i : i + 2] for i in range(0, len(padded), 2)]


def render_pair(font: dict[str, Glyph], pair: str) -> bytes:
    """The 128-byte Saturn cell for ``pair`` (two characters; space allowed)."""
    if len(pair) != 2:
        raise ValueError(f"a pair has two characters: {pair!r}")
    pixels = [[0] * 16 for _ in range(16)]
    for index, char in enumerate(pair):
        if char == " ":
            continue
        glyph = font[char]
        origin = FIRST_X + ADVANCE * index + glyph.left
        for y, row in enumerate(glyph.rows):
            for dx, value in enumerate(row):
                x = origin + dx
                if not value or not 0 <= x < 16:
                    continue
                if pixels[y][x] and pixels[y][x] != SHADOW and value == SHADOW:
                    continue
                pixels[y][x] = value
    return bytes(
        (pixels[y][x] << 4) | pixels[y][x + 1]
        for y in range(16)
        for x in range(0, 16, 2)
    )


def unused_codes(codes: Sequence[int], texts: Sequence[bytes]) -> list[int]:
    """Table codes no line of ``texts`` uses (two bytes per glyph; ``0x0A`` skipped)."""
    used: set[int] = set()
    for text in texts:
        i = 0
        while i < len(text) - 1:
            if text[i] == 0x0A:
                i += 1
                continue
            used.add(int.from_bytes(text[i : i + 2], "big"))
            i += 2
    return [c for c in codes if c not in used]
