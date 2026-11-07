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

**Corrected 2026-11-05 (`EXP-0040`):** the Japanese table also has 624
pointers. Slots 494-623, speaker names among them, sit at
`0x0A38AE`-`0x0A3AB5` in `cybotsj` and point to records past `0x0AA8D4`;
`cybotsj`'s ending reads slots 610 and 614 there.

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

**Corrected 2026-11-02 (`PAIR-001`, `EXP-0023`).** The record reader stopped
at the space code `0x0020`, which occurs 60 times inside arcade Japanese
records, so 60 records were cut short. With the fix, 897 of Saturn lines
0-898 pair (852 identical, 45 edited), in 488 slots. The map learned 590 of
596 codes, still with no conflicts. Only lines 34 (dead data, D-021) and 258
are unpaired in 0-898. Lines 899-1850 still have no counterpart. The counts
above are the first run's.

**Corrected 2026-11-03 (`WIN-001`, `EXP-0031`).** The arcade table has 624
slots, not 494: `find_tables` stops at 494. Slots 494-623 follow Saturn
lines from 899 at a fixed offset (slot k = line k + 405; 79 exact matches in
slots 494-600), and the US table has English in all 130. So part of the
range 899-1850 does have arcade counterparts: VS captions and versus win
quotes (D-029). Lines from 1029 on are not matched. (Correction, D-060: the VS
captions' slots 494-551 hold one shared record, not caption English.)

**Corrected 2026-11-04 (`EXP-0035`):** line 258 is not Saturn-only. It is
slot 140's second line with its punctuation changed, too short for the
alignment; slot 140's English covers it.

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

## D-018: M2, the M1 change works from a rebuilt image (`DISC-002`, `EXP-0019`)

An image built from the untouched source by `tools/disc/patch_image.py` has
26 bytes of `STG0AS.BIN` changed at file offset `0xF09C`, the M1 hiragana
over Saturn line 4. Only LSN 22,568 changes, and EDC/ECC is regenerated
(Track 01 SHA-256 `739a58e2…`). On that image Jin's first pre-fight box
shows the change, with no RAM write. This holds in a replay from the
pre-load state 4138 (strip hash `1d501a`; the original image gives
`ead786`) and after a cold boot played through arcade mode with Jin. The cold
boot to the title is frame-identical to the original image's. The tool's
identity rebuild is byte-identical to the source.

Reproduce: `research/experiments/EXP-0019/README.md`, "Procedure".

## D-019: The dialogue font is `KANJI.BIN`; glyphs come from a code table (`FONT-001`, `EXP-0020`)

As a box scene starts, `KANJI.BIN` (LSN 4,780, 80 sectors) is read raw into
VDP2 VRAM `0x40000` by the same CD copy loop as the script (`0x06041FB4`).
It holds 1,280 glyphs of 16×16 at 4 bpp, as 8×8 VDP2 tiles in a sheet 16
tiles wide. Glyph `g` is tiles `t`, `t+1`, `t+16`, `t+17`, with
`t = (g // 8) × 32 + (g % 8) × 2`. A re-encode of the decoded glyphs is
byte-identical (`tools/font/kanji.py`).

For each two-byte text code, `0x0606E9E8` searches the 1,222-entry table at
`0x060AAD7C` (`STG0AS.BIN` offset `0x4AD7C`; also in `END.BIN` and
`VICTORY.BIN`) and takes the code's position as `g`. `0x06011224` copies
VDP2 tile `0x2000 + t` into the WRAM-H cell that VDP1 draws. The mapping
predicts all 25 cells of the M1 box. A probe image with glyph 600 replaced
shows that character, and only it, changed.

The font has full-width digits and capitals A-Z, but no lower case, plus two
half-width pair glyphs (`Dr`, `!?`).

Reproduce: `research/experiments/EXP-0020/README.md`, "Procedure".

## D-020: No native English path; the box holds 4 rows of 16 cells and 60 glyphs (`FONT-002`, `EXP-0021`)

The typing routine (`0x0606E5C0`) places each two-byte character itself, at
x = base + 14 × column and y = base + 16 × row. It never wraps. A line ends at
its 0 byte. The next row comes from the box record, a header of 8 bytes and
then 8-byte entries `(line pointer, word)`, where `0xFFFF` continues and
anything else ends the box. The M1 box's record is at `0x0609D184`.

Neither the typing routine nor the layout loop (`0x0606E734`) branches on a
region or language. No English dialogue is on the disc (ASCII, arcade code or
full-width).

Live RAM tests from checkpoint A, each with a control, show:
- full-width capitals and digits draw from the existing font;
- codes outside the table draw blank cells;
- a 17th cell runs off the screen edge, and `0x0A` is not a line break while
  typing;
- a record with five entries shows four rows inside the box.

`0x0601118E` reserves 60 glyph cells per box (`0x060FE200`-`0x060FFFFF`)
and the allocator has no bounds check. A box past 60 cells hangs the game
(SUPPORTED).

Of the 450 paired arcade slots, 31 fit in full-width capitals as written and
272 after re-wrapping to 16 cells. All 450 fit with two characters per cell,
which needs 571 distinct pair glyphs.
**Corrected 2026-11-02 (`EXP-0023`)** for the 488 paired slots of the
revised D-011: 33 as written, 298 re-wrapped, and 488 with pairs (579
distinct pairs).

Reproduce: `research/experiments/EXP-0021/README.md`, "Procedure".

## D-021: What selects a story box; Jin's 17 story scenes (`RE-002`, `EXP-0022`)

The chain:
1. The stage code (stage byte `0x060CFF88`, step byte `0x060CFF89`, table
   `0x0609353C`) posts constant scene numbers through `0x0606DBEA`, as message
   `0x14000000` in the queue `0x060DAF78`.
2. The scene task (`0x0606E1E8`) takes the pilot from the byte at task +
   `0x1F` and the scene from the byte at task + `0x23`. The pilot picks a
   scene list from `0x060AAD24` (Jin's is `0x060AA840`, 22 scripts).
3. The bytecode interpreter (`0x0606E230`) shows box N for a word N below
   `0x8000`, and closes it for `0x8000 | N`; `0xE000` ends the scene.
4. Box N's record is `@(0x060A5684 + 4N)`: an 8-byte header, then 8-byte
   (line pointer, word) entries, where `0xFFFF` continues.

Jin's stage code posts scenes 21 and 0-15 in a fixed order over stages 0-8.
They show boxes 0-62: Saturn lines 0-120, except the dead line 34, all in
`STG0AS.BIN`. Jin's scenes 16-20 are posted from `END.BIN` (his ending).
Writing the scene byte right after it is set shows any chosen scene: three
forced scenes drew exactly their predicted cells.

(Correction, `EXP-0074`: the scene table has 313 entries, ending at the
list table `0x060AAD24`; the 335 used in tools runs 22 words past it. The
boxes found are unchanged.)

Reproduce: `research/experiments/EXP-0022/README.md`, "Procedure".

## D-022: Jin's story pairs box for slot with the arcade English (`PAIR-001`, `EXP-0023`)

The arcade's dialogue scripts (`0x12150`: per-pilot, then per-scene 16-bit
offsets, read at `0x11CC6`) and the Saturn's (D-021) are the same bytecode.
For Jin (pilot 0), the arcade's scenes 21 and 0-15 name exactly the Saturn's
boxes, number for number, so each Saturn box N is shown where the arcade shows
slot N. The arcade stores that slot (`0xFF2F7A`) and only then picks the
language table, so slot N's English record is the official English for Saturn
box N.

In MAME (`cybotsu`), the unforced run shows scene 21 then scene 0 (slots 0-5),
as on the Saturn. Scenes 4, 9 and 15, forced at `0x11CEA`, show slots 18, 33
and 59 in English, the same first boxes that the Saturn shows when forced
(EXP-0022), with the same portraits.

All 63 of Jin's boxes (120 lines) have an English record. With REF-006's
reader fixed (D-011, corrected), all 120 lines also align with their slot's
Japanese: 115 identical and 5 edited. Jin's story has no Saturn-only line.
Pairing: `data/translations/jin_pairing.json`.

Reproduce: `research/experiments/EXP-0023/README.md`, "Procedure".

## D-023: Font codes in use, the font's users, record size, and free RAM (`LAYOUT-001`, `EXP-0024`)

- **Codes in use.** The Japanese text of `STG0AS.BIN`, `VICTORY.BIN` and
  `END.BIN` uses 912 of the 1,222 table codes. 310 codes, plus 26 empty table
  slots and 58 empty glyph slots, are used by no line.
- **The font's users.** Only those three files call the glyph routine
  `0x06011224`, so a glyph change reaches story, endings and `VICTORY.BIN`
  alike.
- **Record size.** Box records are 32 bytes apart, which allows 3 lines in
  place.
- **Free RAM.** WRAM-H `0x06002F00`-`0x06007CFF` and `0x060E3300`-`0x060E7FFF`
  were zero in all 166 REF-005 states. They took no CPU write over a full
  stage, game over and the ranking screen (12,000 frames).

Reproduce: `research/experiments/EXP-0024/README.md`, "Procedure".

## D-024: Pair glyphs from the arcade's letters work after a cold boot (`LAYOUT-001`, `EXP-0025`)

The arcade's English dialogue font is monospace (8-pixel advance; a space
advances 5), with a 1-pixel shadow. It can be captured whole by drawing a test
record from work RAM (a breakpoint at `0x11F6E` redirects slot 2's record
pointer).

