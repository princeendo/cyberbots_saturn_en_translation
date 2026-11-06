# EXP-0055: Play Check of the English Boot Warnings

Task: BOOT-005
Status: DONE
Confidence: CONFIRMED

## Observation

- `EXP-0054`: the built image (M8 plus the English boot warnings) shows each
  warning under its condition exactly as generated.
- D-048: what a button does on each warning was SUPPORTED only (code and the
  screens' words); a RAM-written button was not seen by the CPU.

## Hypothesis

One real pad press continues the game on `WARNING0` and `WARNING4` and calls
the BIOS (the control panel) on `WARNING1`-`3`; a normal boot reaches the
title; every earlier regression reference still rebuilds.

## Controlled Change

Per boot, one backup-memory condition and one A press, 120 frames after the
warning appears. The normal boot has no press.

## Prediction

| Case | Warning | After A |
| --- | --- | --- |
| damaged | 0 | the game goes on and rewrites the save (`0x06036A1C`, `0x06036A58`) |
| zero, cart-zero, both-zero | 1, 2, 3 | the BIOS routine at the `0x0600026C` vector (`0x0000186C`); the control panel |
| free4 | 4 | the game goes on (`0x06036D8A`), no save written |
| normal | none | the title, with no key |

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Built image | `build/boot004/a`, Track 01 `ef27ebc6…fe25` (`data/regression/boot004_boot_warnings.json`) |
| Fixtures | as `EXP-0051` (`local/boot001/fixtures/`) |
| BIOS vector | `0x0600026C` holds `0x0000186C` (WRAM-H of `EXP-0051`'s `zero` state, `mcs_extract`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`press.py`](press.py) | Cold boot in `EXP-0019/drive.py`'s pad-key home with the fixtures; log-mode breakpoints; one press through System Events (only while Mednafen is in front); screenshots |
| [`summarize.py`](summarize.py) | → [`play.json`](play.json) |
| [`regress.py`](regress.py) | Rebuilds earlier references with outputs and records redirected → [`regress.json`](regress.json) |

## Procedure

```bash
F=local/boot001/fixtures; P=research/experiments/EXP-0055/press.py; O=local/boot005
./invenv.sh python $P $O/damaged --bkr $F/damaged.bkr
./invenv.sh python $P $O/zero --bkr $F/zero.bkr
./invenv.sh python $P $O/cart-zero --bkr $F/save.bkr --bcr $F/cart_zero.bcr --cart backup
./invenv.sh python $P $O/both-zero --bkr $F/zero.bkr --bcr $F/cart_zero.bcr --cart backup
./invenv.sh python $P $O/free4 --bkr $F/free4.bkr
./invenv.sh python $P $O/normal --bkr $F/save.bkr
./invenv.sh python research/experiments/EXP-0055/summarize.py --out research/experiments/EXP-0055/play.json
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin re007_jin_santana \
  re008_roster end010_jin_ending end011_jin_timing --out research/experiments/EXP-0055/regress.json
```

2026-11-06, 08:04-08:16 local. Six cold boots and five single A presses,
asked first: "Yes, run all 6 (Recommended)".

## Actual Result

### Play check (`play.json`)

| Case | Warning | A press (logged frame) | Then | Screen after |
| --- | --- | --- | --- | --- |
| damaged | 0 | 1623 | `0x06036A1C`, save rewritten (`0x06036A58`, frame 1600) | NOW LOADING, then the opening |
| zero | 1 | 1610 | BIOS `0x0000186C` (frame 1588) | the Saturn control panel ("Start Application") |
| cart-zero | 2 | 1609 | BIOS | the control panel |
| both-zero | 3 | 1609 | BIOS | the control panel |
| free4 | 4 | 1612 | `0x06036D8A`, no save written | the opening |
| normal | none | no key | save accepted (`0x06037064`) | the title, `PRESS START BUTTON` (frame 3720) |

- Each warning screen equals `EXP-0054`'s for the same case (same hash).
- After the BIOS call the BIOS's own code runs at the same work-RAM
  addresses, so breakpoint hits there are not the game's: one run logged 1.2
  million of them. `summarize.py` stops at the BIOS hit.
- `0x06036A1C` and `0x06036D8A` are also passed on the normal path (save
  found and accepted), so they mark "the check went on", not a warning
  alone.

### Regression (`regress.json`)

`re003_jin`, `re007_jin_santana`, `re008_roster`, `end010_jin_ending` and
`end011_jin_timing` rebuild with every replacement file, Track 01, the cue
and the prediction, change and ending hashes they record. `end023` is
reproduced by `EXP-0054`; `boot004` is new.

## Conclusion

Prediction met. A button press does what the English says on every
warning; the normal boot reaches the title; every regression reference
holds. The boot warnings are done.

## Uncertainty and Alternatives

- Only button A was pressed; the code treats the seven pad bits alike
  (D-048).
- Record hashes of the older references are not compared: they describe
  builds that later records superseded (each reference says so).

## Reproduction

Run the procedure (six cold boots with presses: ask the user first).
Expect `play.json` and `regress.json` as committed.
