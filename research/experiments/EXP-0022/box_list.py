"""EXP-0022: list a pilot's story boxes from the game's own tables.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0022/box_list.py STG0AS.BIN \\
        [--pilot 0] [--out data/text/jin_boxes.json]

Reads, from ``STG0AS.BIN`` as loaded at ``0x06060000`` (D-017):

- the per-pilot scene lists at ``0x060AAD24`` (pilot byte at task + ``0x1E``);
- each scene's bytecode script: a word below ``0x8000`` shows that box, the
  same number with ``0x8000`` closes it; ``0xFFFF`` and words of ``0xC000`` or
  more are commands (``0xE000`` ends the scene);
- the box records through the table at ``0x060A5684``: an 8-byte header
  (``0``, x, y, attribute), then 8-byte entries (line pointer, word), where
  ``0xFFFF`` continues;
- the dialogue lines from ``0x0606F01C``, numbered in file order, 4-byte
  aligned and NUL-terminated (D-008).

Prints, and writes as JSON with ``--out``, each scene's boxes with their
record addresses and line numbers. It holds no text (``AGENTS.md`` rule 21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BASE = 0x06060000
PILOT_SCENES = 0x060AAD24
RECORDS = 0x060A5684
LINES = 0x0606F01C
LINES_BYTES = 50112


def main(path: Path, pilot: int, out: Path | None) -> int:
    data = path.read_bytes()

    def u16(a: int) -> int:
        return int.from_bytes(data[a - BASE : a - BASE + 2], "big")

    def u32(a: int) -> int:
        return int.from_bytes(data[a - BASE : a - BASE + 4], "big")

    lines: dict[int, int] = {}
    a = LINES
    while a < LINES + LINES_BYTES:
        if data[a - BASE] == 0:
            a += 4
            continue
        lines[a] = len(lines)
        end = data.index(b"\0", a - BASE) + BASE
        a = (end + 1 + 3) & ~3
    scene_list = u32(PILOT_SCENES + 4 * pilot)
    next_list = min(
        u32(PILOT_SCENES + 4 * k)
        for k in range(22)
        if u32(PILOT_SCENES + 4 * k) > scene_list
    )
    scripts = [u32(scene_list + 4 * k) for k in range((next_list - scene_list) // 4)]
    all_starts = sorted({u32(0x060AA840 + 4 * k) for k in range(335)})
    scenes: list[dict[str, object]] = []
    for number, script in enumerate(scripts):
        later = [s for s in all_starts if s > script]
        end = later[0] if later else script + 0x80
        boxes: list[int] = []
        for addr in range(script, end, 2):
            word = u16(addr)
            if word == 0xFFFF or word >= 0xC000:
                continue
            if (word & 0x7FFF) not in boxes:
                boxes.append(word & 0x7FFF)
        entries = []
        for box in boxes:
            record = u32(RECORDS + 4 * box)
            header = [u16(record + 2 * k) for k in range(4)]
            box_lines = []
            entry = record + 8
            while True:
                pointer, word = u32(entry), u16(entry + 4)
                box_lines.append(lines.get(pointer, -1))
                if word != 0xFFFF or len(box_lines) > 8:
                    break
                entry += 8
            entries.append(
                {
                    "box": box,
                    "record": f"0x{record:08X}",
                    "x": header[1],
                    "y": header[2],
                    "attribute": header[3],
                    "lines": box_lines,
                }
            )
        scenes.append({"scene": number, "script": f"0x{script:08X}", "boxes": entries})
    report = {
        "file": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "pilot": pilot,
        "scene_list": f"0x{scene_list:08X}",
        "scenes": scenes,
    }
    for s in scenes:
        boxes_out = s["boxes"]
        assert isinstance(boxes_out, list)
        print(s["scene"], s["script"], [(b["box"], b["lines"]) for b in boxes_out])
    if out:
        out.write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("--pilot", type=int, default=0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.file, args.pilot, args.out))
