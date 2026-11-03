"""EXP-0025: cold-boot an image and drive Jin's arcade route to the M1 box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/cold_route.py CUE OUT

Uses ``research/experiments/EXP-0019/drive.py`` (patched build, scratch home
``local/mednafen_route``, pad keys through System Events). Each key is retried
up to 4 times if Mednafen is not frontmost. The route, from the screens of
EXP-0019's play check:

1. wait for frame 3500;
2. press Start only when the title shows its logo and the cyan prompt, until
   the mode menu shows;
3. A (ARCADE MODE), A (Jin, under the cursor), A twice (Blodia);
4. a screenshot every 2 s for 90 s.

Screens are classified by pixel counts only. All shots and ``log.jsonl`` go
to ``OUT``.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

DRIVE = "research/experiments/EXP-0019/drive.py"
W = 352


def run(*args: str) -> int:
    return subprocess.run(["./invenv.sh", "python", DRIVE, *args]).returncode


def shot(out: Path, name: str) -> bytes:
    if run("shot", str(out), name):
        raise SystemExit("screenshot failed")
    command = ["ffmpeg", "-loglevel", "error", "-i", str(out / f"{name}.png")]
    command += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    return subprocess.run(command, capture_output=True, check=True).stdout


def key(out: Path, button: str, seconds: str = "0.4") -> None:
    for _ in range(4):
        if run("key", str(out), button, seconds) == 0:
            return
        time.sleep(0.7)
    raise SystemExit(f"{button} could not be sent")


def features(raw: bytes) -> tuple[int, int, int]:
    def p(x: int, y: int) -> bytes:
        return raw[(y * W + x) * 3 : (y * W + x) * 3 + 3]

    prompt = sum(
        1
        for y in range(165, 185)
        for x in range(80, 280)
        if p(x, y)[2] > 200 and p(x, y)[0] < 80
    )
    logo = sum(
        1
        for y in range(20, 100, 2)
        for x in range(20, 330, 2)
        if p(x, y)[0] > 200 and p(x, y)[2] < 120
    )
    menu = sum(
        1
        for y in range(150, 170)
        for x in range(80, 280)
        if p(x, y)[2] > 200 and p(x, y)[1] > 200 and p(x, y)[0] < 120
    )
    return prompt, logo, menu


def main(cue: Path, out: Path) -> int:
    if run("launch", str(cue), str(out)):
        raise SystemExit("launch failed")
    sys.path.insert(0, str(Path.cwd()))
    from tools.mednafen.agent import Agent

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
    shot(out, "select-pilot")
    key(out, "a")  # Jin
    time.sleep(6)
    shot(out, "select-machine")
    key(out, "a")  # Blodia
    time.sleep(2)
    key(out, "a")
    for k in range(45):
        time.sleep(2)
        shot(out, f"route{k:02d}")
    run("stop", str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
