"""EXP-0082: every built win-quote box drawn by the game, from a saved state.

Run from the repository root (no key, no cold boot):

    ./invenv.sh python research/experiments/EXP-0082/check_quotes.py OUT \\
        --build build/sp017/a [--state local/win002/saturn/post.mcs] BOX...

``EXP-0032/saturn_quote.py force`` on a built image without a new cold
boot: the state (`WIN-002`, the untouched image just after `VICTORY.BIN`'s
selector ran) holds the untouched `VICTORY.BIN` in RAM and the untouched
font in VDP2 VRAM, so for each BOX the state is loaded and halted in one
agent exchange (`EXP-0070`), then:

- every `VICTORY.BIN` range of the build's ``changes.json`` (table codes,
  rows, box records) is written to its RAM copy (``0x06060000`` + offset),
  and the build's `KANJI.BIN` to VDP2 VRAM ``0x40000`` (as
  ``EXP-0072/check_captions.py``);
- BOX is written over the box word of the chosen scene's script, as
  ``saturn_quote.py force`` (the scene from ``select.json`` next to the
  state);
- a screenshot after ``--shot-at`` (100) frames, while the quote shows; after
  250 frames, the 60 glyph cells (WRAM-H ``0x060FE200``). The box passes
  when its predicted cells (the build's ``prediction.json``) are the
  leading cells.

Writes ``OUT/check.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
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

BASE = 0x06060000
TABLE = 0x0606FAA0  # VICTORY.BIN quote table (D-030)
QUOTE_SCRIPTS = 0x0607DA00  # list 9's script pointers
CELLS = 0x060FE200
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("boxes", type=int, nargs="+")
    p.add_argument("--build", type=Path, required=True)
    p.add_argument("--state", type=Path, default=Path("local/win002/saturn/post.mcs"))
    p.add_argument("--frames", type=int, default=250)
    p.add_argument("--shot-at", type=int, default=100)
    a = p.parse_args()
    out: Path = a.out
    build: Path = a.build
    vic = (build / "VICTORY.BIN").read_bytes()
    ranges = [
        r
        for r in json.loads((build / "changes.json").read_text())["ranges"]
        if r["file"] == "VICTORY.BIN"
    ]
    font = (build / "KANJI.BIN").read_bytes()
    pred = {
        q["box"]: q["cells"]
        for q in json.loads((build / "prediction.json").read_text())
    }
    regs = json.loads((a.state.parent / "select.json").read_text())["regs"]
    scene = vic[TABLE - BASE + regs["R8"] + 2 * (regs["R0"] & 7)]
    script = int.from_bytes(vic[QUOTE_SCRIPTS - BASE + 4 * scene :][:4], "big")
    word = script
    while int.from_bytes(vic[word - BASE : word - BASE + 2], "big") >= 0x8000:
        word += 2
    session.launch(a.state, out, build / CUE)
    agent = session.agent_of(out)
    results: list[dict[str, Any]] = []
    try:
        for box in a.boxes:
            agent.run()
            agent.command(f"loadstate {a.state.resolve()}", "pause")
            agent.wait_halted(30.0)
            for r in ranges:
                agent.bus_write(BASE + r["start"], vic[r["start"] : r["end"]])
            agent.write("vdp2vram", 0x40000, font)
            agent.bus_write(word, box.to_bytes(2, "big"))
            agent.frames(a.shot_at)
            agent.wait_halted(120.0)
            shot = (out / f"quote-{box}.png").resolve()
            agent.screenshot(shot)
            agent.frames(a.frames - a.shot_at)
            agent.wait_halted(120.0)
            data = agent.bus_read(CELLS, 60 * 128)
            have = [
                hashlib.sha256(data[k * 128 : (k + 1) * 128]).hexdigest()
                for k in range(60)
            ]
            want = pred.get(box, [])
            matched = 0
            while matched < len(want) and have[matched] == want[matched]:
                matched += 1
            results.append(
                {
                    "box": box,
                    "predicted": len(want),
                    "matched": matched,
                    "ok": bool(want) and matched == len(want),
                    "shot_sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                }
            )
            print(json.dumps(results[-1]), flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    report = {
        "state": str(a.state),
        "scene": scene,
        "word": f"0x{word:08X}",
        "boxes": len(results),
        "passed": sum(r["ok"] for r in results),
        "results": results,
    }
    (out / "check.json").write_text(json.dumps(report, indent=1) + "\n")
    print(report["passed"], "of", report["boxes"])
    return 0 if report["passed"] == report["boxes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
