# EXP-0024: Limits of Each Layout Route, and the User's Choice

Task: LAYOUT-001 (Phases A and B)
Status: DONE for Phases A-B; Phase C (proof on a rebuilt image) is next
Confidence: CONFIRMED (code census, font users, record size, the route counts, free RAM over one full stage); SUPPORTED (dead ending lines in `STG0AS.BIN`, free VDP1 VRAM in dialogue)

## Observation

The box shows 4 rows of 16 full-width cells and at most 60 glyph cells, with
no wrapping and no native English path (D-020). The font has 1,280 glyphs, of
which 1,222 have codes in the table and 58 are free (D-019). Jin's 63 boxes
all pair with arcade English records (D-022).

## Hypothesis

Each route's cost can be measured from the game's data and a few runs:
glyphs, bytes, rows per record, and RAM. That is enough for the user to
choose a route.

## Controlled Change

None to the game. One write-breakpoint log over candidate free RAM, from a
REF-005 state with no input.

## Prediction

Some table codes are unused by every Japanese line. The text room is bounded
by the files' own layout. Free RAM, if any, shows no CPU write over a full
stage.

## Inputs and Provenance

- `STG0AS.BIN`, `END.BIN`, `VICTORY.BIN`, `KANJI.BIN` and all 264 files from
  `local/extracted/saturn_jp/`; `data/text/script_census.json`.
- The arcade English decode `local/ref003/text-cybotsu.json` (ignored; counts
  only), `data/translations/jin_pairing.json`,
  `data/text/saturn_arcade_pairing.json` (as fixed in EXP-0023).
- The 166 REF-005 states and the three M1 checkpoints. State `f00004138.mcs`
  (`3eb789da…`) for the write log.
