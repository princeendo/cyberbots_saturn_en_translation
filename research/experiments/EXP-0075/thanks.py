"""EXP-0075: list 7's scenes in both arcade sets; does the Saturn have their lines?

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0075/thanks.py \\
        [--out research/experiments/EXP-0075/thanks.json]

1. **Scenes.** List 7's scene scripts are read as `EXP-0040`'s
   ``compare_scripts.py`` reads lists 0-5 (the interpreter's table, found in
   each set's disassembly; a scene's opened slots are its words below
   ``0x8000`` up to the ``0xE0xx`` end word), for scenes 0-6 (the byte
   table at ``0x631BC`` names no other) in `cybotsu` and `cybotsj`.
2. **Saturn.** Each line of the Japanese records of those slots (`cybotsj`,
   table ``0x0A30F6``) is decoded with the learned code map
   (``data/text/arcade_jp_map.json``, `REF-006`) and searched among every
   Saturn script line (``tools.text.dialogue.text_lines``: `STG0AS.BIN`,
   `END.BIN`, `VICTORY.BIN`): exact matches and the best ``difflib`` ratio.
3. **Every scene.** All 206 scenes of lists 0-7 (each list's scenes run to
   the next list's head; list 7's to the first script) are read the same
   way, and the slots 594-623 that none of them opens are listed.
4. **Records.** Each of the three tables' pointers for slots 600-623, as
   record addresses, to show which slots share a record.

Writes counts, slots and line indexes only, no text (`AGENTS.md` rule 21).
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.text.arcade_pairing import read_jp_record
from tools.text.dialogue import text_lines

_spec = importlib.util.spec_from_file_location(
    "compare_scripts", Path("research/experiments/EXP-0040/compare_scripts.py")
)
assert _spec and _spec.loader
compare_scripts = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(compare_scripts)

SETS = {
    "cybotsu": (
        Path("local/ref003/cybotsu-maincpu.bin"),
        Path("local/win002/mame/cybotsu-0-c0000.asm"),
    ),
    "cybotsj": (
        Path("local/ref003/cybotsj-maincpu.bin"),
        Path("local/end004/mame/dasm-j/cybotsj-0-c0000.asm"),
    ),
}
JP_TABLE = 0x0A30F6  # cybotsj's Japanese table (D-009, EXP-0040)
MAP = Path("data/text/arcade_jp_map.json")
LIST = 7
TABLES = {  # D-009, EXP-0040
    "cybotsu": {"ja": 0x0A310A, "es": 0x0AB956, "en": 0x0B33AA},
    "cybotsj": {"ja": 0x0A30F6, "es": 0x0AB942, "en": 0x0B3396},
}


def u16(image: bytes, a: int) -> int:
    return int.from_bytes(image[a : a + 2], "big")


def every_scene(image: bytes, scripts: int) -> dict[str, list[int]]:
    """Opened slots of every scene of lists 0-7, keyed "list/scene"."""
    heads = [scripts + u16(image, scripts + 2 * k) for k in range(8)]
    first = min(
        heads[k] + u16(image, heads[k] + 2 * s)
        for k in range(7)
        for s in range((heads[k + 1] - heads[k]) // 2)
    )
    out: dict[str, list[int]] = {}
    for k, head in enumerate(heads):
        end = heads[k + 1] if k < 7 else first
        for s in range((end - head) // 2):
            a = head + u16(image, head + 2 * s)
            opened: list[int] = []
            while (w := u16(image, a)) & 0xFF00 != 0xE000:
                if w < 0x8000 and w not in opened:
                    opened.append(w)
                a += 2
            out[f"{k}/{s}"] = opened
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--out", type=Path, default=Path("research/experiments/EXP-0075/thanks.json")
    )
    a = p.parse_args()
    report: dict[str, Any] = {"list": LIST, "sets": {}}
    slots: set[int] = set()
    images: dict[str, bytes] = {}
    for name, (image_path, asm_path) in SETS.items():
        image = image_path.read_bytes()
        images[name] = image
        got = compare_scripts.read_set(image, asm_path.read_text().splitlines())
        scenes = {s: got["opened"](LIST, s) for s in range(7)}
        slots.update(x for v in scenes.values() for x in v)
        every = every_scene(image, got["scripts"])
        opened_any = {x for v in every.values() for x in v}
        report["sets"][name] = {
            "image_sha256": hashlib.sha256(image).hexdigest(),
            "scripts_table": f"0x{got['scripts']:05X}",
            "scene_slots": scenes,
            "scenes_read": len(every),
            "slots_594_623_never_opened": [
                x for x in range(594, 624) if x not in opened_any
            ],
            "records_600_623": {
                lang: {
                    str(x): f"0x{int.from_bytes(image[t + 4 * x : t + 4 * x + 4]):06X}"
                    for x in range(600, 624)
                }
                for lang, t in TABLES[name].items()
            },
        }
    mapping = {
        int(k, 16): bytes.fromhex(v) for k, v in json.loads(MAP.read_text()).items()
    }
    saturn = text_lines()
    by_text: dict[bytes, list[int]] = {}
    for i, line in enumerate(saturn):
        by_text.setdefault(line, []).append(i)
    image = images["cybotsj"]
    lines_out = []
    for slot in sorted(slots):
        address = int.from_bytes(image[JP_TABLE + 4 * slot : JP_TABLE + 4 * slot + 4])
        for index, codes in enumerate(read_jp_record(image, address)):
            unknown = sum(c not in mapping for c in codes)
            text = b"".join(mapping.get(c, b"??") for c in codes)
            best = max(
                (
                    difflib.SequenceMatcher(None, text, s, autojunk=False).ratio(),
                    i,
                )
                for i, s in enumerate(saturn)
            )
            lines_out.append(
                {
                    "slot": slot,
                    "line": index,
                    "codes": len(codes),
                    "unmapped_codes": unknown,
                    "saturn_exact": by_text.get(text, []),
                    "best_ratio": round(best[0], 3),
                    "best_saturn_line": best[1],
                }
            )
    report["saturn_lines_searched"] = len(saturn)
    report["japanese_lines"] = lines_out
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
