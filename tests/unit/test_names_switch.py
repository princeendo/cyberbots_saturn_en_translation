"""Tests for tools.text.names_switch (synthetic files only: zero bytes with
the expected original words planted where the patches check them)."""

from __future__ import annotations

import struct

import pytest

from tools.sh2 import disasm
from tools.text import names_switch as ns

WORDS = {
    "menu": {
        "entry": "EXTRA OPTIONS",
        "title": "EXTRA OPTIONS",
        "row": "NAMES",
        "values": ["ENGLISH", "JAPANESE"],
    }
}


def put16(buf: bytearray, base: int, address: int, value: int) -> None:
    struct.pack_into(">H", buf, address - base, value)


def put32(buf: bytearray, base: int, address: int, value: int) -> None:
    struct.pack_into(">I", buf, address - base, value)


def originals() -> dict[str, bytes]:
    cyber = bytearray(0x50E70)
    put32(cyber, ns.CYBER_BASE, 0x06038DA0, 0x06060000)
    put32(cyber, ns.CYBER_BASE, 0x06038DC0, 0x06046398)
    put16(cyber, ns.CYBER_BASE, 0x06038CD6, 0xBC63)
    opdemo = bytearray(0xBE88)
    for i, address in enumerate(ns.ROWS):
        put16(opdemo, ns.OVERLAY_BASE, address, 0xE508 + 2 * (i % 8))
    put16(opdemo, ns.OVERLAY_BASE, ns.TITLE_ROW[0], ns.TITLE_ROW[1])
    put32(opdemo, ns.OVERLAY_BASE, 0x06062470, 0x0602A766)
    put32(opdemo, ns.OVERLAY_BASE, 0x06062B3C, 0x06063FD0)
    put16(opdemo, ns.OVERLAY_BASE, 0x060627E6, 0xA14A)
    for address, (old, _new) in ns.WRAP.items():
        put16(opdemo, ns.OVERLAY_BASE, address, old)
    stg = bytearray(0x1000)
    put32(stg, ns.OVERLAY_BASE, 0x060606C0, 0x06038E9C)
    stg0a = bytes(range(256)) * 0x200
    return {
        "CYBER.BIN": bytes(cyber),
        "OPDEMO.BIN": bytes(opdemo),
        "STG0AS.BIN": bytes(stg),
        "STG0A.BIN": stg0a,
        "SELECT.VAD": bytes(0x1A000),
        "PL3F_0.BIN": bytes(0xA000),
    }


def test_code_fits_the_free_range_and_hooks_are_wired() -> None:
    built = ns.build(originals(), WORDS)
    start, end = built.code_range
    assert start == ns.FREE[0] and end <= ns.FREE[1] and end % 4 == 0
    cy = built.files["CYBER.BIN"]

    def long_at(address: int) -> int:
        return int(struct.unpack_from(">I", cy, address - ns.CYBER_BASE)[0])

    assert long_at(0x06038DA0) == built.labels["hookC"]
    assert long_at(0x06038DC0) == built.labels["hookA"]
    _, text = disasm.decode(cy, ns.CYBER_BASE, 0x06038CD6)
    assert text.startswith("jsr @r4")
    _o, old, new = built.stg0as
    assert old == struct.pack(">I", 0x06038E9C)
    assert new == struct.pack(">I", built.labels["hookB"])


def test_hook_c_copies_the_part_table_and_jumps_to_init() -> None:
    src = originals()
    built = ns.build(src, WORDS)
    cy = built.files["CYBER.BIN"]
    parts = src["STG0A.BIN"][ns.PARTS_RANGE[0] : ns.PARTS_RANGE[1]]
    assert len(parts) == 124
    assert parts in cy[built.labels["parts"] - ns.CYBER_BASE :]
    texts = [
        disasm.decode(cy, ns.CYBER_BASE, pc)[1]
        for pc in range(built.labels["hookC"], built.labels["hookC"] + 0x20, 2)
    ]
    assert any(t.startswith("jmp @r2") for t in texts)


def test_rows_move_up_two_and_the_title_to_row_two() -> None:
    src = originals()
    built = ns.build(src, WORDS)
    op = built.files["OPDEMO.BIN"]
    for address in ns.ROWS:
        o = address - ns.OVERLAY_BASE
        before = struct.unpack_from(">H", src["OPDEMO.BIN"], o)[0]
        after = struct.unpack_from(">H", op, o)[0]
        assert after == before - 2
    o = ns.TITLE_ROW[0] - ns.OVERLAY_BASE
    assert struct.unpack_from(">H", op, o)[0] == 0xE502


def test_strings_are_the_approved_words() -> None:
    built = ns.build(originals(), WORDS)
    cy = built.files["CYBER.BIN"]
    for name, text in (
        ("S_extra", b"EXTRA OPTIONS\0"),
        ("S_names", b"NAMES\0"),
        ("S_eng", b"ENGLISH\0"),
        ("S_jpn", b"JAPANESE\0"),
    ):
        o = built.labels[name] - ns.CYBER_BASE
        assert cy[o : o + len(text)] == text


def test_tail_files_are_the_untouched_ranges() -> None:
    src = originals()
    built = ns.build(src, WORDS)
    names = [name for name, _ in built.tail]
    assert names == ["ZNAMES1.BIN;1", "ZNAMES2.BIN;1"]
    assert len(built.tail[0][1]) == 8640 and len(built.tail[1][1]) == 38700


def test_refuses_unexpected_originals() -> None:
    src = originals()
    bad = bytearray(src["OPDEMO.BIN"])
    put16(bad, ns.OVERLAY_BASE, 0x060627E6, 0x0009)
    with pytest.raises(ValueError):
        ns.build({**src, "OPDEMO.BIN": bytes(bad)}, WORDS)
    cyber = bytearray(src["CYBER.BIN"])
    cyber[ns.FREE[0] - ns.CYBER_BASE] = 1
    with pytest.raises(ValueError):
        ns.build({**src, "CYBER.BIN": bytes(cyber)}, WORDS)


def test_patch_stg0as_checks_the_built_file() -> None:
    src = originals()
    built = ns.build(src, WORDS)
    patched = ns.patch_stg0as(src["STG0AS.BIN"], built)
    o, _old, new = built.stg0as
    assert patched[o : o + 4] == new and len(patched) == len(src["STG0AS.BIN"])
    with pytest.raises(ValueError):
        ns.patch_stg0as(patched, built)


def test_title_and_entry_must_match() -> None:
    words = {"menu": {**WORDS["menu"], "title": "OTHER"}}
    with pytest.raises(ValueError):
        ns.build(originals(), words)
