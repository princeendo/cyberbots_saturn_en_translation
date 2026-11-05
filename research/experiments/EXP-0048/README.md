# EXP-0048: How Ending Boxes Are Timed, and a Rule for the English

Task: END-011
Status: DONE
Confidence: CONFIRMED (cues, typing words, the script's wait for typing; the rule on Jin's ending, built and live); SUPPORTED (the rule on lists 1-5, dry runs)

## Observation

- In END-010's build, English boxes 409, 493 and 420 finished typing 4-7
  frames before they closed (D-042). The user chose a follow-up task:
  "Accept now, follow-up task (Recommended)".
- In Jin's scripts, each box is `E206`, the box, a portrait word, `EAnn`,
  then the box's close. `nn` counts up through the ending. The closes,
  counted from post 16, fall on round frame counts (210, 480, 750, 810, 990).

## Hypotheses (tested in turn)

1. `EAnn` waits until the scene timer reaches cue `nn` of a per-list table;
   moving one cue moves only that close and the next box's open.
2. `E2nn` sets the following box's typing interval to `nn` frames a glyph.

## Controlled Changes

From the END-001 checkpoint, untouched image, one RAM write each:
1. Jin's cue 2 (`0x06087872`) from 480 (`01E0`) to 540 (`021C`), after
   post 16.
2. Box 409's typing word (`0x06082CF4`) from `E206` to `E203`, 300 frames
   after `END.BIN` loads.

A first attempt at change 1 wrote to `0x06067872` (code, `04BC`). Nothing
changed, and the address was corrected; the table is at file `0x2786E`.

## Predictions

1. Box 409 closes 60 frames later; box 493 opens 60 frames later and closes
   on its own cue; nothing else moves.
2. Box 409 types twice as fast; its open and close are unchanged.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Checkpoint | `local/end001/checkpoint/jin_ending_a16503.mcs` |
| Controls | `local/end002/control` (EXP-0038); `local/end011/control` (2,600 frames) |
| Pairings | `data/translations/*_ending_pairing.json`; `data/text/ending_surfaces.json` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0042/probe.py` | Forced runs, RAM writes, cell dumps |
| [`timing.py`](timing.py) | Each roster box's hold at the Japanese timing (exploration; numbers only) |
| `tools/text/ending_timing.py` | The rule; `tools.text.dialogue --retime` |
| [`check_all.py`](check_all.py) → [`rule.json`](rule.json) | The rule on lists 0-5, dry runs |
| `EXP-0045/check_build.py`, `check_live.py` | Build and live checks |

Agent Mednafen 1.32.1, silent home; no key, no cold boot.

## Procedure

```bash
P=research/experiments/EXP-0042/probe.py; export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $P local/end011/control --frames 2600 --cells-until 0
./invenv.sh python $P local/end011/cue2 --frames 2600 --cells-until 0 \
  --write 06087872=021C --write-scene 16
./invenv.sh python $P local/end011/speed409 --frames 2200 --cells-until 2200 \
  --write 06082CF4=E203 --write-load END.BIN:300
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-011 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade \
  --ending data/translations/jin_ending_pairing.json --retime"
$B --out build/end011/jin --ending-record build/end011/jin-record.json
$B --out build/end011/jin-again --ending-record build/end011/jin-again-record.json
./invenv.sh python research/experiments/EXP-0045/check_build.py build/end011/jin build/end011/jin-again
./invenv.sh python -m tools.disc.sector "build/end011/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
./invenv.sh python $P local/end011/live-final \
  --cue "build/end011/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  --frames 13400 --step 5 --cells-until 6400
./invenv.sh python research/experiments/EXP-0045/check_live.py local/end011/live-final build/end011/jin
./invenv.sh python research/experiments/EXP-0048/check_all.py local/ref003/cybotsu-maincpu.bin \
  --out research/experiments/EXP-0048/rule.json
