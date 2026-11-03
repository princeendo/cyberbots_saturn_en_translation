"""EXP-0021: write test text over the M1 box in live WRAM-H, with a control.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0021/write_text.py OUT TEST [STEPS]

``TEST`` names an entry of ``TESTS`` below, or ``control`` (no write). Based
on ``research/experiments/EXP-0017/ram_write.py``. Loads checkpoint A (box
open, empty) in the patched build's silent home and pauses. For each
``(address, bytes)`` of the test it reads the original bytes, writes the test
bytes and reads them back. Then it runs STEPS (default 12) x 25 frames, with
a screenshot after each (``step01.png`` ...). ``result.json`` records every
address, original, written and read-back bytes, and the frames. Mednafen is
closed afterwards.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure

BINARY = Path("vendor/mednafen/build-agent/src/mednafen")
IMAGE = Path(
    "local/disc_images/cyberbots_saturn_jp_2m/"
    "Cyberbots - Fullmetal Madness (Japan) (2M).cue"
)
STATE = Path("local/checkpoints/m1/a-box-open.mcs")
LINE4 = 0x0606F09C  # Saturn line 4, 26 bytes + NUL (D-015)
LINE5 = 0x0606F0B8  # Saturn line 5, 24 bytes + NUL
# The M1 box record: x, y, attribute, then 8-byte entries (line, word): FFFF
# continues with the next entry, 0 ends the box (EXP-0021).
RECORD = 0x0609D184


def sjis(text: str) -> bytes:
    return text.encode("shift_jis")


def fw(text: str) -> bytes:
    """Shift-JIS of ``text`` with ASCII letters and digits made full-width."""
    return sjis(
        "".join(
            chr(ord(c) + 0xFEE0) if c.isascii() and c.isalnum() else c for c in text
        )
    )


TESTS: dict[str, list[tuple[int, bytes]]] = {
    # Full-width capitals on line 4 and digits on line 5, same lengths.
    "capitals": [(LINE4, fw("ABCDEFGHIJKLM")), (LINE5, fw("0123456789NO"))],
    # Codes not in the table: the pair "AB", full-width "a"; then the
    # table's pair glyphs "Dr" and "!?", then 9 hiragana. 26 bytes.
    "unknown": [(LINE4, b"AB" + fw("a") + b"Dr!?" + sjis("\u3042" * 9))],
    # 20 full-width cells and a NUL: runs over line 4's NUL into line 5.
    "long": [(LINE4, fw("ABCDEFGHIJKLMNOPQRST") + b"\x00")],
    # Line breaks inside line 4: AA / BB / CC / DD / EEF, 26 bytes.
    "breaks": [(LINE4, fw("AA\nBB\nCC\nDD\nEEF"))],
    # Five rows: line 5's entry continues (FFFF) to three more entries
    # (lines 4, 5, 4) written over the padding and the next record's header.
    "rows": [
        (
            RECORD + 20,
            bytes.fromhex("ffff0000")
            + LINE4.to_bytes(4, "big")
            + bytes.fromhex("ffff0000")
            + LINE5.to_bytes(4, "big")
            + bytes.fromhex("ffff0000")
            + LINE4.to_bytes(4, "big")
            + bytes(4),
        )
    ],
}


def connect(agent: Agent, timeout: float = 30.0) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            agent.status()
            return
        except AgentError:
            if time.monotonic() > deadline:
                raise
            time.sleep(0.5)


def main(out: Path, test: str, steps: int) -> int:
    writes = [] if test == "control" else TESTS[test]
    out.mkdir(parents=True, exist_ok=False)
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    result: dict[str, object] = {"state": str(STATE), "test": test, "writes": []}
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
        )
        try:
            agent = Agent(agent_dir, timeout=20.0)
            connect(agent)
            time.sleep(3)  # let the boot settle before replacing the machine state
            if agent.halted():
                agent.run()
            agent.loadstate(STATE.resolve())
            agent.pause()
            result["paused_frame"] = int(agent.status()["frame"])
            for address, data in writes:
                original = agent.bus_read(address, len(data))
                agent.bus_write(address, data)
                result["writes"].append(  # type: ignore[attr-defined]
                    {
                        "address": f"0x{address:08X}",
                        "original": original.hex(),
                        "written": data.hex(),
                        "readback": agent.bus_read(address, len(data)).hex(),
                    }
                )
            agent.run()
            frames = []
            for step in range(1, steps + 1):
                agent.frames(25)
                frames.append(int(agent.wait_halted(30.0)["frame"]))
                agent.screenshot(out / f"step{step:02d}.png")
                agent.run()
            result["step_frames"] = frames
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()
    (out / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "writes"}))
    return 0


if __name__ == "__main__":
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2], steps))
