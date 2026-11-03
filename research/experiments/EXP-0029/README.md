# EXP-0029: The Compiler and Checks Handle a Set of Pilots

Task: RE-006
Status: DONE
Confidence: CONFIRMED (Jin's regression, determinism, the budget stop, the checks for pilots 0 and 1); SUPPORTED (Santana's ending lines are dead in `STG0AS.BIN`'s copy, as Jin's are, EXP-0024)

## Observation

`tools/text/dialogue.py` (EXP-0026) builds Jin only. Its kept lines are any
record's users, and its dead ending lines are a fixed list for Jin (EXP-0024).
Santana's boxes are paired (EXP-0028). Line 144 is shared with another
pilot's box 292. Box 63 is in no scene but shares Santana's lines 121-123.

## Hypothesis

The room, the kept lines and the dead lines can be derived for any set of
pilots from the scene scripts:
- A line's users are the boxes some pilot's scene shows.
- A pilot's ending is its scenes outside its story scenes. An ending line is
  dead if every box using it is a selected pilot's ending box and appears in
  no other scene.

For Jin alone this gives EXP-0026's room, so the image is byte for byte
RE-003's.

## Controlled Change

The compiler: several `--pairing` files, one pair-code pool, derived kept and
dead lines, a sacrifice limit (`--max-sacrifice`, default 18, the number
approved) and a budget report (`--budget`). No change to the game.

## Prediction

- Jin alone reproduces `data/regression/re003_jin.json`: Track 01
  `904402b6…3f01`, the two files, the prediction and the record.
- Jin + Santana stop with a budget of about 73 sacrificed codes (EXP-0027's
  408 pairs against 335 free codes), and write nothing.
- The forced check, given a pilot, shows the same results as EXP-0026 and
  EXP-0027.

## Inputs and Provenance

- `data/translations/jin_pairing.json`, `santana_pairing.json`
  (`0ebbcdf1…`), `data/text/jin_boxes.json`, `santana_boxes.json`
  (`d6ea9fa9…`).
- The arcade font capture `local/layout001/font/arcade_font.json` and the ROM
  zips (ignored), as in EXP-0026.
