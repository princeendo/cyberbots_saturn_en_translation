# EXP-0039: Ending Text in RAM and on Disc, and What Selects the Ending

Task: END-003
Status: DONE
Confidence: CONFIRMED (selection by the winner's pilot byte; per-list posts and boxes for Jin and Santana; credits strings, cast-roll and QSound load paths); SUPPORTED (per-list posts for the other lists, from code only; machine, route and result do not change the text)

## Observation

`END-001` reached Jin's ending: `END.BIN` posted scenes 16-19, not 20.
EXP-0033 matched ending scenes to pilots by number only, believing the
posts named no list. `END-002` found the layers and files. It did not
find where each surface's text sits in RAM, nor what selects the ending.

## Hypothesis

1. A byte set at the last win selects one of several ending routines in
   `END.BIN`. Each routine posts its own fixed scenes with its list number.
2. The other surfaces' text is loaded raw from `KEND.BIN`, `KEND_1.BIN`
   and `QSD.PIX`.

## Controlled Change

Every run starts from the END-001 checkpoint (`7e314718…64f2`), untouched
image, one change each. The control is EXP-0038's control run (same
checkpoint, no change).

| Run | Change | Purpose |
| --- | --- | --- |
| `santana` | On the hit at `0x06018E0C` (right after the round end stores `0x060CFF7E`), write `0x060CFF7E` = 1. Player 1's pilot stays Jin | The ending number alone |
| `pilot` | On the hit at `0x06018DE8` (start of the last-fight round end), write player 1's pilot byte `0x060D02AE` (record `0x060CFFDC` + `0x2D2`) = 1 | The pilot byte, through the game's own copy |
| `arcade` | After `KEND.BIN` is read (+100 frames), RAM `0x06062F1E` `41` to `58`. Write breakpoints on `0x06062F1E`, `0x00280000` and `0x25E20000` (4 bytes each) | Credits text; load paths |
| `thanks` | The same, `0x06063240` `41` to `49` (meant for `THANK YOU`; it is in `SPECIAL THANKS`) | Credits heading |
| `thanks2` | The same, `0x060634EE` `41` to `49` | The thank-you screen |

## Prediction

- `santana` and `pilot`: Santana's ending, list 1. Posts with R4 = 1 for
  scenes 16-22 in that order. The boxes `end_scenes.py` reads for those
  scenes open in order, each drawing its predicted cells.
- `arcade`: the CD copy loop writes `KEND.BIN` to `0x06060000` and
  `KEND_1.BIN` to `0x00280000`, and `QSD.PIX` is written to VDP2 VRAM
  `0x20000`. The heading shows `XRCADE STAFF`.
- `thanks2`: the screen shows `THINK YOU FOR PLAYING!`.

## Inputs and Provenance

- Untouched image, `local/disc_images/cyberbots_saturn_jp_2m/` (`ENV-005`).
- END-001 checkpoint `local/end001/checkpoint/jin_ending_a16503.mcs`
  (`7e314718…64f2`).
- `local/extracted/saturn_jp/`: `END.BIN` `a4868d8d…`, `STG0AS.BIN`
  `3fabb4db…`, `KEND.BIN`, `KEND_1.BIN`, `QSD.PIX`, `SE.DAT` `0430d5e7…`;
  WRAM-H at the cast roll (`local/end002/probe/cast-control/`, EXP-0038) for
  the resident round-end code; `data/text/script_census.json`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`end_scenes.py`](end_scenes.py) (`bf6370c4…`) | Static: dispatchers, step tables, every post call with R4 and R5, each posted scene's opened boxes and lines; checks `END.BIN`'s scene data against `STG0AS.BIN`'s. Writes `data/text/ending_posts.json` (`4aa3e3ae…`) |
| [`ending_probe.py`](ending_probe.py) (`1814168a…`) | EXP-0038's harness (copied, commit `865b649`) plus on-hit writes, writes armed by a file load, a watched byte, and R4 on each post |
| [`check_cells.py`](check_cells.py) (`87c48f1e…`) | Each opened `END.BIN` box's predicted cells against a run's cell dumps |
| `tools/sh2/disasm.py` | `END.BIN` (base `0x06060000`) and the resident code (WRAM-H dump) |

