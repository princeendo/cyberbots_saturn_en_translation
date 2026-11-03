# EXP-0022: What Selects Each Box; Jin's Boxes; Forcing a Scene

Task: RE-002
Status: DONE
Confidence: CONFIRMED (selector chain, Jin's scene list and order, box list, forcing); SUPPORTED (scenes 16-20 are the ending, from `END.BIN`'s posts)

## Observation

The M1 box is drawn from the record at `0x0609D184` (D-020). The typing
routine gets its record as `@(table + index × 4)` (`0x0606E5B6`). Dialogue is
fixed from a checkpoint (D-014).

## Hypothesis

A per-pilot, per-stage scene number, written by the stage code, picks a
script, and the script names the box indices. Writing the scene number
before the scene starts shows another scene's boxes.

## Controlled Change

- **Traces** (no change to the game): PC and write breakpoints from the
  REF-005 states 4138, 4493 and 5208.
- **Forcing:** a one-shot write of the scene byte right after the game writes
  it. The control is the same run without it.

## Prediction

A short chain from stage code to record, found in the code. Forcing scenes 4,
9 and 15 draws exactly their first boxes' predicted cells; the control draws
scene 0.

## Inputs and Provenance

- REF-005 states `f00004138.mcs` (`3eb789da…`), `f00004493.mcs`
  (`0b52c695…`) and `f00005208.mcs` (`71aba73e…`), and all 166 states for the
  stage-byte scan.
- `STG0AS.BIN` and `END.BIN` from `local/extracted/saturn_jp/`; `KANJI.BIN`
  for the cell predictions (D-019).
