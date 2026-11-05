"""EXP-0038: compare a probe run of ``ending_probe.py`` with its control.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/compare_runs.py \\
        CONTROL TEST [--glyph G ...]

A debug harness; it never ships. It prints JSON with no game text or
pixels. Both runs start from the same checkpoint, so their polls fall on the
same frames. It reports:

- whether the two runs logged the same disc reads, scene posts and box calls;
- every glyph cell (``cNNNNN.bin``, 60 cells of ``0x80`` bytes) that differs
  at the same frame, grouped by cell index, with what the test run's cell
  holds: the probe block (128 bytes of ``0xEE``), one of the ``--glyph``
  cells decoded from the untouched ``KANJI.BIN`` (``tools.font.kanji``), or
  something else (its SHA-256 prefix), and what the control held;
- for every screenshot (``fNNNNN.png``) at the same frame, the number of
  differing pixels and their bounding box.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji

CELL = 0x80
PROBE = bytes([0xEE]) * CELL
FONT = Path("local/extracted/saturn_jp/KANJI.BIN")


def read_png(path: Path) -> tuple[int, int, int, bytes]:
    """Width, height, bytes per pixel, unfiltered rows (8-bit RGB or RGBA)."""
    data = path.read_bytes()
    pos, idat = 8, b""
    width = height = bpp = 0
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + length]
        if kind == b"IHDR":
            width, height, depth, color = struct.unpack(">IIBB", body[:10])
            if depth != 8 or color not in (2, 6):
                raise ValueError(f"{path}: unsupported PNG {depth=} {color=}")
            bpp = 3 if color == 2 else 4
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(idat)
    stride = width * bpp
    out = bytearray()
    prev = bytearray(stride)
    for y in range(height):
        ftype = raw[y * (stride + 1)]
        row = bytearray(raw[y * (stride + 1) + 1 : (y + 1) * (stride + 1)])
        for i in range(stride):
            a = row[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ftype == 1:
                row[i] = (row[i] + a) & 0xFF
            elif ftype == 2:
                row[i] = (row[i] + b) & 0xFF
            elif ftype == 3:
                row[i] = (row[i] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                row[i] = (row[i] + pred) & 0xFF
        out += row
        prev = row
    return width, height, bpp, bytes(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("control", type=Path)
    parser.add_argument("test", type=Path)
    parser.add_argument("--glyph", type=int, action="append", default=[])
    args = parser.parse_args()
    a = json.loads((args.control / "route.json").read_text())
    b = json.loads((args.test / "route.json").read_text())
    font = kanji.decode(FONT.read_bytes())
    named = {font[g]: f"glyph {g}" for g in args.glyph} | {PROBE: "probe block"}

    def name(cell: bytes) -> str:
        if cell in named:
            return named[cell]
        if cell == bytes(CELL):
            return "zero"
        return "other " + hashlib.sha256(cell).hexdigest()[:12]

    # The runs may differ in length: compare the events up to the shorter's end.
    end = min(
        max(int(p.stem[1:]) for p in run.glob("f*.png"))
        for run in (args.control, args.test)
    )
    report: dict[str, Any] = {
        key: [x for x in a[key] if x["frame"] <= end]
        == [x for x in b[key] if x["frame"] <= end]
        for key in ("loads", "posts", "boxes")
    }
    by_cell: dict[int, dict[str, Any]] = {}
    frames = 0
    for path in sorted(args.control.glob("c*.bin")):
        other = args.test / path.name
        if not other.exists():
            continue
        frames += 1
        x, y = path.read_bytes(), other.read_bytes()
        for i in range(len(x) // CELL):
            cx, cy = x[i * CELL : (i + 1) * CELL], y[i * CELL : (i + 1) * CELL]
            if cx != cy:
                entry = by_cell.setdefault(i, {"frames": [], "pairs": {}})
                entry["frames"].append(int(path.stem[1:]))
                key = f"{name(cx)} -> {name(cy)}"
                entry["pairs"][key] = entry["pairs"].get(key, 0) + 1
    report["cell_frames_compared"] = frames

    def windows(run: dict[str, Any]) -> list[tuple[int, int, int]]:
        """(box, open frame, close frame) for every END.BIN box, in order."""
        out: list[tuple[int, int, int]] = []
        opened: dict[int, int] = {}
        for x in run["boxes"]:
            if x["table"] != "0x060817B4":
                continue
            word, frame = int(x["word"], 16), x["frame"]
            if word & 0x8000 and word & 0x7FFF in opened:
                out.append((word & 0x7FFF, opened.pop(word & 0x7FFF), frame))
            elif not word & 0x8000:
                opened[word] = frame
        return sorted(out, key=lambda w: w[1])

    def last_dump(run: Path, start: int, stop: int) -> bytes | None:
        inside = [p for p in run.glob("c*.bin") if start < int(p.stem[1:]) < stop]
        return (
            max(inside, key=lambda p: int(p.stem[1:])).read_bytes() if inside else None
        )

    # Poll frames drift a few frames between runs; game events do not. So
    # each box is also compared by the last dump taken while it is open.
    final: list[dict[str, Any]] = []
    for (box, s1, e1), (box2, s2, e2) in zip(windows(a), windows(b), strict=False):
        x, y = last_dump(args.control, s1, e1), last_dump(args.test, s2, e2)
        if x is None or y is None:
            final.append({"box": box, "missing_dump": True})
            continue
        cells = [
            {
                "cell": i,
                "control_to_test": f"{name(x[i * CELL : (i + 1) * CELL])} -> "
                f"{name(y[i * CELL : (i + 1) * CELL])}",
            }
            for i in range(len(x) // CELL)
            if x[i * CELL : (i + 1) * CELL] != y[i * CELL : (i + 1) * CELL]
        ]
        final.append(
            {"box": box, "same_box": box == box2, "open": [s1, s2], "differing": cells}
        )
    report["boxes_final_compared"] = len(final)
    report["boxes_final_differing"] = [
        f
        for f in final
        if f.get("differing") or not f.get("same_box", True) or f.get("missing_dump")
    ]
    report["cells_differing"] = {
        i: {
            "first": e["frames"][0],
            "last": e["frames"][-1],
            "polls": len(e["frames"]),
            "control_to_test": e["pairs"],
        }
        for i, e in sorted(by_cell.items())
    }
    shots: list[dict[str, Any]] = []
    for path in sorted(args.control.glob("f*.png")):
        other = args.test / path.name
        if not other.exists():
            continue
        w, h, bpp, p = read_png(path)
        w2, h2, bpp2, q = read_png(other)
        if (w, h, bpp) != (w2, h2, bpp2):
            shots.append({"frame": int(path.stem[1:]), "size_differs": True})
            continue
        xs, ys, n = [], [], 0
        for k in range(w * h):
            if p[k * bpp : k * bpp + 3] != q[k * bpp : k * bpp + 3]:
                n += 1
                xs.append(k % w)
                ys.append(k // w)
        if n:
            shots.append(
                {
                    "frame": int(path.stem[1:]),
                    "pixels": n,
                    "box": [min(xs), min(ys), max(xs), max(ys)],
                    "size": [w, h],
                }
            )
    report["screenshots_compared"] = sum(
        (args.test / p.name).exists() for p in args.control.glob("f*.png")
    )
    report["screenshots_differing"] = shots
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
