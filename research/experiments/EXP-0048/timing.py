"""EXP-0048: how long each roster ending box holds its finished English line.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0048/timing.py \\
        local/ref003/cybotsu-maincpu.bin [--out OUT.json]

Static, plus the forced runs' box frames (``data/text/ending_surfaces.json``);
numbers only.

- **Cues.** `END.BIN`'s pointer table ``0x060879A0`` gives each list's cue
  table (16-bit frames; list N's runs to list N + 1's pointer). Script word
  ``0xEAnn`` waits until the scene timer reaches cue ``nn``; the box then
  closes (EXP-0048's controlled change).
- **Script walk.** From the first post's script (`END.BIN`'s scene lists
  ``0x06086E54``), the words are read in order:
  - below ``0x8000``: open a box;
  - ``0x8000`` | N: close box N;
  - ``0xEAnn``: wait for cue ``nn``;
  - ``0xE3xx``: wait ``xx`` frames;
  - ``0xE000``: wait for the next segment;
  - other words: not timing.

  The walk stops once every observed opening is matched. Each non-name
  opening gets the first timing word after it, before its close.
- **Typing.** The English rows as the compiler wraps them
  (``tools.text.dialogue.wrap``), counted in glyph cells (``cells_of``), at
  ``FRAMES_PER_CELL`` (6, measured in `EXP-0045`) plus ``START`` frames.
- **Hold.** The observed open time (open to close) less the typing time.
  For a box ending on a cue, the hold can be moved within its segment:
  each segment's spare is the sum over its cued boxes of (open time -
  typing - the minimum hold).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import decode, long, read_record
from tools.text import dialogue

BASE = 0x06060000
CUE_POINTERS = 0x060879A0
SCENE_LISTS = 0x06086E54
FRAMES_PER_CELL = 6
START = 6
END_BIN = Path("local/extracted/saturn_jp/END.BIN")
SURFACES = Path("data/text/ending_surfaces.json")
PAIRINGS = [
    Path(f"data/translations/{n}_ending_pairing.json")
    for n in ("jin", "santana", "mary", "arieta", "gawaine", "baomao")
]
NAMES = range(601, 615)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us = args.us.read_bytes()
    end = END_BIN.read_bytes()

    def u16(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 2], "big")

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    pointers = [u32(CUE_POINTERS + 4 * k) for k in range(10)]
    surfaces = json.loads(SURFACES.read_text())["lists"]
    result: list[dict[str, Any]] = []
    for n in range(6):
        cues = [u16(a) for a in range(pointers[n], pointers[n + 1], 2)]
        entry = surfaces[n]
        slot_of = {
            u["box"]: u["arcade_slot"]
            for u in json.loads(PAIRINGS[n].read_text())["units"]
            if u.get("arcade_slot") is not None
        }
        cells: dict[int, int] = {}
        for box, slot in slot_of.items():
            text = decode(read_record(us, long(us, dialogue.EN_TABLE + 4 * slot)).codes)
            cells[box] = dialogue.cells_of(dialogue.wrap(text))
        openings = [o for o in entry["openings"]]
        first_scene = entry["posts"][0]["scene"]
        a = u32(u32(SCENE_LISTS + 4 * n) + 4 * first_scene)
        tokens: list[tuple[str, int]] = []
        want = [o["box"] for o in openings]
        matched = 0
        while matched < len(want) and len(tokens) < 4000:
            w = u16(a)
            a += 2
            if w < 0x8000:
                tokens.append(("open", w))
                if w == want[matched]:
                    matched += 1
            elif w == 0xFFFF:
                continue
            elif w < 0xC000:
                tokens.append(("close", w & 0x7FFF))
            elif w & 0xFF00 == 0xEA00:
                tokens.append(("cue", w & 0xFF))
            elif w & 0xFF00 == 0xE300:
                tokens.append(("wait", w & 0xFF))
            elif w == 0xE000:
                tokens.append(("segment", 0))
        if matched < len(want):
            raise SystemExit(f"list {n}: script walk matched {matched}/{len(want)}")
        # Each non-name opening: its ending token and segment number.
        ends: list[tuple[str, int, int]] = []
        segment = 0
        for k, (kind, value) in enumerate(tokens):
            if kind == "segment":
                segment += 1
            if kind == "open" and value not in NAMES:
                stop = next(
                    (
                        (tk, tv)
                        for tk, tv in tokens[k + 1 :]
                        if tk in ("cue", "wait", "segment")
                        or (tk == "close" and tv == value)
                    ),
                    ("none", 0),
                )
                ends.append((stop[0], stop[1], segment))
        rows = []
        non_names = [o for o in openings if o["box"] not in NAMES]
        for o, (kind, value, seg) in zip(non_names, ends, strict=False):
            typing = START + FRAMES_PER_CELL * cells.get(o["box"], 0)
            rows.append(
                {
                    "box": o["box"],
                    "open": o["open"],
                    "close": o["close"],
                    "open_time": o["open_time"],
                    "ends_on": kind,
                    "cue": value if kind == "cue" else None,
                    "cue_frames": cues[value] if kind == "cue" else None,
                    "wait": value if kind == "wait" else None,
                    "segment": seg,
                    "english_cells": cells.get(o["box"]),
                    "typing": typing if o["box"] in cells else None,
                    "hold": (
                        o["open_time"] - typing
                        if o["open_time"] is not None and o["box"] in cells
                        else None
                    ),
                }
            )
        result.append({"list": n, "cues": cues, "boxes": rows})
        short = [
            (r["box"], r["hold"], r["ends_on"])
            for r in rows
            if r["hold"] is not None and r["hold"] < 60
        ]
        print(n, "boxes", len(rows), "hold < 60:", short)
    if args.out:
        args.out.write_text(json.dumps({"lists": result}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
