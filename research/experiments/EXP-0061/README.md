# EXP-0061: Play Check of the Latin Name Art

Task: LOC-006
Status: DONE
Confidence: CONFIRMED

## Observation

- `EXP-0060`: every built name shows as built from saved states, but the
  select check wrote `STG0A.BIN`'s built part table into RAM (it is resident
  in every state), and versus mode's `SET UP` screen was not seen.

## Hypothesis

From a cold boot, the pilot select, `MACHINE SELECT`, `SET UP` and VS
screens show only the built Latin name art, with no katakana name part;
every earlier regression reference still rebuilds.

## Controlled Change

None to the image: `build/loc005/a` (Track 01 `e1a88dc6…4a6d`). Two cold
boots, driven by single pad presses.

## Prediction

At every screen check, built name parts only (zero katakana parts); the
names read as approved; all eight references match.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Built image | `build/loc005/a` (`data/regression/loc005_name_art.json`) |
| Untouched files | `SELECT.VAD`, `PL3F_0.BIN`, `STG0AS.BIN` (`dialogue.checked`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0019/drive.py` | Cold boot in the pad-key home; one press per call (System Events, only while Mednafen is in front); screenshots |
| [`look.py`](look.py) | Pauses, screenshots, and classifies every 4 bpp sprite: built or katakana name art (VS records first, then the select block) |
| [`summarize.py`](summarize.py) | → [`play.json`](play.json) (with the names the agent read on each screen) |
| `EXP-0055/regress.py` | → [`regress.json`](regress.json) |

`look.py` was first tested from saved states (no key): on the built image
it found 1 built select part (state 2538 + 470) and 6 built VS parts (6448
+ 345), no katakana; on `build/boot004/a` 2 katakana select parts and 12
katakana VS parts, no built ones.

## Procedure

```bash
D="./invenv.sh python research/experiments/EXP-0019/drive.py"
L="./invenv.sh python research/experiments/EXP-0061/look.py"
CUE="build/loc005/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
$D launch "$CUE" local/loc006/arcade
# presses (one per call; the log has each frame): start, start, start (title), a (ARCADE MODE),
# right, right, down, a (Santana), p2a (Arieta), down, a (REPTOS), p2a (BLODIA),
# a, p2a (variants), start (SET UP); $L local/loc006/arcade/agent local/loc006/arcade NAME at each screen
$D stop local/loc006/arcade
$D launch "$CUE" local/loc006/versus
# start, start, start, down, a (VERSUS MODE), right x3, p2left (Gawaine, Bao&Mao), a, p2a,
# down/p2down to FORDY and GULDIN, a, p2a, down, p2down (KILLER BEE, CYCLONE), a, p2a, start
$D stop local/loc006/versus
./invenv.sh python research/experiments/EXP-0061/summarize.py --out research/experiments/EXP-0061/play.json
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin re007_jin_santana re008_roster \
  end010_jin_ending end011_jin_timing end023_roster_endings boot004_boot_warnings loc005_name_art \
  --out research/experiments/EXP-0061/regress.json
```

2026-11-06, 11:33-11:48 local. Two cold boots, asked first: "Yes, run both
(Recommended)". 15 and 32 single presses (`play.json` lists each); some
presses were refused by `drive.py` because Mednafen was not in front, and
were sent again once; presses during a screen's entrance were ignored by
the game and repeated.

## Actual Result

### Play check (`play.json`)

| Boot | Screen | Names read | Built parts |
| --- | --- | --- | --- |
| arcade | pilot select | Jin, Mary, Santana (P1); Arieta (P2) | 2 each |
| arcade | `MACHINE SELECT` | Latin labels only | 0 |
| arcade | `SET UP` | Santana, Arieta | 2 |
| arcade | VS | REPTOS RF-004, Santana; BLODIA BX-02, Arieta | 6 |
| versus | pilot select | Jin, Santana, Gawaine (P1); Arieta, Bao&Mao (P2) | 2 each |
| versus | `MACHINE SELECT` | Latin labels only | 0 |
| versus | `SET UP` | Gawaine, Bao&Mao | 2 |
| versus | VS | F·KILLER BEE F7900J, Gawaine; G·CYCLONE GP-02, Bao&Mao | 6 |

- 43 and 32 screen checks (26 and 24 with name art on screen): **no
  katakana name part on any**.
- Arcade mode came up with player 2 already joined (Arieta on the right at
  the first select screen; the reason was not traced). The game held the
  select until player 2 chose, then ran a two-player match with a
  `SET UP` screen, so the arcade boot also saw `SET UP`.
- `MACHINE SELECT` takes a body type and then a variant (D-054); the
  first boot sat on the variant step until each player pressed again.
- Down presses on the pilot select did not move either cursor to the
  second row (Devilotte, Chiyomaru, Shade).

### Regression (`regress.json`)

All eight references (`re003_jin` … `boot004_boot_warnings`,
`loc005_name_art`) rebuild with every replacement file, Track 01, the cue
and every prediction, change and ending hash they record.

## Conclusion

Prediction met. The Latin name art shows from a cold boot on every name
surface, with the select part table read from the disc; the build is
locked as `data/regression/loc005_name_art.json` (no new image).

## Uncertainty and Alternatives

- Ten of the 34 names were seen on cold boots; the rest from saved states
  (`EXP-0060`), on the same code path.
- The second grid row was not reached on a cold boot; how it is reached is
  `SPECIAL-001`'s question.
- Bank-63 frames `0x70` and `0x74`-`0x79` stay as they are (not seen on any
  screen; `docs/coverage_exceptions.md`).

## Reproduction

Run the procedure (two cold boots with presses: ask the user first).
Expect `play.json` (screens and counts; frames will differ) and
`regress.json` as committed.
