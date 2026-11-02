"""Tests for the Cyberbots arcade dialogue decoder, on synthetic images only."""

from __future__ import annotations

from tools.reference.cybots_text import (
    DECODE,
    decode,
    find_tables,
    read_table,
    table_report,
)

ENCODE = {char: code for code, char in DECODE.items()}


def encode(text: str) -> bytes:
    return bytes(0xFF if char == "\n" else ENCODE[char] for char in text)


def record(text: str, x: int = 0x7C) -> bytes:
    body = bytes([0, 0, 0, x, 0, 0xA8, 0, 0x0E]) + encode(text) + b"\x00"
    return body + b"\x00" * (-len(body) % 2)


def image_with_table(texts: list[str], order: list[int]) -> tuple[bytes, int]:
    table_at = 0x40
    records_at = table_at + 4 * len(order)
    blob = b""
    addresses = []
    for text in texts:
        addresses.append(records_at + len(blob))
        blob += record(text)
    table = b"".join(addresses[i].to_bytes(4, "big") for i in order)
    return b"\xaa" * table_at + table + blob + b"\x00" * 16, table_at


def test_map_is_one_tile_sheet() -> None:
    assert DECODE[0x40] == "0" and DECODE[0x49] == "9"
    assert DECODE[0x4A] == "A" and DECODE[0x63] == "Z"
    assert DECODE[0x64] == "a" and DECODE[0x7D] == "z"
    assert (DECODE[0x7E], DECODE[0x7F]) == ("?", "!")


def test_decode_marks_unknown_codes_and_breaks_lines() -> None:
    assert decode(encode("It's me!\nOk.") + b"\x09") == "It's me!\nOk.{09}"


def test_find_and_read_table_with_shared_records() -> None:
    texts = ["Hello, pilot.", "Who are you?", "Go!"]
    image, table_at = image_with_table(texts, [0, 1, 2, 1])
    assert find_tables(image, min_entries=3) == [(table_at, 4)]
    records = read_table(image, table_at, 4)
    assert [decode(r.codes) for r in records] == [*texts, texts[1]]
    assert records[0].header == (0, 0x7C, 0xA8, 0x0E)


def test_report_counts_without_text() -> None:
    texts = ["Hello, pilot.", "Who are you?", "Go!"]
    image, table_at = image_with_table(texts, [0, 1, 2, 1])
    report = table_report(image, table_at, 4)
    assert report["entries"] == 4 and report["distinct_records"] == 3
    assert report["unmapped_codes"] == {}
    assert report["latin_map_coverage"] == 1.0
    assert "pilot" not in repr(report)


def test_short_runs_are_not_tables() -> None:
    image, _ = image_with_table(["A.", "B."], [0, 1])
    assert find_tables(image, min_entries=3) == []
