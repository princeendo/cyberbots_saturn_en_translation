"""EXP-0028: pair a pilot's story boxes with arcade slots by both games' scripts.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0028/pair_pilot.py \\
        local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \\
        --pilot 1 --boxes data/text/santana_boxes.json \\
        --out data/translations/santana_pairing.json

Generalizes ``research/experiments/EXP-0023/pair_jin.py`` (Jin, pilot 0). The
scenes compared are the box list's ``story_scenes`` (EXP-0027), or, for Jin,
21 and 0-15. For each story scene, it compares the arcade's slots for that
pilot (``0x12150``: per-pilot, then per-scene 16-bit offsets, D-022) with the
Saturn's boxes. Each box is paired with the slot of the same number, and each
line is labelled from REF-006 (as fixed in EXP-0023):

- ``exact`` or ``edited`` when its aligned slot is the box, or a slot whose
  English record is the box's own (REF-006 names the first such slot);
- ``aligned-to-slot-N`` when it aligns elsewhere;
- ``unaligned`` when it aligns nowhere.

It also records whether slot N has an English record and how many Japanese
lines it has. Writes numbers, labels and hashes only (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import read_record

SCRIPTS = 0x12150
EN_TABLE = 0x0B33AA
JP_TABLE = 0x0A30F6
JIN_SCENES = [21, *range(16)]


def u16(image: bytes, a: int) -> int:
    return int.from_bytes(image[a : a + 2], "big")


def u32(image: bytes, a: int) -> int:
    return int.from_bytes(image[a : a + 4], "big")


def arcade_scenes(image: bytes, pilot: int) -> list[list[int]]:
    pilots = SCRIPTS + u16(image, SCRIPTS + 2 * pilot)
    later = sorted(
        SCRIPTS + u16(image, SCRIPTS + 2 * k)
        for k in range(16)
        if SCRIPTS + u16(image, SCRIPTS + 2 * k) > pilots
    )
    scenes = []
    for n in range((later[0] - pilots) // 2):
        a = pilots + u16(image, pilots + 2 * n)
        slots: list[int] = []
        while True:
            w = u16(image, a)
            a += 2
            if w & 0xFF00 == 0xE000:
                break
            if 0xE100 <= w <= 0xE8FF or w & 0xF000 == 0xF000:
                continue
            if w & 0x7FFF not in slots:
                slots.append(w & 0x7FFF)
        scenes.append(slots)
    return scenes


def jp_lines(image: bytes, slot: int) -> list[int]:
    """Code count of each line of the Japanese record (0xFFFF breaks lines)."""
    a = u32(image, JP_TABLE + 4 * slot) + 8
    lines, n = [], 0
    while (code := u16(image, a)) >> 8:
        if code == 0xFFFF:
            lines.append(n)
            n = 0
        else:
            n += 1
        a += 2
    lines.append(n)
    return lines


def main(us: Path, jp: Path, pilot: int, boxes_path: Path, out: Path | None) -> int:
    us_image, jp_image = us.read_bytes(), jp.read_bytes()
    boxes = json.loads(boxes_path.read_text())
    in_scope = boxes.get("story_scenes", JIN_SCENES)
    ref006 = json.loads(Path("data/text/saturn_arcade_pairing.json").read_text())
    census = json.loads(Path("data/text/script_census.json").read_text())
    saturn_lengths = {}
    for f in census["files"]:
        if f["file"] == "STG0AS.BIN":
            for i, row in enumerate(f["blocks"][0]["table"]):
                saturn_lengths[i] = row[1]
    arcade = arcade_scenes(us_image, pilot)
    pairs = []
    mismatched_scenes = []
    shared_record_slots: set[int] = set()
    for scene in in_scope:
        sat = boxes["scenes"][scene]["boxes"]
        if [b["box"] for b in sat] != arcade[scene]:
            mismatched_scenes.append(scene)
        for b in sat:
            slot = b["box"]
            en = u32(us_image, EN_TABLE + 4 * slot)
            arcade_jp = jp_lines(jp_image, slot)
            english = read_record(us_image, en) if en else None
            labels = []
            for line in b["lines"]:
                p = ref006["saturn"][line]
                if p is not None and p[0] == slot:
                    labels.append(p[2])
                elif p is None:
                    labels.append("unaligned")
                elif u32(us_image, EN_TABLE + 4 * p[0]) == en:
                    # REF-006 names the first slot holding this record; this
                    # slot points to the same English record (EXP-0028).
                    labels.append(p[2])
                    shared_record_slots.add(p[0])
                else:
                    labels.append(f"aligned-to-slot-{p[0]}")
            pairs.append(
                {
                    "scene": scene,
                    "box": slot,
                    "arcade_slot": slot,
                    "saturn_lines": b["lines"],
                    "labels": labels,
                    "arcade_english_record": f"0x{en:06X}",
                    "english_characters": len(english.codes) if english else 0,
                    "arcade_japanese_line_lengths": arcade_jp,
                    "saturn_line_bytes": [saturn_lengths.get(x) for x in b["lines"]],
                    "evidence": "same scene script in both games (EXP-0028)"
                    if b["box"] in arcade[scene]
                    else "box not in the arcade scene",
                }
            )
    counts = {
        "boxes": len(pairs),
        "lines": sum(len(p["saturn_lines"]) for p in pairs),
        "exact": sum(p["labels"].count("exact") for p in pairs),
        "edited": sum(p["labels"].count("edited") for p in pairs),
        "unaligned": sum(p["labels"].count("unaligned") for p in pairs),
        "aligned_elsewhere": sum(
            1 for p in pairs for x in p["labels"] if x.startswith("aligned-to")
        ),
    }
    report = {
        "sources": {
            "cybotsu_program_sha256": hashlib.sha256(us_image).hexdigest(),
            "cybotsj_program_sha256": hashlib.sha256(jp_image).hexdigest(),
            "boxes": str(boxes_path),
            "pilot": pilot,
            "ref006": "data/text/saturn_arcade_pairing.json",
        },
        "arcade_scenes": {str(n): s for n, s in enumerate(arcade)},
        "scenes_with_different_scripts": mismatched_scenes,
        "slots_sharing_a_record_with_a_paired_box": sorted(shared_record_slots),
        "pairs": pairs,
        "counts": counts,
    }
    print(json.dumps({"mismatched": mismatched_scenes, **counts}))
    if out:
        out.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("us", type=Path)
    parser.add_argument("jp", type=Path)
    parser.add_argument("--pilot", type=int, default=0)
    parser.add_argument("--boxes", type=Path, default=Path("data/text/jin_boxes.json"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.us, args.jp, args.pilot, args.boxes, args.out))
