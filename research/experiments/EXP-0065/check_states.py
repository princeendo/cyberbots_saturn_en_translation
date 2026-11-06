"""EXP-0065: the names switch from saved states (no key).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0065/check_states.py OUT \\
        [--build build/opt005/a] [--out-json PATH]

The patched build (D-007) in the silent home with the built image mounted.

1. **Boot** (state 384, before `CYBER.BIN` is loaded): run 1,400 frames; the
   game's directory table (``0x060DCB68``, 24-byte entries) must list
   ``ZNAMES1.BIN`` and ``ZNAMES2.BIN`` after ``WARNING4.PIX`` with the end flag
   (byte 11 bit 0) on the last; `CYBER.BIN`'s changed bytes and the
   `OPDEMO.BIN` overlay in RAM must equal the built files.
2. **Later states hold the old program**, so each later check first writes
   the built bytes the boot was shown to load: every `CYBER.BIN` change,
   the `STG0AS.BIN` literal (when that overlay is in RAM), the whole built
   `OPDEMO.BIN` (when it is), the three directory entries read in step 1 and
   the entry count (``0x060DBC58``: 329 after the boot, 327 in the states).
3. **Options** (state 27173): redraw (state 1); the cursor on EXTRA OPTIONS;
   the sub-menu (state 3 with the cursor on 8); the value set to JAPANESE;
   back to OPTION MODE. A screenshot at each step.
4. **Names** (state 2538, pilot select; state 6448, VS), each with the
   setting 0 and 1: the loads then run from the disc through the hooks, and
   ``EXP-0061/look.py`` classifies every name sprite as built (Latin) or
   katakana.

Writes ``OUT/states.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
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
TABLE, ENTRY = 0x060DCB68, 24
COUNT = 0x060DBC58  # the number of directory entries the loader stored
FLAG = 0x060D9295
LOOK = Path("research/experiments/EXP-0061/look.py")


def entries(agent: Any, first: int, count: int) -> list[dict[str, Any]]:
    raw = agent.bus_read(TABLE + ENTRY * first, ENTRY * count)
    out = []
    for k in range(count):
        e = raw[ENTRY * k : ENTRY * (k + 1)]
        out.append(
            {
                "index": first + k,
                "fad": int.from_bytes(e[0:4], "big"),
                "size": int.from_bytes(e[4:8], "big"),
                "flags": e[8:12].hex(),
                "name": e[12:24].split(b"\0")[0].decode("latin-1"),
                "raw": e.hex(),
            }
        )
    return out


def restart(agent: Any, state: Path) -> None:
    agent.run()
    agent.loadstate(state.resolve())
    agent.pause()


def shot(agent: Any, out: Path, name: str) -> str:
    path = (out / f"{name}.png").resolve()
    agent.screenshot(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(agent: Any, frames: int) -> None:
    agent.frames(frames)
    agent.wait_halted(120.0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--build", type=Path, default=Path("build/opt005/a"))
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    out: Path = args.out
    build: Path = args.build
    changes = json.loads((build / "names_switch_changes.json").read_text())["changes"]
    opdemo = (build / "OPDEMO.BIN").read_bytes()
    stg_literal = next(c for c in changes if c["file"] == "STG0AS.BIN")
    report: dict[str, Any] = {}

    session.launch(STATES / "f00000384.mcs", out, build / CUE)
    agent = session.agent_of(out)
    try:
        # 1. Boot from the disc.
        run(agent, 1400)
        boot = entries(agent, 325, 5)
        cy_ok = all(
            agent.bus_read(int(c["address"], 16), len(bytes.fromhex(c["new"])))
            == bytes.fromhex(c["new"])
            for c in changes
            if c["file"] == "CYBER.BIN"
        )
        ov = agent.bus_read(0x06060000, len(opdemo))
        report["boot"] = {
            "entries_325_329": boot,
            "cyber_changes_in_ram": cy_ok,
            "opdemo_in_ram_equal_chunks": sum(
                1
                for i in range(0, len(opdemo), 2048)
                if ov[i : i + 2048] == opdemo[i : i + 2048]
            ),
            "opdemo_chunks": (len(opdemo) + 2047) // 2048,
        }
        names = [e["name"] for e in boot]
        z = [e for e in boot if e["name"].startswith("ZNAMES")]
        report["boot"]["ok"] = (
            names[1:4] == ["WARNING4.PIX", "ZNAMES1.BIN", "ZNAMES2.BIN"]
            and int(z[-1]["flags"][-2:], 16) & 1 == 1
            and int(boot[1]["flags"][-2:], 16) & 1 == 0
            and cy_ok
        )
        table_bytes = bytes.fromhex("".join(e["raw"] for e in boot[1:4]))
        count = agent.bus_read(COUNT, 4)
        report["boot"]["directory_count"] = int.from_bytes(count, "big")

        def inject(overlay: str | None) -> None:
            for c in changes:
                if c["file"] == "CYBER.BIN":
                    agent.bus_write(int(c["address"], 16), bytes.fromhex(c["new"]))
            agent.bus_write(TABLE + ENTRY * 326, table_bytes)
            agent.bus_write(COUNT, count)
            if overlay == "OPDEMO.BIN":
                agent.bus_write(0x06060000, opdemo)
            if overlay == "STG0AS.BIN":
                agent.bus_write(
                    int(stg_literal["address"], 16), bytes.fromhex(stg_literal["new"])
                )

        # 3. Options.
        restart(agent, STATES / "f00027173.mcs")
        inject("OPDEMO.BIN")
        steps = {}
        agent.bus_write(0x060CFEE0, (1).to_bytes(2, "big"))
        run(agent, 90)
        steps["main"] = shot(agent, out, "opt-main")
        agent.bus_write(0x0606BE8C, (8).to_bytes(4, "big"))
        agent.bus_write(0x060CFEE0, (1).to_bytes(2, "big"))
        run(agent, 90)
        steps["main_cursor8"] = shot(agent, out, "opt-main-cursor8")
        agent.bus_write(0x060CFEE4, (0).to_bytes(2, "big"))
        agent.bus_write(0x060CFEE0, (3).to_bytes(2, "big"))
        run(agent, 150)
        steps["sub_english"] = shot(agent, out, "opt-sub-english")
        steps["sub_state"] = (
            agent.bus_read(0x060CFEE0, 2).hex()
            + "/"
            + agent.bus_read(0x060CFEE4, 2).hex()
        )
        agent.bus_write(FLAG, b"\x01")
        run(agent, 20)
        steps["sub_japanese"] = shot(agent, out, "opt-sub-japanese")
        agent.bus_write(0x060CFEE4, (0).to_bytes(2, "big"))
        agent.bus_write(0x060CFEE0, (1).to_bytes(2, "big"))
        run(agent, 120)
        steps["back_main"] = shot(agent, out, "opt-back-main")
        steps["flag_after"] = agent.bus_read(FLAG, 1).hex()
        report["options"] = steps

        # 4. Names on the pilot select and VS screens.
        looks: dict[str, Any] = {}
        for label, state, overlay, frames in (
            # At 2538 STG0A.BIN is still arriving at 0x06060000: no overlay write.
            ("select", "f00002538.mcs", None, 480),
            ("vs", "f00006448.mcs", "STG0AS.BIN", 345),
        ):
            for value in (0, 1):
                restart(agent, STATES / state)
                inject(overlay)
                agent.bus_write(FLAG, bytes([value]))
                run(agent, frames)
                agent.run()
                name = f"{label}-{value}"
                subprocess.run(
                    [
                        "./invenv.sh",
                        "python",
                        str(LOOK),
                        str(out / "agent"),
                        str(out),
                        name,
                        "--build",
                        "build/loc005/a",
                    ],
                    check=True,
                )
                agent.pause()
                looks[name] = json.loads((out / f"{name}.json").read_text())["counts"]
        report["names"] = looks
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    print(json.dumps(report, indent=1))
    if args.out_json:
        args.out_json.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
