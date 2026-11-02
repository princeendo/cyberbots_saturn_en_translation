# Known Unknowns

Open questions about Cyberbots, each with its current evidence and the smallest
experiment that would answer it. Close an entry by linking the task or
experiment that answered it.

| Question | Current evidence | Smallest discriminating experiment | Task |
| --- | --- | --- | --- |
| Is this image a verified Redump dump, and what does "(2M)" distinguish? | Header `T-1217G V1.002 19970219`; names and layout agree. redump.org refused the connection (2026-11-02). | Compare per-track size, CRC-32, MD5 and SHA-1 with the Redump entries for this title. | `ENV-007` |
| Which cartridge setting does the game need? | Peripheral field `JW`. Both siblings needed 4 MiB; no Cyberbots evidence. | Cold boots with `ss.cart` `none`, `extram1`, `extram4`. | `EMU-004` |
| Is the story dialogue drawn from the plain Shift-JIS strings in `END.BIN`, `VICTORY.BIN` and `STG0AS.BIN`? | About 1,763 strings per file, same opening lines, slightly different character counts (SESSION-0001). | Shift-JIS search of WRAM at a checkpoint with a known line on screen; then a one-character RAM change. | `TXT-001`, `DBG-004`, `RE-001` |
| Which of the three script copies does the game read, and when? | Each sits after a `SsCB` marker at a different offset. | Write breakpoint on the RAM text from a pre-load checkpoint, in a stage, after a win, and in an ending. | `DISC-001` |
| Is `KANJI.BIN` the dialogue font, and what is its format? | 163,840 bytes, which would fit 5,120 16×16 1-bit glyphs (arithmetic only). | Write breakpoint on a glyph cell while a line draws; decode the source rows. | `FONT-001` |
| Where and how does the arcade store its English dialogue? | Not as ASCII in the decrypted US program image. | Offset histogram of common words over each ROM, then a MAME read trace while a line draws. | `REF-003` |
| Does the Saturn renderer keep any arcade English or half-width path? | None known. Such a leftover saved XvSF all font capacity work. | Disassemble the text routine around region/language reads once `FONT-001` finds it. | `FONT-002` |
| What are the 21 named ISO entries past track 01 (`ARI_END1`, `BAO_END`, ...)? | Their LSNs fall in the audio tracks, as do the numbered entries `01`-`52`. | Map each entry's LSN to a CUE track start; listen to one. | `END-001` |
| Which surfaces show Japanese text? | Not yet inventoried. File names suggest story demos, warnings, select, continue, ranking and endings. | Several recorded captures per condition. | `REF-005` |
