"""EXP-0077: do the Saturn-only pilots' lines have official arcade English?

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0077/official.py \\
        [--min-ratio 0.6] [--out data/text/special_official.json]

1. **Arcade bounds** (both sets, from the data images): the pilot-select
   ring at ``0xCE00`` (six (left, right) pairs, read through ``A0`` after
   ``lea ($CE00,PC),A0`` at ``0xCD80``, so plain data), and the scene-script
   table's lists (`EXP-0075` ``every_scene``: eight lists, 0-5 the pilots,
   6 the win quotes, 7 the thank-you screen).
2. **Lines.** Every line of ``data/text/special_census.json`` (`SPECIAL-010`):
   story, win quotes and captions in `STG0AS.BIN`'s table, endings in
   `END.BIN`'s. Each is compared with every line of every record of
   `cybotsj`'s Japanese table (``0x0A30F6``, 624 slots), decoded with
   ``data/text/arcade_jp_map.json`` (`REF-006`): exact matches, else the
   best ``difflib`` ratio; at least ``--min-ratio`` is an edited match.
3. **Control.** Jin's story lines (``data/text/jin_boxes.json``), which
   pair with the arcade exactly or with small edits (D-022), go through the
   same comparison; their match rate is reported.
4. **Boxes.** A real counterpart matches a whole box: every line of a
   Saturn box (by its record) matches a line of one and the same arcade
   slot. Boxes of lists 6-8 with more than one line are tested this way.
5. **Posted?** A matched slot counts as official English for the line only
   if an arcade scene opens it (``every_scene``, both sets) or it is a
   caption slot the caption drawer reads (494-549, D-060).

Writes slot numbers, line numbers and ratios only (`AGENTS.md` rule 21).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.text import ending
from tools.text.arcade_pairing import read_jp_record
from tools.text.dialogue import line_table

_spec = importlib.util.spec_from_file_location(
    "thanks", Path("research/experiments/EXP-0075/thanks.py")
)
assert _spec and _spec.loader
thanks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(thanks)

SRC = Path("local/extracted/saturn_jp")
IMAGES = {
    "cybotsu": Path("local/ref003/cybotsu-maincpu.bin"),
    "cybotsj": Path("local/ref003/cybotsj-maincpu.bin"),
}
SCRIPTS = {"cybotsu": 0x12150, "cybotsj": 0x12138}  # EXP-0040
RING = 0xCE00
JP_TABLE = 0x0A30F6
SLOTS = 624
CAPTION_SLOTS = range(494, 550)  # D-060: the caption drawer's slots
MAP = Path("data/text/arcade_jp_map.json")


def chars(raw: bytes) -> tuple[bytes, ...]:
    raw = raw.replace(b"\n", b"")
    return tuple(raw[i : i + 2] for i in range(0, len(raw) - 1, 2))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--min-ratio", type=float, default=0.6)
    p.add_argument("--out", type=Path, default=Path("data/text/special_official.json"))
    a = p.parse_args()
    report: dict[str, Any] = {"task": "SPECIAL-011", "arcade": {}}
    opened: set[int] = set()
    for name, path in IMAGES.items():
        image = path.read_bytes()
        ring = image[RING : RING + 12]
        every = thanks.every_scene(image, SCRIPTS[name])
        lists = sorted({int(k.split("/")[0]) for k in every})
        opened |= {x for v in every.values() for x in v}
        report["arcade"][name] = {
            "image_sha256": hashlib.sha256(image).hexdigest(),
            "select_ring": [[ring[2 * k], ring[2 * k + 1]] for k in range(6)],
            "select_pilots": sorted(set(ring)),
            "scene_lists": lists,
            "scenes_per_list": {
                str(k): sum(1 for x in every if int(x.split("/")[0]) == k)
                for k in lists
            },
        }
    posted = opened | set(CAPTION_SLOTS)

    mapping = {
        int(k, 16): bytes.fromhex(v) for k, v in json.loads(MAP.read_text()).items()
    }
    image = IMAGES["cybotsj"].read_bytes()
    arcade: list[tuple[int, int, tuple[bytes, ...]]] = []
    for slot in range(SLOTS):
        address = int.from_bytes(image[JP_TABLE + 4 * slot : JP_TABLE + 4 * slot + 4])
        for n, codes in enumerate(read_jp_record(image, address)):
            arcade.append((slot, n, tuple(mapping.get(c, b"??") for c in codes)))
    by_text: dict[tuple[bytes, ...], list[tuple[int, int]]] = {}
    for slot, n, t in arcade:
        by_text.setdefault(t, []).append((slot, n))

    stg = (SRC / "STG0AS.BIN").read_bytes()
    end = (SRC / "END.BIN").read_bytes()
    sources = {
        "STG0AS.BIN": [chars(stg[o : o + n]) for o, n in line_table()],
        "END.BIN": [chars(end[o : o + n]) for o, n in ending.end_lines()],
    }
    census = json.loads(Path("data/text/special_census.json").read_text())
    surfaces = {
        "story": "STG0AS.BIN",
        "win_quotes": "STG0AS.BIN",
        "captions": "STG0AS.BIN",
        "ending": "END.BIN",
    }
    results: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for entry in census["lists"]:
        for surface, file in surfaces.items():
            for line in entry[surface]["line_ids"]:
                if (file, line) in seen:
                    continue
                seen.add((file, line))
                text = sources[file][line]
                exact = by_text.get(text, []) if text else []
                best = (0.0, -1, -1)
                if not exact and text:
                    sm = difflib.SequenceMatcher(None, (), text, autojunk=False)
                    for slot, n, t in arcade:
                        sm.set_seq1(t)
                        if (
                            sm.real_quick_ratio() <= best[0]
                            or sm.quick_ratio() <= best[0]
                        ):
                            continue
                        r = sm.ratio()
                        if r > best[0]:
                            best = (r, slot, n)
                match = (
                    "exact" if exact else "edited" if best[0] >= a.min_ratio else "none"
                )
                slots = (
                    sorted({s for s, _ in exact})
                    if exact
                    else ([best[1]] if match == "edited" else [])
                )
                results.append(
                    {
                        "list": entry["list"],
                        "surface": surface,
                        "file": file,
                        "line": line,
                        "chars": len(text),
                        "match": match,
                        "slots": slots,
                        "best_ratio": 1.0 if exact else round(best[0], 3),
                        "best_slot": slots[0] if slots else best[1],
                        "posted_slots": [s for s in slots if s in posted],
                    }
                )

    def best_match(text: tuple[bytes, ...]) -> tuple[float, int]:
        if text in by_text:
            return 1.0, by_text[text][0][0]
        best = (0.0, -1)
        sm = difflib.SequenceMatcher(None, (), text, autojunk=False)
        for slot, _, t in arcade:
            sm.set_seq1(t)
            if sm.real_quick_ratio() <= best[0] or sm.quick_ratio() <= best[0]:
                continue
            r = sm.ratio()
            if r > best[0]:
                best = (r, slot)
        return best

    jin = json.loads(Path("data/text/jin_boxes.json").read_text())
    jin_lines = sorted(
        {n for sc in jin["scenes"] for b in sc["boxes"] for n in b["lines"]}
    )
    ctrl = [best_match(sources["STG0AS.BIN"][n]) for n in jin_lines]
    report["control_jin"] = {
        "lines": len(ctrl),
        "exact": sum(r == 1.0 for r, _ in ctrl),
        "edited": sum(a.min_ratio <= r < 1.0 for r, _ in ctrl),
        "none": sum(r < a.min_ratio for r, _ in ctrl),
        "min_ratio_seen": round(min(r for r, _ in ctrl), 3),
    }
    # Box level: all lines of a multi-line box against one slot.
    import tools.text.dialogue as dl

    def u32(x: int) -> int:
        return int.from_bytes(stg[x - dl.BASE : x - dl.BASE + 4])

    line_at = {dl.BASE + o: i for i, (o, _) in enumerate(line_table())}
    stg_box_lines: dict[int, list[int]] = {}
    for box in range(1074):
        e = u32(dl.RECORDS + 4 * box) + 8
        while True:
            found = line_at.get(u32(e))
            if found is not None:
                stg_box_lines.setdefault(box, []).append(found)
            if stg[e + 4 - dl.BASE : e + 6 - dl.BASE] != b"\xff\xff":
                break
            e += 8
    end_box_lines = ending.record_lines(end, ending.end_lines())
    slot_lines: dict[int, list[tuple[bytes, ...]]] = {}
    for slot, _, t in arcade:
        slot_lines.setdefault(slot, []).append(t)

    def ratio(x: tuple[bytes, ...], y: tuple[bytes, ...]) -> float:
        return difflib.SequenceMatcher(None, x, y, autojunk=False).ratio()

    whole: list[dict[str, Any]] = []
    tested = 0
    for entry in census["lists"]:
        for surface, file in surfaces.items():
            table = end_box_lines if file == "END.BIN" else stg_box_lines
            for box in entry[surface]["box_list"]:
                ls = [sources[file][n] for n in table.get(box, []) if sources[file][n]]
                if len(ls) < 2:
                    continue
                tested += 1
                for slot, tl in slot_lines.items():
                    if len(tl) >= len(ls) and all(
                        max(ratio(x, y) for y in tl) >= a.min_ratio for x in ls
                    ):
                        whole.append(
                            {
                                "list": entry["list"],
                                "surface": surface,
                                "box": box,
                                "slot": slot,
                            }
                        )
    jin_boxes = [
        (
            b["box"],
            [sources["STG0AS.BIN"][n] for n in b["lines"] if sources["STG0AS.BIN"][n]],
        )
        for sc in jin["scenes"]
        for b in sc["boxes"]
    ]
    jin_multi = [(b, ls) for b, ls in jin_boxes if len(ls) >= 2]
    jin_whole = sum(
        any(
            len(tl) >= len(ls)
            and all(max(ratio(x, y) for y in tl) >= a.min_ratio for x in ls)
            for tl in slot_lines.values()
        )
        for _, ls in jin_multi
    )
    report["control_jin_boxes"] = {
        "multi_line": len(jin_multi),
        "whole_box_matched": jin_whole,
    }
    report["boxes_tested"] = tested
    report["whole_box_matches"] = whole
    report["min_ratio"] = a.min_ratio
    report["lines"] = results
    summary: dict[str, dict[str, int]] = {}
    for row in results:
        key = f"{row['list']}/{row['surface']}"
        s = summary.setdefault(
            key, {"lines": 0, "exact": 0, "edited": 0, "none": 0, "posted": 0}
        )
        s["lines"] += 1
        s[row["match"]] += 1
        s["posted"] += bool(row["posted_slots"])
        report["summary"] = summary
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print("control", report["control_jin"])
    print("multi-line boxes tested", tested, "whole-box matches", whole)
    print("control boxes", report["control_jin_boxes"])
    best_none = sorted(x["best_ratio"] for x in results if x["match"] == "none")
    print(
        "best ratio of unmatched lines: max",
        best_none[-1],
        "median",
        best_none[len(best_none) // 2],
    )
    for name, v in report["arcade"].items():
        print(name, v["select_pilots"], v["scene_lists"], v["scenes_per_list"])
    for k, v in summary.items():
        print(k, v)
    for row in results:
        if row["match"] != "none":
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
