"""EXP-0017 (M1): change line 4 of the M1 box in live WRAM-H, with a control.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0017/ram_write.py OUT [--control]

Loads checkpoint A (box open, empty) in the patched build's silent home,
pauses, reads line 4's 26 bytes at WRAM-H ``0x0606F09C`` and, unless
``--control``, writes the test string there and reads it back. Then runs
6 x 50 frames with a screenshot after each (``step01.png`` ...).
``result.json`` records the bytes and frames. Mednafen is closed afterwards.
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
STATE = Path("local/checkpoints/m1/a-box-open.mcs")
LINE4 = 0x0606F09C  # Saturn line 4 in resident STG0AS.BIN (D-015)
TEST = "あいうえおかきくけこさしす".encode("shift_jis")  # 26 bytes, as line 4


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


def main(out: Path, control: bool) -> int:
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "control": control}
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
            agent.pause()
            result["paused_frame"] = int(agent.status()["frame"])
            original = agent.bus_read(LINE4, len(TEST))
            result["original"] = original.hex()
            if not control:
                agent.bus_write(LINE4, TEST)
                result["written"] = TEST.hex()
                result["readback"] = agent.bus_read(LINE4, len(TEST)).hex()
            agent.run()
            frames = []
            for step in range(1, 7):
                agent.frames(50)
                frames.append(int(agent.wait_halted(30.0)["frame"]))
                agent.screenshot(out / f"step{step:02d}.png")
                agent.run()
            result["step_frames"] = frames
            result["after"] = agent.bus_read(LINE4, len(TEST)).hex()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), "--control" in sys.argv[2:]))
