# EXP-0026: Jin's Story in English, Built From the Source Image (M3)

Task: RE-003
Status: DONE
Confidence: CONFIRMED (M3)

## Observation

Jin's story is 17 scenes and 63 boxes (D-021). Each box pairs with an
official English record, slot for slot (D-022). Pair glyphs from the arcade's
letters work after a cold boot (D-024). The user's GO (2026-11-02) covers the
official English unchanged, and, if needed, the glyph slots of the rarest
Japanese characters (`docs/localization_policy.md`).

## Hypothesis

A compiler can turn each box's English record into pair-glyph rows and
records deterministically. An image built from the untouched source with them
then shows every one of Jin's boxes as predicted, and other pilots' Japanese
is unchanged except where a sacrificed glyph appears.

## Controlled Change

Two files, both changed by the compiler (`tools/text/dialogue.py`):
- `KANJI.BIN`: pair glyphs;
- `STG0AS.BIN`: new table codes, rows and box records.

The control is the original image, from the same states and forcing.

## Prediction

Every box of every forced scene draws its predicted cells; the original image
draws none of them. A cold boot played through the first stages shows the
English boxes. Pilot 1's Japanese boxes draw their original cells.

## Inputs and Provenance

- **Arcade English:** read from `cybotsu` at build time (the ROM zips in
  `local/arcade/`, the driver `local/mame_src/cps2.cpp`). The program image's
  SHA-256 is in the record.
- **Inputs from earlier experiments:** `data/translations/jin_pairing.json`
  (EXP-0023), `data/text/jin_boxes.json` (EXP-0022), and the arcade glyph
  capture `local/layout001/font/arcade_font.json` (EXP-0025; ignored).
- **Saturn files:** from `local/extracted/saturn_jp/`, checked against the
  listing.
- **States:** REF-005 `f00004138.mcs` (`3eb789da…`) for the forced scenes, and
  `f00006983.mcs` for the fight study.
