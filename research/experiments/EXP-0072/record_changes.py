"""EXP-0072: every changed range of the UI-006 build, with hashes (rule 12).

    ./invenv.sh python research/experiments/EXP-0072/record_changes.py \\
        [--build build/ui006/b] [--base build/opt005/a] \\
        [--out research/experiments/EXP-0072/changes.json]

For each file that differs from ``--base`` (the `opt006` image's outputs):
the differing byte runs (merged when under 16 bytes apart), each with its
offset, length, and the SHA-256 of the original and new bytes. The bytes
themselves are not written (they hold game text and art; `AGENTS.md` rule
21). A file the base did not replace is compared with the untouched one;
files new to the disc: size and SHA-256. Also the image's Track 01 hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE = Path("local/extracted/saturn_jp")


def runs(a: bytes, b: bytes, gap: int = 16) -> list[tuple[int, int]]:
    out: list[list[int]] = []
    for i in (i for i in range(len(a)) if a[i] != b[i]):
        if out and i - out[-1][1] <= gap:
            out[-1][1] = i + 1
        else:
            out.append([i, i + 1])
    return [(s, e) for s, e in out]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--build", type=Path, default=Path("build/ui006/b"))
    p.add_argument("--base", type=Path, default=Path("build/opt005/a"))
    p.add_argument(
        "--out", type=Path, default=Path("research/experiments/EXP-0072/changes.json")
    )
    a = p.parse_args()
    report: dict[str, object] = {}
    files: dict[str, object] = {}
    for path in sorted(a.build.iterdir()):
        if not path.is_file() or path.suffix == ".json":
            continue
        new = path.read_bytes()
        old_path = a.base / path.name
        if not old_path.exists():  # not replaced before: the untouched file
            old_path = SOURCE / path.name
        if not old_path.exists():
            files[path.name] = {
                "new_file": True,
                "size": len(new),
                "sha256": hashlib.sha256(new).hexdigest(),
            }
            continue
        old = old_path.read_bytes()
        if old == new:
            continue
        if len(old) != len(new):
            raise SystemExit(f"{path.name}: size changed")
        files[path.name] = {
            "size": len(new),
            "base_sha256": hashlib.sha256(old).hexdigest(),
            "sha256": hashlib.sha256(new).hexdigest(),
            "ranges": [
                {
                    "offset": f"0x{s:05X}",
                    "length": e - s,
                    "original_sha256": hashlib.sha256(old[s:e]).hexdigest(),
                    "new_sha256": hashlib.sha256(new[s:e]).hexdigest(),
                }
                for s, e in runs(old, new)
            ],
        }
    manifest = json.loads((a.build / "image" / "build_manifest.json").read_text())
    report["track01_sha256"] = manifest["output_sha256"][
        "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
    ]
    report["files"] = files
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(
        {
            k: (len(v["ranges"]) if isinstance(v, dict) and "ranges" in v else "new")
            for k, v in files.items()
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
