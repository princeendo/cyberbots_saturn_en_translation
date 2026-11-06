"""EXP-0059: Latin name samples drawn on the real select and VS screens.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0059/sample.py select OUT
    ./invenv.sh python research/experiments/EXP-0059/sample.py vs OUT

A debug harness for the user's choice; it never ships and changes no file.
One launch of the patched build (D-007) in the silent home:

- ``select``: session state 3070, the name record (``0x06065192``) set to
  Santana's frame (``0x15``); each sample is drawn over that name's parts,
  run 4 frames, screenshot;
- ``vs``: session state 6805, the player-1 pilot record set to frame
  ``0x03`` (Santana) and the mech record left on Blodia. The model code
  (indices 0xA-0xC) is kept.

The name's parts are found in the live VDP1 command list (colour word and
screen area), with their flip bits (command word 0, bits 4-5): each sample
is rendered as displayed across the parts, then each part's slice is
un-flipped and written to its pattern. On the VS screen VDP1 VRAM
``0x10000`` up is refreshed each frame from WRAM-H ``0x060F0000`` up, so
those patterns are written there (bus ``0x060E0000`` + the VRAM offset).

Writes ``OUT/<n>-<style>-<name>.png`` and ``OUT/samples.json`` (hashes).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.memory import vdp1_sprites

_spec = importlib.util.spec_from_file_location(
    "exp0059_banner", Path("research/experiments/EXP-0059/banner.py")
)
assert _spec and _spec.loader
banner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(banner)

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
STATES = Path("local/ref005/session/states")
PILOTS = ["Jin", "Santana", "Bao & Mao", "Devilotte", "Chiyomaru", "SHADE"]
MECHS = ["BLODIA", "R·LIGHTNING", "KILLER BEE"]


def start(out: Path, state: Path) -> tuple[subprocess.Popen[bytes], Agent]:
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    log = (out / "mednafen.log").open("wb")
    process = subprocess.Popen(
        [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=log
    )
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


def step(agent: Agent, frames: int, writes: list[tuple[int, bytes]]) -> None:
    for _ in range(frames):
        for address, data in writes:
            agent.bus_write(address, data)
        agent.frames(1)
        agent.wait_halted(30.0)


Part = tuple[int, int, int, int, int, int]  # source, width, height, x, y, flips


def name_parts(agent: Agent, colour: int, y0: int, y1: int, x1: int) -> list[Part]:
    """The player-1 name's sprite parts on screen, with their flip bits."""
    vram = agent.read("vdp1vram", 0, 0x80000)
    out = []
    for sp in vdp1_sprites.sprites(vram):
        if sp.color_word == colour and y0 <= sp.y <= y1 and sp.x < x1:
            control = struct.unpack_from(">H", vram, sp.command_address)[0]
            out.append((sp.source, sp.width, sp.height, sp.x, sp.y, (control >> 4) & 3))
    return out


def read_part(agent: Agent, part: Part, mirror: bool) -> list[list[int]]:
    source, width, height, _x, _y, flips = part
    size = width * height // 2
    if mirror and source >= 0x10000:
        data = agent.bus_read(0x060E0000 + source, size)
    else:
        data = agent.read("vdp1vram", source, size)
    grid = [
        [
            (data[(y * width + x) // 2] >> (4 if x % 2 == 0 else 0)) & 15
            for x in range(width)
        ]
        for y in range(height)
    ]
    if flips & 1:
        grid = [row[::-1] for row in grid]
    if flips & 2:
        grid = grid[::-1]
    return grid


def write_part(agent: Agent, part: Part, grid: list[list[int]], mirror: bool) -> None:
    source, _width, _height, _x, _y, flips = part
    if flips & 2:
        grid = grid[::-1]
    if flips & 1:
        grid = [row[::-1] for row in grid]
    data = banner.pack(grid)
    if mirror and source >= 0x10000:
        agent.bus_write(0x060E0000 + source, data)
    else:
        agent.write("vdp1vram", source, data)


def place(
    agent: Agent,
    parts: list[Part],
    name: str,
    kind: str,
    style: str,
    mirror: bool,
    keep: tuple[int, ...] = (),
) -> None:
    """Draw ``name`` across the parts as displayed, keeping ``keep`` indices."""
    left = min(p[3] for p in parts)
    width = max(p[3] + p[1] for p in parts) - left
    width += width % 2
    grid = banner.render(name, kind, style, width)
    if keep:
        for part in parts:
            old = read_part(agent, part, mirror)
            for y, row in enumerate(old[:16]):
                for x, v in enumerate(row):
                    if v in keep:
                        grid[y][part[3] - left + x] = v
    for part in parts:
        x0 = part[3] - left
        write_part(
            agent, part, [row[x0 : x0 + part[1]] for row in grid[: part[2]]], mirror
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("screen", choices=("select", "vs"))
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    shots: dict[str, str] = {}
    n = 0
    if args.screen == "select":
        process, agent = start(out, STATES / "f00003070.mcs")
        record = [(0x06065198, b"\x00\x15")]
        try:
            step(agent, 20, record)
            parts = name_parts(agent, 0x61E0, 195, 215, 352)
            for style in ("banner", "white"):
                for name in PILOTS:
                    place(agent, parts, name, "pilot", style, mirror=False)
                    step(agent, 4, record)
                    n += 1
                    slug = re.sub(r"[^A-Za-z]", "", name)
                    path = out / f"{n:02d}-{style}-{slug}.png"
                    agent.screenshot(path.resolve())
                    shots[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        finally:
            process.terminate()
            process.wait(timeout=30)
    else:
        process, agent = start(out, STATES / "f00006805.mcs")
        record = [(0x06087E9E, b"\x00\x03")]
        try:
            step(agent, 20, record)
            pilot_parts = name_parts(agent, 0x41E0, 200, 220, 176)
            mech_parts = name_parts(agent, 0x41C0, 25, 45, 176)
            for style in ("banner", "white"):
                for k, mech in enumerate(MECHS):
                    place(
                        agent, pilot_parts, PILOTS[1 + k], "pilot", style, mirror=True
                    )
                    place(
                        agent,
                        mech_parts,
                        mech,
                        "mech",
                        style,
                        mirror=True,
                        keep=(10, 11, 12),
                    )
                    step(agent, 3, record)
                    n += 1
                    slug = re.sub(r"[^A-Za-z]", "", mech)
                    path = out / f"{n:02d}-{style}-{slug}.png"
                    agent.screenshot(path.resolve())
                    shots[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        finally:
            process.terminate()
            process.wait(timeout=30)
    (out / "samples.json").write_text(json.dumps(shots, indent=1) + "\n")
    print(out, len(shots))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
