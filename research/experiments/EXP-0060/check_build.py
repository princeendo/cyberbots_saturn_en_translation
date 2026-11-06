"""EXP-0060: check the LOC-005 build (M8, boot warnings and Latin name art).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0060/check_build.py \\
        build/loc005/a build/loc005/b [--out research/experiments/EXP-0060/build.json]

Numbers only; exits 1 if a check fails.

- **Two builds:** every output file, Track 01 and the ending records
  (``local/loc005/rec-a``, ``rec-b``) identical.
- **Earlier work unchanged:** every replacement of
  ``data/regression/boot004_boot_warnings.json`` and its prediction,
  change and ending outputs equal; the records equal the committed ones.
- **Name art files:** `SELECT.VAD`, `STG0A.BIN` and `PL3F_0.BIN` differ from
  the untouched files only inside ``name_art_changes.json``'s ranges; the
  bank-63 frame table the build read (`STG0AS.BIN` ``0x1B49C``-``0x1B590``)
  is the same in the built `STG0AS.BIN`; every record any bank-63 part
  points at decodes (type 2), or is not type 2.
- **Image:** against the BOOT-004 Track 01 (``build/boot004/a``), every
  differing sector lies in the three files' extents; all sectors valid.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.disc import sector
from tools.text import dialogue, name_art, pattern_t2

TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
BASE = Path("build/boot004/a/image") / TRACK
REFERENCE = Path("data/regression/boot004_boot_warnings.json")
LISTING = Path("references/saturn_jp/iso_listing.json")
FILES = ("SELECT.VAD", "STG0A.BIN", "PL3F_0.BIN")
RAW = 2352


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    a, b = args.first, args.second
    ok = True
    report: dict[str, Any] = {}

    outputs = sorted(p.name for p in a.iterdir() if p.is_file())
    differ = [n for n in outputs if sha(a / n) != sha(b / n)]
    track_a, track_b = sha(a / "image" / TRACK), sha(b / "image" / TRACK)
    rec_a, rec_b = Path("local/loc005/rec-a"), Path("local/loc005/rec-b")
    recs = sorted(p.name for p in rec_a.iterdir())
    rec_differ = [n for n in recs if sha(rec_a / n) != sha(rec_b / n)]
    report["two_builds"] = {
        "outputs": len(outputs),
        "differing": differ,
        "track01_sha256": track_a,
        "track01_equal": track_a == track_b,
        "records_differing": rec_differ,
    }
    ok &= not differ and track_a == track_b and not rec_differ

    ref = json.loads(REFERENCE.read_text())
    same = {
        iso.split(";")[0]: sha(a / iso.split(";")[0]) == digest
        for iso, digest in ref["replacements"].items()
    }
    committed = {n: sha(rec_a / n) == sha(Path("data/translations") / n) for n in recs}
    report["earlier_unchanged"] = {"files": same, "records_equal_committed": committed}
    ok &= all(same.values()) and all(committed.values())

    ranges = json.loads((a / "name_art_changes.json").read_text())["ranges"]
    files: dict[str, Any] = {}
    for name in FILES:
        original = bytes(dialogue.checked(name))
        data = (a / name).read_bytes()
        diff = [i for i in range(len(data)) if data[i] != original[i]]
        inside = all(
            any(r["file"] == name and r["start"] <= i < r["end"] for r in ranges)
            for i in diff
        )
        files[name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes_changed": len(diff),
            "inside_ranges": inside,
            "size_kept": len(data) == len(original),
        }
        ok &= inside and len(data) == len(original)
    stg_built = (a / "STG0AS.BIN").read_bytes()
    stg_orig = bytes(dialogue.checked("STG0AS.BIN"))
    table_same = stg_built[0x1B49C:0x1B590] == stg_orig[0x1B49C:0x1B590]
    pl = (a / "PL3F_0.BIN").read_bytes()
    decoded = failed = other = 0
    for f in range(1, name_art.VS_FRAMES + 1):
        for p in name_art.frame_parts(
            stg_orig, name_art.VS_FRAME_TABLE, name_art.VS_FRAMES, f
        ):
            w1, w2 = struct.unpack_from(">2H", pl, 6 * p + 2)
            offset = (((w1 & 1) << 16) | w2) * 4
            if pl[offset] >> 4 != 2:
                other += 1
                continue
            try:
                pattern_t2.decode(pl[offset:])
                decoded += 1
            except pattern_t2.FormatError:
                failed += 1
    files["bank63"] = {
        "frame_table_unchanged_in_built_STG0AS": table_same,
        "type2_parts_decoding": decoded,
        "type2_parts_failing": failed,
        "other_type_parts": other,
    }
    ok &= table_same and failed == 0
    report["name_art_files"] = files

    listing = {f["path"]: f for f in json.loads(LISTING.read_text())["files"]}
    extents = []
    for name in FILES:
        f = listing[f"{name};1"]
        extents.append((f["lsn"], f["lsn"] + (f["size_bytes"] + 2047) // 2048))
    new, old = (a / "image" / TRACK).read_bytes(), BASE.read_bytes()
    changed = [
        s
        for s in range(len(new) // RAW)
        if new[s * RAW : (s + 1) * RAW] != old[s * RAW : (s + 1) * RAW]
    ]
    outside = [s for s in changed if not any(lo <= s < hi for lo, hi in extents)]
    invalid = sector.verify_track(a / "image" / TRACK)
    report["image"] = {
        "boot004_track01_sha256": sha(BASE),
        "sectors_changed_vs_boot004": len(changed),
        "changed_outside_the_three_files": outside,
        "sectors": len(new) // RAW,
        "invalid_sectors": len(invalid),
    }
    ok &= not outside and not invalid
    report["ok"] = ok
    print(json.dumps(report, indent=1))
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
