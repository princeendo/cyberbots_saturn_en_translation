# Confirmed Discoveries

Only durable `CONFIRMED` findings about Cyberbots belong here, each with an ID
(`D-NNN`), its evidence (experiment, task) and reproduction instructions.
Hypotheses and failures go in `research_log.md`; open questions go in
`docs/known_unknowns.md`.

MSHvSF and XvSF findings are never recorded here. A sibling finding enters this
file only after a Cyberbots experiment confirms the Cyberbots equivalent.

## D-001: Stock Mednafen cold-boots Cyberbots to the title screen (`EMU-003`, `EXP-0001`)

Stock Mednafen 1.32.1 (`077ac658…669f`) with the Japanese BIOS `sega_101.bin`
(`dcfef4b9…deac`) and the silent home `local/mednafen_quiet/` cold-boots the
untouched source image with no input. The log reports `SGID: T-1217G`,
`SGNAME: CYBER BOTS`, `SGAREA: J` and `Cart: 1MiB Extended RAM`
(`ss.cart auto`). The title logo shows from about 57 s after launch, with
`PRESS START BUTTON` from about 61 s to 66 s. Three boots gave byte-identical
frames at one-second sampling (119 of 119); title frame 064 hashes
`e9f12474…ee24`. Source hashes were unchanged.

Reproduce: `research/experiments/EXP-0001/README.md`, "Procedure".

## D-002: Every audio track has one ISO 9660 entry (`EXP-0001`)

The 61 ISO 9660 entries whose extents lie beyond track 01 start exactly at
the 61 audio tracks' first sectors, one entry per track: the LSN in the
directory record equals the track's LBA in Mednafen's table of contents (and
in the CUE sheet). `01`-`32` are tracks 2-33, `45`-`52` are tracks 34-41, and
the 21 per-pilot `*_END*` entries are tracks 42-62 (full map in
`EXP-0001`, "Side observations"). This is disc layout only; what the tracks
contain is not established.

Reproduce: compare `references/saturn_jp/iso_listing.json` (`lsn` of each
entry with `unreadable`) with the `Track N, ... LBA:` lines of any
`local/emu003/boot*/mednafen.log`.

## D-003: No cartridge is needed to boot and run attract mode (`EMU-004`, `EXP-0002`)

With `ss.cart` set to `none`, `backup`, `extram1` or `extram4`, the untouched
image boots with no input to the title and the attract fight without any
warning. `extram1` and `extram4` give frames byte-identical to D-001 (119 of
119 each). `none` and `backup` show the same screens, including identical
title frames 058 and 064, shifted by about one second in places (attract
fight earlier with no cart; intro later with a save cart). Only boot and
attract were tested, not play. The project setting stays `ss.cart auto`
(1 MiB).

Reproduce: `research/experiments/EXP-0002/README.md`, "Procedure".

## D-004: Screenshots and save/load states work by hotkey (`EMU-006`, `EXP-0003`)

In stock 1.32.1, F9 writes a 352x240 PNG (330x240 during the BIOS phase) to
the home's `snaps/`, and F5 writes `mcs/<image>.<md5>.mc0` (1,099,526 bytes
at the title). F7 restores the saved title later in the same session and in a
fresh cold boot, about 35 s before a normal boot reaches the title. The
reloaded title is byte-identical to a screenshot taken near save time, and the
attract sequence continues from it in its normal order. The state file is
unchanged by loading. Send hotkeys with `tools/mednafen/hotkeys.py
--keep-focus`: one F9 was lost in a run that returned focus between keys.

Reproduce: `research/experiments/EXP-0003/README.md`, "Procedure".

## D-005: The stock debugger dumps, writes and breaks, unattended (`EMU-007`, `EXP-0004`)

Driven by `tools/mednafen/hotkeys.py --keep-focus --script`, stock 1.32.1's
debugger, frozen at the title, dumps WRAM-L and WRAM-H (1,048,576 bytes each)
repeatably: two dumps of each at one freeze are byte-identical
(`bb0628a5…517c`, `fc70d589…8b10`). Loading a 16-byte file into WRAM-H offset
`0xF0000` and dumping it back reads the file; loading the saved original
restores it. A write breakpoint on `06000000-060fffff 26000000-260fffff`
halts the CPU (identical window captures seconds apart) at a store into
WRAM-H. One run lost its WRAM-L dumps without an error: check that every dump
file exists.

Reproduce: `research/experiments/EXP-0004/README.md`, "Procedure".

## D-006: The save-state extractor is valid for work RAM and VRAM (`DBG-001`, `EXP-0005`)

`tools/memory/mcs_extract.py` with its default `saturn` byte order (each
stored 16-bit element swapped) reproduces stock debugger dumps of the same
frozen instant byte for byte: WRAM-L and WRAM-H at two instants, VDP1 VRAM and
VDP2 VRAM at one. Without the swap (`--byte-order state`) every region
differs. These four regions extracted from Mednafen 1.32.1 states may be used
as evidence. Cart RAM is not validated, and the tool's 4 MiB cart entry
refuses Cyberbots' 1 MiB cart, so pass `--region` explicitly.

