# EXP-0003: Screenshots and Save/Load States by Hotkey

Task: EMU-006
Status: DONE
Confidence: CONFIRMED

## Observation

Stock Mednafen 1.32.1 takes screenshots and saves or loads states only through
hotkeys (F9, F5, F7 by default). The title screen is static at one-second
sampling: D-001 frames 062-067 are byte-identical, so a state saved there can
be checked with byte-equal screenshots, a stronger test than XvSF's animated
title allowed (its `EXP-0003` used SSIM).

## Hypothesis

F9 writes a screenshot, F5 saves a state and F7 loads it, both within the
same session and into a fresh cold boot; a reloaded title state shows the
same screen as when it was saved.

## Controlled Change

No change to binary, BIOS, configuration or source. Hotkeys are pressed by
`tools/mednafen/hotkeys.py` through macOS System Events. `sav/` and `mcs/`
were emptied before run 1 and run 1b; only `sav/` before run 2, which uses
run 1b's state. The user was present ("Run EMU-006", 2026-11-02).

## Prediction

- Run 1: F9 just before F5 shows the title; F9 at about 92 s shows the attract
  fight; F9 about 1-2 s after F7 shows the title again.
- Run 2: F9 at about 20 s shows a boot screen, not the title; F9 about 2 s
  after F7 shows the title, which a normal boot reaches only at about 57 s.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/cyberbots_saturn_jp_2m/` (63
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock 1.32.1 binary
(`077ac658…669f`), home `local/mednafen_quiet/` with the sibling pad
bindings (config `aad9a7ef…57cf`).

## Tools and Environment

- `tools/mednafen/hotkeys.py` (copied from XvSF, `ENV-003`): launches
  Mednafen; for each `--at SECONDS:KEY` brings the Mednafen process (by PID)
  to the front, checks it is frontmost, sends the macOS key code, and by
  default restores the previous front app; `--keep-focus` keeps Mednafen in
  front for the whole run. Sends F12 at the end. Accessibility permission was
  already in place from the sibling projects: no prompt appeared.
- Screenshots: Mednafen's own PNGs in the home's `snaps/`, numbered by its
  counter across runs.

## Procedure

```bash
CUE="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
find local/mednafen_quiet/sav local/mednafen_quiet/mcs local/mednafen_quiet/snaps -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys "$CUE" local/emu006/run1.log \
  --at 62:F9 --at 63:F5 --at 92:F9 --at 93:F7 --at 94:F9
# moved snaps/*.png to local/emu006/run1_snaps/, copied the state to run1_state/
find local/mednafen_quiet/sav local/mednafen_quiet/mcs -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys "$CUE" local/emu006/run1b.log --keep-focus \
  --at 62:F9 --at 64:F5 --at 92:F9 --at 95:F7 --at 97:F9 --at 100:F9
# moved snaps/*.png to local/emu006/run1b_snaps/
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys "$CUE" local/emu006/run2.log --keep-focus \
  --at 20:F9 --at 22:F7 --at 24:F9 --at 27:F9
# moved snaps/*.png to local/emu006/run2_snaps/; re-hashed the state
```

Source manifests were taken before and after (`local/emu006/source-*.json`).
SSIM by ffmpeg 9.0.1 (`-lavfi ssim`).

## Actual Result

All three runs exited 0; the Mednafen logs are identical (128 lines, SHA-256
`521ac7ff…79d1`). Key times are seconds after launch as recorded in
`local/emu006/run*.json`.

**Run 1** (focus restored after each key): F9 63.65, F5 64.83, F9 93.18,
F7 95.05, F9 96.90, F12 98.15. Only two screenshots were written, and the
counter file read 2:

| Shot | When | Screen (agent-reviewed) | SHA-256 |
| --- | --- | --- | --- |
| `-0000` | 63.65 s | Title, `PRESS START BUTTON` blinked off | `b7286b3c…a1a9` |
| `-0001` | 93.18 s | Attract fight, `4 HIT COMBO!` | `2163024…f6fa` |

The F9 at 96.90 s, 1.85 s after F7, produced no file, and nothing in the log
shows whether the F7 load happened. The state (1,098,431 bytes,
`c9bb2842…b8ea`) was kept in `local/emu006/run1_state/`.

**Run 1b** (`--keep-focus`, wider gaps): F9 63.15, F5 64.31, F9 92.99, F7 95.97,
F9 97.31, F9 100.32, F12 100.66. Four screenshots, all 352x240:

| Shot | When | Screen (agent-reviewed) | SHA-256 |
| --- | --- | --- | --- |
| `-0002` | 63.15 s | Title with `PRESS START BUTTON` | `e39d8e2e…70c7` |
| `-0003` | 92.99 s | Attract fight | `95d0dedd…d6ff` |
| `-0004` | 1.34 s after F7 | Title, prompt blinked off | `b7286b3c…a1a9` (= run 1's `-0000`) |
| `-0005` | 4.35 s after F7 | Black, as a normal boot shows after the title | `f0858bda…0ef6` |

SSIM: `-0002`/`-0004` 0.987 (the blinking prompt), `-0002`/`-0003` 0.069.
State: `Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2.mc0`,
1,099,526 bytes, SHA-256
`a904685f35e32bff63edec05b1dec8aeee905b6b51b462401aa6cd9361013a69`.

**Run 2** (fresh cold boot, run 1b's state): F9 21.18, F7 22.32, F9 24.32,
F9 27.33, F12 27.65.

| Shot | When | Screen (agent-reviewed) | SHA-256 |
| --- | --- | --- | --- |
| `-0006` | 21.18 s | Black, 330x240 (every pixel 0; boot) | `091e40d8…58ba` |
| `-0007` | 2.00 s after F7 | Title with `PRESS START BUTTON`, 352x240 | `e39d8e2e…70c7` (= run 1b's `-0002`) |
| `-0008` | 5.01 s after F7 | VA schematic with `PRESS START BUTTON`, as a normal boot shows after the title | `789aa924…1acf` |

- The state's SHA-256 is unchanged after being loaded in run 2.
- Source manifests are identical before and after; the binary and both config
  files hash as before.
- `git check-ignore` covers the state (`local/`) and `*.mc*`/`*.png` under
  `research/experiments/`.

## Conclusion

**CONFIRMED.** F9 writes a 352x240 screenshot (330x240 during the BIOS
phase), F5 saves a state of about 1.1 MB, and F7 restores it later in the same
session and in a fresh cold boot about 35 s before a normal boot reaches the
title. A reloaded title state shows a screen byte-identical to one taken at
or near save time (`-0004` = `-0000`; `-0007` = `-0002`), and play continues
from it in the normal attract order.

## Uncertainty and Alternatives

- One F9 was lost in run 1, when focus was handed back to another app between
  keys and the F9 came 1.85 s after F7. With `--keep-focus` and 1.3 s or more
  between keys, no key was lost. Whether focus switching, the time since F7,
  or something else lost it is **UNKNOWN**; use `--keep-focus` for hotkey
  runs, and check the snapshot counter after each run.
- The state is about 1.1 MB, against XvSF's 3.5 MB; a smaller cart (1 MiB) is
  the likely reason, not checked.
- Whether a state saved in play (not at the title) restores the same way is
  for the first checkpoint tasks (`DBG-003`).

## Reproduction

Run the procedure above from the repository root, with the user present.
Evidence stays in the ignored `local/emu006/` (`run*.log`, `run*.json`,
`run*_snaps/`, `run1_state/`, source manifests) and the state in
`local/mednafen_quiet/mcs/`.
