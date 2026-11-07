# EXP-0082: The Saturn-Only Pilots' English Built and Checked From Saved States (SPECIAL-017)

Task: SPECIAL-017
Status: DONE
Confidence: CONFIRMED (two identical builds; every new box and the roster's
seen drawing their predicted cells from saved states; all earlier
references rebuild). Cold boots: `SPECIAL-018`.

## Observation

`SPECIAL-013`-`016` approved the English of lists 6-8 (`special_list{6,7,8}.json`),
mech 16's name (`special_mech.json`) and a cap of 330 Japanese codes, and
showed it all fits (D-067). The build (`tools.text.dialogue`) knew only
arcade-paired English.

## Hypothesis

With the new translation added to the UI build's command, every new box,
quote, caption and ending box draws its predicted cells, the roster's text
stays as it was, and the unlock mech's VS name reads ZERO-AKUMA G-18EX.

## Controlled Change

The `ui007_ui_text.json` command plus `--special` (three files),
`--special-mech` and `--max-sacrifice 330`. Tool changes, all behind the new
options (the ten earlier references rebuild byte for byte):

| Tool | Change |
| --- | --- |
| `tools/text/dialogue.py` | `--special`: new story and quote boxes (`special_boxes`, slot -1), indented by half a cell against the roster's fixed pairs (`shift_rows_fixed`), records for them (`special_records.json`); the new captions merged into the caption set; the total of Japanese codes taken checked against `--max-sacrifice` (`special_budget.json`). `--special-mech` passes mech 16 to the name art. |
| `tools/text/ending.py` | `special=`: lists 6-8's own ending boxes get story-font codes only (`KANJI.BIN`, the story's code or a spare sacrifice code), kept out of the `SE.DAT` allocation; row variants chosen greedily (plain on a tie); lists 6-8 retimed by END-011's rule; their predictions in `KANJI.BIN` cells. |
| `tools/text/name_art.py` | `extra_mechs`: mech 16's VS name, frame `0x79` (the mech table `0x06087A1C` gives it; its frame-table end is a 0, so `parts_of` follows the last-part flag). The frame keeps its own part positions and flips; its art is drawn in its own palette (`EXTRA_FRAMES`, measured by `palette.py`). |

## Prediction

Two identical builds; every check below passes.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| The `ui007_ui_text.json` inputs | Unchanged |
| `data/translations/special_list{6,7,8}.json`, `special_mech.json` | The approved English |
| REF-005 states 384, 3070, 4138, 6448; `local/win002/saturn/post.mcs`; the END-001 checkpoint | Saved states (untouched image) |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| `research/experiments/EXP-0029/force_check.py` | | Story scenes forced, cells against `prediction.json` |
| [`devilotte_boxes.json`](devilotte_boxes.json), [`chiyomaru_boxes.json`](chiyomaru_boxes.json), [`shade_boxes.json`](shade_boxes.json) | `2c6b878f…`, `da5a4b9f…`, `1a174060…` | Lists 6-8's scene boxes (numbers), for `force_check.py` |
| [`check_quotes.py`](check_quotes.py) | `e0f9948a…` | Win quotes from the WIN-002 state, with the build's `VICTORY.BIN` changes and font written in |
| `research/experiments/EXP-0072/check_captions.py` | | All 81 captions |
| `research/experiments/EXP-0042/probe.py` + [`check_endings.py`](check_endings.py) | `16915f28…` | All nine endings played (ending number set by an on-hit write), cells against the predictions |
| [`check_mech.py`](check_mech.py), [`palette.py`](palette.py) | `b703188e…`, `4556e2d9…` | Mech 16 forced to the VS screen under both NAMES settings; palette colours read off screenshots |
| `research/experiments/EXP-0055/regress.py`, `EXP-0072/record_changes.py` | | Earlier references; the changed ranges |

Tool hashes: `tools/text/dialogue.py` `43164b45…`, `ending.py` `7c7af4c6…`,
`name_art.py` `022e9c22…`.

## Procedure

