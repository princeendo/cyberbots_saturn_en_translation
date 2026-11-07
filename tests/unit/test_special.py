"""SPECIAL-017's build helpers, on synthetic data."""

from __future__ import annotations

import struct

import pytest

from tools.text import dialogue, name_art


def test_shift_rows_fixed_indents_when_the_fixed_pairs_cover_it() -> None:
    # "AB" as is needs pair "AB"; indented, " A" and "B " are fixed already.
    assert dialogue.shift_rows_fixed(["AB"], {" A", "B "}) == [" AB"]
    # With "AB" fixed, the row stays as it is (ties keep it).
    assert dialogue.shift_rows_fixed(["AB"], {"AB"}) == ["AB"]


def test_shift_rows_fixed_never_indents_a_full_row() -> None:
    row = "X" * dialogue.ROW_CHARS
    assert dialogue.shift_rows_fixed([row], set()) == [row]


def test_special_boxes_skips_official_and_blank() -> None:
    doc = {
        "boxes": [
            {"section": "story", "box": 1, "english": "Hello there."},
            {"section": "story", "box": 2, "english": None, "official_slot": 610},
            {"section": "story", "box": 3, "english": ""},
            {"section": "ending", "box": 4, "english": "Elsewhere."},
        ]
    }
    lines = {1: [10, 11], 2: [12], 3: [13], 4: [14]}
    boxes = dialogue.special_boxes([doc], lines, "story")
    assert boxes == [dialogue.Box(1, -1, (10, 11), ("Hello there.",))]


def test_special_boxes_refuses_four_rows() -> None:
    doc = {"boxes": [{"section": "story", "box": 1, "english": "word " * 40}]}
    with pytest.raises(SystemExit):
        dialogue.special_boxes([doc], {1: [0]}, "story")


def test_parts_of_follows_the_last_part_flag() -> None:
    frames = name_art.VS_FRAMES
    table = bytearray(name_art.VS_FRAME_TABLE + 2 * frames)
    # Frame 1 starts at part 4; frame 2's entry is a 0 terminator.
    struct.pack_into(">H", table, name_art.VS_FRAME_TABLE, 4)
    pl = bytearray(name_art.VS_PART_SIZE * 8)
    struct.pack_into(">H", pl, name_art.VS_PART_SIZE * 6 + 2, name_art.LAST_PART)
    assert list(name_art.parts_of(bytes(table), bytes(pl), 1)) == [4, 5, 6]
