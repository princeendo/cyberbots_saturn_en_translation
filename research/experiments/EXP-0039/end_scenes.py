"""EXP-0039: which ending scenes `END.BIN` posts for each pilot list, and their boxes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0039/end_scenes.py \\
        [--out data/text/ending_posts.json]

A static reading of ``END.BIN`` as loaded at ``0x06060000`` (D-034); it
prints and writes numbers only (``AGENTS.md`` rule 21).

- **Dispatchers.** ``0x06060446`` calls ``@(0x060775B4 + 4 x E)``, where E
  is the byte ``0x060CFF7E`` (the ending number). Each of the 9 dispatchers
  jumps through its own step table, indexed by the step word ``0x060CFEE8``;
  the table's address is the first ``mov.l`` literal in the dispatcher.
- **Posts.** Every call of the scene post ``0x06066852`` (R4 = a list
  number, R5 = the scene; the message is ``0x14000000`` + R4). R4 and R5 are
  resolved by walking back from the call over ``mov #imm`` and ``mov rM,rN``
  in straight-line code, following a ``bra`` into the call when the code
  just before it is a literal pool.
- **Scenes.** `END.BIN` holds a copy of `STG0AS.BIN`'s scene data, shifted
  by ``0x23ED0`` (the per-list scene-list table ``0x06086E54``, the box
  records ``0x060817B4``). For each posted (list, scene), the script's
  boxes and their lines (line n = string n of `END.BIN`'s dialogue table in
  ``data/text/script_census.json``) are read as ``EXP-0022/box_list.py``
  reads `STG0AS.BIN`'s, except that only the boxes a script opens are
  listed (a word below ``0x8000``), not those it closes. The copy is
  checked: every script of every list shows the same boxes in both files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path.cwd()))
from tools.sh2.disasm import decode

FILES = Path("local/extracted/saturn_jp")
CENSUS = Path("data/text/script_census.json")
BASE = 0x06060000
SHIFT = 0x23ED0  # STG0AS.BIN data address - END.BIN data address
DISPATCHERS = 0x060775B4
LISTS = 9
POST = 0x06066852
SCENE_LISTS = 0x06086E54
RECORDS = 0x060817B4
STG_SCENE_LISTS = 0x060AAD24
STG_RECORDS = 0x060A5684
CODE_END = 0x06077000


def u16(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - BASE : a - BASE + 2], "big")


def u32(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - BASE : a - BASE + 4], "big")


def literal(text: str) -> int | None:
    m = re.search(r"! 0x([0-9A-F]+)", text)
    return int(m.group(1), 16) if m else None


def resolve(data: bytes, call: int, branches: dict[int, list[int]]) -> dict[str, int]:
    """Constant values of R4 and R5 at the call (its delay slot included)."""
    want = {"r4": "R4", "r5": "R5"}
    found: dict[str, int] = {}
    alias: dict[str, str] = {}  # register now holding a wanted value -> name

    def apply(text: str) -> None:
        m = re.match(r"mov #(-?\d+),(r\d+)$", text)
        if m and m.group(2) in alias:
            found.setdefault(alias.pop(m.group(2)), int(m.group(1)) & 0xFF)
            return
        m = re.match(r"mov (r\d+),(r\d+)$", text)
        if m and m.group(2) in alias:
            alias[m.group(1)] = alias.pop(m.group(2))

    alias.update(want)
    apply(decode(data, BASE, call + 2)[1])  # delay slot runs first for r4/r5
    pc = call - 2
    for _ in range(60):
        if not alias:
            break
        text = decode(data, BASE, pc)[1]
        if text.startswith(("rts", "jmp", "bra", "jsr", "bsr")):
            break
        if text.startswith(".word") or pc in branches:
            # the code before is a literal pool or a join: follow one bra in
            src = branches.get(pc, [])
            if len(src) == 1:
                apply(decode(data, BASE, src[0] + 2)[1])
                pc = src[0] - 2
                continue
            break
        apply(text)
        pc -= 2
    return found


def scene_boxes(
    data: bytes, lists: int, records: int, p: int, scene: int, starts: list[int]
) -> list[int]:
    script = u32(data, u32(data, lists + 4 * p) + 4 * scene)
    later = [s for s in starts if s > script]
    end = later[0] if later else script + 0x80
    boxes: list[int] = []
    for a in range(script, end, 2):
        w = u16(data, a)
        if w == 0xE000:
            break
        if w >= 0x8000:  # closes (0x8000 | N), commands, 0xFFFF
            continue
        if w not in boxes:
            boxes.append(w)
    return boxes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    end = (FILES / "END.BIN").read_bytes()
    stg = (FILES / "STG0AS.BIN").read_bytes()
    census = json.loads(CENSUS.read_text())
    strings = next(f for f in census["files"] if f["file"] == "END.BIN")["blocks"][0]
    line_of = {BASE + row[0]: n for n, row in enumerate(strings["table"])}

    # Code, branches into each address, and the post calls.
    code = [(pc, decode(end, BASE, pc)[1]) for pc in range(BASE, CODE_END, 2)]
    branches: dict[int, list[int]] = {}
    for pc, text in code:
        m = re.match(r"bra 0x([0-9A-F]+)", text)
        if m:
            branches.setdefault(int(m.group(1), 16), []).append(pc)
    calls = []
    for pc, text in code:
        if literal(text) == POST:
            reg = text.split(",")[-1].split()[0]
            for k in range(pc, pc + 30, 2):
                t = decode(end, BASE, k)[1]
                if t in (f"jsr @{reg}", f"jmp @{reg}"):
                    calls.append(k)
                    break
    dispatchers = [u32(end, DISPATCHERS + 4 * k) for k in range(LISTS)]
    region = [*sorted(dispatchers), CODE_END]

    # Script starts (for script ends), from every list in both files.
    def starts(data: bytes, lists: int) -> list[int]:
        return sorted(
            {
                u32(data, u32(data, lists + 4 * p) + 4 * s)
                for p in range(11)
                for s in range(40)
                if BASE
                <= u32(data, u32(data, lists + 4 * p) + 4 * s)
                < BASE + len(data)
            }
        )

    end_starts, stg_starts = starts(end, SCENE_LISTS), starts(stg, STG_SCENE_LISTS)
    copy_checked = 0
    for p in range(LISTS):
        n = (u32(end, SCENE_LISTS + 4 * (p + 1)) - u32(end, SCENE_LISTS + 4 * p)) // 4
        for s in range(max(n, 0)):
            a = scene_boxes(end, SCENE_LISTS, RECORDS, p, s, end_starts)
            b = scene_boxes(stg, STG_SCENE_LISTS, STG_RECORDS, p, s, stg_starts)
            if a != b:
                raise SystemExit(f"list {p} scene {s}: END.BIN {a} != STG0AS.BIN {b}")
            copy_checked += 1

    def lines(box: int) -> list[int]:
        out, entry = [], u32(end, RECORDS + 4 * box) + 8
        while True:
            out.append(line_of.get(u32(end, entry), -1))
            if u16(end, entry + 4) != 0xFFFF or len(out) > 8:
                return out
            entry += 8

    tables = set()
    for disp in dispatchers:
        for pc in range(disp, disp + 12, 2):
            t = decode(end, BASE, pc)[1]
            if t.split("!")[0].strip().endswith(",r0") and literal(t):
                tables.add(literal(t))
                break
    report: list[dict[str, Any]] = []
    for p, disp in enumerate(dispatchers):
        table = 0  # the literal loaded into r0 (then mov.l @(r0,r3),r3)
        for pc in range(disp, disp + 12, 2):
            t = decode(end, BASE, pc)[1]
            if t.split("!")[0].strip().endswith(",r0") and literal(t):
                table = literal(t) or 0
                break
        steps: list[int] = []
        while BASE <= u32(end, table + 4 * len(steps)) < CODE_END and (
            table + 4 * len(steps) not in tables
            or not steps  # the next list's table starts here
        ):
            steps.append(u32(end, table + 4 * len(steps)))
        lo, hi = disp, next(r for r in region if r > disp)
        posts = []
        for c in calls:
            regs = resolve(end, c, branches)
            posts.append({"call": c, **regs})
        mine = [x for x in posts if lo <= x["call"] < hi]
        report.append(
            {
                "list": p,
                "dispatcher": f"0x{disp:08X}",
                "step_table": f"0x{table:08X}",
                "steps": len(steps),
                "posts": [
                    {
                        "call": f"0x{x['call']:08X}",
                        "step": max(
                            (k for k, a in enumerate(steps) if a <= x["call"]),
                            key=lambda k: steps[k],
                            default=None,
                        ),
                        "r4": x.get("R4"),
                        "scene": x.get("R5"),
                        "boxes": [
                            {"box": b, "lines": lines(b)}
                            for b in scene_boxes(
                                end,
                                SCENE_LISTS,
                                RECORDS,
                                x.get("R4", p),
                                x["R5"],
                                end_starts,
                            )
                        ]
                        if x.get("R5") is not None
                        else None,
                    }
                    for x in mine
                ],
            }
        )
    result = {
        "file": "END.BIN",
        "sha256": hashlib.sha256(end).hexdigest(),
        "scripts_checked_against_stg0as": copy_checked,
        "post_calls": len(calls),
        "lists": report,
    }
    for r in report:
        print(
            r["list"],
            r["dispatcher"],
            r["step_table"],
            r["steps"],
            [(x["r4"], x["scene"], x["step"]) for x in r["posts"]],
        )
    print("calls", len(calls), "scripts checked", copy_checked)
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
