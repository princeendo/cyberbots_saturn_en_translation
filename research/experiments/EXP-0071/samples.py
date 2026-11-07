"""EXP-0071: rendered samples for the UI-005 gate (captions and city signs).

Run from the repository root (no key, no cold boot):

    ./invenv.sh python research/experiments/EXP-0071/samples.py OUT \\
        [--font local/layout001/font/arcade_font.json]

The patched build (D-007), silent home, untouched image. Each sample loads a
state with ``loadstate`` and ``pause`` in one agent exchange (`EXP-0070`),
writes its change to RAM or VRAM only, runs, and takes a screenshot:

- **Captions** (session state 6448, pilot 0 in both player blocks, stage 0
  (box 496) or 4 (box 500), 345 frames, as `EXP-0067` `captions.py`):
  ``jp`` (as is); ``none`` (the reader ``0x0606CAE8`` made to return at
  once: ``rts``, ``nop``); ``en-centre`` and ``en-left`` (a draft English
  caption drawn as pair glyphs (``tools.font.pairs``, the arcade's letters)
  into unused `KANJI.BIN` glyph slots 1100+ in VDP2 VRAM, and the box's line
  rewritten to their codes; centred with leading spaces, or not).
- **Signs** (``local/ui002/s2/signs.mcs``, 2 frames; also rendered offline
  from the layer as ``store-*.png``, the whole store front without the
  HUD): ``jp`` (as is);
  ``blank`` (each banner's text colours set to its base colour; on the
  slanted sale sign, colours 5, 10 and 11 within 4 rows of the text's
  fitted line; NBG2 blocks of `EXP-0070`
  ``signs.json``); ``en`` (blank, plus sample English lettering: the
  arcade's dialogue capitals stacked on the banners, `FIX.BIN`'s 8 x 8
  capitals along the sale sign's slope).

Samples only: nothing is built, and the English here is a draft for the
gate. Writes ``OUT/samples.json`` (each shot's SHA-256 and what changed).
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
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.font import kanji, pairs
from tools.memory.mcs_extract import encode_png, parse_state

_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)

FILES = Path("local/extracted/saturn_jp")
CAPTION_STATE = Path("local/ref005/session/states/f00006448.mcs")
SIGN_STATE = Path("local/ui002/s2/signs.mcs")
SIGN_BLOCKS = Path("local/ui002/s2/plane2.json")
ARCADE_FONT = Path("local/layout001/font/arcade_font.json")
BLOCK = 0x060CFFDC
READER = 0x0606CAE8
FIRST_GLYPH = 1100
CELLS = 13  # inside the banner (EXP-0069)
DRAFTS = {496: "Enter: Mystery Cyborg", 500: "Rogue VA: Save the Girl"}
STAGES = {496: 0, 500: 4}
# Signs: interior boxes (plane pixels, inclusive), text colours, base colour,
# and the sample lettering (vertical: one letter a row; horizontal: a line).
SIGNS: list[dict[str, Any]] = [
    {
        "name": "red banner",
        "box": (449, 461, 250, 329),
        "text": {6, 7, 8, 9, 0xB},
        "base": 0xA,
        "ink": 7,
        "word": "SALE",
        "vertical": True,
    },
    {
        "name": "white banner and small sign",
        "box": (478, 492, 240, 335),
        "text": {3, 4, 5, 6, 9, 0xA, 0xB},
        "base": 7,
        "ink": 9,
        "word": "BAZAAR",
        "vertical": True,
    },
    {
        "name": "sale sign",
        "box": (418, 492, 408, 426),
        "text": {0xA, 0xB},
        "base": 6,
        "ink": 0xA,
        "word": "BARGAIN SALE",
        "vertical": False,
    },
]


def line_of(stg: bytes, box: int) -> int:
    record = int(struct.unpack_from(">I", stg, 0x060A5684 + 4 * box - 0x06060000)[0])
    return int(struct.unpack_from(">I", stg, record + 8 - 0x06060000)[0])


def caption_writes(
    stg: bytes, font: dict[str, pairs.Glyph], box: int, centre: bool
) -> list[tuple[str, int, bytes]]:
    codes = kanji.read_code_table(stg)
    text = DRAFTS[box]
    if centre:
        text = " " * ((2 * CELLS - len(text)) // 2) + text
    cells = pairs.split_pairs(text)
    writes: list[tuple[str, int, bytes]] = []
    line = b""
    for n, pair in enumerate(cells):
        glyph = FIRST_GLYPH + n
        cell = pairs.render_pair(font, pair)
        for k, tile in enumerate(kanji.tiles(glyph)):
            half = 0 if k % 2 == 0 else 4
            rows = range(0, 8) if k < 2 else range(8, 16)
            data = b"".join(cell[r * 8 + half : r * 8 + half + 4] for r in rows)
            writes.append(("vdp2vram", 0x40000 + tile * 32, data))
        line += codes[glyph].to_bytes(2, "big")
    writes.append(("bus", line_of(stg, box), line + b"\0\0"))
    return writes


def sign_vram(blank_only: bool) -> tuple[bytearray, list[tuple[str, int, bytes]]]:
    vram = bytearray(parse_state(SIGN_STATE.read_bytes()).sections["VDP2"]["VRAM"])
    blocks = json.loads(SIGN_BLOCKS.read_text())["blocks"]
    fix = (FILES / "FIX.BIN").read_bytes()
    font = pairs.load_arcade_font(ARCADE_FONT)

    def at(x: int, y: int) -> tuple[int, bool]:
        char = int(blocks[f"{x // 16},{y // 16}"]["char_addr"], 16)
        sx, sy = x % 16, y % 16
        a = char + ((sy // 8) * 2 + sx // 8) * 32 + (sy % 8) * 4 + (sx % 8) // 2
        return a, sx % 2 == 0

    def get(x: int, y: int) -> int:
        a, high = at(x, y)
        b = vram[a ^ 1]  # the state keeps VRAM as little-endian words
        return b >> 4 if high else b & 15

    touched: set[int] = set()

    def put(x: int, y: int, v: int) -> None:
        a, high = at(x, y)
        b = vram[a ^ 1]
        vram[a ^ 1] = (v << 4 | b & 15) if high else (b & 0xF0 | v)
        touched.add(a & ~0x7F)

    for sign in SIGNS:
        x0, x1, y0, y1 = sign["box"]
        if sign["vertical"]:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    if get(x, y) in sign["text"]:
                        put(x, y, sign["base"])
        else:
            # slanted: per column, everything between the top and bottom
            # border lines (colour 5) becomes the base colour
            ink = [
                (x, y)
                for x in range(x0, x1 + 1)
                for y in range(y0, y1 + 1)
                if get(x, y) in sign["text"]
            ]
            n = len(ink)
            mx, my = sum(p[0] for p in ink) / n, sum(p[1] for p in ink) / n
            slope = sum((p[0] - mx) * (p[1] - my) for p in ink) / sum(
                (p[0] - mx) ** 2 for p in ink
            )
            sign["fit"] = (mx, my, slope)
            left, right = min(p[0] for p in ink) - 1, max(p[0] for p in ink) + 1
            for x in range(left, right + 1):
                centre = round(my + slope * (x - mx))
                for y in range(centre - 4, centre + 5):
                    if get(x, y) in sign["text"] | {5}:
                        put(x, y, sign["base"])
        if blank_only:
            continue
        word = sign["word"]
        for n_, ch in enumerate(word):
            if ch == " ":
                continue
            if sign["vertical"]:
                glyph = font[ch]
                ox = x0 + (x1 - x0 + 1 - 7) // 2
                oy = y0 + 2 + n_ * 14 - 2
                for gy, row in enumerate(glyph.rows):
                    for gx, v in enumerate(row):
                        if v and v != pairs.SHADOW:
                            put(ox + glyph.left + gx, oy + gy, sign["ink"])
            else:
                mx, my, slope = sign["fit"]
                ox = x0 + 1 + n_ * 6
                oy = round(my + slope * (ox + 3 - mx)) - 4
                tile = fix[32 * ord(ch) : 32 * ord(ch) + 32]
                for ty in range(8):
                    for tx in range(8):
                        b = tile[ty * 4 + tx // 2]
                        if (b >> 4 if tx % 2 == 0 else b & 15) == 5:
                            put(ox + tx, oy + ty, sign["ink"])
    out = []
    for block in sorted(touched):
        data = bytes(vram[(block + i) ^ 1] for i in range(0x80))
        out.append(("vdp2vram", block, data))
    return vram, out


def render_store(vram: bytes | bytearray, path: Path, scale: int = 3) -> None:
    """NBG2 plane pixels x 400-511, y 224-431 (the store), as `EXP-0070` nbg2.py."""
    vdp2 = parse_state(SIGN_STATE.read_bytes()).sections["VDP2"]
    cram = vdp2["CRAM"]
    blocks = json.loads(SIGN_BLOCKS.read_text())["blocks"]
    x0, x1, y0, y1 = 400, 512, 224, 432
    w, h = (x1 - x0) * scale, (y1 - y0) * scale
    img = bytearray(w * h * 3)
    for y in range(y0, y1):
        for x in range(x0, x1):
            blk = blocks[f"{x // 16},{y // 16}"]
            char, w0 = int(blk["char_addr"], 16), int(blk["w0"], 16)
            sx, sy = x % 16, y % 16
            a = char + ((sy // 8) * 2 + sx // 8) * 32 + (sy % 8) * 4 + (sx % 8) // 2
            b = vram[a ^ 1]
            i = b >> 4 if sx % 2 == 0 else b & 15
            c = int(struct.unpack_from("<H", cram, 2 * ((w0 & 0x7F) * 16 + i))[0])
            rgb = bytes(((c & 31) * 8, ((c >> 5) & 31) * 8, ((c >> 10) & 31) * 8))
            if i == 0:
                rgb = bytes((120, 160, 220))
            for dy in range(scale):
                for dx in range(scale):
                    o = (((y - y0) * scale + dy) * w + (x - x0) * scale + dx) * 3
                    img[o : o + 3] = rgb
    path.write_bytes(encode_png(w, h, bytes(img)))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument(
        "--font", type=Path, default=Path("local/layout001/font/arcade_font.json")
    )
    a = p.parse_args()
    out: Path = a.out
    stg = (FILES / "STG0AS.BIN").read_bytes()
    font = pairs.load_arcade_font(a.font)
    samples: list[tuple[str, Path, int, int | None, list[tuple[str, int, bytes]]]] = []
    for box in (496, 500):
        samples += [
            (f"caption-{box}-jp", CAPTION_STATE, 345, box, []),
            (
                f"caption-{box}-en-centre",
                CAPTION_STATE,
                345,
                box,
                caption_writes(stg, font, box, True),
            ),
        ]
    samples += [
        (
            "caption-496-en-left",
            CAPTION_STATE,
            345,
            496,
            caption_writes(stg, font, 496, False),
        ),
        (
            "caption-496-none",
            CAPTION_STATE,
            345,
            496,
            [("bus", READER, bytes.fromhex("000B0009"))],
        ),
        ("signs-jp", SIGN_STATE, 2, None, []),
        ("signs-blank", SIGN_STATE, 2, None, sign_vram(True)[1]),
        ("signs-en", SIGN_STATE, 2, None, sign_vram(False)[1]),
    ]

    session.launch(CAPTION_STATE, out, session.UNTOUCHED)
    agent = session.agent_of(out)
    report = []
    try:
        for name, state, frames, which, writes in samples:
            agent.run()
            agent.command(f"loadstate {state.resolve()}", "pause")
            agent.wait_halted(30.0)
            if which is not None:
                for base in (BLOCK, BLOCK + 0x2F4):
                    agent.bus_write(base + 0x2D2, bytes([0]))
                    agent.bus_write(base + 0x2E3, bytes([STAGES[which]]))
            for space, address, data in writes:
                if space == "bus":
                    agent.bus_write(address, data)
                else:
                    agent.write(space, address, data)
            agent.frames(frames)
            agent.wait_halted(120.0)
            shot = (out / f"{name}.png").resolve()
            agent.screenshot(shot)
            report.append(
                {
                    "sample": name,
                    "state": str(state),
                    "frames": frames,
                    "writes": [
                        {
                            "space": s,
                            "address": f"0x{ad:08X}",
                            "length": len(d),
                            "sha256": hashlib.sha256(d).hexdigest(),
                        }
                        for s, ad, d in writes
                    ],
                    "shot_sha256": hashlib.sha256(shot.read_bytes()).hexdigest(),
                }
            )
            print(name, flush=True)
    finally:
        os.kill(json.loads((out / "run.json").read_text())["pid"], 15)
        time.sleep(2)
    untouched = parse_state(SIGN_STATE.read_bytes()).sections["VDP2"]["VRAM"]
    render_store(untouched, out / "store-jp.png")
    render_store(sign_vram(True)[0], out / "store-blank.png")
    render_store(sign_vram(False)[0], out / "store-en.png")
    (out / "samples.json").write_text(
        json.dumps({"drafts": DRAFTS, "samples": report}, indent=1) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
