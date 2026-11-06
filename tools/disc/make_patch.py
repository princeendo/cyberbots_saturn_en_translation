"""Make and verify an xdelta3 (VCDIFF) release patch for a built image (REL-001).

Copied into the Cyberbots repository from the XvSF repository,
``tools/disc/make_patch.py`` at commit ``e19a152`` (XvSF's ``REL-001`` and
``RA-001``; XvSF copied it from MSHvSF ``tools/disc/make_patch.py`` at
``5e8d4ec``), for Cyberbots' ``REL-001``. Changed: the source image folder,
track 01 name and manifest are Cyberbots' and are arguments
(``--source-dir``, ``--track01``, ``--manifest``); ``--reference`` names a
Cyberbots regression file (``data/regression/*.json``) whose
``output_sha256`` holds track 01's hash, in place of XvSF's
``references.json`` list and ``--baseline``; the record also carries the
disc header's RetroAchievements MD5 (``ra_md5``). Notes below about MSHvSF or
XvSF are their history; for Cyberbots every behaviour is at most a
HYPOTHESIS until validated on Cyberbots (``AGENTS.md`` rules 13 and 26).

The patch turns the untouched source image into a built image. Every component
that differs gets its own patch; components that are byte-identical (normally all
audio tracks and the CUE sheet) are listed as unchanged and need no patch.

Safety and reproducibility:

- Source components are only read, and their SHA-256 must appear in the tracked
  source manifest (``references/saturn_jp/README.md``).
- With ``--reference``, the built track 01 must equal that regression
  reference's recorded track 01 hash.
- The built track 01 must keep the source's disc header (``ra_header``), the
  bytes RetroAchievements identifies the game by (XvSF ``RA-001``;
  ``docs/lessons_from_xvsf.md`` lesson 3). The check compares the built
  header with the source's, so no Cyberbots hash is assumed.
- Patches are written under ``build/`` (git-ignored): their bytes include
  game-derived data, which is never committed (``AGENTS.md`` rule 21).
- xdelta3 runs with fixed flags (``XDELTA_ENCODE``): no secondary compressor, so
  any VCDIFF patcher can apply it, no application header, so no local file
  names are stored, and the largest input window. Each patch is encoded twice
  and must be byte-identical, then decoded with ``xdelta3 -d`` and compared
  with the built component.
- The JSON record (hashes, sizes, xdelta3 version, flags) is metadata only and
  may be committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

from tools.disc.iso9660 import Track
from tools.disc.patch_image import REPO_ROOT, load_manifest_hashes, sha256_file

# -W 16 MiB (xdelta3's largest input window; MSHvSF REL-003): later copies of
# repeated new data can copy from earlier output instead of being stored again.
XDELTA_ENCODE = ("-e", "-9", "-S", "none", "-A", "-W", "16777216", "-f")
SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
SOURCE_MANIFEST = Path("references/saturn_jp/README.md")
TRACK01 = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
OUT_DIR = Path("build/release")
# RetroAchievements hashes a Saturn disc as the MD5 of the first 512 bytes of
# track 01's sector 0 (rcheevos ``rc_hash_sega_cd``, ``src/hash/rc_hash_disc.c``
# at ``0aea57b``, as read by XvSF). A patch that changes them makes the game
# unrecognised.
RA_HEADER = 512


def components(directory: Path) -> dict[str, Path]:
    """Image components (BIN and CUE files) by name."""
    return {
        p.name: p
        for p in sorted(directory.iterdir())
        if p.is_file() and p.suffix.lower() in (".bin", ".cue")
    }


def compare_images(
    source: dict[str, Path], built: dict[str, Path]
) -> tuple[list[str], list[str]]:
    """(differing, unchanged) component names; the name sets must match."""
    if set(source) != set(built):
        raise ValueError(f"component names differ: {sorted(set(source) ^ set(built))}")
    differing: list[str] = []
    unchanged: list[str] = []
    for name in sorted(source):
        same = sha256_file(source[name]) == sha256_file(built[name])
        (unchanged if same else differing).append(name)
    return differing, unchanged


def ra_header(track: Path) -> bytes:
    """The first 512 bytes of sector 0's user data: what RetroAchievements hashes."""
    with track.open("rb") as stream:
        return Track(stream, track.stat().st_size).user(0)[:RA_HEADER]


def ra_hash(track: Path) -> str:
    return hashlib.md5(ra_header(track)).hexdigest()


def patch_name(stem: str, component: str) -> str:
    """Patch filename: the release stem plus the component's track label."""
    track = re.search(r"\((Track \d+)\)", component)
    label = track.group(1).replace(" ", "") if track else Path(component).stem
    return f"{stem}.{label}.xdelta"


