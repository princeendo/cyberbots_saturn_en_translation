# EXP-0025: Pair Glyphs From the Arcade's Own Letters, Proven After a Cold Boot

Task: LAYOUT-001 (Phase C)
Status: DONE
Confidence: CONFIRMED

## Observation

The user chose pair glyphs (EXP-0024, 2026-11-02): two characters per 16×16
font cell, mixed case. The Saturn draws a cell every 14 pixels and reserves 60
cells per box (D-020). 310 table codes are used by no Japanese line (D-023).
The arcade's English dialogue font is in the arcade's graphics, drawn by the
routine at `0x11F5C` (D-010).

## Hypothesis

The arcade's letters can be captured from MAME and set two to a cell at a
7-pixel advance, using the Saturn font's own shades. With the pair glyphs
placed in unused code slots, and the test text in Jin's dead ending lines with
box 2's record given a third line, the M1 box shows the test text after a cold
boot. Japanese text drawn with the untouched glyphs is unchanged.

## Controlled Change

One image, built from the untouched source:
- `KANJI.BIN`: 48 glyph cells replaced;
- `STG0AS.BIN`: three test rows written into dead lines 752-777, and box 2's
  record given three entries.

The control is the original image, from the same state and on the same route.

## Prediction

Only the sectors of those glyph groups, those lines and that record change.
The box draws exactly the predicted cells. Shade's reply after it draws its
original Japanese cells, and the same box appears after a cold boot played to
it.

## Inputs and Provenance

- **Arcade:** `cybotsu` (REF-001), MAME 0.289. Test records are written to work
  RAM `0xFFF000`, which was all zero just before (dumped in each run).
- **Saturn files:** `STG0AS.BIN` and `KANJI.BIN` from
  `local/extracted/saturn_jp/`, SHA-256 checked against
  `references/saturn_jp/iso_listing.json`.
- **Saturn states:** REF-005 state `f00004138.mcs` (`3eb789da…`), and the M1
  control screenshot (`local/re001/control/step05.png`, EXP-0017) for the
  palette.
- **Arcade glyph capture:** `local/layout001/font/arcade_font.json`, SHA-256
  `e3a4b793…`. It is ignored: the arcade's glyph art is never committed.
