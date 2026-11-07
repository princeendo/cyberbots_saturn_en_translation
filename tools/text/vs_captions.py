"""English VS chapter captions as story pair glyphs (UI-006).

The approved captions (``data/translations/vs_captions.json``, `UI-005`) are
one row each, centred in the banner's 26 character places (D-060), drawn by
the caption reader through the story's box routine with `KANJI.BIN` and
`STG0AS.BIN`'s code table (D-019, D-020).

``tools.text.dialogue --vs-captions`` calls ``compile_captions`` after the
story, quotes and endings are compiled, so their codes, glyphs and rows stay
as they were:

- **Pairs.** A caption pair the story already has keeps the story's code.
  Each new pair takes the next code of ``candidates``: Japanese codes in the
  sacrifice order, from which the caller has removed every code the story,
  the quotes and the endings use, and every code of a shown line that stays
  Japanese. So no shown Japanese line changes.
- **Rows.** Each row (NUL-terminated, 4-byte aligned, ``0x8140`` for two
  spaces) goes first-fit into ``room``: what the story rows left of their
  room, then the captions' own Japanese lines.
- **Records.** Each caption box's single entry is pointed at its row: only
  the entry's 4-byte pointer changes.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from tools.font import pairs

BASE = 0x06060000
RECORDS = 0x060A5684
PLACES = 26  # 13 cells, two characters each (D-060)


@dataclass
class Compiled:
    rows: dict[int, str]  # box -> centred row
    new_pairs: dict[str, int]  # pair -> code (pairs the story did not have)
    changes: list[dict[str, object]] = field(default_factory=list)
    prediction: list[dict[str, object]] = field(default_factory=list)
    placed: dict[int, int] = field(default_factory=dict)  # box -> file offset


def centred(text: str) -> str:
    if len(text) > PLACES:
        raise ValueError(f"{text!r}: {len(text)} characters, {PLACES} fit")
    return " " * ((PLACES - len(text)) // 2) + text


def caption_rows(
    approved: Mapping[str, Any], story: Mapping[str, int] | None = None
) -> dict[int, str]:
    """Each caption centred; with ``story``, nudged by half a cell where that
    lets it reuse pairs (``best_offsets``)."""
    texts = {int(c["box"]): str(c["english"]) for c in approved["captions"]}
    if story is None:
        return {box: centred(text) for box, text in texts.items()}
    return best_offsets(texts, story)


def best_offsets(texts: Mapping[int, str], story: Mapping[str, int]) -> dict[int, str]:
    """Centre each caption, or move it half a cell either way (one leading
    space more or fewer), whichever adds fewer pairs that neither the story
    nor another caption has (as ``tools.text.dialogue.shift_rows``, CAP-001).
    Greedy passes in box order until nothing changes; ties stay centred."""

    def variants(text: str) -> list[str]:
        base = (PLACES - len(text)) // 2
        out = [" " * base + text]
        for k in (base - 1, base + 1):
            if 0 <= k <= PLACES - len(text):
                out.append(" " * k + text)
        return out

    def ps(row: str) -> set[str]:
        return {p for p in pairs.split_pairs(row) if p != "  "}

    boxes = sorted(texts)
    options = {b: variants(texts[b]) for b in boxes}
    choice = dict.fromkeys(boxes, 0)
    count: dict[str, int] = {}
    for b in boxes:
        for p in ps(options[b][0]):
            count[p] = count.get(p, 0) + 1
    while True:
        changed = 0
        for b in boxes:
            for p in ps(options[b][choice[b]]):
                count[p] -= 1
            cost = [
                sum(1 for p in ps(v) if p not in story and count.get(p, 0) <= 0)
                for v in options[b]
            ]
            best = min(range(len(cost)), key=lambda i: (cost[i], i))
            changed += best != choice[b]
            choice[b] = best
            for p in ps(options[b][best]):
                count[p] = count.get(p, 0) + 1
        if not changed:
            return {b: options[b][choice[b]] for b in boxes}


def new_pairs(rows: Mapping[int, str], story: Mapping[str, int]) -> list[str]:
    """Pairs the captions need that the story has not, in caption order."""
    return list(
        dict.fromkeys(
            p
            for box in sorted(rows)
            for p in pairs.split_pairs(rows[box])
            if p != "  " and p not in story
        )
    )


def leftover(rows: Sequence[bytes], room: Sequence[Sequence[int]]) -> list[list[int]]:
    """The free spans after ``tools.text.dialogue.place`` put ``rows`` in ``room``."""
    free = [list(r) for r in room]
    for data in rows:
        for span in free:
            if span[1] - span[0] >= len(data):
                span[0] += len(data)
                break
        else:
            raise ValueError("the rows do not fit in the text room")
    return [s for s in free if s[1] > s[0]]


def row_bytes(row: str, codes: Mapping[str, int], space: int) -> bytes:
    data = b"".join(
        (space if p == "  " else codes[p]).to_bytes(2, "big")
        for p in pairs.split_pairs(row)
    )
    data += b"\0"
    return data + bytes(-len(data) % 4)


def compile_captions(
    approved: Mapping[str, Any],
    stg: bytearray,
    cells: list[bytes],
    table: Sequence[int],
    story: Mapping[str, int],
    font: dict[str, pairs.Glyph],
    candidates: Sequence[int],
    room: Sequence[Sequence[int]],
    space: int,
) -> Compiled:
    """Write the captions into ``stg`` and ``cells``; see the module notes."""
    rows = caption_rows(approved, story)
    wanted = new_pairs(rows, story)
    if len(wanted) > len(candidates):
        raise ValueError(f"{len(wanted)} new pairs, {len(candidates)} codes free")
    added = dict(zip(wanted, candidates, strict=False))
    codes = {**story, **added}
    out = Compiled(rows=rows, new_pairs=added)
    for pair, code in added.items():
        glyph = table.index(code)
        cells[glyph] = pairs.render_pair(font, pair)
    free = [list(r) for r in room]
    for box in sorted(rows):
        data = row_bytes(rows[box], codes, space)
        span = next((s for s in free if s[1] - s[0] >= len(data)), None)
        if span is None:
            raise ValueError(f"box {box}: no room for {len(data)} bytes")
        off = span[0]
        span[0] += len(data)
        stg[off : off + len(data)] = data
        out.placed[box] = off
        out.changes.append(
            {
                "file": "STG0AS.BIN",
                "start": off,
                "end": off + len(data),
                "what": f"caption box {box} row",
            }
        )
        rec = int.from_bytes(
            stg[RECORDS - BASE + 4 * box : RECORDS - BASE + 4 * box + 4], "big"
        )
        entry = rec - BASE + 8
        stg[entry : entry + 4] = (BASE + off).to_bytes(4, "big")
        out.changes.append(
            {
                "file": "STG0AS.BIN",
                "start": entry,
                "end": entry + 4,
                "what": f"caption box {box} row pointer",
            }
        )
        drawn = [
            cells[table.index(codes[p])]
            for p in pairs.split_pairs(rows[box])
            if p != "  "
        ]
        out.prediction.append(
            {"box": box, "cells": [hashlib.sha256(c).hexdigest() for c in drawn]}
        )
    return out