Its shades `#FFFFFF`, `#DDDDDD`, `#AAAAAA`, `#555555` and `#111111` map one to
one onto the Saturn font's values 9-13 (drawn `#F0F0F0`-`#101010`). Glyph
sprites are drawn 8 pixels lower on screen than their VDP1 y.

Two letters per Saturn cell at a 7-pixel advance, each narrowed by one column
(`tools/font/pairs.py`), placed in unused code slots, draw exactly as
predicted (48/48 cells). That held in a replay and after an agent-driven cold
boot of an image rebuilt from the untouched source. Three test rows of 32
characters came from dead lines through an extended record, and the
following Japanese box is unchanged (25/25).

Reproduce: `research/experiments/EXP-0025/README.md`, "Procedure".

## D-025: M3, Jin's story in English from the source image; fighter vitality (`RE-003`, `EXP-0026`)

`tools/text/dialogue.py` compiles the official arcade English for Jin's 63
story boxes, read from the `cybotsu` ROM at build time, into pair-glyph rows
of up to 32 characters and 3 rows per box, with rewritten box records:
- pairs take codes no Japanese uses first, then new codes in the table's last
  row (keeping its 0 terminator), then, by the user's decision, the 18
  least-used Japanese characters;
- rows go into Jin's own lines and his dead ending lines, leaving lines shared
  with other boxes.

The image built from the untouched source (82 sectors, all valid, Track 01
`904402b6…`):
- **Forced:** every box of all 17 scenes draws exactly its predicted cells
  (63/63); the original image draws none.
- **Cold boot:** played through two fights, it shows the English boxes.
- **Other pilots:** pilot 1's Japanese draws its original cells.

Fighter records sit at `0x060CFFE0` (player 1) and `0x060D02D4` (player 2):
x position at `+0x14`, vitality in bar units (152 full) at `+0x44`. A fight ends
only on a hit or at time-out.

Reproduce: `research/experiments/EXP-0026/README.md`, "Procedure".

## D-026: The pilot lists are the arcade's pilots; per-pilot stage groups (`RE-004`, `EXP-0027`)

Saturn per-pilot scene lists 0-5 (`0x060AAD24`) are the arcade's pilots 0-5,
with identical scene scripts outside the endings: Jin, Santana, Mary, Arieta,
Gawaine, and Bao and Mao. Lists 6-8 match no arcade pilot (the Saturn's own
pilots). On the pilot select screen Jin is first, Mary is one move right and
Santana two.

Each pilot's story is one block of constant scene posts in `STG0AS.BIN`, and
the stage byte `0x060CFF88` starts at that pilot's group of the shared stage
table: Jin 0, Santana 9, Mary 18. A cold boot with Santana posted 23, 0, 1,
2, 3 and 4, block 1's order. His story is scenes 0-15 and 23-26 (boxes
64-127, lines 121-237), and his ending is 16-22.

Reproduce: `research/experiments/EXP-0027/README.md`, "Procedure".

## D-027: Santana's story pairs box for slot too; slots can share a record (`PAIR-002`, `EXP-0028`)

Santana's 20 story scenes run the same scene scripts in both games, so each
of his 64 Saturn boxes N pairs with arcade slot N. All have an English record,
and all 117 lines align with their slot's Japanese (114 exact, 3 edited).

Forced in MAME (the interpreter's pilot set to 1 at `0x11CDA` and the scene at
`0x11CEA`), scenes 4, 9 and 24 play slots 81-84, 99-105 and 87-88: the
Saturn's boxes for those scenes.

Slots can share a record. Arcade slots 63 and 64 point to one record in both
languages, and Saturn boxes 63 and 64 to one record; box 63 is in no scene.

Reproduce: `research/experiments/EXP-0028/README.md`, "Procedure".

## D-028: M4, Jin and Santana in English from one source-built image (`RE-007`, `EXP-0030`)

`tools/text/dialogue.py` builds several pilots from one pair-code pool, with
kept and dead lines derived from the scene scripts (EXP-0029). Jin and
Santana together need 408 pairs: 310 unused codes, 25 new and 73 sacrificed
Japanese glyphs (the user's approved budget). Jin's codes and predicted cells
are those of his Jin-only build.

The image built from the untouched source (85 sectors, all valid, Track 01
`a63ba806…`):
- **Forced:** every story box of both pilots draws exactly its predicted
  cells (63/63 and 64/64); the original image draws none.
- **Cold boots:** Santana, chosen two moves right, plays through two forced
  fights into his third stage with his English boxes; Jin's first two scenes
  show as before.
- **Other pilots:** Mary's scene 0 draws her original Japanese, except the
  sacrificed `0x8BC1` in box 131, which shows its pair glyph.

The typing routine draws no cell for the full-width space `0x8140`.

Reproduce: `research/experiments/EXP-0030/README.md`, "Procedure".

## D-029: Versus mode shows win quotes from `VICTORY.BIN`; the arcade table has 624 slots (`WIN-001`, `EXP-0031`)

After a versus-mode win the game loads `VICTORY.BIN` (file-table entry 318,
request `0x140`) and `KANJI.BIN`, and shows a `VICTORY!` screen: the winner's
portrait and mech and one dialogue-table line (Saturn line 959 after Jin's
win), then an English `RESULT` tally. Arcade-mode wins and losses and the
attract mode never load `VICTORY.BIN` (CD Play Disc logs from REF-005
states). The load script that names it is at `0x0604C320`.

The arcade Japanese and US dialogue tables (`0x0A30F6`, `0x0B33AA`) have 624
pointers. Slots 494-623 follow the Saturn lines from 899 (slot k = line k +
405); line 959 is slot 558. The US set has English in all 130 slots.
(Correction, D-060: slots 494-551 all point to one record, which is not
caption English.)

**Corrected 2026-11-04 (`EXP-0032`):** the offset is not constant: slot 494
is line 899 (+405), slot 558 line 959 (+401), slot 600 line 1005 (+405).
Boxes that share a line or hold two lines move it. What holds is box for
slot: slot N's Japanese record is Saturn box N's lines (`VICTORY.BIN` box
table `0x0607849C`), D-030.

Reproduce: `research/experiments/EXP-0031/README.md`, "Procedure".

## D-030: Both games pick a win quote from a per-pilot table; box N is slot N; the US set has one English quote per level (`WIN-002`, `EXP-0032`)

- **Saturn** (`VICTORY.BIN` at `0x06060000`): the selector `0x06060B46`
  reads (scene, byte) from `0x0606FAA0` + 16 x winner's pilot + 2 x entry,
  where the entry is a random value & 7, and posts `0x14000009`: list 9 of
  the scene lists `0x0607DB3C` (the same 11 lists as `STG0AS.BIN`), 72
  scripts of one box each. In a versus run the halt at `0x06060BCE` gave
  R0 & 7 = 7 for Jin; the screen then showed box 560, as the table predicts.
- **Arcade** (`cybotsu`): `0x6301C` reads (scene, byte) from `0x630CE`
  (decrypted program space) for pilots 0-5 and posts `0x14000006`: list 6,
  48 scripts. Its scenes equal the Saturn table's for pilots 0-5, and its 48
  scripts equal the Saturn's list 9 scenes 0-47, box for slot. Forcing the
  table offset (`0x630B8`) for Jin's entries 2, 5 and 7 showed slots 599,
  558 and 560.
- **Saturn box N, arcade slot N:** boxes 554 and 556-600 (lines 955 and
  957-1005) are pilots 0-5's quotes; 37 of the 46 have the slot's Japanese
  exactly. Forcing boxes 599, 558 and 556 into the Saturn's script showed
  lines 1004, 959 and 957. Box 555 is in no table entry; boxes 1023-1044
  (lines 1790-1821) are pilots 6-8's.
- **US English:** one record per pilot and level (entries 2k and 2k+1):
  24 records for the 46 boxes. The Saturn's two quotes of a level share it.

Reproduce: `research/experiments/EXP-0032/README.md`, "Procedure".

## D-031: Block k is pilot list k; pilot select routes; stage groups of 9 (`RE-005`, `EXP-0033`)

Choosing a pilot posts the opening scene of that pilot's block of
`STG0AS.BIN`'s scene posts, then scene 0, and the stage byte `0x060CFF88`
starts at 9 x the list number. Cold boots of the untouched image showed it
for lists 3 (Arieta: 22, 0; stage 27), 4 (Gawaine: 20, 0; 36), 5 (Bao and
Mao: 27, 0; 45) and 6 (18, 0; 54), as D-026 did for lists 0-2. On the
pilot select screen, from Jin: Mary is one move right, Santana two,
Gawaine three, Bao and Mao four, Arieta five; one move left is list 6 and
two moves left list 8 (stage 72). Moves pressed while a portrait is still
loading are lost.

Reproduce: `research/experiments/EXP-0033/README.md`, "Procedure".

## D-032: Mary, Arieta, Gawaine, and Bao and Mao pair box for slot (`PAIR-003`, `EXP-0035`)

The story scenes of lists 2-5 run the same scene scripts in both games
(only ending scenes differ), so each Saturn box N pairs with arcade slot N.
Each of their 519 lines matches the same line of its own slot's Japanese
record, exactly (489) or with small edits (30), and every slot has a US
English record. Forced in MAME (pilot byte at `0x11CDA`, scene at
`0x11CEA`), scenes Mary 2 and 7, Arieta 1 and 9, Gawaine 5 and 10, and Bao
and Mao 2 and 11 played slots equal to the Saturn's boxes; forced on the
Saturn, every box of those scenes drew its predicted Japanese cells (757
of 757). Slots 283/284, 290/291 and 335/336 share a record; boxes 283, 290
and 335 are in no scene.

Reproduce: `research/experiments/EXP-0035/README.md`, "Procedure".

## D-033: M5, the roster's story and win quotes in English from the source image (`RE-008`, `EXP-0036`)

`tools/text/dialogue.py --roster data/text/m5_roster.json --indent --rank
staying --max-sacrifice 160` builds, from the untouched source, one image
with the six roster pilots' 404 story boxes (`STG0AS.BIN`) and 46 win-quote
boxes (`VICTORY.BIN`: its own records, line room and code-table copy) in
the official US arcade English: 487 pair glyphs, 152 sacrificed codes, 102
changed sectors, all valid (Track 01 `2c8505df…`). Two builds are
identical, and every changed byte lies in a range the compiler lists.

- **Forced:** every story box of the 114 story scenes and every roster quote
  box draws exactly its predicted cells (10,529 and 615); the original image
  draws none (0 of 905).
- **Play:** cold boots with menu keys only reach stage 2 of their groups for
  Jin, Santana, Arieta, Gawaine, and Bao and Mao, and Mary's stage 1 (her
  stage 19 is a cockpit stage that ends without input), with English boxes;
  a versus win shows an English quote.
