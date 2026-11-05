"""EXP-0043: erase the QSound notice's Japanese line; a test image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0043/qsound.py \\
        [--image build/end010/qsd] [--out research/experiments/EXP-0043/qsound.json]

Static, plus one test image; numbers only. Applies
``tools.text.ending.erase_qsound_line`` to the untouched `QSD.PIX` and
reports what it changes:
- every changed byte lies in rows 180-190, x 89-300;
- the bitmap's other non-background pixels near the line are kept: the
  logo's edge (x 84-88) and the English line above (row 179 and up);
- rows 179 and 191 inside x 89-300, the line's edges.

With ``--image``, patches the result into ``IMAGE/image`` from the untouched
source (``tools.disc.patch_image``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image
from tools.text import dialogue, ending

W = ending.QSD_WIDTH
BG = ending.QSD_BACKGROUND


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = bytes(dialogue.checked("QSD.PIX"))
    erased, changes = ending.erase_qsound_line(data)
    changed = [i for i, (a, b) in enumerate(zip(data, erased, strict=True)) if a != b]
    rows = sorted({i // W for i in changed})
    cols = sorted({i % W for i in changed})
    region = {r * W + x for r in ending.QSD_ROWS for x in ending.QSD_COLUMNS}
    near = [
        (r, x)
        for r in range(170, 200)
        for x in range(0, 320)
        if data[r * W + x] != BG and r * W + x not in region
    ]
    result = {
        "QSD.PIX": hashlib.sha256(data).hexdigest(),
        "erased": hashlib.sha256(erased).hexdigest(),
        "bytes_changed": len(changed),
        "rows": [rows[0], rows[-1]],
        "columns": [cols[0], cols[-1]],
        "all_inside_region": all(i in region for i in changed),
        "non_background_in_region_after": sum(1 for i in region if erased[i] != BG),
        "kept_non_background_rows_170_199": {
            "logo_edge_x84_88": sum(1 for r, x in near if 84 <= x <= 88),
            "left_of_x84": sum(1 for r, x in near if x < 84),
            "row_179_x89_300": sum(1 for r, x in near if r == 179 and 89 <= x <= 300),
            "rows_191_plus_x89_300": sum(
                1 for r, x in near if r >= 191 and 89 <= x <= 300
            ),
            "rows_170_178_x89_300": sum(
                1 for r, x in near if r <= 178 and 89 <= x <= 300
            ),
        },
        "changes": changes,
    }
    if args.image:
        args.image.mkdir(parents=True, exist_ok=False)
        (args.image / "QSD.PIX").write_bytes(erased)
        code = patch_image.main(
            [
                "--source-dir",
                str(dialogue.SOURCE_DIR),
                "--manifest",
                str(dialogue.MANIFEST),
                "--track",
                dialogue.TRACK,
                "--file",
                "QSD.PIX;1",
                "--data",
                str(args.image / "QSD.PIX"),
                "--out-dir",
                str(args.image / "image"),
            ]
        )
        if code:
            return code
    print(json.dumps({k: v for k, v in result.items() if k != "changes"}))
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