- Untouched image; all 63 components unchanged
  (`local/logs/layout001-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`room.py`](room.py) | Rows, cells, bytes and glyphs per route, for Jin and the roster |
| `tools/font/kanji.py` | The code table |
| `tools/memory/mcs_extract.py` | WRAM and VDP1 VRAM of the session states (never-nonzero scans) |
| `tools/mednafen/replay_state.py` | The write log over candidate free RAM |

The code census, the search for callers of the glyph routines, the dead-line
check and the RAM scans were scratch scripts; their logic is described with
each result.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0024/room.py local/ref003/text-cybotsu.json
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/ref005/session/states/f00004138.mcs local/layout001/freeram1 \
  --steps 48 --step-frames 250 \
  --bp write:06002F00-06007CFF,26002F00-26007CFF,060E3300-060E7FFF,260E3300-260E7FFF \
  --agent-dir local/layout001/agent-f
```

18:44-18:55 local, 2026-11-02, the user present.

## Actual Result

### Phase A: limits

- **Code census.** Across the dialogue blocks of `STG0AS.BIN` (1,852
  strings), `VICTORY.BIN` (1,855) and `END.BIN` (1,927), the text uses
  **912** of the 1,222 table codes. **310** codes are used by no Japanese line,
  and there are 58 free glyph slots and 26 free table slots. So without
  breaking any Japanese, **336 codes** (310 + 26) and **368 glyphs** (310 +
  58) can be reused. A few codes in the text are not in the table: 3 in
  `STG0AS.BIN`, 8 in `VICTORY.BIN` and 65 in `END.BIN`'s block, which is
  larger and contains strings that are not dialogue.
- **Who draws with `KANJI.BIN`.** Literal references to the glyph routine
  `0x06011224` are in `STG0AS.BIN` (the story), `END.BIN` (the endings) and
  `VICTORY.BIN` (two sites). The cell routines `0x060111F4` and `0x0601118E`
  are in the same three. Single hits in `AC3.LF`, `AC4.LF` and four
  `M2CB0E*`/`M3CB0E*` files are in graphics data, not code. All three
  readers use the same code table bytes (D-019). A glyph that any Japanese
  line uses is shared by story, endings and `VICTORY.BIN`.
- **Records.** Records are 32 bytes apart (D-021): an 8-byte header and three
  8-byte entries. So a box holds at most **3 lines in place**; a 4-line box
  needs its record moved (the pointer table `0x060A5684` can point anywhere).
- **Text room in `STG0AS.BIN`.**
  - Jin's Japanese lines (0-120, aligned) take **3,448 bytes**.
  - Jin's ending boxes (scenes 16-20) are in `STG0AS.BIN`'s copy but shown
    from `END.BIN`'s (EXP-0022). Of their 20 boxes, 17 appear in no other
    `STG0AS.BIN` scene, and their 29 lines (752-777, 897, 898, 953), **820
    bytes**, are pointed at by no other record. That is dead room in this
    copy (SUPPORTED: it holds if `STG0AS.BIN`'s code never posts Jin's scenes
    16-20, which is true of the stage code seen).
  - Line 34 is dead data (D-021).
  - The file's last sector has 812 bytes past its end, but the loader writes
    whole sectors, and the RAM after the file (`0x060AE4D4` onward) is
    working memory: it is not room.
- **Route counts** (`room.py`; English re-flowed per route; 488 paired slots):

| Route | Jin: fit (≤ 4 rows, ≤ 60 cells) | Roster: fit | Most cells in a box | Boxes over 3 lines (Jin / roster) | Line bytes (Jin / roster) | New glyphs (Jin / roster) |
| --- | --- | --- | --- | --- | --- | --- |
| (a) full-width capitals, 16 per row | 35 / 63 | 298 / 488 | 77 | 42 / 273 | 7,544 / 53,804 | 2 / 2 |
| (b) pair glyphs, 32 characters per row | 63 / 63 | 488 / 488 | 47 | 0 / 0 | 3,992 / 28,488 | 353 / 579 |
| (c) half-width at an 8-px advance, 28 per row | 43 / 63 | 372 / 488 | 77 | 16 / 84 | 7,448 / 53,056 | 53 / 58 |
| (c) + (d), 252 cells | 63 / 63 | 488 / 488 | | | | |

  Route (c) still costs 2 bytes per character because the renderer reads
  two bytes per glyph. A first count that used 1 byte was corrected before
  this record.
- **Free RAM for code routes.**
  - **Never nonzero** in any of the 166 states (256-byte granularity): WRAM-H
    `0x06002F00` (19,968 bytes), `0x0600AD00` (6,656), `0x060DF900` (5,376)
    and `0x060E3300` (19,712). There are no such runs of 4 KiB or more in
    WRAM-L or VDP1 VRAM.
  - **No CPU writes:** the write log over `0x06002F00`-`0x06007CFF` and
    `0x060E3300`-`0x060E7FFF` (both mirrors) from state 4138, for 12,000
    frames, recorded none. The run covered the load, the narration, Jin's
    dialogue, the VS screen, both rounds of the fight (lost), the continue
    countdown, game over and the ranking screen (contact sheet in the ignored
    `local/layout001/freeram1/`).
  - **VDP1 VRAM during dialogue:** across 10 dialogue-scene states
    (4851-5563 and the M1 checkpoints), `0x0E80` (29,056 bytes), `0x16400`
    (32,256), `0x1F100` (3,840) and `0x7EA80` (5,504) are never used.
    `0x16400`-`0x1E1FF`, just below the 60-cell buffer, would hold 252 cells
    (SUPPORTED; fights use it, so route (d) would need it only while a box is
    open).

### Phase B: the decision

The routes were put to the user as one multiple-choice question:
- pair glyphs (marked Recommended);
- narrow letters with a code patch;
- full-width capitals.

Each option carried its fit and cost from the table above. The user's answer
(2026-11-02), verbatim: **"Pair glyphs (Recommended)"**.

## Conclusion

**CONFIRMED (measurements); decided:** route (b), pair glyphs.
- It fits all of Jin's boxes and all 488 paired roster boxes in 4 rows and
  60 cells.
- No record needs a fourth line.
- Jin's text (3,992 bytes) fits in the room his Japanese and his dead ending
  lines leave in `STG0AS.BIN` (3,448 + 820 bytes). It needs no code change.
- Its cost: 353 glyphs for Jin against 336 codes that no Japanese uses. Until
  every pilot is English, a few Japanese glyphs, or the pair choice, must
  give.

## Uncertainty and Alternatives

- The 336-code budget assumes pairs start at every second character of a row.
  Choosing pair boundaries per row (spaces placed to reuse pairs) may bring
  Jin under 336; that is the compiler's job in `RE-003`.
- The free-RAM log covers one stage and its game over, with no input, and a
  CPU breakpoint does not see DMA. Later stages, endings and other modes are
  not covered. The pair route does not need free RAM.
- The dead ending lines are dead only in `STG0AS.BIN`'s copy; `END.BIN` keeps
  its own.
- The readability of 7-pixel letters is to be judged on screen in Phase C.

## Reproduction

Run the procedure. `room.py` should print the counts in the table, and the
write log should record no hits.
