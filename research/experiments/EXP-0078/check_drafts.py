"""EXP-0078: check a Saturn-only pilot's English against the box rules.

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0078/check_drafts.py DRAFTS \\
        [--list 6] [--out OUT.json]

DRAFTS is a JSON file with ``boxes``: ``section`` (story, win_quotes,
captions, ending), ``box`` and ``english`` (other keys ignored). Checks:

- **Coverage:** exactly the boxes ``data/text/special_census.json`` lists
  for the list and section (`SPECIAL-010`), each once.
- **Characters:** only those the arcade pair font draws
  (``tools.font.pairs``: letters, digits, space and ``! " ' , - . : ?``).
- **Fit:** story, win-quote and ending boxes re-flowed by
  ``tools.text.dialogue.wrap`` (rows of up to 32 characters) must take at
  most ``MAX_ROWS`` (3) rows and ``MAX_CELLS`` (60) pair cells, as the
  roster's English (`LAYOUT-001`); captions one row of at most 26 characters
  (D-060).

Prints each failure and a summary; exits 1 on any failure. ``--out`` writes
the per-box rows, row count and cells (English only).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.text import dialogue

ALLOWED = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !\"',-.:?"
)
CAPTION_CHARS = 26
SECTIONS = ("story", "win_quotes", "captions", "ending")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("drafts", type=Path)
    p.add_argument("--list", type=int, default=6)
    p.add_argument("--out", type=Path)
    a = p.parse_args()
    drafts = json.loads(a.drafts.read_text())
    census = next(
        e
        for e in json.loads(Path("data/text/special_census.json").read_text())["lists"]
        if e["list"] == a.list
    )
    failures: list[str] = []
    rows_out: list[dict[str, Any]] = []
    for section in SECTIONS:
        want = sorted(census[section]["box_list"])
        got = [b["box"] for b in drafts["boxes"] if b["section"] == section]
        if sorted(got) != want:
            missing = sorted(set(want) - set(got))
            extra = sorted(set(got) - set(want))
            dupes = sorted({b for b in got if got.count(b) > 1})
            failures.append(f"{section}: missing {missing} extra {extra} twice {dupes}")
    for b in drafts["boxes"]:
        text = b["english"]
        bad = sorted(set(text) - ALLOWED)
        if bad:
            failures.append(f"box {b['box']}: characters {bad}")
        if b["section"] == "captions":
            rows = [text]
            if len(text) > CAPTION_CHARS:
                failures.append(
                    f"box {b['box']}: caption {len(text)} > {CAPTION_CHARS}"
                )
        else:
            rows = dialogue.wrap(text)
            if len(rows) > dialogue.MAX_ROWS:
                failures.append(f"box {b['box']}: {len(rows)} rows: {rows}")
            if not bad and dialogue.cells_of(rows) > dialogue.MAX_CELLS:
                failures.append(f"box {b['box']}: {dialogue.cells_of(rows)} cells")
        rows_out.append(
            {
                "section": b["section"],
                "box": b["box"],
                "rows": rows,
                "row_count": len(rows),
                "cells": dialogue.cells_of(rows) if not bad else None,
            }
        )
    for f in failures:
        print(f)
    print(
        f"list {a.list}: {len(drafts['boxes'])} boxes, {len(failures)} failures, "
        f"max rows {max(r['row_count'] for r in rows_out)}, "
        f"max cells {max(r['cells'] or 0 for r in rows_out)}"
    )
    if a.out:
        a.out.write_text(
            json.dumps({"list": a.list, "boxes": rows_out}, indent=1) + "\n"
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
