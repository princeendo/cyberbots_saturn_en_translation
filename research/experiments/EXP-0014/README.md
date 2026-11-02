# EXP-0014: Dialogue Selection From One Checkpoint

Task: DBG-002
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0013` replayed the M1 checkpoint once and got Jin's box (Saturn lines
4-5) byte-identical to the session. Both siblings found that their post-fight
quote could vary between replays of one state (a random pick), and that
frames after a state load shift by a few frames.

## Hypothesis

Story dialogue is script-driven, not random: every replay of the checkpoint
shows the same box, followed by the same reply, possibly with a frame-level
timing offset.

## Controlled Change

None to the game. The same states replayed repeatedly in the silent home.

## Prediction

The completed box and the following reply have the same box-region hash in
every run; intermediate frames may differ by typing progress.

## Inputs and Provenance

States from `EXP-0011`: `f00005386.mcs` (`1e8adce3…`, Jin's box just
opened) and `f00005208.mcs` (`71aba73e…`, the previous box, the
introduction). Untouched image; patched binary `2fc3d547…eaaf`.

## Tools and Environment

`tools/mednafen/replay_state.py` (re-validated in `EXP-0013`); ffmpeg crop
`352x72+0+168` (the dialogue strip) hashed as raw RGB.

## Procedure

```bash
CUE="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
for n in 2 3 4; do
  ./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
    local/ref005/session/states/f00005386.mcs local/dbg002/a$n \
    --steps 8 --step-frames 50 --agent-dir local/dbg002/agent
done
for n in 1 2; do
  ./invenv.sh python -m tools.mednafen.replay_state "$CUE" \
    local/ref005/session/states/f00005208.mcs local/dbg002/b$n \
    --steps 12 --step-frames 50 --agent-dir local/dbg002/agent
done
```

Plus `EXP-0013`'s `local/ref008/replay1` (6 steps from `f00005386`).
16:49:43-16:50:56 local.

## Actual Result

Dialogue-strip hash per step (first 6 hex digits):

| Run | From | Steps 1-8 (… 12) |
| --- | --- | --- |
| replay1 | 5386 | b7cfa0 ee9760 88b13f b9f7bd **ead786 ead786** |
| a2 | 5386 | 264e3b 6f6ab2 99e55a **ead786 ead786 ead786** 16e5a3 d04251 |
| a3 | 5386 | b7cfa0 ee9760 88b13f b9f7bd **ead786 ead786** 16e5a3 d04251 |
| a4 | 5386 | 264e3b 6f6ab2 99e55a **ead786 ead786 ead786** 16e5a3 d04251 |
| b1 | 5208 | e7afda e7afda 3d8fbe 3d8fbe 0efd14 79a223 780fdc **ead786 ead786** 9f8f08 3891a4 2109ec |
| b2 | 5208 | e7afda e7afda 3d8fbe 3d8fbe 0efd14 45d367 bb972b **ead786 ead786** 9f8f08 3891a4 ca1f31 |

- Every run reaches the same completed Jin box (`ead786`, Saturn lines 4-5)
  and then the same Shade reply (`16e5a3`, `d04251`; the b runs' `9f8f08`,
  `3891a4` are later frames of it).
- Runs from one state fall into two timing variants: replay1 and a3 are
  identical at every step, as are a2 and a4, and the a2/a4 variant is a few
  frames ahead (its box completes one step earlier). Full-frame hashes at
  steps 1 and 4 show the same two variants; step 8 is identical in all three
  a runs.
- Agent review of the differing frames: they differ only in how far the
  text has typed or in the portrait's mouth frame, never in text or speaker.
- Source manifests identical before and after; both home configs unchanged.

## Conclusion

**CONFIRMED:** from a checkpoint, the dialogue is fixed: the same box and the
same reply in all six runs, from two different states. Replays shift by a
few frames, so comparisons must use completed boxes (or the box region at a
settled moment), not frame-aligned whole screens.

## Uncertainty and Alternatives

- Only one scene was tested. Branches that depend on play (a win or loss, a
  route) are not covered by replaying a fixed state.
- The cause of the two timing variants (when the load lands within a frame)
  is not established; it matches the siblings' observation.

## Reproduction

Run the procedure; expect `ead786` for the completed box in every run.
