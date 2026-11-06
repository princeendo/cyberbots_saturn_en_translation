"""EXP-0060: every Latin name on the real screens of the built image.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0060/check_screens.py OUT \\
        [--build build/loc005/a] [--out-json research/experiments/EXP-0060/screens.json]

No key, no cold boot. The patched build (D-007) in the silent home with the
built image mounted:

- **Select** (session state 2538, before `SELECT.VAD` loads): the built
  `SELECT.VAD` loads from the disc; `STG0A.BIN` is already resident in that
  state, so its built part table (``name_art_changes.json``'s range) is
  written into RAM at ``0x06060000`` + offset right after the load. When the
  select screen is up, each name frame (``0x14``-``0x1C``) is set in the name
  record (``0x06065198``).
- **VS** (session state 6448, before `PL3F_0.BIN` loads): everything from
  the disc. For each pilot frame (``0x02``-``0x0A``) and mech frame
  (``0x0C``-``0x1B``) the state is loaded again (the VS screen lasts only a
  few seconds), run to the VS screen, and the frame set in the player-1
  record.

For each name: a screenshot, and the name's sprite parts (by colour word and
area) compared with the built data: each part's pixels must be one of the
frame's built patterns (the `SELECT.VAD` slot, or a decoded `PL3F_0.BIN`
record), and every built pattern of the frame must be on screen. Writes
``OUT/<screen>-<frame>.png`` and the JSON report.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.memory import vdp1_sprites
from tools.text import dialogue, name_art, pattern_t2

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
STATES = Path("local/ref005/session/states")
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"


def start(out: Path, cue: Path, state: Path) -> tuple[subprocess.Popen[bytes], Agent]:
    configure()
    agent_dir = (out / f"agent-{state.stem}").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    log = (out / f"mednafen-{state.stem}.log").open("wb")
    process = subprocess.Popen([str(BINARY), str(cue)], env=env, stdout=log, stderr=log)
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
    agent.pause()
    return process, agent


def run(agent: Agent, frames: int, writes: list[tuple[int, bytes]]) -> None:
    if not writes:
        agent.frames(frames)
        agent.wait_halted(120.0)
        return
    for _ in range(frames):
        for address, data in writes:
            agent.bus_write(address, data)
        agent.frames(1)
        agent.wait_halted(30.0)


def on_screen(agent: Agent, colour: int, y0: int, y1: int, mirror: bool) -> list[bytes]:
    vram = agent.read("vdp1vram", 0, 0x80000)
    out = []
    for sp in vdp1_sprites.sprites(vram):
        if sp.color_word == colour and y0 <= sp.y <= y1 and sp.x < 176:
            size = sp.width * sp.height // 2
            if mirror and sp.source >= 0x10000:
                out.append(agent.bus_read(0x060E0000 + sp.source, size))
            else:
                out.append(vdp1_sprites.pixel_bytes(vram, sp))
    return out


def shot(agent: Agent, path: Path) -> str:
    agent.screenshot(path.resolve())
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--build", type=Path, default=Path("build/loc005/a"))
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    cue = args.build / CUE
    vad = (args.build / "SELECT.VAD").read_bytes()
    stg0a = (args.build / "STG0A.BIN").read_bytes()
    pl = (args.build / "PL3F_0.BIN").read_bytes()
    stg0as = bytes(dialogue.checked("STG0AS.BIN"))
    ranges = json.loads((args.build / "name_art_changes.json").read_text())["ranges"]
    parts_range = next(r for r in ranges if r["file"] == "STG0A.BIN")
    approved = json.loads(Path("data/translations/name_art.json").read_text())
    report: dict[str, Any] = {"select": [], "vs": []}

    process, agent = start(out, cue, STATES / "f00002538.mcs")
    try:
        lo, hi = parts_range["start"], parts_range["end"]
        agent.bus_write(0x06060000 + lo, stg0a[lo:hi])
        run(agent, 460, [])
        for k, frame in enumerate(name_art.SEL_FRAMES):
            run(agent, 6, [(0x06065198, frame.to_bytes(2, "big"))])
            slot = name_art.SEL_BLOCK + name_art.SEL_SLOT * k
            want = {vad[slot : slot + name_art.SEL_SLOT]}
            have = on_screen(agent, 0x61E0, 195, 215, mirror=False)
            png = out / f"select-{frame:02x}.png"
            report["select"].append(
                {
                    "frame": f"0x{frame:02X}",
                    "name": approved["pilots"]["names"][k],
                    "parts_on_screen": len(have),
                    "all_built": all(h in want for h in have) and bool(have),
                    "screenshot_sha256": shot(agent, png),
                }
            )
    finally:
        process.terminate()
        process.wait(timeout=30)

    def built_patterns(frame: int) -> set[bytes]:
        patterns = set()
        for p in name_art.frame_parts(
            stg0as, name_art.VS_FRAME_TABLE, name_art.VS_FRAMES, frame
        ):
            w1, w2 = struct.unpack_from(">2H", pl, 6 * p + 2)
            offset = (((w1 & 1) << 16) | w2) * 4
            data = pattern_t2.decode(pl[offset:])
            if any(data):
                patterns.add(data)
        return patterns

    process, agent = start(out, cue, STATES / "f00006448.mcs")
    try:
        cases = [(f, 0x06087E9E, 0x41E0, (200, 220)) for f in name_art.VS_PILOTS]
        cases += [(f, 0x06087A44, 0x41C0, (25, 45)) for f in name_art.VS_MECHS]
        names = approved["pilots"]["names"] + [m[0] for m in approved["mechs"]["names"]]
        for (frame, address, colour, (y0, y1)), name in zip(cases, names, strict=True):
            # The VS screen lasts only a few seconds: reload the state each time.
            agent.run()
            agent.loadstate((STATES / "f00006448.mcs").resolve())
            agent.pause()
            run(agent, 340, [])
            run(agent, 8, [(address, frame.to_bytes(2, "big"))])
            want = built_patterns(frame)
            have = [h for h in on_screen(agent, colour, y0, y1, mirror=True) if any(h)]
            png = out / f"vs-{frame:02x}.png"
            report["vs"].append(
                {
                    "frame": f"0x{frame:02X}",
                    "name": name,
                    "parts_on_screen": len(have),
                    "all_built": all(h in want for h in have) and set(have) == want,
                    "screenshot_sha256": shot(agent, png),
                }
            )
    finally:
        process.terminate()
        process.wait(timeout=30)

    report["ok"] = all(r["all_built"] for r in report["select"] + report["vs"])
    print(json.dumps(report, indent=1, ensure_ascii=False))
    if args.out_json:
        args.out_json.write_text(
            json.dumps(report, indent=1, ensure_ascii=False) + "\n"
        )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
