"""EXP-0070: one controlled VRAM or RAM change at the city stage's signs.

    ./invenv.sh python research/experiments/EXP-0070/probe.py OUT \\
        [--state local/ui002/s1/city.mcs] [--cue CUE] [--frames 120] \\
        [--fill SPACE:OFFSET:LENGTH:BYTE ...] [--dump SPACE:OFFSET:LENGTH ...] \\
        [--variant NAME ...]

The patched build (D-007), silent home, no keys. For each variant (each
``--fill`` is one variant unless ``--together``; the first variant is always
the control), the checkpoint is loaded and halted in one command exchange (so every
variant starts on the same frame), the fill is written, FRAMES frames
run, a screenshot is taken and each ``--dump`` region is read. Writes
``OUT/probe.json`` (each variant's fills, the bytes they replaced (SHA-256),
its shot's SHA-256 and the pixel box where it differs from the control).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import struct
import sys
import time
import zlib
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)


def pixels(path: Path) -> tuple[int, int, list[bytes]]:
    """RGB rows of a PNG (8-bit RGB or RGBA, any filter)."""
    data = path.read_bytes()
    i, idat = 8, b""
    width = height = colour = 0
    while i < len(data):
        n = struct.unpack(">I", data[i : i + 4])[0]
        kind = data[i + 4 : i + 8]
        if kind == b"IHDR":
            width, height, _, colour = struct.unpack(">IIBB", data[i + 8 : i + 18])
        if kind == b"IDAT":
            idat += data[i + 8 : i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(idat)
    bpp = {2: 3, 6: 4}[colour]
    stride = width * bpp
    rows, prev, p = [], bytearray(stride), 0
    for _ in range(height):
        filt, line = raw[p], bytearray(raw[p + 1 : p + 1 + stride])
        p += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b, c = prev[x], (prev[x - bpp] if x >= bpp else 0)
            if filt == 1:
                line[x] = (line[x] + a) & 255
            elif filt == 2:
                line[x] = (line[x] + b) & 255
            elif filt == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif filt == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pred) & 255
        rows.append(bytes(b for k, b in enumerate(line) if k % bpp < 3))
        prev = line
    return width, height, rows


def differ(a: Path, b: Path) -> dict[str, object]:
    w, h, ra = pixels(a)
    _, _, rb = pixels(b)
    pts = [
        (x, y)
        for y in range(h)
        for x in range(w)
        if ra[y][3 * x : 3 * x + 3] != rb[y][3 * x : 3 * x + 3]
    ]
    if not pts:
        return {"pixels": 0}
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return {"pixels": len(pts), "box": [min(xs), max(xs), min(ys), max(ys)]}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--state", type=Path, default=Path("local/ui002/s1/city.mcs"))
    p.add_argument("--cue", type=Path, default=session.UNTOUCHED)
    p.add_argument("--frames", type=int, default=120)
    p.add_argument("--fill", action="append", default=[])
    p.add_argument("--together", action="store_true", help="all fills in one variant")
    p.add_argument("--dump", action="append", default=[])
    a = p.parse_args()
    out: Path = a.out
    fills = [f.split(":") for f in a.fill]
    groups = [[f] for f in fills] if not a.together else ([fills] if fills else [])
    variants = [[], *groups]
    session.launch(a.state, out, a.cue)
    agent = session.agent_of(out)
    rows: list[dict[str, Any]] = []
    try:
        for n, group in enumerate(variants):
            agent.run()
            # one exchange: the state loads and the emulator halts in the same
            # poll, so every variant starts on the same frame
            agent.command(f"loadstate {a.state.resolve()}", "pause")
            agent.wait_halted(30.0)
            done = []
            for space, offset, length, byte in group:
                o, ln = int(offset, 16), int(length, 16)
                before = agent.read(space, o, ln)
                agent.write(space, o, bytes([int(byte, 16)]) * ln)
                done.append(
                    {
                        "space": space,
                        "offset": f"0x{o:05X}",
                        "length": ln,
                        "byte": byte,
                        "before_sha256": hashlib.sha256(before).hexdigest(),
                    }
                )
            agent.frames(a.frames)
            agent.wait_halted(120.0)
            shot = (out / f"v{n:02d}.png").resolve()
            agent.screenshot(shot)
            dumps = []
            for d in a.dump:
                space, offset, length = d.split(":")
                data = agent.read(space, int(offset, 16), int(length, 16))
                path = out / f"v{n:02d}_{space}_{offset}.bin"
                path.write_bytes(data)
                dumps.append(
                    {"file": path.name, "sha256": hashlib.sha256(data).hexdigest()}
                )
            rows.append(
                {
                    "variant": n,
                    "fills": done,
                    "shot_sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                    "dumps": dumps,
                }
            )
            print(n, done and done[0]["offset"], flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    for row in rows[1:]:
        row["differs_from_control"] = differ(
            out / "v00.png", out / f"v{row['variant']:02d}.png"
        )
    result = {
        "state": str(a.state),
        "state_sha256": hashlib.sha256(a.state.read_bytes()).hexdigest(),
        "cue": str(a.cue),
        "frames": a.frames,
        "variants": rows,
    }
    (out / "probe.json").write_text(json.dumps(result, indent=1) + "\n")
    for row in rows[1:]:
        print(
            row["variant"],
            row["fills"][0]["offset"] if row["fills"] else "",
            row["differs_from_control"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
