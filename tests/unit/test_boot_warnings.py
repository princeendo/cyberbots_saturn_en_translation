"""Tests for tools.text.boot_warnings (synthetic font and files only)."""

from __future__ import annotations

import pytest

from tools.text import boot_warnings as bw

# A 6 x 6 block letter for every character used, with a shadow column.
FONT: bw.Font = {
    ch: [(x, y, 0) for x in range(6) for y in range(2, 8)]
    + [(6, y, "shadow") for y in range(2, 8)]
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,'"
}


def original(name: str) -> bytes:
    size = bw.SIZES[name]
    return bytes((i * 7) % 16 for i in range(size))


def test_spans_marks() -> None:
    assert bw.spans("a {b} [c] d") == [
        ("a ", "white"),
        ("b", "cyan"),
        (" ", "white"),
        ("c", "red"),
        (" d", "white"),
    ]
    assert bw.plain("a {b} [c]") == "a b c"
    for bad in ("{a", "a}", "{a [b]}"):
        with pytest.raises(bw.FitError):
            bw.spans(bad)


def test_layout_centres_and_colours() -> None:
    canvas, fit = bw.layout("AB", ["Hello", "", "{Cy} [R]"], FONT)
    assert len(canvas) == bw.SHOWN_H and len(canvas[0]) == bw.SHOWN_W
    assert fit["lines"] == 2 and fit["widest_line_px"] == 40
    title_row = canvas[bw.TITLE_TOP + 4]
    assert title_row[(bw.SHOWN_W - 16) // 2] == bw.RAMPS["yellow"][0]
    values = {v for row in canvas for v in row}
    assert {bw.RAMPS["cyan"][0], bw.RAMPS["red"][0], bw.RAMPS["white"][0]} <= values
    assert bw.SHADOW in values and bw.BACKGROUND in values
    assert 0 not in values


def test_layout_refuses_overflow_and_missing() -> None:
    with pytest.raises(bw.FitError):
        bw.layout("A", ["A" * 41], FONT)
    with pytest.raises(bw.FitError):
        bw.layout("A", ["A"] * 13, FONT)
    with pytest.raises(bw.FitError):
        bw.layout("A", ["A ~"], FONT)


def test_picture_keeps_hidden_bytes() -> None:
    canvas, _ = bw.layout("A", ["B"], FONT)
    for name in ("WARNING0.PIX", "WARNING4.PIX"):
        src = original(name)
        out = bw.picture(name, src, canvas)
        assert len(out) == len(src)
        assert out[bw.SHOWN_W : bw.WIDTH] == src[bw.SHOWN_W : bw.WIDTH]
        assert out[bw.SHOWN_H * bw.WIDTH :] == src[bw.SHOWN_H * bw.WIDTH :]
        assert out[: bw.SHOWN_W] == bytes(canvas[0])


def test_picture_checks() -> None:
    canvas, _ = bw.layout("A", ["B"], FONT)
    with pytest.raises(ValueError):
        bw.picture("WARNING0.PIX", bytes(100), canvas)
    src = original("WARNING1.PIX")
    bad = bytearray(src)
    bad[bw.SHOWN_W] ^= 1
    with pytest.raises(ValueError):
        bw.check("WARNING1.PIX", src, bytes(bad))
    bad = bytearray(src)
    bad[0] = 16
    with pytest.raises(ValueError):
        bw.check("WARNING1.PIX", src, bytes(bad))


def test_build_records_changes() -> None:
    approved = {
        "title": "WARNING",
        "screens": {
            "WARNING0.PIX": {"lines": ["Press any button."]},
            "WARNING4.PIX": {"lines": ["Needs [6] blocks.", "{Memory Manager}"]},
        },
    }
    originals = {name: original(name) for name in approved["screens"]}
    pictures, changes = bw.build(approved, FONT, originals)
    assert set(pictures) == set(approved["screens"])
    assert [c["file"] for c in changes] == list(approved["screens"])
    assert all(c["end"] == bw.SHOWN_H * bw.WIDTH for c in changes)
    assert all(c["bytes_changed"] > 0 for c in changes)


def test_rgb_maps_zero_to_black() -> None:
    colours = [(255, 255, 255)] + [(i, i, i) for i in range(1, 16)]
    canvas = [[0, 15]]
    assert bw.rgb(canvas, colours) == bytes((0, 0, 0, 15, 15, 15))
