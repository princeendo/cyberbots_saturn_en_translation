# Known Unknowns

Open questions about Cyberbots, each with its current evidence and the smallest
experiment that would answer it. Close an entry by linking the task or
experiment that answered it.

| Question | Current evidence | Smallest discriminating experiment | Task |
| --- | --- | --- | --- |
| Is this image a verified Redump dump, and what does "(2M)" distinguish? | Header `T-1217G V1.002 19970219`; names and layout agree. redump.org refused the connection (2026-11-02). | Compare per-track size, CRC-32, MD5 and SHA-1 with the Redump entries for this title. | `ENV-007` |
| ~~Which cartridge setting does the game need?~~ Partly answered: none for boot and attract (D-003). Still open: does play (Start, story, fights) check or use the cart, and what does the header's `W` mean? | `none` and `backup` give the same boot and attract screens with ~1 s timing shifts; 1 MiB and 4 MiB identical (`EXP-0002`). | One play session start (Start, mode select, first fight) with `ss.cart none`, compared with `auto`. | later `EMU` task, if it ever matters |
| Is the story dialogue drawn from the plain Shift-JIS strings in `END.BIN`, `VICTORY.BIN` and `STG0AS.BIN`? | About 1,763 strings per file, same opening lines, slightly different character counts (SESSION-0001). | Shift-JIS search of WRAM at a checkpoint with a known line on screen; then a one-character RAM change. | `TXT-001`, `DBG-004`, `RE-001` |
| Which of the three script copies does the game read, and when? | Each sits after a `SsCB` marker at a different offset. | Write breakpoint on the RAM text from a pre-load checkpoint, in a stage, after a win, and in an ending. | `DISC-001` |
| Is `KANJI.BIN` the dialogue font, and what is its format? | 163,840 bytes, which would fit 5,120 16×16 1-bit glyphs (arithmetic only). | Write breakpoint on a glyph cell while a line draws; decode the source rows. | `FONT-001` |
| Where and how does the arcade store its English dialogue? | Not as ASCII in the decrypted US program image. | Offset histogram of common words over each ROM, then a MAME read trace while a line draws. | `REF-003` |
| Does the Saturn renderer keep any arcade English or half-width path? | None known. Such a leftover saved XvSF all font capacity work. | Disassemble the text routine around region/language reads once `FONT-001` finds it. | `FONT-002` |
| What do audio tracks 42-62 (the per-pilot `*_END*` entries) hold: ending music or voiced narration? | Layout answered (D-002): one ISO entry per audio track; the 21 `*_END*` entries are tracks 42-62, two or three per pilot. Content not checked. | Listen to one track, or reach one ending and note which track plays. | `END-001` |
| Is cart RAM extraction valid, and how should the extractor read a 1 MiB cart? | State section `CART_EXTRAM` holds `LO`/`HI`, 512 KiB each; `mcs_extract`'s entry expects 4 MiB and refuses (`EXP-0005`). The stock debugger has no cart space to compare with. | Size the entry from the state, then compare a cart word read by the agent interface with the extracted copy. | only if cart RAM ever matters |
| Why do some unattended debugger runs lose keys or dumps silently? | `EXP-0003` run 1 lost an F9; `EXP-0004` run A lost both WRAM-L dumps; `EXP-0005` run G never opened the memory editor. Runs with keys spaced about a second apart, or with captures between keys, worked. | Repeat one failing script with only the key spacing changed. | not needed once the agent interface (`EMU-021`) replaces hotkeys |
| Which surfaces show Japanese text? | Not yet inventoried. File names suggest story demos, warnings, select, continue, ranking and endings. | Several recorded captures per condition. | `REF-005` |
