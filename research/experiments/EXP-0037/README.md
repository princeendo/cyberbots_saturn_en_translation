# EXP-0037: Jin's Ending, Reached by RAM Writes, and What It Shows

Task: END-001
Status: DONE
Confidence: CONFIRMED (route, checkpoint, loads, scene posts and boxes, surfaces); SUPPORTED (the ending's glyphs come from `SE.DAT`'s copy of `KANJI.BIN`)

## Observation

Jin's story posts scenes 21 and 0-15 over stages 0-8 (D-021); scenes 16-20
are posted from `END.BIN`. `REF-005` and every later play reached at most
stage 2, so no ending had been seen. Fights end only at time-out or on a
hit, so a no-key route must hold the vitality (D-025) and bring the game to
its last stage some other way.

## Hypothesis

Writing the right progress bytes from a saved state, before the stage
starts, makes the game run Jin's last stage and, after a time-out win, his
ending, with no key pressed.

## Controlled Change

RAM writes only, from REF-005 state 4138 (machine select, Jin, before
`STG0AS.BIN` loads; SHA-256 `3eb789da…a437`), at frame 318, right after the
arcade start has set player 2 (`0x06027848`, frame 305):

| Address | Bytes | Why |
| --- | --- | --- |
| `0x060D02BF` (player 1 record `0x060CFFDC` + `0x2E3`) | `08` | Stage index; the stage start reads it |
| `0x060D05A2` (player 2 record `0x060D02D0` + `0x2D2`) | `08 0B 0B 0B` | Pilot and machine bytes for index 8 (`0x0604B5C0`[8], `0x0604B650`[8]) |
| `0x060CFF08` | `00 08` | Opponent word, as `0x06027950` writes it |
| `0x060CFF07` | `01` | Last-fight flag: entry 9 of the opponent row is 255 |

Then, from the post of scene 15 until `END.BIN` is read, player 1's
vitality pair is held at 152 (144 writes) and player 2's is set to 0 once
(D-025). No key is pressed. Every write is logged with its frame
(`OUT/writes.jsonl`).

## Prediction

The stage start sets stage 8 itself; scenes 14 and 15 play; the fight ends
at time-out; the round-end code takes the last-fight branch; `END.BIN`
loads and posts scenes 16-20; then credits.

## Inputs and Provenance

- Untouched image, `local/disc_images/cyberbots_saturn_jp_2m/` (`ENV-005`).
- M5 image `build/re008/roster/image/` (Track 01 `2c8505df…`, `EXP-0036`).
- `local/ref005/session/states/f00004138.mcs` (`3eb789da…a437`).
- `local/extracted/saturn_jp/`: `END.BIN` `a4868d8d…`, `SE.DAT` `0430d5e7…`,
  `KANJI.BIN` `898de5bc…`; `data/text/script_census.json`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`ending_route.py`](ending_route.py) (`d185aa05…`) | The route: the writes above, vitality, Play Disc and scene-post log (with callers), `END.BIN` box calls, 25-frame polls, a screenshot and the 60 glyph cells every 50 frames, optional checkpoint |
| [`m5_glyphs.py`](m5_glyphs.py) (`5299d2e3…`) | Each ending box's predicted cells on both images against both runs' cell dumps |
| `research/experiments/EXP-0031/loads.py` | Its Play Disc decoder (imported) |
| `tools/memory/mcs_extract.py` | Checkpoint memory regions (D-006) |
| `tools/sh2/disasm.py` | The stage start, opponent, round-end and mode code |

Python 3.13.13; Mednafen 1.32.1 with the agent interface, silent home;
pairs of runs used `MEDNAFEN_ALLOWMULTI=1` (a second instance on the same
home is otherwise refused). The committed scripts differ from the ones that
ran only by a variable rename and a type annotation (for `mypy`).

## Procedure