Reproduce: `research/experiments/EXP-0005/README.md`, "Procedure".

## D-007: The agent interface works on Cyberbots (`EMU-021`, `EXP-0006`)

The sibling patch (`c30146ef…5244`) applies unchanged to stock 1.32.1 and
builds (`vendor/mednafen/build-agent/src/mednafen`, `2fc3d547…eaaf`). Without
`MEDNAFEN_AGENT_DIR` it cold-boots frame-identically to stock (119 of 119
frames equal D-001). With it, through `tools/mednafen/agent.py`: `read` of
WRAM-L, WRAM-H, VDP1 and VDP2 VRAM equals validated extraction (D-006) of a
state saved in the same poll; a write round-trips exactly; `pause`, `step`,
`run` and `frames N` work; `savestate` is refused while halted; log-mode
write breakpoints record hits (with all registers) while frames advance; a
halt-mode breakpoint stops with registers as text. Agent output may be used
as evidence.

Reproduce: `research/experiments/EXP-0006/README.md`, "Procedure".

## D-008: One shared dialogue table in three program files (`TXT-001`, `EXP-0007`)

Static file facts (not yet runtime facts). `VICTORY.BIN`, `END.BIN` and
`STG0AS.BIN` each contain the same 50,112 bytes (SHA-256 prefix
`f69902f8d27f98d2`): 1,851 Shift-JIS dialogue lines, each 4-byte aligned,
NUL-terminated and zero-padded, followed by the ASCII literal `SsCB`. At
load base `0x06060000`, every dialogue line is pointed to by a 32-bit word in
each file, inside record-like structures after the table. No other file on
the data track holds such a table. Lines are at most 16 full-width
characters (34 bytes); the script uses 909 distinct double-byte characters
(729 kanji) and a few ASCII characters. Offsets, lengths and hashes per line:
`data/text/script_census.json`.

Reproduce: `research/experiments/EXP-0007/README.md`, "Procedure".

## D-009: The arcade English dialogue table (`REF-003`, `EXP-0008`)

In the US/EU arcade program region (68000 order), a table of 624 big-endian
32-bit pointers at `0x0B33AA` (`0x0B3396` in `cybotsj`) addresses 530
distinct English dialogue records (`0x0B3D6A`-`0x0BB9A6`). A record is four
16-bit words (the fourth `0x000E`), one byte per character, and `0x00`. The
map is one tile sheet: `0x40`-`0x49` `0`-`9`, `0x4A`-`0x63` `A`-`Z`,
`0x64`-`0x7D` `a`-`z`, `0x7E` `?`, `0x7F` `!`, plus `0x14` `.`, `0x1B` `,`,
`0xF8` `'`, `0xF0` space, `0xFF` line break. It decodes 99.87% of the code
bytes; `09`, `0B`, `18` and `1C` remained, and D-010 settles them. Two more
tables of the same layout hold Spanish (624 slots) and Japanese (494 slots).
All five held sets carry identical record content in all three tables.
Decoder: `tools/reference/cybots_text.py`; metadata:
`data/arcade/dialogue_tables.json`.

Reproduce: `research/experiments/EXP-0008/README.md`, "Procedure".

## D-010: What the arcade draws, and what selects it (`REF-004`, `EXP-0009`)

In MAME 0.289, starting a 1-player game in `cybotsu` shows story dialogue
drawn from the English table (D-009): the reader at PC `0x011F6A` fetches
slot N and the box shows record N, typed out. The slot comes from a dialogue
script (`0x12150`) and is written to `0xFF2F7A` by PC `0x011D48` immediately
before; the region byte at `0xFF80A0` chooses the table (`0x00` Japanese;
US `0x02` and EU `0x08` English; Spanish for 6, 10, or 8 with another flag
set). The draw routine `0x11F5C` places the box from header words 1 and 2.
Forcing slots through a breakpoint on `0x11F5C` showed the last four codes:
`09` `:`, `0B` `-`, `18` `"`, `1C` `.` (D-009's map now decodes all English
records). `cybotsj` reads only the Japanese table, and its first line opens
like the Saturn script's first line.

Reproduce: `research/experiments/EXP-0009/README.md`, "Procedure".

## D-011: Saturn lines pair with arcade slots, and so with the arcade English (`REF-006`, `EXP-0010`)

The arcade Japanese records use 16-bit codes (`0xFFFF` line break), and the
code map can be learned from the two scripts with no conflicting votes (573
of 579 codes; `data/text/arcade_jp_map.json`). 825 of Saturn lines 0-898
pair, in order, with arcade record lines (787 identical, 38 edited), in 450
arcade slots; each slot's Saturn lines are consecutive in 449 of 450 cases.
The arcade passes one slot number to whichever language table is selected,
and `cybotsj` shows the same slot sequence as `cybotsu` in the scene
observed, so a paired Saturn record's English is the arcade English record
with the same slot number. Saturn lines 899-1850 (952 lines) have no arcade
counterpart, and so no official English; they begin with VS-screen chapter
captions (D-012). Pairs:
`data/text/saturn_arcade_pairing.json`.

