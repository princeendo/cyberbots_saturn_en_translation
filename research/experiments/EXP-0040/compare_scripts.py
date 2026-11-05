"""EXP-0040: the arcade's ending posts and scene scripts against the Saturn's.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0040/compare_scripts.py \\
        local/ref003/cybotsu-maincpu.bin local/win002/mame/cybotsu-0-c0000.asm \\
        local/ref003/cybotsj-maincpu.bin local/end004/mame/dasm-j/cybotsj-0-c0000.asm \\
        [--out data/arcade/ending_scripts.json]

Static; it writes numbers only (``AGENTS.md`` rule 21). For each arcade set
(the program image, plain for data, and MAME's debugger disassembly):

- **Dispatchers.** ``move.b ($6b2c,A5),D0`` (the ending number) followed by
  ``movea.l ($10,PC,D0.w),A0`` reads a table of 6 longword routine addresses,
  one per list 0-5 (``0xE496`` in `cybotsu`). It is read PC-relative, so
  through the decrypted opcode space; its words come from the disassembly.
- **Posts.** Every ``move.l #$1400000k,D1`` with ``moveq #s,D2`` at or after
  the first dispatcher is an ending post of list k, scene s (the poster
  ``0x163E``; the message is ``0x14000000`` + list, D2 the scene).
- **Scripts.** The interpreter's table (``lea (table,PC),A4`` before
  ``move.b ($15,A6),D0``: ``0x12150`` in `cybotsu`) gives per-list, then
  per-scene 16-bit offsets (``EXP-0028/pair_pilot.py``). A scene's opened
  slots are its words below ``0x8000`` up to ``0xE0xx``.

The Saturn side is ``data/text/ending_posts.json`` (``EXP-0039``). For each
list and posted scene it reports both arcade sets' opened slots and the
Saturn's opened boxes, and what differs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

SATURN = Path("data/text/ending_posts.json")
LISTS = 6


def u16(image: bytes, a: int) -> int:
    return int.from_bytes(image[a : a + 2], "big")


def u32(image: bytes, a: int) -> int:
    return int.from_bytes(image[a : a + 4], "big")


def read_set(image: bytes, asm: list[str]) -> dict[str, Any]:
    addr = {i: int(line[:6], 16) for i, line in enumerate(asm) if line[:6].strip()}
    table = scripts = 0
    for i, line in enumerate(asm):
        if re.search(r"move\.b\s+\(\$6b2c,A5\), D0", line) and re.search(
            r"movea\.l\s+\(\$10,PC,D0\.w\), A0", asm[i + 3]
        ):
            table = addr[i + 3] + 2 + 0x10
        if re.search(r"move\.b\s+\(\$15,A6\), D0", line):
            m = re.search(r"lea\s+\(\$([0-9a-f]+),PC\), A4", asm[i - 2])
            if m and not scripts:
                scripts = int(m.group(1), 16)
    # The table is read PC-relative, so through the decrypted opcode space:
    # take its words from the disassembly's hex column, not from the image.
    words: dict[int, int] = {}
    for line in asm:
        m = re.match(r"([0-9A-F]{6}): ((?:[0-9A-F]{4} ?)+)", line)
        if m:
            for n, w in enumerate(m.group(2).split()):
                words[int(m.group(1), 16) + 2 * n] = int(w, 16)
    dispatchers = [
        words[table + 4 * k] << 16 | words[table + 4 * k + 2] for k in range(LISTS)
    ]
    posts: dict[int, list[dict[str, int]]] = {k: [] for k in range(LISTS)}
    for i, line in enumerate(asm):
        m = re.search(r"move\.l\s+#\$1400000([0-9a-f]), D1", line)
        if not m or addr[i] < min(dispatchers) or int(m.group(1), 16) >= LISTS:
            continue  # lists 6-7 are the win-quote and other posts (D-030)
        for k in range(i - 3, i + 4):
            d2 = re.search(r"moveq\s+#\$([0-9a-f]+), D2", asm[k])
            if d2:
                posts[int(m.group(1), 16)].append(
                    {"at": addr[i], "scene": int(d2.group(1), 16)}
                )
                break

    def opened(lst: int, scene: int) -> list[int]:
        base = scripts + u16(image, scripts + 2 * lst)
        a = base + u16(image, base + 2 * scene)
        out: list[int] = []
        while (w := u16(image, a)) & 0xFF00 != 0xE000:
            if w < 0x8000 and w not in out:
                out.append(w)
            a += 2
        return out

    return {
        "dispatch_table": table,
        "dispatchers": dispatchers,
        "scripts": scripts,
        "posts": {k: [p["scene"] for p in v] for k, v in posts.items()},
        "opened": opened,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us_image", type=Path)
    parser.add_argument("us_asm", type=Path)
    parser.add_argument("jp_image", type=Path)
    parser.add_argument("jp_asm", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    sets = {
        name: read_set(image.read_bytes(), asm.read_text().splitlines())
        for name, image, asm in (
            ("cybotsu", args.us_image, args.us_asm),
            ("cybotsj", args.jp_image, args.jp_asm),
        )
    }
    saturn = json.loads(SATURN.read_text())["lists"]
    lists = []
    for k in range(LISTS):
        sat = {p["scene"]: [b["box"] for b in p["boxes"]] for p in saturn[k]["posts"]}
        scenes = []
        for s in sorted(set(sat) | set(sets["cybotsu"]["posts"][k])):
            u = sets["cybotsu"]["opened"](k, s)
            j = sets["cybotsj"]["opened"](k, s)
            b = sat.get(s)
            scenes.append(
                {
                    "scene": s,
                    "posted_by": [
                        n
                        for n, posted in (
                            ("saturn", list(sat)),
                            ("cybotsu", sets["cybotsu"]["posts"][k]),
                            ("cybotsj", sets["cybotsj"]["posts"][k]),
                        )
                        if s in posted
                    ],
                    "saturn_boxes": b,
                    "cybotsu_slots": u,
                    "cybotsj_slots": j,
                    "saturn_only": [x for x in (b or []) if x not in u],
                    "cybotsu_only": [x for x in u if x not in (b or [])],
                    "cybotsj_differs_from_cybotsu": j != u,
                }
            )
        lists.append(
            {
                "list": k,
                "saturn_posts": list(sat),
                "cybotsu_posts": sets["cybotsu"]["posts"][k],
                "cybotsj_posts": sets["cybotsj"]["posts"][k],
                "scenes": scenes,
            }
        )
    result = {
        "sources": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (args.us_image, args.jp_image, SATURN)
        },
        "sets": {
            n: {
                "dispatch_table": f"0x{s['dispatch_table']:06X}",
                "dispatchers": [f"0x{d:06X}" for d in s["dispatchers"]],
                "scripts": f"0x{s['scripts']:06X}",
            }
            for n, s in sets.items()
        },
        "lists": lists,
    }
    print(json.dumps(result["sets"]))
    for lst in lists:
        print(
            lst["list"],
            "posts S",
            lst["saturn_posts"],
            "U",
            lst["cybotsu_posts"],
            "J",
            lst["cybotsj_posts"],
        )
        for s in lst["scenes"]:
            print(
                "  ",
                s["scene"],
                s["posted_by"],
                "S-only",
                s["saturn_only"],
                "U-only",
                s["cybotsu_only"],
                "J!=U",
                s["cybotsj_differs_from_cybotsu"],
            )
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
