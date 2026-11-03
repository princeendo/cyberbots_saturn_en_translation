"""Tests for tools.font.pairs with a synthetic font only."""

from __future__ import annotations

import json
from pathlib import Path

from tools.font import pairs


def synthetic_font(tmp_path: Path) -> Path:
    bar = [[1] + [0] * 6 + [2]] + [[0] * 8] * 15  # one white pixel, one shadow
    font = {
        "palette": ["666666", "ffffff", "111111"],
        "glyphs": {
            "4A": {"char": "A", "left": 0, "rows": bar},
            "64": {"char": "a", "left": 1, "rows": bar},
        },
    }
    path = tmp_path / "font.json"
    path.write_text(json.dumps(font))
    return path


def test_split_pairs_pads_odd_rows() -> None:
    assert pairs.split_pairs("Abc") == ["Ab", "c "]
    assert pairs.split_pairs("") == []


def test_render_pair_places_second_character_seven_pixels_on(tmp_path: Path) -> None:
    font = pairs.load_arcade_font(synthetic_font(tmp_path))
    cell = pairs.render_pair(font, "Aa")
    first_row = [(cell[i // 2] >> (4 * (1 - i % 2))) & 0xF for i in range(16)]
    # narrowed to 7 columns: A white at x 0, shadow at x 6;
    # a (left 1, second): white at x 8, shadow at x 14
    assert first_row[0] == 9 and first_row[8] == 9
    assert first_row[6] == 13 and first_row[14] == 13
    assert len(cell) == 128


def test_letter_wins_over_shadow(tmp_path: Path) -> None:
    font = pairs.load_arcade_font(synthetic_font(tmp_path))
    blank = ((0,) * 8,) * 15
    font["S"] = pairs.Glyph(0, ((0,) * 7 + (13,), *blank))  # shadow at x 7
    font["L"] = pairs.Glyph(0, ((9,) + (0,) * 7, *blank))  # letter at its x 0
    font["l"] = pairs.Glyph(-7, ((9,) + (0,) * 7, *blank))  # letter at x 0
    font["s"] = pairs.Glyph(-7, ((0,) * 7 + (13,), *blank))  # shadow at x 0

    def x7(cell: bytes) -> int:
        return cell[3] & 0xF

    assert x7(pairs.render_pair(font, "SL")) == 9  # a letter over a shadow
    assert (pairs.render_pair(font, "Ls")[0] >> 4) == 9  # a shadow under a letter


def test_unused_codes() -> None:
    text = (0x82A0).to_bytes(2, "big") + b"\n" + (0x82A2).to_bytes(2, "big")
    assert pairs.unused_codes([0x82A0, 0x82A2, 0x82A4], [text]) == [0x82A4]


def test_narrow_keeps_the_shadow_column() -> None:
    glyph = pairs.Glyph(0, ((9, 9, 0, 0, 9, 9, 0, 13),) + ((0,) * 8,) * 15)
    narrowed = pairs.narrow(glyph)
    assert len(narrowed.rows[0]) == 7
    assert narrowed.rows[0][-1] == 13
