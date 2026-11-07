# EXP-0068: The English Art Already in the Fonts (UI-001, part 2)

Task: UI-001 (part 2, the font inventory; part 1 is `EXP-0067`)
Status: DONE
Confidence: CONFIRMED (the menu font's source and its `t`-`z`; the cast
roll's `KEND_1.BIN` records decode byte for byte; the stores' contents as
rendered); SUPPORTED (which stage store holds the city signs)

## Observation

`UI-001` needs every piece of English or Latin art in the stores that UI
screens load, before any task draws on them. Three questions were open:
where the menu print routine (`0x0602A82A`) takes its glyphs and whether it
has `t`-`z`; whether `KEND_1.BIN` (the cast roll's name images) is in a
decoded format; and what the stores the attract loads (`EXP-0067`) hold.

## Hypothesis

The menu font is `FIX.BIN` at VDP2 VRAM `0x0` (the credits' ASCII-indexed
font, D-035), with lower case. `KEND_1.BIN`'s records are type-2 records
(D-053), because they go through the same decoder (`0x0601446C`).

## Controlled Change

None to the disc. One saved-state run of the untouched image with VRAM and
RAM writes (the menu font); one saved-state run with no writes (the cast
roll); everything else offline.

## Prediction

- Blanking `FIX.BIN` tile `0x44` in VDP2 VRAM removes every small `D` from
  `OPTION MODE`; a menu string rewritten to `tuvwxyz?!.,:'/()+=` draws those
  characters.
- Every `KEND_1.BIN` record of the cast roll decodes with
  `tools.text.pattern_t2.decode`, and the decoded bytes occur exactly in the
  game's sprite shadow (WRAM-H `0x060E0000`-`0x060FFFFF`, D-035) during the
  roll.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched files | `local/extracted/saturn_jp/` (`FIX.BIN`, `ST0n_FNT.BIN`, `KANJI.BIN`, the `*.PIX` files, `SELECT.VAD`, `KEND_1.BIN`) |
| Current image's `KANJI.BIN` | `build/opt005/a/KANJI.BIN` |
| Options state | `local/ref005/session/states/f00027173.mcs` (`EXP-0062`) |
| Pre-roll state | `local/end010/cast-pre/s06450.mcs` (`EXP-0044`) |
| Select-screen RAM | `local/loc001/ram3070/wram_h.bin` (`EXP-0056`, for bank 56) |
| Load log | `research/experiments/EXP-0067/attract_loads.json` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`render.py`](render.py) → [`render.json`](render.json) | Renders every decoded store: `FIX.BIN` and `ST00`-`ST0A_FNT.BIN` as 4 bpp 8×8 tiles (64 a row; index = byte offset / 32), `KANJI.BIN` (untouched and current) with `tools.font.kanji`, the `*.PIX` files as 512-wide 8 bpp bitmaps → `OUT/render.json` |
| [`grid.py`](grid.py) | 4× crops of a tile store with a tile grid, to read tile indices |
| [`shadow.py`](shadow.py) → [`shadow.json`](shadow.json) | Runs the cast roll from the pre-roll state, dumps the sprite shadow at 15 points, decodes bank 16's `KEND_1.BIN` records and finds each in the dumps → `OUT/shadow.json` |
| `EXP-0057/bank56.py` | Bank 56's 628 patterns, one picture each, and a contact sheet |
| `EXP-0062/session.py` | The menu-font run (inline script, below) |

Mednafen 1.32.1 with the agent patch (`tools/mednafen/`), silent home, no
keys, no cold boot.

## Procedure

```bash
E=research/experiments/EXP-0068
./invenv.sh python $E/render.py local/ui001/fonts
./invenv.sh python $E/grid.py FIX.BIN 0 8 local/ui001/fonts/g_0_0.png --half 0   # and the other crops
./invenv.sh python research/experiments/EXP-0057/bank56.py local/ui001/bank56
./invenv.sh python $E/shadow.py local/ui001/kend/run      # about 1 min, no key
```

The menu-font run (from the Options state, untouched image): through
`EXP-0062` `session.launch`, read VDP2 VRAM `0x44 * 32` (32 bytes), write
zeros there, run 20 frames, screenshot (`blankD.png`); restore the tile,
write `tuvwxyz?!.,:'/()+=` at `0x06065A44` (an `OPDEMO.BIN` menu string) and
the cursor `0x0606BE8C` = 0, run 20 frames, screenshot (`tz.png`).

2026-11-06, 19:20-21:30 local.

## Actual Result

### The menu font (prediction met)

- `blankD.png` (`b6c29844…9e6b`): every small `D` of `OPTION MODE` is gone
  (`IFFICULTY`, `SOUN`, `ATA RESET`, `3M RAM MO E`); nothing else changed.
  The large yellow title is not drawn from these tiles.
