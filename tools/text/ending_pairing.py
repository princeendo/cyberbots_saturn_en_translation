"""Pair an ending's text units with the arcade's English (END-021).

Run from the repository root:

    ./invenv.sh python -m tools.text.ending_pairing \\
        local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \\
        --list 1 --out data/translations/santana_ending_pairing.json

Generalizes ``research/experiments/EXP-0041/pair_ending.py`` (commit
``ea2e69c``) from Jin's ending to any roster list. It writes numbers,
labels and hashes only (``AGENTS.md`` rule 21).

- **Units.** The boxes the ending is seen to open, in order
  (``data/text/ending_surfaces.json``, D-043). A posted script runs on into
  the next scenes, so the posted scripts alone are not enough. A unit is a
  (scene, box), where the scene is the post in force when the box first
  opens. The blank box 1072 is a unit with no slot.
- **Pairing.** The Saturn openings (less 1072) are aligned with the slots
  the arcade's story reader read in a forced run of the same ending
  (``cybotsu``; ``cybotsj`` must agree). A box and a slot with the same
  number pair. Otherwise a box that is not itself a slot number (a speaker
  name) pairs with the arcade's next slot that is not a box number. An
  opening with no such slot is left unpaired, as is a slot with no
  opening. Every box must pair with one slot at all its paired openings.
- **Labels.** Each Saturn line (`END.BIN`'s own copy of the line table) is
  compared with the same line of the slot's `cybotsj` Japanese
  (``0x0A30F6``, through ``data/text/arcade_jp_map.json``): ``exact``,
  ``edited`` (with ``difflib`` similarity) or ``no-counterpart``. A box
  whose slot has another number is also compared with the slot of its own
  number.
- **Surface.** From the box record's 8-byte header in `END.BIN` (table
  ``0x060817B4``): ``0x30`` in the first word is a caption, ``0x50`` in the
  third narration, ``0x8C`` in the second a dialogue box, and the rest of
  the ``0xAC`` boxes are speaker names (`EXP-0047`).
- **Names.** A speaker name is also compared with the arcade slot its box
  number + 9 gives (D-038's rule), and the file says whether that is the
  slot shown at the same place. Where they differ, the gate chooses.
- **English.** The slot's `cybotsu` record (``0x0B33AA``): address,
  character and line counts, and SHA-256, never the text.

Jin's image units (the cast roll's names and the QSound line, END-005) are
shared by every ending (D-043) and are written only for list 0.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from tools.reference.cybots_text import decode, long, read_record
from tools.text.arcade_pairing import read_jp_record

EN_TABLE = 0x0B33AA
JP_TABLE = 0x0A30F6
BLANK_BOX = 1072
NAME_SHIFT = 9  # Saturn speaker-name box N shows arcade name slot N + 9 (D-038)
BASE = 0x06060000
RECORDS = 0x060817B4
END_BIN = Path("local/extracted/saturn_jp/END.BIN")
SURFACES = Path("data/text/ending_surfaces.json")
SCRIPTS = Path("data/arcade/ending_scripts.json")
CODE_MAP = Path("data/text/arcade_jp_map.json")
CENSUS = Path("data/text/script_census.json")
PILOTS = ["Jin", "Santana", "Mary", "Arieta", "Gawaine", "Bao and Mao"]
FILE_NAMES = ["jin", "santana", "mary", "arieta", "gawaine", "baomao"]

# Jin's image units (END-005, EXP-0041), unchanged.
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


def surface_of(header: bytes) -> str:
    """The kind of box, from its record's 8-byte header (EXP-0047)."""
    words = [int.from_bytes(header[i : i + 2], "big") for i in range(0, 8, 2)]
    if words[0] == 0x30:
        return "caption"
    if words[2] == 0x50:
        return "narration"
    if words[1] == 0x8C:
        return "dialogue box"
    if words[2] == 0xAC:
        return "speaker name"
    raise ValueError(f"unknown box header {header.hex()}")


