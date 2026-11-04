# EXP-0035: Mary, Arieta, Gawaine, and Bao and Mao Pair Box for Slot

Task: PAIR-003
Status: DONE
Confidence: CONFIRMED

## Observation

Jin's and Santana's story boxes pair box for slot with the arcade English
(D-022, D-027). The M5 roster adds lists 2-5 (`RE-005`). `EXP-0027`'s
candidates had 0-4 boxes per pilot that were not slot for slot: Mary 1,
Arieta 0, Gawaine 4, Bao and Mao 4.

## Hypothesis

Lists 2-5 run the arcade's scene scripts for their story scenes, so each
Saturn box N shows where the arcade shows slot N, and the boxes that looked
irregular hold lines that other boxes also use.

## Controlled Change

None to either game. Forced scenes: in MAME, the interpreter's pilot byte
(`0x11CDA`) and the first scene (`0x11CEA`); on the Saturn, the scene-list
redirect and scene byte of `EXP-0029/force_check.py` from REF-005 state
4138, on the untouched image.

## Prediction

Story scenes have the same scripts in both games; every line's own slot
holds its Japanese, exact or edited; forced scenes show slot N in MAME and
box N's Japanese on the Saturn.

## Inputs and Provenance

- `local/ref003/cybotsu-maincpu.bin`, `cybotsj-maincpu.bin` (`REF-003`).
- `data/text/{mary,arieta,gawaine,baomao}_boxes.json` (`RE-005`).
- The untouched image; REF-005 state `f00004138`.
- MAME NVRAM base `local/win002/mame/nvram_base` (`eeprom` `7264edf9…`,
  `EXP-0032`), copied fresh into each run.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `research/experiments/EXP-0028/pair_pilot.py` | The pairing files (box = slot, REF-006 labels) |
| [`check_lines.py`](check_lines.py) | Each line against its own slot's Japanese line; shared-record slots explained |
| [`timelines/`](timelines/) | MAME forced scenes, pilot 2-5, two scenes each |
| `research/experiments/EXP-0029/force_check.py`, `EXP-0030/japanese_check.py` | Saturn forced scenes and their cells |

Python 3.13.13; MAME 0.289; Mednafen 1.32.1 with the agent interface.

## Procedure

```bash
for spec in 2:mary 3:arieta 4:gawaine 5:baomao; do p=${spec%%:*}; n=${spec#*:}
  ./invenv.sh python research/experiments/EXP-0028/pair_pilot.py \
    local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
    --pilot $p --boxes data/text/${n}_boxes.json --out data/translations/${n}_pairing.json
done
./invenv.sh python research/experiments/EXP-0035/check_lines.py local/ref003/cybotsj-maincpu.bin \
  data/translations/{mary,arieta,gawaine,baomao}_pairing.json
for t in research/experiments/EXP-0035/timelines/*.txt; do n=$(basename $t .txt)
  O=local/pair003/mame/$n; mkdir -p $O/snap $O/nvram; cp -R local/win002/mame/nvram_base/* $O/nvram/
  MAME_TIMELINE=$t mame cybotsu -rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua \
    -snapshot_directory $O/snap -cfg_directory local/mame_arcade/cfg -nvram_directory $O/nvram \
    -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 300 -debug -debugger none
done
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
F=research/experiments/EXP-0029/force_check.py; P=build/re007/js/prediction.json   # ignored with --control
for spec in mary:2:7 arieta:1:9 gawaine:5:10 baomao:2:11; do IFS=: read n a b <<< "$spec"
  ./invenv.sh python $F "$ORIG" $P local/pair003/saturn-$n --boxes data/text/${n}_boxes.json \
    --scenes $a $b --steps 100 --control
  for s in $a $b; do ./invenv.sh python research/experiments/EXP-0030/japanese_check.py \
    data/text/${n}_boxes.json $s local/pair003/saturn-$n/scene-$(printf '%02d' $s); done
done
```

2026-11-04, 11:20-11:52 local; no cold boots, no key presses (the Saturn
runs start from a saved state in the silent home).

