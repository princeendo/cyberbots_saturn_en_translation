"""EXP-0045: check the END-010 build (Jin's ending with the M5 roster).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0045/check_build.py \\
        build/end010/jin build/end010/jin-again

Prints JSON; exits 1 if a check fails. It reports:

- **Two builds:** every output file of the two builds (``changes.json``,
  ``prediction.json``, the ending's files, each replacement file, the image
  manifest and Track 01) and their records (``OUT/../NAME-record.json``) are
  identical.
- **M5 unchanged:** the story files, ``prediction.json`` and
  ``changes.json`` have the hashes of ``data/regression/re008_roster.json``.
- **Ending files:** every byte of `END.BIN`, `SE.DAT`, `KEND_1.BIN` and
  `QSD.PIX` that differs from the untouched file lies in a range of
  ``ending_changes.json``; the counts are reported. `SE.DAT`'s other
  regions (outside ``0x40000``-``0x67FFF``) are unchanged.
- **Image:** the files the image replaced, and the source hashes in the
  build manifest equal the tracked ones.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.text import ending

SOURCE = Path("local/extracted/saturn_jp")
REFERENCE = Path("data/regression/re008_roster.json")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
ENDING_FILES = ("END.BIN", "SE.DAT", "KEND_1.BIN", "QSD.PIX")


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main(first: Path, second: Path) -> int:
    report: dict[str, object] = {}
    ok = True
    names = sorted(
        p.name for p in first.iterdir() if p.is_file() and p.suffix != ".log"
    )
    same = {n: sha(first / n) == sha(second / n) for n in names}
    for side in ("image/build_manifest.json", f"image/{TRACK}"):
        same[side] = sha(first / side) == sha(second / side)
    rec1 = first.parent / f"{first.name}-record.json"
    rec2 = second.parent / f"{second.name}-record.json"
    same["record (no path)"] = (
        json.loads(rec1.read_text())["boxes"] == json.loads(rec2.read_text())["boxes"]
    )
    report["two_builds_identical"] = same
    ok &= all(same.values())

    ref = json.loads(REFERENCE.read_text())
    m5 = {
        f: sha(first / f) == ref["replacements"][f + ";1"]
        for f in ("STG0AS.BIN", "KANJI.BIN", "VICTORY.BIN")
    }
    m5["prediction.json"] = sha(first / "prediction.json") == ref["prediction_sha256"]
    m5["changes.json"] = sha(first / "changes.json") == ref["changes_sha256"]
    report["m5_unchanged"] = m5
    ok &= all(m5.values())

    ranges = json.loads((first / "ending_changes.json").read_text())["ranges"]
    files: dict[str, object] = {}
    for name in ENDING_FILES:
        old, new = (SOURCE / name).read_bytes(), (first / name).read_bytes()
        mine = [(r["start"], r["end"]) for r in ranges if r["file"] == name]
        diff = [i for i, (a, b) in enumerate(zip(old, new, strict=True)) if a != b]
        outside = [i for i in diff if not any(s <= i < e for s, e in mine)]
        files[name] = {
            "size_equal": len(old) == len(new),
            "bytes_changed": len(diff),
            "ranges": len(mine),
            "outside_ranges": len(outside),
        }
        ok &= not outside and len(old) == len(new)
    se_old, se_new = (SOURCE / "SE.DAT").read_bytes(), (first / "SE.DAT").read_bytes()
    files["SE.DAT outside the font copy unchanged"] = (
        se_old[: ending.FONT_START] == se_new[: ending.FONT_START]
        and se_old[ending.FONT_END :] == se_new[ending.FONT_END :]
    )
    report["ending_files"] = files

    manifest = json.loads((first / "image/build_manifest.json").read_text())
    report["image"] = {
        "replaced": sorted(f["file"] for f in manifest["files"]),
        "changed_sectors": manifest["changed_sectors"],
        "track_01_sha256": sha(first / f"image/{TRACK}"),
        "source_track_01_sha256": manifest["source_sha256"].get(TRACK),
    }
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
