# EXP-0030: Jin and Santana in English, Built From the Source Image (M4)

Task: RE-007
Status: DONE
Confidence: CONFIRMED (M4)

## Observation

The compiler builds any set of pilots from one pair-code pool (EXP-0029).
The user's GO (2026-11-03) covers Santana's official English as paired and
up to 73 sacrificed Japanese glyphs by the same rule
(`docs/localization_policy.md`).

## Hypothesis

One image built from the untouched source with Jin's and Santana's boxes
shows every one of their 127 story boxes as predicted, in forced scenes and
in play, and a third pilot's Japanese is unchanged except where a sacrificed
glyph appears.

## Controlled Change

The compiler (`tools/text/dialogue.py`) changes two files:
- `KANJI.BIN`: pair glyphs;
- `STG0AS.BIN`: new table codes, rows and box records.

The control is the original image, from the same state and forcing.

## Prediction

- Every box of every forced story scene draws its predicted cells; the
  original image draws none of them.
- A cold boot with Santana posts his block's scenes and shows his English
  boxes. A cold boot with Jin shows his first scenes as before.
- Mary's forced scene 0 draws her original Japanese, except box 131's
  sacrificed `0x8BC1`, which shows its pair glyph.

## Inputs and Provenance

- **Pairings and box lists:** `data/translations/jin_pairing.json`,
  `santana_pairing.json`; `data/text/jin_boxes.json`, `santana_boxes.json`,
  and `mary_boxes.json` (new: `box_list.py --pilot 2`).
- **Arcade English and font:** the ROM zips and
  `local/layout001/font/arcade_font.json` (ignored), as in EXP-0026.
- **State:** REF-005 `f00004138.mcs` (`3eb789da…`), before `STG0AS.BIN`
  loads, so the script in RAM is the image's own.
- **Source image:** untouched; all 63 components unchanged
  (`local/logs/re007-source-after.json`, equal to `re004-source-after.json`).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`tools/text/dialogue.py`](../../../tools/text/dialogue.py) | The build (`--pairing` twice, `--record-dir`, `--task RE-007`) |
| `research/experiments/EXP-0029/force_check.py` | Each story scene forced from state 4138, every box checked |
| [`japanese_check.py`](japanese_check.py) | Every box of a forced Japanese scene against given files (built or original) |
| `research/experiments/EXP-0027/play_route.py` | Cold boot, pilot chosen on the select screen, fights forced (D-025) |
| [`check_play.py`](check_play.py) | A play run's cells against the prediction, per scene |

Python 3.13.13; Mednafen 1.32.1 with the agent interface (D-007).

## Procedure

```bash
C="--font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp --rompath local/arcade"
J=data/translations/jin_pairing.json; S=data/translations/santana_pairing.json
./invenv.sh python -m tools.text.dialogue --pairing $J --pairing $S $C --out build/re007/js \
  --record-dir data/translations --task RE-007
./invenv.sh python -m tools.text.dialogue --pairing $J --pairing $S $C --out build/re007/js-b \
  --record-dir build/re007/rec-b --task RE-007
./invenv.sh python -m tools.disc.sector \
  "build/re007/js/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
./invenv.sh python -m tools.disc.hash_source --json local/disc_images/cyberbots_saturn_jp_2m/* \
  > local/logs/re007-source-after.json
CUE="build/re007/js/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
P=build/re007/js/prediction.json; F=research/experiments/EXP-0029/force_check.py
./invenv.sh python $F "$CUE" $P local/re007/force-jin --boxes data/text/jin_boxes.json
./invenv.sh python $F "$CUE" $P local/re007/force-santana --boxes data/text/santana_boxes.json
./invenv.sh python $F "$ORIG" $P local/re007/control-jin --boxes data/text/jin_boxes.json --scenes 9
./invenv.sh python $F "$ORIG" $P local/re007/control-santana --boxes data/text/santana_boxes.json --scenes 9
./invenv.sh python $F "$CUE" $P local/re007/mary-english --boxes data/text/mary_boxes.json --scenes 0 --control
./invenv.sh python $F "$ORIG" $P local/re007/mary-original --boxes data/text/mary_boxes.json --scenes 0 --control
for run in english original; do for files in build/re007/js local/extracted/saturn_jp; do
  ./invenv.sh python research/experiments/EXP-0030/japanese_check.py data/text/mary_boxes.json 0 \
    local/re007/mary-$run/scene-00 --files $files
done; done
./invenv.sh python research/experiments/EXP-0027/play_route.py "$CUE" local/re007/santana-play \
  --moves right,right --until-stage 2
./invenv.sh python research/experiments/EXP-0030/check_play.py $P local/re007/santana-play \
  --boxes data/text/santana_boxes.json
./invenv.sh python research/experiments/EXP-0027/play_route.py "$CUE" local/re007/jin-play --until-stage 0
./invenv.sh python research/experiments/EXP-0030/check_play.py $P local/re007/jin-play \
  --boxes data/text/jin_boxes.json
```

