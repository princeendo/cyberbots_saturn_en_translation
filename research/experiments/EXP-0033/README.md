# EXP-0033: Census of the 11 Pilot Lists; the M5 Roster

Task: RE-005
Status: DONE
Confidence: CONFIRMED (block k is list k in play for lists 0-6; the pilot select routes; stage group 9 x list for the lists played); SUPPORTED (list 10 is never posted by the Saturn; END.BIN scenes by number)

## Observation

`STG0AS.BIN` has 11 per-pilot scene lists (`0x060AAD24`, D-026) and 9
blocks of story-scene posts (`EXP-0027`). Blocks 0-2 were seen in play as
lists 0-2 (Jin, Santana, Mary). Lists 3-5 matched the arcade's pilots by
their scripts only; lists 9 and 10 matched the arcade's pilots 6 and 7.
`WIN-002` showed list 9 is the versus win quotes (D-030).

## Hypothesis

Block k is list k for every pilot: choosing pilot k on the select screen
posts block k's opening scene, then scene 0, and starts the stage byte at
pilot k's own group.

## Controlled Change

None to the game. One variable per cold boot: the moves on the pilot
select screen. Scene posts are logged by a log-mode PC breakpoint; each run
stops after two posts, before the first fight, so no key is pressed after
the machine select.

## Prediction

Each run posts the opening scene of one block (21, 23, 19, 22, 20, 27, 18,
17 or 21 for blocks 0-8), then 0, and the stage byte reads that pilot's
group.

## Inputs and Provenance

- The untouched image (`local/disc_images/cyberbots_saturn_jp_2m/`).
- `STG0AS.BIN`, `END.BIN` extracted from it (`local/extracted/saturn_jp/`).
- `data/text/saturn_arcade_pairing.json` (REF-006).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`census.py`](census.py) | Per list: scenes, story/ending/unposted scenes, story boxes and lines, pairing, sharing, routes → `data/text/pilot_census.json` |
| [`roster.py`](roster.py) | `data/text/m5_roster.json` and the box lists of lists 2-5 |
| [`routes.json`](routes.json) | Pilot select moves, first stage group and first posts per list, with the run that showed them |
| `research/experiments/EXP-0027/play_route.py` | Cold boot to a chosen pilot; new options `--stop-after-posts`, `--select-wait`, `--move-wait` |
| `research/experiments/EXP-0022/box_list.py` | Box lists; the last list (10) now ends at the list table (it raised an error); lists 0-2's output unchanged |

Python 3.13.13; Mednafen 1.32.1 with the agent interface (D-007).

## Procedure

```bash
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
R="./invenv.sh python research/experiments/EXP-0027/play_route.py $ORIG"
$R local/re005/right3b --moves right,right,right --stop-after-posts 2 --select-wait 10
$R local/re005/right4b --moves right,right,right,right --stop-after-posts 2 --select-wait 10 --move-wait 3
$R local/re005/right5b --moves right,right,right,right,right --stop-after-posts 2 --select-wait 10 --move-wait 3
$R local/re005/left1 --moves left --stop-after-posts 2 --select-wait 10
$R local/re005/left2 --moves left,left --stop-after-posts 2 --select-wait 10
./invenv.sh python research/experiments/EXP-0033/census.py \
  --routes research/experiments/EXP-0033/routes.json --out data/text/pilot_census.json
./invenv.sh python research/experiments/EXP-0033/roster.py
```

