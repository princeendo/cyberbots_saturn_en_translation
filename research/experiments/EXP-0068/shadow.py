"""EXP-0068: does the type-2 decoder reproduce the cast roll's name images?

    ./invenv.sh python research/experiments/EXP-0068/shadow.py OUT \\
        [--state local/end010/cast-pre/s06450.mcs] [--shots 100,450,...]

Part 1 (Mednafen, untouched image, silent home, no keys): loads the pre-roll
state (`EXP-0044`), runs, and after each ``--shots`` frame count reads the
sprite shadow, WRAM-H ``0x060E0000``-``0x060FFFFF`` (D-035), to
``OUT/hNNNN.bin``.

Part 2 (offline): walks bank 16's frames ``0x1B6``-``0x1C9`` (D-040: header
at `KEND.BIN` + ``0xA704``, 6-byte parts, bit ``0x20`` = a `KEND_1.BIN`
record at 4 x (bit 0 << 16 | word 2)) in the state's own RAM, decodes every
record with ``tools.text.pattern_t2.decode`` (D-053) and searches each
result in every shadow dump. Writes ``OUT/shadow.json``: per record its
offset, frame, size, decoded SHA-256 and the shadow address (or none) where
the exact bytes were found.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.mednafen.agent import Agent, AgentError
from tools.mednafen.home import QUIET_HOME, configure
from tools.memory import mcs_extract
from tools.text import pattern_t2

_spec = importlib.util.spec_from_file_location(
    "exp0031_loads", Path("research/experiments/EXP-0031/loads.py")
)
assert _spec and _spec.loader
_loads = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_loads)
BINARY, IMAGE = _loads.BINARY, _loads.IMAGE
KEND_1 = Path("local/extracted/saturn_jp/KEND_1.BIN")
SHOTS = "100,450,600,750,900,1050,1200,1350,1500,1650,1800,1950,2100,2300,2500"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(state: Path, out: Path, shots: list[int]) -> None:
    configure()
    agent_dir = (out / "agent").resolve()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(QUIET_HOME.resolve()),
        "MEDNAFEN_AGENT_DIR": str(agent_dir),
    }
    with (out / "mednafen.log").open("wb") as log:
        process = subprocess.Popen(
            [str(BINARY), str(IMAGE)], env=env, stdout=log, stderr=subprocess.STDOUT
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
            agent.loadstate(state.resolve())
            agent.pause()
            agent.wait_halted(30.0)
            done = 0
            for n in shots:
                agent.frames(n - done)
                agent.wait_halted(60.0)
                done = n
                (out / f"h{n:04d}.bin").write_bytes(
                    agent.read("workramh", 0xE0000, 0x20000)
                )
        finally:
            process.terminate()
            process.wait(timeout=30)
    configure()


def records(state: Path, out: Path) -> dict[int, int]:
    mcs_extract.main(
        [
            str(state),
            "--out-dir",
            str(out / "state"),
            "--region",
            "wram_h",
            "--region",
            "wram_l",
            "--overwrite",
        ]
    )
    high = (out / "state" / "wram_h.bin").read_bytes()
    low = (out / "state" / "wram_l.bin").read_bytes()

    def word(a: int) -> int:
        a &= 0x07FFFFFF
        if a >= 0x06000000:
            return int(struct.unpack_from(">H", high, a - 0x06000000)[0])
        return int(struct.unpack_from(">H", low, a - 0x00200000)[0])

    def long(a: int) -> int:
        return int(struct.unpack_from(">I", high, a - 0x06000000)[0])

    header = 0x0606A704
    table, parts = long(header + 4), long(header + 8)
    found: dict[int, int] = {}
    for frame in range(0x1B6, 0x1CA):
        first, end = word(table + 2 * (frame - 1)), word(table + 2 * frame)
        for p in range(first, end if end > first else first + 4):
            a = parts + 6 * p
            w1, w2 = word(a + 2), word(a + 4)
            if w1 & 0x20:
                found.setdefault(4 * (((w1 & 1) << 16) | w2), frame)
    return found


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument(
        "--state", type=Path, default=Path("local/end010/cast-pre/s06450.mcs")
    )
    p.add_argument("--shots", default=SHOTS)
    p.add_argument("--offline", action="store_true", help="reuse OUT's dumps")
    a = p.parse_args()
    out: Path = a.out
    shots = sorted(int(x) for x in a.shots.split(","))
    if not a.offline:
        out.mkdir(parents=True, exist_ok=False)
        run(a.state, out, shots)
    dumps = {n: (out / f"h{n:04d}.bin").read_bytes() for n in shots}
    kend = KEND_1.read_bytes()
    report = []
    for offset, frame in sorted(records(a.state, out).items()):
        item: dict[str, object] = {
            "offset": f"0x{offset:05X}",
            "frame": f"0x{frame:03X}",
        }
        try:
            width, height = pattern_t2.size_of(kend[offset:])
            pixels = pattern_t2.decode(kend[offset:])
        except (pattern_t2.FormatError, IndexError) as error:
            item["error"] = str(error)
            report.append(item)
            continue
        item |= {"size": [width, height], "sha256": sha256(pixels)}
        for n, dump in dumps.items():
            at = dump.find(pixels)
            if at >= 0:
                item |= {"shadow": f"0x{0x060E0000 + at:08X}", "after": n}
                break
        report.append(item)
    summary = {
        "state": str(a.state),
        "state_sha256": sha256(a.state.read_bytes()),
        "kend_1_sha256": sha256(kend),
        "shots": shots,
        "dumps": {n: sha256(d) for n, d in dumps.items()},
        "records": report,
        "decoded": sum("sha256" in r for r in report),
        "matched": sum("shadow" in r for r in report),
    }
    (out / "shadow.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(summary["decoded"], "decoded,", summary["matched"], "found in the shadow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