```bash
R=research/experiments/EXP-0037/ending_route.py
M5="build/re008/roster/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $R local/end001/final-a --frames 32000 --save-at 16500
./invenv.sh python $R local/end001/final-b --frames 32000 --save-at 16500
./invenv.sh python $R local/end001/final-c --start-state local/end001/final-a/checkpoint.mcs --frames 15500
./invenv.sh python $R local/end001/final-m5 --cue "$M5" --frames 24000
./invenv.sh python research/experiments/EXP-0037/m5_glyphs.py \
  local/end001/final-a local/end001/final-m5 build/re008/roster
```

2026-11-04, 20:55-23:20 local; no cold boot and no key press (every run
starts from a saved state). A full run takes about 12 minutes.

## Actual Result

### How the route was found (each failure is in `research_log.md`)

1. Writing the stage byte `0x060CFF88` = 8 after the stage start played stage
   8's scenes and fight, but the win led to stage 1 (`route1`). The stage
   start (`0x06060836`) sets the stage from the order table `0x0607B440`
   [pilot x 10 + index], the index at record + `0x2E3`; a win adds 1 to it
   (`0x06018EE6`).
2. Writing the index too: the win led to index 9, whose entry is 0, and Jin's
   story started again (`route2`). The opponent was still index 0's (Shade
   in machine 5): the arcade start sets player 2 from `0x0604B5C0`/
   `0x0604B650`[row x 16 + index] (`0x06027834`) before the index can be
   written.
3. With the opponent written (Shade in machine 11, as the VS screen showed),
   the win again went back to stage 0 (`route3`).
