"""EXP-0055: cold-boot the built image under one condition and press one button.

Run from the repository root (macOS; the user present, asked first):

    ./invenv.sh python research/experiments/EXP-0055/press.py OUT \\
        [--bkr FIXTURE.bkr] [--bcr FIXTURE.bcr] [--cart auto] \\
        [--press a] [--until 4200]

The play-check harness for `BOOT-005`. It builds the pad-key home of
``EXP-0019/drive.py`` (``local/mednafen_route``; pad 1 on keyboard keys),
copies the fixtures in as its backup memory (as ``EXP-0051/boot_case.py``),
and cold-boots the patched build (D-007) on the built image with
``-ss.cart CART``. Log-mode PC breakpoints mark the save check, the warning
picture (R4), the two continuing paths and the BIOS call. When a warning has
been on screen for 120 frames, the button ``--press`` (a pad key, sent with
System Events only while Mednafen is in front, ``drive.key``) is pressed
once; with no warning no key is sent. Screenshots: 60 frames after the
warning, 120 frames after the press, then every 300 frames to ``--until``.
Everything is logged to ``OUT/route.json``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError

_spec = importlib.util.spec_from_file_location(
    "exp0019_drive", Path("research/experiments/EXP-0019/drive.py")
)
assert _spec and _spec.loader
drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drive)

IMAGE = Path("build/boot004/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue")
GAME = "Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2"
SMPC = Path("local/mednafen_quiet/sav") / f"{GAME}.smpc"
WARNING = 0x06036DA8
WATCHED = {
    0x06036C3E: "check (find save)",
    WARNING: "warning picture (R4 = index)",
    0x06036A1C: "warning 0: after the wait",
    0x06036A58: "write save",
    0x06037064: "save accepted",
    0x06036D8A: "warning 4: after the wait",
    0x0000186C: "BIOS routine at the 0x0600026C vector",
}
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--bkr", type=Path)
    parser.add_argument("--bcr", type=Path)
    parser.add_argument("--cart", default="auto")
    parser.add_argument("--press", default="a")
    parser.add_argument("--until", type=int, default=4200)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    home = drive.make_home()
    sav = home / "sav"
    sav.mkdir(exist_ok=True)
    shutil.copy(SMPC, sav / SMPC.name)
    if args.bkr:
        shutil.copy(args.bkr, sav / f"{GAME}.bkr")
    if args.bcr:
        shutil.copy(args.bcr, sav / f"{GAME}.bcr")
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    hits: list[dict[str, Any]] = []
    shots: list[dict[str, Any]] = []
    presses: list[dict[str, Any]] = []
    with (out / "mednafen.log").open("wb") as stream:
        process = subprocess.Popen(
            [str(drive.BINARY), "-ss.cart", args.cart, str(args.cue)],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(
        json.dumps({"pid": process.pid, "cue": str(args.cue)})
    )
    try:
        agent = Agent((out / "agent").resolve(), timeout=20.0)
        deadline = time.monotonic() + 30
        while True:
            try:
                agent.pause()
                break
            except AgentError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.05)
        agent.bpmode("log")
        agent.breakpoints("pc", [f"{a:08X}" for a in WATCHED])
        agent.clear_events()
        warned_at: int | None = None
        pressed_at: int | None = None
        next_shot = 300
        done = 0
        while done < args.until:
            agent.frames(30)
            status = agent.wait_halted(60.0)
            done += 30
            frame = int(status["frame"])
            for e in agent.events():
                f = dict(FIELD.findall(e))
                if "PC" not in f:
                    continue
                pc = int(f["PC"], 16)
                hits.append(
                    {
                        "frame": int(f["frame"]),
                        "PC": f"0x{pc:08X}",
                        "what": WATCHED.get(pc, "?"),
                        "R4": f.get("R4"),
                    }
                )
                if pc == WARNING and warned_at is None:
                    warned_at = int(f["frame"])
            agent.clear_events()
            name = None
            taken = {s["why"] for s in shots}
            if (
                warned_at is not None
                and pressed_at is None
                and frame >= warned_at + 60
                and "warning" not in taken
            ):
                name = f"warning_{frame:05d}"
                shots.append({"why": "warning", "frame": frame, "png": name + ".png"})
            if (
                pressed_at is not None
                and frame >= pressed_at + 120
                and "after press" not in taken
            ):
                name = f"after_{frame:05d}"
                shots.append(
                    {"why": "after press", "frame": frame, "png": name + ".png"}
                )
            if name is None and done >= next_shot:
                name = f"f{frame:05d}"
                shots.append({"why": "periodic", "frame": frame, "png": name + ".png"})
            if done >= next_shot:
                next_shot += 300
            if name:
                agent.screenshot((out / f"{name}.png").resolve())
            agent.run()
            if (
                args.press
                and warned_at is not None
                and pressed_at is None
                and frame >= warned_at + 120
            ):
                drive.key(out, args.press, 0.2)
                pressed_at = int(agent.status()["frame"])
                presses.append({"button": args.press, "frame": pressed_at})
                agent.pause()
            else:
                agent.pause()
    finally:
        process.terminate()
        process.wait(timeout=30)
        drive.configure()
    result = {
        "cue": str(args.cue),
        "cart": args.cart,
        "bkr": str(args.bkr) if args.bkr else None,
        "bcr": str(args.bcr) if args.bcr else None,
        "hits": hits,
        "presses": presses,
        "shots": shots,
        "sav_after": {
            p.name: p.stat().st_size for p in sorted(sav.iterdir()) if p.is_file()
        },
    }
    (out / "route.json").write_text(json.dumps(result, indent=1) + "\n")
    seen = sorted({h["what"] for h in hits})
    print(out.name, "presses", presses, "seen", seen)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