def xdelta_version(xdelta: str) -> str:
    result = subprocess.run([xdelta, "-V"], capture_output=True, text=True)
    match = re.search(r"Xdelta version (\S+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError("cannot read the xdelta3 version")
    return match.group(1).rstrip(",")


def encode(xdelta: str, source: Path, target: Path, out: Path) -> None:
    subprocess.run(
        [xdelta, *XDELTA_ENCODE, "-s", str(source), str(target), str(out)],
        check=True,
    )


def decode(xdelta: str, source: Path, patch: Path, out: Path) -> None:
    subprocess.run(
        [xdelta, "-d", "-f", "-s", str(source), str(patch), str(out)], check=True
    )


def reference_track01(reference: Path, track01: str = TRACK01) -> str:
    """Track 01's SHA-256 in a Cyberbots regression file's ``output_sha256``."""
    outputs = json.loads(reference.read_text()).get("output_sha256", {})
    if track01 not in outputs:
        raise ValueError(f"{reference} records no output_sha256 for {track01!r}")
    return str(outputs[track01])


def check_inputs(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> tuple[dict[str, Path], dict[str, Path], list[str], list[str]]:
    """The checks ``make_patch`` and ``make_ssp`` share; exits on a failure.

    Returns (source components, built components, differing, unchanged).
    """
    source, built = components(args.source_dir), components(args.built_dir)
    if args.track01 not in source:
        parser.error(f"no {args.track01!r} in {args.source_dir}")
    known = load_manifest_hashes(args.manifest)
    unknown = [n for n, p in source.items() if sha256_file(p) not in known]
    if unknown:
        parser.error(f"source components not in the manifest: {unknown}")
    try:
        differing, unchanged = compare_images(source, built)
    except ValueError as error:
        parser.error(str(error))
    if ra_header(built[args.track01]) != ra_header(source[args.track01]):
        parser.error("built track 01 changes the disc header RetroAchievements hashes")
    if args.reference:
        expected = reference_track01(args.reference, args.track01)
        if sha256_file(built[args.track01]) != expected:
            parser.error(f"built track 01 does not match reference {args.reference}")
    return source, built, differing, unchanged


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--built-dir", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--track01", default=TRACK01, help="track 01's file name")
    parser.add_argument("--manifest", type=Path, default=SOURCE_MANIFEST)
    parser.add_argument(
        "--reference",
        type=Path,
        help="regression file (data/regression/*.json) the build must match",
    )
    parser.add_argument("--stem", required=True, help="patch filename stem")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--record", type=Path, help="also write the JSON record here")


def checked_out_dir(parser: argparse.ArgumentParser, out_dir: Path) -> Path:
    """``out_dir`` resolved; it must be under the repository's ``build/``."""
    resolved = out_dir.resolve()
    build_root = (REPO_ROOT / "build").resolve()
    if build_root not in resolved.parents and resolved != build_root:
        parser.error(f"output must be under {build_root}")
    return resolved


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    add_common_arguments(parser)
    parser.add_argument("--xdelta", default="xdelta3")
    args = parser.parse_args(argv)

    out_dir = checked_out_dir(parser, args.out_dir)
    xdelta = shutil.which(args.xdelta)
    if xdelta is None:
        parser.error(f"{args.xdelta} not found; install xdelta3")

    source, built, differing, unchanged = check_inputs(parser, args)
    if any(not n.lower().endswith(".bin") for n in differing):
        parser.error(f"only BIN tracks may differ: {differing}")

    out_dir.mkdir(parents=True, exist_ok=True)
    patches = []
    for name in differing:
        patch = out_dir / patch_name(args.stem, name)
        again = out_dir / (patch.name + ".again")
        check = out_dir / (patch.name + ".decoded")
        encode(xdelta, source[name], built[name], patch)
        encode(xdelta, source[name], built[name], again)
        deterministic = patch.read_bytes() == again.read_bytes()
        again.unlink()
        decode(xdelta, source[name], patch, check)
        round_trip = sha256_file(check) == sha256_file(built[name])
        check.unlink()
        if not (deterministic and round_trip):
            parser.error(f"{patch.name}: {deterministic=} {round_trip=}")
        patches.append(
            {
                "component": name,
                "patch": patch.name,
                "patch_size": patch.stat().st_size,
                "patch_sha256": sha256_file(patch),
                "source_size": source[name].stat().st_size,
                "source_sha256": sha256_file(source[name]),
                "target_sha256": sha256_file(built[name]),
                "deterministic": deterministic,
                "round_trip": round_trip,
            }
        )
    record = {
        "tool": "tools.disc.make_patch",
        "reference": str(args.reference) if args.reference else None,
        "ra_md5": ra_hash(source[args.track01]),
        "xdelta3_version": xdelta_version(xdelta),
        "xdelta3_encode_flags": " ".join(XDELTA_ENCODE),
        "patches": patches,
        "unchanged_components": [
            {"component": n, "sha256": sha256_file(source[n])} for n in unchanged
        ],
    }
    text = json.dumps(record, indent=1) + "\n"
    (out_dir / f"{args.stem}.json").write_text(text)
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        args.record.write_text(text)
    print(
        json.dumps(
            [{k: p[k] for k in ("patch", "patch_size", "round_trip")} for p in patches]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
