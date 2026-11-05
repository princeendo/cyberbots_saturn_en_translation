"""EXP-0036: every changed byte of a build is one the compiler says it wrote.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/untouched.py build/re008/roster

Compares each replacement file in ``OUT`` (``STG0AS.BIN``, ``VICTORY.BIN``,
``KANJI.BIN``) with the untouched one in ``local/extracted/saturn_jp``:

- `STG0AS.BIN`, `VICTORY.BIN`: every differing byte must lie in a range of
  ``OUT/changes.json`` (a row, a record's entries, the new table codes);
- `KANJI.BIN`: decoded into glyph cells (``tools.font.kanji``), every
  differing cell must be one of ``kanji_glyphs`` (the cells of the codes the
  build assigned), and re-encoding the original cells must give the original
  file back (so nothing outside the cells is stored).

Also reports the bytes and cells changed. Prints JSON; exits 1 on any byte
outside the ranges.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji

SOURCE = Path("local/extracted/saturn_jp")


def main(out: Path) -> int:
    changes = json.loads((out / "changes.json").read_text())
    report: dict[str, object] = {}
    ok = True
    for name in ("STG0AS.BIN", "VICTORY.BIN"):
        if not (out / name).exists():
            continue
        old, new = (SOURCE / name).read_bytes(), (out / name).read_bytes()
        allowed = bytearray(len(old))
        for r in changes["ranges"]:
            if r["file"] == name:
                allowed[r["start"] : r["end"]] = b"\1" * (r["end"] - r["start"])
        diff = [i for i in range(len(old)) if old[i] != new[i]]
        outside = [i for i in diff if not allowed[i]]
        ok &= not outside and len(old) == len(new)
        report[name] = {
            "bytes_changed": len(diff),
            "bytes_allowed": sum(allowed),
            "outside": [hex(i) for i in outside[:20]],
            "same_size": len(old) == len(new),
        }
    old_k, new_k = (SOURCE / "KANJI.BIN").read_bytes(), (out / "KANJI.BIN").read_bytes()
    old_cells, new_cells = kanji.decode(old_k), kanji.decode(new_k)
    changed = [
        i for i, (a, b) in enumerate(zip(old_cells, new_cells, strict=True)) if a != b
    ]
    glyphs = set(changes["kanji_glyphs"])
    round_trip = kanji.encode(old_cells) == old_k
    outside_cells = [i for i in changed if i not in glyphs]
    ok &= round_trip and not outside_cells and len(old_k) == len(new_k)
    report["KANJI.BIN"] = {
        "cells_changed": len(changed),
        "cells_allowed": len(glyphs),
        "outside": outside_cells[:20],
        "round_trip": round_trip,
    }
    report["ok"] = ok
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
