"""Tests for the Saturn-to-arcade line pairing, on synthetic data only."""

from __future__ import annotations

from tools.text.arcade_pairing import (
    align,
    decode,
    edited_pairs,
    learn_map,
    read_jp_record,
    runs,
)


def chars(text: str) -> tuple[bytes, ...]:
    return tuple(char.encode("shift_jis") for char in text)


SATURN = [chars(t) for t in ["あいう", "いうえお", "おかき", "くけこ", "あいか"]]
CODES = {char: 0x1000 + n for n, char in enumerate("あいうえおかきくけこ")}


def codes(text: str) -> tuple[int, ...]:
    return tuple(CODES[char] for char in text)


def test_read_jp_record_splits_lines_and_stops() -> None:
    body = bytes(8) + b"\x10\x01\x10\x02\xff\xff\x10\x03\x00\x0e"
    assert read_jp_record(body, 0) == [(0x1001, 0x1002), (0x1003,)]


def test_read_jp_record_keeps_spaces() -> None:
    body = bytes(8) + b"\x10\x01\x00\x20\x10\x02\x00\x00"
    assert read_jp_record(body, 0) == [(0x1001, 0x0020, 0x1002)]


def test_learn_map_from_scripts() -> None:
    arcade = [codes(t) for t in ["あいう", "いうえお", "おかき", "くけこ"]]
    mapping, conflicts = learn_map(arcade, SATURN)
    assert conflicts == 0
    assert decode(codes("くけこ"), mapping) == chars("くけこ")


def test_learn_map_counts_conflicts() -> None:
    arcade = [codes("あいう"), codes("あいう")]
    _, conflicts = learn_map(arcade, [chars("あいう"), chars("あいえ")])
    assert conflicts == 1


def test_align_keeps_order_and_skips_additions() -> None:
    first = [chars("あいう"), chars("おかき")]
    second = [chars("あいう"), chars("いうえお"), chars("おかき")]
    assert align(first, second) == [(0, 0), (1, 2)]


def test_edited_pairs_stay_between_anchors() -> None:
    first = [chars("あいう"), chars("いうえか"), chars("おかき")]
    second = [chars("あいう"), chars("いうえお"), chars("おかき"), chars("いうえか")]
    # The identical line at Saturn index 3 lies after the anchor (2, 2), so
    # only the edited line inside the gap may pair.
    assert edited_pairs(first, second, [(0, 0), (2, 2)], min_ratio=0.6) == [
        (1, 1, 0.75)
    ]
    assert edited_pairs(first, second, [(0, 0), (2, 2)], min_ratio=0.9) == []


def test_runs() -> None:
    assert runs([5, 1, 2, 3, 7, 8]) == [[1, 3], [5, 5], [7, 8]]
