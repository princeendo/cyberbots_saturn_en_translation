"""English boot-warning pictures, `WARNING0.PIX`-`WARNING4.PIX` (`BOOT-004`).

The approved text and style are in ``data/translations/boot_warnings.json``
(`BOOT-003`, `EXP-0053`). The format is D-049's:

- each file is a VDP2 bitmap, 512 bytes a row, one byte a pixel, values
  0-15, no header; 122,880 bytes (``WARNING4``: 131,072);
- the screen shows file columns 0-351 and rows 0-223, with the 16 colours
  of `CYBER.BIN`'s table at ``0x06053AAC`` (value 0 transparent);
- the Japanese background is value 15.

A picture is the untouched file with its visible 352 x 224 pixels redrawn:
the title and lines are drawn in the arcade dialogue letters
(``arcade_font.json``, `EXP-0025`, not narrowed) at an 8-pixel advance, each
line centred, the body centred vertically below the title. Body text is
white, the title yellow, ``{...}`` cyan and ``[...]`` red, each as a ramp
of the table for the arcade's four letter shades; shadows are value 1.
Bytes outside the visible area are kept, so nothing hidden changes.

Promoted from ``research/experiments/EXP-0053/render.py`` (same layout and
colours; its approved renders are reproduced exactly).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

WIDTH = 512  # bytes a row in the file
SHOWN_W, SHOWN_H = 352, 224  # visible pixels (D-049)
BACKGROUND, SHADOW = 15, 1
ADVANCE, LINE_PITCH, TITLE_TOP = 8, 18, 16
MARGIN_X, MARGIN_BOTTOM = 16, 8
SIZES = {
    "WARNING0.PIX": 122880,
    "WARNING1.PIX": 122880,
    "WARNING2.PIX": 122880,
    "WARNING3.PIX": 122880,
    "WARNING4.PIX": 131072,
}
RAMPS = {
    "white": (7, 6, 5, 4),
    "yellow": (12, 12, 11, 10),
    "cyan": (14, 14, 13, 13),
    "red": (9, 9, 8, 8),
}
ARCADE_SHADES: dict[str, int | str] = {
    "ffffff": 0,
    "dddddd": 1,
    "aaaaaa": 2,
    "555555": 3,
    "111111": "shadow",
}
CYBER_BASE, PALETTE_ADDRESS = 0x0600D000, 0x06053AAC

Pixel = tuple[int, int, int | str]  # (x, y, shade index or "shadow")
Font = dict[str, list[Pixel]]
Canvas = list[list[int]]


class FitError(ValueError):
    """The text does not fit the visible area, or a character is missing."""


@dataclass
class Picture:
    name: str
    data: bytes
    canvas: Canvas
    fit: dict[str, Any]


def load_font(path: Path) -> Font:
    """The arcade letters of ``arcade_font.json`` as shaded pixels."""
    font = json.loads(path.read_text())
    colours = font["palette"]
    out: Font = {}
    for code in sorted(font["glyphs"], key=lambda c: int(c, 16)):
        entry = font["glyphs"][code]
        ch = entry["char"]
        if not ch or (ch in out and not (ch == "." and code == "14")):
            continue
        pixels: list[Pixel] = []
        for y, row in enumerate(entry["rows"]):
            for x, v in enumerate(row):
                shade = ARCADE_SHADES.get(colours[v])
                if shade is not None:
                    pixels.append((x + entry["left"], y, shade))
        out[ch] = pixels
    return out


def palette(cyber: bytes) -> list[tuple[int, int, int]]:
    """The 16 colours as Mednafen's screenshots show them (``c << 3``)."""
    off = PALETTE_ADDRESS - CYBER_BASE
    out = []
    for i in range(16):
        c = int.from_bytes(cyber[off + 2 * i : off + 2 * i + 2], "big")
        out.append(((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3))
    return out


def spans(line: str) -> list[tuple[str, str]]:
    """Split a line into (text, colour) by ``{cyan}`` and ``[red]`` marks."""
    out, colour, buf = [], "white", ""
    for ch in line:
        if ch in "{[":
            if colour != "white":
                raise FitError(f"nested mark in {line!r}")
            out.append((buf, colour))
            buf, colour = "", "cyan" if ch == "{" else "red"
        elif ch in "}]":
            if colour == "white":
                raise FitError(f"unopened mark in {line!r}")
            out.append((buf, colour))
            buf, colour = "", "white"
        else:
            buf += ch
    if colour != "white":
        raise FitError(f"unclosed mark in {line!r}")
    out.append((buf, colour))
    return [s for s in out if s[0]]


def plain(line: str) -> str:
    return "".join(t for t, _ in spans(line))


def _draw(canvas: Canvas, font: Font, text: str, x: int, y: int, colour: str) -> int:
    ramp = RAMPS[colour]
    for ch in text:
        if ch != " ":
            if ch not in font:
                raise FitError(f"no glyph for {ch!r}")
            for gx, gy, shade in font[ch]:
                px, py = x + gx, y + gy
                if not (0 <= px < SHOWN_W and 0 <= py < SHOWN_H):
                    raise FitError(f"{ch!r} at ({px}, {py}) is outside the screen")
                if shade == "shadow":
                    if canvas[py][px] == BACKGROUND:
                        canvas[py][px] = SHADOW
                else:
                    assert isinstance(shade, int)
                    canvas[py][px] = ramp[shade]
        x += ADVANCE
    return x


def layout(
    title: str, lines: Sequence[str], font: Font
) -> tuple[Canvas, dict[str, Any]]:
    """Draw one screen; raise ``FitError`` if anything leaves the room."""
    canvas = [[BACKGROUND] * SHOWN_W for _ in range(SHOWN_H)]
    y = TITLE_TOP
    _draw(canvas, font, title, (SHOWN_W - ADVANCE * len(title)) // 2, y, "yellow")
    y += LINE_PITCH + LINE_PITCH // 2
    body = sum(LINE_PITCH if line else LINE_PITCH // 2 for line in lines)
    y = max(y, y + (SHOWN_H - MARGIN_BOTTOM - y - body) // 2)
    widest = 0
    for line in lines:
        if not line:
            y += LINE_PITCH // 2
            continue
        width = ADVANCE * len(plain(line))
        if width > SHOWN_W - 2 * MARGIN_X:
            raise FitError(f"{line!r} is {width} pixels wide")
        widest = max(widest, width)
        x = (SHOWN_W - width) // 2
        for text, colour in spans(line):
            x = _draw(canvas, font, text, x, y, colour)
        y += LINE_PITCH
    if y > SHOWN_H - MARGIN_BOTTOM:
        raise FitError(f"text ends at row {y}")
    used = [r for r in range(SHOWN_H) if any(v != BACKGROUND for v in canvas[r])]
    return canvas, {
        "lines": sum(1 for line in lines if line),
        "widest_line_px": widest,
        "first_row_used": min(used),
        "last_row_used": max(used),
    }


def picture(name: str, original: bytes, canvas: Canvas) -> bytes:
    """The original file with its visible pixels replaced; checked."""
    if SIZES.get(name) != len(original):
        raise ValueError(f"{name}: {len(original)} bytes, expected {SIZES.get(name)}")
    out = bytearray(original)
    for y in range(SHOWN_H):
        out[y * WIDTH : y * WIDTH + SHOWN_W] = bytes(canvas[y])
    check(name, original, bytes(out))
    return bytes(out)


def check(name: str, original: bytes, data: bytes) -> None:
    """D-049's format: size kept, values 0-15, hidden bytes unchanged."""
    if len(data) != len(original):
        raise ValueError(f"{name}: size changed")
    if max(data) > 15:
        raise ValueError(f"{name}: a value above 15")
    for i in range(len(data)):
        row, col = divmod(i, WIDTH)
        if (row >= SHOWN_H or col >= SHOWN_W) and data[i] != original[i]:
            raise ValueError(f"{name}: hidden byte {i} changed")


def build(
    approved: Mapping[str, Any], font: Font, originals: Mapping[str, bytes]
) -> tuple[dict[str, Picture], list[dict[str, Any]]]:
    """All pictures of the approved file, and their change records."""
    pictures: dict[str, Picture] = {}
    changes: list[dict[str, Any]] = []
    for name, screen in approved["screens"].items():
        canvas, fit = layout(approved["title"], screen["lines"], font)
        original = originals[name]
        data = picture(name, original, canvas)
        pictures[name] = Picture(name, data, canvas, fit)
        changes.append(
            {
                "file": name,
                "start": 0,
                "end": SHOWN_H * WIDTH,
                "what": "boot warning: columns 0-351 of rows 0-223 redrawn (BOOT-004)",
                "bytes_changed": sum(
                    a != b for a, b in zip(original, data, strict=True)
                ),
                "original_sha256": hashlib.sha256(original).hexdigest(),
                "new_sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return pictures, changes


def rgb(canvas: Canvas, colours: Sequence[tuple[int, int, int]]) -> bytes:
    """The visible pixels as the screen shows them (value 0 black)."""
    return bytes(
        v
        for row in canvas
        for value in row
        for v in (colours[value] if value else (0, 0, 0))
    )
