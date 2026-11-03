# EXP-0021: No Native English Path; What the Box Holds

Task: FONT-002
Status: DONE
Confidence: CONFIRMED (no language branch and no English dialogue data; full-width Latin; unknown codes; no wrap; rows from the record; 4 visible rows; the 60-cell reservation); SUPPORTED (the hang past 60 cells)

## Observation

The renderer reads two bytes per glyph and looks each code up in a 1,222-entry
table. The font `KANJI.BIN` has full-width digits and capitals but no lower
case, plus the pair glyphs `Dr` and `!?` (D-019). In XvSF a leftover arcade
English mode made font capacity work unnecessary (`docs/lessons_from_xvsf.md`,
lesson 1).

## Hypothesis

- **A:** if the Saturn port kept an English path, it shows as a branch on a
  flag, region or language value near the text code, and English dialogue
  data on the disc.
- **B:** without one, the box's capacity follows from the layout code, and
  live RAM tests show it.

## Controlled Change

Phase A changes nothing. Phase B makes one live WRAM-H write per test from
checkpoint A, while paused and before the box types. The control is the same
run without a write.

## Prediction

- **A:** none of the text code's branches depends on a region or language;
  no English dialogue exists on the disc.
- **B:** full-width capitals draw as mapped; codes outside the table draw
  nothing. Rows of 16 cells; more rows only from the box record.

## Inputs and Provenance

- Checkpoint A `local/checkpoints/m1/a-box-open.mcs` (`236c610e…ddfc`,
  EXP-0015). Its WRAM-H dump in `research/memory_dumps/dbg004/a-box-open/`
  (EXP-0016). Halt dump `local/font001/trace1/workramh.bin` (EXP-0020).
- `STG0AS.BIN`, `KANJI.BIN` and all 264 data-track files from
  `local/extracted/saturn_jp/`.
- The arcade English decode `local/ref003/text-cybotsu.json` (REF-003,
  ignored) and the pairing `data/text/saturn_arcade_pairing.json` (D-011).
