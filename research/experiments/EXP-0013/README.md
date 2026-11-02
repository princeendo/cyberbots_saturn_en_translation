# EXP-0013: The M1 Target Line and Its Checkpoint

Task: REF-008
Status: DONE
Confidence: CONFIRMED (the box shown, its script lines, the checkpoint replays it)

## Observation

The play session (`EXP-0011`) recorded Jin's first scene with states every
3 s. The Saturn script's first lines pair exactly with arcade slots 0-6
(D-011), and the arcade draws slots 0-5 in that scene (D-010).

## Hypothesis

Jin's first pre-fight box is Saturn lines 4 and 5, both paired to arcade
slot 2, and the session state at frame 5386 (the box just opened, empty)
replays to that box with identical text pixels.

## Controlled Change

None to the game. One replay of the untouched image from the session state,
in the silent home, through the agent interface.

## Prediction

The replay's finished box equals the session's finished box byte for byte in
the box region.

## Inputs and Provenance

- Session state `local/ref005/session/states/f00005386.mcs`, 1,523,335
  bytes, SHA-256
  `1e8adce30c14262d5b88ae99bcc6c85bb87b9b2638d0042409aceea7f7809b56`
  (fallback: `f00005208.mcs`, during the previous box).
- Session screenshots `f00005386.png` (box empty), `f00005443.png` (first
  line typing), `f00005632.png` and `f00005693.png` (box complete),
  `f00005752.png` (Shade's reply).
- Untouched image (Redump 58190); patched binary `2fc3d547…eaaf`.

## Tools and Environment

`tools/mednafen/replay_state.py` (copied from XvSF; first use here, which
re-validates it on Cyberbots: it loaded the state, stepped, captured and
closed Mednafen, and left both home configs unchanged), ffmpeg 9.0.1 for
crops.

## Procedure

```bash
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/ref005/session/states/f00005386.mcs local/ref008/replay1 \
  --steps 6 --step-frames 50 --agent-dir local/ref008/agent
ffmpeg -v error -i IMAGE -vf crop=268:68:84:166 -f rawvideo -pix_fmt rgb24 - | shasum -a 256
```

## Actual Result

- In the session, the box opens empty at 5386, the first line types by
  5443, the box is complete from 5504 to about 5693, and Shade's reply box
  replaces it at 5752. Speaker: Jin (portrait at left).
- Agent-reviewed: the box's two lines are Saturn lines 4 and 5 (census rows
  `[7528, 26, 4f587e16e11d3a6c, 1]` and `[7556, 24, 85f8f8681dddb582, 1]` in
  `VICTORY.BIN`; the same hashes in `END.BIN` and `STG0AS.BIN`), 13 and 12
  characters. Transcription in the ignored `local/ref008/transcription.txt`.
- Pairing (`data/text/saturn_arcade_pairing.json`): both lines are exact
  matches to arcade slot 2, lines 0 and 1; the English record for slot 2 was
  drawn by the arcade in `EXP-0009` (Jin's first line to Shade).
- Replay: the box region (268×68 at 84,166) of steps 5 and 6 and of session
  frames 5632 and 5693 all hash `c10179ad2f7af072`; steps 1 and 3 show the
  box empty and half typed, as in the session.

## Conclusion

**CONFIRMED.** M1's target is Jin's first pre-fight box, Saturn lines 4-5,
arcade slot 2; checkpoint `f00005386.mcs` reproduces it exactly. The
milestone unit is the **box**: one arcade record, shown as one or two
consecutive Saturn lines, because the official English pairs at record
level (D-011) and the Saturn draws each box as a unit.

## Uncertainty and Alternatives

- Whether the box's text comes from the Shift-JIS table in RAM (and which
  file's copy) is `DBG-004`.
- Replays were compared in the box region only; the background animates.

## Reproduction

Run the procedure; expect the box-region hash `c10179ad2f7af072` at steps 5
and 6.
