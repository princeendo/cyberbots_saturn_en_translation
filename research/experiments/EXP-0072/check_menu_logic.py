"""EXP-0072: the EXTRA OPTIONS input logic, run on a small SH-2 interpreter.

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0072/check_menu_logic.py \\
        [--build build/ui006/b] [--out research/experiments/EXP-0072/menu_logic.json]

Pad presses cannot be injected into the emulator (the CPU reads the pad
words through its cache), so the built `CYBER.BIN`'s sub-menu handler (label
``extra``, substate 2) is executed here instruction by instruction, for every
cursor row (0, 1), ``NAMES`` (0, 1), ``SIGNS`` (0-2) and button (none, Up,
Down, Left, Right, A, C, Start, B): 108 cases. Calls (``bsr``/``jsr``) are
recorded and not entered (the draw, sound and fade routines); the run ends at
the handler's ``rts``. Each case is compared with the user's design
(``docs/localization_policy.md``, "UI Text and Art, Decided"; Up/Down move the
row; on NAMES, Right/Left/A/C toggle it; on SIGNS, Right/A/C step forward
and Left back, 0 -> 1 -> 2 -> 0; Start/B leave: state 1, substate 0).

Only the instructions the handler uses are implemented; any other stops the
run with an error. Writes ``--out``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BASE = 0x0600D000
FLAG, FLAG2, ROW = 0x060D9295, 0x060D9296, 0x060E0EA0
SUB, STATE, FADE, PAD1, PAD2 = (
    0x060CFEE4,
    0x060CFEE0,
    0x060CFEA0,
    0x060CC016,
    0x060CC026,
)
BUTTONS = {
    "none": 0,
    "Up": 0x1000,
    "Down": 0x2000,
    "Left": 0x4000,
    "Right": 0x8000,
    "A": 0x0400,
    "C": 0x0200,
    "Start": 0x0800,
    "B": 0x0100,
}


class Machine:
    def __init__(self, code: bytes, ram: dict[int, int]) -> None:
        self.code, self.ram = code, ram
        self.r = [0] * 16
        self.r[15] = 0x06008000
        self.t = 0
        self.pr = 0xDEAD0000
        self.calls: list[int] = []

    def fetch16(self, a: int) -> int:
        o = a - BASE
        return int.from_bytes(self.code[o : o + 2], "big")

    def fetch32(self, a: int) -> int:
        o = a - BASE
        return int.from_bytes(self.code[o : o + 4], "big")

    def rd(self, a: int, n: int) -> int:
        if BASE <= a < BASE + len(self.code):
            return int.from_bytes(self.code[a - BASE : a - BASE + n], "big")
        return int.from_bytes(bytes(self.ram.get(a + i, 0) for i in range(n)), "big")

    def wr(self, a: int, n: int, v: int) -> None:
        for i, b in enumerate((v & ((1 << (8 * n)) - 1)).to_bytes(n, "big")):
            self.ram[a + i] = b

    def run(self, pc: int, limit: int = 400) -> None:
        delayed: int | None = None
        for _ in range(limit):
            op = self.fetch16(pc)
            nxt = pc + 2
            target: int | None = None
            n, m, i8 = (op >> 8) & 15, (op >> 4) & 15, op & 0xFF
            s8 = i8 - 256 if i8 & 0x80 else i8
            r = self.r
            hi = op >> 12
            if op == 0x0009:
                pass
            elif op == 0x000B:  # rts
                target = self.pr
            elif op == 0x4F22:
                r[15] -= 4
                self.wr(r[15], 4, self.pr)
            elif op == 0x4F26:
                self.pr = self.rd(r[15], 4)
                r[15] += 4
            elif hi == 0xD:  # mov.l @(disp,PC),Rn
                r[n] = self.fetch32(((pc + 4) & ~3) + i8 * 4)
            elif hi == 0x9:  # mov.w @(disp,PC),Rn
                v = self.fetch16(pc + 4 + i8 * 2)
                r[n] = v - 0x10000 if v & 0x8000 else v
            elif hi == 0xE:
                r[n] = s8
            elif hi == 0x7:
                r[n] = (r[n] + s8) & 0xFFFFFFFF
            elif hi == 0x6 and op & 15 == 0:  # mov.b @Rm,Rn
                v = self.rd(r[m], 1)
                r[n] = v - 0x100 if v & 0x80 else v
            elif hi == 0x6 and op & 15 == 1:  # mov.w @Rm,Rn
                v = self.rd(r[m], 2)
                r[n] = v - 0x10000 if v & 0x8000 else v
            elif hi == 0x6 and op & 15 == 2:
                r[n] = self.rd(r[m], 4)
            elif hi == 0x6 and op & 15 == 0xD:  # extu.w
                r[n] = r[m] & 0xFFFF
            elif hi == 0x2 and op & 15 == 0:
                self.wr(r[n], 1, r[m])
            elif hi == 0x2 and op & 15 == 1:
                self.wr(r[n], 2, r[m])
            elif hi == 0x2 and op & 15 == 8:  # tst
                self.t = int(r[n] & r[m] & 0xFFFFFFFF == 0)
            elif hi == 0x2 and op & 15 == 0xB:  # or
                r[n] = (r[n] | r[m]) & 0xFFFFFFFF
            elif hi == 0x3 and op & 15 == 2:  # cmp/hs
                self.t = int((r[n] & 0xFFFFFFFF) >= (r[m] & 0xFFFFFFFF))
            elif op >> 8 == 0x88:  # cmp/eq #imm,r0
                self.t = int((r[0] & 0xFFFFFFFF) == (s8 & 0xFFFFFFFF))
            elif op >> 8 == 0xCA:  # xor #imm,r0
                r[0] ^= i8
            elif hi == 0x0 and op & 0xFF == 0x29:  # movt
                r[n] = self.t
            elif op >> 8 in (0x89, 0x8B, 0x8D, 0x8F):
                taken = self.t == (1 if op >> 8 in (0x89, 0x8D) else 0)
                dest = pc + 4 + s8 * 2
                if op >> 8 in (0x89, 0x8B):  # no delay slot
                    pc = dest if taken else nxt
                    continue
                target = dest if taken else None
                if target is None:
                    delayed = None
            elif hi in (0xA, 0xB):  # bra / bsr
                d = op & 0xFFF
                d = d - 0x1000 if d & 0x800 else d
                dest = pc + 4 + d * 2
                if hi == 0xB:
                    self.calls.append(dest)
                    target = nxt + 2  # a call: recorded, not entered
                else:
                    target = dest
            elif hi == 0x4 and op & 0xFF == 0x0B:  # jsr @Rm
                self.calls.append(r[n])
                target = nxt + 2
            else:
                raise ValueError(f"0x{pc:08X}: 0x{op:04X} not implemented")
            if delayed is not None:
                pc = delayed
                delayed = None
                if pc == 0xDEAD0000:
                    return
                continue
            if target is not None:
                delayed = target
            pc = nxt
        raise ValueError("no return")


def expected(row: int, names: int, signs: int, button: str) -> dict[str, int]:
    out = {"row": row, "names": names, "signs": signs, "state": 3, "sub": 2}
    if button in ("Start", "B"):
        out.update(state=1, sub=0)
    elif button in ("Up", "Down"):
        out["row"] = row ^ 1
    elif button in ("Left", "Right", "A", "C"):
        if row == 0:
            out["names"] = int(names == 0)
        else:
            out["signs"] = (signs + (2 if button == "Left" else 1)) % 3
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--build", type=Path, default=Path("build/ui006/b"))
    p.add_argument(
        "--out",
        type=Path,
        default=Path("research/experiments/EXP-0072/menu_logic.json"),
    )
    a = p.parse_args()
    code = (a.build / "CYBER.BIN").read_bytes()
    labels = {
        k: int(v, 16)
        for k, v in json.loads((a.build / "names_switch_changes.json").read_text())[
            "labels"
        ].items()
    }
    cases: list[dict[str, Any]] = []
    for row in (0, 1):
        for names in (0, 1):
            for signs in (0, 1, 2):
                for button, bits in BUTTONS.items():
                    ram: dict[int, int] = {}
                    m = Machine(code, ram)
                    m.wr(SUB, 2, 2)
                    m.wr(STATE, 2, 3)
                    m.wr(FADE, 4, 0)
                    m.wr(PAD1, 2, bits)
                    m.wr(PAD2, 2, 0)
                    m.wr(ROW, 1, row)
                    m.wr(FLAG, 1, names)
                    m.wr(FLAG2, 1, signs)
                    m.run(labels["extra"])
                    got = {
                        "row": m.rd(ROW, 1),
                        "names": m.rd(FLAG, 1),
                        "signs": m.rd(FLAG2, 1),
                        "state": m.rd(STATE, 2),
                        "sub": m.rd(SUB, 2),
                    }
                    want = expected(row, names, signs, button)
                    drew = labels["draw"] in m.calls
                    cases.append(
                        {
                            "row": row,
                            "names": names,
                            "signs": signs,
                            "button": button,
                            "got": got,
                            "ok": got == want,
                            "redrawn": drew,
                        }
                    )
    passed = sum(c["ok"] for c in cases)
    report = {
        "build_cyber_sha256": __import__("hashlib").sha256(code).hexdigest(),
        "cases": len(cases),
        "passed": passed,
        "results": cases,
    }
    a.out.write_text(json.dumps(report, indent=1) + "\n")
    print(passed, "of", len(cases))
    for c in cases:
        if not c["ok"]:
            print(c)
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
