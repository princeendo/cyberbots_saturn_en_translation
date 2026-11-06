"""EXP-0051: what one button press does on a warning screen (from a state).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0051/button.py CASE \\
        --read PC [--bits 0100] [--frames 900]

A debug harness; it never ships. No key is pressed and no cold boot is made:
it starts the patched build in ``CASE/home`` (the case's own fixtures), loads
the case's warning state (``CASE/s*.mcs``), and halts at ``--read``, the
instruction that reads the pad word (``mov.w @(8,Rn)``, Rn = ``0x060CC00E``).
There it writes ``--bits`` to ``0x060CC016``, as if that button had been
pressed, then runs ``--frames`` frames with log-mode breakpoints on the
routines below. Hits and screenshots (every 150 frames) go to
``CASE/button_BITS/``.
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

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
PAD = 0x060CC016
WATCHED = {
    0x0600026C: "BIOS vector call",
    0x06036A1C: "warning 0: after the wait",
    0x06036A58: "write save",
    0x06037064: "save accepted",
    0x06036D8A: "warning 4: after the wait",
    0x06036DA8: "warning picture (R4 = index)",
}
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("case", type=Path)
    parser.add_argument("--read", required=True)
    parser.add_argument("--bits", default="0100")
    parser.add_argument("--frames", type=int, default=900)
    parser.add_argument("--cart", default="auto")
    args = parser.parse_args()
    state = sorted(args.case.glob("s*.mcs"))[0]
    out = args.case / f"button_{args.bits}"
    out.mkdir()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str((args.case / "home").resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {
        "state": str(state),
        "read": args.read,
        "bits": args.bits,
    }
    hits: list[dict[str, str]] = []
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), "-ss.cart", args.cart, str(IMAGE)],
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
            agent.loadstate(state.resolve())
            agent.bpmode("halt")
            agent.breakpoints("pc", [args.read])
            status = agent.wait_halted(30.0)
            before = agent.bus_read(PAD, 2)
            agent.bus_write(PAD, bytes.fromhex(args.bits))
            result["halt"] = status
            result["pad_before"] = before.hex()
            result["pad_written"] = agent.bus_read(PAD, 2).hex()
            agent.breakpoints("pc", [])
            agent.bpmode("log")
            agent.breakpoints("pc", [f"{a:08X}" for a in WATCHED])
            agent.clear_events()
            done = 0
            while done < args.frames:
                agent.frames(30)
                status = agent.wait_halted(60.0)
                done += 30
                for e in agent.events():
                    f = dict(FIELD.findall(e))
                    if "PC" in f:
                        hits.append(
                            {
                                "frame": f["frame"],
                                "PC": f["PC"],
                                "what": WATCHED.get(int(f["PC"], 16), "?"),
                                "R4": f.get("R4", ""),
                            }
                        )
                agent.clear_events()
                if done % 150 == 0:
                    agent.screenshot(out / f"f{int(status['frame']):05d}.png")
                agent.run()
        finally:
            process.terminate()
            process.wait(timeout=30)
    result["hits"] = hits
    (out / "route.json").write_text(json.dumps(result, indent=1) + "\n")
    first: dict[str, str] = {}
    for h in hits:
        first.setdefault(h["what"], h["frame"])
    print(
        args.case.name, "pad", result["pad_before"], "->", result["pad_written"], first
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