- **Untouched source image:** all 63 components unchanged after the work
  (`local/logs/layoutc-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`timelines/`](timelines/) | MAME code sheets `codes-0`…`codes-6` (`codes-6` is punctuation), and the first record-based captures `slot-*` (superseded) |
| [`capture_font.py`](capture_font.py) | Glyphs cut from the code sheets |
| [`tools/font/pairs.py`](../../../tools/font/pairs.py) | New: loads the capture, narrows letters to 7 columns, maps arcade shades to Saturn values, renders pair cells, finds unused codes. Tests: `tests/unit/test_font_pairs.py` |
| [`build.py`](build.py) | The Phase C image, prediction and preview |
| [`replay_cells.py`](replay_cells.py), [`check_cells.py`](check_cells.py) | State replays that save the 60 glyph cells per step, and their check |
| [`cold_route.py`](cold_route.py) | Agent-driven cold boot to the M1 box (`EXP-0019/drive.py`) |

## Procedure

```bash
for k in 0 1 2 3 4 5 6; do
  mkdir -p local/layout001/fontcodes/$k
  MAME_TIMELINE=research/experiments/EXP-0025/timelines/codes-$k.txt \
    mame cybotsu -rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua \
    -snapshot_directory local/layout001/fontcodes/$k -cfg_directory local/mame_arcade/cfg \
    -nvram_directory local/mame_arcade/nvram -skip_gameinfo -nothrottle -video none \
    -sound none -seconds_to_run 200 -debug -debugger none
done
./invenv.sh python research/experiments/EXP-0025/capture_font.py local/layout001/font
./invenv.sh python research/experiments/EXP-0025/build.py \
  local/layout001/font/arcade_font.json build/layout001/phasec
./invenv.sh python -m tools.disc.sector \
  "build/layout001/phasec/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
S=local/ref005/session/states/f00004138.mcs
./invenv.sh python research/experiments/EXP-0025/replay_cells.py \
  "build/layout001/phasec/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" $S \
  local/layout001/phasec-rebuilt 100
./invenv.sh python research/experiments/EXP-0025/replay_cells.py \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" $S \
  local/layout001/phasec-original 100
for r in rebuilt original; do
  ./invenv.sh python research/experiments/EXP-0025/check_cells.py \
    local/layout001/phasec-$r build/layout001/phasec/prediction.json
done
./invenv.sh python research/experiments/EXP-0025/cold_route.py \
  "build/layout001/phasec/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/layout001/play2
```

18:58-19:30 local, 2026-11-02, the user present.

## Actual Result

### Capturing the arcade's letters

- **Forced records** (`slot-*` timelines): replacing slot 2 at `0x11F5C` with
  records that hold every character worked. But cutting characters out of
  running text failed, because each glyph's 1-pixel outline touches its
  neighbours. Slot 622 is drawn over the portrait, outside the box.
- **Writing the ROM** with the debugger had no effect. Instead, a breakpoint
  at `0x11F6E` (after the record pointer is loaded) points slot 2 at a test
  record in work RAM `0xFFF000`. That record holds every code from `0x01` to
  `0xEF`, each followed by a space (`0xF0`), 15 to a line. A fourth line
  overlaps the box's border, so 3 lines per sheet; sheet 6 holds the
  punctuation and the apostrophe `0xF8`.
- **Grid** (measured): characters advance 8 pixels and a space 5, so the
  sheet's glyphs are 13 apart from x = 132. Lines are 16 apart from y = 152.
- **Result:** 206 glyphs. All 60 characters of the English dialogue are
  captured, plus `Q`, `Z` and all ten digits, which no record uses. Codes
  `0x01`-`0x3F` also hold Spanish letters and symbols; codes above `0x7F` hold
  graphics.
- The first cut window reached into a wide neighbour glyph (`0x14`, a period,
  picked up pixels from `0x15`). The window is now 1 pixel left of the cell to
  its 8th column.

### Shades and shape

- **The arcade's text shades:** `#FFFFFF`, `#DDDDDD`, `#AAAAAA`, `#555555`, and
  a `#111111` shadow on a `#666666` box.
- **The Saturn's values,** measured on the M1 control screenshot: the 25 known
  cells (D-019) sit at sprite x = 116 + 14n and y = 164 + 16r (screen y is 8
  more than the VDP1 y). Values 9-13 draw as `#F0F0F0`, `#D0D0D0`, `#A0A0A0`,
  `#707070` and `#101010`, and 14 as `#808080`, on `#606060`. So the arcade's
  five shades map one to one onto values 9-13.
- **Width:** arcade letters are 7 pixels plus a 1-pixel shadow. At a 7-pixel
  advance, wide capitals and digits touched (a first preview showed `BROWN`
  running together and `?` reading as `2`). `pairs.narrow` removes the column
  most like its neighbour, so one column of a 2-pixel stem goes, and keeps
  the shadow column. The second preview separates every letter.

### Build

- **Pairs:** the test rows are 3 × 32 characters, using lower case, capitals,
  digits, `:` `!` `?` `,` `.` `-` `'` and `"`. They make 48 distinct pairs,
  placed in the glyph slots of the first 48 of the 310 unused codes. The table
  is unchanged.
- **Rows:** the three rows (codes, then a NUL, 4-byte aligned) start at
  `0x060742CC` (line 752); the last one is at `0x06074314`. They stay within
  the dead lines' room, `0x060742CC`-`0x060745A9`.
- **Record:** box 2's record has three entries: `FFFF`, `FFFF`, `0000`.
- **Changed sectors:** `KANJI.BIN` LSN 4,780-4,787 and 4,790-4,794; `STG0AS.BIN`
  LSN 22,578 (the lines) and 22,660 (the record). That is 15 in all, as
  predicted, and every one of the 43,793 sectors passes EDC/ECC.
- **Repeat build:** identical (Track 01 `2cea6c51…`); the other components
  equal the source.

### Replay from state 4138 (100 × 25 frames)

| Image | Test box: 48 predicted cells | Shade's reply: 25 cells, original glyphs |
| --- | --- | --- |
| rebuilt | **48** (step 62) | **25** (step 72) |
| original | 0 | 25 (step 70) |

On screen (agent-reviewed), the box shows the three rows across all 16 cells.
The last cell reaches the screen edge.

### Cold boot (agent-driven, 19:26-19:29)

- The route from a cold boot: Start pressed only when the title shows its logo
  and prompt, then the mode menu, then A three times (ARCADE MODE, Jin,
  Blodia) and A once more. Every key was sent: 5 presses logged with frames in
  `local/layout001/play2/log.jsonl`.
- **Screens** (screenshots every 2 s): loading, the narration in Japanese, the
  test box typing out and completed (`route12.png`), Shade's Japanese reply,
  the rest of scene 0, the VS screen with its Japanese caption, and the fight.
- **Pixel check:** the test box region of `route12.png` is pixel-identical to
  the replay's step 62 (crop `240x64+112+152` hashes `58725ebd`). Shade's reply
  equals step 72 in both its text and portrait regions (`20a75c3e`,
  `e0b89994`).
- **An earlier attempt** missed keys ("Mednafen is not frontmost") while
  another Mednafen (the MSHvSF session) was open. Its keys were not sent
  anywhere, and it was stopped. After the user closed the other window, the
  rerun above sent every key.

The source is unchanged.

## Conclusion

**CONFIRMED (LAYOUT-001 Phase C):**

- Pair glyphs made from the arcade's own captured letters, narrowed to 7
  pixels and shaded with the Saturn font's values, draw in the M1 box exactly
  as predicted: 48/48 cells. That holds after a cold boot, from an image built
  from the untouched source.
- The box shows 3 rows of 16 cells (32 characters each) through an extended
  record, from text placed in `STG0AS.BIN`'s dead ending lines.
- Japanese drawn with untouched glyphs is unchanged.

The route the user chose works with no code change.

## Uncertainty and Alternatives

- A fourth row needs the record moved (records hold 3 lines in place, D-023).
  None of the paired English needs one (EXP-0024).
- The 48 test pairs used unused codes only. Jin's English needs 353 pairs
  against 336 free codes (EXP-0024); `RE-003`'s compiler must close that gap.
- 7-pixel letters are a narrowed form of the arcade's 8-pixel font. The user
  has not yet seen them on screen; the preview and the screenshots are in the
  ignored `local/layout001/` and `build/layout001/phasec/`.
- The cold boot played only to the M1 box and the first fight.

## Reproduction

Run the procedure. Expect 206 glyphs captured, 15 changed sectors, 48/48 and
25/25 cells, and the cold-boot box pixel-identical to the replay's.