def align(
    boxes: Sequence[int], slots: Sequence[int]
) -> list[tuple[int | None, int | None]]:
    """Pair Saturn openings with arcade slot reads (module docstring)."""
    slot_set, box_set = set(slots), set(boxes)
    out: list[tuple[int | None, int | None]] = []
    i = j = 0
    while i < len(boxes) or j < len(slots):
        b = boxes[i] if i < len(boxes) else None
        s = slots[j] if j < len(slots) else None
        same_number = b is not None and b == s
        both_names = (
            b is not None and b not in slot_set and s is not None and s not in box_set
        )
        if same_number or both_names:
            out.append((b, s))
            i += 1
            j += 1
        elif b is not None and b not in slot_set:
            out.append((b, None))
            i += 1
        else:
            out.append((None, s))
            j += 1
    return out


def pair_list(n: int, us: bytes, jp: bytes) -> dict[str, Any]:
    end = END_BIN.read_bytes()
    census = json.loads(CENSUS.read_text())
    table = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0][
        "table"
    ]
    lines = [end[off : off + length] for off, length, *_ in table]
    line_at = {BASE + row[0]: k for k, row in enumerate(table)}
    code_map = {
        int(k, 16): bytes.fromhex(v)
        for k, v in json.loads(CODE_MAP.read_text()).items()
    }

    def u32(a: int) -> int:
        return int.from_bytes(end[a - BASE : a - BASE + 4], "big")

    def record(box: int) -> tuple[bytes, list[int]]:
        rec = u32(RECORDS + 4 * box)
        found, entry = [], rec + 8
        while True:
            found.append(line_at[u32(entry)])
            if end[entry + 4 - BASE : entry + 6 - BASE] != b"\xff\xff":
                return end[rec - BASE : rec - BASE + 8], found
            entry += 8

    def slot_jp(slot: int) -> list[bytes]:
        return [
            b"".join(code_map.get(c, b"??") for c in codes)
            for codes in read_jp_record(jp, long(jp, JP_TABLE + 4 * slot))
        ]

    def compare(saturn: list[int], slot: int) -> tuple[list[str], list[float]]:
        arcade = slot_jp(slot)
        labels, ratios = [], []
        for i, k in enumerate(saturn):
            if i >= len(arcade):
                labels.append("no-counterpart")
                ratios.append(0.0)
            elif arcade[i] == lines[k]:
                labels.append("exact")
                ratios.append(1.0)
            else:
                labels.append("edited")
                ratios.append(
                    round(difflib.SequenceMatcher(None, arcade[i], lines[k]).ratio(), 3)
                )
        return labels, ratios

    surfaces = json.loads(SURFACES.read_text())["lists"][n]
    openings = surfaces["openings"]
    posts = surfaces["posts"]
    reads = {a["set"]: [x["slot"] for x in a["slot_reads"]] for a in surfaces["arcade"]}
    if reads["cybotsu"] != reads["cybotsj"]:
        raise SystemExit(f"list {n}: cybotsu and cybotsj read different slots")
    shown = [o for o in openings if o["box"] != BLANK_BOX]
    pairs = align([o["box"] for o in shown], reads["cybotsu"])
    slot_of: dict[int, int] = {}
    unpaired_openings: dict[int, int] = {}
    unpaired_slots: list[int] = []
    for b, s in pairs:
        if b is not None and s is not None:
            if slot_of.setdefault(b, s) != s:
                raise SystemExit(f"list {n}: box {b} pairs with {slot_of[b]} and {s}")
        elif b is not None:
            unpaired_openings[b] = unpaired_openings.get(b, 0) + 1
        elif s is not None:
            unpaired_slots.append(s)

    def scene_at(frame: int) -> int:
        return int([p["scene"] for p in posts if p["frame"] <= frame][-1])

    units: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    positions: dict[int, int] = {}
    for o in openings:
        box, scene = o["box"], scene_at(o["open"])
        if (scene, box) in seen:
            continue
        seen.add((scene, box))
        header, saturn_lines = record(box)
        if box == BLANK_BOX:
            units.append(
                {
                    "unit": f"scene {scene} box {BLANK_BOX}",
                    "surface": "dialogue box",
                    "scene": scene,
                    "box": BLANK_BOX,
                    "saturn_lines": saturn_lines,
                    "saturn_line_bytes": [len(lines[k]) for k in saturn_lines],
                    "blank": all(lines[k] == b"\x81\x40" for k in saturn_lines),
                    "arcade_slot": None,
                    "label": "no-counterpart",
                    "no_official_english": False,
                    "handling": {"meaning": "blank; nothing to show"},
                    "evidence": "a full-width space; the arcade scene opens no "
                    "slot for it (D-037)",
                }
            )
            continue
        position = positions.get(scene, 0)
        positions[scene] = position + 1
        slot = slot_of.get(box)
        surface = surface_of(header)
        unit: dict[str, Any] = {
            "unit": f"scene {scene} box {box}",
            "surface": surface,
            "scene": scene,
            "position": position,
            "box": box,
            "saturn_lines": saturn_lines,
            "saturn_line_bytes": [len(lines[k]) for k in saturn_lines],
        }
        if slot is None:
            unit |= {
                "arcade_slot": None,
                "label": "no-counterpart",
                "no_official_english": True,
                "evidence": "no arcade slot is read where this box opens "
                "(D-043, EXP-0047)",
            }
            units.append(unit)
            continue
        labels, ratios = compare(saturn_lines, slot)
        en = long(us, EN_TABLE + 4 * slot)
        english = read_record(us, en)
        text = decode(english.codes)
        unit |= {
            "arcade_slot": slot,
            "slot_is_box_number": slot == box,
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
            "english_characters": len(english.codes),
            "english_lines": text.count("\n") + 1,
            "english_sha256": sha256(text.encode()),
            "no_official_english": False,
            "evidence": "same place in the boxes the Saturn opens and the slots "
            "the arcade's story reader reads, in forced runs of this ending "
            "(D-043, EXP-0046, EXP-0047)",
        }
        if slot != box:
            own_labels, own_ratios = compare(saturn_lines, box)
            unit["own_number_slot"] = {
                "slot": box,
                "line_labels": own_labels,
                "line_similarity": own_ratios,
            }
        if surface == "speaker name":
            rule = box + NAME_SHIFT
            rule_labels, rule_ratios = compare(saturn_lines, rule)
            unit["name_rule_slot"] = {
                "slot": rule,
                "line_labels": rule_labels,
                "line_similarity": rule_ratios,
                "same_as_placed_slot": rule == slot,
            }
        if box in unpaired_openings:
            unit["openings_without_an_arcade_slot"] = unpaired_openings[box]
        units.append(unit)
    if n == 0:
        units += image_units()
    counts: dict[str, int] = {}
    line_counts: dict[str, int] = {}
    for u in units:
        counts[u["label"]] = counts.get(u["label"], 0) + 1
        for x in u.get("line_labels", []):
            line_counts[x] = line_counts.get(x, 0) + 1
    return {
        "sources": {
            "cybotsu_program_sha256": sha256(us),
            "cybotsj_program_sha256": sha256(jp),
            "END.BIN": sha256(end),
            "ending_surfaces": str(SURFACES),
            "ending_surfaces_sha256": sha256(SURFACES.read_bytes()),
        },
        "list": n,
        "pilot": PILOTS[n],
        "units": units,
        "unpaired_arcade_slots": unpaired_slots,
        "shared_units": (
            None
            if n == 0
            else "the cast roll's names and the QSound line, as in "
            "jin_ending_pairing.json; every ending shows them (D-043)"
        ),
        "counts": {
            "units": len(units),
            "by_label": counts,
            "dialogue_lines": line_counts,
            "no_official_english": sum(u["no_official_english"] for u in units),
        },
    }


def image_units() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for k, name in enumerate(CAST):
        out.append(
            {
                "unit": f"cast roll name {k}",
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
    out.append(
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
    return out


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("us", type=Path)
    parser.add_argument("jp", type=Path)
    parser.add_argument("--list", type=int, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = pair_list(args.list, args.us.read_bytes(), args.jp.read_bytes())
    print(json.dumps(result["counts"]))
    for u in result["units"]:
        if u.get("arcade_slot") is not None or u["box" if "box" in u else "unit"]:
            print(
                u["unit"],
                u.get("surface"),
                "slot",
                u.get("arcade_slot"),
                u["label"],
                u.get("line_labels"),
                u.get("line_similarity"),
                u.get("openings_without_an_arcade_slot", ""),
            )
    if result["unpaired_arcade_slots"]:
        print("unpaired arcade slots", result["unpaired_arcade_slots"])
    if args.out:
        args.out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
