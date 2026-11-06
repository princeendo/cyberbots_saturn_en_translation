"""EXP-0050: from a saved state, force Jin to his last stage and run into an ending.

Copied from ``EXP-0037/ending_route.py`` (commit ``ea2e69c``) with one
option added: ``--ending N`` makes the round end's copy of the winner's pilot
byte into the ending number (``0x06018E0C``, D-036) write N instead, by an
on-hit RAM write, so list N's ending plays (``EXP-0039``'s method).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0050/ending_route.py OUT \\
        [--state STATE] [--cue CUE] [--index 8] [--frames 30000] \\
        [--save-at FRAME] [--start-state CHECKPOINT]

A debug harness; it never ships. No key is pressed. It loads ``STATE``
(default: REF-005 state 4138, machine select with Jin, before `STG0AS.BIN`
loads) with ``CUE`` mounted (default: the untouched image) in the silent
home, then:

- **Stage:** at the first poll after the arcade start has set player 2
  (``0x06027834``'s write at ``0x06027848``, frame 305 from 4138), it writes
  player 1's stage index (``0x060D02BF``, record ``0x060CFFDC`` + ``0x2E3``)
  = ``--index``. `STG0AS.BIN`'s stage start (``0x0606086C``, near frame 619)
  then sets the stage byte ``0x060CFF88`` itself from the order table
  (``0x0607B440`` + pilot x 10 + index). Earlier versions of this script
  wrote the stage byte after the stage start: one stage-0 step had already
  run, so scene 21 was posted with stage 8's scene 14 (``route1``-``run8``);
  the untouched image showed both, the M5 image stalled. A run that wrote only
  the stage byte went on to stage 1 after the win (``route1``): the index
  carries the progress.
- **Opponent:** the same poll does what ``0x06027950`` (the caller of
  ``0x06027834``) does after a win, for entry k = row x 16 + index (the row
  at record + ``0x2E2``): player 2's pilot (record ``0x060D02D0`` +
  ``0x2D2``) = ``0x0604B5C0``[k], its machine bytes (+ ``0x2D3``-``0x2D5``)
  = ``0x0604B650``[k], the word ``0x060CFF08`` = the pilot, and, when
  entry k + 1 is negative (the row's end), the last-fight flag
  ``0x060CFF07`` = 1. A run without the opponent fought index 0's opponent
  (``route2``); a run without the flag went back to stage 0 after the win
  (``route3``). Every RAM write is logged to ``OUT/writes.jsonl``. With
  ``--start-state`` it loads that checkpoint instead and writes none of
  these.
- **Fight:** from the post of scene ``--fight-after`` (default 15, Jin's
  last pre-fight scene, posted by stage 8 step 8) until `END.BIN` is read
  or posts a scene, it holds player 1's vitality pair at 152 and, once player
  2's pair is settled, sets it to 0 (D-025), so the fight ends at time-out.
- **Logs:** Play Disc commands and scene posts (``EXP-0031/loads.py``'s
  decoder, with each post's return address PR as ``caller``); every call
  of `END.BIN`'s box routine ``0x0606268C`` (its copy of `STG0AS.BIN`'s
  ``0x0606E504``: R5 the record table, R6 the box word,
  ``0x8000`` set to close); the stage and step bytes every 25 frames
  (``OUT/poll.jsonl``); and every 50 frames a screenshot (``OUT/fNNNNN.png``)
  and the 60 glyph cells at ``0x060FE200`` (``OUT/cNNNNN.bin``, D-020).
- **Checkpoint:** with ``--save-at FRAME`` it saves ``OUT/checkpoint.mcs``
  at the first poll at or after that frame (resuming first: a save is
  refused while halted) and records the frame it was taken at.

Runs ``--frames`` in 25-frame steps. Writes ``OUT/route.json``.
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

STATE = Path("local/ref005/session/states/f00004138.mcs")
STAGE = 0x060CFF88
P1_VITALITY, P2_VITALITY = 0x060D0024, 0x060D0318
FULL = 152
STEP = 25
END_POST = 0x06066852
OPPONENT_SET = 0x06027848  # 0x06027834's write of player 2's pilot
END_BOX = 0x0606268C  # END.BIN's copy of the box routine (STG0AS 0x0606E504)
CELLS, CELL_BYTES = 0x060FE200, 60 * 0x80
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
ENDING_COPY = 0x06018E0C  # the round end, after the pilot byte's copy (D-036)
ENDING_NUMBER = 0x060CFF7E
INDEX = 0x060D02BF
CPU_PILOT, FOES, FOE_MACHINES = 0x060D05A2, 0x0604B5C0, 0x0604B650
ROW, FOE_WORD, LAST_FIGHT = 0x060D02BE, 0x060CFF08, 0x060CFF07


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--state", type=Path, default=STATE)
    parser.add_argument("--start-state", type=Path)
    parser.add_argument("--cue", type=Path, default=IMAGE)
    parser.add_argument("--index", type=int, default=8)
    parser.add_argument("--fight-after", type=int, default=15)
    parser.add_argument("--frames", type=int, default=30000)
    parser.add_argument("--save-at", type=int)
    parser.add_argument("--ending", type=int, help="force list N's ending")
    args = parser.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    files = json.loads(LISTING.read_text())["files"]
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
    start = args.start_state or args.state
    result: dict[str, object] = {
        "state": str(start),
        "state_sha256": sha256(start),
        "cue": str(args.cue),
        "index": None if args.start_state else args.index,
    }
    writes = (out / "writes.jsonl").open("w")
    polls = (out / "poll.jsonl").open("w")

    def write(agent: Agent, frame: int, address: int, data: bytes, why: str) -> None:
        agent.bus_write(address, data)
        writes.write(
            json.dumps(
                {
                    "frame": frame,
                    "address": f"0x{address:08X}",
                    "data": data.hex(),
                    "why": why,
                }
            )
            + "\n"
        )

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
            agent.loadstate(start.resolve())
            agent.clear_events()
            agent.bpmode("log")
            actions: list[str] = []
            watched = [CR1, CR2, *POSTS, OPPONENT_SET, END_BOX]
            if args.ending is not None:
                watched.append(ENDING_COPY)
            agent.breakpoints("pc", [f"{a:08X}" for a in watched])
            if args.ending is not None:
                agent.onhit_write(ENDING_COPY, ENDING_NUMBER, bytes([args.ending]))
            staged = bool(args.start_state)
            holding = bool(args.start_state)
            ended = False
            done = 0
            while done < args.frames:
                agent.frames(STEP)
                status = agent.wait_halted(60.0)
                done += STEP
                frame = int(status["frame"])
                raw = agent.events()
                actions += [e for e in raw if e.startswith("action")]
                raw = [e for e in raw if "PC=" in e]  # on-hit action lines
                if not staged and any(f"PC={OPPONENT_SET:08X}" in e for e in raw):
                    write(agent, frame, INDEX, bytes([args.index]), "stage index")
                    k = 16 * agent.bus_read(ROW, 1)[0] + args.index
                    foe, after = agent.bus_read(FOES + k, 2)
                    machine = agent.bus_read(FOE_MACHINES + k, 1)[0]
                    write(
                        agent,
                        frame,
                        CPU_PILOT,
                        bytes([foe, machine, machine, machine]),
                        "player 2 pilot, machine",
                    )
                    write(
                        agent, frame, FOE_WORD, foe.to_bytes(2, "big"), "opponent word"
                    )
                    if after >= 0x80:
                        write(agent, frame, LAST_FIGHT, b"\1", "last-fight flag")
                    staged = True
                found_loads, found_posts = decode(raw, files)
                callers = [
                    f"0x{int(f['PR'], 16):08X}"
                    for f in (dict(FIELD.findall(e)) for e in raw)
                    if int(f.get("PC", "0"), 16) in POSTS
                ]
                for post, caller in zip(found_posts, callers, strict=True):
                    post["caller"] = caller
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
                agent.clear_events()
                loads += found_loads
                posts += found_posts
                if any(
                    str(x.get("file", "")).startswith("END.BIN") for x in found_loads
                ):
                    ended = True
                for p in found_posts:
                    if p["routine"] == f"0x{END_POST:08X}":
                        ended = True
                    elif p["scene"] == args.fight_after:
                        holding = True
                stage = agent.bus_read(STAGE, 2)
                polls.write(
                    json.dumps({"frame": frame, "stage": stage[0], "step": stage[1]})
                    + "\n"
                )
                if holding and not ended:
                    pair = agent.bus_read(P2_VITALITY, 4)
                    if pair[0:2] == pair[2:4] and pair != bytes(4):
                        write(agent, frame, P2_VITALITY, bytes(4), "player 2 vitality")
                    mine = agent.bus_read(P1_VITALITY, 4)
                    full = FULL.to_bytes(2, "big") * 2
                    if mine != full:
                        write(agent, frame, P1_VITALITY, full, "player 1 vitality")
                if done % 50 == 0:
                    agent.screenshot(out / f"f{frame:05d}.png")
                    (out / f"c{frame:05d}.bin").write_bytes(
                        agent.bus_read(CELLS, CELL_BYTES)
                    )
                agent.run()
                if (
                    args.save_at is not None
                    and frame >= args.save_at
                    and "checkpoint" not in result
                ):
                    agent.savestate(out / "checkpoint.mcs")
                    result["checkpoint"] = {
                        "requested": args.save_at,
                        "frame_after": int(agent.status()["frame"]),
                    }
        finally:
            process.terminate()
            process.wait(timeout=30)
            writes.close()
            polls.close()
    configure()
    if (out / "checkpoint.mcs").exists():
        result["checkpoint"]["sha256"] = sha256(out / "checkpoint.mcs")  # type: ignore[index]
    result |= {"frames": args.frames, "loads": loads, "posts": posts, "boxes": boxes}
    (out / "route.json").write_text(json.dumps(result, indent=1) + "\n")
    for item in posts:
        print(json.dumps(item))
    print(json.dumps({"loads": len(loads), "posts": len(posts)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