13:00-14:12 local, 2026-11-03, the user present for the cold boots.

## Actual Result

### The build

- **Codes:** 127 boxes, 260 rows, 408 pairs. 310 unused codes, 25 new codes
  (`0xF040` onward), and **73 sacrificed**, the approved number, by the same
  rule. The first 18 are Jin-alone's 18, in the same order, and every one
  of Jin's pairs keeps its code (the records' code lists are equal).
- **Room:** 7,316 of 8,088 bytes; kept lines 57, 75 and 144.
- **Image:** 85 sectors changed (76 in `KANJI.BIN`, 9 in `STG0AS.BIN`); all
  43,793 sectors pass EDC/ECC. Two builds identical: Track 01 `a63ba806…`,
  `STG0AS.BIN` `cfe0945a…`, `KANJI.BIN` `bc414e4a…`, prediction
  `dd4b1235…`, both records equal.
- **Rule 12:** `OUT/image/build_manifest.json` lists each changed sector with
  its original and modified SHA-256; the records list each box's row
  addresses and the sacrificed codes.
- **Records:** `data/translations/jin_story.json` (`59fda139…`) and
  `santana_story.json` (`ca1d93c9…`); regression
  `data/regression/re007_jin_santana.json`.

### Every box, forced (from state 4138, 150 × 25 frames per scene)

| Pilot | Scenes | Boxes matched completely | Cells |
| --- | --- | --- | --- |
| Jin | 21, 0-15 (17) | **63 of 63** | 1,759 |
| Santana | 0-15, 23-26 (20) | **64 of 64** | 1,462 |

Controls (original image): Jin's scene 9 matches 0 of 233 cells, Santana's
scene 9 0 of 178. A forced screen (agent-reviewed): Santana's scene 9 shows
his English in the arcade's letters.

### A third pilot: Mary

Mary's scene 0 (boxes 130-132), forced on both images; each run checked
against the built files and against the original files:

| Image | Built files' prediction | Original files' prediction |
| --- | --- | --- |
| English | 25/25, **28/28**, 24/24 | 25/25, **23/28**, 24/24 |
| Original | 25/25, 23/28, 24/24 | 25/25, 28/28, 24/24 |

Box 131's 24th character is `0x8BC1`, one of the sacrificed codes: on the
English image it draws its pair glyph, as recorded. Boxes 130 and 132 are
unchanged. The first prediction counted the full-width space `0x8140` as a
cell (EXP-0027's `check_first_box.py` did, but its boxes had no space); the
typing routine draws no cell for it, and `japanese_check.py` now skips it.

### Cold boot with Santana (14:01-14:09)

- **Route:** title, arcade mode, two moves right (the select screen shows
  Santana's portrait and name), the machine. Stage byte 9, 10, then 11:
  two forced fights won, into his third stage. Two key presses were refused
  while Mednafen was not in front; the route went on.
- **Posts:** 23, 0, 1, 2, 3, 4: block 1's order (EXP-0027).
- **Boxes:** every box of those six scenes matched completely (64-66,
  68-84), except box 67, caught mid-typing at 17 of 19 cells; its full match
  is in the forced run.
- **Screens** (agent-reviewed): his English beside his portrait over the
  stage.

### Cold boot with Jin (14:09-14:12)

- **Route:** title, arcade mode, Jin (no move), the machine. Posts 21 and 0;
  stage 0 into its fight. Four key presses were refused while Mednafen was
  not in front; the route went on.
- **Boxes:** all of scene 21 (2/2) and scene 0 (4/4) match completely, as
  in RE-003's cold boot.
- **Jin unchanged in effect:** all 63 of Jin's boxes predict the same cells
  as a Jin-only build, whose prediction is still RE-003's `394f745c…`.
- **Screen** (agent-reviewed): his English box beside his portrait, as
  before.

The source is unchanged.

## Conclusion

**CONFIRMED (M4):** one image built from the untouched source has Jin's and
Santana's story dialogue in official English. All 127 boxes draw as
predicted when forced; cold boots show Santana's first six scenes and Jin's
first scenes in play. A third pilot's Japanese is unchanged except for the
recorded sacrificed glyphs.

## Uncertainty and Alternatives

- The fight wins are forced (D-025).
- Santana's later scenes were checked forced, not in play.
- Box 67 was caught mid-typing in play.
- 62 lines of `STG0AS.BIN` (198 with the other files' copies) show pair
  glyphs until those pilots are English; Mary's box 131 is one.
- Endings and `VICTORY.BIN` are not checked.

## Reproduction

Run the procedure. Expect Track 01 `a63ba806…`, 127/127 boxes, 0 in the
controls, the Mary table, and the play checks above.
