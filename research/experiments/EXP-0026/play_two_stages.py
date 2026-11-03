"""EXP-0026: cold-boot an image and play Jin's story into stage 2, fights forced.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/play_two_stages.py CUE OUT

A debug harness; it never ships.

- **Route:** as ``research/experiments/EXP-0025/cold_route.py`` (pad keys
  through ``research/experiments/EXP-0019/drive.py``; Start only on the title
  prompt), up to the machine select.
- **Fights:** every 1.5 s the stage bytes are read: stage ``0x060CFF88``, step
  ``0x060CFF89`` (D-021). During a fight (step 14), Jin's vitality pair
  ``0x060D0024``/``0x060D0026`` is set to 152 (full). The opponent's pair
  ``0x060D0318``/``0x060D031A`` (EXP-0026: zeroing it empties the opponent's
  bar) is set to 0, but only while it reads as a pair of equal values. Then
  A is pressed, so the next hit ends the fight.
- **End:** 60 s after the stage byte reaches 2, or after 15 minutes.

Each poll saves a screenshot, the 60 glyph cells (WRAM-H ``0x060FE200``) as
``OUT/cells-NNNN.bin``, and a line of ``OUT/poll.jsonl``.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0025"))
from cold_route import features, key, run, shot  # type: ignore[import-not-found]

from tools.mednafen.agent import Agent

STAGE, STEP = 0x060CFF88, 0x060CFF89
JIN_VITALITY, FOE_VITALITY = 0x060D0024, 0x060D0318
FULL = 152


def main(cue: Path, out: Path) -> int:
    if run("launch", str(cue), str(out)):
        raise SystemExit("launch failed")
    agent = Agent((out / "agent").resolve())
    while int(agent.status()["frame"]) < 3500:
        time.sleep(1)
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
    key(out, "a")  # ARCADE MODE
    time.sleep(9)
    key(out, "a")  # Jin
    time.sleep(6)
    key(out, "a")  # Blodia
    time.sleep(2)
    key(out, "a")
    start = time.time()
    reached: float | None = None
    poll = 0
    with (out / "poll.jsonl").open("a") as log:
        while time.time() - start < 900:
            poll += 1
            stage = agent.bus_read(STAGE, 2)
            record: dict[str, object] = {
                "poll": poll,
                "time": time.strftime("%H:%M:%S"),
                "frame": int(agent.status()["frame"]),
                "stage": stage[0],
                "step": stage[1],
            }
            if stage[1] == 14:
                foe = agent.bus_read(FOE_VITALITY, 4)
                if foe[0:2] == foe[2:4]:
                    agent.bus_write(FOE_VITALITY, bytes(4))
                    record["foe_was"] = int.from_bytes(foe[0:2], "big")
                agent.bus_write(JIN_VITALITY, FULL.to_bytes(2, "big") * 2)
                key(out, "a", "0.15")
            run("shot", str(out), f"p{poll:04d}")
            (out / f"cells-{poll:04d}.bin").write_bytes(
                agent.bus_read(0x060FE200, 60 * 0x80)
            )
            log.write(json.dumps(record) + "\n")
            log.flush()
            if stage[0] >= 2 and reached is None:
                reached = time.time()
            if reached is not None and time.time() - reached > 60:
                break
            time.sleep(1.5)
    run("stop", str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
