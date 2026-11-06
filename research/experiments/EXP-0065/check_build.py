"""EXP-0065: check the names-switch build against LOC-005's.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/check_build.py \\
        build/opt005/a build/opt005/b [--out research/experiments/EXP-0065/build.json]

- **Two builds:** every output file, Track 01 and the ending records
  (``local/opt005/rec-a``, ``rec-b``) identical.
- **Against LOC-005** (``build/loc005/a``): every output the earlier build
  has is equal, except `STG0AS.BIN`, which differs only in the hook-B
  literal; `CYBER.BIN` and `OPDEMO.BIN` differ from the untouched files only
  at the recorded changes.
- **Image:** sectors that differ from LOC-005's Track 01 lie in `CYBER.BIN`,
  `OPDEMO.BIN` or `STG0AS.BIN`, the root directory's last sector (LSN 27)
  or the new files' sectors; all sectors valid; the ISO listing has the two
  new files, equal to the untouched ranges they restore.
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
from tools.text import dialogue, names_switch

TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
LOC005 = Path("build/loc005/a")
RAW, USER = 2352, 2048


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
    report: dict[str, Any] = {}
    ok = True

    outputs = sorted(p.name for p in a.iterdir() if p.is_file())
    differ = [n for n in outputs if sha(a / n) != sha(b / n)]
    ta, tb = sha(a / "image" / TRACK), sha(b / "image" / TRACK)
    ra, rb = Path("local/opt005/rec-a"), Path("local/opt005/rec-b")
    rec_differ = [
        n for n in sorted(p.name for p in ra.iterdir()) if sha(ra / n) != sha(rb / n)
    ]
    report["two_builds"] = {
        "outputs": len(outputs),
        "differing": differ,
        "track01_sha256": ta,
        "track01_equal": ta == tb,
        "records_differing": rec_differ,
    }
    ok &= not differ and ta == tb and not rec_differ

    record = json.loads((a / "names_switch_changes.json").read_text())
    earlier = {}
    for p in sorted(LOC005.iterdir()):
        if not p.is_file() or p.name in ("name_art_changes.json",):
            continue
        if not (a / p.name).exists():
            earlier[p.name] = "missing"
            continue
        if p.name == "STG0AS.BIN":
            new, old = (a / p.name).read_bytes(), p.read_bytes()
            diff = [i for i in range(len(new)) if new[i] != old[i]]
            earlier[p.name] = {"differing_offsets": [hex(i) for i in diff]}
            ok &= bool(diff) and set(diff) <= {0x6C0, 0x6C1, 0x6C2, 0x6C3}
        else:
            same = sha(p) == sha(a / p.name)
            earlier[p.name] = same
            ok &= same
    report["against_loc005"] = earlier

    files = {}
    for name in ("CYBER.BIN", "OPDEMO.BIN"):
        original = bytes(dialogue.checked(name))
        data = (a / name).read_bytes()
        allowed: set[int] = set()
        for c in record["changes"]:
            if c["file"] == name:
                start = int(c["offset"], 16)
                allowed.update(range(start, start + len(bytes.fromhex(c["new"]))))
        diff = [i for i in range(len(data)) if data[i] != original[i]]
        inside = all(i in allowed for i in diff)
        files[name] = {
            "bytes_changed": len(diff),
            "inside_recorded_changes": inside,
            "size_kept": len(data) == len(original),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        ok &= inside and len(data) == len(original)
    report["patched_files"] = files

    listing = {
        f["path"]: f
        for f in json.loads(Path("references/saturn_jp/iso_listing.json").read_text())[
            "files"
        ]
    }
    allowed_sectors = {27}
    for name in ("CYBER.BIN", "OPDEMO.BIN", "STG0AS.BIN"):
        f = listing[f"{name};1"]
        allowed_sectors.update(
            range(f["lsn"], f["lsn"] + (f["size_bytes"] + USER - 1) // USER)
        )
    for p in record["added_files"]:
        allowed_sectors.update(range(p["lsn"], p["lsn"] + p["sectors"]))
    new_track = (a / "image" / TRACK).read_bytes()
    old_track = (LOC005 / "image" / TRACK).read_bytes()
    changed = [
        s
        for s in range(len(new_track) // RAW)
        if new_track[s * RAW : (s + 1) * RAW] != old_track[s * RAW : (s + 1) * RAW]
    ]
    outside = [s for s in changed if s not in allowed_sectors]
    invalid = sector.verify_track(a / "image" / TRACK)
    added = {}
    originals = {n: bytes(dialogue.checked(n)) for n in ("SELECT.VAD", "PL3F_0.BIN")}
    expect = {
        "ZNAMES1.BIN;1": originals["SELECT.VAD"][slice(*names_switch.SELECT_RANGE)],
        "ZNAMES2.BIN;1": originals["PL3F_0.BIN"][slice(*names_switch.VS_RANGE)],
    }
    for p in record["added_files"]:
        data = b"".join(
            new_track[(p["lsn"] + k) * RAW + 16 : (p["lsn"] + k) * RAW + 16 + USER]
            for k in range(p["sectors"])
        )[: p["size_bytes"]]
        added[p["name"]] = {
            "lsn": p["lsn"],
            "size": p["size_bytes"],
            "equals_untouched_range": data == expect[p["name"]],
        }
        ok &= data == expect[p["name"]]
    report["image"] = {
        "loc005_track01_sha256": sha(LOC005 / "image" / TRACK),
        "sectors_changed_vs_loc005": len(changed),
        "changed_outside_expected": outside,
        "invalid_sectors": len(invalid),
        "added_files": added,
        "directory_last_record": record["verification"].get("last_record"),
    }
    ok &= not outside and not invalid
    report["ok"] = bool(ok)
    print(json.dumps(report, indent=1))
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
