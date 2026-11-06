"""EXP-0064: a recorded cold boot with read/write logs on candidate ranges.

Run from the repository root (a cold boot with presses: ask the user first):

    ./invenv.sh python research/experiments/EXP-0064/cold_watch.py launch OUT \\
        --ranges FILE [--cart none]
    ./invenv.sh python research/experiments/EXP-0064/cold_watch.py report OUT

``launch`` makes ``EXP-0019/drive.py``'s pad-key home, sets ``ss.cart``
(default ``none``: no RAM cart, so `3M RAM MODE` is off), cold-boots the
untouched image paused at frame 0, sets log-mode read and write
breakpoints on every range of FILE, and lets it run. Presses are then sent
with ``drive.py key OUT BUTTON`` (one per call). ``report`` summarizes
``OUT/agent/events.log``: hits per PC with first and last frame, to
``OUT/cold_watch.json``.
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

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import apply_settings

_spec = importlib.util.spec_from_file_location(
    "drive", Path("research/experiments/EXP-0019/drive.py")
)
assert _spec and _spec.loader
drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drive)
UNTOUCHED = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def launch(out: Path, ranges_file: Path, cart: str) -> None:
    out.mkdir(parents=True, exist_ok=False)
    home = drive.make_home()
    apply_settings(home / "mednafen.cfg", {"ss.cart": cart})
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as stream:
        process = subprocess.Popen(
            [str(drive.BINARY), str(UNTOUCHED)],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(
        json.dumps({"pid": process.pid, "cue": str(UNTOUCHED)})
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
    agent.pause()
    ranges = json.loads(ranges_file.read_text())
    spec = [f"{a}-{int(b, 16) - 1:08X}" for a, b in ranges]
    agent.bpmode("log")
    agent.breakpoints("read", spec)
    agent.breakpoints("write", spec)
    agent.clear_events()
    frame = int(agent.status()["frame"])
    agent.run()
    drive.log(
        out, {"action": "launch", "pid": process.pid, "frame": frame, "cart": cart}
    )
    print("running from frame", frame)


def report(out: Path) -> None:
    counts: dict[str, list[int]] = {}
    with (out / "agent" / "events.log").open() as stream:
        for line in stream:
            f = dict(FIELD.findall(line))
            if "PC" not in f:
                continue
            frame = int(f.get("frame", "0"))
            row = counts.setdefault(f["PC"], [0, frame, frame])
            row[0] += 1
            row[2] = frame
    rows = sorted(counts.items(), key=lambda kv: kv[1][1])
    result = {pc: {"hits": c, "first": a, "last": b} for pc, (c, a, b) in rows}
    (out / "cold_watch.json").write_text(json.dumps(result, indent=1) + "\n")
    for pc, r in result.items():
        print(pc, r)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["launch", "report"])
    parser.add_argument("out", type=Path)
    parser.add_argument("--ranges", type=Path)
    parser.add_argument("--cart", default="none")
    args = parser.parse_args()
    if args.command == "launch":
        launch(args.out, args.ranges, args.cart)
    else:
        report(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def attribute_cold(out: Path, ranges_file: Path, cyber: Path) -> dict[str, object]:
    """Per-range hits of a cold-boot log, for PCs inside ``CYBER.BIN``.

    The instruction at each PC is read from ``CYBER.BIN`` (resident at
    ``0x0600D000``); hits from other code (BIOS, boot loader, overlays) are
    listed by PC and frame span, unattributed.
    """
    aspec = importlib.util.spec_from_file_location(
        "attribute", Path("research/experiments/EXP-0064/attribute.py")
    )
    assert aspec and aspec.loader
    attribute = importlib.util.module_from_spec(aspec)
    aspec.loader.exec_module(attribute)
    code = cyber.read_bytes()
    base = 0x0600D000
    ranges = [(int(a, 16), int(b, 16)) for a, b in json.loads(ranges_file.read_text())]
    by_range: dict[str, dict[str, list[int]]] = {}
    other: dict[str, list[int]] = {}
    with (out / "agent" / "events.log").open() as stream:
        for line in stream:
            f = dict(FIELD.findall(line))
            if "PC" not in f:
                continue
            pc, frame = int(f["PC"], 16), int(f.get("frame", "0"))
            if base <= pc < base + len(code) - 1:
                op = int.from_bytes(code[pc - base : pc - base + 2], "big")
                regs = {k: int(v, 16) for k, v in f.items() if k[0] in "RG"}
                hit = attribute.access(op, regs)
                k = attribute.in_ranges(hit[0], hit[1], ranges) if hit else None
                if k is not None and hit is not None:
                    row = by_range.setdefault(str(k), {}).setdefault(
                        f"{f['PC']}:{hit[2]}", [0, frame, frame]
                    )
                    row[0] += 1
                    row[2] = frame
                    continue
            row = other.setdefault(f["PC"], [0, frame, frame])
            row[0] += 1
            row[2] = frame
    return {"by_range": by_range, "other": other}
