"""EXP-0027: cold-boot an image, pick a pilot, and play into a stage, fights forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0027/play_route.py CUE OUT \\
        [--moves right,right] [--until-stage 2]

A debug harness; it never ships. It generalizes
``research/experiments/EXP-0026/play_two_stages.py``:

- **Pilot:** at pilot select, after a screenshot (``select-0.png``), it
  presses each of ``--moves`` (pad directions), takes a screenshot after each
  one, and confirms with A. Then it presses A twice for the machine.
- **Scene posts:** a PC breakpoint in log mode on the scene-post routines
  (`STG0AS.BIN` ``0x0606DBEA``, `END.BIN` ``0x06066852``; EXP-0022) logs R5,
  the scene, at every post (``events.txt``).
- **Fights:** during a fight (step 14), it holds player 1's vitality pair at
  152 and player 2's at 0, and presses A (D-025).
- **Polling:** every 1.5 s it reads the stage, the step and the pilot byte of
  the scene task (``@0x0600800C`` + ``0x1F``), and saves a screenshot and the
  60 glyph cells.
- **End:** 60 s after the stage byte reaches the pilot's first stage group
  plus ``--until-stage``, or after ``--max-minutes`` (default 20). With
  ``--stop-after-posts N`` (EXP-0033) it ends once N scene
  posts are logged, before any fight, so it presses no keys after the
  machine select. With ``--no-fight-keys`` (RE-008) it presses nothing during
  fights either: each fight ends at time-out with the vitality held (the
  user, 2026-11-03: no repeated key presses). If no scene is posted 45 s
  after the machine select, it presses A again, at most twice (RE-008: a
  press can be lost while a portrait loads).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
from cold_route import features, key, run, shot  # type: ignore[import-not-found]

from tools.mednafen.agent import Agent

STAGE = 0x060CFF88
P1_VITALITY, P2_VITALITY = 0x060D0024, 0x060D0318
POSTS = ["0606DBEA", "06066852"]
FULL = 152


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--moves", default="")
    parser.add_argument("--until-stage", type=int, default=2)
    parser.add_argument("--stop-after-posts", type=int, default=0)
    parser.add_argument("--select-wait", type=float, default=6.0)
    parser.add_argument("--move-wait", type=float, default=1.0)
    parser.add_argument("--no-fight-keys", action="store_true")
    parser.add_argument("--max-minutes", type=float, default=20)
    args = parser.parse_args()
    out: Path = args.out
    if run("launch", str(args.cue), str(out)):
        raise SystemExit("launch failed")
    agent = Agent((out / "agent").resolve())
    while int(agent.status()["frame"]) < 3500:
        time.sleep(1)
    agent.bpmode("log")
    agent.breakpoints("pc", POSTS)
    n = 0
    deadline = time.time() + 480
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
    for attempt in range(
        4
    ):  # ARCADE MODE; a press right after the menu appears can be lost
        key(out, "a")
        time.sleep(3)
        _, logo, menu = features(shot(out, f"menu-after-{attempt}"))
        if not (logo > 200 and menu > 150):
            break
    else:
        raise SystemExit("ARCADE MODE not taken")
    time.sleep(args.select_wait)  # moves before the cursor appears are lost
    shot(out, "select-0")
    for i, move in enumerate(m for m in args.moves.split(",") if m):
        key(out, move, "0.2")
        time.sleep(args.move_wait)  # a portrait loads from CD after each move
        shot(out, f"select-{i + 1}")
    key(out, "a")  # the pilot under the cursor
    time.sleep(6)
    shot(out, "machine")
    key(out, "a")
    time.sleep(2)
    key(out, "a")
    start = time.time()
    reached: float | None = None
    base: int | None = None
    poll = 0
    extra_a = 0
    with (out / "poll.jsonl").open("a") as log:
        while time.time() - start < 60 * args.max_minutes:
            poll += 1
            stage = agent.bus_read(STAGE, 2)
            task = int.from_bytes(agent.bus_read(0x0600800C, 4), "big")
            pilot = (
                agent.bus_read(task + 0x1F, 1)[0]
                if 0x06000000 <= task < 0x06100000
                else None
            )
            record: dict[str, object] = {
                "poll": poll,
                "time": time.strftime("%H:%M:%S"),
                "frame": int(agent.status()["frame"]),
                "stage": stage[0],
                "step": stage[1],
                "task_pilot": pilot,
            }
            if (
                extra_a < 2
                and time.time() - start > 45 * (extra_a + 1)
                and not any("PC=0606DBEA" in e.upper() for e in agent.events())
            ):  # a machine-select press lost while a portrait loads (RE-008)
                extra_a += 1
                key(out, "a")
            if stage[1] == 14:
                foe = agent.bus_read(P2_VITALITY, 4)
                if foe[0:2] == foe[2:4]:
                    agent.bus_write(P2_VITALITY, bytes(4))
                agent.bus_write(P1_VITALITY, FULL.to_bytes(2, "big") * 2)
                if not args.no_fight_keys:
                    key(out, "a", "0.15")
            run("shot", str(out), f"p{poll:04d}")
            (out / f"cells-{poll:04d}.bin").write_bytes(
                agent.bus_read(0x060FE200, 60 * 0x80)
            )
            log.write(json.dumps(record) + "\n")
            log.flush()
            if base is None and stage[1] in (1, 4, 8):
                base = stage[0]  # the pilot's first stage group (Jin 0, Mary 18)
            if (
                base is not None
                and stage[0] >= base + args.until_stage
                and reached is None
            ):
                reached = time.time()
            if reached is not None and time.time() - reached > 60:
                break
            if args.stop_after_posts and (
                sum("PC=0606DBEA" in e.upper() for e in agent.events())
                >= args.stop_after_posts
            ):
                break
            time.sleep(1.5)
    (out / "events.txt").write_text("\n".join(agent.events()) + "\n")
    run("stop", str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
