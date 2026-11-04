"""EXP-0031: log which disc files the game reads, from a state, with screenshots.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0031/loads.py STATE OUT \\
        [--frames 2500] [--cue CUE]

A debug harness; it never ships. It loads ``STATE`` with ``CUE`` mounted
(default: the untouched image) in the silent home, with no input, and logs:

- **Play Disc commands:** a log-mode PC breakpoint on the CD command
  routine's CR1 and CR2 writes (``0x0603D18C``, ``0x0603D194``; EXP-0018).
  A CR1 value ``0x10xx`` is Play Disc. With bit ``0x80`` set, the start is
  a FAD, ``(CR1 & 0x7F) << 16 | CR2``, named by the ISO listing (LSN = FAD -
  150); without it, CR2 is a track and index (audio).
- **Scene posts:** R5 at the scene-post routines (`STG0AS.BIN`
  ``0x0606DBEA``, `END.BIN` ``0x06066852``; EXP-0022).

It runs ``--frames`` in 25-frame steps and saves a screenshot every 50
frames to ``OUT/fNNNNN.png``. Writes ``OUT/loads.json`` and prints a summary.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
LISTING = Path("references/saturn_jp/iso_listing.json")
CR1, CR2 = 0x0603D18C, 0x0603D194
POSTS = (0x0606DBEA, 0x06066852)
STEP = 25
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def name_of(fad: int, files: list[dict[str, object]]) -> str:
    lsn = fad - 150
    for f in files:
        start = int(f["lsn"])  # type: ignore[call-overload]
        sectors = -(-int(f["size_bytes"]) // 2048)  # type: ignore[call-overload]
        if start <= lsn < start + sectors:
            return f"{f['path']}+{lsn - start}"
    return "?"


def decode(
    raw: list[str], files: list[dict[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Play Disc commands and scene posts in a batch of logged events."""
    loads: list[dict[str, object]] = []
    posts: list[dict[str, object]] = []
    events = [dict(FIELD.findall(e)) for e in raw]
    for i, e in enumerate(events):
        pc = int(e["PC"], 16)
        r3 = int(e["R3"], 16) & 0xFFFF
        if pc == CR1 and r3 >> 8 == 0x10 and i + 1 < len(events):
            cr2 = int(events[i + 1]["R3"], 16) & 0xFFFF
            item: dict[str, object] = {
                "frame": int(e["frame"]),
                "cr1": f"{r3:04X}",
                "cr2": f"{cr2:04X}",
            }
            if r3 & 0x80:  # start given as a FAD: a data read
                fad = (r3 & 0x7F) << 16 | cr2
                item["fad"] = f"0x{fad:06X}"
                item["file"] = name_of(fad, files)
            else:  # start given as track and index: audio
                item["track"] = cr2 >> 8
                item["index"] = cr2 & 0xFF
            loads.append(item)
        elif pc in POSTS:
            posts.append(
                {
                    "frame": int(e["frame"]),
                    "routine": f"0x{pc:08X}",
                    "scene": int(e["R5"], 16),
                }
            )
    return loads, posts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--frames", type=int, default=2500)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    files = json.loads(LISTING.read_text())["files"]
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    loads: list[dict[str, object]] = []
    posts: list[dict[str, object]] = []
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
                    time.sleep(0.5)
            time.sleep(3)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("pc", [f"{a:08X}" for a in (CR1, CR2, *POSTS)])
            done = 0
            while done < args.frames:
                agent.frames(STEP)
                status = agent.wait_halted(60.0)
                done += STEP
                frame = int(status["frame"])
                found_loads, found_posts = decode(agent.events(), files)
                agent.clear_events()
                loads += found_loads
                posts += found_posts
                if done % 50 == 0:
                    agent.screenshot(out / f"f{frame:05d}.png")
                agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    result = {
        "state": str(args.state),
        "frames": args.frames,
        "loads": loads,
        "posts": posts,
    }
    (out / "loads.json").write_text(json.dumps(result, indent=1) + "\n")
    for item in loads:
        print(json.dumps(item))
    for item in posts:
        print(json.dumps(item))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
