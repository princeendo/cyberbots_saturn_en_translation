"""EXP-0031: watch a running cold boot: log loads and posts, force player 1's win.

Run from the repository root, while ``EXP-0019/drive.py launch`` runs in OUT:

    ./invenv.sh python research/experiments/EXP-0031/watch.py OUT SECONDS [--force]

A debug harness; it never ships. It attaches to the agent in ``OUT/agent``,
sets ``loads.py``'s log-mode PC breakpoints (CD Play Disc and scene posts),
and every 1.5 s decodes and clears the events and saves a screenshot
``OUT/wTIME-NNNN.png``. With ``--force`` it holds player 1's vitality pair at
152 and player 2's at 0 (D-025: ``0x060D0024``, ``0x060D0318``), so the fight
ends at time-out in player 1's favour. It sends no key presses: each press
brings Mednafen to the front (the user, 2026-11-03). Writes
``OUT/watch-TIME.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0019"))
from drive import agent_for  # type: ignore[import-not-found]
from loads import CR1, CR2, LISTING, POSTS, decode

P1_VITALITY, P2_VITALITY = 0x060D0024, 0x060D0318
FULL = 152


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("seconds", type=float)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    files = json.loads(LISTING.read_text())["files"]
    agent = agent_for(args.out)
    agent.clear_events()
    agent.bpmode("log")
    agent.breakpoints("pc", [f"{a:08X}" for a in (CR1, CR2, *POSTS)])
    loads: list[dict[str, object]] = []
    posts: list[dict[str, object]] = []
    polls: list[dict[str, object]] = []
    start = time.time()
    n = 0
    while time.time() - start < args.seconds:
        n += 1
        found_loads, found_posts = decode(agent.events(), files)
        agent.clear_events()
        loads += found_loads
        posts += found_posts
        for item in found_loads + found_posts:
            print(json.dumps(item), flush=True)
        vit = agent.bus_read(P1_VITALITY, 4), agent.bus_read(P2_VITALITY, 4)
        polls.append(
            {
                "poll": n,
                "frame": int(agent.status()["frame"]),
                "p1": vit[0].hex(),
                "p2": vit[1].hex(),
            }
        )
        if args.force:
            agent.bus_write(P1_VITALITY, FULL.to_bytes(2, "big") * 2)
            if vit[1][0:2] == vit[1][2:4]:
                agent.bus_write(P2_VITALITY, bytes(4))
        agent.screenshot(args.out / f"w{int(start)}-{n:04d}.png")
        time.sleep(1.5)
    agent.breakpoints("pc")
    agent.clear_events()
    (args.out / f"watch-{int(start)}.json").write_text(
        json.dumps({"loads": loads, "posts": posts, "polls": polls}, indent=1) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