- **Japanese left:** a Saturn-only box draws its sacrificed code's pair
  glyph, as recorded.

Reproduce: `research/experiments/EXP-0036/README.md`, "Procedure".


## D-034: Jin's ending: how it is reached and what it shows (`END-001`, `EXP-0037`)

A win ends the story only when the last-fight flag `0x060CFF07` is set. After
each win the game adds 1 to player 1's stage index (record `0x060CFFDC` +
`0x2E3`), sets the next opponent from `0x0604B5C0`/`0x0604B650`[row x 16 +
index], and sets that flag when the row's next entry is negative. The
round-end code then sets game mode 5 (`0x060CFEDC`), whose handler loads
`END.BIN`. The stage start sets the stage byte from `0x0607B440`[pilot x 10
+ index].

From REF-005 state 4138, writing index 8, Jin's last opponent (pilot 8,
machine 11), the opponent word and the flag before the stage start, and
holding the vitality, reaches his ending with no key pressed. Two runs log
the same posts, disc reads and box calls frame for frame. A checkpoint
before the win (`7e314718…64f2`) reproduces the ending exactly.

- **Loads:** `END.BIN`, portraits, `STDEMO.*`, `SE.DAT`, tracks 42-44
  (`JIN_END1`-`3`); then `KEND.BIN`, `KEND_0.BIN`, `KEND_1.BIN`,
  `ST09_FNT.BIN` and tracks 40 and 36 for the cast roll and credits; then
  `QSD.PIX` and the game over. No `KANJI.BIN`.
- **Scenes:** `END.BIN` posts scenes 16-19. They show boxes 408-422, 493,
  601, 605 and 1072 through its copy of the box routine (`0x0606268C`) and
  its record table `0x060817B4`, as dialogue boxes (16-17), narration on
  black (18) and captions with speaker names (19). Every box's predicted
  cells were drawn.
- **Japanese surfaces:** those three, the cast roll's names and one QSound
  line. The credits and everything after them are English.

Reproduce: `research/experiments/EXP-0037/README.md`, "Procedure".

## D-035: How Jin's ending draws each surface, and with which font (`END-002`, `EXP-0038`)

- **Dialogue boxes (scenes 16-19).** They follow the story's text path:
  `END.BIN`'s Shift-JIS lines in RAM, `END.BIN`'s 1,222-code table, one
  glyph cell per character at `0x060FE200` (D-019, D-020).
  - Their glyphs come from VDP2 VRAM `0x40000`. `SE.DAT` fills it: `SE.DAT`
    is read raw as a whole VDP2 VRAM image, and all 512 KiB equal the file
    through scenes 16-19. `KANJI.BIN` is not used.
  - From the END-001 checkpoint, against a no-change control:
    - an image with one glyph of `SE.DAT`'s font copy replaced changes only
      box 408's first cell, and only that character on screen;
    - writing one character code in `END.BIN`'s line in RAM changes only
      that cell, to the new code's glyph.
- **Cast-roll names.** VDP1 sprites, one per name line. Each is refreshed
  from a work-RAM shadow (WRAM-H `0x060E0000` + its VDP1 offset). The
  decoder `0x0601446C` writes that shadow from command and longword streams
  in `KEND_1.BIN`, which is loaded raw at WRAM-L `0x00280000`.
- **Staff credits and the thank-you screen.** VDP2 NBG0, drawn with
  `FIX.BIN`'s characters (loaded raw at VDP2 VRAM `0x0`). The small font is
  ASCII-indexed.
- **QSound notice.** `QSD.PIX`, a 512×256 256-colour bitmap loaded raw at
  VDP2 VRAM `0x20000` (NBG1). Its Japanese trademark line is pixels in that
  file.
- **Controlled changes from saved states.** Each removed exactly the
  predicted item:
  - zeroing one name sprite removed that name;
  - zeroing `FIX.BIN` character `0x41` removed every small `A`;
  - zeroing ten bitmap rows removed only the Japanese line.

  Zeroing 16 bytes of `KEND_1.BIN`'s command stream in RAM changed the
  names decoded after them.
- **Translation consequence.** `SE.DAT`'s font copy must change along with
  `KANJI.BIN`. The cast-roll names (SUPPORTED: whole-name images) and the
  QSound line are images, not text.

Reproduce: `research/experiments/EXP-0038/README.md`, "Procedure".

## D-036: The winner's pilot selects the ending; each list posts fixed scenes (`END-003`, `EXP-0039`)

- **Selection.** The last-fight round end (`0x06018DE8`) copies the
  winner's pilot byte (record + `0x2D2`) to `0x060CFF7E`. In mode 5,
  `END.BIN` (`0x06060446`) runs the dispatcher at `@(0x060775B4 + 4 ×
  [0x060CFF7E])`, one per list 0-8. Each dispatcher steps through its own
  table of routines (step word `0x060CFEE8`).
- **Posts.** Each routine posts fixed scenes through `0x06066852` with R4 =
  its list number and R5 = the scene; 41 calls, all constants. The scene's
  boxes come from that list's script in `END.BIN`'s copy of `STG0AS.BIN`'s
  scene data. The copy is shifted by `0x23ED0`, and all 234 scripts match.
  `data/text/ending_posts.json` lists each list's scenes and boxes:
  - Jin: 16-19;
  - Santana: 16-22;
  - Mary: 16;
  - Arieta: 16-21, 27, 28;
  - Gawaine: 16-19;
  - Bao and Mao: 16, 17, 28, 18, 19, 21, 22.

  Jin's scene 20 (box 550) is never posted.

  Corrected by D-043: a posted script runs on into the next scenes'
  words, so the boxes shown are more than these lists (Mary's ending shows
  the arcade's scenes 17-18, Bao and Mao's its scene 20).
