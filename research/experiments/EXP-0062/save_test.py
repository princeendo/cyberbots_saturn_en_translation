"""EXP-0062: make the game save from the Options screen, with one byte changed.

Run from the repository root (no key):

    ./invenv.sh python research/experiments/EXP-0062/save_test.py OUT \\
        [--write ADDR=HEX ...] [--state STATE]

A scratch copy of the silent home (configuration, firmware link, backup
memory) in ``OUT/home``. Loads STATE (default the session's Options screen,
27173) on the untouched image, makes the writes, then sets the menu's state
word ``0x060CFEE0`` to 4, the state the Start button leads to (it waits
for the fade flag ``0x060CFEA0`` to be clear, then calls the save routine
``0x06036A58``). Log-mode PC breakpoints at ``0x06036A58`` (save) and
``0x06036F10`` (buffer build). Runs 600 frames, screenshots, quits
Mednafen so it writes the backup memory, then extracts the game's file
``CYBERBOTS01`` from ``OUT/home/sav/*.bkr`` to ``OUT/CYBERBOTS01.bin`` and
writes ``OUT/save.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
UNTOUCHED = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
STATE = Path("local/ref005/session/states/f00027173.mcs")
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
BLOCK = 64


def scratch_home(home: Path) -> Path:
    configure()
    home.mkdir(parents=True)
    shutil.copyfile(QUIET_HOME / "mednafen.cfg", home / "mednafen.cfg")
    (home / "firmware").symlink_to((QUIET_HOME / "firmware").resolve())
    shutil.copytree(QUIET_HOME / "sav", home / "sav")
    return home


def game_file(bkr: bytes, name: bytes) -> bytes:
    """The data of a backup-RAM file (layout in tools/mednafen/backup_ram.py).

    Assumes the block-number list fits in the first block (true for a
    256-byte save: four numbers and the terminator).
    """
    for first in range(2, len(bkr) // BLOCK):
        block = bkr[first * BLOCK : (first + 1) * BLOCK]
        if block[:4] == b"\x80\0\0\0" and block[4:15] == name:
            size = int.from_bytes(block[30:34], "big")
            numbers, p = [], 34
            while (n := int.from_bytes(block[p : p + 2], "big")) != 0:
                numbers.append(n)
                p += 2
            data = bytearray(block[p + 2 :])
            for n in numbers:
                data += bkr[n * BLOCK + 4 : (n + 1) * BLOCK]
            return bytes(data[:size])
    raise SystemExit(f"{name!r} not found")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--write", action="append", default=[])
    parser.add_argument("--state", type=Path, default=STATE)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    home = scratch_home(out / "home")
    bkr_path = next((home / "sav").glob("*.bkr"))
    try:
        before = game_file(bkr_path.read_bytes(), b"CYBERBOTS01")
    except SystemExit:
        before = b""
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(UNTOUCHED)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
    agent = Agent((out / "agent").resolve(), timeout=20.0)
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
    agent.bus_write(0x060CFEE0, (4).to_bytes(2, "big"))
    agent.bpmode("log")
    agent.breakpoints("pc", ["06036A58", "06036F10"])
    agent.clear_events()
    agent.frames(600)
    agent.wait_halted(120.0)
    hits = [dict(FIELD.findall(e)) for e in agent.events()]
    hits = [h for h in hits if "PC" in h]
    settings = agent.bus_read(0x060D9290, 16)
    agent.screenshot((out / "after.png").resolve())
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=30)
    after = game_file(bkr_path.read_bytes(), b"CYBERBOTS01")
    (out / "CYBERBOTS01.bin").write_bytes(after)
    report = {
        "writes": args.write,
        "save_calls": [h["PC"] for h in hits][:10],
        "settings_ram": settings.hex(),
        "file_size": len(after),
        "before_sha256": hashlib.sha256(before).hexdigest(),
        "after_sha256": hashlib.sha256(after).hexdigest(),
        "differ_offsets": [
            i for i in range(len(after)) if i >= len(before) or after[i] != before[i]
        ][:40],
        "after_bytes_0_40": after[:40].hex(" "),
    }
    (out / "save.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
