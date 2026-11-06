"""The in-game names switch: OPTION MODE → EXTRA OPTIONS → NAMES (OPT-005).

The user's design (``docs/localization_policy.md``, "Names Switch, Decided"):
OPTION MODE's title moves from text row 4 to 2 and its rows up two rows; a
new row ``EXTRA OPTIONS`` (row 22) opens a sub-menu with one row ``NAMES``,
values ``ENGLISH`` / ``JAPANESE``, and ``PRESS START TO EXIT``. The value is
the settings block's spare byte ``0x060D9295`` (D-055: saved with the other
options; 0 = ENGLISH). With the byte set, the original katakana name art is
put back after the game loads the Latin build's files:

- **pilot select** (``CYBER.BIN``): right after ``0x060388FA``(10) has loaded
  ``STG0A.BIN`` and before its init runs, the 124 untouched part-table bytes
  (``STG0A.BIN`` ``0x1CA18``-``0x1CA94``, inline in the code block) are copied
  to ``0x0607CA18`` (hook C, the literal of ``0x06038C9E``); right after
  ``SELECT.VAD`` is loaded to VDP1 VRAM (``0x06038CD6``), ``ZNAMES1.BIN``
  (untouched ``SELECT.VAD`` ``0x17840``-``0x19A00``) is loaded to
  ``0x25C37840`` (hook A, the literal of ``0x06038CD4``);
- **VS screen** (``STG0AS.BIN``): when the poll of the ``PL3F_0.BIN`` load
  reports done, ``ZNAMES2.BIN`` (untouched ``PL3F_0.BIN`` ``0x90``-``0x97BC``)
  is loaded to ``0x20200090`` (hook B, the literal ``0x060606C0``).

All new code lives in ``0x06055424``-``0x06055824``, zero bytes inside
``CYBER.BIN``'s file (D-057). ``ZNAMES1.BIN`` and ``ZNAMES2.BIN`` go into
Track 01's free tail with directory records sorting after ``WARNING4.PIX``
(``tools.disc.add_files``; D-056).

The patch plans were designed statically and checked by independent reviews
in ``OPT-005`` (an SH-2 interpreter run of the menu's cursor code: 204
cases); every original word is asserted before it is changed.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

from tools.sh2.asm import Assembler

CYBER_BASE = 0x0600D000
OVERLAY_BASE = 0x06060000
FREE = (0x06055424, 0x06055824)  # D-057
FLAG = 0x060D9295  # D-055
SELECT_RANGE = (0x17840, 0x19A00)
PARTS_RANGE = (0x1CA18, 0x1CA94)
VS_RANGE = (0x90, 0x97BC)
TAIL_NAMES = ("ZNAMES1.BIN", "ZNAMES2.BIN")

# OPTION MODE's text-row immediates (mov #row,r5) in OPDEMO.BIN's draw
# routine 0x060623A4-0x0606262F; each moves up two rows.
ROWS = {
    0x060623CA: "DIFFICULTY label",
    0x060623DE: "TIME LIMIT label",
    0x060623F2: "SHORT CUT label",
    0x06062406: "SOUND label",
    0x0606241A: "SOUND TEST label",
    0x0606242E: "DATA RESET label",
    0x06062442: "KEY CONFIG. label",
    0x0606245E: "3M RAM MODE label",
    0x060624B4: "difficulty scale",
    0x060624C6: "star bar, empty stars",
    0x060624DE: "star bar, filled stars",
    0x06062502: "TIME LIMIT ON",
    0x0606251A: "TIME LIMIT OFF",
    0x06062530: "SHORT CUT ON",
    0x06062544: "SHORT CUT OFF",
    0x06062552: "SOUND STEREO",
    0x06062568: "SOUND MONAURAL",
    0x06062584: "SOUND TEST number",
    0x060625D2: "DATA RESET PRESS A+B+C",
    0x060625E0: "KEY CONFIG PRESS A or C",
    0x06062604: "3M RAM MODE ON",
    0x0606261A: "3M RAM MODE OFF",
}
SHIFT = 2
TITLE_ROW = (0x060623AA, 0xE504, 0xE502)
EXTRA_ROW = 22

# The cursor wrap 0x06062A7E-0x06062AD7: cursor 8 = EXTRA OPTIONS; without a
# RAM cart, 7 (3M RAM MODE) is skipped; the cursor is stored only while the
# state word is still 2 (so A/C with Up/Down opens the row it was on).
WRAP = {
    0x06062A84: (0x2D32, 0x6020),
    0x06062A86: (0x6020, 0x4311),
    0x06062A88: (0x600C, 0x8D01),
    0x06062A8A: (0x8801, 0xE108),
    0x06062A8C: (0x8B1A, 0x6313),
    0x06062A8E: (0x61D2, 0x3317),
    0x06062A90: (0x4111, 0x8B00),
    0x06062A92: (0x8D01, 0xE300),
    0x06062A94: (0xE407, 0x2008),
    0x06062A96: (0x2D42, 0x8B18),
    0x06062A98: (0x62D2, 0x6033),
    0x06062A9A: (0x3247, 0x8807),
    0x06062A9C: (0x891A, 0x8B15),
    0x06062A9E: (0xA01B, 0xA011),
    0x06062AA0: (0x0009, 0x4B11),
    0x06062AC4: (0x61D2, 0x8D01),
    0x06062AC6: (0x4111, 0xE308),
    0x06062AC8: (0x8D01, 0xE306),
    0x06062ACA: (0xE406, 0x6091),
    0x06062ACC: (0x2D42, 0x8802),
    0x06062ACE: (0x62D2, 0x8B03),
    0x06062AD0: (0x3247, 0x2D32),
    0x06062AD2: (0x8B01, 0x0009),
    0x06062AD4: (0xE100, 0x0009),
    0x06062AD6: (0x2D12, 0x0009),
}


@dataclass
class Built:
    files: dict[str, bytes]  # CYBER.BIN, OPDEMO.BIN
    stg0as: tuple[
        int, bytes, bytes
    ]  # file offset, original, new (patch the built file)
    tail: list[tuple[str, bytes]]  # (ISO name, data) for Track 01's tail
    changes: list[dict[str, Any]] = field(default_factory=list)
    labels: dict[str, int] = field(default_factory=dict)
    code_range: tuple[int, int] = (0, 0)


class _Patcher:
    def __init__(
        self, name: str, data: bytes, base: int, changes: list[dict[str, Any]]
    ):
        self.name, self.buf, self.base, self.changes = (
            name,
            bytearray(data),
            base,
            changes,
        )

    def put(self, address: int, old: bytes, new: bytes, purpose: str) -> None:
        o = address - self.base
        if bytes(self.buf[o : o + len(old)]) != old:
            raise ValueError(f"{self.name} 0x{address:08X}: not the expected original")
        self.buf[o : o + len(new)] = new
        self.changes.append(
            {
                "file": self.name,
                "offset": f"0x{o:05X}",
                "address": f"0x{address:08X}",
                "original": old.hex(),
                "new": new.hex(),
                "purpose": purpose,
            }
        )

    def word(self, address: int, old: int, new: int, purpose: str) -> None:
        self.put(address, struct.pack(">H", old), struct.pack(">H", new), purpose)

    def long(self, address: int, old: int, new: int, purpose: str) -> None:
        self.put(address, struct.pack(">I", old), struct.pack(">I", new), purpose)


def _bsr(a: Assembler, label: str) -> None:
    def enc(labels: dict[str, int], pc: int) -> bytes:
        d = (labels[label] - (pc + 4)) // 2
        if not -0x800 <= d < 0x800:
            raise ValueError("bsr out of range")
        return (0xB000 | (d & 0xFFF)).to_bytes(2, "big")

    a._emit(2, enc)


def _mova(a: Assembler, label: str) -> None:
    def enc(labels: dict[str, int], pc: int) -> bytes:
        disp, rest = divmod(labels[label] - ((pc & ~3) + 4), 4)
        if rest or not 0 <= disp <= 0xFF:
            raise ValueError("mova out of range")
        return (0xC700 | disp).to_bytes(2, "big")

    a._emit(2, enc)


def menu_code(origin: int, words: dict[str, Any]) -> Assembler:
    """The title hook, the state-3 trampoline and the EXTRA OPTIONS screen."""
    a = Assembler(origin)
    r = a.op
    # Title hook: called instead of 0x0602A766 by 0x060623BA (r4-r7 = title args).
    a.label("title_hook")
    for w in (0x4F22, 0x2F46, 0x2F56, 0x2F66, 0x2F76):  # push pr, r4-r7
        r(w)
    a.mov_l_label("L_cursor", 0)
    r(0x6002)  # mov.l @r0,r0
    r(0x8808)  # cmp/eq #8,r0
    a.branch("bt/s", "th1")
    r(0xE61F)  # r6 = 31 (selected)
    r(0xE614)  # r6 = 20
    a.label("th1")
    r(0xE406)  # x 6
    r(0xE500 | EXTRA_ROW)
    a.mov_l_label("L_s_extra", 7)
    a.mov_l_label("L_print", 0)
    r(0x400B)
    r(0x0009)
    for w in (0x67F6, 0x66F6, 0x65F6, 0x64F6, 0x4F26):  # pop r7-r4, pr
        r(w)
    a.mov_l_label("L_title", 0)
    r(0x402B)  # jmp 0x0602A766
    r(0x0009)
    # State 3: KEY CONFIG unless the cursor is on EXTRA OPTIONS.
    a.label("state3")
    a.mov_l_label("L_cursor", 0)
    r(0x6002)
    r(0x8808)
    a.branch("bt", "extra")
    a.mov_l_label("L_keycfg", 0)
    r(0x402B)
    r(0x0009)
    # EXTRA OPTIONS, substate word 0x060CFEE4 (as KEY CONFIG).
    a.label("extra")
    a.mov_l_label("L_sub", 1)
    r(0x6011)  # mov.w @r1,r0
    r(0x8800)
    a.branch("bt", "sub0")
    r(0x8801)
    a.branch("bt", "sub1")
    r(0x4F22)  # sub2: input
    a.mov_l_label("L_fade", 0)
    r(0x6000)
    r(0x2008)
    a.branch("bf", "ret")
    a.mov_l_label("L_pad1", 1)
    r(0x6211)
    a.mov_l_label("L_pad2", 1)
    r(0x6311)
    r(0x223B)  # or r3,r2
    r(0x622D)  # extu.w r2,r2
    a.mov_w_label("W_exit", 3)
    r(0x2238)  # tst r3,r2 (Start|B)
    a.branch("bf", "leave")
    a.mov_w_label("W_tog", 3)
    r(0x2238)  # Right|Left|A|C
    a.branch("bt", "draw_ret")
    a.mov_l_label("L_byte", 1)
    for w in (0x6010, 0x2008, 0x0029, 0x2100):  # byte = (byte == 0)
        r(w)
    a.label("draw_ret")
    _bsr(a, "draw")
    r(0x0009)
    a.label("ret")
    r(0x4F26)
    r(0x000B)
    r(0x0009)
    a.label("leave")
    a.mov_l_label("L_sound", 0)
    for w in (0xE409, 0xE500, 0x400B, 0xE600):  # sound(9,0,0)
        r(w)
    a.mov_l_label("L_fadeout", 0)
    r(0x400B)
    r(0xE401)  # 0x0602C474(1)
    a.mov_l_label("L_state", 1)
    r(0xE201)
    r(0x2121)  # state = 1
    a.mov_l_label("L_sub", 1)
    r(0xE200)
    r(0x2121)  # substate = 0
    a.branch("bra", "ret")
    r(0x0009)
    a.label("sub0")  # substate = 1, start the fade-out
    r(0xE201)
    r(0x2121)
    a.mov_l_label("L_fadeout", 0)
    r(0x402B)
    r(0xE401)
    a.label("sub1")  # after the fade: clear, draw, fade in
    r(0x4F22)
    a.mov_l_label("L_fade", 0)
    r(0x6000)
    r(0x2008)
    a.branch("bf", "ret")
    a.mov_l_label("L_clear", 0)
    r(0x400B)
    r(0x0009)
    a.mov_l_label("L_edaa2", 0)
    r(0x400B)
    r(0x0009)
    _bsr(a, "draw")
    r(0x0009)
    a.mov_l_label("L_fadein", 0)
    r(0x400B)
    r(0xE401)
    a.mov_l_label("L_sub", 1)
    r(0xE202)
    r(0x2121)  # substate = 2
    a.branch("bra", "ret")
    r(0x0009)
    a.label("draw")
    for w in (0x4F22, 0x2FE6, 0x2FD6):  # push pr, r14, r13
        r(w)
    a.mov_l_label("L_print", 14)
    a.mov_l_label("L_byte", 13)
    a.mov_l_label("L_title", 0)
    for w in (0xE408, 0xE504, 0xE678):  # title: x 8, row 4, colour 120
        r(w)
    a.mov_l_label("L_s_extra", 7)
    r(0x400B)
    r(0x0009)
    for w in (0xE406, 0xE508, 0xE61F):  # NAMES: x 6, row 8, 31
        r(w)
    a.mov_l_label("L_s_names", 7)
    r(0x4E0B)
    r(0x0009)
    r(0x60D0)
    r(0x2008)
    a.branch("bt/s", "d1")
    r(0xE61F)
    r(0xE614)
    a.label("d1")
    r(0xE415)  # ENGLISH: x 21, row 8
    r(0xE508)
    a.mov_l_label("L_s_eng", 7)
    r(0x4E0B)
    r(0x0009)
    r(0x60D0)
    r(0x2008)
    a.branch("bf/s", "d2")
    r(0xE61F)
    r(0xE614)
    a.label("d2")
    r(0xE41E)  # JAPANESE: x 30, row 8
    r(0xE508)
    a.mov_l_label("L_s_jpn", 7)
    r(0x4E0B)
    r(0x0009)
    for w in (0xE40C, 0xE518, 0xE61F):  # PRESS START TO EXIT: x 12, row 24, 31
        r(w)
    a.mov_l_label("L_s_exit", 7)
    r(0x4E0B)
    r(0x0009)
    for w in (0x6DF6, 0x6EF6, 0x4F26, 0x000B, 0x0009):
        r(w)
    a.label("W_exit")
    a.word(0x0900)  # Start | B
    a.label("W_tog")
    a.word(0xC600)  # Right | Left | A | C
    a.align4()
    for name, v in (
        ("L_cursor", 0x0606BE8C),
        ("L_print", 0x0602A82A),
        ("L_title", 0x0602A766),
        ("L_keycfg", 0x06063FD0),
        ("L_sub", 0x060CFEE4),
        ("L_state", 0x060CFEE0),
        ("L_fade", 0x060CFEA0),
        ("L_pad1", 0x060CC016),
        ("L_pad2", 0x060CC026),
        ("L_byte", FLAG),
        ("L_sound", 0x0602B916),
        ("L_fadeout", 0x0602C474),
        ("L_fadein", 0x0602C3CE),
        ("L_clear", 0x0602AAD4),
        ("L_edaa2", 0x0602EDA2),
        ("L_s_exit", 0x06065B24),
    ):
        a.label(name)
        a.long(v)
    for name in ("L_s_extra", "L_s_names", "L_s_eng", "L_s_jpn"):
        a.label(name)
        a.long("S" + name[3:])
    menu = words["menu"]
    for name, text in (
        ("S_extra", menu["entry"]),
        ("S_names", menu["row"]),
        ("S_eng", menu["values"][0]),
        ("S_jpn", menu["values"][1]),
    ):
        a.label(name)
        a.data(text.encode("ascii") + b"\0")
    a.align4()
    return a


def hook_code(origin: int, parts: bytes) -> Assembler:
    """Hooks A (select art), B (VS records) and C (select part table)."""
    a = Assembler(origin)
    a.label("hookB")  # wraps the VS poll; returns its result, 1 when done
    a.push_pr()
    a.mov_l_label("L_poll", 0)
    a.jsr(0)
    a.nop()
    a.tst(0, 0)
    a.branch("bt", "B_ret")
    a.mov_l_label("L_flag", 1)
    a.mov_b_load(1, 0)
    a.tst(0, 0)
    a.branch("bt", "B_done")
    a.mov_l_label("L_zn2", 4)
    a.mov_l_label("L_wraml", 5)
    a.mov_l_label("L_size2", 6)
    a.mov_l_label("L_loader", 0)
    a.jsr(0)
    a.nop()
    a.label("B_done")
    a.mov_imm(1, 0)
    a.label("B_ret")
    a.pop_pr()
    a.rts()
    a.nop()
    a.label("hookA")  # jsr @r4 at 0x06038CD6; r5/r6 from the caller
    a.push_pr()
    a.mov_l_label("L_selname", 4)
    a.mov_l_label("L_loader", 0)
    a.jsr(0)
    a.nop()
    a.mov_l_label("L_flag", 1)
    a.mov_b_load(1, 0)
    a.tst(0, 0)
    a.branch("bt", "A_done")
    a.mov_l_label("L_zn1", 4)
    a.mov_l_label("L_vram", 5)
    a.mov_l_label("L_size1", 6)
    a.mov_l_label("L_loader", 0)
    a.jsr(0)
    a.nop()
    a.label("A_done")
    a.pop_pr()
    a.rts()
    a.nop()
    a.label("hookC")  # jsr @r2 at 0x06038CA0, right after STG0A.BIN is loaded
    a.mov_l_label("L_flag", 1)
    a.mov_b_load(1, 0)
    a.tst(0, 0)
    a.branch("bt", "C_init")
    _mova(a, "parts")
    a.mov_l_label("L_ptab", 1)
    a.mov_imm(len(parts) // 4, 2)
    a.label("C_copy")
    a.mov_l_load(0, 3, post=True)
    a.dt(2)
    a.mov_l_store(3, 1)
    a.branch("bf/s", "C_copy")
    a.add_imm(4, 1)
    a.label("C_init")
    a.mov_l_label("L_init", 2)
    a.op(0x422B)  # jmp @r2: PR untouched, init returns to the caller
    a.nop()
    a.align4()
    for name, v in (
        ("L_loader", 0x060385A0),
        ("L_flag", FLAG),
        ("L_poll", 0x06038E9C),
        ("L_selname", 0x06046398),
        ("L_zn1", "s_zn1"),
        ("L_vram", 0x25C20000 + SELECT_RANGE[0]),
        ("L_size1", SELECT_RANGE[1] - SELECT_RANGE[0]),
        ("L_ptab", OVERLAY_BASE + PARTS_RANGE[0]),
        ("L_init", OVERLAY_BASE),
        ("L_zn2", "s_zn2"),
        ("L_wraml", 0x20200000 + VS_RANGE[0]),
        ("L_size2", VS_RANGE[1] - VS_RANGE[0]),
    ):
        a.label(name)
        a.long(v)
    a.label("parts")
    a.data(parts)
    a.label("s_zn1")
    a.data(TAIL_NAMES[0].encode() + b"\0")
    a.label("s_zn2")
    a.data(TAIL_NAMES[1].encode() + b"\0")
    a.align4()
    return a


def build(originals: dict[str, bytes], words: dict[str, Any]) -> Built:
    """CYBER.BIN and OPDEMO.BIN with the switch, the STG0AS patch, the tail files.

    ``originals``: the untouched CYBER.BIN, OPDEMO.BIN, STG0AS.BIN, STG0A.BIN,
    SELECT.VAD and PL3F_0.BIN.
    """
    menu = words["menu"]
    if menu["title"] != menu["entry"]:
        raise ValueError("the sub-menu's title and its entry row share one string")
    changes: list[dict[str, Any]] = []
    parts = originals["STG0A.BIN"][PARTS_RANGE[0] : PARTS_RANGE[1]]
    m = menu_code(FREE[0], words)
    menu_bytes = m.assemble()
    menu_bytes += bytes(-len(menu_bytes) % 4)  # the hooks start 4-byte aligned
    hooks_origin = FREE[0] + len(menu_bytes)
    h = hook_code(hooks_origin, parts)
    hook_bytes = h.assemble()
    hook_bytes += bytes(-len(hook_bytes) % 4)
    end = hooks_origin + len(hook_bytes)
    if end > FREE[1]:
        raise ValueError(f"new code ends at 0x{end:08X}, past the free range")
    labels = {**m.labels, **h.labels}

    cy = _Patcher("CYBER.BIN", originals["CYBER.BIN"], CYBER_BASE, changes)
    cy.put(
        FREE[0], bytes(end - FREE[0]), menu_bytes + hook_bytes, "new code (D-057 range)"
    )
    cy.long(
        0x06038DA0,
        0x06060000,
        labels["hookC"],
        "literal of 0x06038C9E: STG0A init -> hook C",
    )
    cy.long(
        0x06038DC0,
        0x06046398,
        labels["hookA"],
        "literal of 0x06038CD4: SELECT.VAD name -> hook A",
    )
    cy.word(0x06038CD6, 0xBC63, 0x440B, "bsr 0x060385A0 -> jsr @r4 (hook A)")

    op = _Patcher("OPDEMO.BIN", originals["OPDEMO.BIN"], OVERLAY_BASE, changes)
    for address, purpose in ROWS.items():
        o = address - OVERLAY_BASE
        w = struct.unpack(">H", originals["OPDEMO.BIN"][o : o + 2])[0]
        if w >> 8 != 0xE5:
            raise ValueError(f"0x{address:08X} is not mov #imm,r5")
        row = w & 0xFF
        op.word(
            address, w, 0xE500 | (row - SHIFT), f"{purpose}: row {row} -> {row - SHIFT}"
        )
    op.word(*TITLE_ROW, "OPTION MODE title: row 4 -> 2")
    op.long(
        0x06062470,
        0x0602A766,
        labels["title_hook"],
        "literal of the title call -> title hook",
    )
    op.long(
        0x06062B3C, 0x06063FD0, labels["state3"], "literal of state 3 -> trampoline"
    )
    op.word(
        0x060627E6,
        0xA14A,
        0xA118,
        "dispatch default (cursor 8) -> the KEY CONFIG handler",
    )
    for address, (was, now) in WRAP.items():
        op.word(address, was, now, "cursor wrap")

    stg = originals["STG0AS.BIN"]
    o = 0x060606C0 - OVERLAY_BASE
    old = stg[o : o + 4]
    if old != struct.pack(">I", 0x06038E9C):
        raise ValueError("STG0AS.BIN poll literal not as expected")
    new = struct.pack(">I", labels["hookB"])
    changes.append(
        {
            "file": "STG0AS.BIN",
            "offset": f"0x{o:05X}",
            "address": "0x060606C0",
            "original": old.hex(),
            "new": new.hex(),
            "purpose": "literal of 0x060605BA: VS poll -> hook B",
        }
    )
    tail = [
        (
            TAIL_NAMES[0] + ";1",
            originals["SELECT.VAD"][SELECT_RANGE[0] : SELECT_RANGE[1]],
        ),
        (TAIL_NAMES[1] + ";1", originals["PL3F_0.BIN"][VS_RANGE[0] : VS_RANGE[1]]),
    ]
    return Built(
        files={"CYBER.BIN": bytes(cy.buf), "OPDEMO.BIN": bytes(op.buf)},
        stg0as=(o, old, new),
        tail=tail,
        changes=changes,
        labels=labels,
        code_range=(FREE[0], end),
    )


def patch_stg0as(built_stg0as: bytes, built: Built) -> bytes:
    """Apply the hook-B literal to an already built STG0AS.BIN."""
    o, old, new = built.stg0as
    if built_stg0as[o : o + 4] != old:
        raise ValueError("built STG0AS.BIN differs at the hook-B literal")
    return built_stg0as[:o] + new + built_stg0as[o + 4 :]