Python 3.13.13; Mednafen 1.32.1 with the agent interface, silent home,
`MEDNAFEN_ALLOWMULTI=1`. The first `santana` and `pilot` runs crashed. The
agent logs each on-hit action as an event line without a `PC` field, and the
decoder did not expect it. Both were rerun after the fix (the action lines
are now logged apart). `ruff format` reflowed the scripts after the runs.

## Procedure

```bash
E=research/experiments/EXP-0039
P=$E/ending_probe.py
export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $E/end_scenes.py --out data/text/ending_posts.json
./invenv.sh python $P local/end003/santana --frames 12000 --cells-until 9000 \
  --onhit 06018E0C:060CFF7E=01 --watch 060CFF7E:1
./invenv.sh python $P local/end003/pilot --frames 12000 --cells-until 9000 \
  --onhit 06018DE8:060D02AE=01 --watch 060CFF7E:1
./invenv.sh python $P local/end003/arcade --frames 13200 --cells-until 0 \
  --write 06062F1E=58 --write-load KEND.BIN:100 --watch 060CFF7E:1 \
  --write-bp 06062F1E-06062F21,26062F1E-26062F21,00280000-00280003,20280000-20280003,25E20000-25E20003
./invenv.sh python $P local/end003/thanks --frames 13000 --cells-until 0 \
  --write 06063240=49 --write-load KEND.BIN:100
./invenv.sh python $P local/end003/thanks2 --frames 12600 --cells-until 0 \
  --write 060634EE=49 --write-load KEND.BIN:100
./invenv.sh python $E/check_cells.py local/end003/santana
./invenv.sh python $E/check_cells.py local/end003/pilot
./invenv.sh python $E/check_cells.py local/end002/control
```

2026-11-05, 10:00-12:40 local; no cold boot and no key press. A run takes
about 15 minutes alone, longer with four in parallel.

## Actual Result

### What selects the ending (code)

- **Round end.** The last-fight round end (`0x06018DE8`, D-034) takes the
  winner's record in R4 (player 1's, `0x060CFFDC`, on this route). It
  copies record + `0x2D2` (the pilot byte) to `0x060CFF7E`, before it sets
  mode 5. The normal-win path (`0x06018E52`) makes the same copy.
- **Dispatch.** In mode 5, `END.BIN`'s `0x06060446` calls the routine at
  `@(0x060775B4 + 4 × [0x060CFF7E])`. That is one of 9 dispatchers, one per
  list 0-8. Each jumps through its own step table, indexed by the step word
  `0x060CFEE8`. Each step routine waits for the running scene to end
  (`0x060CFEB5` = 0), may post the next scene, and advances the step.
- **Posts.** All 41 calls of the post `0x06066852` have constant R4 and R5,
  resolved from the code. In every case R4 equals the list whose dispatcher
  region holds the call. The routine's message is `0x14000000` + R4, and R5
  is the scene. EXP-0033 read only R5.
- **What the step routines read.** Jin's routines read no pilot, machine
  or result variable: only scene, step, timer and display state, and they
  only write `0x060CFF8A`/`0x060CFF8C`. Each of his posts waits only for the
  previous scene to end. The other lists' routines also reference
  `0x060CFFB0`/`0x060CFFB4` (lists 1-5), `0x060CFEF4` (list 2),
  `0x060D81B4` (list 4) and `0x060CFF8F`-`0x060CFF91` (lists 6-8), not
  traced. List 7 reads the machine byte (record + `0x2D3`) to choose a
  sprite. List 5's scene 28 post, the one out of number order, is an
  ordinary step like the others.
- **Unlock flags.** A separate check (`0x060601C8`) runs when
  `0x060CFF7E` > 5. It sets flags in `0x060D9306`-`0x060D930A` and changes
  no scene.

### Per-list ending scenes (`data/text/ending_posts.json`)