```

2026-11-05, 16:15-17:30 local.

## Actual Result

### 1. Cues

| Run | 409 closes | 493 opens / closes | Others |
| --- | --- | --- | --- |
| Control | 2098 | 2100 / 2368 | — |
| Cue 2 = 540 | 2159 | 2161 / 2369 | every other event +1 frame (the run's offset) |

So 409 closed 60 frames later and 493 kept its close. The pointer table
`0x060879A0` holds one pointer per list 0-8. Each list's cue count matches
its boxes that close on cues; Jin's cue values match every close of the
control run (scene 16 from post 16, scene 18 from post 18, scene 19 from 20
frames before post 19).

### 2. Typing

Box 409's 30 Japanese glyphs were all drawn 181 frames after it opened in
the control, and 91 frames after with `E203`. Its open and close and all
other events are unchanged (+1, the run's offset).

### 3. The script waits for typing; the posts follow

| Build | Post 17 | Post 18 | Post 19 | `KEND.BIN` |
| --- | --- | --- | --- | --- |
| Japanese (control) | 2819 | 3217 | 3717 | 6157 |
| END-010 (English at `E206`) | 2921 | 3175 | 3849 | 6139 |
| First rule (3 frames a glyph everywhere) | 2798 | 3163 | 3711 | 6063 |

Post 17 follows box 412's typing + its 60-frame wait + about 30 frames:
24 × 6 + 60 → 2819, 41 × 6 + 60 → 2921, 41 × 3 + 60 → 2798. The music
tracks start with the posts (track 43 at 3208, track 44 at 3688 in the
control). So the rule was extended to keep each box's time to the next
event equal to the Japanese (`ending_timing.py`, steps 3-4):
- **Waits:** a box before waits gets the interval and waits that give the
  Japanese typing + waits. Consecutive waits share the remainder, a byte
  each.
- **Scene ends:** a box before the scene end gets the interval closest to
  the Japanese typing.
- **Leftovers:** what is left goes to the run before the box, through its
  last cue, or else to slower typing (up to 16 frames a glyph).
- **Runs:** runs are joined by the script (no wait or scene end between
  two cued boxes), not by frame gaps. Santana's 432-433 have a 14-frame
  `CA00` between them.

### 4. The rule on Jin's ending, built and live

- **Build** (`build/end011/jin`, the M5 roster + Jin's ending):
  - two builds identical;
  - the M5 files, `prediction.json` and `changes.json` equal RE-008's;
  - `SE.DAT`, `KEND_1.BIN`, `QSD.PIX` and `ending_prediction.json` equal
    END-010's;
  - `END.BIN` differs from END-010's in 31 bytes, all inside the 30 timing
    changes (typing words, waits, cues);
  - 160 sectors changed, all 43,793 valid; the source is unchanged.

  `data/regression/end011_jin_timing.json` holds the hashes.
- **Timing** (`ending_timing.json`):
  - cued boxes type at 3 frames a glyph, and their runs share spare evenly
    (scene 16: 113 frames each; scene 19: 202);
  - box 412's wait goes 60 → 81 and box 413's 120 → 174, keeping the
    Japanese time;
  - box 415 types at 2 frames a glyph (84 frames against the Japanese 78),
    and the run before it gives up 6 (cue 8: 390 → 384);
  - box 422, 7 glyphs before two 240-frame waits, keeps 6 frames a glyph
    with both waits at 255. The 120 frames still missing go to cue 15
    (1620 → 1740).
- **Live** (`local/end011/live-final`, cells every 5 frames):
  - 21 of 21 box openings draw their predicted cells;
  - posts 1618, 2819, 3217, 3717, the track starts (1583, 3208, 3688, 6524,
    8736, 13180), and `FIX.BIN`, `KEND.BIN`, `KEND_1.BIN` and `QSD.PIX`
    load on exactly the control's frames;
  - each English box holds its finished line:

    | Boxes | Held (frames) |
    | --- | --- |
    | 408, 409, 493, 410, 411 | 117, 121, 113, 120, 122 |
    | 412, 413, 414 | 206, 263, 269 |
    | 416-421 | 206-209 |
    | 422 | 677 (until the cast roll) |
    | 415 | 31 |

    Box 415 is followed by the scene end: the screen fades as the post
    comes, as in the Japanese (control shot 3716 is black too).

### 5. The rule on lists 1-5 (dry runs, `rule.json`)

| List | Smallest hold of a cued box | Left over at a scene end | Slower typing |
| --- | --- | --- | --- |
| 0 | 113 | 0 (absorbed: 415, 422) | — |
| 1 | 45 | 0 (434 absorbed by 433's run) | — |
| 2 | 86 | 0 | — |
| 3 | 61 | 455: −5 | 455 at 5 |
| 4 | 82 | 0 | 472 at 16 (5 glyphs in 80 frames) |
| 5 | 85 | 482: +3, 483: −3 | 482 at 6, 483 at 6, 487 at 10 |

All are above the 42-frame floor, and no scene end moves by more than 5
frames. These are dry runs; the M8 build checks them live (`END-023`).

## Conclusion

Both hypotheses are CONFIRMED.
- `EAnn` closes a box at cue `nn` of the list's table, and `E2nn` sets its
  typing interval.
- The script waits for each box's typing, so a box before a wait or the
  scene end sets when the next scene, and its music, starts.

The rule (`--retime`) uses all three. In Jin's ending it gives every English
box that closes on a cue 1.9 s or more with its finished line. It keeps
every scene change, track start and the cast roll on the Japanese frames.

## Uncertainty and Alternatives

- **Box 415** (and any box right before a scene end) holds only while the
  screen fades, as the Japanese does. Only moving the scene change could
  hold it longer.
- **Slower typing:** Gawaine's 472 types at 16 frames a glyph to keep his
  scene's length, which may look slow. That will be seen in the M8 build.
- **Typing estimate:** typing is taken as 6 + 3 × glyphs frames. Jin's
  measured holds are 0-8 frames above the predicted ones, so the estimate
  is slightly conservative.

## Reproduction

Run the procedure. Expect the frames and holds above, and
`data/regression/end011_jin_timing.json`'s hashes.
