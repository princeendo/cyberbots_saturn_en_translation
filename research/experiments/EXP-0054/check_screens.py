"""EXP-0054: each English warning on screen against its built picture.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0054/check_screens.py \\
        [--build build/boot004/a] [--out research/experiments/EXP-0054/screens.json]

For each case in ``local/boot004/screens`` (cold boots of the built image,
``EXP-0051/boot_case.py``): the warning shown (R4), and the screenshot
against the expected screen: the built ``WARNINGn.PIX`` drawn by D-049's
rule (screen row = file row + 8, columns 0-351, the program's palette as
``c << 3``, value 0 and the rows outside the file's visible 224 black).
VDP2 VRAM from ``0x20000`` against the built file. The control (normal
save) against `EXP-0051`'s untouched control: same routine sequence, and
each screenshot equal to the untouched one at the same poll (frame labels
can drift by one). Numbers only.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.text import boot_warnings, dialogue

_spec = importlib.util.spec_from_file_location(
    "exp0038_compare", Path("research/experiments/EXP-0038/compare_runs.py")
)
assert _spec and _spec.loader
_cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cmp)
read_png = _cmp.read_png

RUNS = Path("local/boot004/screens")
CASES = {"damaged": 0, "zero": 1, "cart-zero": 2, "both-zero": 3, "free4": 4}


def expected(data: bytes, colours: list[tuple[int, int, int]]) -> bytes:
    out = bytearray()
    for y in range(240):
        fy = y - 8
        for x in range(352):
            v = data[fy * 512 + x] if 0 <= fy < boot_warnings.SHOWN_H else 0
            out += bytes(colours[v]) if v else b"\0\0\0"
    return bytes(out)


def rgb_of(path: Path) -> bytes:
    w, h, bpp, raw = read_png(path)
    return b"".join(raw[i * bpp : i * bpp + 3] for i in range(w * h))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, default=Path("build/boot004/a"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    colours = boot_warnings.palette(bytes(dialogue.checked("CYBER.BIN")))
    report: dict[str, Any] = {"cases": []}
    ok = True
    for case, n in CASES.items():
        run = RUNS / case
        route = json.loads((run / "route.json").read_text())
        shown = [h["R4"] for h in route["hits"] if h["PC"] == "0x06036DA8"]
        data = (args.build / f"WARNING{n}.PIX").read_bytes()
        shot = next(run.glob("w*.png"))
        have, want = rgb_of(shot), expected(data, colours)
        differing = sum(
            have[i : i + 3] != want[i : i + 3] for i in range(0, len(want), 3)
        )
        vdp2 = next(run.glob("vdp2_*.bin")).read_bytes()
        entry = {
            "case": case,
            "warnings_shown": shown,
            "screenshot": shot.name,
            "screenshot_sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
            "pixels_differing": differing,
            "vram_equals_built_file": vdp2[0x20000 : 0x20000 + len(data)] == data,
        }
        ok &= (
            shown == [f"{n:08X}"] and differing == 0 and entry["vram_equals_built_file"]
        )
        report["cases"].append(entry)
        print(entry)
    new, old = RUNS / "control", Path("local/boot001/control")
    seq = [
        [
            (h["frame"], h["PC"])
            for h in json.loads((r / "route.json").read_text())["hits"]
        ]
        for r in (new, old)
    ]
    # Poll frame labels can drift by a frame between runs (EXP-0038), so the
    # screenshots are paired in poll order and both labels are kept.
    mine = sorted(new.glob("f*.png"))
    theirs = sorted(old.glob("f*.png"))
    pairs = [
        {"built": x.name, "untouched": y.name, "equal": rgb_of(x) == rgb_of(y)}
        for x, y in zip(mine, theirs, strict=True)
    ]
    frames = pairs
    same = [q for q in pairs if q["equal"]]
    report["control"] = {
        "sequence_equal_untouched": seq[0] == seq[1],
        "screenshots": len(pairs),
        "equal_to_untouched": len(same),
        "pairs": pairs,
    }
    ok &= seq[0] == seq[1] and len(same) == len(frames)
    print("control", report["control"])
    report["ok"] = ok
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