| List | Pilot | Dispatcher | Steps | Scenes posted, in step order | Scenes in the list never posted (with EXP-0033's story posts) |
| --- | --- | --- | --- | --- | --- |
| 0 | Jin | `0x06066CF8` | 26 | 16, 17, 18, 19 | 20 |
| 1 | Santana | `0x06067328` | 32 | 16, 17, 18, 19, 20, 21, 22 | — |
| 2 | Mary | `0x060679C4` | 24 | 16 | 15, 17, 18 |
| 3 | Arieta | `0x06067F2C` | 26 | 16, 17, 18, 19, 20, 21, 27, 28 | — |
| 4 | Gawaine | `0x060687B4` | 18 | 16, 17, 18, 19 | 15 |
| 5 | Bao and Mao | `0x06068F14` | 33 | 16, 17, 28, 18, 19, 21, 22 | 20 |
| 6 | Saturn-only | `0x06069668` | 15 | 19, 20 | 17 |
| 7 | Saturn-only | `0x06069958` | 36 | 22, 23, 24, 25, 26 | 21 |
| 8 | Saturn-only | `0x0606A10C` | 18 | 32, 33, 34 | — |

The by-number list (`pilot_census.json`, `ending_scenes_by_number`) was
wrong for Jin (20), Mary (17, 18), Bao and Mao (20) and list 6 (17): those
scenes are never posted. Jin's scene 20 (box 550) is therefore unused by the
code (no constant post; every post call resolved).

- **Scene data.** `END.BIN`'s scene data is `STG0AS.BIN`'s shifted by
  `0x23ED0`: the per-list scene-list table is `0x06086E54`, the records
  `0x060817B4`.
- **Copy check.** All 234 scripts of lists 0-8 open the same boxes in both
  files.
- **Jin's scenes.** The opened boxes read for scenes 16-19 equal the boxes
  END-001 saw, in order: 16 = 1072, 408, 409, 493, 410, 411, 412;
  17 = 1072, 413; 18 = 414, 415; 19 = 605, 416-418, 601, 419-422.

### Selection, forced (`santana`, `pilot`)

| Check | `santana` | `pilot` |
| --- | --- | --- |
| On-hit action | frame 1168, after `0x06018E0C`: `0x060CFF7E` = 1 | frame 1168, after `0x06018DE8`: `0x060D02AE` = 1 |
| `0x060CFF7E` from the next poll | 1 | 1 (copied by the game) |
| Posts (R4, scene) | (1, 16) 1604, (1, 17) 1936, (1, 18) 2147, (1, 19) 2297, (1, 20) 3211, (1, 21) 3744, (1, 22) 4253 | identical |
| Loads | `STDEM1.PIR`, `STDEM7.PIR` (Jin's: `STDEM0`, `STDEM8`); tracks 45-47 (`SAN_END1`-`3`, D-002; Jin's 42-44) | identical |
| Boxes opened | 1072, 423, 424, 603, 425, 604, 426, 603, 427, 604, 428, 603, 429, 430, 431, 603, 432, 611, 433, 603, 434, 603, 435, 436: the predicted boxes, scene by scene | identical |
| Cells | 22 of 22 box openings drew their predicted cells in full | 22 of 22 |
| Screen | Santana and Arieta's dialogue, Santana's portrait; the cast roll starts with Santana (`f02083.png` `ee9c50ef…`, `f04393.png` `46ef00c8…`) | the same |

The two runs log the same disc reads, posts and `END.BIN` box calls. They
differ only after `KEND.BIN` replaces `END.BIN` at `0x06060000`, when the
logged address `0x0606268C` is `KEND.BIN` code. There R5 holds the player's
pilot byte: 0 in `santana`, 1 in `pilot`. The checker run on EXP-0038's
control (Jin): 21 of 21 full.

### Other text in RAM and on disc (`arcade`, `thanks`, `thanks2`)

Write breakpoints from the checkpoint:

| Range | Hit | Written |
| --- | --- | --- |
| `0x06062F1E` | frame 1200 (`END.BIN`), 6170 (`KEND.BIN`, R3 `43414445` = `CADE`) | CD copy loop `0x06041FB4` (D-017) |
| `0x00280000` | frame 6360, R3 `D002C002` = `KEND_1.BIN`'s first bytes (earlier hits at 1341, 1507 are other loads using the same buffer) | `0x06041FB4` |
| VDP2 `0x20000` | frame 12900: `0x06039714` clears VDP2 VRAM from `0x25E19000`; 12933: `0x06041FB4`, R3 `01010101` = `QSD.PIX`'s first bytes | `0x06041FB4` |

| Surface | RAM | Disc | Marker in RAM | On screen |
| --- | --- | --- | --- | --- |
| Staff credits | `0x06060000` + offset (`KEND.BIN`, ASCII strings, NUL-terminated) | `KEND.BIN` from `0x2F1E` (`ARCADE STAFF`) | `0x06062F1E` = `X` | `XRCADE STAFF` (`f09130.png`, `ff6c8583…`) |
| Credits heading | the same | `KEND.BIN` `0x3236` (`SPECIAL THANKS`, arcade staff) | `0x06063240` = `I` | `SPECIAL THINKS` in the arcade-staff block; the consumer-staff `SPECIAL THANKS`, another string, unchanged (`f10110.png`, `656b5685…`) |
| Thank-you screen | the same | `KEND.BIN` `0x34EC` (`THANK YOU FOR PLAYING!`), `0x3504` (`PRODUCED  BY`) | `0x060634EE` = `I` | `THINK YOU FOR PLAYING!` (`f12494.png`, `0a22669b…`) |
| Cast-roll names | WRAM-L `0x00280000` + offset (`KEND_1.BIN`, raw), decoded to WRAM-H `0x060E0000` + VDP1 offset (D-035) | `KEND_1.BIN`; per-name offsets not decoded | EXP-0038 `cast-source`: 16 bytes at `0x002BFF79` | Arieta's katakana changed (EXP-0038) |
| QSound Japanese line | VDP2 VRAM `0x20000` + 512 × row + column | `QSD.PIX`, rows 180-189, x 84-300 | EXP-0038 `qsd` | The line removed (EXP-0038) |
| Ending dialogue | `END.BIN` at `0x06060000` (D-034) | `END.BIN`'s dialogue table (D-008) | EXP-0038 `line` | One character changed (EXP-0038) |

## Conclusion

**CONFIRMED** (`santana`, `pilot`):
- The ending shown is selected by the winner's pilot byte (record +
  `0x2D2`). The last-fight round end copies it to `0x060CFF7E`, and
  `END.BIN` runs that list's routine from `0x060775B4`.
