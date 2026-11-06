"""Tests for ``tools.disc.make_patch`` (REL-001), synthetic data only.

Copied into the Cyberbots repository from the XvSF repository,
``tests/unit/test_disc_make_patch.py`` at commit ``e19a152`` (XvSF copied it
from MSHvSF ``tests/unit/test_disc_make_patch.py`` at ``5e8d4ec``). Changed:
the patch-name example and the synthetic disc header use Cyberbots' names
(``references/saturn_jp/README.md``); the header images pass ``--track01``;
added tests for ``reference_track01`` on Cyberbots' regression format and an
end-to-end run of ``main`` on a synthetic image.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.unit.test_patch_image import valid_image
from tools.disc import make_patch, make_ssp
from tools.disc.iso9660 import RAW_SECTOR, SYNC
from tools.disc.make_patch import (
    TRACK01,
    compare_images,
    components,
    decode,
    encode,
    patch_name,
    ra_hash,
    ra_header,
    reference_track01,
)
from tools.disc.patch_image import replace_file

needs_xdelta = pytest.mark.skipif(
    shutil.which("xdelta3") is None, reason="needs xdelta3"
)


def write(directory: Path, files: dict[str, bytes]) -> dict[str, Path]:
    directory.mkdir()
    for name, data in files.items():
        (directory / name).write_bytes(data)
    (directory / "notes.txt").write_text("ignored")
    return components(directory)


def test_compare_images_lists_differing_and_unchanged(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1", "x.cue": b"c"})
    built = write(tmp_path / "b", {"x (Track 01).bin": b"2", "x.cue": b"c"})
    assert compare_images(source, built) == (["x (Track 01).bin"], ["x.cue"])


def test_compare_images_rejects_different_component_sets(tmp_path: Path) -> None:
    source = write(tmp_path / "a", {"x (Track 01).bin": b"1"})
    built = write(tmp_path / "b", {"y (Track 01).bin": b"1"})
    with pytest.raises(ValueError):
        compare_images(source, built)


def test_patch_name_uses_the_track_label() -> None:
    assert patch_name("m8", TRACK01) == "m8.Track01.xdelta"
    assert patch_name("m8", "disc.bin") == "m8.disc.xdelta"


@needs_xdelta
def test_xdelta_round_trip_and_wrong_source(tmp_path: Path) -> None:
    source, target = tmp_path / "s.bin", tmp_path / "t.bin"
    data = bytes(range(256)) * 400
    source.write_bytes(data)
    target.write_bytes(data[:1000] + b"ENGLISH" + data[1007:])
    patch, out = tmp_path / "p.xdelta", tmp_path / "o.bin"
    encode("xdelta3", source, target, patch)
    decode("xdelta3", source, patch, out)
    assert out.read_bytes() == target.read_bytes()
    wrong = tmp_path / "w.bin"
    wrong.write_bytes(bytes(len(data)))
    with pytest.raises(subprocess.CalledProcessError):
        decode("xdelta3", wrong, patch, tmp_path / "w_out.bin")


def mode1_track(*users: bytes) -> bytes:
    """Mode 1/2352 sectors; the header's address bytes are not read here."""
    return b"".join(
        SYNC + b"\x00\x02\x00\x01" + u.ljust(2048, b"\x00") + bytes(RAW_SECTOR - 2064)
        for u in users
    )


# Synthetic: the fields' layout of a Saturn system ID, not the disc's bytes.
HEADER = b"SEGA SEGASATURN SEGA TP T-12    T-1217G   V1.002".ljust(512, b" ")


def test_ra_header_is_sector_0_user_data_only(tmp_path: Path) -> None:
    a, b = tmp_path / "a.bin", tmp_path / "b.bin"
    a.write_bytes(mode1_track(HEADER + b"boot code", b"files"))
    b.write_bytes(mode1_track(HEADER + b"other code", b"english"))
    assert ra_header(a) == HEADER
    assert ra_hash(a) == ra_hash(b) == hashlib.md5(HEADER).hexdigest()


