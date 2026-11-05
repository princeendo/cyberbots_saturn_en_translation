"""EXP-0036: summarize a play run: the scenes posted and their boxes' cells.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/play_summary.py \\
        PREDICTION RUN BOXES

Runs ``EXP-0030/check_play.py`` for the scenes the run posted (R5 at the
`STG0AS.BIN` post routine, ``RUN/events.txt``), and reports, per scene,
the boxes whose cells all appeared, the stage bytes reached and the keys
sent. Prints JSON.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main(prediction: Path, run: Path, boxes: Path) -> int:
    posted = [
        int(m, 16)
        for line in (run / "events.txt").read_text().splitlines()
        if "PC=0606DBEA" in line
        for m in re.findall(r" R5=([0-9A-F]+)", line)
    ]
    scenes = list(dict.fromkeys(posted))
    result = subprocess.run(
        [
            "./invenv.sh",
            "python",
            "research/experiments/EXP-0030/check_play.py",
            str(prediction),
            str(run),
            "--boxes",
            str(boxes),
            "--scenes",
            *map(str, scenes),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    per_scene = {}
    for line in result.stdout.splitlines():
        r = json.loads(line)
        b = r["boxes"]
        per_scene[r["scene"]] = {
            "boxes": len(b),
            "complete": sum(v["matched"] == v["predicted"] for v in b.values()),
            "incomplete": {
                k: [v["matched"], v["predicted"]]
                for k, v in b.items()
                if v["matched"] < v["predicted"]
            },
        }
    stages = sorted(
        {json.loads(x)["stage"] for x in (run / "poll.jsonl").read_text().splitlines()}
    )
    keys = sum(
        '"action": "key"' in x for x in (run / "log.jsonl").read_text().splitlines()
    )
    print(
        json.dumps(
            {"posted": posted, "scenes": per_scene, "stages": stages, "keys": keys}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])))
