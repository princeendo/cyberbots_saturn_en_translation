"""Pair the Saturn dialogue lines with the arcade dialogue slots (`REF-006`).

Run from the repository root:

    ./invenv.sh python -m tools.text.arcade_pairing \\
        --driver local/mame_src/cps2.cpp --set cybotsj --rompath local/arcade \\
        --saturn local/extracted/saturn_jp/VICTORY.BIN \\
        --map-out data/text/arcade_jp_map.json \\
        --out data/text/saturn_arcade_pairing.json

Arcade Japanese records (`EXP-0010`) use the record layout of
`tools.reference.cybots_text` but 16-bit big-endian character codes, with
``0xFFFF`` as a line break and a word whose high byte is ``0x00`` ending the
text. Each Saturn line (D-008) corresponds to one line of an arcade record.

1. **Map.** The code-to-character map is learned from the two scripts
   themselves: the leading lines that agree in length pair up in order; then,
   repeatedly, an arcade line whose known codes agree with exactly one
   distinct Saturn line of the same length teaches its unknown codes. Votes
   that disagree are counted, never resolved silently.
2. **Exact pairs.** The decoded arcade lines and the Saturn lines are aligned
   in order by a longest common subsequence of identical lines.
3. **Edited pairs.** An unpaired arcade line is paired with the most similar
   unpaired Saturn line between its paired neighbours when the similarity
   (``difflib`` ratio) is at least ``--min-ratio``.

The arcade uses one slot number for every language (`EXP-0009`, `EXP-0010`),
so a Saturn line's arcade slot is also its English slot. The outputs hold
indexes, slots, codes and counts; the map holds characters per code, not
lines of text (`AGENTS.md` rule 21).
"""

from __future__ import annotations

import argparse
import difflib
import json
from array import array
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.cold_boot import sha256
from tools.reference.cybots_text import build_program, find_tables, long
from tools.reference.mame_audit import parse_driver
from tools.text.script_census import find_blocks, units

LINE_BREAK = 0xFFFF
Line = tuple[bytes, ...]
CodeLine = tuple[int, ...]


def read_jp_record(image: bytes, address: int) -> list[CodeLine]:
    """The lines of one 16-bit record: codes after the 8-byte header."""
    lines: list[CodeLine] = []
    current: list[int] = []
    offset = address + 8
    while True:
        code = int.from_bytes(image[offset : offset + 2], "big")
        if code >> 8 == 0:
            break
        if code == LINE_BREAK:
            lines.append(tuple(current))
            current = []
        else:
            current.append(code)
        offset += 2
    lines.append(tuple(current))
    return lines


def record_lines(
    image: bytes, table: int, slots: int
) -> list[tuple[int, int, CodeLine]]:
    """(slot, line within record, codes), each distinct record once, slot order."""
    out = []
    seen: set[int] = set()
    for slot in range(slots):
        address = long(image, table + 4 * slot)
        if address in seen:
            continue
        seen.add(address)
        for index, codes in enumerate(read_jp_record(image, address)):
            out.append((slot, index, codes))
    return out


def learn_map(
    arcade: Sequence[CodeLine], saturn: Sequence[Line], rounds: int = 16
) -> tuple[dict[int, bytes], int]:
    """(code -> character, number of codes with conflicting votes)."""
    votes: defaultdict[int, Counter[bytes]] = defaultdict(Counter)
    for codes, line in zip(arcade, saturn, strict=False):
        if len(codes) != len(line):
            break
        for code, char in zip(codes, line, strict=True):
            votes[code][char] += 1
    by_length: defaultdict[int, list[Line]] = defaultdict(list)
    for line in saturn:
        by_length[len(line)].append(line)
    taught: set[int] = set()
    for _ in range(rounds):
        mapping = {code: v.most_common(1)[0][0] for code, v in votes.items()}
        learned = 0
        for index, codes in enumerate(arcade):
            if index in taught or not codes:
                continue
            known = [(n, mapping[c]) for n, c in enumerate(codes) if c in mapping]
            if len(known) < max(2, len(codes) / 2):
                continue
            fits = {
                line
                for line in by_length[len(codes)]
                if all(line[n] == char for n, char in known)
            }
            if len(fits) == 1:
                (line,) = fits
                for code, char in zip(codes, line, strict=True):
                    votes[code][char] += 1
                taught.add(index)
                learned += 1
        if not learned:
            break
    mapping = {code: v.most_common(1)[0][0] for code, v in votes.items()}
    return mapping, sum(1 for v in votes.values() if len(v) > 1)


def decode(codes: CodeLine, mapping: dict[int, bytes]) -> Line:
    return tuple(mapping.get(code, b"?") for code in codes)


