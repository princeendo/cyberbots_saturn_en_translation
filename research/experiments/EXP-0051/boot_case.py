"""EXP-0051: cold-boot the untouched image under one backup-memory condition.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0051/boot_case.py OUT \\
        [--bkr FIXTURE.bkr] [--bcr FIXTURE.bcr] [--cart auto] [--frames 3000]

A debug harness; it never ships. No key is pressed. It makes a fresh
Mednafen home in ``OUT/home`` (the silent home's configuration and SMPC
file, the shared firmware), puts ``--bkr`` in as the internal backup memory
and ``--bcr`` as the backup cart's memory (each copied; omitted means
Mednafen's own), and cold-boots the patched build (D-007) with
``-ss.cart CART``. It pauses at the first agent reply, sets log-mode PC
breakpoints on the save check's routines (static reading, EXP-0051) and
runs ``--frames`` in 30-frame polls:

- each hit's frame, PC, PR and R4 go to ``OUT/route.json`` (``hits``);
- the check's results (``0x060DBA94``-``0x060DBA9F``) are read at every
  poll (``poll.jsonl``);
- a screenshot every 300 frames, and 60 frames after each warning call
  (``0x06036DA8``) a screenshot, the full VDP2 VRAM and a save state.

Afterwards the home's ``sav/`` files are listed with their hashes, so the
fixtures used and what the game wrote are on record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
GAME = "Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2"
WARNING = 0x06036DA8
WATCHED = {
    0x06036C3E: "check (find save)",
    0x060367F4: "BUP init and status",
    0x060368FC: "read save",
    0x06036754: "warning, wait (any key: BIOS)",
    0x06036974: "warning 0 call",
    WARNING: "warning picture (R4 = index)",
    0x06037064: "save accepted",
    0x06036A58: "write save",
    0x0600026C: "BIOS vector call",
}
RESULTS, RESULTS_LEN = 0x060DBA94, 12
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_home(home: Path, bkr: Path | None, bcr: Path | None) -> None:
    for sub in ("sav", "mcs", "b", "snaps", "cheats", "mcm", "palettes", "pgconfig"):
        (home / sub).mkdir(parents=True)
    shutil.copy(QUIET_HOME / "mednafen.cfg", home / "mednafen.cfg")
    (home / "firmware").symlink_to((QUIET_HOME / "firmware").resolve())
    shutil.copy(QUIET_HOME / "sav" / f"{GAME}.smpc", home / "sav" / f"{GAME}.smpc")
    if bkr:
        shutil.copy(bkr, home / "sav" / f"{GAME}.bkr")
    if bcr:
        shutil.copy(bcr, home / "sav" / f"{GAME}.bcr")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--bkr", type=Path)
    parser.add_argument("--bcr", type=Path)
    parser.add_argument("--cart", default="auto")
    parser.add_argument("--frames", type=int, default=3000)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    home = out / "home"
    make_home(home, args.bkr, args.bcr)
    result: dict[str, object] = {
        "cue": str(args.cue),
        "cart": args.cart,
        "bkr": str(args.bkr) if args.bkr else None,
        "bkr_sha256": sha256(args.bkr) if args.bkr else None,
        "bcr": str(args.bcr) if args.bcr else None,
        "bcr_sha256": sha256(args.bcr) if args.bcr else None,
        "binary_sha256": sha256(BINARY),
    }
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    hits: list[dict[str, object]] = []
    shots: list[dict[str, object]] = []
    polls = (out / "poll.jsonl").open("w")
    pending: list[int] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), "-ss.cart", args.cart, str(args.cue)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            deadline = time.monotonic() + 30
            while True:
                try:
                    agent.pause()
                    break
                except AgentError:
                    if time.monotonic() > deadline:
                        raise
                    time.sleep(0.05)
            result["first_frame"] = int(agent.status()["frame"])
            agent.bpmode("log")
            agent.breakpoints("pc", [f"{a:08X}" for a in WATCHED])
            agent.clear_events()
            done = 0
            while done < args.frames:
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
                            "PR": f.get("PR"),
                            "R4": f.get("R4"),
                        }
                    )
                    if pc == WARNING:
                        pending.append(int(f["frame"]) + 60)
                agent.clear_events()
                polls.write(
                    json.dumps(
                        {
                            "frame": frame,
                            "results": agent.bus_read(RESULTS, RESULTS_LEN).hex(),
                        }
                    )
                    + "\n"
                )
                capture = pending and frame >= pending[0]
                if capture:
                    pending.pop(0)
                    path = out / f"w{frame:05d}.png"
                    agent.screenshot(path)
                    vdp2 = out / f"vdp2_{frame:05d}.bin"
                    vdp2.write_bytes(agent.read("vdp2vram", 0, 0x80000))
                    shots.append({"frame": frame, "png": path.name, "vdp2": vdp2.name})
                elif done % 300 == 0:
                    agent.screenshot(out / f"f{frame:05d}.png")
                agent.run()
                if capture:
                    state = out / f"s{frame:05d}.mcs"
                    agent.savestate(state)
                    shots[-1]["state"] = state.name
        finally:
            process.terminate()
            process.wait(timeout=30)
            polls.close()
    result["hits"] = hits
    result["warning_captures"] = shots
    result["sav_after"] = {
        p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)}
        for p in sorted((home / "sav").iterdir())
    }
    (out / "route.json").write_text(json.dumps(result, indent=1) + "\n")
    warnings = [h["R4"] for h in hits if h["PC"] == f"0x{WARNING:08X}"]
    print(out.name, "warnings (R4):", warnings, "hits:", len(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
