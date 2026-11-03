"""EXP-0025: cut the arcade's English dialogue glyphs out of MAME code sheets.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/capture_font.py OUT

The code sheets are MAME runs (``timelines/codes-N.txt``). Each draws slot 2
from a test record in work RAM: every code of a range, each followed by a
space (``0xF0``), 15 to a line, 3 lines (a fourth line overlaps the box's
border). Sheet 6 holds the punctuation and the apostrophe ``0xF8``. The snapshots are in
``local/layout001/fontcodes/N/``. The arcade's dialogue font is monospace (the
draw routine ``0x11F5C`` adds 8 to x per character), with a 1-pixel outline
reaching into the neighbouring cells. So each glyph is cut from a window from
1 pixel left of its cell to its 8th column. A space advances 5 pixels,
so the glyphs are 13 apart, and its neighbours are spaces,
so the window holds nothing else.

The grid origin is x = 132, y = 152 for the header x ``0x7C`` and y ``0xA8``,
and lines are 16 pixels apart. Uses the last snapshot before the next slot is
written. Writes ``OUT/arcade_font.json`` (an ignored path: the arcade's glyph
art is never committed):

    {"palette": ["666666", ...], "glyphs": {"<hex code>": {"char": c,
     "left": n, "rows": [[index, ...] x 16]}}}

``left`` is the glyph's first inked column relative to its cell's x. The
background is index 0.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import DECODE

W, H = 384, 224
BACKGROUND = bytes((0x66, 0x66, 0x66))
X0, Y0, PITCH_X, PITCH_Y, PER_LINE = 132, 152, 13, 16, 15  # 8 + a 5-px space
CODES = list(range(1, 0xF0))
SHEETS: dict[int, list[int]] = {k: CODES[45 * k : 45 * k + 45] for k in range(6)}
SHEETS[6] = [0x09, 0x0B, 0x14, 0x18, 0x1B, 0x1C, 0xF8, 0x7E, 0x7F]


def rgb(path: Path) -> bytes:
    command = ["ffmpeg", "-loglevel", "error", "-i", str(path)]
    command += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.run(command, capture_output=True, check=True).stdout


def last_full_snapshot(folder: Path) -> Path:
    writes = [
        ln.split() for ln in (folder / "writes-slot.txt").read_text().splitlines()
    ]
    later = [int(w[0]) for w in writes if int(w[0]) > 3231 and not w[2].startswith("8")]
    limit = (min(later) if later else 3470) - 2
    shots = sorted(folder.glob("cybotsu_f*.png"))
    return [p for p in shots if int(p.stem.split("_f")[1]) < limit][-1]


def main(out: Path) -> int:
    palette: list[bytes] = [BACKGROUND]
    glyphs: dict[str, dict[str, object]] = {}
    for sheet, codes in SHEETS.items():
        raw = rgb(last_full_snapshot(Path(f"local/layout001/fontcodes/{sheet}")))

        def px(x: int, y: int, raw: bytes = raw) -> bytes:
            return raw[(y * W + x) * 3 : (y * W + x) * 3 + 3]

        for n, code in enumerate(codes):
            cx = X0 + PITCH_X * (n % PER_LINE)
            cy = Y0 + PITCH_Y * (n // PER_LINE)
            window = range(cx - 1, cx + 9)
            columns = [
                x for x in window if any(px(x, cy + j) != BACKGROUND for j in range(16))
            ]
            if not columns:
                continue
            rows = []
            for j in range(16):
                row = []
                for x in range(columns[0], columns[-1] + 1):
                    c = px(x, cy + j)
                    if c not in palette:
                        palette.append(c)
                    row.append(palette.index(c))
                rows.append(row)
            glyphs[f"{code:02X}"] = {
                "char": DECODE.get(code, ""),
                "left": columns[0] - cx,
                "rows": rows,
            }
    out.mkdir(parents=True, exist_ok=True)
    font = {"palette": [c.hex() for c in palette], "glyphs": glyphs}
    (out / "arcade_font.json").write_text(json.dumps(font))
    latin = {
        str(v["char"]): len(v["rows"][0])  # type: ignore[index]
        for v in glyphs.values()
        if v["char"]
    }
    print(
        json.dumps(
            {"glyphs": len(glyphs), "palette": font["palette"], "latin_widths": latin}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