- Forcing 1, either into the byte or into the pilot before the copy, plays
  Santana's ending: list 1's posts, music, graphics and boxes, every box
  drawing its predicted cells.

**CONFIRMED** (code, and Jin's and Santana's runs): each list's ending
posts a fixed sequence of scenes, with the list number in R4. Each scene
opens the boxes of that list's script in `END.BIN`'s copy of the scene
data. `data/text/ending_posts.json` lists every list's posts and boxes. It
replaces `ending_scenes_by_number`.

**SUPPORTED** (code only; lists 2-8 not run):
- the other lists' sequences;
- that the machine, the route and the result change no ending text (true
  of Jin's routines; the variables other lists reference are untraced);
- that Jin's scene 20 is never shown.

**CONFIRMED** (write breakpoints and markers):
- The credits and thank-you text are ASCII strings in `KEND.BIN`, loaded
  raw at `0x06060000` by the CD copy loop.
- `KEND_1.BIN` (cast-roll names) is loaded raw at WRAM-L `0x00280000`.
- `QSD.PIX` is loaded raw at VDP2 VRAM `0x20000`.

## Uncertainty and Alternatives

- Lists 2-8 were not played. A post reached by a path the static reading
  missed (a computed jump) would change their sequence.
- The 2P side was not run; the round end takes the winner's record, so a
  2P win should use player 2's pilot byte (untested).
- The cast roll's per-name data in `KEND_1.BIN` is not located
  (`docs/known_unknowns.md`).
- `KEND.BIN`'s cast-roll code reads the player's pilot byte (R5 at
  `0x0606268C` after it loads); what it uses it for is not traced. The cast
  roll began with Santana in both selection runs.

## Reproduction

Run the procedure. Expect `end_scenes.py` to print the table above
("calls 41 scripts checked 234"), `santana` and `pilot` to post list 1's
scenes 16-22 with 22 of 22 boxes full, and the three markers to show as in
the table.
