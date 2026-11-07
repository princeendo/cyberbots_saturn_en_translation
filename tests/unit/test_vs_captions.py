"""Unit tests for tools.text.vs_captions (UI-006), synthetic data only."""

from __future__ import annotations

import pytest

from tools.font import pairs
from tools.text import vs_captions


def test_centred_pads_to_the_middle() -> None:
    assert vs_captions.centred("ABCD") == " " * 11 + "ABCD"
    assert vs_captions.centred("A" * 26) == "A" * 26
    with pytest.raises(ValueError):
        vs_captions.centred("A" * 27)


def test_new_pairs_skips_story_pairs_and_spaces() -> None:
    rows = {2: "  ABCD", 1: "ABXY"}
    assert vs_captions.new_pairs(rows, {"AB": 1}) == ["XY", "CD"]


def test_best_offsets_prefers_a_half_cell_shift_that_reuses_pairs() -> None:
    text = "ABCD"  # centred: 11 spaces -> " A", "BC", "D "
    rows = vs_captions.best_offsets({1: text}, {"AB": 1, "CD": 2})
    assert rows[1] == " " * 10 + text  # even start: "AB", "CD"
    story = {" A": 1, "BC": 2, "D ": 3}
    assert vs_captions.best_offsets({1: text}, story)[1] == vs_captions.centred(text)


def test_leftover_follows_first_fit() -> None:
    room = [[0, 8], [16, 40]]
    assert vs_captions.leftover([b"x" * 8, b"y" * 4], room) == [[20, 40]]
    with pytest.raises(ValueError):
        vs_captions.leftover([b"z" * 30], room)


def test_row_bytes_codes_spaces_and_aligns() -> None:
    data = vs_captions.row_bytes("  AB", {"AB": 0x1234}, 0x8140)
    assert data == bytes.fromhex("81401234") + b"\0" + b"\0\0\0"
    assert len(data) % 4 == 0


def test_compile_writes_rows_pointers_and_glyphs() -> None:
    base, records = vs_captions.BASE, vs_captions.RECORDS
    stg = bytearray(0x50000)
    record = 0x060A0000
    stg[records - base + 4 * 7 : records - base + 4 * 7 + 4] = record.to_bytes(4, "big")
    glyph = pairs.Glyph(0, tuple((9,) * 6 for _ in range(16)))
    font = {"A": glyph, "B": glyph}
    table = [0x8001, 0x8002, 0x8003]
    cells = [bytes(128)] * 3
    approved = {"captions": [{"box": 7, "english": "AB"}]}
    out = vs_captions.compile_captions(
        approved, stg, cells, table, {}, font, [0x8003], [[0x100, 0x200]], 0x8140
    )
    assert out.new_pairs == {"AB": 0x8003}
    assert cells[2] == pairs.render_pair(font, "AB")
    row = out.rows[7]
    off = out.placed[7]
    assert (
        stg[off : off + len(row)]
        == vs_captions.row_bytes(row, {"AB": 0x8003}, 0x8140)[: len(row)]
    )
    pointer = int.from_bytes(stg[record - base + 8 : record - base + 12], "big")
    assert pointer == base + off
    with pytest.raises(ValueError):
        vs_captions.compile_captions(
            {"captions": [{"box": 7, "english": "BA"}]},
            stg,
            cells,
            table,
            {},
            font,
            [],
            [[0x100, 0x200]],
            0x8140,
        )