- REF-005 state `f00004138.mcs` (`3eb789da…`).
- The source image, untouched; `patch_image` checks it against the manifest.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`tools/text/dialogue.py`](../../../tools/text/dialogue.py) | Generalized compiler. Tests: `tests/unit/test_dialogue.py` |
| [`force_check.py`](force_check.py) | EXP-0026's forced check for any pilot (`--boxes`), with `other_pilot.py`'s redirect; names its starting state |
| `research/experiments/EXP-0027/play_route.py` | The play check for any pilot (`--moves`, `--until-stage` relative to the pilot's first stage group); it starts from a cold boot |
| `research/experiments/EXP-0027/check_first_box.py` | A forced scene's first box against the original font |

Python 3.13.13; Mednafen 1.32.1 with the agent interface (D-007).

## Procedure

```bash
C="--font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp --rompath local/arcade"
J=data/translations/jin_pairing.json; S=data/translations/santana_pairing.json
./invenv.sh python -m tools.text.dialogue --pairing $J $C --out build/re006/jin --budget
./invenv.sh python -m tools.text.dialogue --pairing $J --pairing $S $C --out build/re006/js --budget
./invenv.sh python -m tools.text.dialogue --pairing $J --pairing $S $C --out build/re006/js   # stops
for r in a b; do
  ./invenv.sh python -m tools.text.dialogue --pairing $J $C --out build/re006/jin-$r --record build/re006/jin-$r.json
  ./invenv.sh python -m tools.text.dialogue --pairing $J --pairing $S $C --out build/re006/js-$r \
    --max-sacrifice 73 --record-dir build/re006/js-$r   # determinism only; not approved
done
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
CUE="build/re006/jin-a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python research/experiments/EXP-0029/force_check.py "$CUE" build/re006/jin-a/prediction.json \
  local/re006/jin --boxes data/text/jin_boxes.json --scenes 9
./invenv.sh python research/experiments/EXP-0029/force_check.py "$ORIG" build/re006/jin-a/prediction.json \
  local/re006/santana-orig --boxes data/text/santana_boxes.json --scenes 4 --control
./invenv.sh python research/experiments/EXP-0027/check_first_box.py data/text/santana_boxes.json 4 \
  local/re006/santana-orig/scene-04
```

2026-11-03, after 11:33 local; the forced runs 12:07-12:10.

## Actual Result

### The compiler

- **Users:** the boxes shown by any scene of the 11 pilot lists (scripts
  parsed as EXP-0022's `box_list.py` does). Box 63 is not one, so Santana's
  lines 121-123 are his own.
- **Jin alone:** kept lines 57 and 75; dead lines 752-777, 897, 898 and 953
  (EXP-0024's list, now derived); 3,992 of 4,196 bytes; 353 pairs; 18
  sacrificed; the same 16 touched lines. The build reproduces
  `re003_jin.json` exactly: `STG0AS.BIN` `41211301…`, `KANJI.BIN`
  `8fe36227…`, prediction `394f745c…`, record `9ae48278…` (identical to
  `data/translations/jin_story.json`), Track 01 `904402b6…3f01`.
- **Jin + Santana** (`--budget`):

| Item | Value |
| --- | --- |
| Boxes | 127 |
| Distinct pairs (one pool) | 408 |
| Unused codes, new codes | 310, 25 |
| **Sacrificed codes needed** | **73** (18 approved) |
| Text / room | 7,316 / 8,088 bytes |
| Kept lines | 57, 75, 144 |
| Dead lines | 752-800, 897, 898, 953, 1016 (Santana's ending adds 778-800 and 1016) |
| Japanese lines touched | 62 in `STG0AS.BIN` (16 for Jin alone); 198 counting the copies in `END.BIN` and `VICTORY.BIN` (48 for Jin alone) |

- **Budget stop:** without `--budget`, the build printed the budget, `73
  sacrificed codes needed, 18 approved`, exited 1, and wrote nothing.
- **Determinism:** two builds of Jin and two of Jin + Santana (at
  `--max-sacrifice 73`, to compare bytes only) are identical: Track 01
  `a63ba806…` for the pair, both records equal.
- **Records:** `--record-dir` writes one record per pilot, holding that
  pilot's boxes and codes; `--task` names the task.
- **Tests:** 161 unit tests pass, among them new ones for the shared pool,
  the kept-line rule, the dead-line rule and the sacrifice stop. Ruff and
  mypy are clean.

### A ranking measured for the gate

Ranking the sacrifice candidates by the uses that stay Japanese, instead of
by all uses, would touch 184 lines across the three copies instead of 198
(48 instead of 62 in `STG0AS.BIN`); for Jin alone, 44 instead of 48. It would
change Jin's image, so it is not used; it is an option for the gate.

### The checks

- **Jin** (`--boxes jin_boxes.json`, scene 9, Jin's image): 8 of 8 boxes
  match completely (27, 46, 40, 27, 27, 25, 7, 34 cells), as in EXP-0026.
- **Santana** (`--boxes santana_boxes.json`, scene 4, original image,
  redirected): box 81 draws its 29 of 29 Japanese cells, as in EXP-0027.
- Each JSON line names the pilot and the start: state 4138, `3eb789da…`,
  saved before `STG0AS.BIN` loads, so the script in RAM is the image's own
  (EXP-0026).
- **Play:** EXP-0027's `play_route.py` already chooses the pilot on the
  select screen and counts stages from the pilot's first stage group. It
  starts from a cold boot, so the script in RAM is the image's own.

The source is unchanged.

## Conclusion

**CONFIRMED:** the compiler builds any set of pilots from one pair-code pool,
with kept and dead lines derived from the scene scripts. It is deterministic,
reproduces Jin's M3 image exactly, and stops at the approved sacrifice count.
Jin + Santana need **73** sacrificed codes, touching 62 Japanese lines, for
the gate extension. The forced check takes any pilot and names its start.

## Uncertainty and Alternatives

- Santana's ending lines are dead only if `STG0AS.BIN` never posts his
  scenes 16-22 (SUPPORTED: EXP-0027's posts, as for Jin in EXP-0024).
- A box used only by a script outside the pilot lists would not count as a
  user. No such script is known (D-021).
- The pair's image built here is for comparison only; it uses 55 more
  sacrifices than approved.

## Reproduction

Run the procedure. Expect the hashes and the budget above, exit 1 for the
stopped build, 8/8 boxes for Jin and 29 cells for Santana.