- `tz.png` (`65542573…8d32`): the rewritten row reads `tuvwxyz?!.,:'/()+=`,
  with the comma and apostrophe as dots (as `EXP-0053` saw offline).
- So the print routine's font is `FIX.BIN` (loaded raw to VDP2 VRAM `0x0`,
  `attract_loads.json` frame 1347), ASCII-indexed, and it has `t`-`z`.

### `KEND_1.BIN` (prediction met)

Bank 16's frames `0x1B6`-`0x1C9` use 29 `KEND_1.BIN` records. All 29
decode with `pattern_t2.decode`, and each decoded picture occurs byte for
byte in the shadow (`shadow.json`: record, frame, size, SHA-256, shadow
address, first dump that has it). 16 are the Japanese names (even frames,
the records `EXP-0044` hid); 13 are the Latin names (odd frames, 40-120 ×
8-16). One more entry (`0x70000`, "type 0") is an artifact of the script's
fallback range after the frame table's last entry, not a record.
`KEND_1.BIN` is therefore a decoded store: type 2.

### The stores (renders reviewed by the agent)

The attract run loads (`attract_loads.json`, `@` names resolved from
`OPDEMO.BIN`'s pointers `0x06065958`-`0x06065994`): `FIX.BIN` (VDP2
`0x0`), `OPS0_0.BIN` and `OPS0_1.BIN` (WRAM-L `0x00200000`, `0x00280000`),
`CAPCOM.PIX`, `OPS10.PIX`, `OPS00.PIX` and `RANKBG.PIX` (VDP2 `0x20000`;
`OPS00.PIX` also to `0x060A6800`), per demo stage `STG0n.BIN`,
`ST0n_FNT.BIN` (VDP2 `0x19000`), `ST0n_SPR.BIN` (VDP1 `0x20000`), and
`PL11_0.BIN` (VDP1 `0x38000`), `PL13_0.BIN` (`0x060A6800`), and the mechs'
`M3PL*`/`M3CB*` files. The select and VS screens use `SELECT.VAD` (bank 56)
and `PL3F_0.BIN` (bank 63) (D-052).

- **`FIX.BIN`** (319,488 bytes, 9,984 tiles): Latin throughout; no kana or
  kanji. Tile ranges (64 a row) in the "English Art In The Fonts" table of
  `docs/text_surfaces.md`.
- **`ST00`-`ST0A_FNT.BIN`**: stage background tiles; text in them can only
  be read through the stage maps. The first demo, which shows the city
  signs, loads `ST00_FNT.BIN` and `ST00_SPR.BIN` (frames 4792, 4865), so
  the signs are in one of them (SUPPORTED; not located).
- **`KANJI.BIN`**: the story font (D-019). Glyphs 23-32 are full-width
  digits and 33-58 full-width capitals `A`-`Z`; no lower case. The current
  image adds the English pair glyphs (D-024).
- **`*.PIX`**: all four decode as 512-wide 8 bpp bitmaps. `CAPCOM.PIX`
  (352 × 224, 103 colours) is the Latin company logo; `OPS00.PIX` (a grid),
  `OPS10.PIX` (stripes) and `RANKBG.PIX` (a plain field with dots) have no
  text.
- **Bank 56** (`SELECT.VAD`): besides the labels `EXP-0057` listed, pattern
  399 (`SELECT.VAD` `0x39460`, 48 × 106, frame `0x35`, the `BODY TYPE`
  panel, stored mirrored) is a Latin list of the four base bodies' names in
  a small plain font. `EXP-0057` and D-052 said bank 56 holds no Latin mech
  name: this is a correction (the list is not a version of the name
  banners; the VS mech names are still katakana only in bank 63).
- **Unknown formats** (not decoded; never drawn on before decoding):
  `OPS0_0.BIN`, `OPS0_1.BIN`, `ST0n_SPR.BIN`, `PL11_0.BIN`, `PL13_0.BIN`,
  `M3PL*`, `M3CB*`. Each is loaded raw by the named loader `0x060385A0`;
  their readers are not traced. The census saw no Japanese on the screens
  that use them except the city signs.

## Conclusion

Both predictions met. The menu font is `FIX.BIN` and has `t`-`z`;
`KEND_1.BIN` is type 2, so the cast roll's Latin names are decoded art
that a later task can copy. The inventory is in `docs/text_surfaces.md`.
New: bank 56 holds a Latin list of the four base bodies (a correction to
D-052's wording).

## Uncertainty and Alternatives

- Tile ranges in `FIX.BIN` were read from 4× gridded renders, by the agent;
  a range's description says what it mostly holds. Palettes are not
  known: the "colours" are the 4-bit indices used, not RGB.
- `FIX.BIN` tiles 1536-1599 (left half) hold large grey art whose tile
  layout was not assembled; it is not identified.
- Stage stores other than the demos' were rendered but not read for text;
  the city signs' tiles are not located.
- The unknown-format stores could hold art not seen in the census.
