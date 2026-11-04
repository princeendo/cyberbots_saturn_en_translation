"""EXP-0032: catch the Saturn's win-quote choice, replay it, and force boxes.

Run from the repository root, while ``EXP-0019/drive.py launch`` runs in OUT
and a versus fight is under way (EXP-0031's menu route):

    ./invenv.sh python research/experiments/EXP-0032/saturn_quote.py catch OUT SECONDS
    ./invenv.sh python research/experiments/EXP-0032/saturn_quote.py replay OUT
    ./invenv.sh python research/experiments/EXP-0032/saturn_quote.py force OUT BOX...

A debug harness; it never ships. It sends no key presses (the user,
2026-11-03): the fight is won by holding the vitality pairs (D-025), as
``EXP-0031/watch.py --force`` does.

- ``catch``: logs CD Play Disc commands (``EXP-0031/loads.py``) every second
  and holds player 1's vitality at full and player 2's at 0. Once
  ``VICTORY.BIN`` has loaded it sets a halt-mode PC breakpoint at
  ``0x06060BCE``, the selector's ``and #7,r0`` right after the random call.
  At the halt it writes the registers to ``OUT/select.json`` (R0: the random
  value, R8: 16 x the winner's pilot) and a screenshot. The agent refuses a
  save state while halted, so it clears the breakpoint, resumes, and saves
  ``OUT/post.mcs`` at once: the selection has run and the quote's script
  task has started its first wait.
- ``replay``: loads ``OUT/post.mcs`` and runs 400 frames with a log-mode
  breakpoint on ``VICTORY.BIN``'s box routine ``0x060615C8`` (R6 is the box,
  ``mov r14,r6`` at ``0x06061396``) and a screenshot every 25 frames
  (``OUT/replay-NNNNN.png``). Adds the boxes to ``OUT/select.json``.
- ``force``: for each BOX, loads ``OUT/post.mcs``, writes BOX over the box
  word of the chosen scene's script (list 9, ``0x0607DA00``; the scene is
  the quote table's entry R0 & 7 of row R8) while the task waits, and runs
  250 frames with the same log and screenshots ``OUT/forceBOX-NNNNN.png``.
  Writes ``OUT/force.json``.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0019"))
sys.path.insert(0, str(Path.cwd() / "research/experiments/EXP-0031"))
from drive import agent_for  # type: ignore[import-not-found]
from loads import CR1, CR2, LISTING, decode  # type: ignore[import-not-found]

from tools.mednafen.agent import Agent

P1_VITALITY, P2_VITALITY = 0x060D0024, 0x060D0318
FULL = 152
SELECT = 0x06060BCE  # and #7,r0 after the random call (VICTORY.BIN)
SHOW_BOX = 0x060615C8  # VICTORY.BIN box routine; R6 is the box
TABLE = 0x0606FAA0  # 9 pilots x 8 (scene, byte)
QUOTE_SCRIPTS = 0x0607DA00  # list 9's script pointers
VICTORY = Path("local/extracted/saturn_jp/VICTORY.BIN")
BASE = 0x06060000
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")


def boxes_shown(agent: Agent, out: Path, prefix: str, frames: int) -> list[list[int]]:
    """Run FRAMES frames from a paused or running state; (frame, box) shown."""
    agent.clear_events()
    agent.bpmode("log")
    agent.breakpoints("pc", [f"{SHOW_BOX:08X}"])
    if agent.halted():
        agent.run()
    for _ in range(0, frames, 25):
        agent.frames(25)
        status = agent.wait_halted(60.0)
        agent.screenshot(out / f"{prefix}-{int(status['frame']):05d}.png")
        agent.run()
    found = []
    for line in agent.events():
        e = dict(FIELD.findall(line))
        if int(e.get("PC", "0"), 16) == SHOW_BOX:
            found.append([int(e["frame"]), int(e["R6"], 16) & 0xFFFF])
    agent.breakpoints("pc")
    agent.clear_events()
    return found


def catch(out: Path, seconds: float) -> int:
    files = json.loads(LISTING.read_text())["files"]
    agent = agent_for(out)
    agent.clear_events()
    agent.bpmode("log")
    agent.breakpoints("pc", [f"{a:08X}" for a in (CR1, CR2)])
    loads: list[dict[str, object]] = []
    armed = False
    start = time.time()
    while time.time() - start < seconds:
        if not armed:
            found, _ = decode(agent.events(), files)
            agent.clear_events()
            loads += found
            for item in found:
                print(json.dumps(item), flush=True)
            if any(str(i.get("file", "")).startswith("VICTORY.BIN") for i in found):
                agent.breakpoints("pc")
                agent.bpmode("halt")
                agent.breakpoints("pc", [f"{SELECT:08X}"])
                armed = True
                print("armed", flush=True)
            else:
                agent.bus_write(P1_VITALITY, FULL.to_bytes(2, "big") * 2)
                vit = agent.bus_read(P2_VITALITY, 4)
                if vit[0:2] == vit[2:4]:
                    agent.bus_write(P2_VITALITY, bytes(4))
        elif agent.halted():
            regs = agent.regs()
            record = {
                "frame": int(agent.status()["frame"]),
                "regs": regs,
                "loads": loads,
            }
            agent.screenshot(out / "select.png")
            (out / "select.json").write_text(json.dumps(record, indent=1) + "\n")
            agent.breakpoints("pc")
            agent.run()
            agent.savestate(out / "post.mcs")
            summary = {
                "halted": record["frame"],
                "R0": regs.get("R0"),
                "R8": regs.get("R8"),
            }
            print(json.dumps(summary))
            return 0
        time.sleep(1.0)
    agent.breakpoints("pc")
    raise SystemExit("did not reach the selector")


def replay(out: Path) -> int:
    agent = agent_for(out)
    agent.loadstate(out / "post.mcs")
    shown = boxes_shown(agent, out, "replay", 400)
    record = json.loads((out / "select.json").read_text())
    record["replay_boxes"] = shown
    (out / "select.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(shown))
    return 0


def force(out: Path, boxes: list[int]) -> int:
    agent = agent_for(out)
    regs = json.loads((out / "select.json").read_text())["regs"]
    image = VICTORY.read_bytes()
    scene = image[TABLE - BASE + regs["R8"] + 2 * (regs["R0"] & 7)]
    script = int.from_bytes(image[QUOTE_SCRIPTS - BASE + 4 * scene :][:4], "big")
    word = script
    while int.from_bytes(image[word - BASE : word - BASE + 2], "big") >= 0x8000:
        word += 2
    results = []
    for box in boxes:
        agent.loadstate(out / "post.mcs")
        agent.pause()
        before = agent.bus_read(word, 2).hex()
        agent.bus_write(word, box.to_bytes(2, "big"))
        shown = boxes_shown(agent, out, f"force{box}", 250)
        results.append(
            {
                "scene": scene,
                "word": f"0x{word:08X}",
                "before": before,
                "box": box,
                "shown": shown,
            }
        )
        print(json.dumps(results[-1]), flush=True)
    (out / "force.json").write_text(json.dumps(results, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    command, out_dir, *rest = sys.argv[1:]
    if command == "catch":
        raise SystemExit(catch(Path(out_dir), float(rest[0])))
    if command == "replay":
        raise SystemExit(replay(Path(out_dir)))
    if command == "force":
        raise SystemExit(force(Path(out_dir), [int(x) for x in rest]))
    raise SystemExit(f"unknown command {command}")
