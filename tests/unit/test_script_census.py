"""Tests for the Shift-JIS string-block census, on synthetic data only."""

from __future__ import annotations

import struct
from pathlib import Path

from tools.text.script_census import (
    census,
    compact_lists,
    compare,
    find_blocks,
    find_load_base,
    parse_block,
    references,
    units,
    words,
)

LINES = [
    "あいうえお".encode("shift_jis"),
    "かきく!?".encode("shift_jis"),
    "さしすせそた".encode("shift_jis"),
    "Dr.なにぬ".encode("shift_jis"),
]


def aligned(lines: list[bytes], extra_zero_words: int = 0) -> bytes:
    out = b""
    for line in lines:
        out += line + b"\x00"
        out += b"\x00" * (-len(out) % 4) + b"\x00" * 4 * extra_zero_words
    return out


def image(base: int = 0x06060000) -> tuple[bytes, int]:
    header = b"\x12\x34\x56\x78" * 4 + b"FILE.BIN\x00\x00\x00\x00"
    start = len(header)
    block = aligned(LINES)
    body = header + block
    offsets = [start]
    for line in LINES[:-1]:
        offsets.append(offsets[-1] + ((len(line) + 4) & ~3))
    pointers = b"".join(struct.pack(">IHH", base + o, 0xFFFF, 0) for o in offsets)
    return body + b"\x7f\x7f\x7f\x7f" + pointers, start


def test_units_splits_single_and_double_byte() -> None:
    assert units("Aあ!".encode("shift_jis")) == [b"A", b"\x82\xa0", b"!"]


def test_parse_block_walks_aligned_lines_and_stops_at_binary() -> None:
    data, start = image()
    block = parse_block(data, start)
    assert [raw for _, raw in block.strings] == LINES
    assert block.end % 4 == 0
    assert data[block.end : block.end + 4] == b"\x7f\x7f\x7f\x7f"


def test_parse_block_skips_extra_zero_words() -> None:
    block = parse_block(aligned(LINES, extra_zero_words=2), 0)
    assert len(block.strings) == len(LINES)


def test_find_blocks_needs_enough_mostly_double_byte_lines() -> None:
    data, start = image()
    assert [b.start for b in find_blocks(data, min_strings=4)] == [start]
    assert find_blocks(data, min_strings=5) == []
    ascii_only = aligned([b"ABC", b"DEF", b"GHI", b"JKL"])
    assert find_blocks(ascii_only, min_strings=2) == []


def test_load_base_and_references() -> None:
    data, start = image(base=0x06060000)
    block = parse_block(data, start)
    offsets = [o for o, _ in block.strings]
    base, count = find_load_base(data, offsets)
    assert (base, count) == (0x06060000, 4)
    assert base is not None
    refs = references(words(data), base, offsets)
    assert [target for _, target in refs] == offsets
    assert len({location % 8 for location, _ in refs}) == 1


def test_census_record_holds_no_text(tmp_path: Path) -> None:
    data, start = image()
    path = tmp_path / "OVL.BIN"
    path.write_bytes(data)
    record = census(path, min_strings=4)
    assert record is not None
    assert record["load_base"] == "0x06060000"
    block = record["blocks"][0]  # type: ignore[index]
    assert block["start"] == start
    assert block["stats"]["single_byte_counts"]["21"] == 1
    serialized = repr(record).encode()
    assert all(line not in serialized for line in LINES)


def test_compare_counts_common_prefix(tmp_path: Path) -> None:
    data, _ = image()
    (tmp_path / "A.BIN").write_bytes(data)
    (tmp_path / "B.BIN").write_bytes(b"\x00" * 8 + data)
    first = census(tmp_path / "A.BIN", min_strings=4)
    second = census(tmp_path / "B.BIN", min_strings=4)
    assert first is not None and second is not None
    result = compare([first, second])
    assert result["A.BIN vs B.BIN"] == {
        "common_prefix_strings": 4,
        "strings": [4, 4],
    }


def test_find_blocks_rejects_short_graphics_runs() -> None:
    graphics = aligned([b"\xaa\xbb", b"\xcc\xaa", b"\xbb\xcc", b"\xaa\xaa"] * 2)
    assert find_blocks(graphics, min_strings=4) == []
    assert len(find_blocks(graphics, min_strings=4, min_longest=2)) == 1


def test_compact_lists_keeps_json_valid() -> None:
    import json

    data = {"table": [[0, 12, "ab12", 1], [16, 8, "cd34", 0]], "n": [1, 2]}
    text = compact_lists(json.dumps(data, indent=1))
    assert json.loads(text) == data
    assert '[0, 12, "ab12", 1]' in text
