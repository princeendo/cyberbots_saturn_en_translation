# EXP-0009: The Arcade Draws the Decoded Records; What Selects Them

Task: REF-004
Status: DONE
Confidence: CONFIRMED (on-screen records, selection variable, table per region byte, codes `09`/`0B`/`18`/`1C`); HYPOTHESIS (script table meaning, `($AD,A5)`, endings)

## Observation

`EXP-0008` decoded 530 English records behind a 624-slot table at
`0x0B33AA`, with four codes read only from context, and Spanish and Japanese
tables of the same layout. Whether the arcade draws these records, what
selects one, and which table a region shows were not observed.

## Hypothesis

When the US set shows story dialogue, it reads slot N of the English table
and draws record N's text in a dialogue box; a RAM variable holds N; the
region byte decides the table.

## Controlled Change

Headless MAME 0.289 runs of the untouched sets with a frame-timed input
script (`tools/reference/mame_timeline.lua`): coin, start, two confirms, then
no input. Runs 4 and 5 add MAME debugger breakpoint actions that replace the
slot number passed to the draw routine; nothing else changes.

## Prediction

Reads of the English table coincide with on-screen boxes showing the decoded
records; a write to one RAM word carries each slot number; the Japanese set
reads only the Japanese table; forced slots show the four unknown codes as
glyphs.

## Inputs and Provenance

Sets in `local/arcade/` (`references/arcade/manifest.json`); driver pin
`a8c09ef8…1602`; decoded text from `tools/reference/cybots_text.py`
(`local/ref003/`, ignored).

## Tools and Environment

MAME 0.289 (Homebrew), `-nothrottle -video none -sound none`, project-local
`-cfg_directory`/`-nvram_directory` under `local/mame_arcade/`;
`tools/reference/mame_timeline.lua` (`logreads`, `logwrites`, `dump`,
`snap`, `press`, `debug`). Disassembly through MAME's own debugger run
headless (`-debug -debugger none`, debugger command `dasm`) on the decrypted
`cybotsud` image, whose code addresses match `cybotsu`. No new tool was
installed or downloaded.

## Procedure

Timelines are in [`timelines/`](timelines/) (paths point to the ignored
`local/ref004/`). Each run:

```bash
MAME_TIMELINE=research/experiments/EXP-0009/timelines/runN.txt \
  mame SET -rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua \
  -snapshot_directory local/ref004/runN/snap \
  -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram \
  -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 200
```

(Runs 4 and 5 and the `dasm` runs add `-debug -debugger none`.)

1. Run 1 (`cybotsu`, attract only, 9,000 frames): read taps on all three
   tables and their records; a snapshot every 30 frames.
2. Run 2: coin (frame 600), Start (720), Button 1 (1020, 1320), then no
   input to frame 4800.
3. `dasm` of `0x11E00`-`0x121FF`, `0x11C80`-`0x11D9F`, `0x97200`-`0x9727F`;
   search of the program for calls to the draw routine and loads of the
   table addresses.
4. Run 3: run 2 plus `logwrites 0xFF2F7A` and dumps of `0xFF8000`-`0xFF80FF`
   at frame 2800.
5. Run 4: run 3 plus breakpoints at `0x11F5C` replacing slots 2-5 with 610,
   475, 154, 561 (records with `09`, `0B`, `18`, `1C`).
6. Run 5: slot 0 replaced with 561 (slot 0 is drawn on an empty screen).
7. Run 6: run 2's route in `cybotsj` and `cybots`.

## Actual Result

- **Run 1:** no read of any dialogue table in 150 s of attract mode; the
  snapshots show logos, warnings, mech schematics, demo fights and rankings,
  no dialogue.
- **Run 2:** only the English table is read (375 read lines; Spanish and
  Japanese 0). The reader at PC `011F6A` reads slots 0, 1, 2, 3, 4, 5 at
  frames 2733, 2929, 3231, 3461, 3601, 3727. Snapshots after each read
  (agent-reviewed) show exactly those records being typed into a dialogue
  box: the story introduction (slots 0-1, box alone on black), then a
  pre-fight exchange between Jin (box right of his portrait) and Shade (box
  left of his). Snapshot `cybotsu_f02800.png` SHA-256 `78060562…`.