Reproduce: `research/experiments/EXP-0010/README.md`, "Procedure".

## D-012: Where the Saturn shows Japanese in an ordinary run (`REF-005`, `EXP-0011`)

In one recorded arcade-mode run (title to game over, plus options), Japanese
appears on three surfaces: the story dialogue boxes; a caption box on the VS
screen before each fight, whose text is a line of the dialogue table
(Saturn lines 899 and 900 were shown, in the Saturn-only block of D-011);
and pilot and mech names drawn as katakana art on the pilot select and VS
screens. Menus, select labels, HUD, banners, round results, bonus,
continue, game over, initials and options are already English. Inventory:
`docs/text_surfaces.md`.

Reproduce: `research/experiments/EXP-0011/README.md`, "Procedure".

## D-013: One set of names; only the name art differs (`REF-007`, `EXP-0012`)

Every pilot named in both the arcade English and the Saturn script has the
same name in both (for example Jin Saotome, Gawaine, Mary, Santana, Arieta,
Bao and Mao, SHADE, Devilotte, Chiyomaru); only the script differs. Tessan
has no arcade English. The pilot select and VS screen show names as katakana
art on the Saturn and the Japanese arcade, and as Latin art on the US
arcade; the HUD is Latin everywhere. The Saturn's VS-screen name art is
uncompressed VDP1 sprite data in `SELECT.VAD` (for example `0x1EE80`).
Table: `docs/names.md`.

Reproduce: `research/experiments/EXP-0012/README.md`, "Procedure".

## D-014: Story dialogue is fixed from a checkpoint (`DBG-002`, `EXP-0014`)

Six replays of two session states before and during Jin's first pre-fight
box all show the same completed box (Saturn lines 4-5) and the same reply
from Shade, by dialogue-strip hash. Runs from one state fall into two timing
variants a few frames apart (typing progress, portrait mouth frames), so
comparisons use completed boxes or the box region at a settled moment, not
frame-aligned whole screens.

Reproduce: `research/experiments/EXP-0014/README.md`, "Procedure".

## D-015: Dialogue is Shift-JIS in RAM and drawn as VDP1 sprites per character (`DBG-004`, `EXP-0016`)

At the M1 checkpoints, Saturn lines 4-5 occur once in work RAM, as plain
Shift-JIS, at WRAM-H `0x0606F09C`/`0x0606F0B8`, inside `STG0AS.BIN` resident
at `0x06060000` (all but 30 bytes equal to the file; dialogue table at
`0x0606F01C`). VDP1 draws the box as one normal sprite per character (color
word `0x70E0`, 16×16, 4 bpp, 14 px apart), from glyph cells at VDP1 VRAM
`0x1E200` + `0x80` × n. Zeroing the first cell blanked the first character
on screen; the cells are refilled continually, apparently from a WRAM-H
shadow at `0x060E0000` + offset. The glyphs are anti-aliased (values 0 and
9-14); `KANJI.BIN` shares that palette, but its glyph layout is not yet
known.

Reproduce: `research/experiments/EXP-0016/README.md`, "Procedure".

## D-016: M1, the box changes when its Shift-JIS changes in RAM (`RE-001`, `EXP-0017`)

From checkpoint A, writing 26 bytes of Shift-JIS (あいうえおかきくけこさしす)
over Saturn line 4 at WRAM-H `0x0606F09C`, before the box types, makes Jin's
first pre-fight box show those characters on its first line, with its second
line and the following box unchanged; a no-write control from the same
checkpoint shows the original box. The Saturn draws its dialogue from the
resident Shift-JIS text.

Reproduce: `research/experiments/EXP-0017/README.md`, "Procedure".

## D-017: The M1 box's text is loaded raw from `STG0AS.BIN` (`DISC-001`, `EXP-0018`)

When the first story stage starts (after machine select), the game issues one
CD Play Disc for FAD `0x58A0`, 157 sectors: `STG0AS.BIN`, LSN 22,538,
320,724 bytes, file 292 in the game's copy of the ISO directory (WRAM-H
`0x060DCB98`, 24-byte entries). An SH-2 longword copy at `0x06041F8C`
moves the data from the CD block's data register (`0x25818000`) to WRAM-H
`0x06060000` in file order, with no decoding and no relocation. So file offset
= address − `0x06060000`, and M1 line 4 is at `STG0AS.BIN` offset `0xF09C`.
After the load, only 10 bytes outside the dialogue table differ from the
file. A write breakpoint on lines 4-5 is hit 14 times from a pre-load state
(twice, identically) and never from a post-load state.

Reproduce: `research/experiments/EXP-0018/README.md`, "Procedure".
