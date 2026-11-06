# EXP-0066: Play Check of the Names Switch

Task: OPT-006
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0065` showed the switch from saved states, with the boot-loaded bytes
written into older states; real pad presses, a cold boot, versus mode,
`SET UP` and a kept setting were not yet seen.

## Hypothesis

From cold boots, real presses reach `EXTRA OPTIONS` and change `NAMES`; the
game saves the choice; the pilot select, `SET UP` and VS screens show the
art of the setting; the setting survives a power cycle; every earlier
regression reference still rebuilds.

## Controlled Change

None to the image: `build/opt005/a` (Track 01 `357f5b65…aac6`). Two cold
boots in the pad-key home, the second with the first's save.

## Prediction

Boot 1: `JAPANESE` set and saved, katakana on all three screens. Boot 2:
`JAPANESE` still selected, then `ENGLISH` set, Latin on all three screens.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Built image | `build/opt005/a` (`data/regression/opt006_names_switch.json`) |
| Boot 2's backup memory | boot 1's, as Mednafen wrote it (named by the built disc's identity, `…650c6e05….bkr`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`boot.py`](boot.py) | Cold boot in `EXP-0019/drive.py`'s pad-key home, with a backup memory copied in; `keep` copies the home's backup memory out |
| `EXP-0019/drive.py` | One press per call; screenshots |
| `EXP-0061/look.py` | Name sprites classified as built (Latin) or katakana, against `build/loc005/a` and the untouched files |
| `EXP-0055/regress.py` | → [`regress.json`](regress.json) (eight earlier references), [`regress_new.json`](regress_new.json) (the new one) |
| — | → [`play.json`](play.json): presses, checks, the agent's reading of each screen, saves |

## Procedure

```bash
CUE="build/opt005/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
B=research/experiments/EXP-0066/boot.py; D=research/experiments/EXP-0019/drive.py
./invenv.sh python $B launch local/opt006/boot1 "$CUE"
# start, start (attract), start (title), down, down, a (OPTION MODE), up (to EXTRA OPTIONS), a,
# right (JAPANESE), start (back), start (leave: saves), down, a (VERSUS MODE), right, right,
# a, p2a, a, p2a, a, p2a (pilots, bodies, variants), start (SET UP); look.py at each screen
./invenv.sh python $D stop local/opt006/boot1; ./invenv.sh python $B keep local/opt006/boot1 local/opt006/save1
./invenv.sh python $B launch local/opt006/boot2 "$CUE" --bkr local/opt006/save1/<the .bkr>
# the same route with left (ENGLISH) instead of right; recorded differences:
# two starts reached the title (one press was refused), one right (Mary), and
# three extra presses at the end (see "Actual Result")
./invenv.sh python $D stop local/opt006/boot2; ./invenv.sh python $B keep local/opt006/boot2 local/opt006/save2
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin re007_jin_santana re008_roster \
  end010_jin_ending end011_jin_timing end023_roster_endings boot004_boot_warnings loc005_name_art \
  --out research/experiments/EXP-0066/regress.json
./invenv.sh python research/experiments/EXP-0055/regress.py opt006_names_switch \
  --out research/experiments/EXP-0066/regress_new.json
```

2026-11-06, 17:10-17:21 local (regression rebuilds to 17:21). Two cold boots, asked first: "Yes, run both
(Recommended)". 22 and 23 single presses were sent (`play.json`); a few
were refused because Mednafen was not in front or dropped during a
screen's entrance, and were sent again once. During boot 2 the user said:
"I may have interrupted your keystrokes with my own." The screens were
checked rather than the press log. At the end of boot 2's machine select,
player 2's variant press was dropped, so a Start sent for `SET UP` landed on
MACHINE SELECT (no effect); player 2's A was sent again, `SET UP` came, a
Start during its entrance did not advance, and a further Start opened the
VS screen: three presses beyond boot 1's route. `boot.py` was changed
between the boots (`keep` now keeps the file's own name, and `--bkr`
copies it under that name); boot 1 ran without `--bkr`, which behaves the
same in both versions.

## Actual Result

### Boot 1 (no save; English by default)

- OPTION MODE from the cold boot: the new layout and the `EXTRA OPTIONS`
  row. **Up** from `DIFFICULTY` wrapped to `EXTRA OPTIONS`; **A** opened
  the sub-menu (`NAMES`, `ENGLISH` selected); **Right** selected
  `JAPANESE` (byte `0x060D9295` = 1); **Start** returned to OPTION MODE
  with the cursor on `EXTRA OPTIONS`; **Start** left Options. (The byte was
  read once with the agent interface, an inline read not kept as a script;
  the save below records the same value.)
- Versus mode: pilot select Santana / Arieta in katakana (2 name parts, katakana);
  `SET UP` katakana (2); VS: the katakana BLODIA banners and both pilots
  (6 parts, katakana, none Latin).
- The save Mednafen wrote: settings `03 00 00 00 01 01 …` (`+5` = 1), sum
  `06fa`, valid.

### Boot 2 (boot 1's save)

- After the boot check the settings block held `+5` = 1 (an inline agent
  read at frame 2,034, not kept as a script); the sub-menu showed
  `JAPANESE` selected (kept). **Left** selected `ENGLISH`; Start,
  Start left Options.
- Versus mode: pilot select Mary / Arieta (Latin, 2 built parts); `SET UP`
  Mary / Arieta (Latin, 2 built parts; look `setup2`); VS: BLODIA BX-02
  twice, Mary, Arieta (6 built parts, none katakana; looks `vs3-*`). The
  looks named `setup` and `vs-8`-`vs-11` caught MACHINE SELECT and those
  named `vs2-*` caught `SET UP` (`play.json`, `look_screens`).
- The save: `+5` = 0, sum `06f9`, valid.

### Regression

All eight earlier references rebuild and match (`regress.json`); the new
`opt006_names_switch.json` rebuilds and matches (`regress_new.json`: its
replacement files, Track 01 and the cue; the two added files are covered
through Track 01's hash, and `names_switch_changes.json`'s hash was checked
by hand).

## Conclusion

Prediction met. The switch works from cold boots with real presses, is
saved, survives a power cycle, and changes the name art on the pilot
select, `SET UP` and VS screens both ways.

## Uncertainty and Alternatives

- Arcade mode's screens were not played with the switch (same load sites,
  `EXP-0063`; the saved-state checks of `EXP-0065` used arcade states).
- B to leave the sub-menu, and the no-cart case (row 7 skipped), were not
  pressed (code review and the interpreter only); this home has a RAM cart.
- Real hardware reading the tail files is untested.

## Reproduction

Run the procedure (two cold boots with presses: ask the user first).
