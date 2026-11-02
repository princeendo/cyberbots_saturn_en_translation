"""Tests for tools.font.kanji with synthetic data only."""

from __future__ import annotations

from tools.font import kanji


def synthetic_font() -> bytes:
    return bytes((i * 7 + i // 32) & 0xFF for i in range(kanji.FILE_BYTES))


def test_tiles_of_first_glyphs() -> None:
    assert kanji.tiles(0) == (0, 1, 16, 17)
    assert kanji.tiles(1) == (2, 3, 18, 19)
    assert kanji.tiles(8) == (32, 33, 48, 49)


def test_decode_builds_cells_like_the_copy_routine() -> None:
    data = synthetic_font()
    cell = kanji.decode(data)[9]
    top_left, top_right, bottom_left, bottom_right = kanji.tiles(9)
    assert cell[0:4] == data[top_left * 32 : top_left * 32 + 4]
    assert cell[4:8] == data[top_right * 32 : top_right * 32 + 4]
    assert cell[8:12] == data[top_left * 32 + 4 : top_left * 32 + 8]
    assert cell[64:68] == data[bottom_left * 32 : bottom_left * 32 + 4]
    assert cell[124:128] == data[bottom_right * 32 + 28 : bottom_right * 32 + 32]


def test_repack_is_identical() -> None:
    data = synthetic_font()
    assert kanji.encode(kanji.decode(data)) == data


def test_code_table_rows_end_at_zero() -> None:
    table = bytearray(kanji.TABLE_ROWS * 64)
    table[0:4] = (0x82A0).to_bytes(2, "big") + (0x82A2).to_bytes(2, "big")
    table[64:66] = (0x4472).to_bytes(2, "big")
    data = bytes(16) + bytes(table)
    codes = kanji.read_code_table(data, offset=16)
    assert codes == [0x82A0, 0x82A2, 0x4472]
    assert kanji.tile_index(codes, 0x4472) == 0x2000 + kanji.first_tile(2)
    assert kanji.tile_index(codes, 0x8140) is None
