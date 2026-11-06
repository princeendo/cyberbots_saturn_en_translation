"""EXP-0057: find each name's sprite parts on screen and their bytes on the disc.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0057/locate.py \\
        [--out research/experiments/EXP-0057/locate.json]

Input: the VDP1 VRAM dumps of ``local/loc002/<run>`` (``EXP-0056/poke.py``
with ``--vdp1-at``; one run per name frame, D-051). For each run it keeps
the sprites of the player-1 name (by colour word and screen area):

- ``sel-FF`` (pilot select): colour ``0x61E0``, y 195-215;
- ``vsp-FF`` (VS pilot name): colour ``0x41E0``, y 200-220, x < 176;
- ``vsm-FF`` (VS mech name): colour ``0x41C0``, y 25-45, x < 176;

and searches each part's pixel bytes (4 bpp, width * height / 2) in every
extracted file. A part found once is reported with its file and offset; a
part found in several places, or nowhere, is reported as such. Numbers
only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.memory import vdp1_sprites

RUNS = Path("local/loc002")
FILES = Path("local/extracted/saturn_jp")
AREAS = {
    "sel": (0x61E0, 195, 215, 0, 352),
    "vsp": (0x41E0, 200, 220, 0, 176),
    "vsm": (0x41C0, 25, 45, 0, 176),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    files = {p.name: p.read_bytes() for p in sorted(FILES.iterdir()) if p.is_file()}
    report: list[dict[str, Any]] = []
    for run in sorted(RUNS.iterdir()):
        kind = run.name.split("-")[0]
        if kind not in AREAS or not list(run.glob("vdp1_*.bin")):
            continue
        colour, y0, y1, x0, x1 = AREAS[kind]
        vram = next(run.glob("vdp1_*.bin")).read_bytes()
        parts = []
        for s in vdp1_sprites.sprites(vram):
            if s.color_word != colour or not (y0 <= s.y <= y1 and x0 <= s.x < x1):
                continue
            data = vdp1_sprites.pixel_bytes(vram, s)
            where = []
            for name, blob in files.items():
                i = blob.find(data)
                while i >= 0 and len(where) < 4:
                    where.append({"file": name, "offset": f"0x{i:X}"})
                    i = blob.find(data, i + 1)
            parts.append(
                {
                    "command": s.command_address,
                    "vram": f"0x{s.source:05X}",
                    "size": [s.width, s.height],
                    "xy": [s.x, s.y],
                    "found": where,
                }
            )
        report.append(
            {"run": run.name, "frame": "0x" + run.name.split("-")[1], "parts": parts}
        )
        print(
            run.name,
            [
                (p["size"], [w["file"] + "@" + w["offset"] for w in p["found"]])
                for p in parts
            ],
        )
    if args.out:
        args.out.write_text(json.dumps({"runs": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
