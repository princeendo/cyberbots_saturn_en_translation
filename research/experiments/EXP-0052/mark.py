"""EXP-0052: a test image with a marker in each WARNINGn.PIX (never ships).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0052/mark.py build/boot002/marked

From the untouched source (``tools.disc.patch_image``), each picture n gets,
in file rows and columns (screen row = file row + 8, D-049 when confirmed):

- an ID block: rows 0-3, columns 16n to 16n+15, value 14 (cyan);
- a bottom band: rows 228-231, columns 0-351, value 12 (yellow), predicted
  visible on screen rows 236-239;
- hidden marks, value 9 (red), predicted never visible: rows 232 to the
  file's last row, columns 0-351; rows 100-103, columns 352-511.

Every changed range is written to ``OUT/changes.json`` with its original
and new bytes (rule 12).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image

SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
LISTING = Path("references/saturn_jp/iso_listing.json")
EXTRACTED = Path("local/extracted/saturn_jp")
WIDTH, SHOWN = 512, 352
ID, BAND, HIDDEN = 14, 12, 9


def marks(n: int, rows: int) -> list[tuple[int, int, int, int, int]]:
    """(first row, last row, first column, last column, value)."""
    return [
        (0, 3, 16 * n, 16 * n + 15, ID),
        (228, 231, 0, SHOWN - 1, BAND),
        (232, rows - 1, 0, SHOWN - 1, HIDDEN),
        (100, 103, SHOWN, WIDTH - 1, HIDDEN),
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    listing = {
        f["path"].split(";")[0]: f for f in json.loads(LISTING.read_text())["files"]
    }
    args.out.mkdir(parents=True, exist_ok=False)
    changes = []
    argv = [
        "--source-dir",
        str(SOURCE_DIR),
        "--manifest",
        str(MANIFEST),
        "--track",
        TRACK,
        "--out-dir",
        str(args.out / "image"),
    ]
    for n in range(5):
        name = f"WARNING{n}.PIX"
        data = bytearray((EXTRACTED / name).read_bytes())
        if hashlib.sha256(data).hexdigest() != listing[name]["sha256"]:
            raise SystemExit(f"{name} differs from the listing")
        rows = len(data) // WIDTH
        for r0, r1, c0, c1, value in marks(n, rows):
            for r in range(r0, r1 + 1):
                start = r * WIDTH + c0
                original = bytes(data[start : start + c1 - c0 + 1])
                data[start : start + c1 - c0 + 1] = bytes([value]) * (c1 - c0 + 1)
                changes.append(
                    {
                        "file": name,
                        "offset": start,
                        "length": c1 - c0 + 1,
                        "original_sha256": hashlib.sha256(original).hexdigest(),
                        "original_values": sorted(set(original)),
                        "new_value": value,
                    }
                )
        path = args.out / name
        path.write_bytes(data)
        argv += ["--file", f"{name};1", "--data", str(path)]
    (args.out / "changes.json").write_text(json.dumps(changes, indent=1) + "\n")
    return patch_image.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
