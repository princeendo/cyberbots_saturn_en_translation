"""Census of NUL-terminated Shift-JIS string blocks in data-track files (`TXT-001`).

Run from the repository root:

    ./invenv.sh python -m tools.text.script_census FILE ... [--out JSON]

A *block* is a run of at least ``--min-strings`` strings that each start on a
4-byte boundary, end with one NUL, are zero-padded to the next 4-byte boundary
(extra all-zero words are allowed between strings), decode as Shift-JIS with
no control characters, of which at least half contain a double-byte
character, and at least one has ``--min-longest`` characters or more (graphics
data such as runs of ``AA``/``BB``/``CC`` bytes otherwise decodes as short
half-width kana lines). Blocks are found by layout, not by meaning: that the game draws
these strings is a runtime question.

For each file with a block, the tool also looks for a load base: the
256-byte-aligned address in WRAM-H or WRAM-L at which the most big-endian
32-bit words of the file (at even offsets) point exactly at string starts.
The words found that way are reported as references.

The output holds offsets, lengths, counts and hashes, never the text itself
(`AGENTS.md` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import struct
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

BASE_RANGES = ((0x06000000, 0x06100000), (0x00200000, 0x00300000))
BASE_STEP = 0x100
CANDIDATE_START = re.compile(rb"\x00(?=[\x81-\x9f\xe0-\xfc])")
INNER_LIST = re.compile(r"\[\n\s+([^\[\]{}]*?)\n\s*\]")


@dataclass(frozen=True)
class Block:
    """One run of aligned strings: ``strings`` holds (offset, raw bytes)."""

    start: int
    end: int
    strings: tuple[tuple[int, bytes], ...]


def units(raw: bytes) -> list[bytes]:
    """Split Shift-JIS bytes into characters (one or two bytes each)."""
    out = []
    index = 0
    while index < len(raw):
        lead = raw[index]
        width = 1 if lead < 0x80 or 0xA1 <= lead <= 0xDF else 2
        out.append(raw[index : index + width])
        index += width
    return out


def is_line(raw: bytes) -> bool:
    """True for non-empty Shift-JIS text with no control characters."""
    if not raw:
        return False
    try:
        text = raw.decode("shift_jis")
    except UnicodeDecodeError:
        return False
    return all(ord(char) >= 0x20 for char in text)


def parse_block(data: bytes, start: int) -> Block:
    """Walk aligned NUL-terminated lines from ``start`` until one fails."""
    strings = []
    offset = start
    while offset < len(data):
        end = data.find(b"\x00", offset)
        if end < 0 or not is_line(data[offset:end]):
            break
        strings.append((offset, data[offset:end]))
        offset = (end + 4) & ~3
        if data[end:offset].strip(b"\x00"):
            break
        while data[offset : offset + 4] == b"\x00\x00\x00\x00":
            offset += 4
    if strings:
        last_offset, last = strings[-1]
        end_offset = (last_offset + len(last) + 4) & ~3
    else:
        end_offset = start
    return Block(start, end_offset, tuple(strings))


def find_blocks(
    data: bytes, min_strings: int = 16, min_longest: int = 4
) -> list[Block]:
    """Every block of at least ``min_strings`` lines, mostly double-byte."""
    blocks: list[Block] = []
    candidates = [match.start() + 1 for match in CANDIDATE_START.finditer(data)]
    if data[:1] and 0x81 <= data[0] <= 0xFC:
        candidates.insert(0, 0)
    covered = 0
    for start in candidates:
        if start % 4 or start < covered:
            continue
        block = parse_block(data, start)
        double = sum(1 for _, raw in block.strings if any(b >= 0x80 for b in raw))
        longest = max((len(units(raw)) for _, raw in block.strings), default=0)
        if (
            len(block.strings) >= min_strings
            and double * 2 >= len(block.strings)
            and longest >= min_longest
        ):
            blocks.append(block)
            covered = block.end
    return blocks


def words(data: bytes) -> dict[int, list[int]]:
    """Big-endian 32-bit words at even offsets, mapped to their offsets."""
    found: dict[int, list[int]] = {}
    for offset in range(0, len(data) - 3, 2):
        found.setdefault(struct.unpack_from(">I", data, offset)[0], []).append(offset)
    return found


def find_load_base(
    data: bytes, offsets: Iterable[int], word_map: dict[int, list[int]] | None = None
) -> tuple[int | None, int]:
    """Return the base at which the most string offsets are pointed to."""
    word_map = words(data) if word_map is None else word_map
    targets = sorted(set(offsets))
    best: tuple[int | None, int] = (None, 0)
    for low, high in BASE_RANGES:
        for base in range(low, high, BASE_STEP):
            count = sum(1 for offset in targets if base + offset in word_map)
            if count > best[1]:
                best = (base, count)
    return best


def references(
    word_map: dict[int, list[int]], base: int, offsets: Iterable[int]
) -> list[tuple[int, int]]:
    """(location, target offset) for every word equal to base + a string offset."""
    found = [
        (location, offset)
        for offset in set(offsets)
        for location in word_map.get(base + offset, [])
    ]
    return sorted(found)


def short_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()[:16]


def block_stats(block: Block) -> dict[str, object]:
    """Counts only: line lengths, character inventory, single-byte codes."""
    chars: Counter[int] = Counter()
    cells: Counter[int] = Counter()
    double: set[bytes] = set()
    single: Counter[str] = Counter()
    for _, raw in block.strings:
        parts = units(raw)
        chars[len(parts)] += 1
        cells[sum(len(part) for part in parts)] += 1
        for part in parts:
            if len(part) == 2:
                double.add(part)
            else:
                single[f"{part[0]:02X}"] += 1
    return {
        "max_chars": max(chars),
        "max_cells": max(cells),
        "chars_histogram": dict(sorted(chars.items())),
        "distinct_double_byte": len(double),
        "distinct_kanji": sum(1 for part in double if part[0] >= 0x88),
        "single_byte_counts": dict(sorted(single.items())),
    }


def census(
    path: Path, min_strings: int = 16, min_longest: int = 4
) -> dict[str, object] | None:
    """The census record of one file, or None if it holds no block."""
    data = path.read_bytes()
    blocks = find_blocks(data, min_strings, min_longest)
    if not blocks:
        return None
    offsets = [offset for block in blocks for offset, _ in block.strings]
    word_map = words(data)
    base, _ = find_load_base(data, offsets, word_map)
    refs = references(word_map, base, offsets) if base is not None else []
    referenced = Counter(target for _, target in refs)
    gaps = Counter(b[0] - a[0] for a, b in itertools.pairwise(refs))
    return {
        "file": path.name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "blocks": [
            {
                "start": block.start,
                "end": block.end,
                "strings": len(block.strings),
                "sha256": hashlib.sha256(data[block.start : block.end]).hexdigest(),
                "stats": block_stats(block),
                "table": [
                    [offset, len(raw), short_hash(raw), referenced[offset]]
                    for offset, raw in block.strings
                ],
            }
            for block in blocks
        ],
        "load_base": None if base is None else f"0x{base:08X}",
        "references": {
            "words": len(refs),
            "strings_referenced": len(referenced),
            "first_location": refs[0][0] if refs else None,
            "last_location": refs[-1][0] if refs else None,
            "location_gaps": dict(gaps.most_common(8)),
        },
    }


def compare(records: Sequence[dict[str, object]]) -> dict[str, object]:
    """Longest common run of string hashes between the first file and each other."""

    def hashes(record: dict[str, object]) -> list[str]:
        blocks = record["blocks"]
        assert isinstance(blocks, list)
        return [str(row[2]) for block in blocks for row in block["table"]]

    if len(records) < 2:
        return {}
    first = hashes(records[0])
    out: dict[str, object] = {}
    for other in records[1:]:
        second = hashes(other)
        prefix = 0
        while prefix < min(len(first), len(second)) and first[prefix] == second[prefix]:
            prefix += 1
        out[f"{records[0]['file']} vs {other['file']}"] = {
            "common_prefix_strings": prefix,
            "strings": [len(first), len(second)],
        }
    return out


def compact_lists(text: str) -> str:
    """Put each innermost JSON list (a table row) on one line."""
    return INNER_LIST.sub(
        lambda match: (
            "[" + ", ".join(item.strip() for item in match.group(1).split(",\n")) + "]"
        ),
        text,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--min-strings", type=int, default=16)
    parser.add_argument("--min-longest", type=int, default=4)
    parser.add_argument("--out", type=Path, help="write the JSON here")
    args = parser.parse_args(argv)
    records = [
        r
        for path in args.files
        if (r := census(path, args.min_strings, args.min_longest))
    ]
    result = {
        "scanned_files": len(args.files),
        "files_with_blocks": [record["file"] for record in records],
        "comparison": compare(records),
        "files": records,
    }
    text = compact_lists(json.dumps(result, indent=1)) + "\n"
    if args.out:
        args.out.write_text(text)
    summary = {k: v for k, v in result.items() if k != "files"}
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
