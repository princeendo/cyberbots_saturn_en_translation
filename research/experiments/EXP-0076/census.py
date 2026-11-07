"""EXP-0076: every surface of the Saturn-only pilots (lists 6-8), as numbers.

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0076/census.py \\
        [--out data/text/special_census.json]

Per list 6-8, from the untouched files and earlier records:

- **Story:** the list's story scenes (``data/text/pilot_census.json``,
  `RE-005`), their boxes (``data/text/reachability.json``, `TXT-010`) and the
  lines each box record points to (`STG0AS.BIN` ``0x060A5684``).
- **Win quotes:** `VICTORY.BIN`'s quote table ``0x0606FAA0`` + 16 x pilot,
  eight (scene, byte) entries (D-030); each scene's boxes in list 9.
- **VS captions:** the caption table ``0x0609CC22`` [pilot x 10 + stage]
  (`EXP-0032`).
- **Ending:** the boxes each Saturn-only ending was seen to open
  (``data/text/ending_surfaces_others.json``, `END-022`) and their lines in
  `END.BIN`'s own table (``tools.text.ending``).

Each box is checked against `TXT-010`'s classes; boxes and lines the
roster (lists 0-5) also shows are listed, for the story by line and for the
endings by box (``data/text/ending_surfaces.json``). Characters are 2-byte
codes, line breaks not counted. Numbers only (`AGENTS.md` rule 21).
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
import tools.text.dialogue as dl
from tools.text import ending

SRC = Path("local/extracted/saturn_jp")
BASE = 0x06060000
QUOTE_TABLE = 0x0606FAA0
LISTS = (6, 7, 8)
# Agent-read from forced select screens and list 7's opening (EXP-0076).
PILOTS = {6: "Devilotte", 7: "Chiyomaru", 8: "SHADE"}
# The select ring (STG0A.BIN 0x060643C0): moves from Jin.
RING_RIGHT = [0, 2, 1, 4, 5, 3, 7, 8, 6]


def chars(line: bytes) -> int:
    return (len(line) - line.count(b"\n")) // 2


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("data/text/special_census.json"))
    a = p.parse_args()
    stg = (SRC / "STG0AS.BIN").read_bytes()
    vic = (SRC / "VICTORY.BIN").read_bytes()
    end = (SRC / "END.BIN").read_bytes()

    def u32(x: int) -> int:
        return int(struct.unpack_from(">I", stg, x - BASE)[0])

    def u16(x: int) -> int:
        return int(struct.unpack_from(">H", stg, x - BASE)[0])

    lines = dl.line_table()
    text = [stg[off : off + n] for off, n in lines]
    address_line = {BASE + off: i for i, (off, _) in enumerate(lines)}
    box_lines: dict[int, list[int]] = {}
    for box in range(1074):
        entry = u32(dl.RECORDS + 4 * box) + 8
        while True:
            n = address_line.get(u32(entry))
            if n is not None:
                box_lines.setdefault(box, []).append(n)
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
    end_table = ending.end_lines()
    end_text = [end[off : off + n] for off, n in end_table]
    end_box_lines = ending.record_lines(end, end_table)

    reach = json.loads(Path("data/text/reachability.json").read_text())
    scene_boxes = {
        (int(e["list"]), int(s["scene"])): list(s["boxes"])
        for e in reach["lists"]
        for s in e["scene_boxes"]
    }
    box_class = {b: c for c, bs in reach["box_classes"].items() for b in bs}
    census = {
        int(e["list"]): e
        for e in json.loads(Path("data/text/pilot_census.json").read_text())["lists"]
    }
    roster_boxes = {
        b
        for n in range(6)
        for s in census[n].get("story_scenes", [])
        for b in scene_boxes[(n, s)]
    }
    roster_lines = {n for b in roster_boxes for n in box_lines.get(b, [])}
    roster_end_boxes = {
        int(o["box"])
        for e in json.loads(Path("data/text/ending_surfaces.json").read_text())["lists"]
        for o in e["openings"]
    }
    endings = {
        int(e["list"]): e
        for e in json.loads(Path("data/text/ending_surfaces_others.json").read_text())[
            "lists"
        ]
    }

    def summary(
        boxes: list[int], table: dict[int, list[int]], src: list[bytes]
    ) -> dict[str, Any]:
        ls = sorted({n for b in boxes for n in table.get(b, [])})
        return {
            "boxes": len(boxes),
            "lines": len(ls),
            "chars": sum(chars(src[n]) for n in ls),
            "line_ids": ls,
        }

    out_lists = []
    all_story: set[int] = set()
    for n in LISTS:
        story_scenes = list(census[n]["story_scenes"])
        story = sorted({b for s in story_scenes for b in scene_boxes[(n, s)]})
        all_story |= set(story)
        quote_entries = [
            tuple(
                vic[
                    QUOTE_TABLE - BASE + 16 * n + 2 * k : QUOTE_TABLE
                    - BASE
                    + 16 * n
                    + 2 * k
                    + 2
                ]
            )
            for k in range(8)
        ]
        quote_scenes = sorted({e[0] for e in quote_entries})
        quotes = sorted({b for s in quote_scenes for b in scene_boxes[(9, s)]})
        captions = [u16(dl.CAPTIONS + 2 * (10 * n + k)) for k in range(10)]
        caption_boxes = sorted({c for c in captions if c})
        opened = sorted({int(o["box"]) for o in endings[n]["openings"]})
        out_lists.append(
            {
                "list": n,
                "pilot": PILOTS[n],
                "select": {
                    "ring_position_right_of_jin": RING_RIGHT.index(n),
                    "moves_left_from_jin": len(RING_RIGHT) - RING_RIGHT.index(n),
                },
                "story": {
                    "scenes": story_scenes,
                    **summary(story, box_lines, text),
                    "box_list": story,
                    "classes": sorted({box_class.get(b, "?") for b in story}),
                    "boxes_shared_with_roster": sorted(set(story) & roster_boxes),
                    "lines_shared_with_roster": sorted(
                        {x for b in story for x in box_lines.get(b, [])} & roster_lines
                    ),
                },
                "win_quotes": {
                    "table_entries": [list(e) for e in quote_entries],
                    "scenes": quote_scenes,
                    **summary(quotes, box_lines, text),
                    "box_list": quotes,
                    "classes": sorted({box_class.get(b, "?") for b in quotes}),
                },
                "captions": {
                    "by_stage": captions,
                    **summary(caption_boxes, box_lines, text),
                    "box_list": caption_boxes,
                    "classes": sorted({box_class.get(b, "?") for b in caption_boxes}),
                },
                "ending": {
                    "posted": [int(x["scene"]) for x in endings[n]["posts"]],
                    **summary(opened, end_box_lines, end_text),
                    "box_list": opened,
                    "font": "KANJI.BIN (D-047)",
                    "boxes_shared_with_roster_endings": sorted(
                        set(opened) & roster_end_boxes
                    ),
                    "shared_after_dialogue": endings[n]["shared_after_dialogue"],
                },
            }
        )
    distinct = {
        "story_boxes": len(all_story),
        "story_lines": len({n for b in all_story for n in box_lines.get(b, [])}),
        "quote_boxes": len({b for e in out_lists for b in e["win_quotes"]["box_list"]}),
        "caption_boxes": len({b for e in out_lists for b in e["captions"]["box_list"]}),
        "ending_boxes": len({b for e in out_lists for b in e["ending"]["box_list"]}),
        "ending_lines": len({n for e in out_lists for n in e["ending"]["line_ids"]}),
    }
    report = {
        "task": "SPECIAL-010",
        "sources": {
            "files": str(SRC),
            "pilot_census": "data/text/pilot_census.json",
            "reachability": "data/text/reachability.json",
            "ending_surfaces_others": "data/text/ending_surfaces_others.json",
        },
        "lists": out_lists,
        "distinct": distinct,
    }
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    for e in out_lists:
        print(
            e["list"],
            e["pilot"],
            {
                k: (e[k]["boxes"], e[k]["lines"], e[k]["chars"])
                for k in ("story", "win_quotes", "captions", "ending")
            },
            e["story"]["classes"],
            "shared",
            e["story"]["lines_shared_with_roster"],
            e["ending"]["boxes_shared_with_roster_endings"],
        )
    print(distinct)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