- **Code** (decrypted image):
  - `0x11CC6`: a task pointer at `-$7DFC(A5)`; a script table at `0x12150`
    indexed by the task's bytes `$15` and `$19`; script words `E0xx`-`E8xx`
    and `Fxxx` are commands, any other word is a slot number.
  - `0x11D48`: `move.w D0,-$5086(A5)` stores the slot; then
    `tst.b $A0(A5)`: 0 → Japanese table `0x0A310A`; 6, 10, or 8 with
    `$AD(A5)` set → Spanish `0x0AB956`; otherwise English `0x0B33AA`;
    `bsr 0x11F5C`.
  - `0x11F5C` (draw): slot × 4 → pointer → record; header word 0 is an
    offset into RAM buffers `0xFF2586` and `0xFF2BB6`, word 1 plus `0x40` the
    X position, word 2 the Y position, word 3 an attribute; then characters
    to `00`, `FF` a line break.
  - A second reader at `0x97222` chooses among the same three tables by a
    word at `-$44D0(A5)` (1 English, other nonzero Spanish, 0 Japanese);
    its use is not observed.
- **Run 3:** `0xFF2F7A` (`-$5086(A5)` with A5 `0xFF8000`) is written by PC
  `0x011D48` with exactly the slot numbers and frames of run 2 (0 @ 2733,
  1 @ 2929, 2 @ 3231, 3 @ 3461, 4 @ 3601, 5 @ 3727), and with `0x8000` +
  the previous slot between them. Region byte `0xFF80A0` = `0x02` (US).
- **Run 4:** the replacements took effect (slots 610, 475, 154, 561 read at
  3231, 3305, 3409, 3607). Agent review of the boxes: `09` is drawn as `:`
  ("Jin:", a speaker label), `0B` as `-` (in "Good-bye"), `18` as `"` on both
  sides of a phrase. Slot 561 was drawn at its own header position over the
  previous text and is illegible.
- **Run 5:** slot 561 in place of slot 0 is legible: a centered single line
  ending with `1C` drawn as a period. All 24 slots holding `1C` (552-582,
  in pairs) share Y `0xB8` and an X that shrinks as the line grows, i.e.
  centered one-line records.
- **Run 6:** `cybotsj` (region byte `0x00`) reads only the Japanese table
  (55 lines); its first box shows the same opening words as the Saturn
  script's first line (D-008). `cybots` (region `0x08`, `$AD(A5)` not
  inspected) reads only the English table and shows record 0.
- With the four codes added, `tools/reference/cybots_text.py` decodes 100%
  of the English table in all five sets (`data/arcade/dialogue_tables.json`).

## Conclusion

**CONFIRMED:** the arcade draws the decoded records. Slot N of the English
table is the record shown; the slot number comes from a dialogue script and
is stored at `0xFF2F7A` by `0x011D48` just before drawing; the region byte at
`0xFF80A0` chooses Japanese (0) or a Latin table (US 2 and EU 8 → English).
`09` `:`, `0B` `-`, `18` `"`, `1C` `.` are read from the arcade's own
rendering.

## Uncertainty and Alternatives

- Endings were not reached; whether they come from these tables (the second
  reader at `0x97222` is a candidate) is open (`END-001`).
- The script table's indexes (`$15`, `$19` of the task) are probably pilot
  and scene; not tested.
- `$AD(A5)` (Spanish in region 8) is not identified.
- The first Japanese arcade line and the first Saturn line share their
  opening; whether the scripts match line for line is `REF-006`.

## Reproduction

Run the procedure. Expect English reads only in `cybotsu` and `cybots`,
Japanese only in `cybotsj`, slot writes at `0xFF2F7A` matching the reads,
and the forced glyphs in runs 4 and 5. Evidence stays in the ignored
`local/ref004/`.
