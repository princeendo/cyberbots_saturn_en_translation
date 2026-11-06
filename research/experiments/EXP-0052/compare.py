"""EXP-0052: compare the marked image's boots with the untouched ones.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0052/compare.py \\
        [--out research/experiments/EXP-0052/compare.json]

For each warning case, ``local/boot002/<case>`` (marked image, ``mark.py``)
against ``local/boot001/<case>`` (untouched, `EXP-0051`):

- the screenshot pixels that differ, split into the predicted ones (screen
  rows 236-239 in yellow; the ID block, rows 8-11, columns 16n to 16n+15,
  in cyan, n the picture shown) and any others;
- whether any red pixel appears (the hidden marks);
- whether VDP2 VRAM from ``0x20000`` equals the marked file;
- the warning calls (R4) of both runs.

For the control (normal save): every screenshot at the same frame, and the
check's routine sequence, equal in both runs. Numbers only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any

_spec = importlib.util.spec_from_file_location(
    "exp0038_compare", Path("research/experiments/EXP-0038/compare_runs.py")
)
assert _spec and _spec.loader
_cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cmp)
read_png = _cmp.read_png

CASES = {"damaged": 0, "zero": 1, "cart-zero": 2, "both-zero": 3, "free4": 4}
YELLOW, CYAN, RED = (240, 240, 0), (0, 240, 240), (240, 0, 0)
MARKED = Path("build/boot002/marked")


def pixels(path: Path) -> tuple[int, int, list[tuple[int, ...]]]:
    w, h, bpp, raw = read_png(path)
    return w, h, [tuple(raw[i * bpp : i * bpp + 3]) for i in range(w * h)]


def warnings(run: Path) -> list[str]:
    route = json.loads((run / "route.json").read_text())
    return [h["R4"] for h in route["hits"] if h["PC"] == "0x06036DA8"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report: dict[str, Any] = {"cases": []}
    for case, n in CASES.items():
        new, old = Path("local/boot002") / case, Path("local/boot001") / case
        shot = next(new.glob("w*.png"))
        w, h, a = pixels(shot)
        _, _, b = pixels(old / "w01457.png")
        predicted = {
            **{(x, y): YELLOW for y in range(236, 240) for x in range(w)},
            **{(x, y): CYAN for y in range(8, 12) for x in range(16 * n, 16 * n + 16)},
        }
        other = 0
        predicted_ok = 0
        for y in range(h):
            for x in range(w):
                i = y * w + x
                if (x, y) in predicted:
                    predicted_ok += a[i] == predicted[(x, y)]
                elif a[i] != b[i]:
                    other += 1
        vdp2 = next(new.glob("vdp2_*.bin")).read_bytes()
        marked = (MARKED / f"WARNING{n}.PIX").read_bytes()
        entry = {
            "case": case,
            "picture": n,
            "screenshot": shot.name,
            "warnings_marked": warnings(new),
            "warnings_untouched": warnings(old),
            "predicted_pixels": len(predicted),
            "predicted_pixels_as_predicted": predicted_ok,
            "other_pixels_differing": other,
            "red_pixels": sum(p == RED for p in a),
            "vram_equals_marked_file": vdp2[0x20000 : 0x20000 + len(marked)] == marked,
        }
        report["cases"].append(entry)
        print(entry)
    new, old = Path("local/boot002/control"), Path("local/boot001/control")
    frames = sorted(p.name for p in new.glob("f*.png"))
    same = [
        name
        for name in frames
        if (old / name).exists() and pixels(new / name)[2] == pixels(old / name)[2]
    ]
    seq = [
        [
            (h["frame"], h["PC"])
            for h in json.loads((r / "route.json").read_text())["hits"]
        ]
        for r in (new, old)
    ]
    control = {
        "screenshots": len(frames),
        "equal_to_untouched": len(same),
        "sequence_equal": seq[0] == seq[1],
    }
    report["control"] = control
    print("control", control)
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
