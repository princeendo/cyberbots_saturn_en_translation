# EXP-0023: Jin's Boxes Pair Slot for Slot With the Arcade English

Task: PAIR-001
Status: DONE
Confidence: CONFIRMED (identical scene scripts; slot = box; English for every box; the REF-006 reader correction)

## Observation

Jin's story is scenes 21 and 0-15, boxes 0-62, Saturn lines 0-120 (D-021).
The arcade's dialogue script table is at `0x12150`. Its interpreter at
`0x11CC6` indexes it by two task bytes, stores each slot at `0xFF2F7A`, and
only then picks the language table (D-010, EXP-0009). REF-006 paired Saturn
lines with arcade lines by text alignment, which is evidence but not the
games' logic (D-011).

## Hypothesis

The Saturn port kept the arcade's scene scripts: for each of Jin's scenes,
the arcade names the same numbers as slots that the Saturn names as boxes.
So box N's official English is arcade English record N.

## Controlled Change

None to either game for the static part. In MAME, a debugger action changes
one value, the scene number, at `0x11CEA`, right after the interpreter reads
it. The control is the unforced run.

## Prediction

The decoded arcade scenes equal the Saturn's box lists. Forcing arcade scenes
4, 9 and 15 shows slots 18, 33 and 59 (the Saturn's forced first boxes,
EXP-0022), in English.

## Inputs and Provenance

- Arcade program images (decrypted, 68000 order, REF-003):
  `local/ref003/cybotsu-maincpu.bin` (SHA-256 `18e8827d…`) and
  `cybotsj-maincpu.bin` (`2d1e6b25…`). Sets verified in
  `references/arcade/manifest.json` (REF-001).
- Arcade English decode `local/ref003/text-cybotsu.json` (ignored), used for
  counts and the agent's review only.
- `data/text/jin_boxes.json` (EXP-0022) and `data/text/saturn_arcade_pairing.json`
  (REF-006; regenerated here).
- Saturn source image unchanged (`local/logs/pair001-source-after.json`).
  MAME 0.289.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/reference/mame_timeline.lua` | MAME runs: inputs, slot write log, script read log, snapshots, debugger actions |
| [`timelines/`](timelines/) | The unforced run and the scenes 4, 9 and 15 runs |
| [`pair_jin.py`](pair_jin.py) | The arcade's Jin scenes from `0x12150`; the comparison; `data/translations/jin_pairing.json` |
| `tools/text/arcade_pairing.py` | REF-006 pairing, **fixed here** (see "Correction") |
| `research/experiments/EXP-0021/capacity.py` | Capacity recount for the revised pairing |

## Procedure

```bash
for s in natural 4 9 15; do
  mkdir -p local/pair001/$s/snap
  MAME_TIMELINE=research/experiments/EXP-0023/timelines/scene-$s.txt \
    mame cybotsu -rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua \
    -snapshot_directory local/pair001/$s/snap -cfg_directory local/mame_arcade/cfg \
    -nvram_directory local/mame_arcade/nvram -skip_gameinfo -nothrottle -video none \
    -sound none -seconds_to_run 200 -debug -debugger none   # -debug only for 4, 9, 15
done
./invenv.sh python -m tools.text.arcade_pairing --driver local/mame_src/cps2.cpp \
  --set cybotsj --rompath local/arcade --saturn local/extracted/saturn_jp/VICTORY.BIN \
  --map-out data/text/arcade_jp_map.json --out data/text/saturn_arcade_pairing.json
./invenv.sh python research/experiments/EXP-0023/pair_jin.py \
  local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
  --out data/translations/jin_pairing.json