def align(first: Sequence[Line], second: Sequence[Line]) -> list[tuple[int, int]]:
    """In-order pairs of identical lines (longest common subsequence)."""
    rows, cols = len(first), len(second)
    table = [array("H", [0]) * (cols + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        here, below, item = table[i], table[i + 1], first[i]
        for j in range(cols - 1, -1, -1):
            if item == second[j]:
                here[j] = below[j + 1] + 1
            else:
                here[j] = max(below[j], here[j + 1])
    pairs = []
    i = j = 0
    while i < rows and j < cols:
        if first[i] == second[j]:
            pairs.append((i, j))
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            i += 1
        else:
            j += 1
    return pairs


def edited_pairs(
    first: Sequence[Line],
    second: Sequence[Line],
    exact: Sequence[tuple[int, int]],
    min_ratio: float,
) -> list[tuple[int, int, float]]:
    """Unpaired lines matched within the gap between their paired neighbours."""
    paired_first = {i for i, _ in exact}
    used = {j for _, j in exact}
    anchors = sorted(exact)
    out = []
    for i, item in enumerate(first):
        if i in paired_first or not item:
            continue
        low = max((j for a, j in anchors if a < i), default=-1)
        high = min((j for a, j in anchors if a > i), default=len(second))
        best = max(
            (
                (difflib.SequenceMatcher(None, item, second[j]).ratio(), j)
                for j in range(low + 1, high)
                if j not in used
            ),
            default=(0.0, -1),
        )
        if best[0] >= min_ratio:
            out.append((i, best[1], round(best[0], 3)))
            used.add(best[1])
    return out


def runs(indexes: Sequence[int]) -> list[list[int]]:
    """Consecutive runs as [first, last]."""
    out: list[list[int]] = []
    for index in sorted(indexes):
        if out and out[-1][1] == index - 1:
            out[-1][1] = index
        else:
            out.append([index, index])
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--set", dest="set_name", default="cybotsj")
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--saturn", type=Path, required=True)
    parser.add_argument("--saturn-lines", type=int, default=1851)
    parser.add_argument("--min-ratio", type=float, default=0.6)
    parser.add_argument("--map-out", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    romset = parse_driver(args.driver.read_text(encoding="latin-1"))[args.set_name]
    archives = [args.rompath / f"{args.set_name}.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    image = build_program([p for p in archives if p.exists()], romset)
    table, slots = find_tables(image)[0]  # the Japanese table comes first (D-009)
    arcade = record_lines(image, table, slots)

    block = find_blocks(args.saturn.read_bytes())[0]
    saturn = [tuple(units(raw)) for _, raw in block.strings[: args.saturn_lines]]

    mapping, conflicts = learn_map([codes for *_, codes in arcade], saturn)
    decoded = [decode(codes, mapping) for *_, codes in arcade]
    exact = align(decoded, saturn)
    edited = edited_pairs(decoded, saturn, exact, args.min_ratio)
    pair_of = {j: (i, "exact", 1.0) for i, j in exact} | {
        j: (i, "edited", r) for i, j, r in edited
    }
    unpaired = [j for j in range(len(saturn)) if j not in pair_of]
    paired_arcade = {i for i, *_ in pair_of.values()}
    codes_seen = Counter(c for *_, codes in arcade for c in codes)
    result = {
        "arcade_set": args.set_name,
        "arcade_table": f"0x{table:06X}",
        "arcade_slots": slots,
        "arcade_lines": len(arcade),
        "saturn_file": args.saturn.name,
        "saturn_sha256": sha256(args.saturn),
        "saturn_lines": len(saturn),
        "map": {
            "codes": len(codes_seen),
            "mapped": sum(1 for c in codes_seen if c in mapping),
            "unmapped_codes": sorted(
                f"{c:04X}" for c in codes_seen if c not in mapping
            ),
            "conflicting_codes": conflicts,
        },
        "pairs": {"exact": len(exact), "edited": len(edited)},
        "saturn_unpaired_runs": runs(unpaired),
        "arcade_unpaired": [
            [arcade[i][0], arcade[i][1]]
            for i in range(len(arcade))
            if i not in paired_arcade
        ],
        # Per Saturn line: [arcade slot, line in record, exact|edited, ratio].
        "saturn": [
            None if j not in pair_of else [*arcade[pair_of[j][0]][:2], *pair_of[j][1:]]
            for j in range(len(saturn))
        ],
    }
    if args.map_out:
        codes_out = {f"{c:04X}": ch.hex().upper() for c, ch in sorted(mapping.items())}
        args.map_out.write_text(json.dumps(codes_out, indent=0) + "\n")
    if args.out:
        args.out.write_text(json.dumps(result, separators=(",", ":")) + "\n")
    summary = {
        k: v for k, v in result.items() if k not in ("saturn", "arcade_unpaired")
    }
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
