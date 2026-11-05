# EXP-0036: M5, the Roster's Story and Win Quotes in English From the Source Image

Task: RE-008
Status: DONE
Confidence: CONFIRMED

## Observation

The six roster pilots' story boxes pair box for slot (D-022, D-027, D-032)
and so do their win quotes (D-030). `CAP-001` chose the budget rule and the
gate approved up to 160 sacrificed codes (`TASKS.md`, 2026-11-04).

## Hypothesis

One build from the roster file puts every roster story box (`STG0AS.BIN`)
and win quote (`VICTORY.BIN`) in official English, changes no other byte,
and the game draws each box as predicted.

## Controlled Change

The image built from the untouched source by
`tools/text/dialogue.py --roster data/text/m5_roster.json --indent --rank
staying --max-sacrifice 160`: `STG0AS.BIN`, `VICTORY.BIN` and `KANJI.BIN`
replaced.

## Prediction

- The build needs 152 sacrificed codes (`EXP-0034`), fits its room, and
  changes only bytes it names.
- Every forced roster box draws its predicted cells; the original image
  draws none of them.
- In play, each roster pilot's boxes and a versus win quote show English.

## Inputs and Provenance

- The untouched image (`references/saturn_jp/README.md`); REF-005 state
  `f00004138` (forcing); `local/win002/mame` is not used.
- `data/text/m5_roster.json`; `data/translations/*_pairing.json`,
  `win_quotes_pairing.json`.