- **Forced.** From the END-001 checkpoint, writing 1 into `0x060CFF7E`
  after the copy, or into player 1's pilot byte before it, plays Santana's
  ending (list 1's posts 16-22, its graphics, tracks 45-47). Every box
  draws its predicted cells (22 of 22).
- **Other text.** The CD copy loop (`0x06041FB4`) loads three files raw:
  - `KEND.BIN` at `0x06060000`, which holds the credits and thank-you text
    as ASCII strings (from offset `0x2F1E`);
  - `KEND_1.BIN` at WRAM-L `0x00280000`, the cast-roll name images;
  - `QSD.PIX` at VDP2 VRAM `0x20000`.

  One-letter RAM markers in `KEND.BIN`'s strings showed on screen
  (`XRCADE STAFF`, `SPECIAL THINKS`, `THINK YOU FOR PLAYING!`).

Reproduce: `research/experiments/EXP-0039/README.md`, "Procedure".

## D-037: The arcade's ending, reached and read; its English for Jin's ending (`END-004`, `EXP-0040`)

- **Selection.** The arcade selects its ending as the Saturn does. The round
  end (`0xDAF4`, in `cybotsu` and `cybotsj`) takes the ending path when
  `0xFFEA28` is set. It then copies the winner's pilot byte to the ending
  number `0xFFEB2C`. The mode handler dispatches on that number to one of 6
  routines (`cybotsu` table `0xE496`).
- **Route.** In headless MAME, from a fixed NVRAM copy, menu presses and one
  breakpoint at `0xDAE4` reach Jin's ending in both sets. The breakpoint
  gives player 1 two round wins, player 2 none, and sets the flag. Repeat
  runs are byte-identical.
- **Readers.** The ending's boxes are read by slot by the story's readers:
  - `cybotsu`: `0x011F6A`/`0x012014`, from the English table;
  - `cybotsj`: `0x011E7A`/`0x011F0E`, from the Japanese table.

  The slots are 408-422, 493, and the names 614 and 610. Nothing reads a
  dialogue table after scene 19, and `0x97222` is not used.
- **Scripts.** Both sets post the same ending scenes with the same slots
  (`data/arcade/ending_scripts.json`). Against the Saturn, box N is slot N,
  with three kinds of difference:
  - the Saturn adds a blank box 1072;
  - its speaker-name boxes are the arcade slot − 9 (Saturn 608 = slot 615);
  - it never posts Mary's scenes 17-18 or Bao and Mao's scene 20.
- **Surfaces.** The US arcade has English for Jin's dialogue, narration and
  captions (with English speaker names). Its cast roll shows Latin names
  only, while `cybotsj` shows katakana over Latin like the Saturn. Its
  ending has no QSound notice. Its staff credits are the arcade staff only.

Reproduce: `research/experiments/EXP-0040/README.md`, "Procedure".

## D-038: Jin's ending pairs box for slot; what has no English; what it needs (`END-005`, `EXP-0041`)

- **Pairing.** In each of scenes 16-19, the Saturn's boxes, less the blank
  box 1072, and the arcade's slots match in count and order
  (`data/translations/jin_ending_pairing.json`). Box N is slot N, except
  the speaker names 605 and 601, which are slots 614 and 610. The arcade
  reads each slot while the Saturn shows the box: five pairs were reviewed
  side by side (408, 493, 414, 605 + 416, 601 + 419).
- **Labels.** Of 30 dialogue lines, 27 are exactly the `cybotsj` slot's
  Japanese. Three have the same wording: box 408's ellipses are middle
  dots in the arcade, and the arcade names use an unmapped code `0x549`
  where the Saturn has a colon. Some of the US English is a free
  localization (for example 493, 416, 419).
- **No official English:**
  - box 1072 (blank);
  - the cast roll's 10 Japanese name images (`cybotsu` shows the Latin
    names only);
  - the QSound notice's Japanese line (no notice in the arcade ending).

  The user, 2026-11-05: "Hide, as US arcade (Recommended)" and "Erase the
  line (Recommended)". No unit needs new text.
- **Capacity.** The English fits:
  - 3 rows and 46 cells a box at most (limits 3 and 60), 16 cells a row
    (the widest Saturn line of each surface);
  - 179 pairs, or 160 with the half-cell indent, against 335 codes free in
    `END.BIN`'s code table by the story's rule. That table equals
    `STG0AS.BIN`'s, but it and `SE.DAT`'s font copy are the ending's own,
    so no Japanese code is sacrificed.
  - Rows need 872-880 bytes. Jin's own ending lines hold 828, so more room
    is needed: lines no ending box shows hold 44,124 (SUPPORTED, code only).
- **Shared.** Boxes 605 and 601 are also posted by lists 3, 4 and 8, and
  box 1072 by lists 1-5 and 7.

Reproduce: `research/experiments/EXP-0041/README.md`, "Procedure".

## D-039: During an ending, `END.BIN` never reads the lines no ending box shows (`END-010`, `EXP-0042`)

- `END.BIN`'s line table holds the 1,851 dialogue lines, then ASCII file
  names. 1,850 lines are pointed to by box records; 1,591 of those (18
  spans, 43,304 bytes) are in no box any ending posts. (`EXP-0041`'s 44,124
  bytes counted the file names too.)
- With those lines filled with a marker code in a test image, read
  breakpoints on the 18 spans log no hit while `END.BIN` is resident, from
  its load to `KEND.BIN`'s, in Jin's ending and in Santana's (list 1,
  forced). A read breakpoint on one of Jin's shown lines hits at its box's
  character reader (`0x06062788`/`0x0606278E`), so the method sees reads.
- Every box draws its original cells, and the box calls equal the
  controls'. The other hits are reads of other files at the same addresses:
  before `END.BIN` loads, and inside `KEND.BIN` (`0x06060000`-`0x0606C8A7`)
  after it loads.
- The other seven endings post only constant scenes through the same code
  (D-036), so for them this is SUPPORTED.

  Corrected by D-046: 16 of those lines (806-819, 888, 1007) are shown by
  Mary's and Bao and Mao's run-on boxes (D-043), so they are not room. The
  room is the lines no box of any list 0-8 is seen to open.

Reproduce: `research/experiments/EXP-0042/README.md`, "Procedure".

## D-040: The cast roll's names are sprite parts; size word 0 hides one (`END-010`, `EXP-0044`)

- The cast roll is bank 16 of the main program's sprite-part routine
  (`0x060113F0`). The bank header is at `KEND.BIN` + `0xA704`: +4 holds a
  16-bit part index per frame, and +8 the 6-byte parts in `KEND_0.BIN` (at
  `0x00200000`).
- A part whose second word has bit `0x20` takes its pattern record from
  `KEND_1.BIN` (at `0x00280000`), at 4 × (bit 0 << 16 | third word). The
  record's first word is the size: width (word & `0x0F00`) >> 5, height
  word & `0x7F`. A size of 0 skips the part (`0x0601157C`/`0x06011584`), so
  no command is written and nothing is decoded.
- Every ending's cast roll draws frames `0x1B6`-`0x1C9`. The even frames are
  the ten Japanese names (colour `0x40E0`, 16 records, 10-11 pixels high),
  the odd frames the Latin names (`0x41E0`).
- From a pre-roll state, setting the 16 records' size words to 0 removes
  every Japanese name and nothing else. The portraits and Latin names are
  unchanged, and shots without names are identical to the control. The
  built image does the same from disc (`EXP-0045`).

Reproduce: `research/experiments/EXP-0044/README.md`, "Procedure".

## D-041: The QSound line is erased by background pixels in `QSD.PIX` (`END-010`, `EXP-0043`)

- In `QSD.PIX`, index 0 is transparent and the notice's background is index
  255.
- The Japanese trademark line is the only non-background content in rows
  180-190, x 89-300; x 84-88 is the logo's edge.
- Setting that region to 255 changes 798 pixels, all of them the line. On
  screen the line is gone with no gap, and the English lines and the logo
  are unchanged (x 115-301, y 172-182 differ; nothing else does).

Reproduce: `research/experiments/EXP-0043/README.md`, "Procedure".

## D-042: Jin's ending in English, built from the source image (M7) (`END-010`, `EXP-0045`)

- `tools.text.dialogue --ending` builds one image with the M5 roster
  unchanged and Jin's ending in the official US arcade English. RE-008's
  story files, prediction and changes hashes are kept, and two builds are
  identical.
  - **`END.BIN`:** 18 boxes, 34 rows. All 179 pairs are on codes no line
    uses, with no sacrifice. The rows use Jin's own free lines (828 bytes,
    including the shared names' lines 1006 and 1010) and 64 bytes of D-039's
    room.
  - **`SE.DAT`'s font copy:** 179 glyphs.
  - **`KEND_1.BIN` and `QSD.PIX`:** D-040 and D-041.
  - 158 sectors changed, all valid.
- From the END-001 checkpoint every unit draws its predicted cells. Forced
  list 4 shows boxes 605/601 in English and its own boxes unchanged. A cold
  boot plays Jin's story in English. The screenshots were agent-reviewed.
- Caption rows 2-3 start under the caption's column, after the speaker
  name, as in the arcade.
- **Box timing.** Each ending box stays open for a time the scene sets, the
  same in both languages within ±8 frames, and typing takes about 6 frames
  a glyph. English boxes 409, 493 and 420 (45, 43 and 31 glyphs, against
  30, 30 and 25 in Japanese) finish typing 7, 7 and 4 frames before they
  close. Nothing is cut off; every other box holds its full line for 80-300
  frames.

Reproduce: `research/experiments/EXP-0045/README.md`, "Procedure".

## D-043: What each roster ending shows; scripts run on into the next scenes (`END-020`, `EXP-0046`)

- **Forced runs.** Each of lists 1-5, forced from the END-001 checkpoint,
  posts exactly D-036's scenes. But the boxes it opens are not only the
  posted scripts' boxes: a posted scene's script runs on past `0xE000` into
  the next scenes' words until the next post. So:
  - Mary's ending (one post, scene 16) shows boxes 437-447 with names 602,
    604 and 610, which are the arcade's scenes 16-18;
  - Bao and Mao's shows box 486, the arcade's scene 20, between posts 19
    and 21;
  - the other lists open their posted boxes, with speaker names reopened
    for each caption.

  `data/text/ending_surfaces.json` records the observed sequence of every
  list 0-5 and supersedes D-036's box lists for these lists.
- **Surfaces.** Every Japanese text in lists 1-5 before the cast roll is an
  `END.BIN` box: dialogue boxes with portraits, captions with or without a
  speaker name, and narration. No picture carries text. After the dialogue,
  every list loads the same `FIX.BIN`, `KEND*.BIN` and `QSD.PIX`, and shows
  the same cast roll, credits, thank-you screen and QSound notice.
