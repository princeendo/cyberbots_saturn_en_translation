"""Tests for tools.text.name_art (synthetic data only)."""

from __future__ import annotations

import pytest

from tools.text import boot_warnings
from tools.text import name_art as na

FONT: boot_warnings.Font = {
    ch: [(x, y, 0) for x in range(1, 6) for y in range(3, 12)] + [(6, 5, "shadow")]
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz·&-8"
}


def test_banner_shape() -> None:
    grid = na.banner(120)
    assert all(v == 0 for v in grid[0]) and all(v == 0 for v in grid[15])
    assert grid[3][8] == na.BAR and grid[3][7] == 0
    assert grid[11][0] == na.BAR and grid[11][111] == na.BAR and grid[11][112] == 0


def test_letters_and_bounds() -> None:
    grid = na.banner(40)
    end = na.letters(grid, FONT, "AB", 4)
    assert end == 20
    assert grid[5][5] == na.RAMP[0] and grid[5][10] == na.SHADOW
    with pytest.raises(na.NameArtError):
        na.letters(na.banner(16), FONT, "ABC", 4)
    with pytest.raises(na.NameArtError):
        na.letters(na.banner(40), FONT, "?", 0)


def test_flips_and_packing() -> None:
    grid = [[1, 2], [3, 4]]
    assert na.stored(grid, 1) == [[2, 1], [4, 3]]
    assert na.stored(grid, 2) == [[3, 4], [1, 2]]
    assert na.stored(na.stored(grid, 3), 3) == grid
    assert na.pack(grid) == bytes([0x12, 0x34])
    assert na.unpack(bytes([0x12, 0x34]), 2, 2) == grid
    with pytest.raises(na.NameArtError):
        na.pack([[1, 2, 3]])


def test_code_of_crops_code_pixels() -> None:
    grid = [[0] * 20 for _ in range(16)]
    grid[2][10] = 10
    grid[4][14] = 12
    grid[5][3] = 3  # not a code colour
    code = na.code_of(grid)
    assert len(code) == 5 and len(code[0]) == 5
    assert code[2][0] == 10 and code[4][4] == 12
    with pytest.raises(na.NameArtError):
        na.code_of([[0, 3], [3, 0]])


def test_frame_parts() -> None:
    table = bytes([0, 1, 0, 3, 0, 4])
    assert list(na.frame_parts(table, 0, 3, 1)) == [1, 2]
    assert list(na.frame_parts(table, 0, 3, 3)) == [4]
