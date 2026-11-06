"""Latin name art for the pilot select and VS screens (`LOC-005`).

Builds the approved names (``data/translations/name_art.json``, `LOC-004`)
into three files, from their untouched copies:

- **Pilot select** (bank 56, D-051/D-052): `SELECT.VAD`'s name block
  (``0x17840``) becomes nine 120 x 16 slots, one per pilot. In `STG0A.BIN`'s
  part table each name frame's first part takes Santana's part words (one
  120 x 16 part, both flips) pointing at its slot; its other parts get size 0,
  which the sprite-part routine skips.
- **VS screen** (bank 63): `PL3F_0.BIN`'s name records (``0x42EC`` to
  ``0x97BC``) are packed again, type-2 compressed (``tools.text.pattern_t2``):
  a blank 8 x 1 record, one record per pilot (Santana's part words), two per
  mech (Blodia's two parts), and frame ``0x0B``'s records copied unchanged.
  The part entries at the start of `PL3F_0.BIN` are pointed at them; parts a
  frame no longer needs point at the blank record. Bank 63's frame table is
  read from `STG0AS.BIN` (``0x1B49C``; loaded at ``0x06060000`` on the VS
  screen).

Part geometry (``EXP-0060``): screen x = 80 + (word 0 >> 6), y = origin +
(word 1 >> 6), both signed; flips = (word 1 >> 2) & 3 (bit 0 horizontal,
bit 1 vertical); word 1 bit 1 marks a frame's last part (the routine stops
there); the pattern index = (word 1 bit 0) << 16 | word 2, in 4-byte units.

Banners are drawn as displayed (letters ``tools.text.boot_warnings`` load
from the arcade font, plus ``&`` and ``·``; the bar rows 3-11), then each
part's slice is flipped back to how it is stored. Each mech keeps its
model code: the code-coloured pixels (indices 8-12) of the original frame,
moved to just after the name.
"""

from __future__ import annotations

import hashlib
import json
import struct
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.text import boot_warnings, pattern_t2

HEIGHT = 16
RAMP, SHADOW, BAR = (15, 1, 2, 3), 5, 6
CODE = (8, 9, 10, 11, 12)
LAST_PART = 0x0002  # word 1 bit 1 ends a frame's part list (EXP-0060)

# Select screen (bank 56): STG0A.BIN tables, SELECT.VAD block.
SEL_FRAMES = range(0x14, 0x1D)
SEL_FRAME_TABLE, SEL_PARTS, SEL_PART_SIZE = 0x1C230, 0x1C35A, 8
SEL_BLOCK, SEL_BLOCK_END, SEL_SLOT = 0x17840, 0x19B20, 960
SEL_TEMPLATE = (0xF09D, 0xFC4E, 0x0F10)  # Santana's part: w0, w1, w3

# VS screen (bank 63): STG0AS.BIN frame table, PL3F_0.BIN parts and records.
VS_PILOTS = range(0x02, 0x0B)
VS_MECHS = range(0x0C, 0x1C)
VS_KEEP = (0x0B,)  # the "G.O.D." banner: records copied, parts re-pointed
VS_FRAME_TABLE, VS_FRAMES, VS_PART_SIZE = 0x1B49C, 122, 6
VS_REGION, VS_REGION_END = 0x42EC, 0x97BC
VS_PILOT_TEMPLATE = (0xF09D, 0xFC4E)
VS_MECH_TEMPLATE = ((0xEE1C, 0xFC42), (0x001C, 0xFC4C))  # left (x 8), right (x 80)

Grid = list[list[int]]


class NameArtError(ValueError):
    pass


@dataclass
class Built:
    files: dict[str, bytes]
    changes: list[dict[str, Any]]
    report: dict[str, Any]


def word(blob: bytes, offset: int) -> int:
    return int(struct.unpack_from(">H", blob, offset)[0])


def s16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def load_font(path: Path) -> boot_warnings.Font:
    font = boot_warnings.load_font(path)
    font["·"] = [(x, y - 5, s) for x, y, s in font["."]]
    amp = [" XX    ", "X  X   ", "X  X   ", " XX  X ", "X  XX  ", "X   X  ", " XXX X "]
    glyph: list[boot_warnings.Pixel] = []
    for r, line in enumerate(amp):
        for c, ch in enumerate(line):
            if ch == "X":
                for y in (2 + 2 * r, 3 + 2 * r):
                    glyph.append((c, y, 0))
                    glyph.append((c + 1, y, "shadow"))
    font["&"] = glyph
    return font