- Untouched image (Redump 58190); all 63 components unchanged after the work
  (`local/logs/re002-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/mednafen/replay_state.py` | PC, read and write breakpoint logs, and one halt (`--halt-pc 0606E504`) |
| `tools/sh2/disasm.py` | The script interpreter, the box function, the scene start, the message queue and the stage handlers |
| [`box_list.py`](box_list.py) | Jin's scenes, boxes, records and lines, from the game's tables (writes `data/text/jin_boxes.json`) |
| [`force_scene.py`](force_scene.py) | The forcing harness (debug only; never ships) |
| [`check_cells.py`](check_cells.py) | Forced run's cells against the predicted first box |

Scratch scans: the scene-post constants in `STG0AS.BIN` and `END.BIN`, and
the stage byte in the 166 states.

## Procedure

```bash
CUE="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
S=local/ref005/session/states
R=tools.mednafen.replay_state
./invenv.sh python -m $R "$CUE" $S/f00005208.mcs local/re002/sel1 --steps 16 --step-frames 50 \
  --bp pc:0606E5B6 --agent-dir local/re002/agent-s
./invenv.sh python -m $R "$CUE" $S/f00005208.mcs local/re002/call1 --steps 16 --step-frames 50 \
  --bp pc:0606E504 --halt-pc 0606E504 --agent-dir local/re002/agent-c
./invenv.sh python -m $R "$CUE" $S/f00004493.mcs local/re002/scene1 --steps 24 --step-frames 50 \
  --bp read:060AA840-060AAD7B,260AA840-260AAD7B --agent-dir local/re002/agent-r
./invenv.sh python -m $R "$CUE" $S/f00004138.mcs local/re002/scenew1 --steps 30 --step-frames 50 \
  --bp write:06008284-0600828B,26008284-2600828B --agent-dir local/re002/agent-w
./invenv.sh python -m $R "$CUE" $S/f00004138.mcs local/re002/post1 --steps 30 --step-frames 50 \
  --bp write:060DAF78-060DB177,260DAF78-260DB177 --agent-dir local/re002/agent-p
./invenv.sh python research/experiments/EXP-0022/box_list.py \
  local/extracted/saturn_jp/STG0AS.BIN --out data/text/jin_boxes.json
./invenv.sh python research/experiments/EXP-0022/force_scene.py local/re002/force-control
for s in 4 9 15; do
  ./invenv.sh python research/experiments/EXP-0022/force_scene.py local/re002/force-$s $s
  ./invenv.sh python research/experiments/EXP-0022/check_cells.py local/re002/force-$s $s
done
```

18:05-18:28 local, 2026-11-02, the user present.

## Actual Result

### The selector chain, top to bottom

1. **Stage flow.** `0x06061210` dispatches on the stage byte `0x060CFF88`,
   through the table `0x0609353C` (16 stage groups), then on the step byte
   `0x060CFF89`, through each group's step table.
   - `0x060CFF88` is 0 through Jin's first stage and 1 after the first fight
     (session states 13139 to 13492, when `STG0AS.BIN` reloads).
2. **Scene post.** Step handlers post the scene with constants. For example,
   stage 0, step 0 (`0x0606123C`) has `mov #21,r5`, and step 7 (`0x060612BA`)
   has `mov #0,r5`. Then they jump to `0x0606DBEA`.
   - That routine queues message `0x14000000` with the scene number in the
     queue at `0x060DAF78` (via `0x0602C13x`).
   - The queue loop (`0x0602C224`) starts the scene task (`0x0606E1E8`)
     through `0x0600D358`, with R6 = the scene number. Seen: scene 21 at
     frame 794 and scene 0 at frame 1474, from 4138.
3. **Scene start** (`0x0606E1E8`). The task is `@0x0600800C` (here
   `0x06008268`).
   - The pilot is the byte at task + `0x1F` (0 for Jin), and it picks a scene
     list from `0x060AAD24`. Jin's list is `0x060AA840`: 22 scripts.
   - The scene is the byte at task + `0x23`, and it picks the script. A read
     breakpoint on the scene lists logs exactly these two reads per scene
     (`0x0606E220`, `0x0606E22E`).
4. **Script** (`0x0606E230`). This is 16-bit bytecode:
   - `0xE000` ends the scene;
   - `0xE1xx`-`0xEAxx` and `0xC000`-`0xDFFF` are other commands;
   - `0xFFFF` is a separator;
   - a word below `0x8000` shows box N, by calling `0x0606E504` with the table
     `0x060A5684`, and the same word with `0x8000` closes it.
   - A halt at `0x0606E504` gives R5 = `0x060A5684` and R6 = 2 for the M1 box.
5. **Record.** `0x060A5684` holds 1,074 pointers (1,066 distinct records,
   32 bytes apart): an 8-byte header (0, x, y, attribute), then 8-byte entries
   (line pointer, word), where `0xFFFF` continues.
   - Box 2 → `0x0609D184` → lines 4-5. A PC log at `0x0606E5B6` from 5208 shows
     boxes 2, 3 and 4 in turn (frames 427, 679 and 951).

### Jin's scenes (`data/text/jin_boxes.json`)

Jin's stage code (stage groups 0-8) posts 17 scenes, in this order:

| Stage | Step 0 | Step 7 (or as noted) |
| --- | --- | --- |
| 0 | 21 (the opening narration) | 0 |
| 1 | 1 | 2 |
| 2 | 3 (`r14` = 3; not a branch) | 4 |
| 3 | 5 | 6 |
| 4 | 7 | 8 |
| 5 | 9 (8-step group) | — |
| 6 | 10 | 11 |
| 7 | 12 | 13 |
| 8 | 14 (step 4) | 15 (step 8) |

So step 0 runs when a stage starts (after the previous fight) and step 7
before its fight.

- **Boxes and lines.** Those 17 scenes show boxes 0-62, with no gaps, all from
  `STG0AS.BIN`.
  - The boxes hold Saturn lines 0-120, except line 34.
  - Line 34 is dead data: the second entry of box 18's record, after an entry
    whose word `0000` ends the box.
  - 43 boxes have 2 lines, 13 have 1, and 7 have 3.
  - Dialogue boxes have x = 140 (61 boxes) and the narration x = 80 (2); all
    have y = 172 and attribute 14.
- **Scenes 16-20** (boxes 408-422, 493, 550, 601, 605, 1072; lines 752-777,
  897-898, 953, 1006, 1010, 1849) are not posted by `STG0AS.BIN`'s code.
  - `END.BIN` has the same post routine, at `0x06066852`, and its 41 posts use
    scenes 16-34. Scene 16's script bytes are in `END.BIN` at `0x06082CD8`.
  - They are Jin's ending (SUPPORTED) and are excluded (rule 23).
- **`VICTORY.BIN`** has no copy of the post routine; its role is not known.
- **Other pilots:** the other blocks of posts in `STG0AS.BIN` (187 posts, 17
  per block) follow the same pattern, with extra scenes; they are out of
  scope here.

### Forcing (from state 5208, 24 × 25 frames)

In the forced runs, a one-shot write of the scene byte `0x0600828B` lands
right after the game's own writes there: 4 log events each.

| Run | First box predicted (cells) | Best leading match | Screen (agent-reviewed) |
| --- | --- | --- | --- |
| control | scene 0, 25 | 25 (step 18) | the M1 box |
| scene 4 | 5 | 5 (step 12) | Jin, a one-line box |
| scene 9 | 20 | 20 (step 20) | Jin, a two-line box |
| scene 15 | 14 | 14 (step 18) | Jin, another portrait, one line |

The control matches none of the three forced boxes (0 cells each). The stage
background is stage 1's in every run, because only the scene was changed.
Every box was predicted from `jin_boxes.json`, the lines and the font.

## Conclusion

**CONFIRMED:**

- A story box is chosen in this order: the stage handler's constant scene
  number, then the pilot's scene list (`0x060AAD24`, Jin `0x060AA840`), then
  that scene's bytecode script, then the box index, then the record
  (`0x060A5684`), then its lines.
- Jin's story posts scenes 21 and 0-15 in a fixed order over stages 0-8, with
  no branches in that code. They show boxes 0-62 and lines 0-120, except the
  dead line 34.
- Writing the scene byte right after it is set shows any chosen scene. Three
  forced scenes drew exactly their predicted cells.

## Uncertainty and Alternatives

- Losing a fight, continues and the 2P side were not traced. A loss may
  repeat a stage's scenes, or post others.
- The task address `0x06008268` is the one this replay uses (deterministic
  from 5208). Another state may allocate the scene task elsewhere: check the
  write breakpoint's log before trusting a forced run.
- Forcing a scene keeps the current stage's background and opponent sprites;
  the dialogue's own portraits follow the script.
- The meaning of most commands (`0xC000`-`0xDFFF`, `0xE1xx`-`0xEAxx`) is not
  traced, beyond what `box_list.py` needs.

## Reproduction

Run the procedure. Expect the chain above, `jin_boxes.json` with SHA-256
`b4b21c45…`, and the forcing table.
