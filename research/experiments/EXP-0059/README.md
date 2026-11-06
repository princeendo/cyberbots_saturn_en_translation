# EXP-0059: Latin Name Art Samples, and the User's Choices

Task: LOC-004
Status: DONE
Confidence: CONFIRMED (samples drawn on the real screens; the user's decisions)

## Observation

- D-052: no Latin pilot or mech name art exists; the select names are raw
  4 bpp parts in `SELECT.VAD`, the VS names compressed records in
  `PL3F_0.BIN`.
- The US arcade's name art: pilots in mixed case, `SHADE` and mechs in
  capitals, no model codes (`EXP-0056`).

## Hypothesis

Latin names set in the game's arcade letters fit the Saturn's banners and
read well on both screens.

## Controlled Change

None to the disc. From saved states, sample banners written into the name
parts' patterns (VDP1 VRAM for the select; its WRAM-H copy for the VS
screen), one screenshot each.

## Prediction

Every sample fits its banner; long mech names collide with the model code
where it sits.

## Inputs and Provenance

Session states 3070 (select) and 6805 (VS); the arcade letters
(`local/layout001/font/arcade_font.json`); the banner palettes read from
colour RAM (`0x61E0`/`0x41E0` names: 1 gold, 2 orange, 3 red, 4 dark red,
5 darker red, 6 bar red, 15 pale yellow; `0x41C0` mechs: blue ramp 1-6,
codes 8-12, 15 white).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`banner.py`](banner.py) | A name banner as 4 bpp pixels (bar, centred letters, two added glyphs `&` and `·`) |
| [`sample.py`](sample.py) | Draws samples over the live name parts (positions, flips and sources from the VDP1 command list) |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0059/sample.py select local/loc004/sel
./invenv.sh python research/experiments/EXP-0059/sample.py vs local/loc004/vs
```

2026-11-06, 10:30-11:20 local. No key, no cold boot.

## Actual Result

- The select names fit the 120-pixel banner (longest, "Devilotte" and
  "Chiyomaru", 72 pixels); the VS pilot name the same; mech names fit the
  144-pixel two-part banner.
- Findings on the way:
  - the select name parts are drawn vertically flipped and the VS mech's
    right part horizontally flipped (command word 0, bits 4-5); the sampler
    now un-flips per part;
  - on the VS screen VDP1 VRAM `0x10000` up is refreshed each frame from
    WRAM-H `0x060F0000` up, so writes to VRAM there do not show;
  - the two colour styles tried differ little (the name palette's lightest
    colour is pale yellow), so colour was not put to the user;
  - "R·LIGHTNING" and "KILLER BEE" overlap the model code where it sits.
- Sheets sent to the user (ignored `local/loc004/`): `sheet-vs.png`,
  `sheet-select.png`, `sheet-vs-long.png`.
- The user's decisions are verbatim under `GATE-TRANSLATION extension for
  the name art` in `TASKS.md`: arcade letters in the banners; US arcade
  case; model codes kept after the name; "Devilotte". The spellings are in
  `data/translations/name_art.json`.

## Conclusion

Prediction met. The Latin name art is decided; `LOC-005` builds it.

## Uncertainty and Alternatives

- Samples were drawn into RAM only; on disc, the VS names must fit
  `PL3F_0.BIN`'s records (D-052), which needs more of the type-2 format or
  other room.
- The `&` and `·` glyphs are new; their shape is checked again in
  `LOC-005`'s screens.

## Reproduction

Run the procedure; compare the screenshots with `samples.json` in each
output folder.
