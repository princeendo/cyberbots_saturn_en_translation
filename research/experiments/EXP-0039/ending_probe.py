"""EXP-0039: run an ending from the END-001 checkpoint and record how it draws.

Copied from EXP-0038, ``ending_probe.py`` (commit ``865b649``), with the
options listed at the end.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0038/ending_probe.py OUT \\
        [--cue CUE] [--state STATE] [--frames 6300] [--step 10] \\
        [--cells-until 6300] [--write ADDR=HEX] [--write-scene 16] \\
        [--vram-at F,F,...] [--save-at F,F,...]

A debug harness; it never ships. No key is pressed and no fight is forced:
the checkpoint (``EXP-0037``, ``jin_ending_a16503.mcs``) is past the fight.
It loads ``STATE`` with ``CUE`` mounted (default: the untouched image) in the
silent home and runs ``--frames`` in ``--step``-frame polls. It logs:

- Play Disc commands and scene posts (``EXP-0031/loads.py``'s decoder) and
  every call of `END.BIN`'s box routine ``0x0606268C`` (R5 table, R6 word);
- the 60 glyph cells at ``0x060FE200`` (D-020) at every poll up to
  ``--cells-until`` (``OUT/cNNNNN.bin``), and a screenshot every 50 frames
  (``OUT/fNNNNN.png``);
- VDP1 and VDP2 VRAM in full at the first poll at or after each
  ``--vram-at`` frame (``OUT/vdp1_NNNNN.bin``, ``OUT/vdp2_NNNNN.bin``, read
  through the agent, D-007);
- a save state at the first poll at or after each ``--save-at`` frame
  (``OUT/sNNNNN.mcs``; taken while running, so its frame is approximate).

``--write ADDR=HEX`` makes one RAM write at the first poll after scene
``--write-scene`` is posted by `END.BIN` (``0x06066852``), after reading the
bytes it replaces; both are logged to ``OUT/writes.jsonl``. Writes
``OUT/route.json``.

``--write-bp`` adds log-mode write breakpoints (``A-B`` hex bus ranges); each
hit's frame, PC, PR and R0-R7 go to ``route.json`` (``write_hits``).

Added in EXP-0039:

- ``--onhit PC:ADDR=HEX`` (repeatable): a log-mode PC breakpoint at ``PC``
  whose hit writes ``HEX`` at ``ADDR`` (the agent's ``onhit``, applied after
  the hit instruction); each hit and each action line is logged
  (``onhit_hits``, ``onhit_actions``).
- ``--write-load FILE:DELAY``: arm ``--write`` at the first poll at least
  ``DELAY`` frames after ``FILE`` is read, instead of after a scene post.
- ``--watch ADDR:LEN``: read those bytes at every poll (``OUT/poll.jsonl``).
- Each scene post also records its R4 (the list number, EXP-0039).
"""

from __future__ import annotations

import argparse
import hashlib
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
from tools.mednafen.home import QUIET_HOME, configure

_spec = importlib.util.spec_from_file_location(
    "exp0031_loads", Path("research/experiments/EXP-0031/loads.py")
)
assert _spec and _spec.loader
_loads = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_loads)
BINARY, IMAGE, LISTING, CR1, CR2, POSTS, decode = (
    _loads.BINARY,
    _loads.IMAGE,
    _loads.LISTING,
    _loads.CR1,
    _loads.CR2,
    _loads.POSTS,
    _loads.decode,
)

