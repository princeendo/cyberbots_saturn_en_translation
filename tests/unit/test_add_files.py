"""Tests for ``tools.disc.add_files`` on small synthetic Mode 1 tracks."""

from __future__ import annotations

import io
import json
import struct
from pathlib import Path

import pytest

from tests.unit.test_iso9660 import raw_sector
from tools.disc.add_files import (
    NewFile,
    add_files,
    directory_room,
    first_free_lsn,
    main,
    sort_key,
    verify_added,
)
from tools.disc.iso9660 import RAW_SECTOR, USER_DATA, Track, primary_volume, walk
from tools.disc.sector import is_valid, regenerate

DATE = bytes([97, 2, 19, 19, 54, 10, 20])
TOTAL = 40
ROOT = 20
FREE = 27  # first LSN after B.DAT (25-26)


def rec(name: bytes, lsn: int, size: int, flags: int = 0) -> bytes:
    length = 33 + len(name) + (1 if len(name) % 2 == 0 else 0)
    record = bytearray(length)
    record[0] = length
    struct.pack_into("<I", record, 2, lsn)
    struct.pack_into(">I", record, 6, lsn)
    struct.pack_into("<I", record, 10, size)
    struct.pack_into(">I", record, 14, size)
    record[18:25] = DATE
    record[25] = flags
    record[28:32] = b"\x01\x00\x00\x01"
    record[32] = len(name)
    record[33 : 33 + len(name)] = name
    return bytes(record)


def filler(count: int, width: int = 3, prefix: str = "F") -> list[bytes]:
    """Records named like ``F000.BIN;1``: 44 bytes at width 3, 46 at width 6."""
    names = [f"{prefix}{i:0{width}d}.BIN;1".encode() for i in range(count)]
    return [rec(name, 23, 5) for name in names]


def default_root() -> list[list[bytes]]:
    return [
        [
            rec(b"\x00", ROOT, 2 * USER_DATA, 2),
            rec(b"\x01", ROOT, 2 * USER_DATA, 2),
            rec(b"A.BIN;1", 23, 5),
            rec(b"AUDIO.DA;1", 5000, 100_000),  # beyond the track (D-002 style)
            rec(b"C.BIN;1", 24, 0),
            rec(b"SUB", 22, USER_DATA, 2),
        ],
        [],
    ]


def build_track(root: list[list[bytes]] | None = None, total: int = TOTAL) -> bytes:
    groups = default_root() if root is None else root
    user = [b""] * total
    pvd = bytearray(USER_DATA)
    pvd[0], pvd[1:6], pvd[6] = 1, b"CD001", 1
    pvd[40:72] = b"SYNTH".ljust(32)
    struct.pack_into("<I", pvd, 80, total)
    struct.pack_into("<H", pvd, 128, USER_DATA)
    struct.pack_into("<I", pvd, 132, 10)
    struct.pack_into("<I", pvd, 140, 18)
    struct.pack_into(">I", pvd, 148, 19)
    pvd[156 : 156 + 34] = rec(b"\x00", ROOT, len(groups) * USER_DATA, 2)
    user[16] = bytes(pvd)
    user[17] = b"\xffCD001\x01"
    user[18] = b"\x01\x00\x14\x00\x00\x00\x01\x00\x00\x00"
    user[19] = b"\x01\x00\x00\x00\x00\x14\x00\x01\x00\x00"
    for index, records in enumerate(groups):
        user[ROOT + index] = b"".join(records)
    sub = ROOT + len(groups)
    user[sub] = rec(b"\x00", sub, USER_DATA, 2) + rec(b"\x01", ROOT, 0, 2)
    user[sub] += rec(b"B.DAT;1", sub + 3, 2050)
    user[sub + 1] = b"hello"
    user[sub + 3] = b"X" * USER_DATA
    user[sub + 4] = b"YZ"
    return b"".join(regenerate(raw_sector(i, data)) for i, data in enumerate(user))


def write(tmp_path: Path, image: bytes) -> Path:
    path = tmp_path / "track.bin"
    path.write_bytes(image)
    return path


def sector(image: bytes, lsn: int) -> bytes:
    return image[lsn * RAW_SECTOR : (lsn + 1) * RAW_SECTOR]


def listing(path: Path) -> list[tuple[str, int, int]]:
    with path.open("rb") as stream:
        track = Track(stream, path.stat().st_size)
        volume = primary_volume(track)
        lsn, size = int(str(volume["root_lsn"])), int(str(volume["root_size"]))
        return [(e.path, e.lsn, e.size_bytes) for e in walk(track, lsn, size)]


def read_back(path: Path, lsn: int, size: int) -> bytes:
    with path.open("rb") as stream:
        return Track(stream, path.stat().st_size).read(lsn, size)


