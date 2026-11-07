# EXP-0073: Cold-Boot Play Check of the UI Build (UI-007)

Task: UI-007
Status: DONE
Confidence: CONFIRMED (three cold boots of the built image with real pad
presses; the regression reference rebuilds byte for byte)

## Observation

`UI-006` (`EXP-0072`) built the English VS captions and the `SIGNS` setting
and checked them from saved states. The `SIGNS` row's button handling had
been checked only on an interpreter (pad presses cannot be injected,
D-062), and no cold boot had run the build.

## Hypothesis

On cold boots, with real presses, the attract cycle is English with blank
signs, the sub-menu sets and saves `SIGNS`, the saved setting survives a
power cycle and loads the chosen signs, and the VS caption is English.

## Controlled Change

None to the build. Three cold boots of `build/ui006/b` (Track 01
`1feadd13…655b`), asked first: "Yes, run all 3 (Recommended)".

## Prediction

As the hypothesis; no other screen differs from the `opt006` image.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Image | `build/ui006/b`, the command in `data/regression/ui007_ui_text.json` |
| Homes | `EXP-0019/drive.py`'s pad-key home `local/mednafen_route`; boot C with boot B's backup memory (`EXP-0066/boot.py --bkr`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0067/attract.py` | Boot A: no input, every frame recorded, the named-open log |
| `EXP-0019/drive.py`, `EXP-0066/boot.py` | Boots B and C: single presses (one per call), agent screenshots, backup memory kept |
| Agent reads | The settings bytes (`0x060D9295`-`6`) and the city's sign slice in VDP2 VRAM (`0x28D00`-`0x3867F`) against the built versions |
| `EXP-0055/regress.py` | The new reference |

## Procedure

```bash
CUE="build/ui006/b/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python research/experiments/EXP-0067/attract.py local/ui007/attract --cue "$CUE" --frames 7600
./invenv.sh python research/experiments/EXP-0066/boot.py launch local/ui007/bootB "$CUE"
# start (attract), start (title), down, down, a (OPTION MODE), up, a (EXTRA OPTIONS),
# down (SIGNS), right (ENGLISH), start, start (leave, saves); a (ARCADE MODE), a (Jin),
# a, a (BLODIA) to the VS screen; refused or dropped presses sent again (play.json)
./invenv.sh python research/experiments/EXP-0019/drive.py stop local/ui007/bootB
./invenv.sh python research/experiments/EXP-0066/boot.py keep local/ui007/bootB local/ui007/saveB
./invenv.sh python research/experiments/EXP-0066/boot.py launch local/ui007/bootC "$CUE" --bkr local/ui007/saveB/<the .bkr>
# no input until the attract's city demo (VRAM watched); then start x3 (demo end, ranking,
# intro), start (title), down, down, a, up, a, down, right, right, left, start, start
./invenv.sh python research/experiments/EXP-0019/drive.py stop local/ui007/bootC
./invenv.sh python research/experiments/EXP-0055/regress.py ui007_ui_text --out research/experiments/EXP-0073/regress_new.json
```

2026-11-07, 09:59-10:22 local. During boot B the user was using another
application, so presses failed to bring Mednafen forward; asked, the user
said "Go ahead, I'll step away (Recommended)".

## Actual Result

([`play.json`](play.json): every press with its frame, the screenshots'
SHA-256, the saves' SHA-256.)

- **Boot A** (7,600 frames, video `e61aa572…ac55`): the named opens equal
  `EXP-0067`'s frame for frame (`ST00_FNT.BIN` at 4,792); no `ZSIGNS` file
  loads (`BLANK`). One full cycle (`CAPCOM.PIX` at 1,652 and 7,163): every
  screen English; in the city demo the banners are plain orange and white
  (agent-read, every 60th frame).
- **Boot B** (17 presses): OPTION MODE, then `EXTRA OPTIONS` with `NAMES
  ENGLISH` and `SIGNS BLANK` lit (the defaults). Down lit the `SIGNS` row;
  Right lit `ENGLISH`. Leaving saved: the settings read `00 01`. The title
  menu does not return to the attract, so the arcade route followed: Jin's
  story intro in English, then the VS screen with "A Mystery Cyborg
  Appears" in the banner and the Latin names (`f0858bda…`). Its fight
  stage is not the city.
- **Boot C** (power cycle with boot B's save, 15 presses): the settings
  read `00 01` once the save was loaded; in the attract's city demo (frame
  4,900) VDP2 VRAM held the English sign slice byte for byte, and the
  screen showed `SALE`, `BAZAAR`, `BARGAIN SALE` (`851c17a0…`). In
  `EXTRA OPTIONS`, `SIGNS ENGLISH` was lit (kept); Down, Right, Right, Left
  lit `JAPANESE`, `BLANK`, `JAPANESE` (the two `JAPANESE` shots are
  identical); leaving saved `00 02`.
- Presses: in boot B one Start landed during the attract's blueprint fade
  and one Down during the menu's entrance (both ignored), and two were
  refused while Mednafen was not in front (not sent, not logged); in boot
  C one extra Start was needed because the first came at the demo's end.
  No loop was used.
- **Regression** ([`regress_new.json`](regress_new.json)):
  `data/regression/ui007_ui_text.json` rebuilds with every hash equal. The
  nine earlier references rebuilt unchanged with the same tools in
  `EXP-0072` (`regress.json` there).

## Conclusion

The UI build works from cold boots with real presses: English captions,
the `SIGNS` setting saved, kept across a power cycle and loading its signs.
The build is registered as `ui007_ui_text.json`.

## Uncertainty and Alternatives

- The `JAPANESE` signs were not seen on a cold boot (a fourth boot would
  be needed); their VRAM load is `EXP-0072`'s, from a saved state.
- Stages 15 and 16 (also `ST00_FNT.BIN`) were not reached.
- One VS caption was seen on a cold boot; all 54 from saved states.