- **Arcade.** Setting the ending number `0xFFEB2C` after the round end's
  copy (`0xDBB6`/`0xDC0C`) plays that list's ending. Each of lists 1-5, in
  both sets, reads exactly the slots its script opens, including Mary's
  scenes 17-18 and Bao and Mao's 20.

Reproduce: `research/experiments/EXP-0046/README.md`, "Procedure".

## D-044: Every roster ending's text has official English at the same place (`END-021`, `EXP-0047`)

- In each of lists 0-5, the boxes the Saturn opens (less the blank 1072)
  and the slots the arcade's story reader reads, in forced runs of the same
  ending, are the same sequence. Dialogue box N is slot N; each speaker
  name stands where the arcade reads a name slot; each box pairs with one
  slot everywhere. `cybotsj` reads the same slots as `cybotsu`.
- Lists 1-5 have 102 text units, all with official English, 63 exact and
  39 with the same wording (punctuation, the colon code `0x549`, unmapped
  kanji codes). No new translation is needed
  (`data/translations/<pilot>_ending_pairing.json`).
- **Box kinds.** The box record's first 4 words in `END.BIN` give the kind:
  - `0000 008C 00AC 000E`: dialogue box;
  - `0000 0050`/`0070 0050 000E`: narration;
  - `0030 0088 00AC 000E`: caption (`0x30` is the caption column);
  - `0000 0028`-`004C 00AC 000E`: speaker name.
- **Names.** Saturn name box N shows arcade name slot N + 9 (D-038) except
  box 608 (both twins). At its places the arcade shows slot 615 (Bao
  alone); the same two names, with their own English, are slot 617. Box
  603's one extra opening (list 1, before caption 435) shows a name the
  arcade does not open there.

Reproduce: `research/experiments/EXP-0047/README.md`, "Procedure".

## D-045: How ending boxes are timed, and a rule that keeps the scenes in step (`END-011`, `EXP-0048`)

