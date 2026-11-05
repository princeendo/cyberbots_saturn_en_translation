"""Compile an ending's dialogue into `END.BIN` and `SE.DAT`'s font (END-010).

Called by ``tools.text.dialogue`` with ``--ending PAIRING``. The policy is in
`docs/localization_policy.md` (gate GO for Jin's ending, 2026-11-05): the
official US arcade English as paired (D-038), unchanged, in pair glyphs.

Endings draw through `END.BIN`'s own copies (D-035, D-036):

- **Records:** `END.BIN`'s box table (``0x060817B4``; `END.BIN` loads at
  ``0x06060000``, so file offset = address - ``0x06060000``). Each box's
  entries are rewritten as in the story (``dialogue.record_entries``).
- **Codes:** `END.BIN`'s 1,222-code table (file ``0x26EAC``). Each distinct
  pair gets a code no line uses, then a new code in the table's last row.
  No Japanese code is sacrificed: the gate approved none, so the build stops
  if the codes run out.
- **Glyphs:** `SE.DAT`'s copy of `KANJI.BIN` (``0x40000``-``0x67FFF``), which
  VDP2 VRAM ``0x40000`` holds during the ending.
- **Room:** first the ending's own lines that no other posted box uses
  (every box that points to them is one of this ending's, or is never
  posted), in line order; then the lines no ending box shows
  (``data/text/ending_posts.json``), which `EXP-0042` showed are never read
  during an ending. A line a posted box outside this ending uses keeps its
  bytes.

Speaker names shared with other endings (boxes 605 and 601, lists 3, 4 and
8) are translated in place: the user's gate choice "Share, English
everywhere (Recommended)".
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.font import kanji, pairs
from tools.reference.cybots_text import decode, long, read_record
from tools.text import dialogue, ending_timing

BASE = 0x06060000
RECORDS = 0x060817B4
CODE_TABLE = 0x26EAC
FONT_START, FONT_END = 0x40000, 0x68000
BOXES = 1074
POSTS = Path("data/text/ending_posts.json")
SURFACES = Path("data/text/ending_surfaces.json")


# The QSound notice (D-035): `QSD.PIX`, a 512 x 256 bitmap of 256-colour
# pixels. Its Japanese trademark line is the only thing in rows 180-190,
# x 89-300 that is not the background index 255; x 84-88 is the logo's edge
# (EXP-0043). The user: "Erase the line (Recommended)" (END-005).
QSD_WIDTH = 512
QSD_ROWS = range(180, 191)
QSD_COLUMNS = range(89, 301)
QSD_BACKGROUND = 255


def erase_qsound_line(data: bytes) -> tuple[bytes, list[dict[str, object]]]:
    """`QSD.PIX` with the Japanese line set to the background, and the ranges."""
    out = bytearray(data)
    changes: list[dict[str, object]] = []
    for row in QSD_ROWS:
        start = row * QSD_WIDTH + QSD_COLUMNS.start
        stop = row * QSD_WIDTH + QSD_COLUMNS.stop
        if any(out[x] != QSD_BACKGROUND for x in range(start, stop)):
            out[start:stop] = bytes([QSD_BACKGROUND]) * (stop - start)
            changes.append(
                {"file": "QSD.PIX", "start": start, "end": stop, "what": f"row {row}"}
            )
    return bytes(out), changes


# The cast roll (EXP-0044). The main program's sprite-part routine
# (``0x060113F0``) draws bank 16, whose header is `KEND.BIN` + ``0xA704``
# (loaded at ``0x06060000``): +4 the frame table (16-bit part indexes), +8
# the 6-byte parts in `KEND_0.BIN` (loaded at ``0x00200000``). A part whose
# second word has bit ``0x20`` takes its pattern record from `KEND_1.BIN`
# (loaded at ``0x00280000``) at 4 x (bit 0 << 16 | third word); the record's
# first word is the size, and a part of width or height 0 is skipped
# (``0x0601157C``/``0x06011584``). Every ending's cast roll draws the ten
# Japanese names as the even frames ``0x1B6``-``0x1C8`` (16 records) and the
# Latin names as the odd frames. The user: "Hide, as US arcade
# (Recommended)" (END-005) and "Hide in every ending (Recommended)"
# (END-010, 2026-11-05).
CAST_BANK_HEADER = 0xA704
KEND_BASE, KEND_0_BASE = 0x06060000, 0x00200000
JAPANESE_NAME_FRAMES = range(0x1B6, 0x1C9, 2)
NAME_HEIGHTS = (10, 11)


def _u16(data: bytes, at: int) -> int:
    return int.from_bytes(data[at : at + 2], "big")


def cast_name_records(kend: bytes, kend0: bytes, kend1: bytes) -> list[int]:
    """`KEND_1.BIN` offsets of the Japanese cast-name pattern records."""
    header = CAST_BANK_HEADER
    frames = (int.from_bytes(kend[header + 4 : header + 8], "big") & 0x1FFFFFFF) - (
        KEND_BASE
    )
    parts = (int.from_bytes(kend[header + 8 : header + 12], "big") & 0x1FFFFFFF) - (
        KEND_0_BASE
    )
    records: list[int] = []
    for frame in JAPANESE_NAME_FRAMES:
        part = parts + 6 * _u16(kend, frames + 2 * (frame - 1))
        while True:
            second, third = _u16(kend0, part + 2), _u16(kend0, part + 4)
            if not second & 0x20:
                raise ValueError(f"frame 0x{frame:X}: part not in KEND_1.BIN")
            record = 4 * (((second & 1) << 16) | third)
            if _u16(kend1, record) & 0x7F not in NAME_HEIGHTS:
                raise ValueError(f"frame 0x{frame:X}: record 0x{record:X} not a name")
            if record not in records:
                records.append(record)
            if second & 2:
                break
            part += 6
    return records


def hide_cast_names(
    kend: bytes, kend0: bytes, kend1: bytes
) -> tuple[bytes, list[dict[str, object]]]:
    """`KEND_1.BIN` with each Japanese name's size word 0, and the ranges."""
    out = bytearray(kend1)
    changes: list[dict[str, object]] = []
    for record in cast_name_records(kend, kend0, kend1):
        out[record : record + 2] = bytes(2)
        changes.append(
            {
                "file": "KEND_1.BIN",
                "start": record,
                "end": record + 2,
                "what": "cast name size",
            }
        )
    return bytes(out), changes