def test_sort_key_follows_iso9660_order() -> None:
    names = [b"B.BIN;1", b"\x01", b"A.BIN;2", b"AB.BIN;1", b"A.BIN;1", b"\x00"]
    names += [b"A.BI;1", b"SUB"]
    assert sorted(names, key=sort_key) == [
        b"\x00",
        b"\x01",
        b"A.BI;1",
        b"A.BIN;2",
        b"A.BIN;1",
        b"AB.BIN;1",
        b"B.BIN;1",
        b"SUB",
    ]
    assert sort_key(b"WARNING4.PIX;1") < sort_key(b"ZNAMES0.BIN;1")


def test_first_free_lsn_ignores_extents_beyond_the_track(tmp_path: Path) -> None:
    path = write(tmp_path, build_track())
    with path.open("rb") as stream:
        track = Track(stream, path.stat().st_size)
        assert first_free_lsn(track) == FREE
        room = directory_room(track)
    assert room["root_lsn"] == ROOT
    assert room["last_used_sector_lsn"] == ROOT
    assert room["first_free_lsn"] == FREE
    assert room["free_bytes_per_sector"] == [1820, USER_DATA]
    assert room["last_sector_last_name"] == "SUB"


def test_add_one_file_changes_only_its_sectors(tmp_path: Path) -> None:
    source = write(tmp_path, build_track())
    original = source.read_bytes()
    target = tmp_path / "out.bin"
    data = bytes(range(256)) * 9  # 2,304 bytes: two sectors

    result = add_files(source, target, [NewFile("ZNAMES0.BIN;1", data)])

    assert source.read_bytes() == original
    derived = target.read_bytes()
    assert [p.lsn for p in result.placements] == [FREE]
    assert result.placements[0].directory_lsn == ROOT
    assert [c["lsn"] for c in result.changed_sectors] == [ROOT, FREE, FREE + 1]
    assert [c["role"] for c in result.changed_sectors] == [
        "directory",
        "ZNAMES0.BIN;1",
        "ZNAMES0.BIN;1",
    ]
    for index in range(TOTAL):
        a, b = sector(original, index), sector(derived, index)
        assert is_valid(b)
        assert (a != b) == (index in (ROOT, FREE, FREE + 1))
    assert ("ZNAMES0.BIN;1", FREE, len(data)) in listing(target)
    assert read_back(target, FREE, len(data)) == data
    assert result.verification["listed"] == [
        {"name": "ZNAMES0.BIN;1", "lsn": FREE, "size": len(data), "record_index": 6}
    ]
    assert result.verification["records"] == 7
    assert result.verification["last_record"] == {
        "name": "ZNAMES0.BIN;1",
        "record_index": 6,
    }
    # the record: after SUB, date and volume sequence copied, both-endian fields
    root = sector(derived, ROOT)[16 : 16 + USER_DATA]
    start = sum(len(r) for r in default_root()[0])
    record = root[start : start + root[start]]
    assert record[0] == 46
    assert struct.unpack_from("<I", record, 2)[0] == FREE
    assert struct.unpack_from(">I", record, 6)[0] == FREE
    assert struct.unpack_from("<I", record, 10)[0] == len(data)
    assert struct.unpack_from(">I", record, 14)[0] == len(data)
    assert record[18:25] == DATE
    assert record[25] == 0
    assert record[28:32] == b"\x01\x00\x00\x01"
    assert record[33:46] == b"ZNAMES0.BIN;1"
    assert not any(root[start + 46 :])


def test_insert_in_the_middle_shifts_records_and_keeps_order(tmp_path: Path) -> None:
    source = write(tmp_path, build_track())
    target = tmp_path / "out.bin"
    files = [NewFile("B.BIN;1", b"bee"), NewFile("ZZ.BIN;1", b"Z" * 5000)]

    result = add_files(source, target, files)

    assert [(p.lsn, p.sectors) for p in result.placements] == [(FREE, 1), (FREE + 1, 3)]
    names = [name for name, _, _ in listing(target)]
    assert names == [
        "A.BIN;1",
        "AUDIO.DA;1",
        "B.BIN;1",
        "C.BIN;1",
        "SUB",
        "SUB/B.DAT;1",
        "ZZ.BIN;1",
    ]
    listed = result.verification["listed"]
    assert isinstance(listed, list)
    assert [item["record_index"] for item in listed] == [4, 7]
    assert result.verification["last_record"] == {
        "name": "ZZ.BIN;1",
        "record_index": 7,
    }
    assert read_back(target, FREE, 3) == b"bee"
    assert read_back(target, FREE + 1, 5000) == b"Z" * 5000