4. The round-end code (`0x060185A2`) branches to `0x06018DE8`, which sets
   the game mode `0x060CFEDC` = 5, only when `0x060CFF04` is set; that is
   set (`0x060184C6`) only when `0x060CFF07` is non-zero, and
   `0x060CFF07` is set by the opponent routine's caller (`0x06027950`) when
   the next opponent entry is negative (the row's end). Mode 5's handler
   (`0x06017CAE`, table `0x06047F0C`) loads `END.BIN` (`0x06038BC4`) and
   later `KEND*.BIN` (`0x06038BD4`). With the flag written, the ending
   played (`route5`, `route6`).
5. Those runs wrote the stage after the stage start had already run one
   stage-0 step, so scene 21 was posted (caller `0x06061232`, stage 0's
   handler) along with stage 8's scene 14. The untouched image drew both;
   on the M5 image the two scenes' English rows were drawn over each other
   and the scene never ended (`run8`). Writing the index before the stage
   start (the final route) lets the game set stage 8 itself: scene 21 is not
   posted and the M5 image plays the same scenes cleanly.

### Route and checkpoint (final runs)

| | A | B |
| --- | --- | --- |
| Stage 8 at (first poll) | 637 | 633 |
| Scene 14, 15 posted (callers) | 950, 1909 (`0x06061E1C`, `0x06061D42`) | same |
| `END.BIN` read | 17551 | 17551 |
| Scenes 16-19 posted (`0x06066852`) | 18000, 19201, 19599, 20099 | same |
| Disc reads, box calls | 96, 39 | identical, frame for frame |
| Checkpoint | frame 16503, `7e314718…64f2` | frame 16520 |

The route is deterministic: A and B log the same scene posts, disc reads
and box calls at the same frames (the 25-frame polls themselves fall a few
frames apart). The save is
taken while the emulator runs, a few frames after the poll that asks for
it, so the two checkpoints are different instants (their memory differs).
**The checkpoint is A's**: `local/end001/checkpoint/jin_ending_a16503.mcs`,
SHA-256 `7e314718e2f3beaed44c7281d648273d90ae087cbfddce9983392b197eef64f2`,
about 1,050 frames before `END.BIN` is read. Run C, from it, reproduces
A's 43 disc reads and 39 box calls exactly, 16,317 frames earlier.

### Loads (run C, from the checkpoint, frames from the state)

| Frame | Read | When |
| --- | --- | --- |
| 1234 | `END.BIN` | After the win's tally |
| 1325-1365 | `SOUND.LF` (3 reads) | |
| 1375, 1398 | `PL39_0.BIN`, `PL3A_0.BIN` | Portraits |
| 1461-1512 | `STDEMO.CMN`, `STDEM0.PIR`, `STDEM8.PIR` | Scene graphics |
| 1538 | `SE.DAT` | Before scene 16 |
| 1648, 3273, 3753 | Tracks 42, 43, 44 (`JIN_END1`-`3`, D-002) | Scenes 16, 18, 19 |
| 6172 | `FIX.BIN` | After scene 19 |
| 6222 | `KEND.BIN` | Cast roll |
| 6243-6297 | `SOUND.LF` (3 reads) | |
| 6305, 6417 | `KEND_0.BIN`, `KEND_1.BIN` | |
| 6475 | `ST09_FNT.BIN` | |
| 6589, 8801 | Tracks 40, 36 | Cast roll, staff credits |
| 12969 | `QSD.PIX` | QSound notice |
| 13224, 13245, 13467 | `CONTI_0.BIN`, tracks 16, 41 | Game over, initials |
| 14143 on | `OPDEMO.BIN`, `OPS0_*`, `RANKBG.PIX`, `CAPCOM.PIX`, `OPS*0.PIX`, tracks 11, 2 | Ranking and the attract loop |

`KANJI.BIN` is not read after the checkpoint; it was read three times
before the fight (575, 886, 1867).

### Scenes and boxes (run A)

Every ending box is shown by `END.BIN`'s copy of the box routine
(`0x0606268C`, byte for byte `STG0AS.BIN`'s `0x0606E504`) from `END.BIN`'s
own record table `0x060817B4`. The lines are `END.BIN`'s copy of the shared
table (D-008); each was decoded and compared with the screenshots.

| Scene (frame) | Boxes, in order | Lines | Record header (x, y) | On screen |
| --- | --- | --- | --- | --- |
| 16 (18000) | 1072, 408, 409, 493, 410, 411, 412 | 1849 (a blank), 752-759, 897-898 | 140, 172 | Story boxes with portraits over a space background |
| 17 (19201) | 1072, 413 | 760 | 140, 172 | Jin's box, then a white flash |
| 18 (19599) | 414, 415 | 761-764 | 80, 80 and 112, 80 | Typed narration on black, no box |
| 19 (20099) | 605, 416-418, 601, 419-420, 605, 421, 601, 422 | 1010, 765-770, 1006, 771-777 | 136, 172 (first word `0x0030`); names 40 and 76, 172 | A picture, with typed lines below it led by the speaker's name, no box |

Boxes 605 and 601 are the speaker names; they open and close whenever the
speaker changes. Scene 20 (box 550, line 953) is not posted on this route.
Each box's predicted cells (one per character with a table code, the
full-width space drawing none, from `END.BIN`'s code table at file offset
`0x26EAC`, identical to `STG0AS.BIN`'s original 1,222 codes) appear in full
in the cell dumps while it is open, in run A (21 of 21 boxes) and run C.

### Surfaces (run C screenshots, agent-reviewed; every 50 frames)

| Surface | Frames (run C) | Language | Like the story's box? | Sample (SHA-256) |
| --- | --- | --- | --- | --- |
| Win tally (`TARGET DESTROYED`, `BONUS`) | to ~1200 | English | — | `f01020.png` (`21d914a4…7d80`) |
| Ending dialogue boxes, scenes 16-17 | 1683-3280 | Japanese | Yes: portrait and box, story header | `f02069.png` (`3260eff6…2a17`), `f03109.png` (`0f894470…5b60`) |
| Ending narration, scene 18 | 3282-3780 | Japanese | Same routine; no box, white text on black | `f03629.png` (`7242307e…dde8`) |
| Ending captions with speaker names, scene 19 | 3782-6150 | Japanese | Same routine; no box, under a picture | `f04409.png` (`56d90dbb…df73`), `f05189.png` (`3b44d63d…33d4`) |
| Cast roll (`CAST`, portraits, names, "and...", "AS YOU.") | 6589-8800 | **Japanese** names (katakana, one title in kanji) over Latin names | No | `f07276.png` (`b29a715b…9ee7`), `f08056.png` (`deb5723c…060d`) |
| Staff credits (`ARCADE STAFF`, `CONSUMER STAFF`) | 8801-12400 | English | No | `f09096.png` (`58c55296…8d23`) |
| `THANK YOU FOR PLAYING!`, `PRODUCED BY CAPCOM` | ~12400-12960 | English | No | `f12476.png` (`e6c605e9…1c82`) |
| QSound notice (`QSD.PIX`) | 12969-13220 | English, plus **one Japanese trademark line** | No (an image) | `f13102.png` (`d46c3202…2746`) |
| Game over, initials (`CAP` by default) | 13224-14140 | English | — | `f13779.png` (`9e00cf92…cf96`) |
| Ranking, then the attract loop | 14143 on | English | — | `f14829.png` (`3acbdd4b…864e`) |

### M5 image

The final route on the M5 image reaches the same ending, 27 frames later
(scenes 14 and 15 draw their English cleanly at stage 8: a play check of
Jin's last stage). One ending character is predicted to show a pair glyph
there: line 770's first character, glyph 258, one of the build's
`kanji_glyphs`. It does not: box 418's 25 cells match the untouched font in
full on the M5 image, and the screenshot shows the original character.

- `SE.DAT`, read just before scene 16, holds an exact copy of `KANJI.BIN`
  at `0x40000`-`0x67FFF` (163,840 bytes); the M5 build did not change it.
- So the ending's glyph cells very likely come from that copy
  (**SUPPORTED**; `END-002` holds the controlled change).
- On the M5 image, **no line of Jin's ending shows a sacrificed code's pair
  glyph**: the recorded trade-off does not reach this ending.
- Boxes 410 and 420 fell short of a full match in the M5 run, as in an
  untouched control run: the 50-frame dumps missed their last character.
  Every box matched in full in at least one untouched run.

The source image is unchanged.

## Conclusion

**CONFIRMED:** from REF-005 state 4138, four RAM writes before the stage
start (stage index 8, player 2's pilot and machine for index 8, the
opponent word, the last-fight flag) and the vitality hold bring Jin to his
last stage and, after a time-out win, to his ending, with no key pressed.
Two runs agree frame for frame, and a run from the checkpoint reproduces
the ending's disc reads and box calls.

- The win sets game mode 5 only when the last-fight flag is set; mode 5
  loads `END.BIN`.
- `END.BIN` posts scenes 16-19 for this route and shows boxes 408-422, 493,
  601, 605 and 1072 through its own copy of the box routine and its own
  record table `0x060817B4`.
- Japanese is shown by the ending's dialogue boxes, narration and captions,
  by the cast roll's names, and by one line of the QSound notice. The
  credits, tally, game over and ranking are English.
- `KEND.BIN`, `KEND_0.BIN`, `KEND_1.BIN`, `ST09_FNT.BIN` and tracks 40 and 36
  belong to the cast roll and credits; tracks 42-44 to the ending scenes.

**SUPPORTED:** the ending's glyphs come from `SE.DAT`'s copy of
`KANJI.BIN`, not from the copy the stages load.

## Uncertainty and Alternatives

- Scene 20 (box 550) is not posted on this route. Another path (a perfect
  win, a different machine, the 2P side) may post it: `END-003`.
- The route writes the opponent and flag the game would set after the
  previous win; it skips stages 0-7. Anything the earlier stages set, such
  as a score or a count of wins, is not reproduced. The ending seen may
  differ from a played one in such details.
- The cast roll's rendering (sprites, a font in `ST09_FNT.BIN`, `KEND*`
  images) and the QSound line (an image) are not traced: `END-002`.
- Checkpoints are saved while running; their exact frame is not
  reproducible, only the route is.

## Reproduction

Run the procedure. Expect the frames, loads and box calls above, runs A
and B identical, run C equal to A shifted by 16,317 frames, and the M5
check's summary `untouched_full` 21 and `m5_short_of_untouched_cells`
`[410, 420]` (dump sampling).
