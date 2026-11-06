# EXP-0053: English for the Boot Warnings

Task: BOOT-003
Status: DONE
Confidence: CONFIRMED (no official English found in the sources searched; every approved screen fits D-049's room)

## Observation

- D-048: five Japanese warning pictures, one per backup-memory condition.
- D-049: room 352 × 224 pixels, 16 colours from `CYBER.BIN`'s table.
- Policy: no official English → a recorded new translation the user
  approves; absence must be shown, not assumed.

## Hypothesis

There is no official English for these messages. The nearest official
wording is the Saturn BIOS's own labels for its memory screens.

## Controlled Change

None to the game. String searches of the arcade program and both BIOS
files; draft English rendered in two of the game's Latin fonts into the
measured room.

## Prediction

No arcade string about cartridges or backup memory; BIOS labels for the
memory manager and its devices; drafts that fit 352 × 224.

## Inputs and Provenance

| Input | SHA-256 (first 16) | Notes |
| --- | --- | --- |
| `cybotsu` program | as `REF-003` (`local/ref003/cybotsu-maincpu.bin`) | the US arcade set |
| `sega_101.bin` (Japanese BIOS) | `dcfef4b99605f872` | equal to XvSF's |
| `mpr-17933.bin` (US BIOS) | `96e106f740ab448c` | equal to XvSF's, the user's own |
| `arcade_font.json` | ignored, `local/layout001/font/` | the story's arcade letters (`EXP-0025`) |
| `FIX.BIN` | as the listing | the credits' 8 × 8 font (D-035) |
| `EXP-0051` screenshots | as D-048 | the source screens |

## Tools and Environment

| Tool | Use |
| --- | --- |
| Python `re` over the files, both byte orders | Printable runs with memory, backup, format, cartridge, save, RAM, warning, error or data |
| [`render.py`](render.py) | Draws a drafts file into the room in either font; fit report; Japanese-beside-English sheet |
| [`drafts.json`](drafts.json) | The drafts as put to the user (the 05 line before the fix) |
| [`fit.json`](fit.json) | The approved text's fit |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0053/render.py local/boot003/arcade --font arcade --beside
./invenv.sh python research/experiments/EXP-0053/render.py local/boot003/fix --font fix --beside
./invenv.sh python research/experiments/EXP-0053/render.py local/boot003/approved \
  --drafts data/translations/boot_warnings.json --font arcade --beside \
  --out-json research/experiments/EXP-0053/fit.json
```

2026-11-06, 09:00-09:40 local. The search commands are inline Python
(printable runs of 6 or more bytes, case-insensitive keywords).

## Actual Result

### Official English

- **Arcade (`cybotsu`):** no message about a cartridge or saved data. Its
  related strings are the service menu's ("MEMORY CHECK", "GAME DATA",
  "SAVE & EXIT", "RAM OK", "WORK RAM NG", "EEPROM ERROR") and the
  region-warning screen, titled "WARNING". So the title word is the arcade's
  own; nothing else carries over.
- **Saturn BIOS:** both files hold (partly compressed) English labels:
  "Manage Memory", "Memory Manager", "Cartridge", "Clear", "Settings", and
  in the US BIOS "Not Formatted", "available". XvSF reached the screens of
  these same two files (equal hashes; its `EXP-0055`): "Manage Memory" on
  the CD-player menu, then "Memory Manager" with "System Memory". These are
  facts about the BIOS files, not about either game.
- No US Saturn release exists, and the references are arcade-only
  (`REF-002` `REJECTED`).

### Drafts and lettering

- Drafts by the agent, close to the Japanese, using the BIOS terms. The
  fonts have no parentheses, so "(initialize it)" is folded into the
  sentence.
- Arcade letters (16 rows, 8-pixel advance): every screen fits (widest line
  288 px, lowest row 207 of 223) after wrapping at 38 characters; a first
  wrap at 27 characters overflowed `WARNING3` and `WARNING4`.
- `FIX.BIN` letters (8 × 8): every screen fits, but its comma and
  apostrophe are dots and the text is small.
- Sheets were sent to the user: the Japanese beside the arcade-font English,
  and the `FIX.BIN` version.

### The user's decisions (verbatim, 2026-11-06)

| Question | Answer |
| --- | --- |
| Approve the draft wording? | "Approve the drafts (Recommended)" |
| What to call the BIOS screen the Japanese calls the "multiplayer screen"? | "control panel (Recommended)" |
| The out-of-space warning says 05 blocks; the game needs 6. Which number? | "6, what the game checks" |
| Lettering? | "Arcade font, Japanese colours (Recommended)" |

The approved text is `data/translations/boot_warnings.json`, with the
translator, the source screens' hashes and the style. Its renders
(`local/boot003/approved/`): `WARNING0` `32f605cc…`, `WARNING1`
`8bb53015…`, `WARNING2` `fb16b9c3…`, `WARNING3` `3798807f…`, `WARNING4`
`052cb9d0…`; all fit (`fit.json`).

## Conclusion

Prediction met. No official English exists for the boot warnings; the
approved English is the agent's translation with the BIOS's terms, one
opt-in fix (6 blocks), in the arcade letters and the Japanese colours.

## Uncertainty and Alternatives

- The renders are samples drawn by this experiment's code; `BOOT-004`'s
  generator must reproduce them and check them on screen.
- The arcade font is game-derived and stays in an ignored path; the build
  reads it from there.

## Reproduction

Run the procedure. Expect the five render hashes above and `fit.json`.
