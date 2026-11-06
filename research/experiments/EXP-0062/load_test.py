"""EXP-0062: does a changed save load at boot? (from a pre-check state, no key)

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0062/load_test.py OUT BKR \\
        [--set OFFSET=HEX ...] [--fix-sum]

Session state 384 is before the boot save check (``0x06036C3E``, about
frame 1,370, D-048). In a scratch copy of the silent home, the state is
loaded, the internal backup memory (the agent's ``backup`` space, 32 KiB in
the ``.bkr`` layout) is replaced by BKR, with the game file
``CYBERBOTS01``'s data bytes changed by ``--set`` (data offsets) and, with
``--fix-sum``, its last word set to the 16-bit sum of bytes 0-253 (the rule
seen in ``save_test.py``'s two saves). Log-mode PC breakpoints: the check,
the warning picture ``0x06036DA8`` (R4 = picture), the accepted path
``0x06037064``. Runs 1,500 frames; screenshot; ``0x060D9290``-``9F``.
Writes ``OUT/load.json``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError

_spec = importlib.util.spec_from_file_location(
    "save_test", Path("research/experiments/EXP-0062/save_test.py")
)
assert _spec and _spec.loader
save_test = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(save_test)

STATE = Path("local/ref005/session/states/f00000384.mcs")
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
BLOCK = 64
NAME = b"CYBERBOTS01"


def data_offsets(bkr: bytes) -> list[int]:
    """The .bkr offset of each data byte of CYBERBOTS01, in order ([] if none)."""
    for first in range(2, len(bkr) // BLOCK):
        block = bkr[first * BLOCK : (first + 1) * BLOCK]
        if block[:4] == b"\x80\0\0\0" and block[4:15] == NAME:
            size = int.from_bytes(block[30:34], "big")
            numbers, p = [], 34
            while (n := int.from_bytes(block[p : p + 2], "big")) != 0:
                numbers.append(n)
                p += 2
            where = list(range(first * BLOCK + p + 2, (first + 1) * BLOCK))
            for n in numbers:
                where += range(n * BLOCK + 4, (n + 1) * BLOCK)
            return where[:size]
    return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("bkr", type=Path)
    parser.add_argument("--set", action="append", default=[])
    parser.add_argument("--fix-sum", action="store_true")
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    bkr = bytearray(args.bkr.read_bytes())
    where = data_offsets(bytes(bkr))
    for item in args.set:
        offset, value = item.split("=")
        bkr[where[int(offset, 0)]] = int(value, 16)
    data = bytes(bkr[i] for i in where) if where else bytes(256)
    if args.fix_sum and where:
        total = sum(data[:254]) & 0xFFFF
        bkr[where[254]], bkr[where[255]] = total >> 8, total & 0xFF
        data = bytes(bkr[i] for i in where)
    home = save_test.scratch_home(out / "home")
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(save_test.BINARY), str(save_test.UNTOUCHED)],
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
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
    agent.loadstate(STATE.resolve())
    agent.pause()
    agent.write("backup", 0, bytes(bkr))
    agent.bpmode("log")
    agent.breakpoints("pc", ["06036C3E", "06036DA8", "06037064"])
    agent.clear_events()
    agent.frames(1500)
    agent.wait_halted(120.0)
    hits = []
    for e in agent.events():
        f = dict(FIELD.findall(e))
        if "PC" in f:
            hits.append({"PC": f["PC"], "R4": f.get("R4"), "frame": f.get("frame")})
    settings = agent.bus_read(0x060D9290, 16)
    saved = agent.read("backup", 0, 32768)
    (out / "backup_after.bkr").write_bytes(saved)
    agent.screenshot((out / "after.png").resolve())
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=30)
    report = {
        "bkr": str(args.bkr),
        "set": args.set,
        "fix_sum": args.fix_sum,
        "file_settings": data[4:20].hex(),
        "file_sum": data[254:256].hex(),
        "hits": hits[:12],
        "settings_ram_after": settings.hex(),
    }
    (out / "load.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
