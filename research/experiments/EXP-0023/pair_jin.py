"""EXP-0023: pair Jin's Saturn boxes with arcade slots by both games' scripts.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0023/pair_jin.py \\
        local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \\
        --out data/translations/jin_pairing.json

The arcade program images are the decrypted, word-ordered dumps made by
``tools/reference/cybots_text.py`` (REF-003). The script reads:

- the arcade dialogue scripts: ``0x12150`` holds 16-bit offsets per pilot,
  then per scene, to a script; a word ``0xE000`` ends it, ``0xE1xx``-
  ``0xE8xx`` and ``0xFxxx`` are commands, and any other word is a slot
  (``0x8000`` closes it), as at ``0x11CC6`` (EXP-0009);
- Jin's Saturn scenes and boxes from ``data/text/jin_boxes.json`` (EXP-0022);
- the REF-006 text alignment ``data/text/saturn_arcade_pairing.json``;
- the arcade English (``0x0B33AA``) and Japanese (``0x0A30F6``, ``cybotsj``)
  slot tables, to check that each slot has a record, and to count arcade
  Japanese lines.

For every Saturn scene 21 and 0-15, it compares the arcade scene's slots with
the Saturn scene's boxes. Each box is paired with the slot of the same
number, and each line is labelled: ``exact`` or ``edited`` (REF-006), or
``expanded`` (no arcade Japanese line aligns, and the Saturn text is longer
than the slot's Japanese). Writes numbers, labels and hashes only; no text
(``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCRIPTS = 0x12150
EN_TABLE = 0x0B33AA
JP_TABLE = 0x0A30F6
IN_SCOPE = [21, *range(16)]


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


def main(us: Path, jp: Path, out: Path | None) -> int:
    us_image, jp_image = us.read_bytes(), jp.read_bytes()
    boxes = json.loads(Path("data/text/jin_boxes.json").read_text())
    ref006 = json.loads(Path("data/text/saturn_arcade_pairing.json").read_text())
    census = json.loads(Path("data/text/script_census.json").read_text())
    saturn_lengths = {}
    for f in census["files"]:
        if f["file"] == "STG0AS.BIN":
            for i, row in enumerate(f["blocks"][0]["table"]):
                saturn_lengths[i] = row[1]
    arcade = arcade_scenes(us_image, 0)
    pairs = []
    mismatched_scenes = []
    for scene in IN_SCOPE:
        sat = boxes["scenes"][scene]["boxes"]
        if [b["box"] for b in sat] != arcade[scene]:
            mismatched_scenes.append(scene)
        for b in sat:
            slot = b["box"]
            en = u32(us_image, EN_TABLE + 4 * slot)
            arcade_jp = jp_lines(jp_image, slot)
            labels = []
            for line in b["lines"]:
                p = ref006["saturn"][line]
                if p is not None and p[0] == slot:
                    labels.append(p[2])
                elif p is None:
                    labels.append("expanded")
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
                    "arcade_japanese_line_lengths": arcade_jp,
                    "saturn_line_bytes": [saturn_lengths.get(x) for x in b["lines"]],
                    "evidence": "same scene script in both games (EXP-0023)",
                }
            )
    counts = {
        "boxes": len(pairs),
        "lines": sum(len(p["saturn_lines"]) for p in pairs),
        "exact": sum(p["labels"].count("exact") for p in pairs),
        "edited": sum(p["labels"].count("edited") for p in pairs),
        "expanded": sum(p["labels"].count("expanded") for p in pairs),
        "boxes_with_expanded_lines": sum(1 for p in pairs if "expanded" in p["labels"]),
    }
    report = {
        "sources": {
            "cybotsu_program_sha256": hashlib.sha256(us_image).hexdigest(),
            "cybotsj_program_sha256": hashlib.sha256(jp_image).hexdigest(),
            "jin_boxes": "data/text/jin_boxes.json",
            "ref006": "data/text/saturn_arcade_pairing.json",
        },
        "arcade_jin_scenes": {str(n): s for n, s in enumerate(arcade)},
        "scenes_with_different_scripts": mismatched_scenes,
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
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.us, args.jp, args.out))
