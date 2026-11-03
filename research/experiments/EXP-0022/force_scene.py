"""EXP-0022: force which story scene starts, and check its first box's cells.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0022/force_scene.py OUT [SCENE]

A debug harness; it never ships. Loads REF-005 session state 5208 (Jin's
opening narration, before scene 0 is posted) in the patched build's silent
home. With ``SCENE``, it sets a log-mode write breakpoint on the scene byte of
the next scene task (``0x0600828B``, task + ``0x23``) and queues a one-shot
write of ``SCENE`` there, applied right after the game writes it. Without
``SCENE`` it is the control. It then runs 24 x 25 frames, and after each step
saves a screenshot and the first 40 glyph cells of the WRAM-H shadow
(``0x060FE200``, D-015) to ``OUT/cells-NN.bin``. ``result.json`` records the
breakpoint events and frames.
"""

from __future__ import annotations

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
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
STATE = Path("local/ref005/session/states/f00005208.mcs")
SCENE_BYTE = 0x0600828B  # task 0x06008268 + 0x23, as in EXP-0022's traces
CELLS = 0x060FE200
CELL_BYTES = 0x80


def connect(agent: Agent, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            agent.status()
            return
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def main(out: Path, scene: int | None) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "scene": scene}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            connect(agent)
            time.sleep(3)  # let the boot settle before replacing the machine state
            if agent.halted():
                agent.run()
            agent.loadstate(STATE.resolve())
            agent.clear_events()
            if scene is not None:
                agent.bpmode("log")
                agent.breakpoints("write", ["0600828B-0600828B", "2600828B-2600828B"])
                agent.onhit_write(None, SCENE_BYTE, bytes([scene]))
            frames = []
            for step in range(1, 25):
                agent.frames(25)
                frames.append(int(agent.wait_halted(30.0)["frame"]))
                agent.screenshot(out / f"step{step:02d}.png")
                cells = agent.bus_read(CELLS, 40 * CELL_BYTES)
                (out / f"cells-{step:02d}.bin").write_bytes(cells)
                agent.run()
            result["step_frames"] = frames
            result["events"] = agent.events()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"scene": scene, "events": len(result.get("events", []))}))  # type: ignore[arg-type]
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else None)
    )
