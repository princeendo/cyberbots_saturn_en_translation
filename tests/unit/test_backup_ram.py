"""Copied from MSHvSF ``tests/unit/test_backup_ram.py`` at ``447e573``, plus the
corruption parameters (`BOOT-001`).

Copied into the Cyberbots repository from the XvSF repository,
``tests/unit/test_backup_ram.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import pytest

from tools.mednafen.backup_ram import BLOCK, BLOCKS, FORMAT, corrupt, with_free


def file_blocks(image: bytes | bytearray, first: int) -> list[int]:
    """A file's blocks, from its block list (which continues into those blocks)."""
    others: list[int] = []
    stream = image[first * BLOCK + 34 : (first + 1) * BLOCK]
    following = 0
    while True:
        while len(stream) >= 2:
            value = int.from_bytes(stream[:2], "big")
            stream = stream[2:]
            if value == 0:
                return [first, *others]
            others.append(value)
        n = others[following]
        following += 1
        stream += image[n * BLOCK + 4 : (n + 1) * BLOCK]


def test_with_free_leaves_exactly_that_many_blocks() -> None:
    image = with_free(500)
    assert image[:BLOCK] == FORMAT
    assert len(file_blocks(image, 2)) == BLOCKS - 2 - 500


def test_with_free_fills_every_listed_block() -> None:
    image = with_free(8)
    assert file_blocks(image, 2) == list(range(2, BLOCKS - 8))
    size = int.from_bytes(image[2 * BLOCK + 30 : 2 * BLOCK + 34], "big")
    others = BLOCKS - 2 - 8 - 1
    stream = 2 * (others + 1) + size
    assert (BLOCK - 34) + (BLOCK - 4) * (others - 1) < stream
    assert stream <= (BLOCK - 34) + (BLOCK - 4) * others


def test_corrupt_inverts_one_byte() -> None:
    image = bytes(range(256)) * 128
    out = corrupt(image)
    assert sum(a != b for a, b in zip(image, out, strict=True)) == 1


def test_too_much_free_space_is_rejected() -> None:
    with pytest.raises(ValueError):
        with_free(BLOCKS)


def test_corrupt_inverts_the_chosen_byte() -> None:
    image = bytes(BLOCK * BLOCKS)
    out = corrupt(image, block=7, offset=3)
    assert out[7 * BLOCK + 3] == 0xFF
    with pytest.raises(ValueError):
        corrupt(image, offset=BLOCK)


def test_the_most_free_space_is_a_one_block_file() -> None:
    image = with_free(BLOCKS - 3)
    assert file_blocks(image, 2) == [2]
