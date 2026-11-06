"""EXP-0050: check every ending forced on the M8 image against its control.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/check_m8.py BUILD \\
        [--out research/experiments/EXP-0050/live.json]

For each list 0-8, run ``local/end023/listN`` (``EXP-0042/probe.py`` on the
built image, cells every 5 frames) against its control on the untouched
image (list 0: ``local/end002/control``; lists 1-8: ``local/end020/listN``).
Numbers only:

- **Cells** (``EXP-0045/check_live.py``): every box opened draws the build's
  predicted cells if the build translated it, else its original cells.
- **Timing:** the posts, the CD audio starts and the loads of `FIX.BIN`,
  `KEND.BIN`, `KEND_0.BIN`, `KEND_1.BIN` and `QSD.PIX`, frame for frame,
  over the frames both runs cover.
- **Holds:** for every translated non-name box opening, the first 5-frame
  dump with all its predicted cells, and the frames until it closes (or
  until the next post or `KEND.BIN`'s load if it logs no close).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

TABLE = "0x060817B4"
NAMES = range(601, 615)
FILES = ("FIX.BIN", "KEND.BIN", "KEND_0.BIN", "KEND_1.BIN", "QSD.PIX")


def controls(n: int) -> Path:
    return Path("local/end002/control") if n == 0 else Path(f"local/end020/list{n}")


def timing(route: dict[str, Any]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {
        "posts": [p["frame"] for p in route["posts"] if p["routine"] == "0x06066852"],
        "audio": [x["frame"] for x in route["loads"] if not x.get("file")],
    }
    for name in FILES:
        out[name] = [
            x["frame"]
            for x in route["loads"]
            if str(x.get("file", "")).startswith(name + ";1+0")
        ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("build", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    pred = {
        p["box"]: p["cells"]
        for p in json.loads((args.build / "ending_prediction.json").read_text())
    }
    report: list[dict[str, Any]] = []
    for n in range(9):
        run = Path(f"local/end023/list{n}")
        cells = json.loads(
            subprocess.run(
                [
                    sys.executable,
                    "research/experiments/EXP-0045/check_live.py",
                    str(run),
                    str(args.build),
                ],
                capture_output=True,
                text=True,
                check=True,
            ).stdout
        )["summary"]
        route = json.loads((run / "route.json").read_text())
        control = json.loads((controls(n) / "route.json").read_text())
        last = min(route["frames"], control["frames"]) + 150
        mine, theirs = timing(route), timing(control)
        compared = {
            k: (
                [f for f in mine[k] if f < last],
                [f for f in theirs[k] if f < last],
            )
            for k in mine
        }
        same = {k: a == b for k, (a, b) in compared.items()}
        events = [
            (b["frame"], int(b["word"], 16))
            for b in route["boxes"]
            if b["table"] == TABLE
        ]
        stops = sorted(mine["posts"] + mine["KEND.BIN"])
        dumps = sorted((int(p.stem[1:]), p) for p in run.glob("c*.bin"))
        holds = []
        for i, (frame, word) in enumerate(events):
            if word & 0x8000 or word not in pred or word in NAMES:
                continue
            want = pred[word]
            close = next((f for f, w in events[i + 1 :] if w == (word | 0x8000)), None)
            nxt = next((s for s in stops if s > frame), None)
            stop = close if close is not None else nxt
            if stop is None or stop > 7500:
                continue
            full = None
            for f, path in dumps:
                if not frame < f < stop:
                    continue
                data = path.read_bytes()
                have = [
                    hashlib.sha256(data[k * 128 : (k + 1) * 128]).hexdigest()
                    for k in range(60)
                ]
                best = 0
                for s in range(60):
                    m = 0
                    while m < len(want) and s + m < 60 and have[s + m] == want[m]:
                        m += 1
                    best = max(best, m)
                if best == len(want):
                    full = f
                    break
            holds.append(
                {
                    "box": word,
                    "open": frame,
                    "full": full,
                    "until": stop,
                    "closes_on": "close" if close is not None else "next scene",
                    "held": None if full is None else stop - full,
                }
            )
        entry = {
            "list": n,
            "cells": cells,
            "timing_equal": same,
            "timing": {k: v[0] for k, v in compared.items()},
            "timing_differences": {
                k: {"built": a, "control": b}
                for k, (a, b) in compared.items()
                if a != b
            },
            "holds": holds,
            "smallest_hold_closing_on_a_close": min(
                (
                    h["held"]
                    for h in holds
                    if h["held"] is not None and h["closes_on"] == "close"
                ),
                default=None,
            ),
        }
        report.append(entry)
        print(
            n,
            "cells",
            cells,
            "timing equal",
            all(same.values()),
            entry["timing_differences"] or "",
            "smallest hold",
            entry["smallest_hold_closing_on_a_close"],
        )
    if args.out:
        args.out.write_text(json.dumps({"lists": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
