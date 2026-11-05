from tools.text.ending_timing import (
    endings,
    interval_and_wait,
    segment_interval,
    shares,
)


def test_shares_keep_the_total_and_split_the_spare_evenly() -> None:
    new, hold = shares([100, 50, 80], [40, None, 20])
    assert sum(new) == 230
    assert new[1] == 50  # a box left as it is keeps its window
    assert hold == 60  # (100 + 80 - 40 - 20) // 2
    assert new == [100, 50, 80]


def test_shares_remainder_goes_to_the_last_english_box() -> None:
    new, hold = shares([101, 100], [10, 10])
    assert hold == 90
    assert new == [100, 101]


def test_interval_and_wait_keeps_typing_plus_waits() -> None:
    # Japanese: 24 glyphs at 6 + 60 = 204; English 41 glyphs at 3 + 81 = 204.
    assert interval_and_wait([60], 24, 41, 6) == (3, [81])


def test_interval_and_wait_spreads_over_consecutive_waits_and_clips() -> None:
    # 32 x 6 + 480 = 672; 7 glyphs leave too much even at 6: waits at 255 each.
    interval, waits = interval_and_wait([240, 240], 32, 7, 6)
    assert waits == [255, 255]
    assert interval == 6
    # with slower typing allowed it still cannot reach 672 by 16
    assert interval_and_wait([240, 240], 32, 7, 6, 16) == (16, [255, 255])


def test_segment_interval_is_closest_to_the_japanese_typing() -> None:
    assert segment_interval(13, 42, 6) == 2  # 84 against 78
    assert segment_interval(16, 5, 5) == 5  # capped at the original
    assert segment_interval(16, 5, 5, 16) == 16  # 80 against 80


def test_endings_find_cues_waits_and_consecutive_waits() -> None:
    tokens = [
        (0x10, "open", 408),
        (0x12, "cue", 1),
        (0x14, "close", 408),
        (0x16, "open", 605),  # a name: no entry
        (0x18, "open", 412),
        (0x1A, "wait", 0xF0),
        (0x1C, "wait", 0xF0),
        (0x1E, "segment", 0),
    ]
    assert endings(tokens) == [
        (0x10, 408, "cue", 1, []),
        (0x18, 412, "wait", 0x1E0, [(0x1A, 0xF0), (0x1C, 0xF0)]),
    ]
