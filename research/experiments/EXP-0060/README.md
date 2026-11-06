# EXP-0060: The Latin Name Art, Built and Seen

Task: LOC-005
Status: DONE
Confidence: CONFIRMED (the type-2 format as used; the build; every name on screen from saved states)

## Observation

- D-052: select names are raw parts in `SELECT.VAD`; VS names are type-2
  records in `PL3F_0.BIN`, of which only the literal handlers were read.
  Literal-only Latin art would not fit.
- Some name frames reuse one pattern at two places (Mary's), so Latin
  letters cannot follow the old part layout.

## Hypothesis

With the whole type-2 format, the Latin VS names fit `PL3F_0.BIN`'s name
region; giving every name one part (select) or two (VS mech) makes the
layout simple; the image changes in three files only.

## Controlled Change

The `boot004` build command plus `--name-art data/translations/name_art.json`.

## Prediction

Two identical builds; only `SELECT.VAD`, `STG0A.BIN`, `PL3F_0.BIN` change,
inside the recorded ranges; every name shows as built.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched source | as `references/saturn_jp/README.md` |
| `data/translations/name_art.json` | `LOC-004`'s approved spellings |
| `arcade_font.json` | ignored; the arcade letters |
| `build/boot004/a` | comparison base (Track 01 `ef27ebc6…`) |
| Session states 2538, 6448 | screen checks |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/pattern_t2.py` (new, tests) | Type-2 decoder and greedy encoder |
| `tools/text/name_art.py` (new, tests) | Banners, part tables, record packing, change records |
| `tools/text/dialogue.py --name-art` (new option) | Writes the three files and `name_art_changes.json` |
| [`check_build.py`](check_build.py) | → [`build.json`](build.json) |
| [`check_screens.py`](check_screens.py) | → [`screens.json`](screens.json) |

## Procedure

```bash
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --endings data/text/m8_endings.json \
  --boot-warnings data/translations/boot_warnings.json --name-art data/translations/name_art.json"
mkdir -p local/loc005/rec-a local/loc005/rec-b
$B --out build/loc005/a --ending-record-dir local/loc005/rec-a
$B --out build/loc005/b --ending-record-dir local/loc005/rec-b
./invenv.sh python research/experiments/EXP-0060/check_build.py build/loc005/a build/loc005/b \
  --out research/experiments/EXP-0060/build.json
./invenv.sh python research/experiments/EXP-0060/check_screens.py local/loc005/screens \
  --out-json research/experiments/EXP-0060/screens.json
```

2026-11-06, 11:30-13:30 local. No key, no cold boot.

## Actual Result

### The type-2 format (`pattern_t2.py`)

Read from the 256 handlers (each 16 bytes from `0x060144C8`) and three
unrolled routines (`0x060154C8` literal copies, `0x0601556C` back copies,
`0x0601552A` fills); the table is in D-053. The decoder reproduces all 14
name parts the game had decoded in VRAM; on the original 45 name records
the greedy encoder needs 21,992 bytes against the game's 20,804.

### Part words

Fitted against every on-screen VS name part: x = 80 + (word 0 >> 6), y =
origin + (word 1 >> 6), flips = (word 1 >> 2) & 3. A first build drew only
the left half of each mech name: word 1 bit 1 marks the frame's **last**
part, and the copied left-part template carried it into the first slot.
The builder now sets that bit on the last part only.

### Build (`build.json`)

- Two builds: all outputs, Track 01 (`e1a88dc6…4a6d`) and the six ending
  records identical; every `boot004` replacement and output unchanged.
- `SELECT.VAD` 7,572 bytes, `STG0A.BIN` 36, `PL3F_0.BIN` 20,155 changed,
  all inside `name_art_changes.json`'s ranges (original and new hashes per
  range); sizes kept. VS records: 12,316 of 21,712 bytes.
- All 1,599 type-2 parts of bank 63 decode; the frame table read from
  `STG0AS.BIN` is the same in the built `STG0AS.BIN`.
- 18 sectors differ from `boot004`, all in the three files; 43,793 sectors,
  0 invalid.

### Screens (`screens.json`)

All 34 names: every part on screen equals a built pattern (select: the
`SELECT.VAD` slot; VS: the decoded records) and, on the VS screen, every
built pattern of the frame is on screen. The agent read every screen: the
nine pilot names in both places and the sixteen mech names, each followed
by its model code (for example "F·KILLER BEE F7900J", "WARLOCK X-0").

- Select: from state 2538 the built `SELECT.VAD` loads from the disc, but
  `STG0A.BIN` is already in RAM in every saved state, so its built part
  table was written into RAM right after the load. A cold boot reading
  `STG0A.BIN` itself is `LOC-006`'s play check.
- VS: from state 6448, everything from the disc. The VS screen lasts a few
  seconds, so the state is reloaded for each name (a single run passed the
  screen after eight names).

## Conclusion

Prediction met after the last-part fix. The pilot select and VS screen
show every name in Latin as approved.

## Uncertainty and Alternatives

- The katakana art is not kept in these files (D-052: no room); `OPT-001`
  needs storage for it.
- Versus mode's `SET UP` screen uses the select bank and is expected to
  show the same Latin names; not checked here (`LOC-006`).

## Reproduction

Run the procedure. Expect `build.json` and `screens.json` as committed and
`data/regression/loc005_name_art.json`.
