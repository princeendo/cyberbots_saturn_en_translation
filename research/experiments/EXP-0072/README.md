# EXP-0072: Building the UI Changes (UI-006)

Task: UI-006
Status: DONE
Confidence: CONFIRMED (captions: all 54 drawn with the predicted cells;
signs: VRAM equal to each version byte for byte; menu: every row and value
drawn, and the input logic on an interpreter, 108 of 108), from saved
states; real button presses and a cold boot are `UI-007`'s

## Part 1: The English VS Captions

### Observation

`UI-005` approved 54 English captions (`data/translations/vs_captions.json`),
centred, one row of 13 cells (D-060). The current build's story takes all
310 free codes, 25 new ones and 152 sacrificed Japanese codes.

### Hypothesis

The captions can be added after the story, quotes and endings, with every
earlier output unchanged, if their new pairs take codes no shown Japanese
line uses, and their rows go into the story's left-over room and the
captions' own lines.

### Change

`tools/text/vs_captions.py` and `tools.text.dialogue --vs-captions
APPROVED --caption-touch N`:

- caption rows centred; each may move half a cell (one leading space more
  or fewer) where that reuses pairs (as the story's `--indent`, CAP-001):
  37 new pairs centred, 23 with the shifts;
- new pairs take codes in the sacrifice order that no shown Japanese line
  uses (10), then up to `N` codes that do, cheapest first (the user,
  2026-11-06: "Take the 13 codes (Recommended)");
- rows first-fit in the story room's leftover, then the captions' own
  lines; each record's one row pointer changes.

The budget (`--budget`) reports the captions' new pairs, free codes, the
next codes' shown lines and the captions' own room (1,180 bytes).

### Prediction

Only caption ranges of `STG0AS.BIN` and caption glyph tiles of `KANJI.BIN`
change; every caption draws its predicted cells.

### Procedure

```bash
./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --out build/ui006/a \
  --endings data/text/m8_endings.json --ending-record-dir local/ui006/rec-a \
  --boot-warnings data/translations/boot_warnings.json --name-art data/translations/name_art.json \
  --names-switch data/translations/names_switch.json \
  --vs-captions data/translations/vs_captions.json --caption-touch 13
./invenv.sh python research/experiments/EXP-0072/check_captions.py local/ui006/captions   # about 10 min, no key
```

### Result

- [`caption_changes.json`](caption_changes.json): 54 rows, 23 new pairs
  (10 codes no shown line uses, 13 that touch one shown line each of
  pilots 6-8: lines 1054, 1117, 1187, 1217, 1247, 1335, 1352, 1433, 1590,
  1693 (two codes), 1762, 1837; boxes of lists 6, 7, 8 and pilot 7's
  caption box 1060). 200 ranges.
- Against `build/opt005/a`: `STG0AS.BIN` differs in 1,425 bytes and
  `KANJI.BIN` in 1,950, every one inside a caption range; every other file
  is identical.
- [`check_captions.json`](check_captions.json): from session state 6448,
  with the build's font, code table and caption ranges written in, each of
  the 54 captions drew only its own box, and its leading glyph cells
  (WRAM-H `0x060FE200`) equal the prediction: 54 of 54. The agent read all
  54 on screen: each reads as approved. The arcade letters' hyphen is a
  small raised dash and its double quote a small tick, as in the story.
- A first check run wrote no code table and showed blank cells for pairs
  on the story's new codes (`0xF040`+): the state's RAM holds the untouched
  table. With the built table written, all match.
- A first build counted staying lines from `STG0AS.BIN` after the story rows
  had overwritten dead ending lines (whose `END.BIN` copies lists 6-8 still
  show); it now reads the untouched file, and its touched lines match the
  budget's.

## Part 2: The SIGNS Setting

### Observation

`UI-005`'s design: an `EXTRA OPTIONS` row `SIGNS` (`BLANK` default,
`ENGLISH`, `JAPANESE`), saved in `0x060D9296`; the disc holds the blank
signs, a tail file the other versions. The names switch already fills 740
of the 1,024 free bytes in `CYBER.BIN` (D-057, D-058).

### Hypothesis

The stage tiles are loaded by one routine, `0x060385BA` (reached only from
`0x060385FA`, the stage-tile loader, called at `0x0603875C` for fights and
the attract and at `0x06038CBA` for the pilot select). Its call of the
division helper `0x06039228` (literal `0x06038628`, read only at
`0x060385E0`) runs once the file is in VRAM, so a hook there can load the
chosen sign version over the tiles.

### Change