- **Source image:** untouched; all 63 components unchanged
  (`local/logs/re003-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`tools/text/dialogue.py`](../../../tools/text/dialogue.py) | New: the compiler and build. Tests: `tests/unit/test_dialogue.py` |
| [`force_check.py`](force_check.py) | Each scene forced from state 4138; every box checked against the prediction |
| [`other_pilot.py`](other_pilot.py) | Pilot 1's scene shown on an image (scene list redirected after the load) |
| [`fight_dump.py`](fight_dump.py), [`ko_test.py`](ko_test.py) | Finding the opponent's vitality |
| [`play_two_stages.py`](play_two_stages.py) | Cold boot, pad keys, forced fight wins, cells saved per poll |
| `data/regression/re003_jin.json` | The regression reference |

## Procedure

```bash
./invenv.sh python -m tools.text.dialogue --pairing data/translations/jin_pairing.json \
  --font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp \
  --rompath local/arcade --out build/re003/jin --record data/translations/jin_story.json
./invenv.sh python -m tools.disc.sector \
  "build/re003/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
CUE="build/re003/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python research/experiments/EXP-0026/force_check.py "$CUE" \
  build/re003/jin/prediction.json local/re003/force
./invenv.sh python research/experiments/EXP-0026/force_check.py "$ORIG" \
  build/re003/jin/prediction.json local/re003/force-original --scenes 9
./invenv.sh python research/experiments/EXP-0026/other_pilot.py "$CUE" local/re003/pilot1-english 1 0
./invenv.sh python research/experiments/EXP-0026/other_pilot.py "$ORIG" local/re003/pilot1-original 1 0
./invenv.sh python research/experiments/EXP-0026/play_two_stages.py "$CUE" local/re003/play1
```

20:20-20:50 local, 2026-11-02, the user present.

## Actual Result

### The compiler and build

- **Rows:** 63 boxes become 137 rows of at most 32 characters, with at most 3
  rows (in place) and at most 47 cells per box.
- **Pairs:** 353 distinct pairs.
  - **Codes:** 310 are codes no Japanese line uses; 25 are new codes `0xF040`
    onward in the table's last row, which keeps its 0 terminator, because
    the lookup scans to a 0 word (`0x0606E9E8`, D-019).
  - **Sacrificed:** 18 are the glyph slots of the least-used Japanese
    characters, one script line each (3 copies), per the user's decision.
    They include the full-width `Ｅ` `Ｒ` `Ｙ` (`0x8264`, `0x8271`,
    `0x8278`). The 16 script lines that use a sacrificed code (203, 710, 712,
    770, 975, 1076, 1301, 1341, 1454, 1541, 1582, 1651, 1674, 1675, 1699,
    1701) will show a pair glyph instead until they are English. Line 770 is
    in Jin's ending.
  - **Why not shift rows:** pushing 43 rows right by one space would have
    brought the count down to 299 and spared every Japanese glyph. It was
    not used, because it would indent those rows by 7 pixels.
- **Room:**
  - **Kept lines:** lines 57 and 75 are also used by boxes 315 and 388 (other
    pilots), so their bytes are left as they are.
  - **Space used:** the rows take 3,992 of 4,196 bytes: Jin's other lines
    plus his dead ending lines.
  - **Records:** each box's record is rewritten in place (at most 3 entries).
- **Image:** 82 sectors changed in `KANJI.BIN` and `STG0AS.BIN`. All 43,793
  sectors pass EDC/ECC. Two builds are identical (Track 01
  `904402b6…3f01`).
- **Records:**
  - **Provenance:** `data/translations/jin_story.json` holds, for each box,
    its slot, the English record's address and SHA-256, its rows, cells and
    row addresses. It also holds the codes, the sacrificed codes and the
    sources' hashes, and no text.
  - **Regression:** `data/regression/re003_jin.json`.

### Every box, forced (from state 4138, 150 × 25 frames per scene)

**All 17 scenes; 63 of 63 boxes** match their predicted cells completely:

| Scenes | Boxes |
| --- | --- |
| 21, 0, 1, 2, 3 | 2, 4, 2, 4, 6 |
| 4-8 | 3 each |
| 9, 10, 11, 12, 13, 14, 15 | 8, 3, 5, 3, 4, 3, 4 |

Control: scene 9 forced on the original image matches **0** cells in each of
its 8 boxes.

The first run started from state 5208. It showed Japanese, because that state
was saved after `STG0AS.BIN` loaded, so its RAM keeps the old script; only
`KANJI.BIN` is reloaded per scene. The harness now starts from state 4138,
before the load.

### Winning fights by forcing

- Dumping work RAM every 30 frames through a fight with no input showed two
  fighter records, at `0x060CFFE0` (Jin) and `0x060D02D4` (the opponent). Their
  falling words at `+0x14` turned out to be **x positions**: zeroing the
  opponent's moved Shade across the screen.
- The pairs at `+0x44`, Jin's `0x060D0024` (152 falling to 12) and the
  opponent's `0x060D0318` (152), are the **vitality bars** in bar units.
  Zeroing the opponent's pair empties Shade's bar.
- The game ends a fight only on a hit or at time-out. With Jin's pair held at
  152 and the opponent's at 0, the fights ended at time-out in Jin's favour.
- Other candidates tried and rejected: `0x060D45D8`, `0x060D46D4`,
  `0x060D47D0`, and `0x060E1492`. Writing them changed nothing.

### Cold boot, played (20:35-20:42)

- **Route:** title, arcade mode, Jin, Blodia. It went from stage 0 through the
  fight into stage 1, through its fight into stage 2, and to its fight (154
  polls, stage and step logged in `local/re003/play1/poll.jsonl`).
- **Boxes seen complete** (cells against the prediction):
  - scene 21 (2/2), scene 0 (4/4), scene 1 (2/2), scene 2 (4/4) and scene 3
    (6/6);
  - scene 4: boxes 19 and 20, with box 18 caught mid-typing at 12 of 16
    cells. Its full match is in the forced run.
- **Screens** (agent-reviewed): the English boxes over the stage
  backgrounds, with portraits on both sides, as built.

### Other pilots' Japanese

Pilot 1's scene 0 was shown on both images: Jin's list was pointed at pilot
1's after the load, and the scene was forced to 0. Its boxes 66-69 (lines
126-132, which use no sacrificed glyph) draw their original Japanese cells
exactly on the English image: 26, 8, 27 and 21 cells, the same as on the
original.

The source is unchanged.

## Conclusion

**CONFIRMED (M3):** all of Jin's story dialogue is handled programmatically.
- A deterministic compiler turns the official arcade English, read from the
  ROM at build time, into pair-glyph rows and box records.
- An image built from the untouched source shows all 63 boxes exactly as
  predicted.
- A cold boot played through two fights shows them in the game.
- Other pilots' Japanese is unchanged, except for the 16 recorded lines that
  use a sacrificed glyph.

## Uncertainty and Alternatives

- Line breaks are the compiler's word wrap at 32 characters, not the
  arcade's own breaks (the box is narrower). The words are unchanged.
- The fight wins are forced: the vitality pair and time-out, not real play.
- Box 18 was checked in the forced run but caught mid-typing in the cold boot.
- `VICTORY.BIN` and `END.BIN` keep Japanese copies of Jin's lines; they show
  his ending (excluded) and an unknown screen. Sacrificed glyphs appear there
  too.
- Losing a fight or continuing was not tested with the English image.

## Reproduction

Run the procedure. Expect Track 01 `904402b6…3f01`, 63/63 boxes, 0 in the
control, and the pilot-1 cells equal on both images.
