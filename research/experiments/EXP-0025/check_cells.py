"""EXP-0025: compare replayed glyph cells with the Phase C prediction.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/check_cells.py RUN PREDICTION

For ``RUN/cells-NN.bin`` (``replay_cells.py``), reports the best leading match
of two predictions:

- the test box: the cells in ``PREDICTION`` (``build.py``'s
  ``prediction.json``), pairs of spaces excluded;
- the box after it, Shade's reply (Saturn lines 6-7), from the original font.

Prints counts only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji

FILES = Path("local/extracted/saturn_jp")


def best(run: Path, want: list[str]) -> tuple[int, str]:
    result = (0, "")
    for path in sorted(run.glob("cells-*.bin")):
        data = path.read_bytes()
        n = 0
        while (
            n < len(want)
            and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest() == want[n]
        ):
            n += 1
        result = max(result, (n, path.name))
    return result


def reply_cells() -> list[str]:
    stg = (FILES / "STG0AS.BIN").read_bytes()
    cells = kanji.decode((FILES / "KANJI.BIN").read_bytes())
    codes = kanji.read_code_table(stg)
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    want = []
    for line in (6, 7):
        off, n, _, _ = table[line]
        text = stg[off : off + n]
        for i in range(0, n - 1, 2):
            code = int.from_bytes(text[i : i + 2], "big")
            if code in codes:
                want.append(hashlib.sha256(cells[codes.index(code)]).hexdigest())
    return want


def main(run: Path, prediction: Path) -> int:
    rows = json.loads(prediction.read_text())["rows"]
    test = [c["sha256"] for row in rows for c in row if c["slot"] is not None]
    reply = reply_cells()
    print(
        json.dumps(
            {
                "test_box": {"predicted": len(test), "best": best(run, test)},
                "reply": {"predicted": len(reply), "best": best(run, reply)},
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
