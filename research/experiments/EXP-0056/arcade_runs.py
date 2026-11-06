"""EXP-0056: MAME timelines for the arcade's pilot select and VS screens.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0056/arcade_runs.py \\
        [--sets cybotsu,cybotsj] [--out local/loc001/mame]

Headless MAME 0.289 (``tools/reference/mame_timeline.lua``), the route of
``EXP-0009`` run 2 (coin at 600, Start at 720), then:

- ``select``: P1 Right ten times, 60 frames apart from frame 1000, with a
  snapshot 30 frames after each press (and one before the first);
- ``mechK`` (K = 0-3): Button 1 at 1020 (the pilot under the cursor), Down K
  times from 1200, Button 1 at 1320 + 30K; snapshots every 60 frames from
  1500 to 4800 (the VS screen);
- ``mechKbB``: as ``mechK``, confirming the machine with Button B (2-4),
  to see whether a button picks a variant;
- ``pilotP`` (P = 1-9): Right P times from 900, Button 1 at 1020 + 30P,
  Button 1 again 300 frames later; snapshots as ``mechK``.

Snapshots go to ``OUT/<set>/<run>/``; the timelines themselves are written
next to them. Nothing is committed from the output.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LUA = "tools/reference/mame_timeline.lua"


def timelines() -> dict[str, list[str]]:
    base = ["600 press 8 Coin 1", "720 press 8 1 Player Start"]
    vs_snaps = [f"{f} snap" for f in range(1500, 4801, 60)]
    out: dict[str, list[str]] = {}
    sel = [*base, "970 snap"]
    for k in range(10):
        sel += [f"{1000 + 60 * k} press 8 P1 Right", f"{1030 + 60 * k} snap"]
    out["select"] = [*sel, "1700 exit"]
    for k in range(4):
        lines = [*base, "1020 press 8 P1 Button 1"]
        lines += [f"{1200 + 30 * i} press 8 P1 Down" for i in range(k)]
        lines += [f"{1320 + 30 * k} press 8 P1 Button 1", *vs_snaps, "4820 exit"]
        out[f"mech{k}"] = lines
    for k in range(4):
        for button in (2, 3, 4):
            lines = [*base, "1020 press 8 P1 Button 1"]
            lines += [f"{1200 + 30 * i} press 8 P1 Down" for i in range(k)]
            lines += [f"{1320 + 30 * k} press 8 P1 Button {button}", *vs_snaps]
            out[f"mech{k}b{button}"] = [*lines, "4820 exit"]
    for p in range(1, 10):
        lines = base + [f"{900 + 20 * i} press 8 P1 Right" for i in range(p)]
        pick = 1020 + 30 * p
        lines += [f"{pick} press 8 P1 Button 1", f"{pick + 300} press 8 P1 Button 1"]
        lines += [*vs_snaps, "4820 exit"]
        out[f"pilot{p}"] = lines
    return out


def run(game: str, name: str, lines: list[str], out: Path) -> str:
    folder = out / game / name
    (folder / "snap").mkdir(parents=True, exist_ok=True)
    timeline = folder / "timeline.txt"
    timeline.write_text("\n".join(lines) + "\n")
    command = [
        "mame",
        game,
        "-rompath",
        "local/arcade",
        "-autoboot_script",
        LUA,
        "-snapshot_directory",
        str(folder / "snap"),
        "-cfg_directory",
        "local/mame_arcade/cfg",
        "-nvram_directory",
        "local/mame_arcade/nvram",
        "-skip_gameinfo",
        "-nothrottle",
        "-video",
        "none",
        "-sound",
        "none",
        "-seconds_to_run",
        "200",
    ]
    env = {**os.environ, "MAME_TIMELINE": str(timeline)}
    with (folder / "mame.log").open("w") as log:
        code = subprocess.run(
            command, env=env, stdout=log, stderr=subprocess.STDOUT
        ).returncode
    snaps = len(list((folder / "snap").rglob("*.png")))
    return f"{game} {name} exit {code} snaps {snaps}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sets", default="cybotsu,cybotsj")
    parser.add_argument("--out", type=Path, default=Path("local/loc001/mame"))
    parser.add_argument("--only", help="comma-separated run names")
    args = parser.parse_args()
    jobs = [
        (game, name, lines)
        for game in args.sets.split(",")
        for name, lines in timelines().items()
        if not args.only or name in args.only.split(",")
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for line in pool.map(lambda j: run(j[0], j[1], j[2], args.out), jobs):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