- Untouched image (Redump 58190); all 63 components unchanged after the work
  (`local/logs/font002-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/sh2/disasm.py` | The typing routine, the layout loop, the cell allocator |
| `tools/mednafen/replay_state.py` | PC log of the layout loop's entries |
| [`write_text.py`](write_text.py) | Live writes from checkpoint A (tests `capitals`, `unknown`, `long`, `breaks`, `rows`, or `control`), 25-frame steps with screenshots |
| [`capacity.py`](capacity.py) | Fit counts for the 450 paired arcade slots (counts only) |
| `tools/font/kanji.py` | Code table (D-019) |

Dialogue-strip crop `352x72+0+168` hashed as raw RGB (ffmpeg).

## Procedure

```bash
H=local/font001/trace1/workramh.bin
./invenv.sh python -m tools.sh2.disasm $H --base 0x06000000 --start 0x0606E5C0 --end 0x0606E9B6
./invenv.sh python -m tools.sh2.disasm $H --base 0x06000000 --start 0x0601118E --end 0x060111F4
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/checkpoints/m1/a-box-open.mcs local/font002/entry1 --steps 2 --step-frames 60 \
  --bp pc:0606E734,0606E6E0,0606E710 --agent-dir local/font002/agent-e
for t in control capitals unknown long breaks rows; do
  ./invenv.sh python research/experiments/EXP-0021/write_text.py local/font002/$t $t
done
./invenv.sh python research/experiments/EXP-0021/write_text.py local/font002/rows2 rows 24
./invenv.sh python research/experiments/EXP-0021/capacity.py local/ref003/text-cybotsu.json
```

Scratch searches (English words over the 264 files) were made inline. They are
described under Phase A. 17:55-18:04 local, 2026-11-02, the user present.

## Actual Result

### Phase A: native path

- **Typing routine** (`0x0606E5C0`-`0x0606E6CA`). It walks the box record at
  `r13` and checks these bytes and words:
  - the header byte `@r2` for 4 or 5, which moves the base x by `0xFF80`
    (−128; a box layout variant, presumably the portrait side);
  - the text byte for 0 (end of the line);
  - the entry word for `0xFFFF` (another line follows) or anything else (the
    box ends);
  - the flag bytes `0x060CFE9E`, `0x060CFF04` and `0x060AE682` (typing,
    waiting and skip states, from their use).

  For each two-byte character it builds a one-character buffer at
  `0x0600CBA8`: the high byte (from `0x0603963E`, a compiler helper that
  shifts right by 8), the low byte, then 0. It calls the layout
  loop at x = base + 14 × column and y = base + 16 × row. A PC log shows that
  call every 5 frames with R4 = `0x0600CBA8`, R5 = `0x74`, `0x82`, `0x90` … and
  R6 = `0x9C`.
- **Layout loop** (`0x0606E734`, entries `0x0606E6E0` and `0x0606E710`). It
  checks:
  - column ≥ 16 (wrap);
  - the byte `0x0A` (line break);
  - a 0 byte (end), as the first or second byte of a pair.

  Then it looks the code up (D-019). A code with no glyph (`0x8140`, `0x2020`
  or anything not in the table) takes a position but no cell. Its wrap and
  line-break logic never acts while a box types, because it is given one
  character at a time.
- **No branch** in either routine reads a region, language or option value.
- **No English dialogue on the disc.** The 40 most frequent words of six or
  more letters in the paired arcade English were searched in all 264
  data-track files: as ASCII, in the arcade's one-byte code (D-009) and as
  full-width Shift-JIS. There is one ASCII hit, `weapon` in `CYBER.BIN`'s
  English cast list ("Final weapon's Brain", near names such as "SHADE"). It
  is not dialogue, and there is no other hit.
- **Conclusion A:** there is no native English path to switch on.

### Phase B: live tests (checkpoint A, all writes read back exactly)

| Test | Address, bytes | Completed box (step 11) | Strip hash |
| --- | --- | --- | --- |
| control | none | the original box | ead786 |
| capitals | `0x0606F09C` 26: full-width `A`-`M`; `0x0606F0B8` 24: `0`-`9`, `N`, `O` | `ABCDEFGHIJKLM` / `0123456789NO`, as mapped | 4afb40 |
| unknown | `0x0606F09C` 26: `AB` (half-width), `ａ`, `Dr`, `!?`, 9 × `あ` | two blank cells, then the `Dr` and `!?` pair glyphs, 9 × `あ`; line 2 unchanged | ba1d83 |
| long | `0x0606F09C` 41: full-width `A`-`T` and a NUL (over line 4's NUL and line 5) | row 1 runs on from x = 116: `A`-`P` in full, `Q` cut at the screen edge, and `R`-`T` off-screen; row 2 is line 5's pointer reading the overwritten bytes: `OPQRST` | 0f7939 |
| breaks | `0x0606F09C` 26: `AA` `0A` `BB` `0A` … `EEF` | one row: `AA`, three blank cells, `CC`, three blanks, `EEF`. Each `0A` makes a pair with the next byte that is not in the table, and the pairs after it are misaligned (`BB`, `DD` lost) | 6dfdb3 |
| rows | record `0x0609D198` 28: line 5's word `FFFF`, then entries line 4 `FFFF`, line 5 `FFFF`, line 4 `0000` (over the padding and the next record's header) | rows 1-4 inside the box: lines 4, 5, 4, 5. Row 5 (y = 220) types below the box's bottom edge | 1beaf4 (step 11) |

- The control's completed box is `ead786`, as in every earlier replay. Every
  test reaches the same next box at step 12 (`d3c6fc`), except `rows`, whose
  next record header was overwritten.
- **Cell limit.** `0x0601118E` is called with 60 and sets the cell base to
  `0x06100000` − 60 × `0x80` = `0x060FE200`, so 60 cells are reserved per box,
  ending at the last byte of WRAM-H. The allocator `0x060111F4` adds `0x80` per
  glyph and has no limit check.
  - In the `rows` run, rerun for 24 steps (`rows2`), the fifth row types until
    step 13, at about 58 cells in all. From step 14 the screen is black to the
    end of the run (11 steps, 275 frames).
  - So a box that needs more than 60 cells writes past WRAM-H and hangs the
    game (SUPPORTED: the timing fits the 61st cell; the exact cell was not
    traced).
- **Row width.** From x = 116, 16 cells fit before the screen edge at 352. A
  17th cell is cut off (`long`). In Shade's reply, with the portrait on the
  right, text starts at x = 12 and the portrait at about x = 236: 16 cells
  again.
- **Punctuation in the table:** `！` `？` `．` `”` `ー` and `、` `。` are present;
  the full-width comma `，` and apostrophe `’` are not.

### Capacity statement (inputs to `LAYOUT-001`)

- **The box:** 4 visible rows × 16 cells, at most **60 glyph cells** in all.
  Spaces take a position but no cell. No wrapping: the rows are the record's
  lines.
- **The paired arcade English** (450 slots, D-011): the longest line is 32
  characters, and the most lines is 4 (`capacity.py`).

| Route | What it needs | Paired slots that fit (≤ 4 rows, ≤ 60 cells) |
| --- | --- | --- |
| Full-width capitals, arcade line breaks | the existing font (plus a comma and an apostrophe) | 31 of 450 |
| Full-width capitals, re-wrapped to 16 | the same, and new line entries per record | 272 of 450 |
| Pair glyphs (2 characters per cell), re-wrapped to 32 | 571 distinct pairs, as glyphs and table codes | 450 of 450 |

- **Font room:**
  - The table has 1,248 slots (1,222 used) and the font 1,280 glyphs (58
    free).
  - Lower case alone (26 glyphs) fits the free room. The pair route's 571
    glyphs do not, unless glyphs the English build no longer needs are
    reused: kanji and kana, if no Japanese text stays on that font.
  - Records whose lines change count also need new record entries. Records
    are packed back to back (`0x0609D184`: an 8-byte header, then 8-byte
    entries), so that is a relocation question for `RE-002` and `LAYOUT-001`.
- There is **no native English path**.

## Conclusion

**CONFIRMED:** the Saturn renderer has no language branch, and the disc has no
English dialogue: there is no arcade English to switch on.

The box draws full-width Latin capitals and digits from the existing font.
Codes outside the table draw blank cells. Each line is a single row with no
wrapping; extra rows come only from the record's entries. Four rows of 16
cells are visible.

The box reserves 60 glyph cells with no bounds check, and exceeding them hangs
the game (SUPPORTED). Two characters per cell fits every paired arcade record;
single full-width capitals fit 272 after re-wrapping.

## Uncertainty and Alternatives

- The `rows` test overwrote the next record's header, so its later behaviour
  (and the hang) mixes two effects. The cell limit is also bounded from the
  code, which has no check.
- Other box types (header byte 4 or 5, VS captions, endings) may have other
  origins and widths; only the M1 box and Shade's reply were seen.
- Readability of 7-pixel characters in pair glyphs is a `LAYOUT-001`
  question, for the user.

## Reproduction

Run the procedure. Expect the strip hashes in the table and a black screen
from step 14 of `rows2`. `capacity.py` should print 31, 272 and 450 fits and
571 pairs.
