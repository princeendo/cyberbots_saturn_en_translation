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
