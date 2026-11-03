"""Tests for tools.text.dialogue with synthetic data only."""

from __future__ import annotations

import pytest

from tools.text import dialogue


def test_wrap_reflows_record_lines() -> None:
    rows = dialogue.wrap("one two\nthree four five six seven eight nine")
    assert all(len(r) <= dialogue.ROW_CHARS for r in rows)
    assert " ".join(rows) == "one two three four five six seven eight nine"


def test_cells_skip_space_pairs() -> None:
    assert dialogue.cells_of(["ab  cd"]) == 2
    assert dialogue.cells_of(["abc"]) == 2  # "ab", "c "


def test_allocate_codes_in_order_unused_then_new_then_rare() -> None:
    codes, new, sacrificed = dialogue.allocate_codes(
        ["aa", "bb", "cc", "dd"], unused=[0x1000], new_slots=2, rare=[0x2000, 0x3000]
    )
    assert codes == {"aa": 0x1000, "bb": 0xF040, "cc": 0xF041, "dd": 0x2000}
    assert new == [0xF040, 0xF041]
    assert sacrificed == [0x2000]


def test_allocate_codes_fails_when_out_of_codes() -> None:
    with pytest.raises(ValueError):
        dialogue.allocate_codes(["aa", "bb"], unused=[1], new_slots=0, rare=[])


def test_place_first_fit() -> None:
    assert dialogue.place([b"x" * 8, b"y" * 4, b"z" * 8], [(0, 12), (100, 120)]) == [
        0,
        8,
        100,
    ]
    with pytest.raises(ValueError):
        dialogue.place([b"x" * 16], [(0, 12)])


def test_row_bytes_and_record_entries() -> None:
    data = dialogue.row_bytes("ab  c", {"ab": 0x1234, "c ": 0x5678})
    assert data == bytes.fromhex("1234814056780000")
    assert len(data) % 4 == 0
    entries = dialogue.record_entries([0x06070000, 0x06070010])
    assert entries == bytes.fromhex("06070000ffff00000607001000000000")


def test_codes_in_skips_line_breaks() -> None:
    assert dialogue.codes_in(bytes.fromhex("82a00a82a2")) == {0x82A0, 0x82A2}
