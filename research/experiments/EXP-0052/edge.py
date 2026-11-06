"""EXP-0052: find the picture's visible bottom row by writing VDP2 VRAM.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0052/edge.py OUT

A debug harness; no key, no cold boot. It starts the patched build in
``local/boot001/zero/home``, loads that case's warning state (`EXP-0051`,
`WARNING1` on screen), takes a screenshot, then writes into the bitmap at
VDP2 VRAM ``0x20000`` (512 bytes a row):

- file rows 220-223, columns 0-351: value 12 (yellow);
- file rows 224-227, columns 0-351: value 9 (red);
- file rows 50-53, columns 348-351: value 14 (cyan).

It runs 10 frames and takes a second screenshot. ``OUT/edge.json`` lists,
per screen row, the colours that changed. Numbers only.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError

_spec = importlib.util.spec_from_file_location(
    "exp0038_compare", Path("research/experiments/EXP-0038/compare_runs.py")
)
assert _spec and _spec.loader
_cmp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_cmp)
read_png = _cmp.read_png

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
CASE = Path("local/boot001/zero")
BITMAP, WIDTH = 0x20000, 512
WRITES = [(220, 223, 0, 351, 12), (224, 227, 0, 351, 9), (50, 53, 348, 351, 14)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str((CASE / "home").resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
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
                    time.sleep(0.2)
            if agent.halted():
                agent.run()
            agent.loadstate((CASE / "s01457.mcs").resolve())
            agent.frames(10)
            agent.wait_halted(30.0)
            agent.screenshot((out / "before.png").resolve())
            for r0, r1, c0, c1, value in WRITES:
                for r in range(r0, r1 + 1):
                    agent.write(
                        "vdp2vram",
                        BITMAP + r * WIDTH + c0,
                        bytes([value]) * (c1 - c0 + 1),
                    )
            agent.frames(10)
            agent.wait_halted(30.0)
            agent.screenshot((out / "after.png").resolve())
        finally:
            process.terminate()
            process.wait(timeout=30)
    w, h, bpp, a = read_png(out / "before.png")
    _, _, _, b = read_png(out / "after.png")
    rows = {}
    for y in range(h):
        changed: Counter[str] = Counter()
        for x in range(w):
            i = (y * w + x) * bpp
            if a[i : i + 3] != b[i : i + 3]:
                changed[bytes(b[i : i + 3]).hex()] += 1
        if changed:
            rows[y] = dict(changed)
    result = {"writes": WRITES, "changed_screen_rows": rows}
    (out / "edge.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
