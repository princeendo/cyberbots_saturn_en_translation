"""EXP-0055: summarize the play-check boots (numbers only).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0055/summarize.py \\
        [--out research/experiments/EXP-0055/play.json]

Per case in ``local/boot005``: the warning shown (R4), the press and its
frame, the routines hit after the press (from 60 frames after the warning; the
press comes at 120): the BIOS routine at the ``0x0600026C`` vector, the
continue paths, a save written (stopping at the BIOS hit, after which the
BIOS's own code runs at those addresses), the screenshot
hashes, and the size of each backup file after the run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RUNS = Path("local/boot005")
CASES = ("damaged", "zero", "cart-zero", "both-zero", "free4", "normal")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report: list[dict[str, Any]] = []
    for case in CASES:
        run = RUNS / case
        route = json.loads((run / "route.json").read_text())
        pressed = route["presses"][0]["frame"] if route["presses"] else None
        hits = []
        for h in route["hits"]:
            hits.append(h)
            if h["PC"] == "0x0000186C":
                break  # the BIOS's own code follows at the same addresses
        warned = [h for h in hits if h["PC"] == "0x06036DA8"]
        warnings = [int(h["R4"], 16) for h in warned]
        # The press comes 120 frames after the warning; take what follows it,
        # up to the first BIOS hit (after it the BIOS's own code runs at the
        # same work-RAM addresses, so later hits are not the game's).
        after: list[str] = []
        for h in hits:
            if not warned or h["frame"] <= warned[0]["frame"] + 60:
                continue
            if h["what"] not in after:
                after.append(h["what"])
            if h["PC"] == "0x0000186C":
                break
        entry = {
            "case": case,
            "warnings": warnings,
            "press_logged_at_frame": pressed,
            "routines_after_press": after,
            "shots": {
                s["png"]: hashlib.sha256((run / s["png"]).read_bytes()).hexdigest()
                for s in route["shots"]
                if s["why"] != "periodic" or s is route["shots"][-1]
            },
            "sav_after_bytes": route["sav_after"],
        }
        report.append(entry)
        print(case, warnings, pressed, after)
    if args.out:
        args.out.write_text(json.dumps({"cases": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
