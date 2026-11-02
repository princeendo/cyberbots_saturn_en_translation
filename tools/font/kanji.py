"""Decode and re-encode the dialogue font ``KANJI.BIN`` (`FONT-001`).

Run from the repository root:

    ./invenv.sh python -m tools.font.kanji KANJI.BIN [--check]
        [--sheet OUT.png] [--table STG0AS.BIN] [--json]

Format (`EXP-0020`, D-019). The file is loaded unchanged to VDP2 VRAM
``0x25E40000`` and holds 4-bit 8x8 tiles, 32 bytes each, in VDP2 cell
layout: 4 bytes per tile row, the high nibble is the left pixel. The tiles
form a sheet 16 tiles wide. Glyph ``g`` (0-1279) is 16x16 pixels and uses
tiles ``t``, ``t + 1``, ``t + 16`` and ``t + 17``, where
``t = (g // 8) * 32 + (g % 8) * 2``. The game's routine at ``0x06011224``
copies those tiles into a 128-byte cell: 16 rows of 8 bytes, the left tile's
row then the right tile's row. ``decode`` returns cells in that layout and
``encode`` inverts it.

Glyph numbers come from a table of 16-bit codes, at ``0x060AAD7C`` in the
resident ``STG0AS.BIN`` (file offset ``0x4AD7C``; the same bytes are in
``END.BIN`` and ``VICTORY.BIN``). It has 39 rows of 32 codes, and a 0 ends a
shorter row. A code's glyph is its position among the non-zero entries; the
game searches linearly (``0x0606E9E8``). The tile index it passes on is
``0x2000 + t``: VDP2 VRAM ``0x40000`` / 32.

``--check`` re-encodes the decoded glyphs and compares the result with the
file. ``--sheet`` writes a PNG of all glyphs, 32 per row, with values as gray
levels. ``--table`` reads the code table from that file. The output holds
counts, offsets and hashes, never glyph images or text (`AGENTS.md` rule
21). The PNG goes wherever the user puts it, under an ignored path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from tools.memory.mcs_extract import encode_png

TILE_BYTES = 32
CELL_BYTES = 128  # 16 x 16 pixels at 4 bpp
SHEET_TILES = 16  # tiles per sheet row
GLYPHS_PER_GROUP = 8
GLYPHS = 1280
FILE_BYTES = GLYPHS * CELL_BYTES
TILE_BASE = 0x2000  # VDP2 VRAM 0x40000 / 32
TABLE_OFFSET = 0x4AD7C  # in STG0AS.BIN; WRAM-H 0x060AAD7C
TABLE_ROWS = 39
TABLE_ROW_CODES = 32


def first_tile(glyph: int) -> int:
    """Top-left tile of ``glyph`` within the file."""
    return (glyph // GLYPHS_PER_GROUP) * 2 * SHEET_TILES + (
        glyph % GLYPHS_PER_GROUP
    ) * 2


def tiles(glyph: int) -> tuple[int, int, int, int]:
    """Top-left, top-right, bottom-left, bottom-right tiles of ``glyph``."""
    t = first_tile(glyph)
    return t, t + 1, t + SHEET_TILES, t + SHEET_TILES + 1


def decode(data: bytes) -> list[bytes]:
    """Split the file into 128-byte glyph cells, as the game builds them."""
    if len(data) != FILE_BYTES:
        raise ValueError(f"expected {FILE_BYTES} bytes, got {len(data)}")
    cells = []
    for glyph in range(GLYPHS):
        top_left, top_right, bottom_left, bottom_right = tiles(glyph)
        cell = bytearray()
        for row in range(16):
            left, right = (
                (top_left, top_right) if row < 8 else (bottom_left, bottom_right)
            )
            r = row % 8
            cell += data[left * TILE_BYTES + r * 4 : left * TILE_BYTES + r * 4 + 4]
            cell += data[right * TILE_BYTES + r * 4 : right * TILE_BYTES + r * 4 + 4]
        cells.append(bytes(cell))
    return cells


def encode(cells: Sequence[bytes]) -> bytes:
    """Inverse of ``decode``."""
    if len(cells) != GLYPHS or any(len(c) != CELL_BYTES for c in cells):
        raise ValueError(f"expected {GLYPHS} cells of {CELL_BYTES} bytes")
    data = bytearray(FILE_BYTES)
    for glyph, cell in enumerate(cells):
        top_left, top_right, bottom_left, bottom_right = tiles(glyph)
        for row in range(16):
            left, right = (
                (top_left, top_right) if row < 8 else (bottom_left, bottom_right)
            )
            r = row % 8
            data[left * TILE_BYTES + r * 4 : left * TILE_BYTES + r * 4 + 4] = cell[
                row * 8 : row * 8 + 4
            ]
            data[right * TILE_BYTES + r * 4 : right * TILE_BYTES + r * 4 + 4] = cell[
                row * 8 + 4 : row * 8 + 8
            ]
    return bytes(data)


def read_code_table(data: bytes, offset: int = TABLE_OFFSET) -> list[int]:
    """Codes in glyph order: 39 rows of 32 big-endian words, 0 ends a row."""
    codes = []
    for row in range(TABLE_ROWS):
        base = offset + row * TABLE_ROW_CODES * 2
        for index in range(TABLE_ROW_CODES):
            code = int.from_bytes(data[base + index * 2 : base + index * 2 + 2], "big")
            if code == 0:
                break
            codes.append(code)
    return codes


def tile_index(codes: Sequence[int], code: int) -> int | None:
    """The tile index the game passes to its copy routine, or None (no glyph)."""
    if code not in codes:
        return None
    return TILE_BASE + first_tile(codes.index(code))


def sheet(cells: Sequence[bytes], columns: int = 32) -> tuple[int, int, bytes]:
    """Width, height and RGB pixels of all glyphs, ``columns`` per row."""
    rows = (len(cells) + columns - 1) // columns
    width, height = columns * 16, rows * 16
    rgb = bytearray(width * height * 3)
    for glyph, cell in enumerate(cells):
        x0, y0 = (glyph % columns) * 16, (glyph // columns) * 16
        for y in range(16):
            for x in range(16):
                byte = cell[y * 8 + x // 2]
                value = (byte >> 4) if x % 2 == 0 else (byte & 0xF)
                level = value * 17
                offset = ((y0 + y) * width + x0 + x) * 3
                rgb[offset : offset + 3] = bytes((level, level, level))
    return width, height, bytes(rgb)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decode the KANJI.BIN dialogue font.")
    parser.add_argument("font", type=Path)
    parser.add_argument("--check", action="store_true", help="byte-identical repack")
    parser.add_argument("--sheet", type=Path, help="write a PNG of every glyph")
    parser.add_argument("--table", type=Path, help="file holding the code table")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    data = args.font.read_bytes()
    cells = decode(data)
    report: dict[str, object] = {
        "font": str(args.font),
        "sha256": hashlib.sha256(data).hexdigest(),
        "glyphs": GLYPHS,
        "blank_glyphs": sum(1 for c in cells if not any(c)),
        "values": sorted({n for c in cells for b in c for n in (b >> 4, b & 0xF)}),
    }
    if args.check:
        report["repack_identical"] = encode(cells) == data
    if args.table:
        codes = read_code_table(args.table.read_bytes())
        report["table_codes"] = len(codes)
        report["table_duplicates"] = len(codes) - len(set(codes))
        report["table_non_sjis"] = sum(1 for c in codes if c < 0x8140)
        report["blank_glyphs_in_table"] = sum(
            1 for g in range(len(codes)) if not any(cells[g])
        )
    if args.sheet:
        width, height, rgb = sheet(cells)
        args.sheet.write_bytes(encode_png(width, height, rgb))
    print(json.dumps(report, indent=None if not args.json else 1))
    if args.check and not report["repack_identical"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
