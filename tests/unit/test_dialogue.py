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


def test_allocate_codes_stops_beyond_the_approved_sacrifice() -> None:
    args = (["aa", "bb", "cc"], [0x1000], 0, [0x2000, 0x3000])
    _, _, sacrificed = dialogue.allocate_codes(*args, max_sacrifice=2)
    assert sacrificed == [0x2000, 0x3000]
    with pytest.raises(ValueError, match="more than 1"):
        dialogue.allocate_codes(*args, max_sacrifice=1)


def test_wanted_pairs_share_one_pool_in_first_use_order() -> None:
    jin = dialogue.Box(box=1, slot=1, lines=(0,), rows=("abcd",))
    other = dialogue.Box(box=70, slot=70, lines=(130,), rows=("cdef  ab",))
    assert dialogue.wanted_pairs([jin, other]) == ["ab", "cd", "ef"]


def test_kept_lines_are_those_a_box_outside_the_build_uses() -> None:
    users = {10: {1}, 11: {1, 300}, 12: {1, 70}}
    assert dialogue.kept_lines([10, 11, 12], users, ours={1, 70}) == [11]


def test_dead_lines_are_used_only_by_ending_boxes() -> None:
    box_lines: dict[int, tuple[int, ...]] = {400: (750, 751), 401: (752,)}
    users = {750: {400}, 751: {400, 300}, 752: {401, 1}}
    dead = dialogue.dead_lines({400, 401}, box_lines, users, ours={1})
    assert dead == [750, 752]


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
