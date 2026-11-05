"""EXP-0042: the lines no ending box shows, and a marker image to test them.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0042/room.py \\
        [--out research/experiments/EXP-0042/room.json] \\
        [--image build/end010/room]

Static, plus one test image; it writes numbers only. `END.BIN`'s line table
(``data/text/script_census.json``) holds the 1,851 dialogue lines and, after
them, ASCII file names. Only lines that a box record points to (record table
``0x060817B4``, D-036) are candidates; the file names and the one line no
record points to are not.

- **Shown:** the lines of every box an ending posts (``ending_posts.json``,
  all 9 lists).
- **Room candidates:** the other referenced lines, merged into byte spans
  (each line with its NUL, 4-byte aligned). Every address a shown box's
  record points to (read up to its NUL) must fall outside them.

With ``--image``, writes a test `END.BIN` whose candidate lines hold the
marker code ``0x82A0`` (a table code) in place of each 2-byte character,
NULs kept, and patches it into ``IMAGE/image`` from the untouched source.
It also prints the read-breakpoint ranges (cached ``0x06…`` and
cache-through ``0x26…`` bus addresses) for ``probe.py --read-bp``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image
from tools.font import kanji

BASE = 0x06060000
RECORDS = 0x060817B4
BOXES = 1074
CODE_TABLE = 0x26EAC
MARKER = 0x82A0
END_BIN = Path("local/extracted/saturn_jp/END.BIN")
CENSUS = Path("data/text/script_census.json")
POSTS = Path("data/text/ending_posts.json")
SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
MANIFEST = Path("references/saturn_jp/README.md")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"


def aligned(length: int) -> int:
    return (length + 1 + 3) & ~3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--image", type=Path)
    args = parser.parse_args()
    end = END_BIN.read_bytes()
    table = next(
        f for f in json.loads(CENSUS.read_text())["files"] if f["file"] == "END.BIN"
    )["blocks"][0]["table"]
    line_at = {BASE + row[0]: n for n, row in enumerate(table)}

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    def u16(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 2], "big")

    pointers: dict[int, list[int]] = {}
    for box in range(BOXES):
        entry = u32(RECORDS + 4 * box) + 8
        while True:
            pointers.setdefault(box, []).append(u32(entry))
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
    box_lines = {
        b: [line_at[p] for p in ps if p in line_at] for b, ps in pointers.items()
    }
    odd = {b: [hex(p) for p in ps if p not in line_at] for b, ps in pointers.items()}
    odd = {b: v for b, v in odd.items() if v}
    referenced = {n for v in box_lines.values() for n in v}
    posts = json.loads(POSTS.read_text())
    shown_boxes = {
        b["box"] for lst in posts["lists"] for p in lst["posts"] for b in p["boxes"]
    }
    shown = {n for b in shown_boxes for n in box_lines[b]}
    room = sorted(referenced - shown)
    spans: list[list[int]] = []
    for n in room:
        start = table[n][0]
        stop = start + aligned(table[n][1])
        if spans and spans[-1][1] == start:
            spans[-1][1] = stop
        else:
            spans.append([start, stop])

    def inside(offset: int) -> bool:
        return any(s <= offset < e for s, e in spans)

    clashes = []
    for b in shown_boxes:
        for p in pointers[b]:
            off = p - BASE
            stop = end.index(b"\0", off)
            if any(inside(x) for x in range(off, stop + 1)):
                clashes.append({"box": b, "pointer": f"0x{p:08X}"})
    if clashes:
        raise SystemExit(f"shown boxes point into the room: {clashes}")
    result: dict[str, Any] = {
        "sources": {
            "END.BIN": hashlib.sha256(end).hexdigest(),
            "census": str(CENSUS),
            "posts": str(POSTS),
        },
        "table_lines": len(table),
        "referenced_lines": len(referenced),
        "unreferenced_dialogue_lines": [
            n for n in range(max(referenced) + 1) if n not in referenced
        ],
        "boxes_pointing_inside_a_line": odd,
        "shown_boxes": len(shown_boxes),
        "shown_lines": len(shown),
        "room_lines": len(room),
        "room_bytes": sum(e - s for s, e in spans),
        "spans": [[f"0x{s:05X}", f"0x{e:05X}"] for s, e in spans],
    }
    ranges = [
        f"{prefix + BASE + s:08X}-{prefix + BASE + e - 1:08X}"
        for prefix in (0, 0x20000000)
        for s, e in spans
    ]
    if args.image:
        if MARKER not in kanji.read_code_table(end, CODE_TABLE):
            raise SystemExit("marker code not in END.BIN's table")
        test = bytearray(end)
        for n in room:
            off, length = table[n][0], table[n][1]
            if length % 2:
                raise SystemExit(f"line {n} has an odd length")
            test[off : off + length] = MARKER.to_bytes(2, "big") * (length // 2)
        args.image.mkdir(parents=True, exist_ok=False)
        (args.image / "END.BIN").write_bytes(test)
        result["marker_end_bin"] = hashlib.sha256(test).hexdigest()
        result["changed_bytes"] = sum(
            1 for a, b in zip(end, test, strict=True) if a != b
        )
        code = patch_image.main(
            [
                "--source-dir",
                str(SOURCE_DIR),
                "--manifest",
                str(MANIFEST),
                "--track",
                TRACK,
                "--file",
                "END.BIN;1",
                "--data",
                str(args.image / "END.BIN"),
                "--out-dir",
                str(args.image / "image"),
            ]
        )
        if code:
            return code
    print(json.dumps({k: v for k, v in result.items() if k != "spans"}))
    print(",".join(ranges))
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