def banner(width: int) -> Grid:
    grid = [[0] * width for _ in range(HEIGHT)]
    for y in range(3, 12):
        for x in range(max(0, 11 - y), width - (y - 3)):
            grid[y][x] = BAR
    return grid


def letters(grid: Grid, font: boot_warnings.Font, text: str, x: int) -> int:
    width = len(grid[0])
    for ch in text:
        if ch != " ":
            if ch not in font:
                raise NameArtError(f"no letter for {ch!r}")
            for gx, gy, shade in font[ch]:
                px = x + gx
                if not (0 <= px < width and 0 <= gy < HEIGHT):
                    raise NameArtError(f"{text!r} leaves its banner")
                if shade == "shadow":
                    if grid[gy][px] in (0, BAR):
                        grid[gy][px] = SHADOW
                else:
                    assert isinstance(shade, int)
                    grid[gy][px] = RAMP[shade]
        x += 8
    return x


def stored(grid: Grid, flips: int) -> Grid:
    """A displayed slice as the pattern stores it (undo the part's flips)."""
    out = [list(row) for row in grid]
    if flips & 2:
        out = out[::-1]
    if flips & 1:
        out = [row[::-1] for row in out]
    return out


def displayed(grid: Grid, flips: int) -> Grid:
    return stored(grid, flips)  # flips are their own inverse


def pack(grid: Grid) -> bytes:
    out = bytearray()
    for row in grid:
        if len(row) % 2:
            raise NameArtError("odd width")
        for x in range(0, len(row), 2):
            out.append((row[x] << 4) | row[x + 1])
    return bytes(out)