2026-11-04, 10:17-10:54 local, the user present and asked before each set
of cold boots ("Yes, go ahead (Recommended)", then "Yes, 2 more
(Recommended)" twice).

## Actual Result

### Cold boots (8 runs, 67 key presses, all before the first fight)

| Run | Moves | First posts | Stage byte | Portrait (agent-reviewed) | Keys |
| --- | --- | --- | --- | --- | --- |
| `right3` | right x3, 1 s apart, 6 s wait | 23, 0 | 9 | Santana: the first move came before the cursor appeared | 8 |
| `right3b` | right x3, 10 s wait | **20, 0** | **36** | Gawaine (`select-3.png`, `d980790a…`) | 8 |
| `right4` | right x4, 1 s apart | 20, 0 | 36 | Gawaine; one key refused (Mednafen not in front) | 9 |
| `right5` | right x5, 1 s apart | 20, 0 | 36 | Gawaine: moves 4 and 5 did not move the cursor | 10 |
| `left1` | left x1 | **18, 0** | **54** | Saturn-only pilot, bottom right; the name art reads Devilot (`d1adf818…`) | 6 |
| `left2` | left x2 | 0, 1 | **72** | Saturn-only pilot, bottom middle; the name art reads Shade (`cf3410e0…`) | 7 |
| `right4b` | right x4, 3 s apart | **27, 0** | **45** | Bao and Mao (`select-4.png`, `991e19c5…`) | 9 |
| `right5b` | right x5, 3 s apart | **22, 0** | **27** | Arieta (`select-5.png`, `6076d707…`) | 10 |

- Presses 1 s apart after the third move are lost while a portrait loads;
  3 s apart they all move the cursor.
- Blocks 3 (22, 0), 4 (20, 0), 5 (27, 0) and 6 (18, 0) open as predicted,
  so block k is list k for k = 0-6. The stage byte starts at 9 x k for every
  list played (0, 9, 18, 27, 36, 45, 54, 72).
- `left2`: stage group 72 (list 8), but the first posts logged were 0 and 1;
  block 8 opens with 21 in the code. Not followed further (list 8 is out of
  scope).

### Census (`data/text/pilot_census.json`, `616b0b79…`)

| List | Pilot | Scenes | Story scenes | Ending by number | Unposted | Story boxes | Lines | Own slot | Saturn-only | Shared |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Jin | 22 | 17 | 16-20 | - | 63 | 120 | 120 | - | 57, 75 |
| 1 | Santana | 27 | 20 | 16-22 | - | 64 | 117 | 114 | - | 144 |
| 2 | Mary | 22 | 18 | 16-18 | 15 | 69 | 119 | 118 | 258 | - |
| 3 | Arieta | 29 | 21 | 16-21, 27, 28 | - | 66 | 127 | 127 | - | 386 |
| 4 | Gawaine | 22 | 17 | 16-19 | 15 | 70 | 137 | 132 | - | 57, 144, 538, 562, 584 |
| 5 | Bao and Mao | 29 | 21 | 16-22, 28 | - | 72 | 136 | 130 | - | 75, 386, 538, 661 |
| 6 | Saturn-only | 21 | 18 | 17, 19, 20 | - | 119 | 244 | 0 | 243 | 661, 1132 |
| 7 | Saturn-only | 27 | 21 | 21-26 | - | 103 | 198 | 0 | 198 | 1132 |
| 8 | Saturn-only | 35 | 32 | 32-34 | - | 117 | 196 | 0 | 196 | 1132 |
| 9 | win quotes | 72 | - | - | all | - | - | - | - | - |
| 10 | name labels | 7 | - | - | all | - | - | - | - | - |

"Own slot" counts lines REF-006 pairs with the arcade slot of the same
number as their box; Santana's 121-123 pair with slot 63 (shared record,
D-027), Gawaine's 5 and Bao and Mao's 6 others with another slot
(`lines_paired_elsewhere`, for `PAIR-003`). Mary's and Gawaine's scene 15
show the same boxes as their scene 14 and are in no block.

### Lists 9 and 10

- List 9: the versus win quotes, posted by `VICTORY.BIN` (D-030; forced and
  natural quotes on screen in `EXP-0032`).
- List 10: 7 scenes; 0-5 show the speaker-name boxes 602-605 one after
  another (lines 1007-1010), 6 shows box 609 (line 1014). Forced scene 0 in
  `EXP-0027` (`local/re004/list-10/step035.png`) shows the first name box.
  The arcade's list 7 has the same 7 scripts and is posted at `0x6319C` with
  a per-pilot scene byte (`0x631BC`). No Saturn file holds a list-10 message
  (`0x1400000A`), so no Saturn post was found.

### Decision

Asked (2026-11-04): "Which pilots make up the M5 roster? The six arcade
pilots (Jin, Santana, Mary, Arieta, Gawaine, Bao and Mao) have 404 story
boxes plus 46 win-quote boxes, all with official arcade English except
Mary's line 258. The three Saturn-only pilots (lists 6-8, e.g. Devilot and
Shade) add 339 story boxes with no official English and are special cases
under rule 24." The user's answer, verbatim: "Six arcade pilots
(Recommended)".

Outputs: `data/text/m5_roster.json` (`299fd317…`), `arieta_boxes.json`,
`gawaine_boxes.json`, `baomao_boxes.json`, and `mary_boxes.json` with story
scenes added (its scenes unchanged); `docs/coverage_exceptions.md`.
`jin_boxes.json` is unchanged: it feeds the regression references, and the
compiler takes Jin's story scenes from D-021, the same 17 the census finds.

The source image is unchanged.

## Conclusion

**CONFIRMED:** block k of `STG0AS.BIN`'s scene posts is pilot list k for
k = 0-6; choosing that pilot posts its opening scene and scene 0, and the
stage byte starts at 9 x k. The routes from Jin: Mary right x1, Santana
right x2, Gawaine right x3, Bao and Mao right x4, Arieta right x5 (moves 3 s
apart), Devilot left x1, Shade left x2. The user chose lists 0-5 as the M5
roster.

## Uncertainty and Alternatives

- List 7 was not played; its route (likely left x3) and group (63) are
  untested.
- `END.BIN`'s posts carry no list number, so ending scenes are matched by
  number only.
- List 10's post was searched for as a literal only; a computed post would
  not be found.
- `left2`'s missing opening post (21) is unexplained.

## Reproduction

Run the procedure. Expect the first posts and stage bytes in the table, and
`census.py` to reproduce `data/text/pilot_census.json` byte for byte.