```bash
B=build/sp017; export MEDNAFEN_ALLOWMULTI=1
CMD="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent --rank staying \
  --max-sacrifice 330 --task SPECIAL-017 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --endings data/text/m8_endings.json \
  --boot-warnings data/translations/boot_warnings.json --name-art data/translations/name_art.json \
  --names-switch data/translations/names_switch.json --signs-switch data/translations/signs_switch.json \
  --vs-captions data/translations/vs_captions.json --caption-touch 13 \
  --special data/translations/special_list6.json --special data/translations/special_list7.json \
  --special data/translations/special_list8.json --special-mech data/translations/special_mech.json"
$CMD --out $B/a --ending-record-dir local/sp017/rec-a; $CMD --out $B/b --ending-record-dir local/sp017/rec-b
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin re007_jin_santana re008_roster \
  end010_jin_ending end011_jin_timing end023_roster_endings boot004_boot_warnings loc005_name_art \
  opt006_names_switch ui007_ui_text --out research/experiments/EXP-0082/regress.json
./invenv.sh python research/experiments/EXP-0072/record_changes.py --build $B/a --base build/ui006/b \
  --out research/experiments/EXP-0082/changes.json
CUE="$B/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"; E=research/experiments/EXP-0082
for n in devilotte chiyomaru shade; do ./invenv.sh python research/experiments/EXP-0029/force_check.py \
  "$CUE" $B/a/prediction.json local/sp017/force-$n --boxes $E/${n}_boxes.json --steps 100; done
# scenes still typing at step 100 (devilotte 3 4 14 15, shade 7): again with --steps 200
./invenv.sh python $E/check_quotes.py local/sp017/quotes --build $B/a <the 68 quote boxes>
./invenv.sh python research/experiments/EXP-0072/check_captions.py local/sp017/captions --build $B/a
for n in 0 1 2 3 4 5 6 7 8; do ./invenv.sh python research/experiments/EXP-0042/probe.py local/sp017/end-list$n \
  --cue "$CUE" --frames 14200 --step 5 --cells-until 9500 --onhit 06018E0C:060CFF7E=0$n --watch 060CFF7E:1; done
./invenv.sh python $E/check_endings.py $B/a local/sp017/endruns --out $E/check_endings.json             # lists 6-8
./invenv.sh python $E/check_endings.py $B/a local/sp017/endruns --lists 0 1 2 3 4 5 --out $E/check_roster_endings.json
for n in jin santana mary arieta gawaine baomao; do ./invenv.sh python research/experiments/EXP-0029/force_check.py \
  "$CUE" $B/a/prediction.json local/sp017/roster-$n --boxes data/text/${n}_boxes.json --scenes 1 --steps 100; done
./invenv.sh python $E/check_mech.py local/sp017/mech --build $B/a
./invenv.sh python $E/palette.py local/sp017/mech
```

2026-11-07, local. No cold boot, no key.

## Actual Result

- **Builds:** A and B byte-identical (Track 01 `f6789cae…`, cue
  `9f1248ad…`). Story: 743 boxes, 620 pairs, 41,020 of 42,320 bytes of room;
  quotes 68 boxes, 2,248 of 40,392 bytes; captions 81. Japanese codes taken
  (`special_budget.json`): 285 by the story, 25 by lists 6-8's endings, 16 by
  the captions: **326 of 330**.
- **Earlier references:** all ten rebuild with every hash equal
  (`regress.json`; the three with name art again after the palette fix,
  `regress_names.json`).
- **Changes** (`changes.json`, hashes only; against the UI build): runs in
  `STG0AS.BIN` 618, `KANJI.BIN` 552, `SE.DAT` 201, `END.BIN` 100,
  `VICTORY.BIN` 51, `PL3F_0.BIN` 3.
- **Roster unchanged in what it shows:** the 450 roster story and quote boxes
  have exactly the UI build's predicted cells. Ending box 605 ("Gawaine:")
  now takes 4 cells, not 5 (a row variant needs no new pair now), and 4 of
  the 54 roster captions moved half a cell (the centring weighs 27 more
  captions); the words are unchanged.
- **Story** (`check_story.json`): lists 6-8, **71 of 71 scenes, all 339
  boxes** draw their predicted cells (five long scenes needed 200 steps).
  Roster: one scene per pilot, all boxes (`check_roster_story.json`).
- **Win quotes** (`check_quotes.json`): **68 of 68** (46 roster, 22 new).
- **Captions** (`check_captions.json`): **81 of 81**.
- **Endings:** lists 6-8 (`check_endings.json`) 15, 28 and 19 boxes opened,
  every one drawn in full (1072 blank); lists 0-5
  (`check_roster_endings.json`) 22, 24, 17, 27, 20, 28, all in full. The
  checker's window had to run to the later of a box's close word and the
  next opening: box 879's close word comes 11 frames after it opens, before
  its last cell is typed, and its cells stay drawn until frame 7760.
- **Mech 16** (`check_mech.json`): from state 4138 with the build's
  `CYBER.BIN` changes and directory written in (the state's own code hangs
  the built `STG0AS.BIN` at the VS screen, seen without them), body 8 and
  mech 16 show the VS screen with "ZERO-AKUMA G-18EX" under NAMES ENGLISH
  and the original kanji under NAMES JAPANESE (every changed `PL3F_0.BIN`
  byte lies in the range that setting restores). The first art drew dark
  red letters: frame `0x79` uses another palette. `palette.py` read both
  palettes off the screenshots (fits of 1.0); with the measured map the
  letters are white with light-blue edges on a blue bar (its bar is (0, 0,
  144) where the sixteen's is (0, 0, 192), the nearest it has), the model
  code in its own colours.

## Conclusion

Prediction met after one fix. The image has the Saturn-only pilots' story,
quotes, captions and endings and the unlock mech's name in English, and
everything the roster showed is unchanged in content.

## Uncertainty and Alternatives

- All checks are from saved states of the untouched image with the build's
  files written in where needed; cold boots of the real image are
  `SPECIAL-018`.
- The roster's story was sampled (one scene per pilot); its predictions
  equal the checked UI build's for all 450 boxes.
- The mech-16 banner's blue is a shade darker than the sixteen's.
