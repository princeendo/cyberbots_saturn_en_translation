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
