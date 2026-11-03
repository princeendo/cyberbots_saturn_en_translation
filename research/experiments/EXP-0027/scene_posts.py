"""EXP-0027: list the story-scene posts in a stage overlay, grouped by pilot.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/scene_posts.py \\
        FILE [--post 0x0606DBEA]

``FILE`` is loaded at ``0x06060000`` (D-017). A scene is posted by a call to
the post routine (``0x0606DBEA`` in `STG0AS.BIN`, EXP-0022) with the scene
number in r5. This finds every ``mov.l @(disp,pc),Rn`` that loads the
routine's address and is followed within 13 instructions by ``jsr``/``jmp
@Rn``. The scene is the last ``mov #imm,r5`` from 12 instructions before
the load to the delay slot. A ``mov Rm,r5`` is reported as ``None``.

Posts are grouped into blocks: a block starts at a post greater than 15
that is followed by a post of 0 (each pilot's opening narration, then scene
0; EXP-0027). Prints JSON: the posts, and the blocks as lists of scene
numbers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BASE = 0x06060000


def posts(data: bytes, routine: int) -> list[tuple[int, int | None]]:
    def u16(o: int) -> int:
        return int.from_bytes(data[o : o + 2], "big")

    def u32(o: int) -> int:
        return int.from_bytes(data[o : o + 4], "big")

    found: list[tuple[int, int | None]] = []
    for o in range(0, len(data) - 2, 2):
        w = u16(o)
        if w & 0xF000 != 0xD000:
            continue
        n = (w >> 8) & 0xF
        literal = ((o + 4) & ~3) + (w & 0xFF) * 4
        if literal + 4 > len(data) or u32(literal) != routine:
            continue
        for k in range(1, 14):
            x = u16(o + 2 * k)
            if x in (0x400B | (n << 8), 0x402B | (n << 8)):
                scene: int | None = None
                for j in range(-12, k + 2):
                    y = u16(o + 2 * j)
                    if y & 0xFF00 == 0xE500:
                        scene = y & 0xFF
                    elif y & 0xF00F == 0x6003 and (y >> 8) & 0xF == 5:
                        scene = None
                found.append((BASE + o, scene))
                break
    return found


def blocks(values: list[int | None]) -> list[list[int | None]]:
    out: list[list[int | None]] = []
    current: list[int | None] = []
    for i, v in enumerate(values):
        nxt = values[i + 1] if i + 1 < len(values) else None
        if isinstance(v, int) and v > 15 and nxt == 0 and current:
            out.append(current)
            current = []
        current.append(v)
    out.append(current)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--post", type=lambda s: int(s, 0), default=0x0606DBEA)
    args = parser.parse_args()
    found = posts(args.file.read_bytes(), args.post)
    print(
        json.dumps(
            {
                "posts": [[f"0x{a:08X}", s] for a, s in found],
                "blocks": blocks([s for _, s in found]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
