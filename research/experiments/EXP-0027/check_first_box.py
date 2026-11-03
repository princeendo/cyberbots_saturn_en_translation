"""EXP-0027: check a forced scene's first box against the original font.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/check_first_box.py BOXES SCENE RUN

``BOXES`` is a box list (``data/text/<pilot>_boxes.json``). Predicts the
first box of ``SCENE`` from the untouched `STG0AS.BIN` lines and `KANJI.BIN`
(D-019): one cell per character that has a glyph. Reports the best leading
match over ``RUN/cells-*.bin``. Prints counts only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji

FILES = Path("local/extracted/saturn_jp")


def main(boxes: Path, scene: int, run: Path) -> int:
    stg = (FILES / "STG0AS.BIN").read_bytes()
    cells = kanji.decode((FILES / "KANJI.BIN").read_bytes())
    codes = kanji.read_code_table(stg)
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    box = json.loads(boxes.read_text())["scenes"][scene]["boxes"][0]
    want = []
    for line in box["lines"]:
        off, n, _, _ = table[line]
        text = stg[off : off + n]
        for i in range(0, n - 1, 2):
            code = int.from_bytes(text[i : i + 2], "big")
            if code in codes:
                want.append(hashlib.sha256(cells[codes.index(code)]).hexdigest())
    best = (0, "")
    for path in sorted(run.glob("cells-*.bin")):
        data = path.read_bytes()
        n = 0
        while (
            n < len(want)
            and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest() == want[n]
        ):
            n += 1
        best = max(best, (n, path.name))
    print(
        json.dumps(
            {"scene": scene, "box": box["box"], "predicted": len(want), "best": best}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])))
