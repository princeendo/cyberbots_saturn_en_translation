"""EXP-0027: compare the arcade pilots as candidates for the second pilot.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/candidates.py ENGLISH_JSON

For Saturn pilot lists 1-5 (the arcade pilots, matched to the arcade's
pilots 1-5 by scene scripts, EXP-0027), the story scenes are the scene
numbers in that pilot's block of `STG0AS.BIN`'s scene posts
(``scene_posts.py``; block k is pilot k). A post computed into r5 is taken as
3, as in Jin's block (``r14`` = 3, EXP-0022). For each pilot it counts:

- story boxes, lines, and lines paired with an arcade slot equal to the box
  (D-022's rule; REF-006 as fixed);
- lines shared with boxes outside the pilot's story (they must be kept);
- distinct pairs, new pairs beyond Jin's, and the union with Jin's;
- boxes needing more than 3 rows, the line bytes needed, and the room in the
  pilot's own lines;

using ``tools.text.dialogue``'s wrapping. ``ENGLISH_JSON`` is the ignored
REF-003 decode, used for counts only. Prints JSON lines with no text.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.font import pairs
from tools.text.dialogue import wrap

BASE = 0x06060000
STG = Path("local/extracted/saturn_jp/STG0AS.BIN")


def main(english: Path) -> int:
    data = STG.read_bytes()

    def u16(a: int) -> int:
        return int.from_bytes(data[a - BASE : a - BASE + 2], "big")

    def u32(a: int) -> int:
        return int.from_bytes(data[a - BASE : a - BASE + 4], "big")

    scan = json.loads(
        subprocess.run(
            [sys.executable, "research/experiments/EXP-0027/scene_posts.py", str(STG)],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
    )
    blocks = [[3 if s is None else s for s in b] for b in scan["blocks"]]
    lists = [u32(0x060AAD24 + 4 * p) for p in range(11)]
    ordered = sorted(set(lists))
    starts = sorted({u32(0x060AA840 + 4 * k) for k in range(335)})
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    address = {BASE + off: i for i, (off, _, _, _) in enumerate(table)}
    ref006 = json.loads(Path("data/text/saturn_arcade_pairing.json").read_text())[
        "saturn"
    ]
    english_table = json.loads(english.read_text())["0x0B33AA"]

    def scene_scripts(p: int) -> list[int]:
        head = lists[p]
        nxt = [x for x in ordered if x > head]
        return [
            u32(head + 4 * k)
            for k in range(((nxt[0] if nxt else 0x060AAD24) - head) // 4)
        ]

    def boxes(script: int) -> list[int]:
        end = (
            next(x for x in starts if x > script)
            if script < starts[-1]
            else script + 0x80
        )
        out: list[int] = []
        for a in range(script, end, 2):
            w = u16(a)
            if w < 0x8000 and w not in out:
                out.append(w)
        return out

    def lines(box: int) -> list[int]:
        entry, out = u32(0x060A5684 + 4 * box) + 8, []
        while True:
            line = address.get(u32(entry))
            if line is not None:
                out.append(line)
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
        return out

    users: dict[int, set[int]] = {}
    for box in range(1074):
        for line in lines(box):
            users.setdefault(line, set()).add(box)

    def pair_set(slot: int) -> set[str]:
        return {
            p
            for row in wrap(english_table[slot])
            for p in pairs.split_pairs(row)
            if p != "  "
        }

    jin = json.loads(Path("data/translations/jin_pairing.json").read_text())
    jin_pairs = set().union(*(pair_set(p["arcade_slot"]) for p in jin["pairs"]))
    for pilot in range(1, 6):
        story = sorted(set(blocks[pilot]))
        scripts = scene_scripts(pilot)
        story_boxes = list(dict.fromkeys(b for k in story for b in boxes(scripts[k])))
        story_lines = sorted({n for b in story_boxes for n in lines(b)})
        box_slot = sum(
            1
            for b in story_boxes
            if all(ref006[n] and ref006[n][0] == b for n in lines(b))
        )
        shared = [n for n in story_lines if users.get(n, set()) - set(story_boxes)]
        with_english = [
            b for b in story_boxes if b < len(english_table) and english_table[b]
        ]
        own = set().union(*(pair_set(b) for b in with_english))
        rows = {b: wrap(english_table[b]) for b in with_english}
        needed = sum(
            ((2 * len(pairs.split_pairs(r)) + 1 + 3) & ~3)
            for rs in rows.values()
            for r in rs
        )
        room = sum(((table[n][1] + 1 + 3) & ~3) for n in story_lines if n not in shared)
        print(
            json.dumps(
                {
                    "pilot": pilot,
                    "story_scenes": len(story),
                    "boxes": len(story_boxes),
                    "lines": len(story_lines),
                    "boxes_paired_slot_for_slot": box_slot,
                    "boxes_with_english": len(with_english),
                    "shared_lines": shared,
                    "pairs": len(own),
                    "new_beyond_jin": len(own - jin_pairs),
                    "union_with_jin": len(own | jin_pairs),
                    "boxes_over_3_rows": sum(1 for rs in rows.values() if len(rs) > 3),
                    "bytes_needed": needed,
                    "room_in_own_lines": room,
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
