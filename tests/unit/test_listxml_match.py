"""Copied into the Cyberbots repository from the XvSF repository,
``tests/unit/test_listxml_match.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from tools.reference.listxml_match import identify, main, parse_listxml

PROG = b"parent program"
GFX = b"shared graphics"
CLONE = b"clone program"
KEY = b"k" * 20


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


LISTXML = f"""<?xml version="1.0"?>
<mame>
 <machine name="parent">
  <description>Synthetic (Europe)</description>
  <rom name="p.03" size="14" sha1="{sha1(PROG)}"/>
  <rom name="g.13" size="15" sha1="{sha1(GFX)}"/>
 </machine>
 <machine name="clone" cloneof="parent" romof="parent">
  <description>Synthetic (USA)</description>
  <rom name="c.03" size="13" sha1="{sha1(CLONE)}"/>
  <rom name="clone.key" size="20" sha1="{sha1(KEY)}"/>
  <rom name="g.13" merge="g.13" size="15" sha1="{sha1(GFX)}"/>
 </machine>
</mame>
"""


def write_zip(path: Path, members: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as bundle:
        for name, data in members.items():
            bundle.writestr(name, data)
    return path


def test_split_clone_zip_matches_by_hash_despite_renamed_member(
    tmp_path: Path,
) -> None:
    machines = parse_listxml(LISTXML)
    archive = write_zip(tmp_path / "oldname.zip", {"c.03x": CLONE})

    result = identify(archive, machines)

    assert result["complete_sets"] == ["clone"]
    assert result["titles"] == {"clone": "Synthetic (USA)"}
    assert result["members"]["c.03x"]["matches"] == ["clone:c.03"]  # type: ignore[index]
    assert result["unmatched"] == []


def test_parent_zip_needs_every_owned_rom(tmp_path: Path) -> None:
    machines = parse_listxml(LISTXML)
    partial = write_zip(tmp_path / "partial.zip", {"p.03": PROG, "junk": b"x"})
    full = write_zip(tmp_path / "parent.zip", {"p.03": PROG, "g.13": GFX})

    assert identify(partial, machines)["complete_sets"] == []
    assert identify(partial, machines)["unmatched"] == ["junk"]
    assert identify(full, machines)["complete_sets"] == ["parent"]


def test_loose_key_file_reports_its_machines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    listxml = tmp_path / "list.xml"
    listxml.write_text(LISTXML)
    key = tmp_path / "anyname.key"
    key.write_bytes(KEY)

    assert main(["--listxml", str(listxml), str(key)]) == 0

    report = json.loads(capsys.readouterr().out)
    entry = report["files"][0]
    assert entry["complete_sets"] == []
    assert entry["members"]["anyname.key"]["matches"] == ["clone:clone.key"]
    assert report["listxml_sha256"] == hashlib.sha256(LISTXML.encode()).hexdigest()
