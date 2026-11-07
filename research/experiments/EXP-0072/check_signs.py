"""EXP-0072: the SIGNS setting from saved states (no key, no cold boot).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0072/check_signs.py OUT \\
        [--build build/ui006/b]

The patched build (D-007) in the silent home with the built image mounted.
Each state is loaded and halted in one agent exchange (`EXP-0070`).

1. **Boot** (state 384): run 1,400 frames; the game's directory table
   (``0x060DCB68``, 24-byte entries) must list ``ZNAMES1.BIN``,
   ``ZNAMES2.BIN``, ``ZSIGNS1.BIN``, ``ZSIGNS2.BIN`` after ``WARNING4.PIX``,
   the end flag (byte 11 bit 0) on the last only; `CYBER.BIN`'s changes in
   RAM.
2. **Later states hold the old program and directory**: each check first
   writes every `CYBER.BIN` change, the directory entries read in step 1
   and the count (``0x060DBC58``), and, in OPTION MODE, the built
   `OPDEMO.BIN` (as `EXP-0065`).
3. **Menu** (state 27173): the sub-menu opened by state writes (as
   `EXP-0065`), then each cursor row and value combination written to RAM
   and redrawn (substate 1); the bytes and a screenshot of each. (Pad
   presses cannot be injected: the CPU reads the pad words through its
   cache, so agent writes are not seen. The input logic is checked by
   ``check_menu_logic.py``; real presses come in `UI-007`.)
4. **Signs** (state 25772, the attract before the city demo): ``SIGNS`` = 0,
   1, 2; run 5,530 frames (the signs on screen, `EXP-0070`); VDP2 VRAM
   ``0x28D00``-``0x3867F`` must equal the built blank file's slice, the
   English slice and the Japanese slice; a log-mode breakpoint counts hook
   S and its load (``S_load``); a screenshot.
5. **Another stage** (state 6448, a VS screen, then the fight's load):
   ``SIGNS`` = 1; hook S must run and not load (its stage's tile file is not
   ``ST00_FNT.BIN``).

Writes ``OUT/signs.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)

STATES = Path("local/ref005/session/states")
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
TABLE, ENTRY, COUNT = 0x060DCB68, 24, 0x060DBC58
FLAG, FLAG2, ROW = 0x060D9295, 0x060D9296, 0x060E0EA0
STATE_WORD, SUB_WORD, CURSOR = 0x060CFEE0, 0x060CFEE4, 0x0606BE8C
SLICE = (0x28D00, 0x38680)
FIELD = re.compile(r"PC=([0-9A-Fa-f]+)")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--build", type=Path, default=Path("build/ui006/b"))
    a = p.parse_args()
    out: Path = a.out
    build: Path = a.build
    sw = json.loads((build / "names_switch_changes.json").read_text())
    labels = {k: int(v, 16) for k, v in sw["labels"].items()}
    cyber = [c for c in sw["changes"] if c["file"] == "CYBER.BIN"]
    opdemo = (build / "OPDEMO.BIN").read_bytes()
    blank = (build / "ST00_FNT.BIN").read_bytes()
    zs1, zs2 = (
        (build / "ZSIGNS1.BIN").read_bytes(),
        (build / "ZSIGNS2.BIN").read_bytes(),
    )
    lo, hi = SLICE[0] - 0x19000, SLICE[1] - 0x19000
    expected = {0: blank[lo:hi], 1: zs1, 2: zs2}
    report: dict[str, Any] = {"build": str(build)}

    session.launch(STATES / "f00000384.mcs", out, build / CUE)
    agent = session.agent_of(out)

    def restart(state: Path) -> None:
        agent.run()
        agent.command(f"loadstate {state.resolve()}", "pause")
        agent.wait_halted(30.0)

    def run(frames: int) -> None:
        agent.frames(frames)
        agent.wait_halted(300.0)

    def shot(name: str) -> str:
        path = (out / f"{name}.png").resolve()
        agent.screenshot(path)
        return sha(path.read_bytes())

    try:
        # 1. Boot.
        run(1400)
        raw = agent.bus_read(TABLE + ENTRY * 326, ENTRY * 5)
        names = [
            raw[ENTRY * k + 12 : ENTRY * (k + 1)].split(b"\0")[0].decode()
            for k in range(5)
        ]
        ends = [raw[ENTRY * k + 11] & 1 for k in range(5)]
        count = agent.bus_read(COUNT, 4)
        cy_ok = all(
            agent.bus_read(int(c["address"], 16), len(bytes.fromhex(c["new"])))
            == bytes.fromhex(c["new"])
            for c in cyber
        )
        report["boot"] = {
            "entries_326_330": names,
            "end_flags": ends,
            "directory_count": int.from_bytes(count, "big"),
            "cyber_changes_in_ram": cy_ok,
            "ok": names
            == [
                "WARNING4.PIX",
                "ZNAMES1.BIN",
                "ZNAMES2.BIN",
                "ZSIGNS1.BIN",
                "ZSIGNS2.BIN",
            ]
            and ends == [0, 0, 0, 0, 1]
            and cy_ok,
        }

        def inject(overlay: bool = False) -> None:
            for c in cyber:
                agent.bus_write(int(c["address"], 16), bytes.fromhex(c["new"]))
            agent.bus_write(TABLE + ENTRY * 326, raw)
            agent.bus_write(COUNT, count)
            if overlay:
                agent.bus_write(0x06060000, opdemo)

        # 3. Menu.
        restart(STATES / "f00027173.mcs")
        inject(overlay=True)
        agent.bus_write(STATE_WORD, (1).to_bytes(2, "big"))
        run(90)
        agent.bus_write(CURSOR, (8).to_bytes(4, "big"))
        agent.bus_write(SUB_WORD, (0).to_bytes(2, "big"))
        agent.bus_write(STATE_WORD, (3).to_bytes(2, "big"))
        run(150)
        menu: list[dict[str, Any]] = []

        def read_state(step: str) -> None:
            menu.append(
                {
                    "step": step,
                    "row": agent.bus_read(ROW, 1)[0],
                    "names": agent.bus_read(FLAG, 1)[0],
                    "signs": agent.bus_read(FLAG2, 1)[0],
                    "state_word": int.from_bytes(agent.bus_read(STATE_WORD, 2), "big"),
                    "shot": shot(f"menu-{len(menu):02d}-{step}"),
                }
            )

        read_state("open")
        # Each combination set by RAM writes (pad presses cannot be injected:
        # the CPU reads the pad words through its cache; the input logic is
        # checked by check_menu_logic.py), then a redraw (substate 1).
        for row, names_value, signs_value in (
            (1, 0, 0),
            (1, 0, 1),
            (1, 0, 2),
            (0, 1, 2),
            (0, 0, 0),
        ):
            agent.bus_write(ROW, bytes([row]))
            agent.bus_write(FLAG, bytes([names_value]))
            agent.bus_write(FLAG2, bytes([signs_value]))
            agent.bus_write(SUB_WORD, (1).to_bytes(2, "big"))
            run(60)
            read_state(f"row{row}-names{names_value}-signs{signs_value}")
        report["menu"] = menu

        # 4. Signs in the attract demo.
        signs: dict[str, Any] = {}
        hooks = [f"{labels['hookS']:08X}", f"{labels['S_load']:08X}"]
        for value in (0, 1, 2):
            restart(STATES / "f00025772.mcs")
            inject()
            agent.bus_write(FLAG2, bytes([value]))
            agent.clear_events()
            agent.bpmode("log")
            agent.breakpoints("pc", hooks)
            run(5530)
            agent.breakpoints("pc", [])
            hits = [
                m.group(1).upper() for e in agent.events() if (m := FIELD.search(e))
            ]
            vram = agent.read("vdp2vram", SLICE[0], SLICE[1] - SLICE[0])
            signs[str(value)] = {
                "hook_runs": sum(h.endswith(hooks[0][-6:]) for h in hits),
                "loads": sum(h.endswith(hooks[1][-6:]) for h in hits),
                "slice_matches": {str(k): vram == v for k, v in expected.items()},
                "ok": vram == expected[value],
                "shot": shot(f"signs-{value}"),
            }
        report["signs"] = signs

        # 5. Another stage's load.
        restart(STATES / "f00006448.mcs")
        inject()
        agent.bus_write(FLAG2, b"\x01")
        agent.clear_events()
        agent.bpmode("log")
        agent.breakpoints("pc", hooks)
        run(1500)
        agent.breakpoints("pc", [])
        hits = [m.group(1).upper() for e in agent.events() if (m := FIELD.search(e))]
        report["other_stage"] = {
            "hook_runs": sum(h.endswith(hooks[0][-6:]) for h in hits),
            "loads": sum(h.endswith(hooks[1][-6:]) for h in hits),
            "stage_index_word": agent.bus_read(
                int.from_bytes(agent.bus_read(0x060D9198, 4), "big"), 4
            ).hex(),
            "shot": shot("other-stage"),
        }
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "signs.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