- The `cybotsu` ROM zips (`local/arcade`), the arcade font capture
  (`local/layout001/font/arcade_font.json`).

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/dialogue.py` | New `--roster`, `--quotes`: win quotes into `VICTORY.BIN` (its records, table copy, room); `OUT/changes.json` |
| [`untouched.py`](untouched.py) | Every changed byte against `changes.json`; `KANJI.BIN` cell by cell |
| `research/experiments/EXP-0029/force_check.py` | Forced story scenes |
| `research/experiments/EXP-0032/saturn_quote.py` | Versus selector state; forced quote boxes (now with cells) |
| [`check_quotes.py`](check_quotes.py) | Forced quote boxes' cells against the prediction |
| `research/experiments/EXP-0027/play_route.py` | Cold boots; new `--no-fight-keys` |

Python 3.13.13; Mednafen 1.32.1 with the agent interface.

## Procedure

```bash
C=(--font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp --rompath local/arcade)
R=(--roster data/text/m5_roster.json --indent --rank staying --max-sacrifice 160 --task RE-008)
./invenv.sh python -m tools.text.dialogue "${R[@]}" "${C[@]}" --out build/re008/roster --record-dir data/translations
./invenv.sh python -m tools.text.dialogue "${R[@]}" "${C[@]}" --out build/re008/roster-b --record-dir local/re008/rec-b
./invenv.sh python research/experiments/EXP-0036/untouched.py build/re008/roster
./invenv.sh python -m tools.disc.sector "build/re008/roster/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
./invenv.sh python -m tools.disc.hash_source --json local/disc_images/cyberbots_saturn_jp_2m/*
# regression with the default options (re003, re007): see "Actual Result"
CUE="build/re008/roster/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
P=build/re008/roster/prediction.json; F=research/experiments/EXP-0029/force_check.py
for n in jin santana mary arieta gawaine baomao; do
  ./invenv.sh python $F "$CUE" $P local/re008/force-$n --boxes data/text/${n}_boxes.json --steps 100
done
./invenv.sh python $F "$CUE" $P local/re008/force-jin-s9 --boxes data/text/jin_boxes.json --scenes 9 --steps 160
for n in jin santana mary arieta gawaine baomao; do
  ./invenv.sh python $F "$ORIG" $P local/re008/control-$n --boxes data/text/${n}_boxes.json --scenes 9 --steps 100
done
./invenv.sh python research/experiments/EXP-0022/box_list.py local/extracted/saturn_jp/STG0AS.BIN \
  --pilot 6 --out local/re008/list6-boxes.json
./invenv.sh python $F "$CUE" $P local/re008/japanese-list6 --boxes local/re008/list6-boxes.json \
  --scenes 1 --steps 100 --control
for files in build/re008/roster local/extracted/saturn_jp; do
  ./invenv.sh python research/experiments/EXP-0030/japanese_check.py local/re008/list6-boxes.json 1 \
    local/re008/japanese-list6/scene-01 --files $files
done
./invenv.sh python research/experiments/EXP-0036/versus_route.py "$CUE" local/re008/versus \
  554 556 557 ... 600 1023          # the 46 roster quote boxes, then a Saturn-only one
./invenv.sh python research/experiments/EXP-0036/check_quotes.py local/re008/versus build/re008/roster \
  554 556 557 ... 600 1023
RP=research/experiments/EXP-0027/play_route.py
for spec in jin: santana:right,right mary:right arieta:right,right,right,right,right \
    gawaine:right,right,right baomao:right,right,right,right; do n=${spec%%:*}; m=${spec#*:}
  ./invenv.sh python $RP "$CUE" local/re008/play-$n --moves "$m" --until-stage 2 --no-fight-keys \
    --select-wait 10 --move-wait 3
  ./invenv.sh python research/experiments/EXP-0036/play_summary.py $P local/re008/play-$n data/text/${n}_boxes.json
done
# reruns: play-santana2, play-mary2 with --max-minutes 35
```

2026-11-04, 12:00-17:00 local. Forced runs unattended in the silent home;
the 9 cold boots with the user present and asked first ("Yes, at ~14:30
(Recommended)", then "Yes, rerun both (Recommended)").

## Actual Result

### Compiler

- `--roster` reads the pilots' pairings (`data/translations/<name>_pairing.json`
  for `data/text/<name>_boxes.json`) and the win quotes; `--quotes` adds the
  quote boxes a built pilot's quote-table rows reach. Quotes share the pair
  pool, the indent and the sacrifice ranking (their lines count as
  replaced). Their rows go into `VICTORY.BIN`: its copies of the quote lines
  and of the stories' own lines (`VICTORY.BIN` shows only list 9, D-030),
  less lines another list-9 box shows; its quote records are rewritten
  through its box table `0x0607849C`; the new table codes go into its table
  copy too (file `0x1DB94`, equal to `STG0AS.BIN`'s). `OUT/changes.json`
  lists every byte range written and the glyph cells assigned.
- With the old commands, Jin + Santana and Jin alone rebuild to
  `re007_jin_santana.json` and `re003_jin.json` byte for byte (files,
  Track 01, prediction and records; a `quote_boxes` field first changed the
  records and is now written only for quote builds).

### Build

- 404 story boxes (851 rows) and 46 quote boxes; 487 pairs; 310 unused
  codes, 25 new, **152 sacrificed** (160 approved); 51 Japanese lines
  touched. Story text 23,904 bytes in 25,272 of room; quotes 1,324 in
  22,464.
- Two builds identical (all files, Track 01 `2c8505df…`, prediction
  `a5835892…`, records). 102 changed sectors, all 43,793 valid; the 63
  source files unchanged.
- Untouched-byte check: `STG0AS.BIN` 25,492 bytes changed, `VICTORY.BIN`
  1,438, all inside the written ranges; `KANJI.BIN` 487 cells changed, all
  assigned, and the rest of the file round-trips.

### Forced story boxes (built image)

| Pilot | Scenes | Boxes | Cells |
| --- | --- | --- | --- |
| Jin | 17 | 63 | 1,765 / 1,765 (scene 9's last box after 160 steps) |
| Santana | 20 | 64 | 1,466 / 1,466 |
| Mary | 18 | 69 | 1,793 / 1,793 |
| Arieta | 21 | 66 | 1,866 / 1,866 |
| Gawaine | 17 | 70 | 1,982 / 1,982 |
| Bao and Mao | 21 | 72 | 1,657 / 1,657 |

Every box of all 114 story scenes draws its predicted cells (10,529). With
100 steps scene 9 ended before Jin's box 40; with 160 it showed (234/234).
Control, the original image, scene 9 of each pilot: 0 of 905 cells.

### Japanese left

Saturn-only list 6, scene 1 (forced on the built image): all 72 cells as
predicted from the built files; against the original files box 896 stops at
cell 33 of 41, the cell of its sacrificed code (line 1541): the recorded
trade-off.

### Win quotes (versus cold boot, built image)

- Menu keys only (10): Jin against Arieta, Blodia against Blodia; the win
  held in RAM; `VICTORY.BIN` loaded at frame 21521; the selector halted with
  R8 = 0 (Jin) and R0 & 7 = 2.
- The game's own pick, replayed: box 599, the `VICTORY!` screen in English
  (agent-reviewed, `replay-21978.png`, `36c12f74…`), the line the arcade shows for slot
  599 (`EXP-0032`).
- Forced (box word of the scene's script): all 46 roster quote boxes and
  Saturn-only box 1023 shown; cells 615 / 615 (1023: its Japanese, 14/14).

### Play (cold boots of the built image, no keys during fights)

| Pilot | Run | Keys | Stages | Scenes posted | Boxes complete in play |
| --- | --- | --- | --- | --- | --- |
| Jin | `play-jin` | 5 | 0, 1, 2 | 21, 0-4 | 21 / 21 |
| Santana | `play-santana2` | 7 | 9, 10, 11 | 23, 0-4 | 19 / 21 |
| Mary | `play-mary2` | 6 | 18, 19 | 19, 0, 1, 20, 2 | 13 / 14 |
| Arieta | `play-arieta` | 10 | 27, 28, 29 | 22, 0-4 | 22 / 23 |
| Gawaine | `play-gawaine` | 8 | 36, 37, 38 | 20, 0-3 | 21 / 22 |
| Bao and Mao | `play-baomao` | 10 | 45, 46, 47 | 27, 0-3 | 21 / 21 |

- The incomplete boxes were caught mid-typing (1-4 cells short of 18-45);
  each drew in full when forced.
- `play-santana` stopped at MACHINE SELECT: one A was lost while a portrait
  loaded. `play_route.py` now presses A again if no scene is posted 45 s
  after the machine select (at most twice); the rerun needed none.
- Mary, twice (`play-mary`, `play-mary2`): stage 19, her stage 1, is a
  cockpit stage (step 22, not a fight); with no input it ends in GAME OVER
  (`play-mary2/p0300.png`, `299f26f9…`). The vitality hold (step 14) does
  not apply. The rerun was stopped at the title after the game over (its
  scene log taken from the agent's `events.log`).

Asked (2026-11-04): "Five roster pilots reached stage 2 of their groups in cold boots with their English boxes shown. Mary reached only her stage 1 (twice): stage 19 is a cockpit stage, not a fight, and with no input it ends in GAME OVER, so the RAM win doesn't apply there. Her English showed in play in 5 scenes (stages 18-19), and every one of her 69 boxes passed the forced check. How should RE-008 close?" The user's answer, verbatim: "Accept, record why (Recommended)".

The source image is unchanged.

## Conclusion

**CONFIRMED (M5):** one image built from the untouched source by
`dialogue.py --roster data/text/m5_roster.json --indent --rank staying
--max-sacrifice 160` shows all six roster pilots' story dialogue (404
boxes) and their versus win quotes (46 boxes) in the official US arcade
English. Every byte it changes is one the compiler names. Every story box
and quote box, forced, draws its predicted cells (10,529 and 615); the
original image draws none. In play, five pilots reach stage 2 of their
groups and Mary her stage 1, with English boxes, and a versus win shows an
English quote. The Japanese that stays draws as the trade-off records.

## Uncertainty and Alternatives

- Mary's stage 19 cockpit stage was not passed without input (accepted by
  the user).
- Play runs capture cells every 1.5-2 s, so a few boxes are caught
  mid-typing; the forced checks cover them.
- The half-cell indent was seen on screen only through the forced cells and
  play screenshots, not reviewed row by row.
- No real-Saturn boot (near a release only, the user's rule).

## Reproduction

Run the procedure. Expect the build hashes in
`data/regression/re008_roster.json`, the untouched-byte check passing, and
the cell counts above.