def unpack(data: bytes, width: int, height: int) -> Grid:
    return [
        [
            (data[(y * width + x) // 2] >> (4 if x % 2 == 0 else 0)) & 15
            for x in range(width)
        ]
        for y in range(height)
    ]


def frame_parts(table: bytes, table_offset: int, frames: int, frame: int) -> range:
    first = word(table, table_offset + 2 * (frame - 1))
    last = word(table, table_offset + 2 * frame) if frame < frames else first + 1
    return range(first, last)


def build_select(
    names: Sequence[str], font: boot_warnings.Font, vad: bytes, stg0a: bytes
) -> tuple[bytes, bytes, list[dict[str, Any]], dict[str, Any]]:
    vad_out, stg_out = bytearray(vad), bytearray(stg0a)
    if word(stg0a, SEL_PARTS + SEL_PART_SIZE * 218) != SEL_TEMPLATE[0]:
        raise NameArtError("STG0A.BIN is not the expected version")
    if len(names) * SEL_SLOT > SEL_BLOCK_END - SEL_BLOCK:
        raise NameArtError("select block too small")
    widths = {}
    for k, (name, frame) in enumerate(zip(names, SEL_FRAMES, strict=True)):
        grid = banner(120)
        width = 8 * len(name)
        letters(grid, font, name, (120 - width) // 2)
        widths[name] = width
        slot = SEL_BLOCK + SEL_SLOT * k
        vad_out[slot : slot + SEL_SLOT] = pack(stored(grid, 3))
        index = slot // 4
        parts = frame_parts(stg0a, SEL_FRAME_TABLE, 149, frame)
        for n, p in enumerate(parts):
            at = SEL_PARTS + SEL_PART_SIZE * p
            if n == 0:
                w0, w1, w3 = SEL_TEMPLATE
                struct.pack_into(
                    ">4H",
                    stg_out,
                    at,
                    w0,
                    (w1 & ~1) | (index >> 16),
                    index & 0xFFFF,
                    w3,
                )
            else:
                struct.pack_into(">H", stg_out, at + 6, 0)
    changes = [
        {
            "file": "SELECT.VAD",
            "start": SEL_BLOCK,
            "end": SEL_BLOCK + SEL_SLOT * len(names),
            "what": "pilot select names: one 120 x 16 slot each (LOC-005)",
        },
        {
            "file": "STG0A.BIN",
            "start": SEL_PARTS
            + SEL_PART_SIZE
            * frame_parts(stg0a, SEL_FRAME_TABLE, 149, SEL_FRAMES[0])[0],
            "end": SEL_PARTS
            + SEL_PART_SIZE
            * frame_parts(stg0a, SEL_FRAME_TABLE, 149, SEL_FRAMES[-1])[-1]
            + SEL_PART_SIZE,
            "what": "pilot select name frames' parts (bank 56)",
        },
    ]
    return bytes(vad_out), bytes(stg_out), changes, {"text_widths_px": widths}


def compose(
    pl: bytes, frames_table: bytes, frame: int, origin_y: int
) -> tuple[Grid, int]:
    """A frame's original art as displayed, and its left screen x."""
    parts = []
    for p in frame_parts(frames_table, VS_FRAME_TABLE, VS_FRAMES, frame):
        w0, w1, w2 = (word(pl, VS_PART_SIZE * p + 2 * i) for i in range(3))
        offset = (((w1 & 1) << 16) | w2) * 4
        width, height = pattern_t2.size_of(pl[offset : offset + 2])
        grid = displayed(
            unpack(pattern_t2.decode(pl[offset:]), width, height), (w1 >> 2) & 3
        )
        parts.append((80 + (s16(w0) >> 6), (s16(w1) >> 6) + origin_y, grid))
    left = min(x for x, _, _ in parts)
    right = max(x + len(g[0]) for x, _, g in parts)
    out = [[0] * (right - left) for _ in range(HEIGHT)]
    for x, y, grid in parts:
        for gy, row in enumerate(grid):
            for gx, v in enumerate(row):
                if v and 0 <= y + gy < HEIGHT:
                    out[y + gy][x - left + gx] = v
    return out, left


def code_of(grid: Grid) -> Grid:
    """The model code's pixels, cropped to their box (0 elsewhere)."""
    cells = [
        (x, y) for y, row in enumerate(grid) for x, v in enumerate(row) if v in CODE
    ]
    if not cells:
        raise NameArtError("no model code found")
    x0, x1 = min(c[0] for c in cells), max(c[0] for c in cells)
    y0, y1 = min(c[1] for c in cells), max(c[1] for c in cells)
    return [
        [grid[y][x] if grid[y][x] in CODE and y >= y0 else 0 for x in range(x0, x1 + 1)]
        for y in range(0, y1 + 1)
    ]


def build_vs(
    pilots: Sequence[str],
    mechs: Sequence[tuple[str, str]],
    font: boot_warnings.Font,
    pl: bytes,
    stg0as: bytes,
) -> tuple[bytes, list[dict[str, Any]], dict[str, Any]]:
    out = bytearray(pl)
    blank = pattern_t2.encode(bytes(4), 8, 1)
    records: list[bytes] = [blank]
    placement: dict[int, list[int]] = {}  # frame -> record numbers, one per kept part
    report: dict[str, Any] = {"mechs": {}}
    for name, frame in zip(pilots, VS_PILOTS, strict=True):
        grid = banner(120)
        letters(grid, font, name, (120 - 8 * len(name)) // 2)
        records.append(pattern_t2.encode(pack(stored(grid, 3)), 120, HEIGHT))
        placement[frame] = [len(records) - 1]
    for (name, code_text), frame in zip(mechs, VS_MECHS, strict=True):
        original, _left = compose(pl, stg0as, frame, 15)
        code = code_of(original)
        width = 8 * len(name) + 3 + len(code[0])
        if width > 144:
            raise NameArtError(f"{name} {code_text} is {width} pixels wide")
        grid = banner(144)
        x = letters(grid, font, name, (144 - width) // 2) + 3
        for y, row in enumerate(code):
            for cx, v in enumerate(row):
                if v:
                    grid[y][x + cx] = v
        left_half = [row[:72] for row in grid]
        right_half = [row[72:] for row in grid]
        records.append(pattern_t2.encode(pack(stored(left_half, 0)), 72, HEIGHT))
        records.append(pattern_t2.encode(pack(stored(right_half, 3)), 72, HEIGHT))
        placement[frame] = [len(records) - 2, len(records) - 1]
        report["mechs"][name] = {"code_width_px": len(code[0]), "banner_px": width}
    # Records of the kept frames, copied unchanged.
    all_offsets = sorted(
        {
            (
                ((word(pl, VS_PART_SIZE * p + 2) & 1) << 16)
                | word(pl, VS_PART_SIZE * p + 4)
            )
            * 4
            for f in range(1, VS_FRAMES + 1)
            for p in frame_parts(stg0as, VS_FRAME_TABLE, VS_FRAMES, f)
        }
    )
    sizes = pattern_t2.records_of(pl, all_offsets)
    kept: dict[int, int] = {}
    for frame in VS_KEEP:
        for p in frame_parts(stg0as, VS_FRAME_TABLE, VS_FRAMES, frame):
            offset = (
                ((word(pl, VS_PART_SIZE * p + 2) & 1) << 16)
                | word(pl, VS_PART_SIZE * p + 4)
            ) * 4
            if offset not in kept:
                records.append(sizes[offset])
                kept[offset] = len(records) - 1
    # Lay the records out.
    position = VS_REGION
    at: list[int] = []
    for rec in records:
        at.append(position)
        position += len(rec) + (-len(rec) % 4)
    if position > VS_REGION_END:
        need, room = position - VS_REGION, VS_REGION_END - VS_REGION
        raise NameArtError(f"VS records need {need} of {room} bytes")
    out[VS_REGION:VS_REGION_END] = bytes(VS_REGION_END - VS_REGION)
    for start, rec in zip(at, records, strict=True):
        out[start : start + len(rec)] = rec

    def point(
        p: int, record_number: int, template: tuple[int, int] | None, last: bool
    ) -> None:
        index = at[record_number] // 4
        w0, w1 = word(pl, VS_PART_SIZE * p), word(pl, VS_PART_SIZE * p + 2)
        if template:
            w0, w1 = template
        w1 = (w1 & ~LAST_PART) | (LAST_PART if last else 0)
        struct.pack_into(
            ">3H", out, VS_PART_SIZE * p, w0, (w1 & ~1) | (index >> 16), index & 0xFFFF
        )

    first_part = last_part = None
    for frame in [*VS_PILOTS, *VS_MECHS]:
        parts = list(frame_parts(stg0as, VS_FRAME_TABLE, VS_FRAMES, frame))
        first_part = parts[0] if first_part is None else min(first_part, parts[0])
        last_part = parts[-1] if last_part is None else max(last_part, parts[-1])
        templates: list[tuple[int, int]] = (
            [VS_PILOT_TEMPLATE] if frame in VS_PILOTS else list(VS_MECH_TEMPLATE)
        )
        for n, p in enumerate(parts):
            if n < len(placement[frame]):
                point(p, placement[frame][n], templates[n], n == len(parts) - 1)
            else:
                point(p, 0, None, n == len(parts) - 1)
    for frame in VS_KEEP:
        for p in frame_parts(stg0as, VS_FRAME_TABLE, VS_FRAMES, frame):
            offset = (
                ((word(pl, VS_PART_SIZE * p + 2) & 1) << 16)
                | word(pl, VS_PART_SIZE * p + 4)
            ) * 4
            point(
                p, kept[offset], None, bool(word(pl, VS_PART_SIZE * p + 2) & LAST_PART)
            )
    assert first_part is not None and last_part is not None
    report["records_bytes"] = position - VS_REGION
    report["region_bytes"] = VS_REGION_END - VS_REGION
    changes = [
        {
            "file": "PL3F_0.BIN",
            "start": VS_REGION,
            "end": VS_REGION_END,
            "what": "VS name records packed again (LOC-005)",
        },
        {
            "file": "PL3F_0.BIN",
            "start": VS_PART_SIZE * first_part,
            "end": VS_PART_SIZE * (last_part + 1),
            "what": "VS name frames' parts (bank 63), and frame 0x0B's",
        },
    ]
    return bytes(out), changes, report


def build(
    approved: Mapping[str, Any],
    font: boot_warnings.Font,
    originals: Mapping[str, bytes],
) -> Built:
    pilots = approved["pilots"]["names"]
    mechs = [tuple(m) for m in approved["mechs"]["names"]]
    vad, stg0a, sel_changes, sel_report = build_select(
        pilots, font, originals["SELECT.VAD"], originals["STG0A.BIN"]
    )
    pl, vs_changes, vs_report = build_vs(
        pilots, mechs, font, originals["PL3F_0.BIN"], originals["STG0AS.BIN"]
    )
    files = {"SELECT.VAD": vad, "STG0A.BIN": stg0a, "PL3F_0.BIN": pl}
    changes = sel_changes + vs_changes
    for c in changes:
        original, new = originals[c["file"]], files[c["file"]]
        c["original_sha256"] = hashlib.sha256(
            original[c["start"] : c["end"]]
        ).hexdigest()
        c["new_sha256"] = hashlib.sha256(new[c["start"] : c["end"]]).hexdigest()
    for name, data in files.items():
        original = originals[name]
        if len(data) != len(original):
            raise NameArtError(f"{name} changed size")
        for i in range(len(data)):
            if data[i] != original[i] and not any(
                c["file"] == name and c["start"] <= i < c["end"] for c in changes
            ):
                raise NameArtError(f"{name} byte {i:#x} changed outside the ranges")
    return Built(files, changes, {"select": sel_report, "vs": vs_report})


def load_approved(path: Path) -> dict[str, Any]:
    return dict(json.loads(path.read_text()))
