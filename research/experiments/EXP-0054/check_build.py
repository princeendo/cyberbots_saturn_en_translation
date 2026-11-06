"""EXP-0054: check the BOOT-004 build (M8 plus the English boot warnings).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0054/check_build.py \\
        build/boot004/a build/boot004/b \\
        [--out research/experiments/EXP-0054/build.json]

Numbers only; exits 1 if a check fails.

- **Two builds:** every output file of the two builds, Track 01, and the
  ending records written to ``local/boot004/rec-a`` and ``rec-b`` are
  identical.
- **M8 unchanged:** the seven M8 replacements, ``prediction.json``,
  ``changes.json`` and the ending outputs have the hashes of
  ``data/regression/end023_roster_endings.json``; the records equal the
  committed ``data/translations/*_ending.json``.
- **Pictures:** each ``WARNINGn.PIX`` passes ``boot_warnings.check`` against
  the untouched file, and its changed bytes lie in its range in
  ``boot_changes.json``.
- **Image:** against the M8 Track 01 (``build/end023/m8``), every differing
  sector lies inside one of the five pictures' extents (ISO listing), and
  every sector of the new Track 01 has valid EDC/ECC.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.disc import sector
from tools.text import boot_warnings, dialogue

TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
M8 = Path("build/end023/m8/image") / TRACK
REFERENCE = Path("data/regression/end023_roster_endings.json")
LISTING = Path("references/saturn_jp/iso_listing.json")
RAW = 2352
NAMES = [f"WARNING{n}.PIX" for n in range(5)]


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
    recs = sorted(p.name for p in Path("local/boot004/rec-a").iterdir())
    rec_differ = [
        n
        for n in recs
        if sha(Path("local/boot004/rec-a") / n) != sha(Path("local/boot004/rec-b") / n)
    ]
    report["two_builds"] = {
        "outputs": len(outputs),
        "differing": differ,
        "track01_sha256": track_a,
        "track01_equal": track_a == track_b,
        "records_differing": rec_differ,
    }
    ok &= not differ and track_a == track_b and not rec_differ

    ref = json.loads(REFERENCE.read_text())
    m8 = {
        name.split(";")[0]: sha(a / name.split(";")[0]) == digest
        for name, digest in ref["replacements"].items()
    }
    for key, file in (
        ("prediction_sha256", "prediction.json"),
        ("changes_sha256", "changes.json"),
        ("ending_prediction_sha256", "ending_prediction.json"),
        ("ending_changes_sha256", "ending_changes.json"),
        ("ending_timing_sha256", "ending_timing.json"),
    ):
        m8[file] = sha(a / file) == ref[key]
    committed = {
        n: sha(Path("local/boot004/rec-a") / n) == sha(Path("data/translations") / n)
        for n in recs
    }
    report["m8_unchanged"] = {"files": m8, "records_equal_committed": committed}
    ok &= all(m8.values()) and all(committed.values())

    changes = {
        r["file"]: r
        for r in json.loads((a / "boot_changes.json").read_text())["ranges"]
    }
    pictures: dict[str, Any] = {}
    for name in NAMES:
        original = bytes(dialogue.checked(name))
        data = (a / name).read_bytes()
        boot_warnings.check(name, original, data)
        r = changes[name]
        diff = [i for i in range(len(data)) if data[i] != original[i]]
        inside = all(r["start"] <= i < r["end"] for i in diff)
        pictures[name] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes_changed": len(diff),
            "inside_range": inside,
            "recorded": r["bytes_changed"] == len(diff)
            and r["new_sha256"] == hashlib.sha256(data).hexdigest(),
        }
        ok &= inside and pictures[name]["recorded"]
    report["pictures"] = pictures

    listing = {f["path"]: f for f in json.loads(LISTING.read_text())["files"]}
    extents = []
    for name in NAMES:
        f = listing[f"{name};1"]
        extents.append((f["lsn"], f["lsn"] + (f["size_bytes"] + 2047) // 2048))
    new, old = (a / "image" / TRACK).read_bytes(), M8.read_bytes()
    changed = [
        s
        for s in range(len(new) // RAW)
        if new[s * RAW : (s + 1) * RAW] != old[s * RAW : (s + 1) * RAW]
    ]
    outside = [s for s in changed if not any(lo <= s < hi for lo, hi in extents)]
    invalid = sector.verify_track(a / "image" / TRACK)
    report["image"] = {
        "m8_track01_sha256": sha(M8),
        "sectors_changed_vs_m8": len(changed),
        "changed_outside_pictures": outside,
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
