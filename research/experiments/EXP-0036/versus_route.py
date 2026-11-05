"""EXP-0036: one versus cold boot of an image, then every win quote forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0036/versus_route.py CUE OUT BOX...

A debug harness; it never ships. It cold-boots CUE with
``EXP-0019/drive.py`` and, like ``EXP-0027/play_route.py``, finds the
title by pixel counts (``EXP-0025/cold_route.py``). Menu keys only (about
ten, the user, 2026-11-03): Start on the title, Down and A for VERSUS MODE,
then A and pad 2's A for the pilots, body types and machines (Jin against
Arieta, Blodia against Blodia, as ``EXP-0031``), 3 s apart, and Start at
SET UP. Then ``EXP-0032/saturn_quote.py``: ``catch`` (the win held in RAM,
a halt at the selector, ``OUT/post.mcs``), ``replay`` (the natural pick)
and ``force`` for each BOX. Stops Mednafen at the end.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
from cold_route import features, key, run, shot  # type: ignore[import-not-found]

from tools.mednafen.agent import Agent

QUOTE = "research/experiments/EXP-0032/saturn_quote.py"


def main(cue: Path, out: Path, boxes: list[str]) -> int:
    if run("launch", str(cue), str(out)):
        raise SystemExit("launch failed")
    agent = Agent((out / "agent").resolve())
    while int(agent.status()["frame"]) < 3500:
        time.sleep(1)
    deadline = time.time() + 480
    n = 0
    while True:
        if time.time() > deadline:
            raise SystemExit("no menu")
        n += 1
        prompt, logo, menu = features(shot(out, f"title{n:03d}"))
        if logo > 200 and menu > 150:
            break
        if prompt > 30 and logo > 200:
            key(out, "start", "0.5")
            time.sleep(1.0)
        time.sleep(0.3)
    time.sleep(1.0)
    key(out, "down", "0.2")
    time.sleep(1.0)
    shot(out, "menu-versus")
    key(out, "a")
    time.sleep(10)
    shot(out, "select-0")
    for step in ("pilot", "body", "machine"):
        key(out, "a", "0.2")
        time.sleep(3)
        key(out, "p2a", "0.2")
        time.sleep(4)
        shot(out, f"after-{step}")
    time.sleep(2)
    shot(out, "setup")
    key(out, "start", "0.3")
    python = ["./invenv.sh", "python", QUOTE]
    subprocess.run([*python, "catch", str(out), "900"], check=True)
    subprocess.run([*python, "replay", str(out)], check=True)
    subprocess.run([*python, "force", str(out), *boxes], check=True)
    run("stop", str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]))
