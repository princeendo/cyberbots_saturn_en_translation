"""EXP-0082: the colours frame 0x79 (mech 16's VS name) is drawn with.

Run from the repository root, after ``check_mech.py``:

    ./invenv.sh python research/experiments/EXP-0082/palette.py OUT [--build BUILD]

Frame 0x79 draws with another palette than the sixteen mech names (the first
built art came out dark red where R·LIGHTNING is white). From the screenshots
at frame 2700 (``OUT/names0-02700.png``: the built art; ``names1-02700.png``:
the original kanji), each art's index grid is placed where every index shows
one colour, and the colour of each palette index is read off: frame 0x79's
indices from both, the sixteen's from R·LIGHTNING (mech 4, the P2 name).
Prints, per index, the RGB seen. The PNGs are decoded with zlib only.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.text import name_art as na


def png(path: Path) -> list[list[tuple[int, int, int]]]:
    data = path.read_bytes()
    pos, chunks = 8, b""
    width = height = 0
    while pos < len(data):
        n = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + n]
        if kind == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8 and ctype in (2, 6), (depth, ctype)
            bpp = 3 if ctype == 2 else 4
        elif kind == b"IDAT":
            chunks += body
        pos += 12 + n
    raw = zlib.decompress(chunks)
    stride = width * bpp
    rows: list[bytearray] = []
    prev = bytearray(stride)
    i = 0
    for _ in range(height):
        f = raw[i]
        line = bytearray(raw[i + 1 : i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[x] = (line[x] + pr) & 255
        rows.append(line)
        prev = line
    return [
        [tuple(r[x * bpp : x * bpp + 3]) for x in range(width)]  # type: ignore[misc]
        for r in rows
    ]


def fit(
    screen: list[list[tuple[int, int, int]]],
    grid: list[list[int]],
    xs: range,
    ys: range,
) -> dict[int, tuple[int, int, int]]:
    best: tuple[float, dict[int, tuple[int, int, int]]] = (-1.0, {})
    for oy in ys:
        for ox in xs:
            seen: defaultdict[int, Counter[tuple[int, int, int]]] = defaultdict(Counter)
            for y, row in enumerate(grid):
                for x, v in enumerate(row):
                    if v and 0 <= oy + y < len(screen) and 0 <= ox + x < len(screen[0]):
                        seen[v][screen[oy + y][ox + x]] += 1
            total = sum(sum(c.values()) for c in seen.values())
            agree = sum(c.most_common(1)[0][1] for c in seen.values())
            score = agree / total if total else 0
            if score > best[0]:
                best = (score, {v: c.most_common(1)[0][0] for v, c in seen.items()})
                best_at = (ox, oy)
    print("  fit", round(best[0], 3), "at", best_at)
    return best[1]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--build", type=Path, default=Path("build/sp017/a"))
    a = p.parse_args()
    stg = Path("local/extracted/saturn_jp/STG0AS.BIN").read_bytes()
    built = (a.build / "PL3F_0.BIN").read_bytes()
    untouched = Path("local/extracted/saturn_jp/PL3F_0.BIN").read_bytes()
    eng = png(a.out / "names0-02700.png")
    jap = png(a.out / "names1-02700.png")
    print("frame 0x79, built art:")
    g, _ = na.compose(built, stg, 0x79, 0)
    c1 = fit(eng, g, range(0, 60), range(30, 50))
    print("frame 0x79, original kanji:")
    g, _ = na.compose(untouched, stg, 0x79, 0)
    c2 = fit(jap, g, range(0, 60), range(30, 50))
    print("frame 0x10 (R-LIGHTNING), built:")
    g, _ = na.compose(built, stg, 0x10, 15)
    c3 = fit(eng, g, range(170, 230), range(30, 50))
    for label, c in (("0x79 built", c1), ("0x79 kanji", c2), ("sixteen", c3)):
        print(label, {k: c[k] for k in sorted(c)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
