# EXP-0065: The Names Switch, Built and Checked From Saved States

Task: OPT-005
Status: DONE
Confidence: CONFIRMED (the build; the boot load of the new files and code;
the menu, sub-menu and both settings' art from saved states, with the
loaded bytes injected); the cold-boot play check is `OPT-006`

## Observation

- `OPT-004` decided the design; `EXP-0062`-`EXP-0064` (D-055-D-057) gave the
  menu, the save byte, the load sites, the free tail and the free code range.
- Three designs were made and checked by independent reviewers (a background
  workflow, `OPT-005`): the disc tool (`tools/disc/add_files.py`), the menu
  patches (checked on an SH-2 interpreter: 204 pad and cursor cases), and
  the load hooks. The review corrected D-056 (the file search is linear, to
  an end flag) and moved the part-table restore before `STG0A.BIN`'s init.

## Hypothesis

`--names-switch` builds an image whose OPTION MODE has the approved layout
and `EXTRA OPTIONS` sub-menu, and whose pilot select and VS screens show the
Latin art with the byte 0 and the original katakana with the byte 1.

## Controlled Change

The `LOC-005` build command plus `--names-switch
data/translations/names_switch.json`.

## Prediction

Two identical builds; changes only at the recorded places; the boot loads
the new directory entries and code; each screen shows the art of its
setting; old and new saves load.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched files | `CYBER.BIN`, `OPDEMO.BIN`, `STG0AS.BIN`, `STG0A.BIN`, `SELECT.VAD`, `PL3F_0.BIN` (`dialogue.checked`) |
| `data/translations/names_switch.json` | the approved words (`OPT-004`) |
| `build/loc005/a` | comparison base (Track 01 `e1a88dc6…`) |
| Session states | 384 (before the boot loads), 27173 (Options), 2538 (pilot select), 6448 (VS) |
| `local/opt001/save-ctl` backup memory | the game's own save (`EXP-0062`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/names_switch.py` (new, tests) | Menu code, hooks, patches, tail files |
| `tools/disc/add_files.py` (new, tests) | Tail files and their directory records |
| `tools/text/dialogue.py --names-switch` (new option) | Writes `CYBER.BIN`, `OPDEMO.BIN`, patches the built `STG0AS.BIN`, adds the files after `patch_image`, updates the build manifest, writes `names_switch_changes.json` |
| [`check_build.py`](check_build.py) | → [`build.json`](build.json) |
| [`check_states.py`](check_states.py) | → [`states.json`](states.json) |
| `EXP-0062/load_test.py` (now with `--cue`) | → [`saves.json`](saves.json) |

## Procedure

```bash
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent --rank staying \
  --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --endings data/text/m8_endings.json \
  --boot-warnings data/translations/boot_warnings.json --name-art data/translations/name_art.json \
  --names-switch data/translations/names_switch.json"
mkdir -p local/opt005/rec-a local/opt005/rec-b
$B --out build/opt005/a --ending-record-dir local/opt005/rec-a
$B --out build/opt005/b --ending-record-dir local/opt005/rec-b
./invenv.sh python research/experiments/EXP-0065/check_build.py build/opt005/a build/opt005/b \
  --out research/experiments/EXP-0065/build.json
./invenv.sh python research/experiments/EXP-0065/check_states.py local/opt005/states \
  --out-json research/experiments/EXP-0065/states.json
C="build/opt005/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"; S=local/opt001/save-ctl/home/sav/*.bkr
./invenv.sh python research/experiments/EXP-0062/load_test.py local/opt005/load-old $S --cue "$C"
./invenv.sh python research/experiments/EXP-0062/load_test.py local/opt005/load-jp $S --set 9=01 --fix-sum --cue "$C"
```

2026-11-06, 15:10-16:30 local. No key, no cold boot.

## Actual Result

### The build (`build.json`)

- Two builds identical (Track 01 `357f5b65…aac6`, every output, the ending
  records).
