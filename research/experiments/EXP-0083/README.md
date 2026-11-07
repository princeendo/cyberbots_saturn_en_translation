# EXP-0083: Cold-Boot Play Check of the Saturn-Only Pilots' English (SPECIAL-018)

Task: SPECIAL-018
Status: DONE
Confidence: CONFIRMED (three cold boots of the built image with real pad
presses; agent-reviewed screenshots; the new reference rebuilds byte for
byte)

## Observation

`SPECIAL-017` (`EXP-0082`, D-068) built lists 6-8's English and checked
every box from saved states of the untouched image. No cold boot had run
the image, and list 7 had not been reached by its real route.

## Hypothesis

On cold boots, choosing Devilotte (one left of Jin), SHADE (two left) and
Chiyomaru (three left) plays each pilot's story in English.

## Controlled Change

None to the build (`build/sp017/a`, Track 01 `f6789cae…`). Three cold
boots, asked first: "Yes, run all 3 (Recommended)".

## Prediction

Each boot reaches the pilot's stage group (54, 72, 63) and shows its story
scenes in English.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Image | `build/sp017/a`, the command in `data/regression/special018_saturn_only.json` |
| Home | `EXP-0019`'s pad-key home (`local/mednafen_route`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `research/experiments/EXP-0027/play_route.py` | Cold boot to a pilot (`--moves`), scene-post log, a screenshot and the glyph cells every 1.5 s; `--no-fight-keys`, `--until-stage 1` |
| `research/experiments/EXP-0055/regress.py` | The new reference |

## Procedure

```bash
CUE="build/sp017/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"; RP=research/experiments/EXP-0027/play_route.py
for spec in devilotte:left shade:left,left chiyomaru:left,left,left; do n=${spec%%:*}; m=${spec#*:}
  ./invenv.sh python $RP "$CUE" local/sp018/play-$n --moves "$m" --until-stage 1 --no-fight-keys \
    --select-wait 10 --move-wait 3; done
./invenv.sh python research/experiments/EXP-0055/regress.py special018_saturn_only \
  --out research/experiments/EXP-0083/regress_new.json
```

2026-11-07, 14:36-15:33 local.

## Actual Result

([`play.json`](play.json): every key with its frame, the posts, the stage
groups and the reviewed screenshots' SHA-256.)

| Boot | Keys (single presses) | Story posts | Stage groups | Seen in English (agent-read) |
| --- | --- | --- | --- | --- |
| Devilotte | Start, A, Left, A, A, A | 18, 0 | 54 | the opening narration typing "Devilotte,"; scene 0 "Father! I... I have given my heart to a gentleman!!" with her portrait |
| SHADE | Start, A, Left, Left, A, A, A (one more press refused: Mednafen was not in front; not sent) | 0, 1, 2, 3 | 72 | the opening narration typing "But then, something no one expected happe…" |
| Chiyomaru | Start, A, Left, Left, Left, A, A, A | 0, 1, 2, 3, 4 | 63, 64 | the opening narration "his son Chiyomaru went to see Tessan, genius strategist and his father's right hand."; stage 63 "! What!?" (Tessan); after the first win, stage 64 "Say no more! For now, my l…" (typing) |

- **List 7's real route:** three lefts from Jin picked Chiyomaru (stage
  group 63, D-065).
- **First fights:** `play_route.py` holds the fight in RAM only at the
  stage step 14 (Jin's). Chiyomaru's fight is at step 14 and was won at
  time-out; Devilotte's (step 13) and SHADE's (step 20) were lost, so those
  runs ended in the title after their stories' first scenes. Their later
  scenes were checked from saved states in `EXP-0082`.
- **Reference:** `data/regression/special018_saturn_only.json` rebuilds
  with every hash equal (`regress_new.json`).

## Conclusion

The built image plays the Saturn-only pilots' stories in English from cold
boots, list 7 by its real route. It is registered as
`special018_saturn_only.json`.

## Uncertainty and Alternatives

- Devilotte's and SHADE's boots stopped at their first fight; their stories
  past it, and every pilot's ending and quotes, rest on `EXP-0082`'s
  saved-state checks.
- `play_route.py`'s fight hold assumes step 14; for these pilots the fight
  step differs (13, 20).
