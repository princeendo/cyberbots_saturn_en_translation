"""EXP-0074: how the game reaches every box (TXT-010).

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0074/census.py \\
        [--out data/text/reachability.json]

From the untouched `STG0AS.BIN` and `VICTORY.BIN` (D-021, D-030) and
``data/text/pilot_census.json`` (the posted scenes, `RE-005`):

- the scene table ``0x060AA840``: entries up to the pilot-list table
  ``0x060AAD24`` (313; the constant 335 used elsewhere runs 22 words into
  the list table and past it);
- each list's scripts, parsed to their ``0xE000`` end word (a word below
  ``0x8000`` shows that box, ``| 0x8000`` closes it; commands ``0xC000``+
  and ``0xFFFF`` are skipped: the interpreter ``0x0606E230`` has no command
  that jumps, so a posted script shows every box in it);
- every box classified: ``posted`` (a scene some known path posts),
  ``caption`` (the caption table ``0x0609CC22``), ``win-quote`` (list 9,
  picked by `VICTORY.BIN`'s table ``0x0606FAA0``), ``unselected-quote``
  (a list-9 scene that table never picks), ``list-10`` (no Saturn post
  found), ``no-reference``.

Writes numbers only (no text). With ``--arcade DIR`` it adds the arcade
read-tap summary (``DIR/<set>/reads-*.txt``: reader PCs per table).
"""

from __future__ import annotations

import argparse
import collections
import json
import struct
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
import tools.text.dialogue as dl

SRC = Path("local/extracted/saturn_jp")
BASE = 0x06060000
QUOTE_TABLE = 0x0606FAA0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path("data/text/reachability.json"))
    p.add_argument("--arcade", type=Path)
    a = p.parse_args()
    stg = (SRC / "STG0AS.BIN").read_bytes()
    vic = (SRC / "VICTORY.BIN").read_bytes()

    def u32(x: int) -> int:
        return int(struct.unpack_from(">I", stg, x - BASE)[0])

    def u16(x: int) -> int:
        return int(struct.unpack_from(">H", stg, x - BASE)[0])

    entries = (dl.PILOT_LISTS - dl.SCENE_SCRIPTS) // 4
    heads = [u32(dl.PILOT_LISTS + 4 * k) for k in range(dl.PILOTS)]
    commands: collections.Counter[int] = collections.Counter()

    def boxes(script: int) -> list[int]:
        out: list[int] = []
        x = script
        while True:
            w = u16(x)
            x += 2
            if w == 0xE000:
                return out
            if w == 0xFFFF or w >= 0xC000:
                commands[w >> 8] += 1
                continue
            if w & 0x7FFF not in out:
                out.append(w & 0x7FFF)

    census = json.loads(Path("data/text/pilot_census.json").read_text())
    posted = {
        int(e["list"]): set(e.get("story_scenes", []))
        | set(e.get("ending_scenes_by_number", []))
        for e in census["lists"]
    }
    picked = {
        struct.unpack_from(">H", vic, QUOTE_TABLE - BASE + 2 * k)[0] >> 8
        for k in range(9 * 8)
    }
    where: dict[int, list[list[int]]] = {}
    lists = []
    for n, head in enumerate(heads):
        i0 = (head - dl.SCENE_SCRIPTS) // 4
        i1 = (heads[n + 1] - dl.SCENE_SCRIPTS) // 4 if n + 1 < len(heads) else entries
        scenes = []
        for k, i in enumerate(range(i0, i1)):
            found = boxes(u32(dl.SCENE_SCRIPTS + 4 * i))
            scenes.append({"scene": k, "boxes": found})
            for b in found:
                where.setdefault(b, []).append([n, k])
        lists.append({"list": n, "scenes": len(scenes), "scene_boxes": scenes})
    captions = {u16(dl.CAPTIONS + 2 * k) for k in range(90)} - {0}
    classes: dict[str, list[int]] = collections.defaultdict(list)
    for b in range(1074):
        hits = where.get(b, [])
        if any(n < 9 and k in posted.get(n, set()) for n, k in hits):
            c = "posted"
        elif any(n == 9 and k in picked for n, k in hits):
            c = "win-quote"
        elif any(n == 9 for n, k in hits):
            c = "unselected-quote"
        elif any(n == 10 for n, k in hits):
            c = "list-10"
        elif b in captions:
            c = "caption"
        else:
            c = "no-reference"
        classes[c].append(b)
    report: dict[str, Any] = {
        "task": "TXT-010",
        "sources": {
            "STG0AS.BIN": "local/extracted/saturn_jp",
            "posted_scenes": "data/text/pilot_census.json",
        },
        "scene_table_entries": entries,
        "distinct_scripts": len(
            {u32(dl.SCENE_SCRIPTS + 4 * i) for i in range(entries)}
        ),
        "script_commands_by_high_byte": {
            f"0x{k:02X}": v for k, v in sorted(commands.items())
        },
        "interpreter_jumps": (
            "none (0x0606E230: commands E2-EA, C0xx-DFxx set state only)"
        ),
        "quote_scenes_picked": sorted(picked),
        "box_classes": {k: sorted(v) for k, v in sorted(classes.items())},
        "box_class_counts": {k: len(v) for k, v in sorted(classes.items())},
        "unposted_scenes": {
            str(e["list"]): e.get("unposted_scenes", [])
            for e in census["lists"]
            if e.get("unposted_scenes")
        },
        "lists": lists,
    }
    if a.arcade:
        arcade: dict[str, Any] = {}
        for s in sorted(p.name for p in a.arcade.iterdir() if p.is_dir()):
            arcade[s] = {}
            for f in sorted((a.arcade / s).glob("reads-*.txt")):
                pcs = collections.Counter(
                    line.split()[1]
                    for line in f.read_text().splitlines()
                    if line.strip()
                )
                arcade[s][f.stem[6:]] = {
                    f"0x{k.upper()}": v for k, v in sorted(pcs.items())
                }
        report["arcade_reader_pcs"] = arcade
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(report["box_class_counts"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
