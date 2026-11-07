"""EXP-0067: a no-input cold boot of the current image, every frame recorded.

Run from the repository root (a cold boot: ask the user first):

    ./invenv.sh python research/experiments/EXP-0067/attract.py OUT \\
        [--cue CUE] [--frames 32000]

The patched build (D-007) in ``EXP-0019/drive.py``'s pad-key home (so the
silent home stays free), launched with ``-qtrecord OUT/run.mov`` (every
frame, with sound) and no state. As soon as the agent answers, log-mode PC
breakpoints are set on the CD command writes (CR1 ``0x0603D18C``, CR2
``0x0603D194``; Play Disc FADs as in ``EXP-0031/loads.py``) and on the
named open ``0x06038E40`` (R4 = the file name, D-056). It runs to frame
FRAMES with no key, then closes Mednafen. Writes ``OUT/loads.json``: each
Play Disc start (frame, FAD, the file named by the ISO listing) and each
named open (frame, name, destination).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError

_spec = importlib.util.spec_from_file_location(
    "drive", Path("research/experiments/EXP-0019/drive.py")
)
assert _spec and _spec.loader
drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drive)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
CUE = Path("build/opt005/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue")
LISTING = Path("references/saturn_jp/iso_listing.json")


def file_at(lsn: int, files: list[dict[str, Any]]) -> str:
    for f in files:
        if f["lsn"] <= lsn < f["lsn"] + max(1, (f["size_bytes"] + 2047) // 2048):
            return str(f["path"])
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--cue", type=Path, default=CUE)
    parser.add_argument("--frames", type=int, default=32000)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    home = drive.make_home()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(drive.BINARY), "-qtrecord", str(out / "run.mov"), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    try:
        agent = Agent((out / "agent").resolve(), timeout=20.0)
        deadline = time.monotonic() + 30
        while True:
            try:
                agent.status()
                break
            except AgentError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.1)
        agent.bpmode("log")
        agent.breakpoints("pc", ["0603D18C", "0603D194", "06038E40"])
        agent.clear_events()
        if agent.halted():
            agent.run()
        start = int(agent.status()["frame"])
        while int(agent.status()["frame"]) < args.frames:
            time.sleep(2)
        agent.pause()
        names = {}
        events = []
        for line in agent.events():
            f = dict(FIELD.findall(line))
            if "PC" in f:
                events.append(f)
        opens = []
        for f in events:
            if f["PC"] == "06038E40":
                r4 = int(f["R4"], 16)
                if r4 not in names:
                    try:
                        names[r4] = (
                            agent.bus_read(r4, 16).split(b"\0")[0].decode("latin-1")
                        )
                    except AgentError:
                        names[r4] = "?"
                opens.append(
                    {
                        "frame": int(f["frame"]),
                        "name": names[r4],
                        "dest": f["R5"],
                        "max": f["R6"],
                    }
                )
    finally:
        process.terminate()
        process.wait(timeout=60)
    files = json.loads(LISTING.read_text())["files"]
    plays = []
    for i, f in enumerate(events):
        if f["PC"] != "0603D18C":
            continue
        r3 = int(f.get("R3", "0"), 16) & 0xFFFF
        if r3 >> 8 != 0x10 or i + 1 >= len(events):
            continue
        cr2 = int(events[i + 1].get("R3", "0"), 16) & 0xFFFF
        item: dict[str, Any] = {
            "frame": int(f["frame"]),
            "cr1": f"{r3:04X}",
            "cr2": f"{cr2:04X}",
        }
        if r3 & 0x80:  # a FAD: a data read
            fad = ((r3 & 0x7F) << 16) | cr2
            item["fad"] = fad
            item["file"] = file_at(fad - 150, files)
        else:  # a track and index: audio
            item["track"] = cr2 >> 8
        plays.append(item)
    report = {
        "cue": str(args.cue),
        "first_frame_logged": start,
        "frames": args.frames,
        "named_opens": opens,
        "play_disc": plays,
    }
    (out / "loads.json").write_text(json.dumps(report, indent=1) + "\n")
    print(len(opens), "named opens;", len(plays), "play-disc starts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