- Every output of `build/loc005/a` is equal, except `STG0AS.BIN`, which
  differs only at `0x6C0`-`0x6C3` (the hook-B literal).
- `CYBER.BIN` (690 bytes) and `OPDEMO.BIN` (79) differ from the untouched
  files only at the 56 recorded changes (`names_switch_changes.json`: file,
  offset, address, original and new bytes, purpose). New code: 740 bytes at
  `0x06055424`-`0x06055708` (D-057's range): menu code (title hook,
  state-3 trampoline, the sub-menu) then hooks B, A, C with the 124-byte
  part table and the two file names.
- 30 sectors differ from `loc005`'s Track 01, all in `CYBER.BIN`,
  `OPDEMO.BIN`, `STG0AS.BIN`, the root directory's last sector (LSN 27) or
  the new files: `ZNAMES1.BIN` (LSN 43,643, 8,640 bytes, `SELECT.VAD`
  `0x17840`-`0x19A00`) and `ZNAMES2.BIN` (LSN 43,648, 38,700 bytes,
  `PL3F_0.BIN` `0x90`-`0x97BC`), each equal to its untouched range; 0
  invalid sectors.

### From saved states (`states.json`)

- **Boot** (state 384, built image): the game's directory table lists
  `WARNING4.PIX`, `ZNAMES1.BIN` (FAD 43,793), `ZNAMES2.BIN` (FAD 43,798)
  with the end flag on `ZNAMES2.BIN` and off `WARNING4.PIX`; the entry
  count `0x060DBC58` is 329 (327 before); `CYBER.BIN`'s changes are in RAM
  and the `OPDEMO.BIN` overlay equals the built file (24 of 24 sectors).
- **Options** (state 27173, built bytes injected, state 1 for a redraw):
  the title on row 2 and the rows two higher; `EXTRA OPTIONS` on row 22,
  highlighted with the cursor on 8; state 3 with the cursor on 8 opens the
  sub-menu (`EXTRA OPTIONS`, `NAMES  ENGLISH  JAPANESE`, `PRESS START TO
  EXIT`; substate 2); with the byte set, `JAPANESE` is highlighted; back to
  OPTION MODE (state 1) gives the same screen as before (same hash).
- **Names** (`EXP-0061/look.py`):

  | Screen | Byte 0 | Byte 1 |
  | --- | --- | --- |
  | Pilot select (2538) | 1 Latin part | 2 katakana parts |
  | VS (6448) | 6 Latin parts | 12 katakana parts |

  The counts equal `LOC-006`'s checker on `build/loc005/a` (1, 6) and on
  the untouched image (2, 12). Read on screen: "Jin" / its katakana; BLODIA,
  R·LIGHTNING, Jin, SHADE / their katakana banners.

### Saves (`saves.json`)

From state 384 on the built image: the game's save without the setting is
accepted (`0x06037064`), byte 0; the same save with `+9` = 1 and its sum
fixed is accepted, byte 1 in RAM.

### Failed first runs (method)

- Injecting the whole `OPDEMO.BIN` at state 2538 blacked out the select:
  `STG0A.BIN` was still arriving at `0x06060000`. No overlay is injected
  there now.
- The VS screen with the byte set went black: the injected entries were
  not counted (`0x060DBC58` stayed 327, so `ZNAMES2.BIN` was not found).
  The count read after the boot is injected now.

## Conclusion

Prediction met. The image has the approved menu and switch, and each
setting shows its art on the pilot select and VS screens.

## Uncertainty and Alternatives

- Pad input in the menu and sub-menu (Up/Down to row 8, A/C to enter,
  Left/Right/A/C to change, Start/B to leave) is tested by code review and
  the interpreter only; the cold boot of `OPT-006` presses them.
- The later checks wrote the boot-loaded bytes into older states; `OPT-006`
  plays it from a cold boot.
- Versus mode and `SET UP` use the same load sites (static); not run here.
- Real hardware reading the tail is untested.

## Reproduction

Run the procedure. Expect `build.json`, `states.json` and `saves.json` as
committed (screenshot hashes may vary).
