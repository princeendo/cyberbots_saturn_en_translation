"""EXP-0019: build the M2 image, with M1 line 4 changed in ``STG0AS.BIN``.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0019/build.py OUT [--identity]

Reads ``STG0AS.BIN`` as extracted from the untouched data track
(``local/extracted/saturn_jp/``), checks its SHA-256 against
``references/saturn_jp/iso_listing.json`` and the 26 original bytes of Saturn
line 4 at file offset ``0xF09C`` (D-017), writes the edited file to
``OUT/STG0AS.BIN`` and builds ``OUT/image/`` with ``tools.disc.patch_image``
(same size, in place, EDC/ECC regenerated). ``--identity`` writes the file
unchanged, to re-validate the tool on Cyberbots. ``OUT`` must be under
``build/``.
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
EXTRACTED = Path("local/extracted/saturn_jp/STG0AS.BIN")
NAME = "STG0AS.BIN;1"
OFFSET = 0xF09C  # Saturn line 4 (D-017)
ORIGINAL = bytes.fromhex("8e9f82cd83548343837b815b834f95ba82a98145814581458142")
TEST = "あいうえおかきくけこさしす".encode("shift_jis")  # the M1 string (EXP-0017)


def main(out: Path, identity: bool) -> int:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == NAME)
    data = bytearray(EXTRACTED.read_bytes())
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{EXTRACTED} does not match the listing")
    if bytes(data[OFFSET : OFFSET + len(ORIGINAL)]) != ORIGINAL or len(TEST) != len(
        ORIGINAL
    ):
        raise SystemExit("line 4 is not where D-017 puts it")
    if not identity:
        data[OFFSET : OFFSET + len(TEST)] = TEST
    out.mkdir(parents=True, exist_ok=False)
    edited = out / "STG0AS.BIN"
    edited.write_bytes(data)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--identity", action="store_true")
    args = parser.parse_args()
    raise SystemExit(main(args.out, args.identity))