## Actual Result

### Scripts

Every story scene of lists 2-5 has the same script in both games. The
scenes that differ are endings only: Mary 16-18; Arieta 16, 20, 27, 28;
Gawaine 16-19; Bao and Mao 16-22, 28.

### Pairing

| Pilot | Boxes | Lines | Against own slot | REF-006 labels not slot for slot |
| --- | --- | --- | --- | --- |
| Mary | 69 | 119 | 109 exact, 10 edited | box 140, line 258 `unaligned` |
| Arieta | 66 | 127 | 121 exact, 6 edited | none |
| Gawaine | 70 | 137 | 134 exact, 3 edited | box 292 line 144 (to slot 75), box 315 line 57 (to slot 30) |
| Bao and Mao | 72 | 136 | 125 exact, 11 edited | box 347 line 386 (to 213), box 370 line 538 (to 292), box 388 line 75 (to 38) |

- Each of those lines is its own slot's line: lines 144, 57, 386 and 538
  are identical to it (REF-006 pairs a line once, with its first box); line
  75 differs only in codes the map lacks; line 258 is the slot's second
  line with its punctuation changed (similarity 0.667, the lowest of the
  four pilots). So every line pairs with its own slot, and every slot has
  an English record: **no line needs a new translation**. D-011's
  "Saturn-only line 258" is corrected.
- Slots 283/284, 290/291 (Gawaine) and 335/336 (Bao and Mao) share a record
  in both languages; boxes 283, 290 and 335 are in no scene (as Santana's
  63/64, D-027).
- The box/slot/line triples equal `CAP-001`'s estimate, so its counts
  stand.

### Forced scenes (two per pilot)

| Pilot | Scene | MAME slots (`0xFF2F7A`) | MAME screenshot (agent-reviewed) | Saturn cells (untouched image) |
| --- | --- | --- | --- | --- |
| Mary | 2 | 138-141 | `p2-s2/snap/cybotsu_f03450.png` `0e28b41b…` (box 140's English) | 4 boxes, 54/54 |
| Mary | 7 | 163-168 | `p2-s7` f3780 `eb75b332…` | 6 boxes, 145/145 |
| Arieta | 1 | 203-207 | `p3-s1` f3300 `9fd8f6be…` | 5 boxes, 109/109 |
| Arieta | 9 | 236-240 | `p3-s9` f3510 `13db8558…` | 5 boxes, 95/95 |
| Gawaine | 5 | 291-294 | `p4-s5` f3330 `3229ca96…` (box 292) | 4 boxes, 94/94 |
| Gawaine | 10 | 315-318 | `p4-s10` f3150 `7472b425…` (box 315) | 4 boxes, 66/66 |
| Bao and Mao | 2 | 345-349 | `p5-s2` f3360 `176a3113…` (box 347) | 5 boxes, 88/88 |
| Bao and Mao | 11 | 385-388 | `p5-s11` f3450 `83f70603…` (box 388) | 4 boxes, 106/106 |

In each MAME run another scene came first (for Mary, slots 183-184), then
the forced scene. Saturn screenshots of boxes
140 and 388 (`saturn-mary/scene-02/step024.png`,
`saturn-baomao/scene-11/step046.png`) show the decoded lines.

The source image is unchanged.

## Conclusion

**CONFIRMED:** Mary's, Arieta's, Gawaine's, and Bao and Mao's story scenes
run the arcade's scripts, so each Saturn box N pairs with arcade slot N.
Every one of their 519 lines is its own slot's Japanese, exact (489) or
edited (30), and has the slot's US English. Forced scenes showed slot N in
MAME and box N's Japanese on the Saturn, two scenes per pilot.

## Uncertainty and Alternatives

- `edited` lines differ from the slot by punctuation or by codes the map
  lacks; their meaning against the English was not reviewed line by line.
- Only two scenes per pilot were forced; the rest rest on the scripts.

## Reproduction

Run the procedure; expect the label counts, slot sequences and cell counts
above.
