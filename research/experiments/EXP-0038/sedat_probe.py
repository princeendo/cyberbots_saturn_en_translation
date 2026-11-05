"""EXP-0038: build a probe image with one glyph of `SE.DAT`'s font copy replaced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/sedat_probe.py OUT

A debug harness; it never ships. ``SE.DAT`` (512 KiB) holds an exact copy of
``KANJI.BIN`` at ``0x40000``-``0x67FFF`` (EXP-0037). This script checks
``SE.DAT``'s SHA-256 against ``references/saturn_jp/iso_listing.json`` and
that the copy equals ``KANJI.BIN``, decodes the copy with ``tools.font.kanji``,
replaces glyph ``GLYPH`` with the solid block of value 14 that ``EXP-0020``
used, re-encodes it into ``OUT/SE.DAT`` (every other byte unchanged), and
builds ``OUT/image/`` with ``tools.disc.patch_image``. ``OUT`` must be under
``build/``. ``KANJI.BIN`` is not changed.

Glyph 535 is the first character of `END.BIN` line 752 (Jin's first ending
box, 408) and is used once in Jin's ending lines.
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
FILES = Path("local/extracted/saturn_jp")
NAME = "SE.DAT;1"
COPY = 0x40000
GLYPH = 535
PROBE = bytes([0xEE]) * kanji.CELL_BYTES


def main(out: Path) -> int:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == NAME)
    data = (FILES / "SE.DAT").read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit("SE.DAT does not match the listing")
    font = (FILES / "KANJI.BIN").read_bytes()
    if data[COPY : COPY + len(font)] != font:
        raise SystemExit("SE.DAT's copy differs from KANJI.BIN")
    cells = kanji.decode(font)
    cells[GLYPH] = PROBE
    edited = data[:COPY] + kanji.encode(cells) + data[COPY + len(font) :]
    changed = [i for i, (a, b) in enumerate(zip(data, edited, strict=True)) if a != b]
    out.mkdir(parents=True, exist_ok=False)
    (out / "SE.DAT").write_bytes(edited)
    (out / "changes.json").write_text(
        json.dumps(
            {
                "file": NAME,
                "glyph": GLYPH,
                "probe": "solid value 14 (0xEE bytes)",
                "bytes_changed": len(changed),
                "first": f"0x{changed[0]:05X}",
                "last": f"0x{changed[-1]:05X}",
                "sha256_before": entry["sha256"],
                "sha256_after": hashlib.sha256(edited).hexdigest(),
            },
            indent=1,
        )
        + "\n"
    )
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
            str(out / "SE.DAT"),
            "--out-dir",
            str(out / "image"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
