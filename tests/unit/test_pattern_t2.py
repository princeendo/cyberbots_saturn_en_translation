"""Tests for tools.text.pattern_t2 (synthetic data only)."""

from __future__ import annotations

import random

import pytest

from tools.text import pattern_t2 as t2


def record(
    width: int, height: int, controls: list[int], literals: list[bytes]
) -> bytes:
    body = bytes(controls) + b"\0" * (-len(controls) % 4)
    head = t2.header(width, height).to_bytes(2, "big") + len(body).to_bytes(2, "big")
    return head + body + b"".join(literals)


def test_header_and_size() -> None:
    assert t2.header(72, 16) == 0x2910
    assert t2.size_of(bytes.fromhex("2910")) == (72, 16)
    with pytest.raises(t2.FormatError):
        t2.header(12, 16)
    with pytest.raises(t2.FormatError):
        t2.size_of(bytes.fromhex("1910"))


def test_decode_each_operation() -> None:
    a, b = b"\x11\x22\x33\x44", b"\x55\x66\x77\x88"
    # 8 x 4 pixels: row = 4 bytes, 4 longs.
    rec = record(8, 4, [1, 17, 192], [a, b])  # two literals, back 8 bytes, fill
    assert t2.decode(rec) == a + b + a + b"\x33\x44\x33\x44"
    rec = record(8, 4, [0, 209, 0], [a, b])  # literal, row above x2, literal
    assert t2.decode(rec) == a + a + a + b


def test_decode_rejects_bad_reference() -> None:
    with pytest.raises(t2.FormatError):
        t2.decode(record(8, 2, [208, 0], [b"\0" * 4]))


@pytest.mark.parametrize("width", [8, 16, 72, 120])
def test_encode_round_trip(width: int) -> None:
    rnd = random.Random(width)
    height = 16
    rows = []
    base = bytes(rnd.choice([0, 0x66, 0x6F, 0xF6]) for _ in range(width // 2))
    for _ in range(height):
        row = bytearray(base)
        for _ in range(3):
            row[rnd.randrange(len(row))] = rnd.randrange(256)
        rows.append(bytes(row))
    pixels = b"".join(rows)
    rec = t2.encode(pixels, width, height)
    assert t2.decode(rec) == pixels
    assert t2.size_of(rec) == (width, height)


def test_encode_compresses_flat_art() -> None:
    pixels = b"\x66" * (60 * 16)
    rec = t2.encode(pixels, 120, 16)
    assert len(rec) < 64
    assert t2.decode(rec) == pixels


def test_records_of_cuts_at_next_offset() -> None:
    blob = bytes(range(32))
    assert t2.records_of(blob, [8, 0, 8]) == {0: blob[:8], 8: blob[8:]}
