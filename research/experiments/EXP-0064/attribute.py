"""EXP-0064: the address an SH-2 data access used, from its instruction and registers.

``access(op, regs)`` returns ``(address, size, kind)`` for the SH-2's data
load/store forms (``kind`` "r", "w" or "rw"), or None for anything else.
Registers are the values logged at the breakpoint hit, before the
instruction executes (Mednafen's log; ``@-Rn`` therefore uses Rn - size).
Forms follow the Hitachi SH-2 programming manual.
"""

from __future__ import annotations

SIZES = (1, 2, 4)


def access(op: int, regs: dict[str, int]) -> tuple[int, int, str] | None:
    n, m = (op >> 8) & 15, (op >> 4) & 15
    r = lambda i: regs.get(f"R{i}", 0)  # noqa: E731
    top, low = op >> 12, op & 15
    if top == 0x2 and low in (0, 1, 2):
        return r(n), SIZES[low], "w"
    if top == 0x2 and low in (4, 5, 6):
        size = SIZES[low - 4]
        return (r(n) - size) & 0xFFFFFFFF, size, "w"
    if top == 0x6 and low in (0, 1, 2, 4, 5, 6):
        return r(m), SIZES[low % 4], "r"
    if top == 0x0 and low in (4, 5, 6):
        return (r(0) + r(n)) & 0xFFFFFFFF, SIZES[low - 4], "w"
    if top == 0x0 and low in (0xC, 0xD, 0xE):
        return (r(0) + r(m)) & 0xFFFFFFFF, SIZES[low - 0xC], "r"
    if top == 0x1:
        return (r(n) + 4 * low) & 0xFFFFFFFF, 4, "w"
    if top == 0x5:
        return (r(m) + 4 * low) & 0xFFFFFFFF, 4, "r"
    if top == 0x8 and n in (0, 1):
        size = SIZES[n]
        return (r(m) + size * low) & 0xFFFFFFFF, size, "w"
    if top == 0x8 and n in (4, 5):
        size = SIZES[n - 4]
        return (r(m) + size * low) & 0xFFFFFFFF, size, "r"
    gbr = regs.get("GBR", 0)
    disp = op & 0xFF
    if top == 0xC and n in (0, 1, 2):
        size = SIZES[n]
        return (gbr + size * disp) & 0xFFFFFFFF, size, "w"
    if top == 0xC and n in (4, 5, 6):
        size = SIZES[n - 4]
        return (gbr + size * disp) & 0xFFFFFFFF, size, "r"
    if top == 0xC and n in (0xC, 0xD, 0xE, 0xF):
        return (gbr + r(0)) & 0xFFFFFFFF, 1, "rw" if n != 0xC else "r"
    if top == 0x4 and (op & 0xFF) in (0x02, 0x12, 0x22, 0x03, 0x13, 0x23):
        return (r(n) - 4) & 0xFFFFFFFF, 4, "w"
    if top == 0x4 and (op & 0xFF) in (0x06, 0x16, 0x26, 0x07, 0x17, 0x27):
        return r(n), 4, "r"
    if top == 0x4 and (op & 0xFF) == 0x1B:
        return r(n), 1, "rw"
    if top in (0x0, 0x4) and low == 0xF:
        return r(m), 4 if top == 0 else 2, "r"
    return None


def in_ranges(address: int, size: int, ranges: list[tuple[int, int]]) -> int | None:
    for k, (a, b) in enumerate(ranges):
        if address < b and address + size > a:
            return k
    return None