def header_images(tmp_path: Path) -> list[str]:
    """A source and a built image whose disc headers differ, and a manifest."""
    source, built = tmp_path / "source", tmp_path / "built"
    source.mkdir()
    built.mkdir()
    (source / "t (Track 01).bin").write_bytes(mode1_track(HEADER, b"files"))
    (built / "t (Track 01).bin").write_bytes(
        mode1_track(HEADER.replace(b"V1.002", b"V1.003"))
    )
    manifest = tmp_path / "manifest.md"
    digest = hashlib.sha256((source / "t (Track 01).bin").read_bytes()).hexdigest()
    manifest.write_text(digest)
    return [
        *("--source-dir", str(source), "--built-dir", str(built)),
        *("--track01", "t (Track 01).bin", "--manifest", str(manifest)),
        *("--stem", "t", "--out-dir", str(tmp_path / "build" / "release")),
    ]


@needs_xdelta
def test_make_patch_refuses_a_changed_disc_header(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Keep any output inside tmp_path even if the guard ever regresses.
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    with pytest.raises(SystemExit):
        make_patch.main(header_images(tmp_path))
    assert "RetroAchievements" in capsys.readouterr().err


def test_make_ssp_refuses_a_changed_disc_header(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Keep any output inside tmp_path even if the guard ever regresses.
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    if hasattr(make_ssp, "REPO_ROOT"):
        monkeypatch.setattr(make_ssp, "REPO_ROOT", tmp_path)
    with pytest.raises(SystemExit):
        make_ssp.main([*header_images(tmp_path), "--release-version", "0"])
    assert "RetroAchievements" in capsys.readouterr().err


def test_reference_track01_reads_the_regression_format(tmp_path: Path) -> None:
    reference = tmp_path / "ref.json"
    reference.write_text(
        json.dumps({"output_sha256": {TRACK01: "ab" * 32, "x.cue": "cd" * 32}})
    )
    assert reference_track01(reference) == "ab" * 32
    with pytest.raises(ValueError, match="no output_sha256"):
        reference_track01(reference, "other (Track 01).bin")


def synthetic_release(tmp_path: Path) -> list[str]:
    """Source and built images (one changed root file, same CUE) and a manifest."""
    source, built = tmp_path / "source", tmp_path / "built"
    source.mkdir()
    built.mkdir()
    track = "s (Track 01).bin"
    (source / track).write_bytes(valid_image())
    replace_file(source / track, built / track, 20, 5, b"HELLO")
    for folder in (source, built):
        (folder / "s.cue").write_text("FILE")
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        "\n".join(hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir())
    )
    reference = tmp_path / "ref.json"
    target = hashlib.sha256((built / track).read_bytes()).hexdigest()
    reference.write_text(json.dumps({"output_sha256": {track: target}}))
    return [
        *("--source-dir", str(source), "--built-dir", str(built)),
        *("--track01", track, "--manifest", str(manifest)),
        *("--reference", str(reference), "--stem", "t"),
        *("--out-dir", str(tmp_path / "build" / "release")),
    ]


@needs_xdelta
def test_make_patch_end_to_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    assert make_patch.main(synthetic_release(tmp_path)) == 0
    out = tmp_path / "build" / "release"
    record = json.loads((out / "t.json").read_text())
    assert [p["patch"] for p in record["patches"]] == ["t.Track01.xdelta"]
    assert record["patches"][0]["round_trip"] is True
    assert [u["component"] for u in record["unchanged_components"]] == ["s.cue"]
    assert record["ra_md5"] == hashlib.md5(bytes(512)).hexdigest()
    assert sorted(p.name for p in out.iterdir()) == ["t.Track01.xdelta", "t.json"]


def test_make_ssp_end_to_end(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    args = [*synthetic_release(tmp_path), "--release-version", "0.0.1"]
    assert make_ssp.main(args) == 0
    out = tmp_path / "build" / "release"
    record = json.loads((out / "t.ssp.json").read_text())
    assert record["round_trip"] is True
    assert [f["name"] for f in record["files"]] == ["A.BIN"]
    assert sorted(p.name for p in out.iterdir()) == ["t.ssp", "t.ssp.json"]


def test_output_outside_build_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    args = synthetic_release(tmp_path)
    args[-1] = str(tmp_path / "elsewhere")
    with pytest.raises(SystemExit):
        make_ssp.main([*args, "--release-version", "0"])
    assert "must be under" in capsys.readouterr().err


def test_a_wrong_reference_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(make_patch, "REPO_ROOT", tmp_path)
    args = synthetic_release(tmp_path)
    reference = Path(args[args.index("--reference") + 1])
    reference.write_text(json.dumps({"output_sha256": {"s (Track 01).bin": "0"}}))
    with pytest.raises(SystemExit):
        make_ssp.main([*args, "--release-version", "0"])
    assert "does not match reference" in capsys.readouterr().err