@dataclass
class EndingBuild:
    end: bytearray
    se: bytearray
    images: dict[str, bytes] = field(default_factory=dict)
    changes: list[dict[str, object]] = field(default_factory=list)
    prediction: list[dict[str, object]] = field(default_factory=list)
    record: dict[str, Any] = field(default_factory=dict)
    timing: list[dict[str, Any]] = field(default_factory=list)


def end_lines() -> list[tuple[int, int]]:
    census = json.loads(dialogue.CENSUS.read_text())
    end = next(f for f in census["files"] if f["file"] == "END.BIN")
    return [(off, n) for off, n, _, _ in end["blocks"][0]["table"]]


def record_lines(end: bytes, lines: Sequence[tuple[int, int]]) -> dict[int, list[int]]:
    """Box -> the lines its record points to (pointers inside lines skipped)."""
    line_at = {BASE + off: n for n, (off, _) in enumerate(lines)}

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    out: dict[int, list[int]] = {}
    for box in range(BOXES):
        entry = u32(RECORDS + 4 * box) + 8
        found: list[int] = []
        while True:
            n = line_at.get(u32(entry))
            if n is not None:
                found.append(n)
            if end[entry + 4 - BASE : entry + 6 - BASE] != b"\xff\xff":
                break
            entry += 8
        out[box] = found
    return out


def free_lines(
    box_lines: Mapping[int, Sequence[int]], posted: set[int], ours: set[int]
) -> tuple[list[int], list[int]]:
    """(this ending's own free lines, lines no posted box shows), in line order.

    A line is free when every box pointing to it is one of ``ours`` or is
    never posted. It is "own" when one of ``ours`` points to it.
    """
    users: dict[int, set[int]] = {}
    for box, found in box_lines.items():
        for n in found:
            users.setdefault(n, set()).add(box)
    own, unshown = [], []
    for n in sorted(users):
        posted_users = users[n] & posted
        if posted_users - ours:
            continue
        if users[n] & ours:
            own.append(n)
        elif not posted_users:
            unshown.append(n)
    return own, unshown


def spans(lines: Sequence[tuple[int, int]], chosen: Sequence[int]) -> list[list[int]]:
    """Merged ``[start, end)`` file ranges of lines (NUL, 4-byte aligned)."""
    out: list[list[int]] = []
    for n in chosen:
        off, length = lines[n]
        span = [off, off + ((length + 1 + 3) & ~3)]
        if out and out[-1][1] == span[0]:
            out[-1][1] = span[1]
        else:
            out.append(span)
    return out


