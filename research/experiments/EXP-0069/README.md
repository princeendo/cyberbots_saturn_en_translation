# EXP-0069: The VS Captions: Storage, Room and the Arcade's English (UI-003)

Task: UI-003
Status: DONE
Confidence: CONFIRMED (the Saturn storage and room, by controlled changes;
the arcade's region branch, by forcing it both ways in both sets; the US
English slots' pointers, by reading both programs); UNKNOWN (when the two
other creators of the caption object run)

## Observation

`UI-001` (`EXP-0067`) left one Japanese surface outside the attract and the
endings: the VS chapter caption (boxes 496-549 for pilots 0-5, 1045-1071 for
pilots 6-8). `cybotsj` shows it; `cybotsu` shows none. `EXP-0032` read from
code that the arcade reader (`0x62D4C`) draws the Japanese table only and
that the US set has English records at these slots (SUPPORTED). The
ruined-city signs, found in the attract demo, belong to `UI-002`.

## Hypothesis

The US arcade has the caption code but skips it on a region test, and its
English slots 494-549 hold no caption translations. On the Saturn, a
caption is one row of `STG0AS.BIN` text in a fixed banner.

## Controlled Change

- Arcade (MAME 0.289, headless, no player beyond the timeline): read taps on
  the Japanese table's pointers and the region byte; then the caption branch
  at `0x0D442` forced each way by a debugger breakpoint that sets the PC.
- Saturn (untouched image, saved state, no keys): one RAM change per run to
  box 496's line or record.

## Prediction

- `cybotsj` reads the caption's Japanese pointer at the VS screen; `cybotsu`
  does not. Forcing the branch makes `cybotsu` draw the Japanese caption and
  removes it from `cybotsj`.
- Saturn: replacing the line's first code changes only the caption's first
  cell; a 16-cell line overruns the banner; extra record entries add rows.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Arcade sets | `cybotsu`, `cybotsj` (`local/arcade/`, `references/arcade/README.md`); MAME driver source `local/mame_src/cps2.cpp` |
| NVRAM | a fresh copy of `local/mame_arcade/nvram/<set>` per run |
| `cybotsu` listing | `local/win002/mame/cybotsu-0-c0000.asm` (`EXP-0032`) |
| `cybotsj` listing | `local/ui003/mame/cybotsj-0-c0000.asm` (this experiment, same method) |
| Saturn state | `local/ref005/session/states/f00006448.mcs` (before a VS screen) |
| `STG0AS.BIN` | untouched, `local/extracted/saturn_jp/` (SHA-256 in `captions_table.json`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`timelines/`](timelines/) with `tools/reference/mame_timeline.lua` | Coin, start, two button presses (Jin, Blodia), snapshots; `logreads`; `debug bpset` for the forced runs |
| [`caption_room.py`](caption_room.py) → [`caption_room.json`](caption_room.json) | Saturn: control, one-cell, 16-cell, two- and four-row variants of box 496 |
| [`captions_table.py`](captions_table.py) → [`captions_table.json`](captions_table.json) | Offline: every caption box's record, header, line address, file offset and cells; both sets' English pointers for slots 494-551 (numbers only) |

MAME 0.289 (`/opt/homebrew/bin/mame`); Mednafen 1.32.1 with the agent
patch; Python 3.13 via `./invenv.sh`.

## Procedure

```bash
E=research/experiments/EXP-0069
M="-rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua -cfg_directory local/mame_arcade/cfg -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 900"
# cybotsj listing (as EXP-0032 made cybotsu's)
printf '1 debug dasm local/ui003/mame/cybotsj-0-c0000.asm,0,c0000\n2 exit\n' > local/ui003/mame/dasm.txt
MAME_TIMELINE=local/ui003/mame/dasm.txt mame cybotsj $M -debug -debugger none -nvram_directory NV_COPY
# for each SET in cybotsu cybotsj, a fresh NVRAM copy, O=local/ui003/mame/<run>:
MAME_TIMELINE=$E/timelines/vs-SET.txt     mame SET $M -snapshot_directory $O/snap -nvram_directory $O/nvram
MAME_TIMELINE=$E/timelines/region-SET.txt mame SET $M -snapshot_directory $O/snap -nvram_directory $O/nvram
MAME_TIMELINE=$E/timelines/show-cybotsu.txt mame cybotsu $M -debug -debugger none ...
MAME_TIMELINE=$E/timelines/hide-cybotsj.txt mame cybotsj $M -debug -debugger none ...
# Saturn (about 2 min, no key)
./invenv.sh python $E/caption_room.py local/ui003/room
# offline
./invenv.sh python $E/captions_table.py --driver local/mame_src/cps2.cpp \
  --rompath local/arcade --out $E/captions_table.json
```

2026-11-06, 20:00-21:00 local. No cold boot.

## Actual Result

### The arcade

