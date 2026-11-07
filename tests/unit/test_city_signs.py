"""Unit tests for tools.text.city_signs (synthetic sheet only)."""

from __future__ import annotations

from tools.text import city_signs


def one_block_map() -> dict[str, object]:
    return {"signs": [{"blocks": [{"plane_block": [1, 2], "file_offset": "0x00080"}]}]}


def test_sheet_maps_plane_pixels_to_vdp2_cells() -> None:
    data = bytes(0x100)
    sheet = city_signs.Sheet(data, one_block_map())
    assert sheet.has(16, 32) and not sheet.has(15, 32)
    # pixel (16 + 9, 32 + 10): lower-right cell (3), row 2, byte 0, low nibble
    sheet.put(25, 42, 0xC)
    offset = 0x80 + 3 * 32 + 2 * 4 + 0
    assert sheet.data[offset] == 0x0C
    assert sheet.get(25, 42) == 0xC
    sheet.put(24, 42, 0x5)
    assert sheet.data[offset] == 0x5C


def test_robust_line_drops_outliers() -> None:
    points = [(x, 10 + x // 2) for x in range(0, 40, 2)] + [(41, 90)]
    a, b = city_signs._robust_line(points)
    assert abs(b - 0.5) < 0.05 and abs(a - 10) < 1