def test_explicit_lsn_and_refusals(tmp_path: Path) -> None:
    source = write(tmp_path, build_track())
    out = tmp_path / "out.bin"

    result = add_files(source, out, [NewFile("Z.BIN;1", b"z", lsn=TOTAL - 1)])
    assert result.placements[0].lsn == TOTAL - 1

    bad = [
        NewFile("Z.BIN;1", b"z", lsn=23),  # inside A.BIN
        NewFile("Z.BIN;1", b"z" * 3000, lsn=TOTAL - 1),  # past the track end
        NewFile("Z.BIN;1", b"z", lsn=18),  # path table
        NewFile("A.BIN;1", b"z"),  # name exists
        NewFile("z.bin;1", b"z"),  # not a d-character name
        NewFile("Z.BIN", b"z"),  # no version
    ]
    for index, new in enumerate(bad):
        target = tmp_path / f"bad{index}.bin"
        with pytest.raises(ValueError):
            add_files(source, target, [new])
        assert not target.exists()
    with pytest.raises(ValueError):
        add_files(
            source,
            tmp_path / "overlap.bin",
            [NewFile("Y.BIN;1", b"y", lsn=30), NewFile("Z.BIN;1", b"z", lsn=30)],
        )
    with pytest.raises(ValueError):
        add_files(source, out, [NewFile("Y.BIN;1", b"y")])  # target exists
    with pytest.raises(ValueError):
        add_files(source, source, [NewFile("Y.BIN;1", b"y")])
    with pytest.raises(ValueError):
        add_files(source, tmp_path / "none.bin", [])


def test_refuses_non_zero_free_sector(tmp_path: Path) -> None:
    image = bytearray(build_track())
    image[30 * RAW_SECTOR : 31 * RAW_SECTOR] = regenerate(raw_sector(30, b"junk"))
    source = write(tmp_path, bytes(image))
    with pytest.raises(ValueError, match="non-zero"):
        add_files(source, tmp_path / "o.bin", [NewFile("Z.BIN;1", b"z", lsn=30)])


def test_refuses_when_the_directory_sector_is_full(tmp_path: Path) -> None:
    root = default_root()
    root[0][5:5] = filler(32) + filler(8, 6, "G")  # 44 bytes stay free
    assert sum(len(r) for r in root[0]) == USER_DATA - 44
    source = write(tmp_path, build_track(root))
    target = tmp_path / "o.bin"
    with pytest.raises(ValueError, match="no room"):
        add_files(source, target, [NewFile("PIECE00.BIN;1", b"z")])  # 46 bytes
    assert not target.exists()
    # a shorter name still fits (40 bytes)
    add_files(source, target, [NewFile("P.BIN;1", b"z")])
    assert ("P.BIN;1", FREE, 1) in listing(target)


def test_record_goes_to_next_sector_when_its_predecessor_ends_a_full_one(
    tmp_path: Path,
) -> None:
    root = default_root()
    root[0][5:5] = filler(42)
    sub = root[0].pop()  # SUB moves to the second sector; 8 bytes stay free
    root[1] = [sub]
    source = write(tmp_path, build_track(root))
    target = tmp_path / "o.bin"

    result = add_files(source, target, [NewFile("PIECE.BIN;1", b"p")])

    assert result.placements[0].directory_lsn == ROOT + 1
    assert [c["lsn"] for c in result.changed_sectors] == [ROOT + 1, FREE]
    names = [name for name, _, _ in listing(target)]
    assert names.index("PIECE.BIN;1") == names.index("SUB") - 1
    assert names[-1] == "SUB/B.DAT;1"


def test_verify_detects_a_stray_change(tmp_path: Path) -> None:
    source = write(tmp_path, build_track())
    target = tmp_path / "o.bin"
    files = [NewFile("Z.BIN;1", b"z")]
    result = add_files(source, target, files)
    image = bytearray(target.read_bytes())
    image[35 * RAW_SECTOR : 36 * RAW_SECTOR] = regenerate(raw_sector(35, b"stray"))
    target.write_bytes(bytes(image))
    with pytest.raises(ValueError, match="outside the report"):
        verify_added(source, target, files, result.placements, result.changed_sectors)


def test_cli_measures_and_adds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = write(tmp_path, build_track())
    assert main([str(source), "--measure"]) == 0
    assert json.load(io.StringIO(capsys.readouterr().out))["first_free_lsn"] == FREE
    data = tmp_path / "piece.bin"
    data.write_bytes(b"P" * 100)
    out = tmp_path / "out.bin"
    argv = [str(source), "--out", str(out), "--file", "ZNAMES0.BIN;1", str(data)]
    assert main([*argv, "--lsn", "33"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["files"][0]["lsn"] == 33
    assert [c["lsn"] for c in report["changed_sectors"]] == [ROOT, 33]
    assert read_back(out, 33, 100) == b"P" * 100
    with pytest.raises(SystemExit):
        main(argv)  # the output exists now
