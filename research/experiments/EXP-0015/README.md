# EXP-0015: Named Checkpoints Around the M1 Box

Task: DBG-003
Status: DONE
Confidence: CONFIRMED

## Observation

The M1 box (Jin's first pre-fight box, Saturn lines 4-5) is reached by
replaying the session state `f00005386.mcs` (`EXP-0013`), and its content is
fixed across replays, with a few frames of timing jitter (D-014). `DBG-004`
needs states before, during and after the box for memory comparison.

## Hypothesis

States saved through the agent at chosen frame offsets after loading
`f00005386.mcs` replay to, respectively, the box typing out, the completed
box, and the reply that follows it.

## Controlled Change

None to the game. States saved by the agent in the silent home.

## Prediction

Replaying checkpoint A reaches the completed box (`ead786`); B starts on it;
C never shows it.

## Inputs and Provenance

`local/ref005/session/states/f00005386.mcs` (`1e8adce3…9b56`); untouched
image; patched binary `2fc3d547…eaaf`.

## Tools and Environment

[`capture.py`](capture.py) (loads the state, runs `frames N`, screenshots,
resumes, saves a state at once, screenshots again);
`tools/mednafen/replay_state.py`; dialogue-strip crop `352x72+0+168` hashed
as raw RGB.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0015/capture.py \
  local/ref005/session/states/f00005386.mcs local/dbg003/run2
for c in a-box-open b-box-complete c-after-box; do
  ./invenv.sh python -m tools.mednafen.replay_state \
    "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
    local/dbg003/run2/$c.mcs local/dbg003/verify-$c \
    --steps 6 --step-frames 50 --agent-dir local/dbg003/agent
done
```

## Actual Result

- **Run 1** (offsets 1, 300, 420): the screenshots one frame after the load
  were blank; at 300 frames the box was complete at the halt, but in the
  5 frames before the state was saved Jin's box closed and Shade's opened,
  so that state was not "box complete". Discarded (kept in
  `local/dbg003/run1/`).
- **Run 2** (offsets 10, 200, 420; launch-relative frames: load at 185,
  saves at 199, 399, 626):

| Checkpoint | SHA-256 | Size | Screenshots | Replay, dialogue strip per 50 frames |
| --- | --- | ---: | --- | --- |
| A `a-box-open` | `236c610eb7432cfd58109d74f9bf9b8bfa601fe323f7fc2640f8c854efa2ddfc` | 1,537,497 | blank (display not yet redrawn after the load) | f5e722 22c160 bd21cb **ead786 ead786** 560d35 |
| B `b-box-complete` | `b32db0c256308bd4048585e01bea4bce5603cad53977cc20c8cd6af8c7ce4cdd` | 1,645,329 | completed Jin box at the halt and after the save | **ead786** e819eb b386f5 77cfd1 570885 570885 |
| C `c-after-box` | `e21021b11b3c19a110dcfbda2442fbc8e7f888ab5fb1b8b07f51a3bc13ecd7ed` | 1,644,315 | Shade's reply, complete | 51fc96 570885 4581ec 4e163d a3927d 34bb4e |

- The states are copied to the ignored `local/checkpoints/m1/` with the
  session state (`session-f00005386.mcs`).
- Source manifests identical before and after; both home configs unchanged.

## Conclusion

**CONFIRMED:** checkpoint A replays to Jin's box typing out and completing;
B starts on the completed box; C is after it (Shade's reply, `570885`, which
B also reaches). These are the M1 checkpoints.

## Uncertainty and Alternatives

- A state saved one or ten frames after a load shows a blank screen in its
  own screenshots; the replay is the evidence for A, not its screenshot.
- B's box closes about 300 frames after the session state; a state saved
  later than about 290 frames is no longer "box complete".

## Reproduction

Run the procedure; expect the dialogue-strip hashes in the table (timing may
shift by one step, D-014).
