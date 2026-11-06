"""Tests for ``tools.release.make_zips`` and ``check_zips`` (REL-001).

New for Cyberbots: XvSF's ``make_zips.py`` and ``check_zips.sh``
(``research/experiments/EXP-0071/`` at ``9cb01ad``) had no tests. Synthetic
data only: a synthetic ISO 9660 track, its patches made by ``make_patch`` and
``make_ssp``, and hand-written records.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pytest

from tests.unit.test_patch_image import valid_image
from tools.disc.make_patch import encode
from tools.disc.make_ssp import build_ssp, changed_files, entries
from tools.disc.patch_image import replace_file
from tools.release import check_zips, make_zips
from tools.release.make_zips import Release, Variant

META = {
    "Name": "Test",
    "Author": "Someone",
    "URL": "https://example.invalid",
    "Version": "0.0.1",
    "Description": "synthetic",
    "Contact": "https://example.invalid/issues",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def release_tree(tmp_path: Path, xdelta: bool = True) -> tuple[Path, Path, Path]:
    """(source track, records folder, patches root) with one variant ``v``."""
    source, built = tmp_path / "source.bin", tmp_path / "built.bin"
    source.write_bytes(valid_image())
    replace_file(source, built, 20, 5, b"HELLO")
    records, patches = tmp_path / "records", tmp_path / "patches"
    (patches / "b").mkdir(parents=True)
    records.mkdir()
    xpatch = patches / "b" / "v.Track01.xdelta"
    if xdelta:
        encode("xdelta3", source, built, xpatch)
    else:
        xpatch.write_bytes(b"not a real patch")
    spatch = patches / "b" / "v.ssp"
    spatch.write_bytes(build_ssp(changed_files(source, built), entries(source), META))
    common = {
        "source_sha256": sha(source.read_bytes()),
        "target_sha256": sha(built.read_bytes()),
    }
    (records / "v.json").write_text(
        json.dumps(
            {
                "patches": [
                    {
                        "patch": xpatch.name,
                        "patch_size": xpatch.stat().st_size,
                        "patch_sha256": sha(xpatch.read_bytes()),
                        **common,
                    }
                ]
            }
        )
    )
    (records / "v.ssp.json").write_text(
        json.dumps(
            {
                "patch": spatch.name,
                "patch_size": spatch.stat().st_size,
                "patch_sha256": sha(spatch.read_bytes()),
                **common,
            }
        )
    )
    return source, records, patches


def test_zips_are_reproducible_and_name_cyberbots(tmp_path: Path) -> None:
    _, records, patches = release_tree(tmp_path, xdelta=False)
    release = Release("0.0.1")
    variants = [Variant("v", "b", "One image")]
    first = make_zips.make_zips(release, variants, tmp_path / "a", records, patches)
    again = make_zips.make_zips(release, variants, tmp_path / "b", records, patches)
    assert [p.name for p in first] == [
        "cyberbots_saturn_en_0.0.1_xdelta.zip",
        "cyberbots_saturn_en_0.0.1_ssp.zip",
    ]
    assert [p.read_bytes() for p in first] == [p.read_bytes() for p in again]
    bundle = zipfile.ZipFile(first[0])
    assert bundle.namelist() == ["README.txt", "v.Track01.xdelta"]
    assert {i.date_time for i in bundle.infolist()} == {(1980, 1, 1, 0, 0, 0)}
    text = bundle.read("README.txt").decode()
    assert "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin" in text
    assert "keep the other tracks" in text
    assert "X-Men" not in text


def test_a_size_mismatch_is_refused(tmp_path: Path) -> None:
    _, records, patches = release_tree(tmp_path, xdelta=False)
    (patches / "b" / "v.ssp").write_bytes(b"short")
    with pytest.raises(ValueError, match="size differs"):
        make_zips.make_zips(
            Release("0"), [Variant("v", "b", "x")], tmp_path / "z", records, patches
        )


def test_more_than_one_xdelta_patch_is_refused(tmp_path: Path) -> None:
    _, records, patches = release_tree(tmp_path, xdelta=False)
    record = json.loads((records / "v.json").read_text())
    record["patches"].append(record["patches"][0])
    (records / "v.json").write_text(json.dumps(record))
    with pytest.raises(ValueError, match="expected track 01"):
        make_zips.make_zips(
            Release("0"), [Variant("v", "b", "x")], tmp_path / "z", records, patches
        )


def test_make_zips_refuses_output_outside_build(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        make_zips.main(["0", str(tmp_path / "z"), "--variant", "v", "b", "x"])
    assert "must be under" in capsys.readouterr().err


@pytest.mark.skipif(shutil.which("xdelta3") is None, reason="needs xdelta3")
def test_check_zips_applies_every_patch(tmp_path: Path) -> None:
    source, records, patches = release_tree(tmp_path)
    zips = tmp_path / "zips"
    make_zips.make_zips(
        Release("0.0.1"), [Variant("v", "b", "x")], zips, records, patches
    )
    target = json.loads((records / "v.json").read_text())["patches"][0]
    results = check_zips.check_zips(zips, "0.0.1", source, tmp_path / "work")
    assert results == [
        ("v.Track01.xdelta", target["target_sha256"]),
        ("v.ssp", target["target_sha256"]),
    ]
    assert not (tmp_path / "work" / "out.bin").exists()


def test_check_zips_refuses_a_work_folder_outside_build_or_local(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        check_zips.main(["0", str(tmp_path), str(tmp_path / "work")])
    assert "work folder must be under" in capsys.readouterr().err
