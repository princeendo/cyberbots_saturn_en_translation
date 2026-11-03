"""EXP-0030: check every box of a forced Japanese scene against given font files.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0030/japanese_check.py \\
        BOXES SCENE RUN [--files DIR]

A debug harness; it never ships. It generalizes
``research/experiments/EXP-0027/check_first_box.py`` (first box, original
files) to every box of the scene and to any `STG0AS.BIN` and `KANJI.BIN`:
``DIR`` holds the pair, default the untouched ``local/extracted/saturn_jp``.
For a built image, ``DIR`` is the compiler's ``OUT``, so a sacrificed code
predicts its pair glyph, the recorded trade-off.

Each box's prediction is one cell per character of its lines that has a table
code (D-019), from ``DIR``'s files, except the full-width space ``0x8140``,
which the typing routine skips without drawing a cell (EXP-0027's script
counted it; its boxes had none); the lines are numbered in the untouched
`STG0AS.BIN`. Reports the best leading match over ``RUN/cells-*.bin``. Prints
counts only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.text.dialogue import SPACE_CODE

FILES = Path("local/extracted/saturn_jp")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("boxes", type=Path)
    parser.add_argument("scene", type=int)
    parser.add_argument("run", type=Path)
    parser.add_argument("--files", type=Path, default=FILES)
    args = parser.parse_args()
    stg = (args.files / "STG0AS.BIN").read_bytes()
    cells = kanji.decode((args.files / "KANJI.BIN").read_bytes())
    codes = kanji.read_code_table(stg)
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    shots = [p.read_bytes() for p in sorted(args.run.glob("cells-*.bin"))]
    results = {}
    for box in json.loads(args.boxes.read_text())["scenes"][args.scene]["boxes"]:
        want = []
        for line in box["lines"]:
            off, n, _, _ = table[line]
            text = stg[off : off + n]
            for i in range(0, n - 1, 2):
                code = int.from_bytes(text[i : i + 2], "big")
                if code in codes and code != SPACE_CODE:  # a space draws no cell
                    want.append(hashlib.sha256(cells[codes.index(code)]).hexdigest())
        best = 0
        for data in shots:
            n = 0
            while (
                n < len(want)
                and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest() == want[n]
            ):
                n += 1
            best = max(best, n)
        results[str(box["box"])] = {"predicted": len(want), "matched": best}
    print(json.dumps({"scene": args.scene, "files": str(args.files), "boxes": results}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
