"""EXP-0036: check forced win-quote boxes' glyph cells against a prediction.

Run from the repository root, after ``EXP-0032/saturn_quote.py force OUT
BOX...`` on a built image:

    ./invenv.sh python research/experiments/EXP-0036/check_quotes.py \\
        OUT build/re008/roster BOX...

For each BOX, the cells to expect are the build's ``prediction.json`` entry
(an English quote), or, for a box the build did not write, the box's
Japanese lines drawn from the build's `STG0AS.BIN` code table and
`KANJI.BIN`, one cell per character with a table code, the full-width
space ``0x8140`` drawing none (as ``EXP-0030/japanese_check.py``). The
lines are read through `STG0AS.BIN`'s box records; for the quote boxes
they are the same lines as `VICTORY.BIN`'s (D-030). Reports, per box, the
best leading match over ``OUT/forceBOX-cells-*.bin``. Prints JSON.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji
from tools.text.dialogue import BASE, RECORDS, SPACE_CODE, line_table


def u32(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - BASE : a - BASE + 4], "big")


def main(out: Path, build: Path, boxes: list[int]) -> int:
    prediction = {
        p["box"]: p["cells"]
        for p in json.loads((build / "prediction.json").read_text())
    }
    original = Path("local/extracted/saturn_jp/STG0AS.BIN").read_bytes()
    stg = (build / "STG0AS.BIN").read_bytes()
    cells = kanji.decode((build / "KANJI.BIN").read_bytes())
    table = kanji.read_code_table(stg)
    lines = line_table()
    address_line = {BASE + off: i for i, (off, _) in enumerate(lines)}
    results = {}
    for box in boxes:
        if box in prediction:
            want, kind = prediction[box], "english"
        else:
            want, kind, entry = [], "japanese", u32(original, RECORDS + 4 * box) + 8
            while True:
                n = address_line[u32(original, entry)]
                off, length = lines[n]
                text = original[off : off + length]
                for i in range(0, length - 1, 2):
                    code = int.from_bytes(text[i : i + 2], "big")
                    if code in table and code != SPACE_CODE:
                        want.append(
                            hashlib.sha256(cells[table.index(code)]).hexdigest()
                        )
                if (
                    int.from_bytes(original[entry + 4 - BASE : entry + 6 - BASE], "big")
                    != 0xFFFF
                ):
                    break
                entry += 8
        best = 0
        for path in sorted(out.glob(f"force{box}-cells-*.bin")):
            data = path.read_bytes()
            n = 0
            while (
                n < len(want)
                and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest() == want[n]
            ):
                n += 1
            best = max(best, n)
        results[str(box)] = {"kind": kind, "predicted": len(want), "matched": best}
    print(json.dumps(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), Path(sys.argv[2]), [int(a) for a in sys.argv[3:]])
    )