def compile_ending(
    pairing_path: Path,
    program: bytes,
    font: Mapping[str, Any],
    texts: Sequence[bytes],
    task: str,
    retime: bool = False,
) -> EndingBuild:
    pairing = json.loads(pairing_path.read_text())
    end, se = dialogue.checked("END.BIN"), dialogue.checked("SE.DAT")
    english = {}
    boxes: list[dialogue.Box] = []
    for unit in pairing["units"]:
        slot = unit.get("arcade_slot")
        if slot is None:
            continue
        record = read_record(program, long(program, dialogue.EN_TABLE + 4 * slot))
        english[slot] = record
        rows = dialogue.wrap(decode(record.codes))
        if (
            len(rows) > dialogue.MAX_ROWS
            or dialogue.cells_of(rows) > dialogue.MAX_CELLS
        ):
            raise SystemExit(f"ending box {unit['box']}: {len(rows)} rows")
        boxes.append(
            dialogue.Box(unit["box"], slot, tuple(unit["saturn_lines"]), tuple(rows))
        )

    lines = end_lines()
    box_lines = record_lines(bytes(end), lines)
    for b in boxes:
        if list(b.lines) != box_lines[b.box]:
            raise SystemExit(f"box {b.box}: pairing lines differ from END.BIN's record")
    posts = json.loads(POSTS.read_text())
    posted = {
        b["box"] for lst in posts["lists"] for p in lst["posts"] for b in p["boxes"]
    }
    ours = {b.box for b in boxes}
    own, unshown = free_lines(box_lines, posted, ours)
    room = spans(lines, own) + spans(lines, unshown)

    table = kanji.read_code_table(bytes(end), CODE_TABLE)
    unused = pairs.unused_codes(table, texts)
    last_row = kanji.TABLE_ROWS - 1
    last_row_used = len(table) - last_row * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1  # keep a 0 terminator
    wanted = dialogue.wanted_pairs(boxes)
    try:
        codes, new, _ = dialogue.allocate_codes(wanted, unused, new_slots, [], 0)
    except ValueError as error:
        raise dialogue.BudgetExceeded(
            f"ending: {error}; no sacrifice approved"
        ) from error

    build = EndingBuild(end, se)
    row_start = CODE_TABLE + last_row * kanji.TABLE_ROW_CODES * 2
    for k, code in enumerate(new):
        at = row_start + 2 * (last_row_used + k)
        end[at : at + 2] = code.to_bytes(2, "big")
    if new:
        first = row_start + 2 * last_row_used
        build.changes.append(
            {
                "file": "END.BIN",
                "start": first,
                "end": first + 2 * len(new),
                "what": "table codes",
            }
        )
    table = kanji.read_code_table(bytes(end), CODE_TABLE)
    cells = kanji.decode(bytes(se[FONT_START:FONT_END]))
    for pair, code in codes.items():
        cells[table.index(code)] = pairs.render_pair(font, pair)  # type: ignore[arg-type]
    se[FONT_START:FONT_END] = kanji.encode(cells)
    glyphs = sorted(table.index(c) for c in codes.values())
    for g in glyphs:
        for tile in kanji.tiles(g):
            at = FONT_START + tile * kanji.TILE_BYTES
            build.changes.append(
                {
                    "file": "SE.DAT",
                    "start": at,
                    "end": at + kanji.TILE_BYTES,
                    "what": f"glyph {g} tile",
                }
            )

    all_rows = [dialogue.row_bytes(r, codes) for b in boxes for r in b.rows]
    offsets = iter(dialogue.place(all_rows, [(s, e) for s, e in room]))
    data_rows = iter(all_rows)
    out_boxes = []
    placed: list[tuple[int, int]] = []
    for b in boxes:
        pointers = []
        for _ in b.rows:
            off, data = next(offsets), next(data_rows)
            end[off : off + len(data)] = data
            placed.append((off, len(data)))
            build.changes.append(
                {
                    "file": "END.BIN",
                    "start": off,
                    "end": off + len(data),
                    "what": f"box {b.box} row",
                }
            )
            pointers.append(BASE + off)
        rec = int.from_bytes(
            end[RECORDS - BASE + 4 * b.box : RECORDS - BASE + 4 * b.box + 4], "big"
        )
        entries = dialogue.record_entries(pointers)
        end[rec - BASE + 8 : rec - BASE + 32] = entries + bytes(24 - len(entries))
        build.changes.append(
            {
                "file": "END.BIN",
                "start": rec - BASE + 8,
                "end": rec - BASE + 32,
                "what": f"box {b.box} record",
            }
        )
        drawn = [
            cells[table.index(codes[p])]
            for r in b.rows
            for p in pairs.split_pairs(r)
            if p != "  "
        ]
        build.prediction.append(
            {"box": b.box, "cells": [hashlib.sha256(c).hexdigest() for c in drawn]}
        )
        en = english[b.slot]
        out_boxes.append(
            {
                "box": b.box,
                "slot": b.slot,
                "saturn_lines": list(b.lines),
                "english_record": f"0x{en.address:06X}",
                "english_sha256": hashlib.sha256(en.codes).hexdigest(),
                "rows": len(b.rows),
                "cells": len(drawn),
                "row_addresses": [f"0x{p:08X}" for p in pointers],
            }
        )
    # Image units (END-005 decisions, in the pairing's handling entries).
    decisions = {
        u["surface"]: u.get("handling", {}).get("decision")
        for u in pairing["units"]
        if u.get("no_official_english")
    }
    if decisions.get("cast roll name (image)") == "Hide, as US arcade (Recommended)":
        kend1, ranges = hide_cast_names(
            bytes(dialogue.checked("KEND.BIN")),
            bytes(dialogue.checked("KEND_0.BIN")),
            bytes(dialogue.checked("KEND_1.BIN")),
        )
        build.images["KEND_1.BIN"] = kend1
        build.changes += ranges
    if decisions.get("QSound notice (image)") == "Erase the line (Recommended)":
        qsd, ranges = erase_qsound_line(bytes(dialogue.checked("QSD.PIX")))
        build.images["QSD.PIX"] = qsd
        build.changes += ranges
    unhandled = {
        s: d
        for s, d in decisions.items()
        if s not in ("cast roll name (image)", "QSound notice (image)")
    }
    if unhandled:
        raise SystemExit(f"no handler for {unhandled}")

    if retime:  # END-011: faster typing and moved cues (ending_timing)
        surfaces = json.loads(SURFACES.read_text())["lists"][pairing["list"]]
        untouched = bytes(dialogue.checked("END.BIN"))
        jp_codes = set(kanji.read_code_table(untouched, CODE_TABLE)) - {
            dialogue.SPACE_CODE
        }
        jp_box_lines = record_lines(untouched, lines)
        japanese = {
            box: sum(
                1
                for k in jp_box_lines[box]
                for i in range(0, lines[k][1] - 1, 2)
                if int.from_bytes(
                    untouched[lines[k][0] + i : lines[k][0] + i + 2], "big"
                )
                in jp_codes
            )
            for box in range(BOXES)
            if jp_box_lines[box]
        }
        retimed = ending_timing.retime(
            end,
            pairing["list"],
            surfaces,
            {b.box: dialogue.cells_of(b.rows) for b in boxes},
            japanese,
        )
        build.changes += retimed.changes
        build.timing = retimed.boxes + retimed.waits

    used_room = sum(len(r) for r in all_rows)
    own_spans = spans(lines, own)
    own_bytes = sum(e - s for s, e in own_spans)
    beyond = [
        (off, n)
        for off, n in placed
        if not any(s <= off and off + n <= e for s, e in own_spans)
    ]
    build.record = {
        "task": task,
        "policy": (
            "official US arcade English, as paired (D-038), unchanged; pair glyphs"
            " (D-024); END.BIN's own code table and SE.DAT's font (D-035)"
        ),
        "sources": {
            "program_sha256": hashlib.sha256(program).hexdigest(),
            "english_table": f"0x{dialogue.EN_TABLE:06X}",
            "pairing": str(pairing_path),
            "END.BIN": hashlib.sha256(dialogue.checked("END.BIN")).hexdigest(),
            "SE.DAT": hashlib.sha256(dialogue.checked("SE.DAT")).hexdigest(),
        },
        "codes": {n: f"0x{c:04X}" for n, c in enumerate(codes.values())},
        "summary": {
            "boxes": len(boxes),
            "rows": len(all_rows),
            "pairs": len(wanted),
            "unused_codes_used": min(len(wanted), len(unused)),
            "new_codes": len(new),
            "sacrificed": [],
            "glyphs": len(glyphs),
            "own_free_lines": own,
            "own_room_bytes": own_bytes,
            "text_bytes": used_room,
            "bytes_beyond_own_lines": sum(n for _, n in beyond),
            "rows_beyond_own_lines": [f"0x{off:05X}" for off, _ in beyond],
            "unshown_room_bytes": sum(e - s for s, e in spans(lines, unshown)),
            "images": sorted(build.images),
        },
        "boxes": out_boxes,
    }
    return build
