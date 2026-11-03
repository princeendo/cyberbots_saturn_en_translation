"""EXP-0022: compare a forced run's glyph cells with the predicted first box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0022/check_cells.py RUN SCENE

Predicts the cells of the first box of Jin's ``SCENE`` from
``data/text/jin_boxes.json``, the lines in ``STG0AS.BIN`` and the font
(``tools.font.kanji``, D-019): one cell per character that has a glyph, in
order. For each ``RUN/cells-NN.bin`` it counts how many leading cells equal
the prediction, and prints the best step. Prints counts only.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji

FILES = Path("local/extracted/saturn_jp")
BASE = 0x06060000


def predicted(scene: int) -> list[bytes]:
    stg = (FILES / "STG0AS.BIN").read_bytes()
    cells = kanji.decode((FILES / "KANJI.BIN").read_bytes())
    codes = kanji.read_code_table(stg)
    boxes = json.loads(Path("data/text/jin_boxes.json").read_text())
    box = boxes["scenes"][scene]["boxes"][0]
    starts = []
    a = 0x0606F01C
    while a < 0x0606F01C + 50112:
        if stg[a - BASE] == 0:
            a += 4
            continue
        starts.append(a)
        a = (stg.index(b"\0", a - BASE) + BASE + 1 + 3) & ~3
    out = []
    for line in box["lines"]:
        o = starts[line] - BASE
        text = stg[o : stg.index(b"\0", o)]
        for i in range(0, len(text) - 1, 2):
            code = int.from_bytes(text[i : i + 2], "big")
            if code in codes:
                out.append(cells[codes.index(code)])
    return out


def main(run: Path, scene: int) -> int:
    want = predicted(scene)
    best = (0, "")
    for path in sorted(run.glob("cells-*.bin")):
        data = path.read_bytes()
        n = 0
        while n < len(want) and data[n * 0x80 : n * 0x80 + 0x80] == want[n]:
            n += 1
        best = max(best, (n, path.name))
    print(json.dumps({"scene": scene, "predicted_cells": len(want), "best": best}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2])))