- `tools/text/city_signs.py`: the blank and English art from
  `ST00_FNT.BIN` (banner writing colours to their base colour; the sale
  sign filled between its fitted border lines; stacked arcade capitals and
  `FIX.BIN` small capitals), on the store front's block map
  ([`store_blocks.json`](store_blocks.json), from `EXP-0070`'s render).
  26 blocks change, all in the slice `0x0FD00`-`0x1F680` (VRAM
  `0x28D00`-`0x3867F`).
- `tools/text/names_switch.py`: with `signs`, a two-row sub-menu (cursor
  row byte `0x060E0EA0`, in D-057's free range, reset on entry; Up/Down
  move it; on NAMES Right/Left/A/C toggle; on SIGNS Right/A/C step forward,
  Left back; labels and values in 31 or 20), and hook S on the division
  literal: when `SIGNS` is not 0 and the stage's tile file is
  `ST00_FNT.BIN` (`0x060463E0`, from the table `0x0605DADC`, stages 0, 15,
  16), it loads `ZSIGNS1.BIN` (ENGLISH) or `ZSIGNS2.BIN` (JAPANESE) to VDP2
  `0x28D00`. 1,012 of 1,024 bytes (`switch_changes.json`). The names-only
  build is unchanged.
- `tools.text.dialogue --signs-switch data/translations/signs_switch.json`:
  `ST00_FNT.BIN` blank on the disc, the two 63,872-byte slices as tail files
  (LSN 43,667 and 43,699, 32 sectors each; 62 tail sectors left).

### Prediction

The directory lists the four tail files; the menu draws both rows; for each
setting the city's sign slice in VRAM equals that version; other stages
load nothing.

### Procedure

```bash
./invenv.sh python -m tools.text.dialogue ... --names-switch data/translations/names_switch.json \
  --signs-switch data/translations/signs_switch.json \
  --vs-captions data/translations/vs_captions.json --caption-touch 13 --out build/ui006/b
./invenv.sh python research/experiments/EXP-0072/check_signs.py local/ui006/signs-check   # about 15 min
./invenv.sh python research/experiments/EXP-0072/check_menu_logic.py                      # offline
./invenv.sh python research/experiments/EXP-0065/check_states.py local/ui006/names --build build/ui006/b
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin ... opt006_names_switch
./invenv.sh python research/experiments/EXP-0072/record_changes.py
```

2026-11-06 to 2026-11-07, local. No cold boot, no keys.

### Result

- **Boot** (state 384, [`check_signs.json`](check_signs.json)): the
  directory lists `WARNING4.PIX`, `ZNAMES1.BIN`, `ZNAMES2.BIN`,
  `ZSIGNS1.BIN`, `ZSIGNS2.BIN`, the end flag on the last only; count 331;
  every `CYBER.BIN` change in RAM.
- **Menu** (state 27173, built bytes injected): both rows drawn; for each
  of six row/value combinations the cursor row's label and each row's
  value are lit as designed (agent-read screenshots).
- **Input logic** ([`menu_logic.json`](menu_logic.json)): the built
  handler, run on a small SH-2 interpreter for 2 rows x 2 NAMES x 3 SIGNS x
  9 buttons: 108 of 108 as designed (row moves, toggles, steps both ways,
  Start/B leave). Control: the names-only handler fails 48.
- **Signs** (state 25772, the attract to the city demo): with `SIGNS` 0, 1,
  2, hook S ran once each and loaded 0, 1, 1 times; VDP2 VRAM
  `0x28D00`-`0x3867F` equals the blank, English and Japanese slices
  respectively, byte for byte. With a tail file loaded the demo's timing
  shifts (its fight differs from the BLANK run's).
- **Another stage** (state 6448, stage index 1): hook S ran, loaded nothing.
- **Names** (`EXP-0065`'s check on this build): pilot select and VS counts
  equal `EXP-0065`'s exactly (1/2 select, 6/12 VS).
- **The user** saw the final art and the menu (store front rendered from the
  built files) and approved: "Approve both (Recommended)" (asked before the
  pictures reached them, then sent).
- **Captions on this build:** `KANJI.BIN` equals part 1's build, and
  `STG0AS.BIN` differs from it only in the hook-B literal (the names hooks
  moved), so part 1's caption check holds.
- **Builds:** two builds identical (Track 01 `1feadd13…655b`); against the
  `opt006` image only `CYBER.BIN`, `KANJI.BIN`, `STG0AS.BIN` and the new
  `ST00_FNT.BIN` replacement and tail files differ
  ([`changes.json`](changes.json): every range with its original and new
  SHA-256). All nine earlier references rebuild unchanged
  ([`regress.json`](regress.json)).
- **Method notes:** pad presses cannot be injected from the agent (the CPU
  reads `0x060CC016` through its cache; agent writes are not seen); a
  state's `savestate` must be taken while running.

## Conclusion

Both decided UI changes are built from the untouched source: 54 English
captions, and a saved `SIGNS` setting whose three versions reach the city's
tiles exactly. Real presses and a cold boot are `UI-007`.

## Uncertainty and Alternatives

- The menu's input is proven on an interpreter and the drawing on the
  emulator separately; `UI-007` presses the buttons on a cold boot.
- Stages 15 and 16 also use `ST00_FNT.BIN`; they were not reached.
- The pilot-select caller (`0x06038CBA`) also runs hook S; not observed.
- Loading a 32-sector tail file lengthens the city's load; the attract
  demo's play changes with it (no screen was seen to break).