./invenv.sh python research/experiments/EXP-0021/capacity.py local/ref003/text-cybotsu.json
```

The debug flags must be written out; a shell variable holding them is not
split by zsh (the first forced runs failed with "unknown option").
18:30-18:45 local, 2026-11-02, the user present.

## Actual Result

- **Arcade scripts.** `0x12150` holds 16 per-pilot offsets. Pilot 0's table
  (`0x12160`) has 22 scenes, the same count as the Saturn's Jin list.
  - For scenes 21 and 0-15, the arcade's slot sequence equals the Saturn's
    box sequence exactly (`scenes_with_different_scripts`: none). Examples:
    scene 0 has slots 2-5, scene 9 has 33-40, scene 15 has 59-62.
  - In the ending scenes the Saturn differs: in 16 and 17 it adds box 1072,
    and 17 also adds 412; in 19 it uses 605 and 601 where the arcade uses 614
    and 610. Those scenes are out of scope.
- **MAME, unforced** (`cybotsu`, slot writes at `0x011D48`): 0 at 2733, 1 at
  2929, 2 at 3231, 3 at 3461, 4 at 3601, 5 at 3727, each followed by `0x8000`
  + N. That is scene 21, then scene 0, as on the Saturn.
- **MAME, forced** (scene byte replaced when it reads 0):

| Forced scene | Slots written from frame 3231 | Snapshot (agent-reviewed) |
| --- | --- | --- |
| 4 | 18, then 19 | `cybotsu_f03320.png`: Jin, slot 18's English (a one-line question) |
| 9 | 33, then 34 | `cybotsu_f03400.png`: Jin, slot 33's two-line English |
| 15 | 59, then 60 | `cybotsu_f03320.png`: the angry Jin portrait, slot 59's one-line English |

  In each case the record shown is the decoded record N, and the portrait is
  the one the Saturn's forced scene shows (EXP-0022). The unforced scene 0 at
  frame 3440 shows slot 2, the M1 box. Snapshot SHA-256 prefixes:
  `47840283…` (4), `2db5cbbd…` (9), `64a23230…` (15), `e387435a…`
  (unforced).
- **Every box has English.** All 63 slots 0-62 have a non-empty record in
  the English table `0x0B33AA`.
- **Correction to REF-006.**
  - The first comparison labelled 13 lines in 9 boxes as having no arcade
    counterpart. Their arcade Japanese records read as 1-6 codes, yet their
    English runs to 19-92 characters.
  - Raw records showed why: the space code `0x0020` occurs 60 times inside
    the 490 distinct arcade Japanese records. `read_jp_record` stopped at any
    word below `0x0100`, so it cut those records at their first space.
  - It now stops only at other such words, with a unit test. Rerun:

| | REF-006 as first run | Fixed |
| --- | --- | --- |
| Saturn lines 0-898 paired | 825 (787 exact, 38 edited) | 897 (852 exact, 45 edited) |
| Slots | 450 | 488 |
| Map codes | 573 / 579 | 590 / 596, no conflicts |
| Unpaired in 0-898 | 74 | 2: line 34 (dead data, D-021) and 258 |
| Lines 899-1850 | none paired | none paired |

- **Jin's pairing** (`data/translations/jin_pairing.json`, SHA-256
  `ebc7f323…`): 63 boxes and 120 lines; 115 exact and 5 edited against the
  slot's Japanese; none unpaired. There are no Saturn-only lines in Jin's
  story.
- **Capacity recount** (EXP-0021's model, 488 slots): 33 fit as written, 298
  re-wrapped, and 488 with pairs, which need 579 distinct pairs.
- The Saturn source is unchanged.

## Conclusion

**CONFIRMED:**

- For Jin's story, the arcade and the Saturn run the same scene scripts, so
  Saturn box N is arcade slot N. The arcade passes that slot to whichever
  language table its region selects, so English record N is box N's official
  English.
- Forced scenes in both games show the same boxes.
- Every one of Jin's 120 lines has official English, and none is
  Saturn-only.
- REF-006's pairing undercounted because of a reader bug, now fixed: 897 of
  lines 0-898 pair.

## Uncertainty and Alternatives

- The arcade's stage flow (which stage posts which scene) was not traced
  beyond scenes 21 and 0. The pairing does not depend on it, because it is
  per scene and box.
- The 5 edited lines differ in wording from the arcade Japanese. The English
  follows the arcade; the policy uses it unchanged, and fixes are opt-in.
- English records run up to 4 lines for a Saturn box of 1-3 lines (D-009).
  The line split is `LAYOUT-001`'s.

## Reproduction

Run the procedure. Expect identical scene lists, slots 18, 33 and 59 in the
forced runs, the fixed REF-006 counts, and the pairing counts above.
