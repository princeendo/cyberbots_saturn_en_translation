"""EXP-0033: a census of the Saturn's 11 per-pilot scene lists (no text).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0033/census.py \\
        --routes research/experiments/EXP-0033/routes.json \\
        --out data/text/pilot_census.json

Inputs: ``STG0AS.BIN`` and ``END.BIN`` (``local/extracted/saturn_jp``),
``data/text/saturn_arcade_pairing.json`` (REF-006, D-011) and a routes file
(pilot select moves and first stage group per list, from cold boots).

For each list it records:
- **scenes**: all scenes of the list (``EXP-0022/box_list.py``);
- **story_scenes_posted**: the list's block of `STG0AS.BIN`'s scene posts
  (``EXP-0027/scene_posts.py``; block k is list k for k = 0-8; a post
  computed into r5 is taken as 3, as in Jin's block, EXP-0022);
- **ending_scenes_by_number**: for lists 0-8, the other scenes whose
  number `END.BIN` posts (``0x06066852``). `END.BIN`'s posts do not name a
  list, so this is by number only;
- **unposted_scenes**: scenes posted by neither file;
- **story boxes and lines**; the lines paired with the arcade slot of the
  same number as their box (REF-006's line-to-slot pairing); the Saturn-only
  lines (unpaired in REF-006, or past line 898); the lines also used by a
  box of another list (any scene, each script read only up to ``0xE000``:
  ``box_list.py`` reads past it into the next script or, for the last
  script, into the table that follows).

It writes numbers only (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0022"))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0027"))
import box_list  # type: ignore[import-not-found]
from scene_posts import blocks, posts  # type: ignore[import-not-found]

STG0AS = Path("local/extracted/saturn_jp/STG0AS.BIN")
END = Path("local/extracted/saturn_jp/END.BIN")
PAIRING = Path("data/text/saturn_arcade_pairing.json")
LISTS = 11
BASE = 0x06060000
PILOT_LISTS = 0x060AAD24
STORY_BLOCKS = 9
LAST_PAIRED_LINE = 898
NAMES = [
    "Jin",
    "Santana",
    "Mary",
    "Arieta",
    "Gawaine",
    "Bao and Mao",
    "Saturn-only list 6",
    "Saturn-only list 7",
    "Saturn-only list 8",
    "versus win quotes (D-030)",
    "speaker-name boxes (arcade list 7)",
]


POSTED_BY = ["STG0AS.BIN block; END.BIN by number"] * STORY_BLOCKS + [
    "VICTORY.BIN 0x06060B46, after a versus win (D-030)",
    "no Saturn post found; the arcade posts its list 7 at 0x6319C",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scripts_to_end(data: bytes, pilot: int) -> list[list[int]]:
    """Each scene's boxes, reading its script only up to ``0xE000``."""

    def u(a: int, n: int) -> int:
        return int.from_bytes(data[a - BASE : a - BASE + n], "big")

    starts = [u(PILOT_LISTS + 4 * p, 4) for p in range(LISTS)]
    end = min([a for a in starts if a > starts[pilot]] + [PILOT_LISTS])
    scenes = []
    for k in range((end - starts[pilot]) // 4):
        a, boxes = u(starts[pilot] + 4 * k, 4), []
        while (w := u(a, 2)) != 0xE000:
            if w < 0xC000 and w != 0xFFFF and (w & 0x7FFF) not in boxes:
                boxes.append(w & 0x7FFF)
            a += 2
        scenes.append(boxes)
    return scenes


def box_lists() -> list[dict[str, Any]]:
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for p in range(LISTS):
            target = Path(tmp) / f"{p}.json"
            with contextlib.redirect_stdout(io.StringIO()):
                box_list.main(STG0AS, p, target)
            out.append(json.loads(target.read_text()))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--routes", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    routes = json.loads(args.routes.read_text())["lists"]
    lists = box_lists()
    stg_blocks = blocks([s for _, s in posts(STG0AS.read_bytes(), 0x0606DBEA)])
    end_numbers = {s for _, s in posts(END.read_bytes(), 0x06066852) if s is not None}
    pairing = json.loads(PAIRING.read_text())["saturn"]
    slot_of = {n: entry[0] if entry else None for n, entry in enumerate(pairing)}

    data = STG0AS.read_bytes()
    lines_of_box = {
        b["box"]: b["lines"]
        for listing in lists
        for s in listing["scenes"]
        for b in s["boxes"]
    }
    all_lines = [
        {n for boxes in scripts_to_end(data, p) for b in boxes for n in lines_of_box[b]}
        for p in range(LISTS)
    ]
    census = []
    for p, listing in enumerate(lists):
        scenes = [s["scene"] for s in listing["scenes"]]
        posted: list[int] = []
        if p < STORY_BLOCKS:
            posted = [3 if s is None else s for s in stg_blocks[p]]
        story = sorted(set(posted))
        ends = end_numbers if p < STORY_BLOCKS else set()
        ending = [s for s in scenes if s not in story and s in ends]
        neither = [s for s in scenes if s not in story and s not in ends]
        boxes: list[int] = []
        box_of_line: dict[int, int] = {}
        for s in listing["scenes"]:
            if s["scene"] in story:
                for b in s["boxes"]:
                    if b["box"] not in boxes:
                        boxes.append(b["box"])
                    for n in b["lines"]:
                        box_of_line.setdefault(n, b["box"])
        lines = sorted(box_of_line)
        others = set().union(*(all_lines[k] for k in range(LISTS) if k != p))
        census.append(
            {
                "list": p,
                "name": NAMES[p],
                "posted_by": POSTED_BY[p],
                "scene_list": listing["scene_list"],
                "scenes": len(scenes),
                "story_scenes_posted": posted,
                "story_scenes": story,
                "ending_scenes_by_number": ending,
                "unposted_scenes": neither,
                "story_boxes": len(boxes),
                "story_box_range": [min(boxes), max(boxes)] if boxes else None,
                "story_lines": len(lines),
                "lines_paired_with_own_slot": len(
                    [n for n in lines if slot_of.get(n) == box_of_line[n]]
                ),
                "lines_paired_elsewhere": [
                    n
                    for n in lines
                    if slot_of.get(n) is not None and slot_of[n] != box_of_line[n]
                ],
                "saturn_only_lines": [
                    n for n in lines if n > LAST_PAIRED_LINE or slot_of.get(n) is None
                ],
                "lines_shared_with_other_lists": sorted(set(lines) & others),
                **routes.get(str(p), {}),
            }
        )
    result = {
        "sources": {
            "STG0AS.BIN": sha(STG0AS),
            "END.BIN": sha(END),
            "saturn_arcade_pairing.json": sha(PAIRING),
            "routes": sha(args.routes),
        },
        "end_bin_posted_numbers": sorted(end_numbers),
        "lists": census,
    }
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    for c in census:
        print(
            json.dumps(
                {
                    k: c[k]
                    for k in (
                        "list",
                        "scenes",
                        "story_scenes",
                        "ending_scenes_by_number",
                        "unposted_scenes",
                        "story_boxes",
                        "story_lines",
                        "lines_paired_with_own_slot",
                    )
                }
                | {
                    k: len(c[k])
                    for k in (
                        "lines_paired_elsewhere",
                        "saturn_only_lines",
                        "lines_shared_with_other_lists",
                    )
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
