"""Find and decode the Cyberbots arcade (CPS-II) dialogue tables (`REF-003`).

Run from the repository root:

    ./invenv.sh python -m tools.reference.cybots_text \\
        --driver local/mame_src/cps2.cpp --set cybotsu --rompath local/arcade \\
        --report REPORT.json [--text-out TEXT.json]

The 68000 program region is rebuilt in memory from the set's zips (the set's
own, then the parent's) using the pinned MAME driver definition, each 16-bit
word swapped into 68000 byte order. Only the requested outputs are written:
``--report`` holds addresses, counts and code statistics (no text);
``--text-out`` holds decoded game text and must go to an ignored local path
(`AGENTS.md` rule 21).

Layout (`EXP-0008`): a *dialogue table* is a run of big-endian 32-bit pointers
to *records*. A record is four big-endian 16-bit words, the fourth ``0x000E``,
followed by one byte per character and ended by ``0x00``. The tables are
found by layout, not by address: every run of at least ``--min-entries``
pointers whose targets are even and carry ``0x000E`` as the fourth word.

Character map for the Latin tables (`EXP-0008`): ``0x40``-``0x49`` digits,
``0x4A``-``0x63`` ``A``-``Z``, ``0x64``-``0x7D`` ``a``-``z``, ``0x7E`` ``?``,
``0x7F`` ``!``, ``0x14`` ``.``, ``0x1B`` ``,``, ``0xF8`` ``'``, ``0xF0`` space,
``0xFF`` line break. Other codes are shown as ``{xx}``, never guessed.

``find_member`` and ``build_program`` are copied from the XvSF repository,
``tools/reference/xvsf_text.py`` at commit ``a1c82ba``, unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.reference.mame_audit import RomSet, parse_driver

RECORD_MARK = 0x000E
LINE_BREAK = 0xFF
DECODE = (
    {code: chr(ord("0") + code - 0x40) for code in range(0x40, 0x4A)}
    | {code: chr(ord("A") + code - 0x4A) for code in range(0x4A, 0x64)}
    | {code: chr(ord("a") + code - 0x64) for code in range(0x64, 0x7E)}
    | {0x7E: "?", 0x7F: "!", 0x14: ".", 0x1B: ",", 0xF8: "'", 0xF0: " "}
)


@dataclass(frozen=True)
class Record:
    """One dialogue record: its address, four header words and its codes."""

    address: int
    header: tuple[int, int, int, int]
    codes: bytes


def find_member(
    bundles: Sequence[zipfile.ZipFile], name: str, sha1: str
) -> bytes | None:
    """A member by name, else by SHA-1 (older zips use older labels, REF-001)."""
    for bundle in bundles:
        if name in bundle.namelist():
            return bundle.read(name)
    for bundle in bundles:
        for info in bundle.infolist():
            data = bundle.read(info)
            if hashlib.sha1(data).hexdigest() == sha1:
                return data
    return None


def build_program(archives: Sequence[Path], romset: RomSet) -> bytes:
    """Rebuild the maincpu region in 68000 byte order from clone/parent zips."""
    entries = [rom for rom in romset.roms if rom.region == "maincpu"]
    image = bytearray(max(rom.offset + rom.size for rom in entries))
    bundles = [zipfile.ZipFile(path) for path in archives]
    for rom in entries:
        if rom.loader != "ROM_LOAD16_WORD_SWAP":
            raise ValueError(f"unsupported loader {rom.loader} for {rom.name}")
        data = find_member(bundles, rom.name, rom.sha1)
        if data is None:
            raise ValueError(f"{rom.name} not in {[str(p) for p in archives]}")
        if len(data) != rom.size:
            raise ValueError(f"{rom.name}: {len(data)} bytes, expected {rom.size}")
        swapped = bytearray(len(data))
        swapped[0::2] = data[1::2]
        swapped[1::2] = data[0::2]
        image[rom.offset : rom.offset + rom.size] = swapped
    return bytes(image)


def long(image: bytes, address: int) -> int:
    return int.from_bytes(image[address : address + 4], "big")


def is_record(image: bytes, address: int) -> bool:
    """Even, inside the image, fourth header word 0x000E."""
    return (
        address % 2 == 0
        and address + 8 <= len(image)
        and int.from_bytes(image[address + 6 : address + 8], "big") == RECORD_MARK
    )


def read_record(image: bytes, address: int) -> Record:
    header = tuple(
        int.from_bytes(image[address + 2 * k : address + 2 * k + 2], "big")
        for k in range(4)
    )
    end = image.index(b"\x00", address + 8)
    return Record(address, header, image[address + 8 : end])  # type: ignore[arg-type]


def find_tables(image: bytes, min_entries: int = 100) -> list[tuple[int, int]]:
    """(address, entries) of every run of pointers to records."""
    tables = []
    address = 0
    while address + 4 <= len(image):
        count = 0
        # A table ends where its records begin.
        while is_record(image, long(image, address + 4 * count)) and not (
            count and is_record(image, address + 4 * count)
        ):
            count += 1
        if count >= min_entries:
            tables.append((address, count))
            address += 4 * count
        else:
            address += 2
    return tables


def read_table(image: bytes, address: int, entries: int) -> list[Record]:
    return [read_record(image, long(image, address + 4 * i)) for i in range(entries)]


def decode(codes: bytes) -> str:
    return "".join(
        "\n" if code == LINE_BREAK else DECODE.get(code, f"{{{code:02x}}}")
        for code in codes
    )


def table_report(image: bytes, address: int, entries: int) -> dict[str, object]:
    """Counts only: targets, header patterns, map coverage, unmapped codes."""
    records = read_table(image, address, entries)
    unique = {record.address: record for record in records}
    codes: Counter[int] = Counter()
    for record in unique.values():
        codes.update(record.codes)
    total = sum(codes.values())
    unmapped = {
        f"{code:02X}": count
        for code, count in sorted(codes.items())
        if code not in DECODE and code != LINE_BREAK
    }
    return {
        "address": f"0x{address:06X}",
        "entries": entries,
        "distinct_records": len(unique),
        "records_from": f"0x{min(unique):06X}",
        "records_to": f"0x{max(unique):06X}",
        "code_bytes": total,
        "latin_map_coverage": round(1 - sum(unmapped.values()) / total, 4),
        "unmapped_codes": unmapped,
        "headers": {
            " ".join(f"{word:04X}" for word in header): count
            for header, count in Counter(r.header for r in records).most_common(8)
        },
        "records_sha256": hashlib.sha256(
            b"".join(image[r.address : r.address + 8] + r.codes for r in records)
        ).hexdigest(),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--set", dest="set_name", required=True)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--min-entries", type=int, default=100)
    parser.add_argument("--report", type=Path, help="metadata JSON (no text)")
    parser.add_argument("--text-out", type=Path, help="decoded text (ignored path)")
    parser.add_argument("--program-out", type=Path, help="program image (ignored)")
    args = parser.parse_args(argv)
    driver = args.driver.read_text(encoding="latin-1")
    sets = parse_driver(driver)
    romset = sets[args.set_name]
    archives = [args.rompath / f"{args.set_name}.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    image = build_program([p for p in archives if p.exists()], romset)
    tables = find_tables(image, args.min_entries)
    report = {
        "set": args.set_name,
        "title": romset.title,
        "driver_sha256": hashlib.sha256(driver.encode("latin-1")).hexdigest(),
        "program_sha256": hashlib.sha256(image).hexdigest(),
        "tables": [table_report(image, a, n) for a, n in tables],
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=1) + "\n")
    if args.text_out:
        text = {
            f"0x{a:06X}": [decode(r.codes) for r in read_table(image, a, n)]
            for a, n in tables
        }
        args.text_out.write_text(json.dumps(text, indent=1, ensure_ascii=False))
    if args.program_out:
        args.program_out.write_bytes(image)
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
