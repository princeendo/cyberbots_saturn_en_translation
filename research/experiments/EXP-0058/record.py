"""EXP-0058: record a stretch of play, with sound, from a saved state.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0058/record.py OUT --state STATE \\
        --frames N [--write ADDR=HEX ...] [--onhit PC:ADDR=HEX ...]

A debug harness; it never ships. It starts the patched build (D-007) in the
silent home with ``-qtrecord OUT/run.mov`` (video and sound; the silent
home's volume setting does not reach the recording), loads STATE, makes
the writes (and arms ``--onhit`` writes, applied after each hit of PC, as
``EXP-0042/probe.py``), runs N frames, and closes Mednafen. Then ffmpeg keeps only the
last N frames' worth of sound (the part after the load) as
``OUT/clip.wav`` (mono 22,050 Hz, for listening) and a contact sheet of the
video every second (``OUT/sheet.png``). ``OUT/record.json`` holds the
hashes. Nothing here is committed but the record.
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
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
FPS = 59.82  # NTSC Saturn field rate as Mednafen reports it (approximate)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--write", action="append", default=[])
    parser.add_argument("--onhit", action="append", default=[], help="PC:ADDR=HEX")
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    movie = out / "run.mov"
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), "-qtrecord", str(movie), str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
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
            for item in args.write:
                address, data = item.split("=")
                agent.bus_write(int(address, 16), bytes.fromhex(data))
            if args.onhit:
                agent.bpmode("log")
                pcs = []
                for item in args.onhit:
                    pc, rest = item.split(":")
                    address, data = rest.split("=")
                    pcs.append(pc)
                    agent.onhit_write(
                        int(pc, 16), int(address, 16), bytes.fromhex(data)
                    )
                agent.breakpoints("pc", pcs)
            agent.frames(args.frames)
            agent.wait_halted(600.0)
        finally:
            process.terminate()
            process.wait(timeout=60)
    seconds = args.frames / FPS
    clip = out / "clip.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-sseof",
            f"-{seconds:.2f}",
            "-i",
            str(movie),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "22050",
            str(clip),
        ],
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-sseof",
            f"-{seconds:.2f}",
            "-i",
            str(movie),
            "-vf",
            "fps=1,scale=176:-1,tile=6x10",
            "-frames:v",
            "1",
            str(out / "sheet.png"),
        ],
        check=True,
    )
    record = {
        "state": str(args.state),
        "state_sha256": sha(args.state),
        "frames": args.frames,
        "writes": args.write,
        "onhit": args.onhit,
        "clip_sha256": sha(clip),
        "movie_bytes": movie.stat().st_size,
    }
    (out / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
