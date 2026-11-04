"""EXP-0035: label each paired line against its own slot's Japanese record.

Run from the repository root, after ``EXP-0028/pair_pilot.py`` has written
the pairing files:

    ./invenv.sh python research/experiments/EXP-0035/check_lines.py \\
        local/ref003/cybotsj-maincpu.bin data/translations/mary_pairing.json ...

``pair_pilot.py``'s ``labels`` come from REF-006's alignment of the whole
script, which pairs a Saturn line once: a line that several boxes use is
labelled ``aligned-to-slot-N`` (N its first box), and a short line it could
not align is ``unaligned``. This compares each box's Saturn lines, in order,
with the lines of the box's own arcade slot (`cybotsj` table ``0x0A30F6``,
decoded through ``data/text/arcade_jp_map.json``):

- ``exact``: the same bytes;
- ``edited``: different bytes, with ``difflib`` similarity (codes the map
  does not know decode as ``??``);
- ``no-counterpart``: the Saturn box has more lines than the slot.

It adds ``slot_labels`` and ``slot_similarity`` to each pair,
``slot_label_counts`` to the file, and for each slot that shares a record
with a paired box, the box that uses it. The pairing files are updated in
place; they hold no text.
"""

from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.reference.cybots_text import long
from tools.text.arcade_pairing import read_jp_record

JP_TABLE = 0x0A30F6
STG0AS = Path("local/extracted/saturn_jp/STG0AS.BIN")


def main(jp_path: Path, files: list[Path]) -> int:
    jp = jp_path.read_bytes()
    code_map = {
        int(k, 16): bytes.fromhex(v)
        for k, v in json.loads(Path("data/text/arcade_jp_map.json").read_text()).items()
    }
    census = json.loads(Path("data/text/script_census.json").read_text())
    table = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")["blocks"][0][
        "table"
    ]
    stg = STG0AS.read_bytes()
    lines = [stg[off : off + n] for off, n, *_ in table]
    for path in files:
        pairing = json.loads(path.read_text())
        counts: dict[str, int] = {}
        for p in pairing["pairs"]:
            slot = p["arcade_slot"]
            arcade = [
                b"".join(code_map.get(c, b"??") for c in codes)
                for codes in read_jp_record(jp, long(jp, JP_TABLE + 4 * slot))
            ]
            labels, ratios = [], []
            for i, n in enumerate(p["saturn_lines"]):
                if i >= len(arcade):
                    label, ratio = "no-counterpart", 0.0
                elif arcade[i] == lines[n]:
                    label, ratio = "exact", 1.0
                else:
                    label = "edited"
                    ratio = difflib.SequenceMatcher(None, arcade[i], lines[n]).ratio()
                labels.append(label)
                ratios.append(round(ratio, 3))
                counts[label] = counts.get(label, 0) + 1
            p["slot_labels"] = labels
            p["slot_similarity"] = ratios
        pairing["slot_label_counts"] = counts
        boxes = {p["box"]: p["arcade_slot"] for p in pairing["pairs"]}
        shared = pairing.get("slots_sharing_a_record_with_a_paired_box", [])
        pairing["shared_record_slots_explained"] = [
            {
                "slot": s,
                "same_record_as_paired_box": [
                    b
                    for b, slot in boxes.items()
                    if long(jp, JP_TABLE + 4 * slot) == long(jp, JP_TABLE + 4 * s)
                ],
                "slot_in_a_scene": s in boxes,
            }
            for s in shared
        ]
        path.write_text(json.dumps(pairing, indent=1) + "\n")
        print(
            path.name,
            json.dumps(counts),
            json.dumps(pairing["shared_record_slots_explained"]),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), [Path(a) for a in sys.argv[2:]]))
