# EXP-0072: Building the UI Changes (UI-006)

Task: UI-006
Status: IN_PROGRESS (part 1, the captions, done; part 2, the SIGNS setting, next)
Confidence: CONFIRMED for the captions (all 54 drawn by the game with exactly
the predicted glyph cells, from saved states)

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
