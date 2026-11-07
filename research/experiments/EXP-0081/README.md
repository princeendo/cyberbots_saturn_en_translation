# EXP-0081: Codes, Room and Timing for the Whole English Script (SPECIAL-016)

Task: SPECIAL-016
Status: DONE
Confidence: CONFIRMED (by the build's own functions, with its pair, row and
caption counts reproduced exactly; the user's decisions verbatim). Not yet
built (`SPECIAL-017`).

## Observation

Lists 6-8 now have approved English (`SPECIAL-013`-`015`). The current
image (`ui007_ui_text.json`) uses 487 story pairs, 23 caption pairs and 153
+ 13 sacrificed codes; its story room left about 7 KB (`UI-006`). Lists 6-8's
endings draw the story font through `END.BIN`'s codes (D-047).

## Hypothesis

All approved English fits the story font's codes and each file's line room,
and lists 6-8's endings meet `END-011`'s timing rule.

## Controlled Change

None to the game. One measurement script; one approved box changed after
the user's answer (879).

## Prediction

Enough codes once no shown line stays Japanese; room in each file; every
ending box holds at least 42 frames.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `data/translations/special_list{6,7,8}.json`, `vs_captions.json`, `m5_roster.json` and the roster pairings | The English |
| `local/arcade`, `local/mame_src/cps2.cpp` | The roster's official records, as the build reads them |
| `build/ui006/b` (the `ui007_ui_text.json` image) | Its `END.BIN`/`STG0AS.BIN` tables and the roster endings' row bytes |
| `data/text/ending_surfaces_others.json` | Lists 6-8's ending windows (`END-022`) |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| [`capacity.py`](capacity.py) → [`capacity.json`](capacity.json) | `c09f7f21…` → `8bb10d21…` | Pairs, codes, tables, room, timing |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0081/capacity.py
```

2026-11-07, local. No emulator run.

## Actual Result

- **Controls:** the roster's rows and pairs come out as the build's: 487
  pairs and 897 rows (851 story + 46 quotes); 23 caption pairs.
- **Pairs:** lists 6-8 add 145 pairs new to the disc (list 6: 95, list 7:
  71, list 8: 81 of their own; the rest shared): 657 in the story font.
- **Codes:** with lists 6-8 in English, **no shown box stays Japanese**
  (story scenes of lists 0-8, picked quotes, all captions), so no code must
  keep its Japanese glyph: 1,246 usable codes (1,221 plus 25 table slots),
  589 spare. 322 pairs must take codes of Japanese characters (166 now),
  none visible.
- **`END.BIN`'s table:** equal to the story's untouched; in the current
  build the story's has 1,247 codes and `END.BIN`'s 1,241 (the story added
  25 new codes, the endings 19, at the same positions). If lists 6-8's
  endings need a pair on one of the story's last 6 codes, the build adds
  those codes to `END.BIN`'s table too.
- **Room** (bytes; rows as `dialogue.row_bytes`):

  | File | Room | Used | Spare |
  | --- | --- | --- | --- |
  | `STG0AS.BIN` | 50,108 | roster story 23,904, captions 2,032, new story 17,100 | 7,072 |
  | `VICTORY.BIN` | 50,084 | roster quotes 1,324, new quotes 924 | 47,836 |
  | `END.BIN` | 50,896 | roster endings 4,980 (built), new endings 2,848 | 43,068 |

- **Timing** (`END-011`'s rule on a scratch `END.BIN`): list 6, shortest
  hold 165 frames; list 8, 192. List 7 first failed: box 879 is open 57
  frames, so its approved line would hold 18 frames. With the user's new
  line it holds 42 (the minimum); box 878 types slower to keep its scene's
  end in place (rule step 3, as accepted for the roster).
- **The user's answers** (verbatim, 2026-11-07): box 879 "\"WHAT!?\"
  (Recommended)"; code cap "Approve up to 330 (Recommended)"; the mech-16
  name "ZERO-AKUMA (Recommended)" (the game's own Latin list, `CYBER.BIN`
  `0x38C60`, calls it ZERO-GOUKI).

## Conclusion

Prediction met after one change. The whole English script fits: 657 pairs
in 1,246 codes, with no shown Japanese left to break; room in every file
(the story file's margin is about 7 KB); every ending box holds at least
0.7 s.

## Uncertainty and Alternatives

- Rows are measured as the build would make them; the build's placement
  (first fit in spans) can need a little more room than the totals.
- The half-cell indent of new rows is chosen here against the roster's
  fixed rows; the build may choose differently, which changes the pair count
  by a few.
- The mech-16 name's banner width is checked when built (`SPECIAL-017`).
