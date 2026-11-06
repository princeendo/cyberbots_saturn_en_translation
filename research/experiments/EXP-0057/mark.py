"""EXP-0057: a test image marking three name patterns (never ships).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0057/mark.py build/loc002/marked

From the untouched source (``tools.disc.patch_image``):

- `SELECT.VAD` ``0x17A40``-``0x17D3F`` (Jin's select name, the 104 x 16
  part, 832 bytes): every byte ``0x11`` (one solid colour);
- `PL3F_0.BIN`, two compressed type-2 records: Jin's VS name part at
  ``0x4324`` (to ``0x4440``) and Blodia's VS mech part at ``0x5E58`` (to
  ``0x6030``). Only each record's literal stream is filled with ``0x77``
  (from record + 4 + the record's second word to the next record); the
  first two words and the control bytes are kept, so the record still
  decodes, with different pixels.

Predicted: Jin's select name and, on the VS screen, Jin's name and
Blodia's name change; nothing else. Every changed range is written to
``OUT/changes.json`` with its original bytes' hash (rule 12).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image
from tools.text import dialogue

SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
RECORDS = [(0x4324, 0x4440, "Jin's VS name part"), (0x5E58, 0x6030, "Blodia's VS name")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    changes = []
    vad = dialogue.checked("SELECT.VAD")
    start, end = 0x17A40, 0x17A40 + 104 * 16 // 2
    changes.append(
        {
            "file": "SELECT.VAD",
            "start": f"0x{start:05X}",
            "end": f"0x{end:05X}",
            "what": "Jin's select name part",
            "original_sha256": hashlib.sha256(vad[start:end]).hexdigest(),
            "new": "0x11 each",
        }
    )
    vad[start:end] = b"\x11" * (end - start)
    pl = dialogue.checked("PL3F_0.BIN")
    for record, following, what in RECORDS:
        kind = int.from_bytes(pl[record : record + 2], "big") >> 12
        if kind != 2:
            raise SystemExit(f"0x{record:X} is type {kind}, not 2")
        literals = record + 4 + int.from_bytes(pl[record + 2 : record + 4], "big")
        changes.append(
            {
                "file": "PL3F_0.BIN",
                "start": f"0x{literals:05X}",
                "end": f"0x{following:05X}",
                "what": f"{what}: literal stream",
                "original_sha256": hashlib.sha256(pl[literals:following]).hexdigest(),
                "new": "0x77 each",
            }
        )
        pl[literals:following] = b"\x77" * (following - literals)
    (args.out / "SELECT.VAD").write_bytes(vad)
    (args.out / "PL3F_0.BIN").write_bytes(pl)
    (args.out / "changes.json").write_text(json.dumps(changes, indent=1) + "\n")
    return patch_image.main(
        [
            "--source-dir",
            str(SOURCE_DIR),
            "--manifest",
            str(MANIFEST),
            "--track",
            TRACK,
            "--file",
            "SELECT.VAD;1",
            "--data",
            str(args.out / "SELECT.VAD"),
            "--file",
            "PL3F_0.BIN;1",
            "--data",
            str(args.out / "PL3F_0.BIN"),
            "--out-dir",
            str(args.out / "image"),
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
