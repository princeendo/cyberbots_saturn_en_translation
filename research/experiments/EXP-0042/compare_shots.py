"""EXP-0042: compare a run's screenshots with its control's, nearest frame.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0042/compare_shots.py \\
        CONTROL TEST [--until FRAME] [--slack 3]

A debug harness; it prints JSON with no pixels. Poll frames drift by a frame
or two between runs (``EXP-0038``), so each control screenshot
(``fNNNNN.png``) up to ``--until`` is paired with the test screenshot whose
frame is nearest, within ``--slack``. It reports how many pairs are
pixel-identical and, for the others, the differing pixel count and bounding
box. PNG decoding is ``EXP-0038/compare_runs.py``'s ``read_png``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "exp0038_compare", Path("research/experiments/EXP-0038/compare_runs.py")
)
assert _spec and _spec.loader
_compare = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_compare)
read_png = _compare.read_png


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("control", type=Path)
    parser.add_argument("test", type=Path)
    parser.add_argument("--until", type=int, default=1 << 30)
    parser.add_argument("--slack", type=int, default=3)
    args = parser.parse_args()
    test = {int(p.stem[1:]): p for p in args.test.glob("f*.png")}
    same, differing, unmatched = 0, [], []
    for path in sorted(args.control.glob("f*.png")):
        frame = int(path.stem[1:])
        if frame > args.until:
            continue
        near = min(test, key=lambda f: abs(f - frame), default=None)
        if near is None or abs(near - frame) > args.slack:
            unmatched.append(frame)
            continue
        w, h, bpp, a = read_png(path)
        w2, h2, bpp2, b = read_png(test[near])
        if (w, h, bpp) != (w2, h2, bpp2):
            differing.append({"frame": frame, "size": "differs"})
            continue
        pixels = [
            i // bpp for i in range(0, len(a), bpp) if a[i : i + bpp] != b[i : i + bpp]
        ]
        if not pixels:
            same += 1
            continue
        xs = [p % w for p in pixels]
        ys = [p // w for p in pixels]
        differing.append(
            {
                "frame": frame,
                "test_frame": near,
                "pixels": len(pixels),
                "box": [min(xs), min(ys), max(xs), max(ys)],
            }
        )
    print(
        json.dumps(
            {
                "identical": same,
                "differing": differing,
                "unmatched_control_frames": unmatched,
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
