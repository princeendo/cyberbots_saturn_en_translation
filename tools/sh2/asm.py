"""Minimal two-pass SH-2 assembler for the small routines the builds add.

It covers only the forms those routines use, each encoded as in the Hitachi
SH-2 programming manual (and decoded back by `tools.sh2.disasm`, which the
tests use to check every form). Labels resolve in a second pass: branch
targets are ``pc + 4 + 2 * displacement``; ``mov.l`` literals are
``(pc & ~3) + 4 + 4 * displacement``. It is game-independent.

    a = Assembler(0x0601EDC0)
    a.mov_l_label("count", 0)
    a.label("count")
    a.long(0x060148C0)
    code = a.assemble()

Copied into the Cyberbots repository from the XvSF repository,
``tools/sh2/asm.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

from collections.abc import Callable


class Assembler:
    def __init__(self, origin: int) -> None:
        if origin & 1:
            raise ValueError("code must be 2-byte aligned")
        self.origin = origin
        self.items: list[tuple[int, Callable[[dict[str, int], int], bytes]]] = []
        self.labels: dict[str, int] = {}
        self.size = 0

    @property
    def pc(self) -> int:
        return self.origin + self.size

    def _emit(self, size: int, encode: Callable[[dict[str, int], int], bytes]) -> None:
        self.items.append((self.pc, encode))
        self.size += size

    def word(self, value: int) -> None:
        self._emit(2, lambda _l, _p: (value & 0xFFFF).to_bytes(2, "big"))

    def op(self, value: int) -> None:
        self.word(value)

    def label(self, name: str) -> None:
        if name in self.labels:
            raise ValueError(f"label {name} defined twice")
        self.labels[name] = self.pc

    def align4(self) -> None:
        if self.pc & 2:
            self.op(0x0009)  # nop

    def long(self, value: int | str) -> None:
        if self.pc & 3:
            raise ValueError("a long must be 4-byte aligned")

        def encode(labels: dict[str, int], _pc: int) -> bytes:
            v = labels[value] if isinstance(value, str) else value
            return (v & 0xFFFFFFFF).to_bytes(4, "big")

        self._emit(4, encode)

    def data(self, blob: bytes) -> None:
        self._emit(len(blob), lambda _l, _p: blob)

    # Instructions (n, m: register numbers)
    def mov_l_label(self, label: str, n: int) -> None:
        def encode(labels: dict[str, int], pc: int) -> bytes:
            target = labels[label]
            disp, rest = divmod(target - ((pc & ~3) + 4), 4)
            if rest or not 0 <= disp <= 0xFF:
                raise ValueError(f"literal {label} out of reach")
            return (0xD000 | n << 8 | disp).to_bytes(2, "big")

        self._emit(2, encode)

    def mov_w_label(self, label: str, n: int) -> None:
        def encode(labels: dict[str, int], pc: int) -> bytes:
            disp, rest = divmod(labels[label] - (pc + 4), 2)
            if rest or not 0 <= disp <= 0xFF:
                raise ValueError(f"literal {label} out of reach")
            return (0x9000 | n << 8 | disp).to_bytes(2, "big")

        self._emit(2, encode)

    def branch(self, kind: str, label: str) -> None:
        codes = {"bt": 0x8900, "bf": 0x8B00, "bt/s": 0x8D00, "bf/s": 0x8F00}

        def encode(labels: dict[str, int], pc: int) -> bytes:
            disp, rest = divmod(labels[label] - (pc + 4), 2)
            if kind == "bra":
                if rest or not -0x800 <= disp < 0x800:
                    raise ValueError(f"bra {label} out of reach")
                return (0xA000 | disp & 0xFFF).to_bytes(2, "big")
            if rest or not -0x80 <= disp < 0x80:
                raise ValueError(f"{kind} {label} out of reach")
            return (codes[kind] | disp & 0xFF).to_bytes(2, "big")

        self._emit(2, encode)

    def nop(self) -> None:
        self.op(0x0009)

    def rts(self) -> None:
        self.op(0x000B)

    def mov_imm(self, imm: int, n: int) -> None:
        self.op(0xE000 | n << 8 | imm & 0xFF)

    def add_imm(self, imm: int, n: int) -> None:
        self.op(0x7000 | n << 8 | imm & 0xFF)

    def add(self, m: int, n: int) -> None:
        self.op(0x300C | n << 8 | m << 4)

    def mov(self, m: int, n: int) -> None:
        self.op(0x6003 | n << 8 | m << 4)

    def mov_b_load(self, m: int, n: int, post: bool = False) -> None:
        self.op((0x6004 if post else 0x6000) | n << 8 | m << 4)

    def mov_w_load(self, m: int, n: int) -> None:
        self.op(0x6001 | n << 8 | m << 4)

    def mov_l_load(self, m: int, n: int, post: bool = False) -> None:
        self.op((0x6006 if post else 0x6002) | n << 8 | m << 4)

    def mov_b_store(self, m: int, n: int) -> None:
        self.op(0x2000 | n << 8 | m << 4)

    def mov_w_store(self, m: int, n: int) -> None:
        self.op(0x2001 | n << 8 | m << 4)

    def mov_w_r0_disp(self, disp: int, m: int) -> None:
        """mov.w @(disp,Rm),r0 (disp in bytes, even)."""
        self.op(0x8500 | m << 4 | disp // 2)

    def mov_l_store(self, m: int, n: int) -> None:
        self.op(0x2002 | n << 8 | m << 4)

    def tst(self, m: int, n: int) -> None:
        self.op(0x2008 | n << 8 | m << 4)

    def or_(self, m: int, n: int) -> None:
        self.op(0x200B | n << 8 | m << 4)

    def cmp_eq(self, m: int, n: int) -> None:
        self.op(0x3000 | n << 8 | m << 4)

    def cmp_hs(self, m: int, n: int) -> None:
        self.op(0x3002 | n << 8 | m << 4)

    def extu_b(self, m: int, n: int) -> None:
        self.op(0x600C | n << 8 | m << 4)

    def shll8(self, n: int) -> None:
        self.op(0x4018 | n << 8)

    def dt(self, n: int) -> None:
        self.op(0x4010 | n << 8)

    def jsr(self, m: int) -> None:
        self.op(0x400B | m << 8)

    def shll(self, n: int) -> None:
        self.op(0x4000 | n << 8)

    def mov_w_index(self, m: int, n: int) -> None:
        """mov.w @(r0,Rm),Rn."""
        self.op(0x000D | n << 8 | m << 4)

    def push_pr(self) -> None:
        """sts.l pr,@-r15."""
        self.op(0x4F22)

    def pop_pr(self) -> None:
        """lds.l @r15+,pr."""
        self.op(0x4F26)

    def trapa(self, imm: int) -> None:
        self.op(0xC300 | imm & 0xFF)

    def assemble(self) -> bytes:
        out = bytearray()
        for pc, encode in self.items:
            out += encode(self.labels, pc)
        if len(out) != self.size:
            raise AssertionError("size mismatch")
        return bytes(out)
