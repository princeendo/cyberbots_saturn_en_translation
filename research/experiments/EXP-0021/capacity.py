"""EXP-0021: how much of the paired arcade English fits the Saturn box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0021/capacity.py ENGLISH_JSON

``ENGLISH_JSON`` is the ignored REF-003 decode of the US set
(``local/ref003/text-cybotsu.json``; the English table at ``0x0B33AA``). The
paired slots are those of ``data/text/saturn_arcade_pairing.json`` (D-011).
The box, measured in EXP-0021: rows of 16 cells, 4 rows visible, 60 glyph
cells per box, where a space takes a position but no cell. Three ways to fill
it are counted:

- ``as_written``: one character per cell, the arcade's own line breaks;
- ``rewrapped``: one character per cell, words re-flowed into 16-cell rows;
- ``pairs``: two characters per cell (pair glyphs, as ``Dr``), re-flowed into
  32-character rows; a cell of two spaces takes no glyph.

A record fits when it needs at most 4 rows and 60 cells. The script also
counts the distinct two-character pairs the ``pairs`` route needs. Prints
counts only, never text (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROW_CELLS = 16
ROWS = 4
CELLS = 60
PAIRING = Path("data/text/saturn_arcade_pairing.json")
TABLE = "0x0B33AA"


def cells_single(rows: list[str]) -> int:
    return sum(1 for row in rows for c in row if c != " ")


def fits(rows: list[str], width: int, cells: int) -> bool:
    return len(rows) <= ROWS and all(len(r) <= width for r in rows) and cells <= CELLS


def pair_rows(text: str) -> list[str]:
    return textwrap.wrap(text, 2 * ROW_CELLS) or [""]


def pair_cells(rows: list[str]) -> tuple[int, set[str]]:
    pairs = set()
    count = 0
    for row in rows:
        padded = row + " " * (len(row) % 2)
        for i in range(0, len(padded), 2):
            pair = padded[i : i + 2]
            if pair != "  ":
                count += 1
                pairs.add(pair)
    return count, pairs


def main(english: Path) -> int:
    pairing = json.loads(PAIRING.read_text())
    slots = sorted({e[0] for e in pairing["saturn"] if e and e[0] is not None})
    table = json.loads(english.read_text())[TABLE]
    as_written = rewrapped = paired = 0
    longest_line = max_lines = 0
    all_pairs: set[str] = set()
    for slot in slots:
        lines = [line.rstrip() for line in table[slot].split("\n")]
        longest_line = max(longest_line, *(len(line) for line in lines))
        max_lines = max(max_lines, len(lines))
        as_written += fits(lines, ROW_CELLS, cells_single(lines))
        flat = " ".join(line.strip() for line in lines)
        rows = textwrap.wrap(flat, ROW_CELLS) or [""]
        rewrapped += fits(rows, ROW_CELLS, cells_single(rows))
        prow = pair_rows(flat)
        count, pairs = pair_cells(prow)
        paired += fits(prow, 2 * ROW_CELLS, count)
        all_pairs |= pairs
    print(
        json.dumps(
            {
                "slots": len(slots),
                "longest_arcade_line": longest_line,
                "most_arcade_lines": max_lines,
                "fit_as_written": as_written,
                "fit_rewrapped": rewrapped,
                "fit_pairs": paired,
                "distinct_pairs": len(all_pairs),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