- **Same screen, same choice:** both sets reach the first VS screen with
  Jin and Blodia against Shade and R-Lightning (`cybotsu` frame 3872,
  `cybotsj` 3933). `cybotsj` shows the caption box; `cybotsu` none
  (`cybotsu_f03900.png` `6e906ec6…900a`, `cybotsj_f03960.png`
  `36e7dc7f…e10d`).
- **Read taps:** `cybotsj`'s caption drawer (`0x116E8`) reads pointer
  `0x0A38B6` = Japanese table `0x0A30F6` + 4 × 496 at frame 3933 (box
  496, Jin, stage 0). `cybotsu` reads its Japanese table (`0x0A310A`) not
  once in the whole run.
- **The code** (identical in both sets at these addresses):
  - the caption is object type `0x35` of the object table (`0x04E04A` in
    `cybotsu`, dispatcher `0x04E01E`), entry `0x62CFC` (`cybotsu`) /
    `0x62CE8` (`cybotsj`); its first step computes the box from the player
    block (`+0x510` pilot, `+0x52A` stage, or the second player's at
    `+0x910`/`+0x92A` unless `0xFF6A30` = 1), reads the word table
    (`0x62D9A` / `0x62D86`), and calls the drawer (`0x116F2` / `0x116DA`),
    which reads only the Japanese pointer table and has no region test;
  - the VS screen's setup at `0x0D436` creates that object only if
    `0xFF6A30` ≠ 3 and the region byte `0xFF80A0` (D-010) is 0:
    `cmpi.b #3,($6A30,A5)`; `beq`; `tst.b ($A0,A5)`; `bne $D454` (skip).
    The region read taps show both sets reading `0xFF80A0` at `0x0D43E` on
    that frame.
- **Forced** (breakpoint at `0x0D442` setting the PC):
  - `cybotsu`, PC to `0x0D444` (create): the drawer reads `0x0A38CA` =
    `0x0A310A` + 4 × 496 at frame 3872 and the screen shows the Japanese
    caption (`8befb269…4e49`);
  - `cybotsj`, PC to `0x0D454` (skip): no caption read and no caption
    (`9061796f…dbdd1`). Nothing else on either screen changed (agent-read).
- **Two other creators** of type `0x35`, `0x04BDF6` and `0x04C2C0` (with a
  type `0x42` object, no region test), are not traced. In these runs the
  drawer read the table only at the VS screen, and the `EXP-0067` attract
  runs showed no other caption; when they run is UNKNOWN.
- **The US English slots:** in both sets, slots 494-551 of the English
  table all point to one record (`cybotsu` `0x0BB4F6`, `cybotsj`
  `0x0BB4E2`; the same codes), stored right after slot 493's. It is a
  two-line dialogue-style line of 28 and 17 characters (header 80, 92, 168,
  14), not a caption (agent-read; no text committed). No other slot points
  to it. So the US set holds no English caption, and its code never draws
  one.

### The Saturn

- **Storage** (`captions_table.json`): every caption box has one record
  entry (one row) and the same header `0000 0080 0058 0010`; boxes 494 and
  496 share a record. The lines are 6-12 cells in `STG0AS.BIN`; box 496's
  line is at `0x0607526C` (file `0x1526C`, 12 cells). Drawn by the reader
  `0x0606CAE8` through the box routine `0x0606E6E0` and the typing routine
  (D-020) with the story font and code table (D-019; the pair glyphs of
  `EXP-0067` show it).
- **Controlled change** (`caption_room.json`, state 6448, pilot 0 stage 0,
  345 frames): replacing the line's first code with its second changed the
  caption's first cell only (pixels x 96-107, y 84-94 differ from the
  control). The only other difference, the blinking `PRESS START` prompt
  (x 240-335, y 12-27), also differs between the `rows2` and `rows4` runs,
  which change nothing in the caption: run timing, not the change.
- **Room:**
  - the banner is fixed art about 222 pixels wide (x about 65-287); the
    text starts at x 96 with 14-pixel cells and 11-pixel glyphs;
  - a 16-cell line draws all 16 cells (to x 320), past the banner's right
    edge: 13 cells fit inside it from the current start;
  - `rows2` and `rows4` (two and four entries) change nothing on screen
    (`rows4` is pixel-identical to the control): one row only;
  - with pair glyphs (D-024), 13 cells hold 26 Latin characters.

## Conclusion

Predictions met but one: extra rows do not show. The US arcade keeps the
caption code but skips creating it outside Japan; its drawer has only the
Japanese table, and the English slots hold one unrelated filler line. No
official English exists for the VS captions (code trace plus data, both
sets). On the Saturn a caption is one row of up to 13 cells inside a fixed
banner, stored as `STG0AS.BIN` lines.

## Uncertainty and Alternatives

- Room was measured on box 496 only; every caption shares the header, so
  the others are expected to be the same (SUPPORTED).
- The text's start (x 96) may come from header word `0x0080` or the
  routine; moving it, for up to 15 cells, is untested.
- Whether the dropped rows are drawn hidden or not drawn is not traced.
- The Spanish table's slots were not examined.
- Two other creators of the caption object are not reached; their screens
  are UNKNOWN.
