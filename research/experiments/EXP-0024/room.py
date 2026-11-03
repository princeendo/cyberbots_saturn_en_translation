"""EXP-0024: bytes, rows and glyphs each layout route needs, against the room.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0024/room.py ENGLISH_JSON

``ENGLISH_JSON`` is the ignored REF-003 decode (``local/ref003/text-cybotsu.json``,
English table ``0x0B33AA``). For Jin's 63 boxes (``data/translations/jin_pairing.json``)
and for all 488 paired slots (``data/text/saturn_arcade_pairing.json``), each
route re-flows the slot's English into rows and counts:

- ``rows``: rows per box (the box shows 4; a record holds 3 lines in its
  32 bytes, D-021);
- ``cells``: glyph cells (at most 60 per box, D-020);
- ``bytes``: line bytes as stored (2 per cell or pair, NUL, 4-byte alignment);
- ``glyphs``: distinct new glyphs.

Routes: ``a`` full-width capitals, 16 per row; ``b`` pair glyphs, 32
characters per row; ``c`` half-width characters at an 8-pixel advance, 28 per
row (from x = 116 to the screen edge at 352, D-020), one sprite and one
2-byte code each, since the renderer reads two bytes per glyph. Fits are also
counted with route ``d``'s raised limit of 252 cells.

It compares the bytes with the room Jin's Japanese lines now take (lines
0-120) and with the whole dialogue table (50,112 bytes). Prints counts only
(``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROWS_VISIBLE = 4
RECORD_LINES = 3
CELLS = 60
CELLS_RAISED = 252  # route d: VDP1 0x16400-0x1E1FF free in dialogue (EXP-0024)
TABLE_BYTES = 50112


def stored(n_units: int) -> int:
    """Bytes for a line of n two-byte units: NUL, then 4-byte alignment."""
    return (2 * n_units + 1 + 3) & ~3


def route(text: str, route_name: str) -> tuple[int, int, int, set[str]]:
    flat = " ".join(part.strip() for part in text.split("\n"))
    if route_name == "a":
        rows = textwrap.wrap(flat.upper(), 16) or [""]
        cells = sum(1 for r in rows for c in r if c != " ")
        data = sum(stored(len(r)) for r in rows)
        glyphs = {c for r in rows for c in r if c in ",'"}
    elif route_name == "b":
        rows = textwrap.wrap(flat, 32) or [""]
        cells, data, glyphs = 0, 0, set()
        for r in rows:
            padded = r + " " * (len(r) % 2)
            pairs = [padded[i : i + 2] for i in range(0, len(padded), 2)]
            cells += sum(1 for p in pairs if p != "  ")
            glyphs |= {p for p in pairs if p != "  "}
            data += stored(len(pairs))
    else:
        rows = textwrap.wrap(flat, 28) or [""]
        cells = sum(1 for r in rows for c in r if c != " ")
        data = sum(stored(len(r)) for r in rows)  # still one 2-byte code each
        glyphs = {c for r in rows for c in r}
    return len(rows), cells, data, glyphs


def main(english: Path) -> int:
    table = json.loads(english.read_text())["0x0B33AA"]
    jin = json.loads(Path("data/translations/jin_pairing.json").read_text())
    jin_slots = [p["arcade_slot"] for p in jin["pairs"]]
    ref006 = json.loads(Path("data/text/saturn_arcade_pairing.json").read_text())
    roster = sorted({e[0] for e in ref006["saturn"] if e})
    census = json.loads(Path("data/text/script_census.json").read_text())
    stg = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")
    rows_table = stg["blocks"][0]["table"]
    jin_room = sum(((ln + 1 + 3) & ~3) for _, ln, _, _ in rows_table[:121])
    out: dict[str, object] = {
        "jin_japanese_bytes": jin_room,
        "table_bytes": TABLE_BYTES,
    }
    for name in ("a", "b", "c"):
        for label, slots in (("jin", jin_slots), ("roster", roster)):
            results = [route(table[s], name) for s in slots]
            out[f"{name}_{label}"] = {
                "boxes": len(slots),
                "fit_rows_cells": sum(
                    1 for r, c, _, _ in results if r <= ROWS_VISIBLE and c <= CELLS
                ),
                "fit_rows_cells_252": sum(
                    1
                    for r, c, _, _ in results
                    if r <= ROWS_VISIBLE and c <= CELLS_RAISED
                ),
                "most_cells": max(c for _, c, _, _ in results),
                "over_3_lines": sum(1 for r, *_ in results if r > RECORD_LINES),
                "bytes": sum(b for _, _, b, _ in results),
                "glyphs": len(set().union(*(g for *_, g in results))),
            }
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
