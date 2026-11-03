# EXP-0028: Santana's Boxes Pair Slot for Slot With the Arcade English

Task: PAIR-002
Status: DONE
Confidence: CONFIRMED

## Observation

Santana (Saturn pilot list 1 = arcade pilot 1) has 20 story scenes and 64
boxes (D-026). For Jin, both games run the same scene scripts, so box N is
slot N (D-022). In RE-004's table, one of Santana's boxes was not slot for
slot.

## Hypothesis

Santana's story scripts are the arcade's too, so every box N pairs with slot
N. The one exception has an explanation in the data.

## Controlled Change

None to either game for the comparison. In MAME, debugger actions set the
script interpreter's pilot byte to 1 (at `0x11CDA`) and replace scene 0 with
a chosen scene (at `0x11CEA`).

## Prediction

All 20 scenes' scripts are equal. The exception is a shared or duplicated
record. Forced arcade scenes 4, 9 and 24 show slots 81, 99 and 87 first: the
first boxes the Saturn showed for those scenes (EXP-0027).

## Inputs and Provenance

- **Arcade images:** `local/ref003/cybotsu-maincpu.bin` (`18e8827d…`) and
  `cybotsj-maincpu.bin` (`2d1e6b25…`).
- **Box list and pairing:** `data/text/santana_boxes.json` (`d6ea9fa9…`) and
  `data/text/saturn_arcade_pairing.json` (as fixed in EXP-0023).
- **English decode:** ignored; used only for the agent's review.
- **Emulator:** MAME 0.289.
- **Source image:** the Saturn source is not used here; it is unchanged.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`pair_pilot.py`](pair_pilot.py) | Generalizes `EXP-0023/pair_jin.py` to any pilot and box list; recognizes slots that share a record |
| [`timelines/`](timelines/) | MAME runs with the pilot and scene forced |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0028/pair_pilot.py \
  local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin --pilot 0
./invenv.sh python research/experiments/EXP-0028/pair_pilot.py \
  local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
  --pilot 1 --boxes data/text/santana_boxes.json --out data/translations/santana_pairing.json
for s in 4 9 24; do
  mkdir -p local/pair002/$s/snap
  MAME_TIMELINE=research/experiments/EXP-0028/timelines/santana-scene-$s.txt \
    mame cybotsu -rompath local/arcade -autoboot_script tools/reference/mame_timeline.lua \
    -snapshot_directory local/pair002/$s/snap -cfg_directory local/mame_arcade/cfg \
    -nvram_directory local/mame_arcade/nvram -skip_gameinfo -nothrottle -video none \
    -sound none -seconds_to_run 200 -debug -debugger none
done
```

11:20-11:30 local, 2026-11-03.

## Actual Result

- **Generalized script:** `pair_pilot.py --pilot 0` reproduces Jin's
  pairing: 63 boxes, 120 lines, 115 exact, 5 edited.
- **Santana:** all 20 story scenes have the same slot lists in both games
  (`scenes_with_different_scripts`: none). All 64 boxes have an English
  record. Of 117 lines, **114 are exact and 3 edited**; none is unaligned.
- **The exception was a shared record.**
  - Box 64 (scene 23, his opening narration) has lines 121-123, which REF-006
    aligned to slot 63.
  - Arcade slots 63 and 64 point to the same record, in English (`0x0B4DF4`)
    and in Japanese (`0x0A4996`).
  - Saturn boxes 63 and 64 point to the same record (`0x0609D924`), and box
    63 is in no scene of any pilot.
  - So slot 64 is box 64's own English. `pair_pilot.py` now takes a slot
    that shares the box's English record as the box's own (listed in
    `slots_sharing_a_record_with_a_paired_box`: 63).
- **Shared line:** line 144 is used by Santana's box 75 and by box 292 (its
  own record at `0x0609F564`, another pilot's). `RE-006`'s kept-line rule
  covers it. Lines 121-123 are not truly shared, because box 63 is unused.
- **MAME, forced** (`cybotsu`; the pilot set to 1, scene 0 replaced):
  - Each run first plays Santana's scene 21, part of his ending: slots 612,
    432, 620, 433, 612, 434. The Saturn's ending has 603 and 611 in place
    of 612 and 620; endings are out of scope.
  - Then the forced scene:

| Forced scene | Slots (from frame 3438) | Saturn boxes (`santana_boxes.json`) |
| --- | --- | --- |
| 4 | 81, 82, 83, 84 | 81, 82, 83, 84 |
| 9 | 99, 100, 101, 102, 103, 104, 105 | 99-105 |
| 24 | 87, 88 | 87, 88 |

  - Snapshots (agent-reviewed): slot 81's and slot 87's English beside
    Santana's portrait, and slot 99's beside the other speaker's. These are
    the decoded records 81, 99 and 87. Snapshot SHA-256 prefixes:
    `0ba73111…` (4), `7b2c866c…` (9), `4a3b9fa6…` (24).
  - EXP-0027 forced the same three scenes on the Saturn, and their first
    boxes (81, 99 and 87) drew their cells exactly.
- **Output:** `data/translations/santana_pairing.json` (`0ebbcdf1…`), with
  no text.

## Conclusion

**CONFIRMED:** Santana's story uses the same scene scripts in both games, so
each of his 64 boxes pairs with the arcade slot of the same number. That
slot's record is the official English. Three forced scenes show the same
boxes in both games.

All 117 lines have official English; none needs a new translation. The one
apparent exception is two slots sharing a record.

## Uncertainty and Alternatives

- The 3 edited lines differ in wording from the arcade Japanese. The English
  follows the arcade, unchanged, under the policy.
- The ending scenes (16-22) differ in two slots and are out of scope.

## Reproduction

Run the procedure. Expect Jin's counts reproduced, Santana's 114 + 3, and
the slot sequences in the table.
