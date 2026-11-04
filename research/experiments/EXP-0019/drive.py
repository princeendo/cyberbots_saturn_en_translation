"""EXP-0019: play the rebuilt image from a cold boot by sending pad keys.

Run from the repository root, one subcommand per call:

    ./invenv.sh python research/experiments/EXP-0019/drive.py launch CUE OUT
    ./invenv.sh python research/experiments/EXP-0019/drive.py key OUT KEY [SECONDS]
    ./invenv.sh python research/experiments/EXP-0019/drive.py shot OUT NAME
    ./invenv.sh python research/experiments/EXP-0019/drive.py stop OUT

``launch`` makes a scratch home, ``local/mednafen_route``. It is a copy of the
silent home's configuration with pad 1 on keyboard keys (A on K, B on H,
Start on N, directions on I, M, J and L, as XvSF's ``tools/mednafen/route.py``
did; pad 2's keys are ``KEYS_2``, named ``p2a`` and so on, EXP-0031), and its
backup RAM starts empty. The user's homes are not changed.
``launch`` then starts the patched build (agent interface, D-007) on CUE with
no state, a cold boot, and records the PID in ``OUT/run.json``. ``key`` holds
one of those keys for SECONDS (default 0.2) through System Events, only while
Mednafen is frontmost, and logs the frame. ``shot`` saves an agent screenshot
``OUT/NAME.png`` and logs the frame. ``stop`` closes Mednafen. Every action is
appended to ``OUT/log.jsonl``.
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, apply_settings, configure
from tools.mednafen.hotkeys import activate, frontmost_pid, osascript

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
HOME = Path("local/mednafen_route")
# SDL scancodes: K 14, H 11, N 17, I 12, M 16, J 13, L 15.
KEYS = {
    "a": ("k", 14),
    "b": ("h", 11),
    "start": ("n", 17),
    "up": ("i", 12),
    "down": ("m", 16),
    "left": ("j", 13),
    "right": ("l", 15),
}
# Pad 2 (EXP-0031): U 24, Y 28, R 21, X 27, G 10, F 9, V 25. T is a hotkey.
KEYS_2 = {
    "p2a": ("y", 28),
    "p2b": ("r", 21),
    "p2start": ("u", 24),
    "p2up": ("x", 27),
    "p2down": ("g", 10),
    "p2left": ("f", 9),
    "p2right": ("v", 25),
}


def make_home() -> Path:
    configure()
    if HOME.exists():
        shutil.rmtree(HOME)
    HOME.mkdir(parents=True)
    shutil.copyfile(QUIET_HOME / "mednafen.cfg", HOME / "mednafen.cfg")
    (HOME / "firmware").symlink_to(Path("..") / "mednafen_quiet" / "firmware")
    apply_settings(
        HOME / "mednafen.cfg",
        {
            **{
                f"ss.input.port1.gamepad.{button}": f"keyboard 0x0 {code}"
                for button, (_key, code) in KEYS.items()
            },
            **{
                f"ss.input.port2.gamepad.{button[2:]}": f"keyboard 0x0 {code}"
                for button, (_key, code) in KEYS_2.items()
            },
        },
    )
    return HOME


def log(out: Path, record: dict[str, object]) -> None:
    with (out / "log.jsonl").open("a") as stream:
        stream.write(json.dumps({"time": time.strftime("%H:%M:%S"), **record}) + "\n")


def agent_for(out: Path) -> Agent:
    agent = Agent((out / "agent").resolve(), timeout=20.0)
    deadline = time.monotonic() + 30
    while True:
        try:
            agent.status()
            return agent
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def frame(out: Path) -> int:
    return int(agent_for(out).status()["frame"])


def launch(cue: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=False)
    home = make_home()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as stream:
        process = subprocess.Popen(
            [str(BINARY), str(cue)],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(json.dumps({"pid": process.pid, "cue": str(cue)}))
    log(out, {"action": "launch", "pid": process.pid, "frame": frame(out)})


def pid_of(out: Path) -> int:
    return int(json.loads((out / "run.json").read_text())["pid"])


def key(out: Path, button: str, seconds: float) -> None:
    pid = pid_of(out)
    letter = {**KEYS, **KEYS_2}[button][0]
    previous = frontmost_pid()
    activate(pid)
    time.sleep(0.4)
    if frontmost_pid() != pid:
        raise SystemExit("Mednafen is not frontmost; key not sent")
    before = frame(out)
    osascript(
        f'tell application "System Events"\nkey down "{letter}"\n'
        f'delay {seconds}\nkey up "{letter}"\nend tell'
    )
    if previous != pid:
        activate(previous)
    log(out, {"action": "key", "button": button, "seconds": seconds, "frame": before})


def shot(out: Path, name: str) -> None:
    agent = agent_for(out)
    agent.screenshot(out / f"{name}.png")
    log(out, {"action": "shot", "name": name, "frame": int(agent.status()["frame"])})


def stop(out: Path) -> None:
    os.kill(pid_of(out), signal.SIGTERM)
    configure()
    log(out, {"action": "stop"})


if __name__ == "__main__":
    command, *rest = sys.argv[1:]
    if command == "launch":
        launch(Path(rest[0]), Path(rest[1]))
    elif command == "key":
        key(Path(rest[0]), rest[1], float(rest[2]) if len(rest) > 2 else 0.2)
    elif command == "shot":
        shot(Path(rest[0]), rest[1])
    elif command == "stop":
        stop(Path(rest[0]))
    else:
        raise SystemExit(f"unknown command {command}")
