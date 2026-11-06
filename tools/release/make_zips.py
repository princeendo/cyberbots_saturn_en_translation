"""Zip the release patches, one zip per format, each with a readme (REL-001).

Copied into the Cyberbots repository from the XvSF repository,
``research/experiments/EXP-0071/make_zips.py`` at commit ``9cb01ad`` (XvSF's
``REL-001``; XvSF copied it from MSHvSF
``research/experiments/EXP-0102/make_zips.py`` at ``7d4c587``, its
``REL-004``), and promoted from an experiment script to a tool. Changed: the
script's module-level constants (XvSF's one ``name_toggle`` variant, track
name, repository, zip names, readme title and the fixed timestamp) are
arguments with Cyberbots defaults; the readme no longer names a track range
("keep the other tracks"); a record with more than one xdelta patch is
refused instead of silently using the first. For Cyberbots every behaviour is
at most a HYPOTHESIS until validated on Cyberbots (``AGENTS.md`` rules 13 and
26).

Reads the release records (``make_patch``'s ``STEM.json`` and ``make_ssp``'s
``STEM.ssp.json``, metadata that may be committed) for hashes, and the built
patches from ``build/release/BUILD/``. Zip members get a fixed timestamp, so
the zips are reproducible. The zips hold game-derived patches: they go under
``build/`` and are published only as GitHub Release assets, never committed
(``AGENTS.md`` rule 21).

Run from the repository root, for example:

    ./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0 \\
        --variant STEM BUILD "One-line label"
"""

from __future__ import annotations

import argparse
import datetime
import json
import zipfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc.make_patch import TRACK01
from tools.disc.make_ssp import IMAGE, URL
from tools.disc.patch_image import REPO_ROOT

DateTime = tuple[int, int, int, int, int, int]

KINDS = ("xdelta", "ssp")
PREFIX = "cyberbots_saturn_en"
TITLE = "Cyberbots: Fullmetal Madness (Saturn) English"
RECORDS_DIR = Path("release")
PATCHES_DIR = Path("build/release")
# The ZIP format's earliest date, as make_ssp's ZIP_TIME; XvSF used its own
# release date.
DATE = "1980-01-01"
APPLY = {
    "xdelta": [
        'xdelta3 -d -s "{track01}" \\',
        '  <patch>.Track01.xdelta "Track 01 patched.bin"',
    ],
    "ssp": [
        'saturn-patcher <patch>.ssp "Track 01 patched.bin"',
        "(saturn-patcher-egui). The official Sega Saturn Patcher rebuilds the",
        "disc instead; see the full instructions.",
    ],
}


@dataclass(frozen=True)
class Variant:
    stem: str  # record stem: RECORDS/STEM.json and RECORDS/STEM.ssp.json
    build: str  # patch folder under the patches root
    label: str  # one line in the readme


@dataclass(frozen=True)
class Release:
    version: str
    title: str = TITLE
    image: str = IMAGE
    track01: str = TRACK01
    repo: str = URL
    prefix: str = PREFIX

    def zip_name(self, kind: str) -> str:
        return f"{self.prefix}_{self.version}_{kind}.zip"


def stamp(date: str) -> DateTime:
    day = datetime.date.fromisoformat(date)
    if day.year < 1980:
        raise ValueError("ZIP dates start in 1980")
    return (day.year, day.month, day.day, 0, 0, 0)


def add(bundle: zipfile.ZipFile, name: str, data: bytes, when: DateTime) -> None:
    info = zipfile.ZipInfo(name, when)
    info.compress_type = zipfile.ZIP_DEFLATED
    bundle.writestr(info, data)


def readme(release: Release, kind: str, rows: Sequence[str], source: str) -> str:
    return "\n".join(
        [
            f"{release.title} {release.version}",
            f"({kind} patches)",
            "",
            f'For the Japanese Saturn image "{release.image}".',
            "Only track 01 changes; keep the other tracks and the CUE sheet.",
            "",
            "Untouched track 01 SHA-256:",
            f"  {source}",
            "",
            *rows,
            "Apply:",
            *(f"  {line.format(track01=release.track01)}" for line in APPLY[kind]),
            "Then put the patched file in place of track 01, under the same name.",
            "",
            "Full instructions, the change list and known limits:",
            f"  {release.repo}/blob/main/release/README.md",
            "",
        ]
    )


def patch_record(records: Path, stem: str, kind: str) -> dict[str, object]:
    """The one track 01 patch a variant's record describes, for ``kind``."""
    suffix = ".ssp.json" if kind == "ssp" else ".json"
    record = json.loads((records / f"{stem}{suffix}").read_text())
    if kind == "ssp":
        return dict(record)
    patches = record["patches"]
    if len(patches) != 1:
        raise ValueError(f"{stem}.json has {len(patches)} patches; expected track 01")
    return dict(patches[0])


def make_zips(
    release: Release,
    variants: Sequence[Variant],
    out: Path,
    records: Path = RECORDS_DIR,
    patches: Path = PATCHES_DIR,
    date: str = DATE,
) -> list[Path]:
    """Write one zip per kind under ``out``; returns their paths."""
    when = stamp(date)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for kind in KINDS:
        rows: list[str] = []
        files: list[Path] = []
        sources: set[str] = set()
        for variant in variants:
            patch = patch_record(records, variant.stem, kind)
            sources.add(str(patch["source_sha256"]))
            path = patches / variant.build / str(patch["patch"])
            if path.stat().st_size != patch["patch_size"]:
                raise ValueError(f"{path}: size differs from its record")
            rows += [
                variant.label,
                f"  {patch['patch']} ({patch['patch_size']:,} bytes)",
                f"  file SHA-256:     {patch['patch_sha256']}",
                f"  patched track 01: {patch['target_sha256']}",
                "",
            ]
            files.append(path)
        if len(sources) != 1:
            raise ValueError(f"the variants' source tracks differ: {sorted(sources)}")
        name = out / release.zip_name(kind)
        with zipfile.ZipFile(name, "w") as bundle:
            text = readme(release, kind, rows, sources.pop())
            add(bundle, "README.txt", text.encode(), when)
            for path in files:
                add(bundle, path.name, path.read_bytes(), when)
        written.append(name)
    return written


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("version", help="release version, e.g. 0.1.0")
    parser.add_argument("out", type=Path, help="output folder (under build/)")
    parser.add_argument(
        "--variant",
        nargs=3,
        action="append",
        required=True,
        metavar=("STEM", "BUILD", "LABEL"),
        help="record stem, patch folder under --patches, readme label; repeatable",
    )
    parser.add_argument("--records", type=Path, default=RECORDS_DIR)
    parser.add_argument("--patches", type=Path, default=PATCHES_DIR)
    parser.add_argument("--date", default=DATE, help="zip member date, YYYY-MM-DD")
    parser.add_argument("--title", default=TITLE)
    parser.add_argument("--image", default=IMAGE, help="source image named in readme")
    parser.add_argument("--track01", default=TRACK01)
    parser.add_argument("--repo", default=URL)
    parser.add_argument("--prefix", default=PREFIX, help="zip file name prefix")
    args = parser.parse_args(argv)
    build_root = (REPO_ROOT / "build").resolve()
    if build_root not in args.out.resolve().parents:
        parser.error(f"output must be under {build_root}")
    release = Release(
        args.version, args.title, args.image, args.track01, args.repo, args.prefix
    )
    variants = [Variant(*v) for v in args.variant]
    for name in make_zips(
        release, variants, args.out, args.records, args.patches, args.date
    ):
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
