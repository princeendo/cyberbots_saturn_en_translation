"""EXP-0033: write the M5 roster and the roster pilots' box lists (no text).

Run from the repository root, after ``census.py`` has written
``data/text/pilot_census.json``:

    ./invenv.sh python research/experiments/EXP-0033/roster.py

The roster is lists 0-5, the user's choice (2026-11-04, "Six arcade pilots
(Recommended)"). For lists 2-5 it writes ``data/text/<pilot>_boxes.json``
with ``EXP-0022/box_list.py`` and adds ``story_scenes`` (sorted) and
``story_scenes_posted`` (post order) from the census, as
``santana_boxes.json`` has them (EXP-0027). ``jin_boxes.json`` and
``santana_boxes.json`` are left as they are: they are inputs to the
regression references, and the compiler takes Jin's story scenes from
D-021 (``tools/text/dialogue.py`` ``JIN_STORY``), the same scenes the census
finds. Writes ``data/text/m5_roster.json``.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0022"))
import box_list  # type: ignore[import-not-found]

STG0AS = Path("local/extracted/saturn_jp/STG0AS.BIN")
CENSUS = Path("data/text/pilot_census.json")
FILES = ["jin", "santana", "mary", "arieta", "gawaine", "baomao"]
NOTE = (
    "story_scenes: the scene numbers in pilot {p}'s block of STG0AS.BIN's scene "
    "posts (EXP-0027 scene_posts.py), in post order in story_scenes_posted "
    "(EXP-0033 census.py)."
)
DECISION = "Six arcade pilots (Recommended)"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    census = {c["list"]: c for c in json.loads(CENSUS.read_text())["lists"]}
    roster = []
    for p, name in enumerate(FILES):
        path = Path(f"data/text/{name}_boxes.json")
        c = census[p]
        if p >= 2:
            with contextlib.redirect_stdout(io.StringIO()):
                box_list.main(STG0AS, p, path)
            listing = json.loads(path.read_text())
            listing["story_scenes_posted"] = c["story_scenes_posted"]
            listing["story_scenes"] = c["story_scenes"]
            listing["note"] = NOTE.format(p=p)
            path.write_text(json.dumps(listing, indent=1) + "\n")
        roster.append(
            {
                "list": p,
                "pilot": c["name"],
                "boxes_file": str(path),
                "boxes_file_sha256": sha(path),
                "story_scenes": c["story_scenes"],
                "story_scenes_posted": c["story_scenes_posted"],
                "story_boxes": c["story_boxes"],
                "story_lines": c["story_lines"],
                "select_moves": c["select_moves"],
                "first_stage_group": c["first_stage_group"],
                "route_evidence": c["route_evidence"],
            }
        )
    result = {
        "decision": {
            "date": "2026-11-04",
            "task": "RE-005",
            "answer": DECISION,
            "roster": "lists 0-5: story scenes and versus win quotes",
            "exceptions": "docs/coverage_exceptions.md",
        },
        "census": {"file": str(CENSUS), "sha256": sha(CENSUS)},
        "win_quotes": "data/translations/win_quotes_pairing.json (roster_quote_boxes)",
        "pilots": roster,
        "totals": {
            "story_boxes": sum(r["story_boxes"] for r in roster),
            "story_lines": sum(r["story_lines"] for r in roster),
        },
    }
    Path("data/text/m5_roster.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result["totals"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
