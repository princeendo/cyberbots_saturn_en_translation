"""EXP-0057: draw every frame of a sprite bank on the real screen (no keys).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0057/walk.py OUT --state STATE \\
        --record ADDR --first 1 --last 122 [--hold 8] [--crop X,Y,W,H]

A debug harness; it never ships. One launch of the patched build (D-007)
in the silent home: load STATE, then for each frame number N from
``--first`` to ``--last`` write N into the pose record's frame word
(``ADDR`` + 6; D-051), run ``--hold`` frames (the pattern is uploaded and
drawn), and take a screenshot. The record keeps its screen position, so
each frame of the bank is drawn where that record's name normally is.
Writes ``OUT/fNNN.png`` and, with ``--crop``, one contact sheet of the
crops (``OUT/sheet.png``), plus ``OUT/walk.json`` (screenshot hashes).
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
from tools.memory.mcs_extract import encode_png

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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--record", required=True)
    parser.add_argument("--first", type=int, default=1)
    parser.add_argument("--last", type=int, required=True)
    parser.add_argument("--hold", type=int, default=8)
    parser.add_argument("--crop")
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    word = int(args.record, 16) + 6
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    shots: dict[str, str] = {}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.loadstate(args.state.resolve())
            agent.pause()
            for n in range(args.first, args.last + 1):
                agent.bus_write(word, n.to_bytes(2, "big"))
                agent.frames(args.hold)
                agent.wait_halted(30.0)
                path = out / f"f{n:03d}.png"
                agent.screenshot(path.resolve())
                shots[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        finally:
            process.terminate()
            process.wait(timeout=30)
    if args.crop:
        x0, y0, cw, ch = (int(v) for v in args.crop.split(","))
        names = sorted(shots)
        cols = 6
        rows = (len(names) + cols - 1) // cols
        w_all, h_all = cols * cw, rows * (ch + 10)
        sheet = bytearray(bytes((40, 0, 40)) * w_all * h_all)
        for k, name in enumerate(names):
            w, _h, bpp, raw = read_png(out / name)
            ox, oy = (k % cols) * cw, (k // cols) * (ch + 10)
            for y in range(ch):
                for x in range(cw):
                    i = ((y0 + y) * w + x0 + x) * bpp
                    o = ((oy + y) * w_all + ox + x) * 3
                    sheet[o : o + 3] = raw[i : i + 3]
        (out / "sheet.png").write_bytes(encode_png(w_all, h_all, bytes(sheet)))
    (out / "walk.json").write_text(
        json.dumps(
            {"state": str(args.state), "record": args.record, "shots": shots}, indent=1
        )
        + "\n"
    )
    print(out, len(shots), "frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
