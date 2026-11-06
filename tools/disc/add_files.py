"""Add new files to a Mode 1/2352 data track's free sectors and root directory.

Written for Cyberbots ``OPT-005`` (the names switch's katakana files). It is
game-independent; the Cyberbots facts it was written against (``D-056``,
``EXP-0063``) are: the root directory is LSN 20-27, its last sector has
1,532 free bytes, Track 01's files end at LSN 43,643 and LSN 43,643-43,792
are zero-filled Mode 1 sectors. Those are inputs measured on the real track,
not constants here.

What it does, and nothing else:

- copies the source track to a new path (never in place; the target must not
  exist);
- writes each new file's bytes into free sectors: by default from the first
  LSN after every extent that lies in the track (directories, files, and the
  volume descriptors), one file after another; the target sectors must be
  inside the track, Mode 1, all-zero user data, and outside every existing
  extent;
- inserts one ISO 9660 directory record per file into the root directory at
  its sorted place (ECMA-119 9.3: name, then extension, each padded with
  spaces, then version descending). A record never spans a sector: it goes
  right after its predecessor in that predecessor's sector, shifting the
  records after it in that sector, or, when the predecessor ends its sector
  and that sector is full, at the start of the next sector. No room is an
  error. The record's recording date, flags and volume sequence number (and
  any system-use bytes) are copied from the nearest file record before it;
  the extent and size are both-endian; extended-attribute length and the
  interleave fields are zero;
- regenerates the EDC/ECC of every rewritten sector (``tools.disc.sector``).

The PVD, path tables, the directory's own size and every other record are
untouched; the extent of a directory never grows. Files whose extents lie
beyond the track (Cyberbots' audio-track entries, ``D-002``) are ignored for
free-space and overlap checks.

``add_files`` verifies its own output with ``tools.disc.iso9660``: the new
files are listed with their LSN and size and read back equal; the old records
are byte-identical and in the same order; every rewritten sector has valid
EDC/ECC; and the only sectors that differ from the source are those reported.
The report gives each new file's ``record_index`` (0-based position in the
root directory, counting ``.`` and ``..``) and the directory's ``last_record``.

The sorted order is for ISO 9660 (ECMA-119 9.3) and for other readers; the
Cyberbots game does not need it. Disassembly of CYBER.BIN (base 0x0600D000)
shows that the game copies the root directory's records in order into a
24-byte-entry table (0x060DCB68 at the Options screen) with the loader at
0x0604125A, which sets bit 0 of byte 11 on the last entry it stores
(0x060412E6-0x060412EC). The name lookup at 0x060410C0 is a linear search
that stops after the first entry that has that bit set
(0x060410F2-0x060410FE). It is not a binary search. A new file is found
only if it is at or before the entry that has that end flag. Because the
loader moves the flag to the last stored record, a new file at the end of
the directory is expected to be found. This is a HYPOTHESIS until a boot of
a derived image shows ``record_index`` of ``last_record`` with byte 11 bit 0
set and the old last entry without it.

Output holds game data: keep it under ``build/`` or a scratch directory,
never in git (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import struct
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path

from tools.disc.iso9660 import (
    RAW_SECTOR,
    USER_DATA,
    DiscFormatError,
    Entry,
    Track,
    primary_volume,
    walk,
)
from tools.disc.sector import is_valid, regenerate

NAME_PATTERN = re.compile(r"^[A-Z0-9_]{1,8}\.[A-Z0-9_]{0,3};[1-9][0-9]{0,4}$")
SPECIAL = (b"\x00", b"\x01")
DIR_FLAG = 0x02


@dataclass(frozen=True)
class NewFile:
    """A file to add: ISO 9660 identifier (``NAME.EXT;1``), bytes, optional LSN."""

    name: str
    data: bytes
    lsn: int | None = None


@dataclass(frozen=True)
class Placement:
    name: str
    lsn: int
    size_bytes: int
    sectors: int
    directory_lsn: int
    sha256: str


@dataclass
class AddResult:
    placements: list[Placement]
    changed_sectors: list[dict[str, object]]
    verification: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Record:
    """One directory record's position in a directory extent."""

    sector: int  # index within the extent
    offset: int  # within the sector
    raw: bytes

    @property
    def identifier(self) -> bytes:
        return self.raw[33 : 33 + self.raw[32]]

    @property
    def flags(self) -> int:
        return self.raw[25]