STATE = Path("local/end001/checkpoint/jin_ending_a16503.mcs")
END_POST = 0x06066852
END_BOX = 0x0606268C
CELLS, CELL_BYTES = 0x060FE200, 60 * 0x80
VRAM = 0x80000
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frames_list(text: str | None) -> list[int]:
    return sorted(int(x) for x in text.split(",")) if text else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    parser.add_argument("--frames", type=int, default=6300)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--cells-until", type=int, default=6300)
    parser.add_argument("--write")
    parser.add_argument("--write-scene", type=int, default=16)
    parser.add_argument("--vram-at")
    parser.add_argument("--save-at")
    parser.add_argument("--write-bp", help="comma-separated hex ranges, A-B")
    parser.add_argument("--onhit", action="append", default=[])
    parser.add_argument("--write-load")
    parser.add_argument("--watch")
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    files = json.loads(LISTING.read_text())["files"]
    vram_at, save_at = frames_list(args.vram_at), frames_list(args.save_at)
    write_address, write_data = None, b""
    if args.write:
        a, d = args.write.split("=")
        write_address, write_data = int(a, 16), bytes.fromhex(d)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    loads: list[dict[str, object]] = []
    posts: list[dict[str, object]] = []
    boxes: list[dict[str, object]] = []
    dumps: list[dict[str, object]] = []
    saves: list[dict[str, object]] = []
    hits: list[dict[str, str]] = []
    onhit_hits: list[dict[str, object]] = []
    actions: list[str] = []
    polls = (out / "poll.jsonl").open("w")
    result: dict[str, object] = {
        "state": str(args.state),
        "state_sha256": sha256(args.state),
        "cue": str(args.cue),
        "write": args.write,
        "write_scene": args.write_scene if args.write else None,
    }
    writes = (out / "writes.jsonl").open("w")
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(args.cue)], env=env, stdout=log, stderr=subprocess.STDOUT
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
                    time.sleep(0.5)
            time.sleep(3)
            if agent.halted():
                agent.run()
            agent.loadstate(args.state.resolve())
            agent.clear_events()
            agent.bpmode("log")
            onhits = []
            for item in args.onhit:
                pc, rest = item.split(":")
                a, d = rest.split("=")
                onhits.append((int(pc, 16), int(a, 16), bytes.fromhex(d)))
            watched = (CR1, CR2, *POSTS, END_BOX, *(o[0] for o in onhits))
            agent.breakpoints("pc", [f"{a:08X}" for a in watched])
            for pc, a, d in onhits:
                agent.onhit_write(pc, a, d)
            load_name, load_delay = None, 0
            if args.write_load:
                load_name, delay = args.write_load.split(":")
                load_delay = int(delay)
            load_at: int | None = None
            if args.write_bp:
                agent.breakpoints("write", args.write_bp.split(","))
            armed = False
            written = write_address is None
            done = 0
            while done < args.frames:
                agent.frames(args.step)
                status = agent.wait_halted(60.0)
                done += args.step
                frame = int(status["frame"])
                raw = agent.events()
                actions += [e for e in raw if e.startswith("action")]
                raw = [e for e in raw if "PC=" in e]
                found_loads, found_posts = decode(raw, files)
                r4s = [
                    f"{int(f['R4'], 16) & 0xFF}"
                    for f in (dict(FIELD.findall(e)) for e in raw)
                    if int(f.get("PC", "0"), 16) in POSTS
                ]
                for post, r4 in zip(found_posts, r4s, strict=True):
                    post["r4"] = int(r4)
                for e in raw:
                    f = dict(FIELD.findall(e))
                    if onhits and int(f.get("PC", "0"), 16) in {o[0] for o in onhits}:
                        onhit_hits.append(
                            {"frame": int(f["frame"]), "PC": f["PC"], "R4": f["R4"]}
                        )
                for e in raw:
                    f = dict(FIELD.findall(e))
                    if int(f.get("PC", "0"), 16) == END_BOX:
                        boxes.append(
                            {
                                "frame": int(f["frame"]),
                                "table": f"0x{int(f['R5'], 16):08X}",
                                "word": f"0x{int(f['R6'], 16) & 0xFFFF:04X}",
                            }
                        )
                for e in raw:
                    f = dict(FIELD.findall(e))
                    if "PC" in f and int(f["PC"], 16) not in watched:
                        hits.append(
                            {
                                k: f[k]
                                for k in (
                                    "frame",
                                    "PC",
                                    "PR",
                                    "R0",
                                    "R1",
                                    "R2",
                                    "R3",
                                    "R4",
                                    "R5",
                                    "R6",
                                    "R7",
                                )
                                if k in f
                            }
                        )
                agent.clear_events()
                loads += found_loads
                posts += found_posts
                if not written and armed:
                    assert write_address is not None
                    before = agent.bus_read(write_address, len(write_data))
                    agent.bus_write(write_address, write_data)
                    after = agent.bus_read(write_address, len(write_data))
                    writes.write(
                        json.dumps(
                            {
                                "frame": frame,
                                "address": f"0x{write_address:08X}",
                                "before": before.hex(),
                                "data": write_data.hex(),
                                "readback": after.hex(),
                            }
                        )
                        + "\n"
                    )
                    written = True
                for x in found_loads:
                    if load_name and str(x.get("file", "")).startswith(load_name):
                        load_at = load_at or int(str(x["frame"]))
                if load_name:
                    armed = load_at is not None and frame >= load_at + load_delay
                else:
                    for p in found_posts:
                        if p["routine"] == f"0x{END_POST:08X}" and (
                            p["scene"] == args.write_scene
                        ):
                            armed = True
                if args.watch:
                    wa, wl = args.watch.split(":")
                    polls.write(
                        json.dumps(
                            {
                                "frame": frame,
                                "bytes": agent.bus_read(int(wa, 16), int(wl, 16)).hex(),
                            }
                        )
                        + "\n"
                    )
                if done <= args.cells_until:
                    (out / f"c{frame:05d}.bin").write_bytes(
                        agent.bus_read(CELLS, CELL_BYTES)
                    )
                if done % 50 == 0:
                    agent.screenshot(out / f"f{frame:05d}.png")
                if vram_at and frame >= vram_at[0]:
                    vram_at.pop(0)
                    for space, name in (("vdp1vram", "vdp1"), ("vdp2vram", "vdp2")):
                        path = out / f"{name}_{frame:05d}.bin"
                        path.write_bytes(agent.read(space, 0, VRAM))
                        dumps.append({"frame": frame, "file": path.name})
                agent.run()
                if save_at and frame >= save_at[0]:
                    save_at.pop(0)
                    path = out / f"s{frame:05d}.mcs"
                    agent.savestate(path)
                    saves.append(
                        {
                            "requested_after": frame,
                            "frame_after": int(agent.status()["frame"]),
                            "file": path.name,
                        }
                    )
        finally:
            process.terminate()
            process.wait(timeout=30)
            writes.close()
            polls.close()
    configure()
    for s in saves:
        s["sha256"] = sha256(out / str(s["file"]))
    result |= {
        "frames": args.frames,
        "loads": loads,
        "posts": posts,
        "boxes": boxes,
        "vram_dumps": dumps,
        "saves": saves,
        "write_hits": hits,
        "onhit_hits": onhit_hits,
        "onhit_actions": actions,
    }
    (out / "route.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"loads": len(loads), "posts": len(posts), "boxes": len(boxes)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
