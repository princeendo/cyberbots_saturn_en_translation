# EXP-0057: Where the Name Art Is Stored, and Whether Latin Art Exists

Task: LOC-002
Status: DONE
Confidence: CONFIRMED (storage of the select and VS names, by controlled change; no Latin pilot or mech name in either bank, by walking every frame); HYPOTHESIS (a literal-only type-2 encoding is valid; not yet tested on screen)

## Observation

- D-051: the select names are frames `0x14`-`0x1C` of bank 56, the VS
  names frames `0x02`-`0x0A` (pilots) and `0x0C`-`0x1B` (mechs) of bank 63.
- `EXP-0056`: versus mode's own screens had not been reached.

## Hypothesis

The select names are raw pixels in `SELECT.VAD`; the VS names come from
`PL3F_0.BIN`; neither bank holds Latin pilot or mech name art.

## Controlled Change

1. A test image from the untouched source (`mark.py`, never shipped): Jin's
   select name part in `SELECT.VAD` filled with one colour; the literal
   streams of two compressed `PL3F_0.BIN` records (Jin's VS name part,
   Blodia's VS name part) filled with `0x77`.
2. That image and the untouched one run from session states taken before
   each screen's files load (2538 for the select, 6448 for the VS), so the
   game reads the files itself. No key, no cold boot.

## Prediction

Only Jin's select name changes on the select screen; only Jin's and
Blodia's names change on the VS screen.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched image, `SELECT.VAD`, `PL3F_0.BIN` | as the listing |
| Session states 2538, 3070, 6448, 6626, 6805 | `local/ref005/session/states/` |
| Changes of the test image | `build/loc002/marked/changes.json` (3 ranges, original hashes; image deleted after the runs) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0042/probe.py` | Disc loads from a state |
| `EXP-0056/poke.py` (`--vdp1-at`), `EXP-0056/trace.py` (now with `--write`) | Frames drawn with VDP1 dumps; pattern copies traced |
| [`locate.py`](locate.py) | → [`locate.json`](locate.json): each name part's pixels found on the disc |
| [`bank56.py`](bank56.py) | → [`bank56.json`](bank56.json): every part and pattern of bank 56, rendered |
| [`walk.py`](walk.py) | One-launch frame walk (failed after 7 frames; see below) |
| [`mark.py`](mark.py) | The test image |
| `EXP-0019/drive.py` | The versus-mode cold boot |

## Procedure

```bash
P=research/experiments/EXP-0042/probe.py; ST=local/ref005/session/states
./invenv.sh python $P local/loc002/loads-sel1 --state $ST/f00002538.mcs --frames 480 --step 30 --cells-until 0
./invenv.sh python $P local/loc002/loads-vs --state $ST/f00006448.mcs --frames 420 --step 30 --cells-until 0
# one poke.py run per name frame with --vdp1-at (sel-FF, vsp-FF, vsm-FF), then:
./invenv.sh python research/experiments/EXP-0057/locate.py --out research/experiments/EXP-0057/locate.json
# trace.py --write 06087E9E=00FF / 06087A44=00FF --pc 06010552 (up-pFF, up-mFF; up-first from state 6626)
./invenv.sh python research/experiments/EXP-0057/bank56.py local/loc002/bank56 --out research/experiments/EXP-0057/bank56.json
# one poke.py run per bank-63 frame 1-122 (06087A44=NNNN), screenshots in local/loc002/w63/
./invenv.sh python research/experiments/EXP-0057/mark.py build/loc002/marked
# poke.py from states 2538 and 6448, untouched and marked (--cue), shots 440/480 and 340/360
```

2026-11-06, 10:00-11:00 local. One cold boot with 13 single presses for
versus mode, asked first: "Yes, run it now (Recommended)".

## Actual Result

### Pilot select names: `SELECT.VAD`, raw

- `SELECT.VAD` loads (state 2538 + 269) and is copied raw to VDP1 VRAM
  `0x20000`. Bank 56 is a special bank of the sprite-part routine
  (`0x060113AC`, 8-byte parts): a part's pattern is VRAM `0x20000` + 4 ×
  its index, so a `SELECT.VAD` offset.
- The nine names (4 bpp, palette colour word `0x61E0`) are at `0x17840`
  (Jin, two parts) to `0x19B20`; `bank56.json` lists every frame's parts,
  and the runtime sprites (`locate.json`) agree for all nine.

### VS names: `PL3F_0.BIN`, compressed

- `PL3F_0.BIN` loads raw to WRAM-L `0x00200000` before the VS screen
  (state 6448 + 275). Bank 63's 6-byte parts start at its offset 0; a
  part's pattern record is `PL3F_0.BIN` + 4 × its index.
- Each record's first word is type (bits 12-15), width / 8 (bits 8-11) and
  height; the name records are type 2. `0x060107EA` caches a record in VDP1
  VRAM, through `0x06010552` and `0x060101BE`, which dispatches on the type:
  0 a plain copy, 1/2/3 decoders. Type 2 (`0x0601446C`) reads control bytes
  (after the first two words) and literal longs (from record + 4 + the
  second word); each control byte selects one of 256 16-byte handlers.
  Handlers 0-2 copy 1-3 literal longs (read in the code); the others are
  not decoded.
- Record offsets (traced copies): Jin `0x4324`, `0x4440` (plus two small
  shared parts), Santana `0x457C`, Mary `0x4834`/`0x492C`/`0x4954`, Arieta
  `0x4A6C`, Gawaine `0x4D30`, Bao and Mao `0x5034`, Devilotte `0x531C`,
  Chiyomaru `0x5630`, Shade `0x5920`; the 16 mechs from `0x5E58` (Blodia)
  to `0x95F8` (Super-8), two records each and a shared "・" (`0x63D8`).
  The VS pilot names decode to the same pixels as the select art.

### The controlled change

| Screen | Pixels differing (marked / untouched) | Where |
| --- | --- | --- |
| Pilot select (shots 440, 480) | 1,615 | x 38-141, y 209-224: Jin's name only |
| VS screen (shots 340, 360) | 1,772 | rows 41-56 (Blodia's name) and 217-231 (Jin's name) only |

### Latin art on the disc

- **Bank 56** (all 149 frames, 628 patterns, `bank56.py`): no Latin pilot
  or mech name. Its only Latin is the labels `PILOT SELECT`, `MACHINE
  SELECT`, `BODY TYPE`, `1P`, `2P`.
- **Bank 63** (all 122 frames drawn on the VS screen, one run each): no
  Latin version of the nine pilot or sixteen mech names. Frame `0x0B` is a
  Latin pilot-style banner reading "G.O.D."; frames `0x74`-`0x79` are a
  third banner style (brown on pink) with katakana/kanji names of
  story-only characters (one appears to read 鉄山, Tessan); frame `0x70`
  is an unreadable small banner. Where these are shown is not known.
- **Other Latin names on the disc** (not in these banks): the ending cast
  roll's Latin pilot names (`KEND_1.BIN`, bank 16, D-040; their own small
  style), and `CYBER.BIN`'s Latin text lists of 8 pilots and 17 mechs
  (`EXP-0056`), not seen drawn anywhere yet.
- A one-launch walk of bank 63 went black after 7 frames (probably the
  pattern cache filling); one run per frame worked.

### Versus mode (cold boot)

Its pilot select (`fac9875f…`), `SET UP` (`fcc0d433…`) and VS screen
(`91b7a464…`) show the same katakana pilot and mech names (the same banks),
Latin labels, and no chapter caption. No other name art.

### Room

| File | Name art | Free room |
| --- | --- | --- |
| `SELECT.VAD` (379,488 bytes) | 9 names, `0x17840`-`0x19B20` (8,928 bytes), raw 4 bpp | 1,440 bytes of sector slack; every other byte but 792 scattered ones is used by banks 56-57 |
| `PL3F_0.BIN` (333,536 bytes) | 9 pilot and 16 mech names, 47 records, 20,804 bytes compressed (26,188 raw) | 288 bytes of sector slack; 903 records end at the file's end |

- A Latin name of the same size can replace a select name in place (same
  parts, colours 0-15 of its palette).
- A VS replacement must be a type-2 (or other) record. Literal-only would
  take about 28,560 bytes for all 25 names, about 7.8 KB more than the
  current records: in place it needs real compression (more handlers
  decoded) or simpler art, or room elsewhere.
- **Variant difference (for `OPT-001`):** replaced in place, a Latin build
  differs in those two ranges (about 29.7 KB). Keeping the katakana beside
  the Latin, as the switch needs, does not fit in either file; it needs
  storage elsewhere (another file's free space, or a moved or new file).

## Conclusion

Prediction met. Select names are raw art in `SELECT.VAD`; VS names are
compressed records in `PL3F_0.BIN`; no Latin pilot or mech name art exists
in either bank. Latin art must be drawn (or copied from the cast roll's
style, or rendered from a font) for `LOC-004`, and the switch needs new
storage.

## Uncertainty and Alternatives

- That a literal-only type-2 record decodes correctly is a HYPOTHESIS (the
  three literal handlers are read, not tested).
- Banks 56-57's frame counts come from their table layout; coverage of
  `SELECT.VAD` is from every part in those tables.
- Frame `0x0B` ("G.O.D.") and `0x74`-`0x79`: where the game shows them is
  UNKNOWN.

## Reproduction

Run the procedure. Expect `locate.json`, `bank56.json` and the differing
pixel counts above.
