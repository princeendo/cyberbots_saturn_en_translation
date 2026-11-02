"""EXP-0020: build a probe image with one glyph of ``KANJI.BIN`` replaced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0020/probe.py OUT

Reads ``KANJI.BIN`` as extracted from the untouched data track
(``local/extracted/saturn_jp/``), checks its SHA-256 against
``references/saturn_jp/iso_listing.json``, decodes it with
``tools.font.kanji``, and replaces glyph 600 (the first character of the M1
box, Shift-JIS ``0x8E9F``, `EXP-0020`) with a solid block of value 14. It
re-encodes the file to ``OUT/KANJI.BIN`` and builds ``OUT/image/`` with
``tools.disc.patch_image``. ``OUT`` must be under ``build/``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image
from tools.font import kanji

SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
LISTING = Path("references/saturn_jp/iso_listing.json")
EXTRACTED = Path("local/extracted/saturn_jp/KANJI.BIN")
NAME = "KANJI.BIN;1"
GLYPH = 600
PROBE = bytes([0xEE]) * kanji.CELL_BYTES


def main(out: Path) -> int:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == NAME)
    data = EXTRACTED.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{EXTRACTED} does not match the listing")
    cells = kanji.decode(data)
    cells[GLYPH] = PROBE
    out.mkdir(parents=True, exist_ok=False)
    edited = out / "KANJI.BIN"
    edited.write_bytes(kanji.encode(cells))
    return patch_image.main(
        [
            "--source-dir",
            str(SOURCE_DIR),
            "--manifest",
            str(MANIFEST),
            "--track",
            TRACK,
            "--file",
            NAME,
            "--data",
            str(edited),
            "--out-dir",
            str(out / "image"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
