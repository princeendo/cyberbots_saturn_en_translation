"""Identify arcade zips and loose ROM files by SHA-1 against `mame -listxml`.

Member names are ignored: a file matches a MAME ROM entry by SHA-1 alone, so
renamed members and older set names are still identified. A zip is reported as a
set when it holds every ROM that set owns (entries without a `merge` attribute,
which a split set keeps in its own zip). Files are read only.

Copied into the Cyberbots repository from the XvSF repository,
``tools/reference/listxml_match.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Sequence
from pathlib import Path


def parse_listxml(text: str) -> dict[str, dict[str, object]]:
    """Return {machine: {"title", "cloneof", "roms": [{name, sha1, merge}]}}."""
    machines: dict[str, dict[str, object]] = {}
    for machine in ET.fromstring(text).iter("machine"):
        roms = [
            {
                "name": rom.get("name", ""),
                "sha1": rom.get("sha1", ""),
                "merge": rom.get("merge", ""),
            }
            for rom in machine.iter("rom")
            if rom.get("sha1")
        ]
        machines[machine.get("name", "")] = {
            "title": machine.findtext("description", ""),
            "cloneof": machine.get("cloneof", ""),
            "roms": roms,
        }
    return machines


def file_sha1s(path: Path) -> dict[str, str]:
    """Return {member or file name: SHA-1} for a zip or a loose file."""
    if not zipfile.is_zipfile(path):
        return {path.name: hashlib.sha1(path.read_bytes()).hexdigest()}
    with zipfile.ZipFile(path) as bundle:
        return {
            info.filename: hashlib.sha1(bundle.read(info)).hexdigest()
            for info in bundle.infolist()
            if not info.is_dir()
        }


def identify(path: Path, machines: dict[str, dict[str, object]]) -> dict[str, object]:
    """Match one file's contents against every machine's ROM entries."""
    members = file_sha1s(path)
    held = set(members.values())
    member_matches = {}
    for member, sha1 in members.items():
        hits = sorted(
            f"{name}:{rom['name']}"
            for name, machine in machines.items()
            for rom in machine["roms"]  # type: ignore[attr-defined]
            if rom["sha1"] == sha1
        )
        member_matches[member] = {"sha1": sha1, "matches": hits}
    sets = sorted(
        name
        for name, machine in machines.items()
        if (own := [r for r in machine["roms"] if not r["merge"]])  # type: ignore[attr-defined]
        and all(r["sha1"] in held for r in own if not r["name"].endswith(".key"))
        and any(not r["name"].endswith(".key") for r in own)
    )
    return {
        "file": path.name,
        "size": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "complete_sets": sets,
        "titles": {name: machines[name]["title"] for name in sets},
        "members": member_matches,
        "unmatched": sorted(m for m, v in member_matches.items() if not v["matches"]),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listxml", type=Path, required=True)
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args(argv)
    listxml = args.listxml.read_bytes()
    machines = parse_listxml(listxml.decode("utf-8"))
    report = {
        "listxml_sha256": hashlib.sha256(listxml).hexdigest(),
        "files": [identify(path, machines) for path in args.files],
    }
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
