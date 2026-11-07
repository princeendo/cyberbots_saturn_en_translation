"""EXP-0067: menu and versus screens from saved states (no key).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0067/screens.py OUT \
        [--build build/opt005/a]

The patched build (D-007) in the silent home with the current image
mounted. **KEY CONFIG** (session state 27173, the Options screen): the
current image's `OPDEMO.BIN` written to ``0x06060000`` (the state holds the
untouched one), the cursor set to 6 and the menu state to 3 (substate 0),
then screenshots at 60-frame steps. **Versus `VICTORY!`/`RESULT`**
(``local/win002/*/post.mcs``, `EXP-0032`): each state run 1,800 frames with
screenshots every 120 frames. Writes ``OUT/screens.json`` (names and
SHA-256).
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

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
CUE = "image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--build", type=Path, default=Path("build/opt005/a"))
    args = parser.parse_args()
    out: Path = args.out
    shots: dict[str, str] = {}
    session.launch(
        Path("local/ref005/session/states/f00027173.mcs"), out, args.build / CUE
    )
    agent = session.agent_of(out)

    def shot(name: str) -> None:
        path = (out / f"{name}.png").resolve()
        agent.screenshot(path)
        shots[name] = hashlib.sha256(path.read_bytes()).hexdigest()

    try:
        agent.bus_write(0x06060000, (args.build / "OPDEMO.BIN").read_bytes())
        agent.bus_write(0x0606BE8C, (6).to_bytes(4, "big"))
        agent.bus_write(0x060CFEE4, (0).to_bytes(2, "big"))
        agent.bus_write(0x060CFEE0, (3).to_bytes(2, "big"))
        for k in range(1, 6):
            agent.frames(60)
            agent.wait_halted(60.0)
            shot(f"keyconfig-{k * 60:04d}")
        for state in sorted(Path("local/win002").glob("*/post.mcs")):
            agent.run()
            agent.loadstate(state.resolve())
            agent.pause()
            for k in range(1, 16):
                agent.frames(120)
                agent.wait_halted(60.0)
                shot(f"versus-{state.parent.name}-{k * 120:04d}")
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    (out / "screens.json").write_text(json.dumps(shots, indent=1) + "\n")
    print(len(shots), "screenshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
