"""EXP-0030: check a cold-boot play run's glyph cells against the prediction.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0030/check_play.py \\
        PREDICTION RUN --boxes data/text/santana_boxes.json [--scenes 23 0 1]

A debug harness; it never ships. ``RUN`` is an
``research/experiments/EXP-0027/play_route.py`` output: its
``cells-NNNN.bin`` are the 60 glyph cells saved at each poll. For each scene
(default: the box list's ``story_scenes`` in the order posted, or Jin's 21,
0-15), it reports each box's best leading match against ``PREDICTION`` (from
``tools.text.dialogue``), with EXP-0026's matching. Prints one JSON line per
scene with any cell matched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.text.dialogue import JIN_STORY


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("prediction", type=Path)
    parser.add_argument("run", type=Path)
    parser.add_argument("--boxes", type=Path, required=True)
    parser.add_argument("--scenes", type=int, nargs="*")
    args = parser.parse_args()
    box_list = json.loads(args.boxes.read_text())
    scenes = args.scenes or box_list.get(
        "story_scenes_posted", box_list.get("story_scenes", JIN_STORY)
    )
    prediction = {p["box"]: p["cells"] for p in json.loads(args.prediction.read_text())}
    shots = [(p.name, p.read_bytes()) for p in sorted(args.run.glob("cells-*.bin"))]
    for scene in scenes:
        results = {}
        for box in (b["box"] for b in box_list["scenes"][scene]["boxes"]):
            want = prediction[box]
            best = (0, "")
            for name, data in shots:
                n = 0
                while (
                    n < len(want)
                    and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest()
                    == want[n]
                ):
                    n += 1
                best = max(best, (n, name))
            results[str(box)] = {
                "predicted": len(want),
                "matched": best[0],
                "at": best[1],
            }
        if any(r["matched"] for r in results.values()):
            print(json.dumps({"scene": scene, "boxes": results}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
