"""EXP-0026: force each of Jin's story scenes on an image and check every box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0026/force_check.py \\
        CUE PREDICTION OUT [--scenes 21 0 1 ...] [--steps 120] [--control]

A debug harness; it never ships. For each scene, it loads REF-005 state 4138
(machine select, before `STG0AS.BIN` loads; a later state keeps the old
script in RAM) with ``CUE`` mounted. The first scene the stage posts is
replaced. It forces the scene as in
``research/experiments/EXP-0022/force_scene.py`` (a one-shot write of the scene
byte ``0x0600828B`` after the game writes it), runs STEPS x 25 frames, and
saves a screenshot and the 60 glyph cells (WRAM-H ``0x060FE200``) after each
step to ``OUT/scene-NN/``.

It then checks every box of the scene (``data/text/jin_boxes.json``): the
box's predicted cells (``PREDICTION``, from ``tools.text.dialogue``) must
appear as the leading cells of some step. With ``--control`` the prediction
is ignored and only the cells are saved. Prints one JSON line per scene.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
# Before STG0AS.BIN loads: a state saved later keeps the old script in RAM.
STATE = Path("local/ref005/session/states/f00004138.mcs")
SCENE_BYTE = 0x0600828B
CELLS = 0x060FE200
SCENES = [21, *range(16)]


def run_scene(cue: Path, scene: int, out: Path, steps: int) -> None:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(cue)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.status()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.5)
            time.sleep(3)
            if agent.halted():
                agent.run()
            agent.loadstate(STATE.resolve())
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", ["0600828B-0600828B", "2600828B-2600828B"])
            agent.onhit_write(None, SCENE_BYTE, bytes([scene]))
            for step in range(1, steps + 1):
                agent.frames(25)
                agent.wait_halted(30.0)
                agent.screenshot(out / f"step{step:03d}.png")
                (out / f"cells-{step:03d}.bin").write_bytes(
                    agent.bus_read(CELLS, 60 * 0x80)
                )
                agent.run()
            (out / "events.txt").write_text("\n".join(agent.events()) + "\n")
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()


def check(
    out: Path, boxes: list[int], prediction: dict[int, list[str]]
) -> dict[str, dict[str, object]]:
    shots = sorted(out.glob("cells-*.bin"))
    results: dict[str, dict[str, object]] = {}
    for box in boxes:
        want = prediction[box]
        best = (0, "")
        for path in shots:
            data = path.read_bytes()
            n = 0
            while (
                n < len(want)
                and hashlib.sha256(data[n * 128 : n * 128 + 128]).hexdigest() == want[n]
            ):
                n += 1
            best = max(best, (n, path.name))
        results[str(box)] = {"predicted": len(want), "matched": best[0], "at": best[1]}
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("prediction", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--scenes", type=int, nargs="*", default=SCENES)
    parser.add_argument("--steps", type=int, default=150)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    jin = json.loads(Path("data/text/jin_boxes.json").read_text())
    prediction = {p["box"]: p["cells"] for p in json.loads(args.prediction.read_text())}
    for scene in args.scenes:
        out = args.out / f"scene-{scene:02d}"
        run_scene(args.cue, scene, out, args.steps)
        boxes = [b["box"] for b in jin["scenes"][scene]["boxes"]]
        result = {} if args.control else check(out, boxes, prediction)
        ok = (
            all(r["matched"] == r["predicted"] for r in result.values())
            if result
            else None
        )
        print(
            json.dumps(
                {
                    "scene": scene,
                    "time": time.strftime("%H:%M:%S"),
                    "all_boxes": ok,
                    "boxes": result,
                }
            ),
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