def sort_key(identifier: bytes) -> tuple[int, bytes, bytes, int]:
    """ECMA-119 9.3 order: ``\\x00``, ``\\x01``, then name, extension, version."""
    if identifier in SPECIAL:
        return (0, identifier, b"", 0)
    name, _, version = identifier.partition(b";")
    base, _, extension = name.partition(b".")
    return (
        1,
        base.ljust(255, b" "),
        extension.ljust(255, b" "),
        -int(version) if version.isdigit() else 0,
    )


def sectors_for(size: int) -> int:
    return (size + USER_DATA - 1) // USER_DATA


def parse_sectors(data: bytes) -> list[list[Record]]:
    """Records of a directory extent, grouped by sector; none may span one."""
    out: list[list[Record]] = []
    for index in range(len(data) // USER_DATA):
        sector = data[index * USER_DATA : (index + 1) * USER_DATA]
        records: list[Record] = []
        offset = 0
        while offset < USER_DATA and sector[offset]:
            length = sector[offset]
            if length < 34 or offset + length > USER_DATA:
                raise DiscFormatError(
                    f"bad directory record length {length} at sector {index} "
                    f"offset {offset}"
                )
            records.append(Record(index, offset, sector[offset : offset + length]))
            offset += length
        if any(sector[offset:]):
            raise DiscFormatError(f"directory sector {index} has bytes after its end")
        out.append(records)
    return out


def pack_sectors(groups: Sequence[Sequence[bytes]]) -> bytes:
    out = bytearray()
    for records in groups:
        body = b"".join(records)
        if len(body) > USER_DATA:
            raise ValueError("a directory sector would overflow")
        out += body.ljust(USER_DATA, b"\x00")
    return bytes(out)


def make_record(template: bytes, name: bytes, lsn: int, size: int) -> bytes:
    """A file record with ``template``'s date, flags, volume sequence, system use."""
    template_name_length = template[32]
    su_start = 33 + template_name_length + (0 if template_name_length % 2 else 1)
    system_use = template[su_start : template[0]]
    pad = b"" if len(name) % 2 else b"\x00"
    record = bytearray(33 + len(name) + len(pad) + len(system_use))
    if len(record) % 2:
        record.append(0)
    if len(record) > 255:
        raise ValueError(f"record for {name!r} is longer than 255 bytes")
    record[0] = len(record)
    record[1] = 0
    struct.pack_into("<I", record, 2, lsn)
    struct.pack_into(">I", record, 6, lsn)
    struct.pack_into("<I", record, 10, size)
    struct.pack_into(">I", record, 14, size)
    record[18:25] = template[18:25]
    record[25] = template[25]
    record[26] = record[27] = 0
    record[28:32] = template[28:32]
    record[32] = len(name)
    record[33 : 33 + len(name)] = name
    start = 33 + len(name) + len(pad)
    record[start : start + len(system_use)] = system_use
    return bytes(record)


def insert_record(groups: list[list[bytes]], name: bytes, lsn: int, size: int) -> int:
    """Insert a file record in sorted place; return its sector index."""
    flat = [
        (s, i, raw) for s, records in enumerate(groups) for i, raw in enumerate(records)
    ]
    keys = [sort_key(raw[33 : 33 + raw[32]]) for _, _, raw in flat]
    if keys != sorted(keys):
        raise ValueError("the directory's records are not in ISO 9660 order")
    new_key = sort_key(name)
    plain = name.partition(b";")[0]
    for _, _, raw in flat:
        if raw[33 : 33 + raw[32]].partition(b";")[0] == plain:
            raise ValueError(f"{name.decode()} already exists")
    before = [k for k in keys if k < new_key]
    if not before:
        raise ValueError(f"{name.decode()} would sort before the '.' record")
    position = len(before) - 1
    files = [
        raw
        for _, _, raw in flat
        if raw[33 : 33 + raw[32]] not in SPECIAL and not raw[25] & DIR_FLAG
    ]
    if not files:
        raise ValueError("no file record to copy the date and flags from")
    preceding = [
        raw
        for _, _, raw in flat[: position + 1]
        if raw[33 : 33 + raw[32]] not in SPECIAL and not raw[25] & DIR_FLAG
    ]
    template = preceding[-1] if preceding else files[0]
    record = make_record(template, name, lsn, size)
    sector, index, _ = flat[position]
    used = sum(len(r) for r in groups[sector])
    if used + len(record) <= USER_DATA:
        groups[sector].insert(index + 1, record)
        return sector
    last_in_sector = index == len(groups[sector]) - 1
    if last_in_sector and sector + 1 < len(groups):
        used_next = sum(len(r) for r in groups[sector + 1])
        if used_next + len(record) <= USER_DATA:
            groups[sector + 1].insert(0, record)
            return sector + 1
    raise ValueError(
        f"no room for {name.decode()} ({len(record)} bytes) in directory sector "
        f"{sector} ({USER_DATA - used} bytes free)"
    )


def track_extents(track: Track) -> tuple[int, int, list[tuple[int, int]]]:
    """Root LSN, root size, and every (first LSN, sector count) inside the track."""
    volume = primary_volume(track)
    root_lsn, root_size = int(str(volume["root_lsn"])), int(str(volume["root_size"]))
    descriptors = 16
    while descriptors < track.sectors and track.user(descriptors)[0] != 0xFF:
        descriptors += 1
    extents = [(0, descriptors + 1), (root_lsn, sectors_for(root_size))]
    pvd = track.user(16)
    table_size = struct.unpack_from("<I", pvd, 132)[0]
    tables = [
        struct.unpack_from("<I", pvd, 140)[0],
        struct.unpack_from("<I", pvd, 144)[0],
        struct.unpack_from(">I", pvd, 148)[0],
        struct.unpack_from(">I", pvd, 152)[0],
    ]
    extents += [(t, sectors_for(table_size)) for t in tables if 0 < t < track.sectors]
    entries: list[Entry] = list(walk(track, root_lsn, root_size))
    for entry in entries:
        if entry.lsn < track.sectors:
            extents.append((entry.lsn, sectors_for(entry.size_bytes)))
    return root_lsn, root_size, extents


def first_free_lsn(track: Track) -> int:
    _, _, extents = track_extents(track)
    return max(lsn + count for lsn, count in extents)


def _sector_hashes(lsn: int, old: bytes, new: bytes, role: str) -> dict[str, object]:
    return {
        "lsn": lsn,
        "role": role,
        "original_sha256": hashlib.sha256(old).hexdigest(),
        "modified_sha256": hashlib.sha256(new).hexdigest(),
    }


def add_files(source: Path, target: Path, files: Sequence[NewFile]) -> AddResult:
    """Copy ``source`` to ``target`` with ``files`` added; verify and report."""
    if not files:
        raise ValueError("no files to add")
    if target.exists() or target.resolve() == source.resolve():
        raise ValueError(f"{target} exists; the output must be a new path")
    names = [f.name for f in files]
    for name in names:
        if not NAME_PATTERN.match(name):
            raise ValueError(
                f"{name!r} is not an 8.3 ISO 9660 name like 'ZNAMES0.BIN;1'"
            )
    if len({n.partition(";")[0] for n in names}) != len(names):
        raise ValueError("new file names repeat")
    with source.open("rb") as stream:
        track = Track(stream, source.stat().st_size)
        root_lsn, root_size, extents = track_extents(track)
        used: set[int] = set()
        for lsn, count in extents:
            used.update(range(lsn, lsn + count))
        cursor = max(lsn + count for lsn, count in extents)
        placements: list[Placement] = []
        claimed: set[int] = set()
        for new in files:
            lsn = cursor if new.lsn is None else new.lsn
            count = max(1, sectors_for(len(new.data)))
            span = range(lsn, lsn + count)
            if lsn < 0 or lsn + count > track.sectors:
                raise ValueError(
                    f"{new.name}: LSN {lsn}-{lsn + count - 1} is outside the track "
                    f"(last LSN {track.sectors - 1})"
                )
            for index in span:
                if index in used:
                    raise ValueError(f"{new.name}: LSN {index} is inside an extent")
                if index in claimed:
                    raise ValueError(f"{new.name}: LSN {index} is used by a new file")
                stream.seek(index * RAW_SECTOR)
                if stream.read(RAW_SECTOR)[15] != 1:
                    raise ValueError(f"{new.name}: LSN {index} is not Mode 1")
                if any(track.user(index)):
                    raise ValueError(f"{new.name}: LSN {index} has non-zero user data")
            claimed.update(span)
            placements.append(
                Placement(
                    new.name,
                    lsn,
                    len(new.data),
                    count,
                    -1,
                    hashlib.sha256(new.data).hexdigest(),
                )
            )
            cursor = lsn + count

        directory = track.read(root_lsn, root_size)
        groups = [[r.raw for r in records] for records in parse_sectors(directory)]
        for index, (new, place) in enumerate(zip(files, placements, strict=True)):
            sector = insert_record(
                groups, new.name.encode("ascii"), place.lsn, len(new.data)
            )
            placements[index] = Placement(
                place.name,
                place.lsn,
                place.size_bytes,
                place.sectors,
                root_lsn + sector,
                place.sha256,
            )
        new_directory = pack_sectors(groups)

        rewrites: dict[int, tuple[bytes, str]] = {}
        for index in range(sectors_for(root_size)):
            user = new_directory[index * USER_DATA : (index + 1) * USER_DATA]
            if user != directory[index * USER_DATA : (index + 1) * USER_DATA]:
                rewrites[root_lsn + index] = (user, "directory")
        for new, place in zip(files, placements, strict=True):
            for index in range(place.sectors):
                piece = new.data[index * USER_DATA : (index + 1) * USER_DATA]
                rewrites[place.lsn + index] = (
                    piece.ljust(USER_DATA, b"\x00"),
                    new.name,
                )

        changed: list[dict[str, object]] = []
        new_sectors: dict[int, bytes] = {}
        for lsn in sorted(rewrites):
            user, role = rewrites[lsn]
            stream.seek(lsn * RAW_SECTOR)
            raw = stream.read(RAW_SECTOR)
            new_raw = regenerate(raw[:16] + user + raw[16 + USER_DATA :])
            if new_raw != raw:
                new_sectors[lsn] = new_raw
                changed.append(_sector_hashes(lsn, raw, new_raw, role))

    result = AddResult(placements, changed)
    shutil.copyfile(source, target)
    try:
        with target.open("r+b") as out:
            for lsn, new_raw in new_sectors.items():
                out.seek(lsn * RAW_SECTOR)
                out.write(new_raw)
        result.verification = verify_added(source, target, files, placements, changed)
    except Exception:
        target.unlink()
        raise
    return result


def _records(track: Track, lsn: int, size: int) -> list[bytes]:
    return [r.raw for records in parse_sectors(track.read(lsn, size)) for r in records]


def verify_added(
    source: Path,
    target: Path,
    files: Sequence[NewFile],
    placements: Sequence[Placement],
    changed: Sequence[dict[str, object]],
) -> dict[str, object]:
    """Check ``target`` against ``source``; raise ``ValueError`` on any mismatch."""
    expected = {int(str(c["lsn"])) for c in changed}
    with source.open("rb") as a, target.open("rb") as b:
        if source.stat().st_size != target.stat().st_size:
            raise ValueError("the tracks differ in length")
        differing: set[int] = set()
        lsn = 0
        while chunk_a := a.read(RAW_SECTOR * 512):
            chunk_b = b.read(len(chunk_a))
            for offset in range(0, len(chunk_a), RAW_SECTOR):
                raw_b = chunk_b[offset : offset + RAW_SECTOR]
                if chunk_a[offset : offset + RAW_SECTOR] != raw_b:
                    index = lsn + offset // RAW_SECTOR
                    differing.add(index)
                    if not is_valid(raw_b):
                        raise ValueError(f"LSN {index} has bad EDC/ECC")
            lsn += len(chunk_a) // RAW_SECTOR
        if differing != expected:
            raise ValueError(
                f"sectors differ outside the report: {sorted(differing ^ expected)}"
            )
        track_a = Track(a, source.stat().st_size)
        track_b = Track(b, target.stat().st_size)
        volume_a, volume_b = primary_volume(track_a), primary_volume(track_b)
        if volume_a != volume_b:
            raise ValueError("the primary volume descriptor changed")
        root_lsn = int(str(volume_b["root_lsn"]))
        root_size = int(str(volume_b["root_size"]))
        listing = {e.path: e for e in walk(track_b, root_lsn, root_size)}
        identifiers = [
            r[33 : 33 + r[32]] for r in _records(track_b, root_lsn, root_size)
        ]
        listed = []
        for new, place in zip(files, placements, strict=True):
            entry = listing.get(new.name)
            if entry is None or entry.is_dir:
                raise ValueError(f"{new.name} is not listed")
            if (entry.lsn, entry.size_bytes) != (place.lsn, len(new.data)):
                raise ValueError(f"{new.name} is listed at the wrong LSN or size")
            if track_b.read(entry.lsn, entry.size_bytes) != new.data:
                raise ValueError(f"{new.name} reads back different bytes")
            listed.append(
                {
                    "name": new.name,
                    "lsn": entry.lsn,
                    "size": entry.size_bytes,
                    "record_index": identifiers.index(new.name.encode("ascii")),
                }
            )
        new_names = {f.name.encode("ascii") for f in files}
        old_records = _records(track_a, root_lsn, root_size)
        kept = [
            r
            for r in _records(track_b, root_lsn, root_size)
            if r[33 : 33 + r[32]] not in new_names
        ]
        if kept != old_records:
            raise ValueError("existing directory records changed")
        old_listing = [
            (e.path, e.lsn, e.size_bytes, e.flags)
            for e in walk(track_a, root_lsn, root_size)
        ]
        new_listing = [
            (e.path, e.lsn, e.size_bytes, e.flags)
            for e in listing.values()
            if e.path not in {f.name for f in files}
        ]
        if new_listing != old_listing:
            raise ValueError("the listing of existing entries changed")
    return {
        "listed": listed,
        "differing_sectors": sorted(differing),
        "existing_records_unchanged": len(old_records),
        "records": len(identifiers),
        "last_record": {
            "name": identifiers[-1].decode("latin-1"),
            "record_index": len(identifiers) - 1,
        },
    }


def directory_room(track: Track) -> dict[str, object]:
    """Root directory facts: extent, last used sector, its used and free bytes."""
    root_lsn, root_size, _ = track_extents(track)
    groups = parse_sectors(track.read(root_lsn, root_size))
    used = [sum(len(r.raw) for r in records) for records in groups]
    last = max(i for i, u in enumerate(used) if u)
    return {
        "root_lsn": root_lsn,
        "root_size": root_size,
        "records": sum(len(g) for g in groups),
        "last_used_sector_lsn": root_lsn + last,
        "last_sector_records": len(groups[last]),
        "last_sector_last_name": groups[last][-1].identifier.decode("latin-1"),
        "last_sector_used_bytes": used[last],
        "last_sector_free_bytes": USER_DATA - used[last],
        "free_bytes_per_sector": [USER_DATA - u for u in used],
        "first_free_lsn": first_free_lsn(track),
        "track_sectors": track.sectors,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Copy a Mode 1/2352 track to a new path with files added to free "
            "sectors and the root directory."
        )
    )
    parser.add_argument("track", type=Path, help="source track (read only)")
    parser.add_argument("--out", type=Path, help="new output track (must not exist)")
    parser.add_argument(
        "--file",
        nargs=2,
        action="append",
        metavar=("NAME", "PATH"),
        default=[],
        help="ISO 9660 name (NAME.EXT;1) and its data file; repeatable",
    )
    parser.add_argument(
        "--lsn",
        type=int,
        help="first LSN for the files (default: the first free LSN)",
    )
    parser.add_argument(
        "--measure",
        action="store_true",
        help="print the root directory's room and the first free LSN; write nothing",
    )
    args = parser.parse_args(argv)
    try:
        if args.measure:
            with args.track.open("rb") as stream:
                track = Track(stream, args.track.stat().st_size)
                print(json.dumps(directory_room(track), indent=2))
            return 0
        if args.out is None or not args.file:
            parser.error("give --out and at least one --file")
        files = []
        for position, (name, path) in enumerate(args.file):
            lsn = args.lsn if position == 0 else None
            files.append(NewFile(name, Path(path).read_bytes(), lsn))
        result = add_files(args.track, args.out, files)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    report = {
        "tool": "tools.disc.add_files",
        "source": str(args.track),
        "output": str(args.out),
        "files": [asdict(p) for p in result.placements],
        "changed_sectors": result.changed_sectors,
        "verification": result.verification,
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
