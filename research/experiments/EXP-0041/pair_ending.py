"""EXP-0041: pair every text unit of Jin's ending with the arcade's.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0041/pair_ending.py \\
        local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \\
        [--out data/translations/jin_ending_pairing.json]

Static; it writes numbers, labels and hashes only (``AGENTS.md`` rule 21).

**Dialogue units** are the boxes `END.BIN` opens for list 0
(``data/text/ending_posts.json``, D-036). For each posted scene, the
Saturn's boxes less the blank box 1072 are matched, in order, to the arcade
scene's opened slots (``data/arcade/ending_scripts.json``, D-037); both
lists must have the same length. The match is the pairing: a box is shown
where the arcade shows its slot.

Each Saturn line (`END.BIN`'s own copy of the line table, D-008) is
labelled against the same line of the slot's `cybotsj` Japanese record
(``0x0A30F6``, decoded through ``data/text/arcade_jp_map.json``), as
``EXP-0035/check_lines.py`` does: ``exact``, ``edited`` (with ``difflib``
similarity) or ``no-counterpart``. A box is ``exact`` if all its lines are,
else ``edited``. For a box whose slot has another number, the line is also
compared with the slot of the box's own number, to show why that slot is
not the counterpart.

The English is the slot's `cybotsu` record (``0x0B33AA``): its address,
character count, line count and SHA-256 (never the text).

**Image units** (the cast roll's Japanese names, the QSound line) come from
D-035 and D-037; they are listed from the agent's review of both games'
screenshots (``EXP-0041/README.md``), with no arcade text.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import decode, long, read_record
from tools.text.arcade_pairing import read_jp_record

EN_TABLE = 0x0B33AA
JP_TABLE = 0x0A30F6
BLANK_BOX = 1072
SURFACES = {16: "dialogue box", 17: "dialogue box", 18: "narration"}
LIST = 0
END_BIN = Path("local/extracted/saturn_jp/END.BIN")
POSTS = Path("data/text/ending_posts.json")
SCRIPTS = Path("data/arcade/ending_scripts.json")
CODE_MAP = Path("data/text/arcade_jp_map.json")
CENSUS = Path("data/text/script_census.json")

# The cast roll, in screen order: the same ten entries and Latin names in
# both games (Saturn `local/end002/control` f06590-f09018; `cybotsu`
# `local/end004/mame/route-u` f13130-f15240). Only the Saturn and `cybotsj`
# draw a Japanese line over each Latin name. Labels are the project's names
# for who each entry shows, not the screen's text.
CAST = [
    "Santana",
    "Mary",
    "Arieta",
    "Gawaine",
    "Bao and Mao",
    "Devilotte and her two followers",
    "Chiyomaru and Tessan",
    "Shade",
    "G.O.D. (the last boss)",
    "Jin",
]


# The user's decisions for the units with no official English (2026-11-05,
# END-005), verbatim.
CAST_HANDLING = {
    "decision": "Hide, as US arcade (Recommended)",
    "date": "2026-11-05",
    "meaning": "remove the Japanese name image; the Latin name stays",
}
QSOUND_HANDLING = {
    "decision": "Erase the line (Recommended)",
    "date": "2026-11-05",
    "meaning": "blank the line's pixels; the English lines above stay",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("jp", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    us, jp = args.us.read_bytes(), args.jp.read_bytes()
    end = END_BIN.read_bytes()
    census = json.loads(CENSUS.read_text())
    table = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0][
        "table"
    ]
    lines = [end[off : off + n] for off, n, *_ in table]
    code_map = {
        int(k, 16): bytes.fromhex(v)
        for k, v in json.loads(CODE_MAP.read_text()).items()
    }

    def slot_jp(slot: int) -> list[bytes]:
        return [
            b"".join(code_map.get(c, b"??") for c in codes)
            for codes in read_jp_record(jp, long(jp, JP_TABLE + 4 * slot))
        ]

    def compare(saturn: list[int], slot: int) -> tuple[list[str], list[float]]:
        arcade = slot_jp(slot)
        labels, ratios = [], []
        for i, n in enumerate(saturn):
            if i >= len(arcade):
                labels.append("no-counterpart")
                ratios.append(0.0)
            elif arcade[i] == lines[n]:
                labels.append("exact")
                ratios.append(1.0)
            else:
                labels.append("edited")
                ratios.append(
                    round(difflib.SequenceMatcher(None, arcade[i], lines[n]).ratio(), 3)
                )
        return labels, ratios

    posts = json.loads(POSTS.read_text())["lists"][LIST]["posts"]
    arcade_scenes = {
        s["scene"]: s for s in json.loads(SCRIPTS.read_text())["lists"][LIST]["scenes"]
    }
    units: list[dict[str, Any]] = []
    for post in posts:
        scene = post["scene"]
        arcade = arcade_scenes[scene]
        assert arcade["cybotsu_slots"] == arcade["cybotsj_slots"]
        shown = [b for b in post["boxes"] if b["box"] != BLANK_BOX]
        slots = arcade["cybotsu_slots"]
        if len(shown) != len(slots):
            raise SystemExit(f"scene {scene}: {len(shown)} boxes, {len(slots)} slots")
        for b in post["boxes"]:
            if b["box"] == BLANK_BOX:
                units.append(
                    {
                        "unit": f"scene {scene} box {BLANK_BOX}",
                        "surface": "dialogue box",
                        "scene": scene,
                        "box": BLANK_BOX,
                        "saturn_lines": b["lines"],
                        "saturn_line_bytes": [len(lines[n]) for n in b["lines"]],
                        "blank": all(lines[n] == b"\x81\x40" for n in b["lines"]),
                        "arcade_slot": None,
                        "label": "no-counterpart",
                        "no_official_english": False,
                        "handling": {"meaning": "blank; nothing to show"},
                        "evidence": "a full-width space; the arcade scene opens no "
                        "slot for it (D-037)",
                    }
                )
                continue
        for position, (b, slot) in enumerate(zip(shown, slots, strict=True)):
            labels, ratios = compare(b["lines"], slot)
            en = long(us, EN_TABLE + 4 * slot)
            record = read_record(us, en)
            text = decode(record.codes)
            unit: dict[str, Any] = {
                "unit": f"scene {scene} box {b['box']}",
                "surface": SURFACES.get(scene, "caption"),
                "scene": scene,
                "position": position,
                "box": b["box"],
                "saturn_lines": b["lines"],
                "saturn_line_bytes": [len(lines[n]) for n in b["lines"]],
                "arcade_slot": slot,
                "slot_is_box_number": slot == b["box"],
                "line_labels": labels,
                "line_similarity": ratios,
                "arcade_japanese_line_count": len(slot_jp(slot)),
                "arcade_unmapped_codes": sorted(
                    {
                        f"0x{c:X}"
                        for codes in read_jp_record(jp, long(jp, JP_TABLE + 4 * slot))
                        for c in codes
                        if c not in code_map
                    }
                ),
                "label": "exact" if set(labels) == {"exact"} else "edited",
                "arcade_english_record": f"0x{en:06X}",
                "english_characters": len(record.codes),
                "english_lines": text.count("\n") + 1,
                "english_sha256": sha256(text.encode()),
                "no_official_english": False,
                "evidence": "same position in the scene script of both games "
                "(D-036, D-037); the arcade's story reader reads this slot "
                "while the box is shown (EXP-0040)",
            }
            if slot != b["box"]:
                own_labels, own_ratios = compare(b["lines"], b["box"])
                unit["surface"] = "speaker name"
                unit["own_number_slot"] = {
                    "slot": b["box"],
                    "line_labels": own_labels,
                    "line_similarity": own_ratios,
                }
            units.append(unit)
    for n, name in enumerate(CAST):
        units.append(
            {
                "unit": f"cast roll name {n}",
                "surface": "cast roll name (image)",
                "entry": name,
                "latin_line": "the same on the Saturn, cybotsu and cybotsj",
                "arcade_slot": None,
                "label": "no-counterpart",
                "no_official_english": True,
                "handling": CAST_HANDLING,
                "evidence": "a whole-name sprite decoded from KEND_1.BIN (D-035); "
                "cybotsu shows only the Latin name, cybotsj shows a Japanese "
                "line as the Saturn (D-037)",
            }
        )
    units.append(
        {
            "unit": "QSound notice, Japanese line",
            "surface": "QSound notice (image)",
            "arcade_slot": None,
            "label": "no-counterpart",
            "no_official_english": True,
            "handling": QSOUND_HANDLING,
            "evidence": "pixels of QSD.PIX, bitmap rows 180-189 (D-035); the "
            "arcade ending has no QSound notice (D-037)",
        }
    )
    counts: dict[str, int] = {}
    for u in units:
        counts[u["label"]] = counts.get(u["label"], 0) + 1
    line_counts: dict[str, int] = {}
    for u in units:
        for x in u.get("line_labels", []):
            line_counts[x] = line_counts.get(x, 0) + 1
    result = {
        "sources": {
            "cybotsu_program_sha256": sha256(us),
            "cybotsj_program_sha256": sha256(jp),
            "END.BIN": sha256(end),
            "ending_posts": str(POSTS),
            "ending_scripts": str(SCRIPTS),
        },
        "list": LIST,
        "units": units,
        "counts": {
            "units": len(units),
            "by_label": counts,
            "dialogue_lines": line_counts,
            "no_official_english": sum(u["no_official_english"] for u in units),
            "new_text_needed": 0,
        },
    }
    print(json.dumps(result["counts"]))
    for u in units:
        if "arcade_slot" in u and u["arcade_slot"] is not None:
            print(
                u["unit"],
                "slot",
                u["arcade_slot"],
                u["label"],
                u["line_labels"],
                u["line_similarity"],
                u.get("own_number_slot", ""),
            )
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
