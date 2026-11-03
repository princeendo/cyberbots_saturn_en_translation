"""EXP-0029: force any pilot's story scenes on an image and check every box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0029/force_check.py \\
        CUE PREDICTION OUT --boxes data/text/santana_boxes.json \\
        [--scenes 23 0 ...] [--steps 150] [--control]

A debug harness; it never ships. It generalizes
``research/experiments/EXP-0026/force_check.py`` (Jin only) with
``research/experiments/EXP-0026/other_pilot.py``'s scene-list redirect:

- **Start:** REF-005 state 4138 (``STATE``: machine select, before
  `STG0AS.BIN` loads), with ``CUE`` mounted, in the silent home. Each scene's
  JSON line names the state and its SHA-256.
- **Pilot:** the box list's ``pilot``. For pilot 0 nothing is redirected
  (the state's pilot is Jin), so Jin's runs are EXP-0026's. For another
  pilot, after 450 frames (the load is done; the first scene is posted near
  frame 600) pilot 0's entry in the per-pilot scene-list table
  (``0x060AAD24``, D-021) is pointed at the pilot's list.
- **Scene:** the first scene the stage posts is replaced: a one-shot write of
  the scene byte ``0x0600828B`` after the game writes it (EXP-0022).
- **Steps:** STEPS x 25 frames, saving a screenshot and the 60 glyph cells
  (WRAM-H ``0x060FE200``) after each step to ``OUT/scene-NN/``.
- **Check:** each box of the scene must show its predicted cells
  (``PREDICTION``, from ``tools.text.dialogue``) as the leading cells of
  some step. With ``--control`` the prediction is ignored.

The scenes default to the box list's ``story_scenes`` (Jin's list predates
the field: 21, 0-15). Prints one JSON line per scene.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.text.dialogue import JIN_STORY, PILOT_LISTS

# EXP-0026's harness has the same file name; load it by path.
_spec = importlib.util.spec_from_file_location(
    "exp0026_force_check", Path("research/experiments/EXP-0026/force_check.py")
)
assert _spec and _spec.loader
_jin = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_jin)
BINARY, CELLS, SCENE_BYTE, STATE, check = (
    _jin.BINARY,
    _jin.CELLS,
    _jin.SCENE_BYTE,
    _jin.STATE,
    _jin.check,
)


def run_scene(cue: Path, pilot: int, scene: int, out: Path, steps: int) -> None:
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
            if pilot:
                agent.frames(450)
                agent.wait_halted(30.0)
                agent.bus_write(PILOT_LISTS, agent.bus_read(PILOT_LISTS + 4 * pilot, 4))
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("write", ["0600828B-0600828B", "2600828B-2600828B"])
            agent.onhit_write(None, SCENE_BYTE, bytes([scene]))
            if pilot:
                agent.run()
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("prediction", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--boxes", type=Path, required=True)
    parser.add_argument("--scenes", type=int, nargs="*")
    parser.add_argument("--steps", type=int, default=150)
    parser.add_argument("--control", action="store_true")
    args = parser.parse_args()
    box_list = json.loads(args.boxes.read_text())
    pilot = int(box_list["pilot"])
    scenes = args.scenes or box_list.get("story_scenes", JIN_STORY)
    prediction = {p["box"]: p["cells"] for p in json.loads(args.prediction.read_text())}
    state_sha = hashlib.sha256(STATE.read_bytes()).hexdigest()
    for scene in scenes:
        out = args.out / f"scene-{scene:02d}"
        run_scene(args.cue, pilot, scene, out, args.steps)
        boxes = [b["box"] for b in box_list["scenes"][scene]["boxes"]]
        result = {} if args.control else check(out, boxes, prediction)
        ok = (
            all(r["matched"] == r["predicted"] for r in result.values())
            if result
            else None
        )
        print(
            json.dumps(
                {
                    "pilot": pilot,
                    "scene": scene,
                    "start": {"state": str(STATE), "sha256": state_sha},
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