- **Cues.** `END.BIN`'s pointer table `0x060879A0` holds 9 pointers, one cue
  table per ending list (Jin's at `0x0608786E`, file `0x2786E`): 16-bit
  frame counts on the scene's timer. Script word `0xEAnn` after a box waits
  until the timer reaches cue `nn`, then the box closes. Raising Jin's cue 2
  from 480 to 540 in RAM closed box 409 60 frames later, and box 493 opened
  that much later but closed at its own cue; nothing else moved.
- **Typing.** Script word `0xE2nn` before a box sets its typing interval to
  `nn` frames a glyph (`E206` in Jin's ending, `E205`/`E203` in others).
  `E203` in place of box 409's `E206` drew its 30 glyphs in 91 frames instead
  of 181, with the box's open and close unchanged.
- **The script waits for the typing.** After a box opens, the script goes
  on only when its text is typed:
  - `0xE3xx` then waits `xx` frames;
  - `0xE000` ends the scene's script, and the routine posts the next scene
    about 30 frames later (the screen fades meanwhile).

  So a scene change comes from the typing and waits of the box before it.
  Each scene's music track starts with its post (Jin's tracks 43 and 44
  start 9 and 29 frames before posts 18 and 19). Longer or shorter English
  moves the next scene and its music (END-010's build: post 17 +102
  frames).
- **The rule** (`tools/text/ending_timing.py`, the user's "Faster typing +
  move cues"):
  - English boxes that close on a cue type at 3 frames a glyph. Each run of
    cued boxes with no wait or scene end between them keeps its first open
    and last cue and shares its spare time evenly.
  - A box before waits keeps the Japanese typing + waits, through its
    interval and the waits.
  - A box before the scene end gets the interval closest to the Japanese
    typing.
  - What is left goes to the run before it, or else to slower typing (up
    to 16 frames a glyph).

  In Jin's ending every post, track start and the cast roll fall on the
  Japanese frames, and every English box holds its finished line 113 frames
  or more, except box 415. Box 415 comes right before the scene end, so it
  holds only while the screen fades, as the Japanese does. Dry runs on lists
  1-5 hold 45 frames or more, with scene ends within 5 frames.

Reproduce: `research/experiments/EXP-0048/README.md`, "Procedure".

## D-046: All six roster endings' English fits; the Saturn-only endings show only their posted boxes (`END-022`, `EXP-0049`)

- **Lists 6-8** (forced from the END-001 checkpoint) open only their
  posted scripts' boxes, 114 lines, and all show the shared cast roll
  (`data/text/ending_surfaces_others.json`).
- **Capacity.** The 100 English boxes of lists 0-5 take at most 3 rows and
  47 glyph cells, with no row wider than the Saturn's own lines of the same
  kind.
  - **Pairs:** 330 with the half-cell indent, which fits the 335 codes no
    line uses; 388 as is, which also fits the 930 codes no line that stays
    Japanese uses.
  - **Room:** the rows need 4,920-4,980 bytes. The roster's own lines hold
    4,232; the lines no ending is seen to show hold 42,844.
- **Correction to D-039's room.** Its 1,591 lines included 16 that Mary's and
  Bao and Mao's run-on boxes show (806-819, 888, 1007, D-043). The room is
  now the lines no box of any list 0-8 is seen to open: 1,575 lines. M7's
  rows are not in those 16 lines.

Reproduce: `research/experiments/EXP-0049/README.md`, "Procedure".

## D-047: All six roster endings in English (M8); the Saturn-only endings use the story font (`END-023`, `EXP-0050`)

- `tools.text.dialogue --endings data/text/m8_endings.json` builds one image
  from the untouched source with the M5 story and win quotes and the six
  roster endings in the official US arcade English:
  - 100 boxes and 330 pairs in `END.BIN`'s own table and `SE.DAT`'s font,
    with no `END.BIN` code sacrificed;
  - the half-cell indent; box 608 from slot 617;
  - END-011's rule, with typing time counting every code, spaces included.

  Two builds are identical. Forced from the END-001 checkpoint, every box
  of all nine endings draws as expected, and the scene changes and music
  stay within 6 frames of the Japanese. A cold boot plays in English, and
  a play state reaches Arieta's ending in English.
- **Lists 6-8 draw their ending text with `KANJI.BIN`**, which their runs
  load twice; they load no `SE.DAT`. So their Japanese shows the story's
  sacrificed glyphs, and any English box they share must use codes whose
  `KANJI.BIN` glyph is the same pair. The shared names 601/605 take the
  story's codes, plus one new pair at the story's 153rd sacrifice code
  (`0x8CF7`, line 1052), the user's choice. The M7 images showed those
  names garbled in list 8.
- **The renderer draws no glyph for `0x2020`** (two ASCII spaces), as for
  `0x8140`. Typing spends its interval on both.

Reproduce: `research/experiments/EXP-0050/README.md`, "Procedure".

## D-048: The five boot warnings, the save check that shows them, and its conditions (`BOOT-001`, `EXP-0051`)

- **One save check, once, before the title.** The start-up code
  (`0x060169D4`) calls `0x06036C3E` at about frame 1,370 of a cold boot.
  No other code shows a warning: the picture routine `0x06036DA8` has only
  the three `bsr` callers below, and no file holds its address.
- **Status.** `0x060367F4` starts the BIOS backup library and stores the
  status of the internal memory (`0x060DBA94`) and of a cart
  (`0x060DBA98`): observed 0 ready, 1 not connected (no save cart), 2
  unformatted.
- **Which picture** (`0x06036DA8` loads `WARNINGn.PIX`, n = R4, raw to
  VDP2 VRAM `0x20000`; each capture's VRAM there equals its file byte for
  byte):

  | Picture | Condition (cold boot, untouched image) | Meaning (agent's paraphrase) | After a button (CONFIRMED, `EXP-0055`) |
  | --- | --- | --- | --- |
  | `WARNING0` | the game's save fails its checksum (one data byte inverted) | the records could not be read; the old data will not be used | the game starts |
  | `WARNING1` | internal memory unformatted (status 2) | system RAM is not ready; initialize it in the Saturn's data screen | the multiplayer (BIOS) screen |
  | `WARNING2` | a save cart, unformatted (status 2) | cartridge RAM is not ready; initialize it | the multiplayer (BIOS) screen |
  | `WARNING3` | both unformatted | neither is ready; initialize both | the multiplayer (BIOS) screen |
  | `WARNING4` | no save, and less than 0x120 bytes free by the BIOS's count on every device (4 or 5 blocks free: 202 or 260 bytes) | records cannot be saved; free space or copy saves to a cart, then restart | the game starts (without saving) |

  With 6 blocks free, a normal save, or a normal save cart there is no
  warning. `WARNING1`-`3` wait forever in `0x06036754`, so only the first
  one met is shown (both unformatted shows `WARNING3` only).
- **Not producible here:** a read failure of an intact save (10 tries) also
  leads to `WARNING0`; internal status 1 cannot be made in Mednafen. Both
  use pictures already shown.
- **Buttons** were SUPPORTED only here (code and the screens' own words):
  a pad word written in RAM at the read was not seen by the CPU, probably
  because it reads the word from its cache. Confirmed by `BOOT-005`
  (`EXP-0055`): one real A press goes on into the game on `WARNING0` and
  `WARNING4`, and to the Saturn control panel (the BIOS routine at the
  `0x0600026C` vector, `0x0000186C`) on `WARNING1`-`3`.

Reproduce: `research/experiments/EXP-0051/README.md`, "Procedure".

## D-049: The boot warnings are whole 352 × 224 bitmaps on NBG1 with a palette from the program (`BOOT-002`, `EXP-0052`)

- **Location.** Each warning screen draws its own `WARNINGn.PIX` whole
  (`0x06036DA8`, raw to VDP2 VRAM `0x20000`). A test image with a marker in
  each file changed only its own screen's marker pixels under each
  condition, and nothing else, including a normal boot.
- **Format.** 512 bytes a row, one byte a pixel, values 0-15, no header;
  `WARNING0`-`3` 240 rows, `WARNING4` 256. Shown as VDP2 NBG1, the only
  layer on: a 256-colour 512 × 256 bitmap with bitmap palette 2 (colour RAM
  entries 512-527). Screen row = file row + 8 in Mednafen's 240-row
  screenshot; the display has 224 lines, so file rows 0-223 and columns
  0-351 are visible. All five redraw from the files with 0 differing pixels.
- **Palette.** 16 RGB555 colours copied from `CYBER.BIN` `0x06053AAC`
  (file offset `0x46AAC`) by `0x0600F334`, not from the files: 0
  transparent (black back screen), 1-7 grey to white, 8-9 red, 10-12
  yellow, 13-14 cyan, 15 black.
- **Room.** 352 × 224 pixels in those 16 colours, at the file's fixed size.
  The Japanese uses columns 24-328 and rows 20-210.

Reproduce: `research/experiments/EXP-0052/README.md`, "Procedure".

## D-050: The boot warnings in English, built from the untouched source (`BOOT-004`, `EXP-0054`)

- `tools.text.dialogue --boot-warnings data/translations/boot_warnings.json`
  (with the M8 options) builds M8 plus the five warnings in the approved
  English (`tools.text.boot_warnings`): only each file's visible 352 × 224
  pixels are redrawn, in the arcade letters and the program's 16 colours.
- Two builds are identical; every M8 output is unchanged; the 208 sectors
  that differ from M8 all lie in the five pictures; all sectors are valid.
- Under each condition of D-048 a cold boot shows its English picture with
  0 pixels differing from the built file; a normal boot is unchanged.

Reproduce: `research/experiments/EXP-0054/README.md`, "Procedure".

## D-051: Where the select and VS screens' name art is chosen (`LOC-001`, `EXP-0056`)

- The pilot select and the VS screen draw every name through the shared
  sprite-part routine (`0x060118E4` → `0x060113F0`, as D-040): an actor
  points at a 16-byte pose record whose word at +6 is the frame.
- **Pilot select** (`STG0A.BIN` at `0x06060000`): name records from
  `0x06065192`, frames `0x14`-`0x1C`, one per pilot (Jin, Santana, Mary,
  Arieta, Gawaine, Bao and Mao, Devilotte, Chiyomaru, Shade).
- **VS screen**: pilot names from `0x06087E98` (frames `0x02`-`0x0A`, via a
  word-offset table at `0x06087E72`); mech names from `0x06087A3E` (frames
  `0x0C`-`0x1C`, via a table at `0x06087A1C`; 16 names and one entry that
  draws a portrait).
- Writing a record's frame number from a saved state shows the matching
  name on the real screen. Every other surface seen is Latin or nameless;
  the US arcade's Latin forms are in `docs/names.md`.

Reproduce: `research/experiments/EXP-0056/README.md`, "Procedure".

## D-052: Name art storage; no Latin pilot or mech names on the disc's name banks (`LOC-002`, `EXP-0057`)

- **Pilot select:** raw 4 bpp art in `SELECT.VAD` (`0x17840`-`0x19B20`,
  nine names), which the select screen copies to VDP1 VRAM `0x20000`; bank
  56's parts address it directly.
- **VS screen:** compressed records in `PL3F_0.BIN` (loaded to WRAM-L
  `0x00200000`), one or two per name, `0x4324`-`0x5A..` for the nine pilots
  and `0x5E58`-`0x97..` for the sixteen mechs. A record's first word is type
  (bits 12-15), width / 8 and height; the names are type 2, a byte-coded
  format (`0x0601446C`) whose handlers 0-2 copy literal longs.
- A test image marking Jin's select name and two VS records, read by the
  game from saved states before the loads, changed exactly those names.
- Every frame of both banks was drawn (149 and 122): neither holds a Latin
  version of any pilot or mech name. Versus mode uses the same art.
  (Correction, D-059: bank 56 also holds a small Latin list of the four
  base bodies, the `BODY TYPE` panel's pattern `0x39460`.)
- Room: `SELECT.VAD` is full but for 1,440 bytes of slack; `PL3F_0.BIN` has
  288. The VS names take 20,804 bytes compressed (26,188 raw).

Reproduce: `research/experiments/EXP-0057/README.md`, "Procedure".

## D-053: The type-2 pattern format, the part list's end bit, and the Latin name art (`LOC-005`, `EXP-0060`)

- **Type-2 records** (decoder `0x0601446C`): word 0 = type 2 | width / 8 |
  height; word 1 = offset from its end to the literal stream; then control
  bytes, one operation each on 32-bit output longs: 0-15 copy n + 1 literal
  longs; 16-191 repeat the literal 4(n − 15) bytes back; 192-207 fill n − 191
  longs with the previous halfword; 208-255 copy 1-16 longs from the row
  above, at offsets R, R + 4 or R − 4 (R = row bytes).
  `tools/text/pattern_t2.py` decodes every bank-63 record, matching all 14
  name parts the game decoded, and encodes valid records.
- **Part words** (banks 56 and 63): screen x = 80 + (word 0 >> 6), y =
  origin + (word 1 >> 6); flips = (word 1 >> 2) & 3; word 1 bit 1 marks the
  frame's last part, and the routine stops there; pattern index = (word 1
  bit 0) << 16 | word 2. In bank 56 (8-byte parts) a size word of 0 skips
  the part.
- **Latin name art built** (`tools.text.dialogue --name-art`,
  `tools/text/name_art.py`): the nine select names get one 120 x 16 slot
  each in `SELECT.VAD`'s name block and one part each in `STG0A.BIN`'s table;
  the VS names are packed again in `PL3F_0.BIN` (12,316 of 21,712 bytes),
  one record per pilot, two per mech, with the model code moved after the
  name. All 34 names show as built.

Reproduce: `research/experiments/EXP-0060/README.md`, "Procedure".

## D-054: The Latin name art from cold boots; how a mech variant is chosen (`LOC-006`, `EXP-0061`)

- **Cold boots** of `data/regression/loc005_name_art.json`'s image, arcade
  mode with a second player and versus mode: the pilot select, `SET UP`
  and VS screens drew only built name parts (VDP1 sprites compared with the
  built `SELECT.VAD` block and decoded `PL3F_0.BIN` records), never a
  katakana one: Jin, Mary, Santana, Gawaine, Arieta, Bao&Mao, REPTOS
  RF-004, BLODIA BX-02, F·KILLER BEE F7900J, G·CYCLONE GP-02. The select
  screen read `STG0A.BIN`'s built part table from the disc.
- **`MACHINE SELECT` takes two choices per player:** a body type (up/down,
  then a button), then a variant (up/down among the body's mechs, shown by
  name under it), then a button. With FORDY and GULDIN, one down press gave
  KILLER BEE and CYCLONE.
- A second player who has joined holds the arcade-mode select until that
  player chooses; the match then has a `SET UP` screen.

Reproduce: `research/experiments/EXP-0061/README.md`, "Procedure" (cold
boots with presses: ask the user first).

## D-055: The Options screen, its settings block and the game's save (`OPT-001`, `EXP-0062`)

- **Screen:** `OPDEMO.BIN` at `0x06060000`; the menu (state word
  `0x060CFEE0`, table `0x06067624`) prints C strings with `0x0602A82A`
  (x cell, row, colour 31/20, string): labels at x 6, rows 8-20, `3M RAM
  MODE` at row 22 when `0x0606BE90` is set (a RAM cart), `PRESS START TO
  EXIT` at row 24; text row r is at screenshot y = 8r + 12. Cursor
  `0x0606BE8C`.
- **Settings block** `0x060D9290`-`9F` (16 bytes): +0 difficulty, +1 time
  limit, +2 short cut, +3 sound, +4 sound test; +5-15 unused. Each of
  +0-+4 shown by a write. `3M RAM MODE` is the long `0x06047ED4`, not
  saved.
- **Save** `CYBERBOTS01` (256 bytes): the block at +4-19; the last word is
  the 16-bit sum of bytes 0-253. Leaving Options saves (`0x06036A58`). A
  byte set in +5-15 is saved, summed and loaded back at boot (from states
  and a cold boot); with a stale sum the boot shows `WARNING0`. With no
  save, and after `DATA RESET`, +5-15 are 0. Only start-up code and the
  save's copy touched +5-15 in a whole session.

Reproduce: `research/experiments/EXP-0062/README.md`, "Procedure".

## D-056: How the game finds and loads files; room for new files (`OPT-002`, `EXP-0063`)

- **Directory:** the game copies the root directory at start-up into a table
  (`0x060DCB68`, 24-byte entries: FAD, size, flags, name; maximum 384,
  327 used) and finds files by name: a linear search (`0x060410C0`, names compared by `0x0603B550`) that stops after the entry whose byte 11 bit 0 is set, an end flag the directory loader puts on its last record (`0x060412E6`-`0x060412EC`). (Corrected 2026-11-06, `OPT-005` review: first recorded as a binary search.) The
  disc's last directory sector (LSN 27) has 1,532 bytes free.
- **Loader** `0x060385A0`(name, destination, maximum) writes exactly the
  file's size. `SELECT.VAD` is loaded to VDP1 VRAM `0x20000` at
  `0x06038CD6` (after `STG0A.BIN` to `0x06060000` by `0x060388FA`(10));
  `PL3F_0.BIN` to WRAM-L `0x00200000` by `STG0AS.BIN` code at
  `0x060605B6` (wait loop to `0x060605C2`). Each name occurs once on the
  disc.
- **Free sectors:** Track 01's last 150 sectors (LSN 43,643-43,792) are
  unused, valid Mode 1. A copy of `M3CB00A.BIN` placed there, with the
  game's directory entry pointed at it, loaded byte for byte (Mednafen).

Reproduce: `research/experiments/EXP-0063/README.md`, "Procedure".

## D-057: RAM free for new code, and the VDP1 command list's open end (`OPT-003`, `EXP-0064`)

- **Unused once `CYBER.BIN` runs:** `0x06055424`-`0x06055824` (1,024 zero
  bytes inside `CYBER.BIN`'s file, offsets `0x48424`-`0x48824`; loaded with
  it at boot) and `0x060DF8A8`-`0x060E0EA4` (5,628 bytes above its linker
  end). No master-CPU access and no `0xA5` canary change in 174 segments
  (an arcade session and ending checkpoints, cart in), none in a cold boot
  without a cart into a versus fight, and no static path (three independent
  reviews: literals, load destinations, DMA, indexed tables).
- **Not free:** `0x060E32E4`-`0x060E8000` is the VDP1 command list's tail:
  commands are appended at `0x060CE668` from `0x060E1000` with no bound and
  DMA'd to VDP1 each frame (`0x0600FF7C`); the game's high-water mark
  (`0x06047D30`) reached `0x2300`, the census edge. The zero runs from
  `0x06008000` to `0x0600D000` are task and interrupt stacks.

Reproduce: `research/experiments/EXP-0064/README.md`, "Procedure".

## D-058: The names switch: EXTRA OPTIONS, the hooks and the tail files (`OPT-005`, `EXP-0065`)

- **Menu** (`OPDEMO.BIN`): OPTION MODE's title on text row 2, its rows two
  higher, a row `EXTRA OPTIONS` (row 22, cursor 8; with no RAM cart 7 is
  skipped) drawn by a hook on the title call (literal `0x06062470`); state 3
  with the cursor on 8 runs the `EXTRA OPTIONS` sub-menu (literal
  `0x06062B3C`), which toggles the saved byte `0x060D9295`.
- **Art:** with the byte set, hook C copies the untouched part table to
  `0x0607CA18` before `STG0A.BIN`'s init (literal `0x06038DA0`), hook A
  loads `ZNAMES1.BIN` to `0x25C37840` after `SELECT.VAD` (literal
  `0x06038DC0`, `jsr @r4` at `0x06038CD6`), hook B loads `ZNAMES2.BIN` to
  `0x20200090` when the `PL3F_0.BIN` poll ends (literal `0x060606C0` in
  `STG0AS.BIN`). Code: `0x06055424`-`0x06055708`.
- **Files found:** two files added after `WARNING4.PIX` in the root
  directory are in the game's table after boot, the end flag moved to the
  last and the count `0x060DBC58` raised to 329.
- From saved states, byte 0 shows the Latin art and byte 1 the katakana on
  the pilot select and VS screens; saves with and without the byte load.

Reproduce: `research/experiments/EXP-0065/README.md`, "Procedure".

## D-059: The menu font is `FIX.BIN`; `KEND_1.BIN` is type 2; bank 56's Latin body list (`UI-001`, `EXP-0068`)

- **Menu font.** The menu print routine (`0x0602A82A`) draws `FIX.BIN`'s
  ASCII-indexed tiles (loaded raw to VDP2 VRAM `0x0`, 32 bytes a tile). From
  the Options state, zeroing tile `0x44` removed every small `D` of
  `OPTION MODE` and nothing else; a menu string rewritten to
  `tuvwxyz?!.,:'/()+=` drew those characters (comma and apostrophe as dots).
- **`KEND_1.BIN`.** Bank 16's cast-roll frames `0x1B6`-`0x1C9` use 29
  records. Each decodes with `tools/text/pattern_t2.py` (D-053), and each
  decoded picture is found byte for byte in the game's sprite shadow
  (WRAM-H `0x060E0000`+) during the roll. 13 are the Latin names (odd
  frames), 16 the Japanese names.
- **Bank 56** (`SELECT.VAD`) holds one Latin mech list: pattern `0x39460`
  (48 × 106, frame `0x35`, the `BODY TYPE` panel, stored mirrored) lists the
  four base bodies in a small plain font. This corrects D-052's "neither
  holds a Latin version of any pilot or mech name" for bank 56; the VS name
  banners are still katakana only.

Reproduce: `research/experiments/EXP-0068/README.md`, "Procedure".

## D-060: The VS caption: one row in a fixed banner; the US arcade skips it by region and has no English for it (`UI-003`, `EXP-0069`)

- **Saturn storage.** Each caption box (`0x0609CC22`[pilot × 10 + stage])
  has one record entry and the header `0000 0080 0058 0010`; its line is
  `STG0AS.BIN` text (box 496: `0x0607526C`, file `0x1526C`, 12 cells), in
  the story's font and code table. From a saved state, replacing the line's
  first code in RAM changed only the caption's first cell.
- **Room.** The banner is fixed art about 222 pixels wide; the text starts at
  x 96 in 14-pixel cells, so 13 cells fit inside it (a 16-cell line draws
  past its right edge). Records with two or four entries show only the first
  row (four entries: pixel-identical to the control).
- **Arcade.** In both `cybotsu` and `cybotsj` the VS setup at `0x0D436`
  creates the caption object (type `0x35`) only when `0xFF6A30` ≠ 3 and the
  region byte `0xFF80A0` is 0. Its drawer (`0x116F2` `cybotsu`, `0x116DA`
  `cybotsj`) reads only the Japanese table. Forcing the branch drew the
  Japanese caption in `cybotsu` and removed it in `cybotsj`.
- **No official English.** In both sets, English slots 494-551 all point to
  one two-line record that is not a caption.

Reproduce: `research/experiments/EXP-0069/README.md`, "Procedure".

## D-061: The ruined-city signs are raw NBG2 tiles of `ST00_FNT.BIN`; the US arcade blanks them by region (`UI-002`, `EXP-0070`)

- **Saturn.** `ST00_FNT.BIN` is copied raw to VDP2 VRAM `0x19000` (VRAM
  equals the file byte for byte at the sign). The signs (a red vertical
  banner, a white vertical banner with a small sign, a horizontal sale
  sign) are 24 of NBG2's 16 × 16, 4 bpp blocks (map `0x7A000`, palettes
  `0x41`/`0x42`); NBG2 stores its blocks column by column without reuse.
  Block offsets: `EXP-0070` `signs.json`.
  (Correction, D-062: the white banner's left edge is in block column 29
  too; the art changes 26 blocks, `EXP-0072` `store_blocks.json`.)
- **Controlled changes.** From a saved state, zeroing the block at VRAM
  `0x38280` changed only white-banner pixels; a test image from the
  untouched source with `ST00_FNT.BIN` byte `0x1F20D` changed showed
  exactly two different pixels, in the white banner.
- **Arcade.** Both sets hold both versions of the building. For stage 0,
  when the region byte `0xFF80A0` is not 0, the map selector (`0x18832`
  `cybotsu`) uses a block list with blank-sign blocks, and the stage set-up
  (`0x156B6`) loads three US palette blocks. Forcing both branches made
  each set's tile RAM equal the other's, word for word. The US version has
  no English, only blank signs.

Reproduce: `research/experiments/EXP-0070/README.md`, "Procedure".

## D-062: The UI build: English captions and the SIGNS setting (`UI-006`, `EXP-0072`)

- **Captions.** `tools.text.dialogue --vs-captions --caption-touch 13`
  adds the 54 approved captions after the story, quotes and endings (their
  outputs unchanged): 23 new pairs (37 centred; half-cell shifts reuse
  pairs), on 10 codes no shown Japanese line uses and 13 that touch one
  shown line each of pilots 6-8 (the user's choice). The code table cannot
  grow: the lookup `0x0606E9E8` scans 39 rows. From a saved state each
  caption drew exactly its predicted glyph cells (54 of 54).
- **Stage tiles.** `0x060385FA` names the stage's tile file from the table
  `0x0605DADC` (`ST00_FNT.BIN` for stages 0, 15, 16) and loads it through
  `0x060385BA` (fights and attract `0x0603875C`, pilot select
  `0x06038CBA`); its division call (`0x060385E2`, literal `0x06038628`) runs
  with the file in VRAM.
- **SIGNS.** Hook S on that literal loads `ZSIGNS1.BIN` (ENGLISH) or
  `ZSIGNS2.BIN` (JAPANESE), each the 63,872-byte sign slice of
  `ST00_FNT.BIN`, to VDP2 `0x28D00` when `0x060D9296` is 1 or 2 and the file
  is `ST00_FNT.BIN`; the disc's `ST00_FNT.BIN` holds the blank signs. From
  the attract state, the city's VRAM slice equals each version byte for
  byte; another stage loads nothing. The `EXTRA OPTIONS` sub-menu has two
  rows (cursor byte `0x060E0EA0`); its input logic passes 108 of 108 cases
  on an interpreter, and its drawing was checked for every row and value.
- **Pad words** (`0x060CC00E`/`0x060CC01E` blocks, from the raw buffer at
  `*0x060CC008`): current `+4`, previous `+6`, pressed `+8`. The CPU reads
  them through its cache, so agent writes do not simulate presses.

Reproduce: `research/experiments/EXP-0072/README.md`, "Procedure".

## D-063: Every box classified by how it is reached; the arcade's dialogue readers (`TXT-010`, `EXP-0074`)

- The Saturn's scene interpreter (`0x0606E230`) never jumps, so a posted
  scene shows all its boxes. Of 1,074 boxes, 913 are in scenes known paths
  post, 81 are captions, 68 win quotes; box 555 (a win-quote scene
  `VICTORY.BIN`'s table never picks), box 609 (list 10, which nothing
  posts) and 10 boxes in no scene or table (63, 283, 290, 335, 494, 495,
  552, 553, 938, 1073) have no path. `data/text/reachability.json`.
- In play, `cybotsu` reads only its English dialogue table and `cybotsj`
  only its Japanese one (read taps: `0x11F6A`/`0x12014` and
  `0x11E7A`/`0x11F0E`, plus the caption at `0x116E8`). A third reader,
  `0x97236`, draws any slot of any table from two variables; it is not
  reached in play.

Reproduce: `research/experiments/EXP-0074/README.md`, "Procedure".

(Correction, `EXP-0075`: the arcade's list 7 is the location-test
thank-you screen, not speaker names, and a region test does pick its scene,
in the object's creator `0xEC78`; see D-064.)

## D-064: The arcade's only rare text is a location-test thank-you screen behind ROM flags; the Saturn dropped it (`TXT-011`, `EXP-0075`)

- ROM bytes `0x55B` and `0x561` (0 in `cybotsu` and `cybotsj`) are build
  flags: set either one in MAME's ROM region and the boot banner adds `LOCA
  TEST VERSION` or `SHOW VERSION`, and after the last fight the game skips
  the ending (`0xE464`) for a `THANK YOU FOR PLAYING!` screen (`0xEA42` ->
  `0xEB5A`). Byte `0x55A` is the region byte, copied to `0xFF80A0` at boot.
- On that screen the object type `0x93` posts list 7: scene 6 (slot 609)
  when the region byte is non-zero, else the scene for the ending number
  (scenes 0-5 all open slots 602-605). Forced in both sets on Jin's route:
  `cybotsu` opens 609 (one English "coming soon" message), `cybotsj` opens
  602-605 (a Japanese thank-you message) or, with the index set to 6, 609.
  The English and Spanish tables point slots 601-609 at one record.
- None of those Japanese lines is a Saturn line. The Saturn's list 10 opens
  the same box numbers (602-605, 609), which on the Saturn are speaker
  names (arcade 610-623, nine numbers down); no Saturn file posts it by
  constant. Saturn box 609 is arcade slot 618, which no arcade scene opens.

Reproduce: `research/experiments/EXP-0075/README.md`, "Procedure".

## D-065: The Saturn-only pilots: who, how they are reached, the unlocks, and their text (`SPECIAL-010`, `EXP-0076`)

- **Select ring.** The pilot cursor is the player record's `+0x2E2`
  (player 1 `0x060D02BE`); Left and Right follow nine (left, right) pairs
  at `STG0A.BIN` `0x060643C0`, one ring 0, 2, 1, 4, 5, 3, 7, 8, 6. Bottom
  row: lists 7, 8, 6. List 7 is three moves left of Jin. No pilot is locked.
- **Who** (forced on the select screen, agent-read): list 6 Princess
  Devilot (Devilotte), list 7 Chiyomaru, list 8 SHADE. List 7's opening
  narration names Tessan, a character of Chiyomaru's story, not a pilot.
- **Route.** From REF-005 state 4138, setting player 1's pilot bytes
  (`0x060D02B2`, `0x060D02BE`) to 6, 7 or 8 posts list 6 scene 18, list 7
  scene 0 or list 8 scene 0, and the stage byte reads 54, 63 or 72; list
  7's run repeated with identical screenshots.
- **Unlocks** (code): five saved bytes `0x060D9306`-`0x060D930A`, set by
  `END.BIN` (`0x060601C8`) when an ending finishes at difficulty 3 or
  higher (by pilot 6, 7, 8; all three; and with `0x060CFF01` = 0), fill
  the word table `0x060D9230`. A set word gives that Saturn-only pilot a
  free machine choice (otherwise mechs 12, 13, 11 are fixed) and adds a
  body to machine select; body 8 is mech 16, an Akuma-like mech whose VS
  name is kanji art with the model code `G-18EX` (forced; not in
  `LOC-004`'s sixteen).
- **Text** (`data/text/special_census.json`): 339 story boxes (636 lines),
  22 win quotes (32 lines), 27 VS captions and three endings (59 boxes,
  114 lines in `END.BIN`); about 9,500 Japanese characters. All reachable;
  one story line (661) and the ending boxes 1072, 601 and 605 are shared
  with the roster.

Reproduce: `research/experiments/EXP-0076/README.md`, "Procedure".

## D-066: No official English for the Saturn-only pilots beyond three shared lines (`SPECIAL-011`, `EXP-0077`)

- **Six pilots in the arcade** (both sets): the pilot select steps through
  a ring of pilots 0-5 (`(left, right)` pairs at `0xCE00`, read by
  `0xCD80`-`0xCDB8`); the scene scripts have eight lists (pilots 0-5, the
  48 win-quote scenes of 6 pilots, the thank-you screen); six ending
  dispatches (D-037); quotes for pilots 0-5 (D-030).
- **No counterpart.** Of the Saturn-only pilots' 809 lines, one matches an
  arcade line exactly (661, shared with the roster) and 67 partly, all short
  phrases inside unrelated arcade lines. No multi-line box (0 of 259)
  matches an arcade record line for line, while all 61 of Jin's do.
- Only `STG0AS.BIN` line 661 and `END.BIN` lines 1006/1010 (speaker names
  of boxes 601/605) have official English, and they are English on the disc
  already. The other 806 lines need a new translation.
  `data/text/special_official.json`.

Reproduce: `research/experiments/EXP-0077/README.md`, "Procedure".

## D-067: The whole English script fits the story font, the room and the ending timing (`SPECIAL-016`, `EXP-0081`)

- With lists 6-8 in English, no shown box of the story font stays Japanese,
  so all 1,246 codes (1,221 plus 25 table slots) are usable: the script
  needs 657 pairs (487 roster, 23 captions, 145 more for lists 6-8, names),
  322 of them on codes of Japanese characters, none visible. The roster's
  pairs, rows and caption pairs reproduce the build's counts exactly.
- Room: `STG0AS.BIN` 50,108 bytes for 43,036 of rows (7,072 spare);
  `VICTORY.BIN` and `END.BIN` over 40 KB spare each.
- `END.BIN`'s code table equals the story's except the story's last 6 added
  codes, which the build must add if lists 6-8's endings use them.
- `END-011`'s timing rule holds for lists 6-8's endings (shortest hold 42
  frames) after box 879's line was shortened (the user's choice).
- The unlockable mech 16 is ZERO-GOUKI in the game's own Latin list
  (`CYBER.BIN` `0x38C60`).

Reproduce: `research/experiments/EXP-0081/README.md`, "Procedure".

## D-068: The Saturn-only pilots in English: built and seen from saved states (`SPECIAL-017`, `EXP-0082`)

- `tools.text.dialogue --special ... --special-mech ... --max-sacrifice 330`
  builds lists 6-8's approved English into the UI image (two builds
  identical; the ten earlier references rebuild unchanged). 326 Japanese
  codes are taken, none shown.
- From saved states, every box draws its predicted cells: lists 6-8's 71
  story scenes (339 boxes), 68 win quotes, 81 captions and all nine endings;
  the roster's story and quote predictions are unchanged.
- Lists 6-8's own ending boxes must use story-font codes only: the roster's
  endings draw the same `END.BIN` codes from `SE.DAT`.
- The unlock mech's VS name is frame `0x79` (mech table `0x06087A1C`, entry
  16), whose frame-table end is a 0 terminator; it draws with another
  palette than the sixteen mech names (white = index 1, light blue = 2,
  shadow = 7, bar = 6). Under NAMES JAPANESE the original kanji return.

Reproduce: `research/experiments/EXP-0082/README.md`, "Procedure".
