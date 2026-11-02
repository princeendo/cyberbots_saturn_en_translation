# EXP-0020: The Dialogue Font Is `KANJI.BIN`, 16×16 Glyphs of VDP2 Tiles

Task: FONT-001
Status: DONE
Confidence: CONFIRMED (glyph routine, code table, font file, format, mapping); SUPPORTED (two bytes per glyph, with 0x0A a line break)

## Observation

The M1 box is drawn as one VDP1 sprite per character. The sprites come from
4 bpp 16×16 cells, refilled from a WRAM-H shadow at `0x060FE200`
(D-015). `KANJI.BIN` has the cells' value palette, but the glyph was not
found in it as 1-bit or 4 bpp rows (EXP-0016). No 8-byte row of a cell occurs
raw in any data-track file (recheck, 2026-11-02).

## Hypothesis

A routine writes each cell from font data in RAM, selected by the character's
Shift-JIS code. That data is loaded from one disc file whose layout explains
why the rows were not found.

## Controlled Change

- **Traces** (no change to the game): a write breakpoint on cell 0 of the
  shadow; a PC breakpoint on the routine it finds; the CD command registers.
- **Probe image:** glyph 600 of `KANJI.BIN` (the box's first character)
  replaced by a solid block. The control is the original image, from the same
  state.

## Prediction

The cell writer's source is the font in VRAM. Its glyph numbers follow from
the codes through a table. The font file is read from the CD before the box
opens. On the probe image the box's first character is a solid block, and
nothing else changes.

## Inputs and Provenance

- M1 checkpoint A `local/checkpoints/m1/a-box-open.mcs` (`236c610e…ddfc`,
  EXP-0015). Checkpoint B dumps in
  `research/memory_dumps/dbg004/b-box-complete/` (EXP-0016).
- REF-005 states `f00005208.mcs` (`71aba73e…`; the narration before Jin's
  box) and all 166 states for the VDP2 scan.
- `KANJI.BIN` (LSN 4,780, 163,840 bytes, `898de5bc…3f86`) and `STG0AS.BIN`
  from `local/extracted/saturn_jp/`, both checked against
  `references/saturn_jp/iso_listing.json`.
- Untouched image (Redump 58190); after the work all 63 components still hash
  to the recorded values (`local/logs/font001-source-after.json`). Patched
  binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| `research/experiments/EXP-0018/trace.py` | Write-breakpoint traces (halt on the first hit, then log); `--extra` ranges, `--log` |
| `tools/mednafen/replay_state.py` | The PC-breakpoint log and the probe replays |
| `tools/sh2/disasm.py` | Disassembly of the halt dump |
| [`tools/font/kanji.py`](../../../tools/font/kanji.py) | New: decode, encode, code table, glyph sheet, with unit tests |
| [`probe.py`](probe.py) | The probe image (`tools.disc.patch_image`) |

## Procedure

```bash
A=local/checkpoints/m1/a-box-open.mcs
S=local/ref005/session/states/f00005208.mcs
CUE="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
T=research/experiments/EXP-0018/trace.py
./invenv.sh python $T $A local/font001/trace1 --frames 300 \
  --extra 060FE200-060FE27F --extra 260FE200-260FE27F
./invenv.sh python -m tools.sh2.disasm local/font001/trace1/workramh.bin \
  --base 0x06000000 --start 0x06011224 --end 0x060112D8
./invenv.sh python -m tools.mednafen.replay_state "$CUE" $A local/font001/calls1 \
  --steps 6 --step-frames 50 --bp pc:06011224 --agent-dir local/font001/agent-c
./invenv.sh python -m tools.sh2.disasm local/font001/trace1/workramh.bin \
  --base 0x06000000 --start 0x0606E7BC --end 0x0606EA58
./invenv.sh python $T $S local/font001/cdcmd1 --frames 400 --log \
  --extra 25890018-25890027 --extra 05890018-05890027
./invenv.sh python $T $S local/font001/vdp2w1 --frames 400 \
  --extra 25E52C00-25E52C1F --extra 05E52C00-05E52C1F
./invenv.sh python -m tools.font.kanji local/extracted/saturn_jp/KANJI.BIN --check \
  --table local/extracted/saturn_jp/STG0AS.BIN --sheet local/font001/kanji_sheet.png
./invenv.sh python research/experiments/EXP-0020/probe.py build/font001/probe
for r in probe original; do ...; done  # replay_state from $S, 12 x 50 frames, on each image
```

17:47-17:52 local, 2026-11-02, the user present.

## Actual Result

- **Cell writer.** From checkpoint A, the first write to shadow cell 0 is at
  frame 231, PC `0x0601123C`, in the routine at `0x06011224`. It is called
  from `0x0606E7F0`, in `STG0AS.BIN`'s code.
  - Inputs: R4 is a tile index, R6 the destination cell.
  - It copies four 8×8 4 bpp tiles from VDP2 VRAM `0x25E00000` + R4 × 32,
    `+0x20`, `+0x200` and `+0x220`.
  - Each tile row is 4 bytes, and each cell row takes 8 bytes (left tile,
    then right tile). That split is why no 8-byte cell row occurs in any
    file.
- **Calls.** A PC breakpoint on `0x06011224` logs 27 calls. 25 come while
  the box types (frames 234-354, one every 5 frames), with destinations cells
  0-24 and tile indices such as `0x2960` for the first character. The other 2
  (frames 486 and 491) start Shade's reply.
- **Code to glyph.** The caller (`0x0606E7BC`) reads two bytes of text and
  calls `0x0606E9B6`.
  - That searches the table of 16-bit codes at `0x060AAD7C` linearly
    (`0x0606E9E8`): 39 rows of 64 bytes, a 0 ending a row.
  - It returns the code's position `g` among the non-zero entries. Codes
    `0x8140` and `0x2020` return no glyph.
  - The tile index is `0x2000 + (g // 8) × 32 + (g % 8) × 2`.
  - The table is in `STG0AS.BIN` at file offset `0x4AD7C`; the same 2,496
    bytes are in `END.BIN` (`0x26EAC`) and `VICTORY.BIN` (`0x1DB94`).
  - It holds 1,222 codes and no duplicates: rows 1-38 have 32 each and row
    39 has 6. Three entries are half-width pairs: `Dr`, `!?` and two spaces.
  - This mapping predicts the logged tile index of all 25 box characters
    (25/25).
- **Font in VRAM.** The tiles at VDP2 VRAM `0x52C00` occur in `KANJI.BIN` at
  `0x12C00`, so the file sits at VDP2 VRAM `0x40000`. The tiles also occur in
  `SE.DAT` at `0x52C00`: `SE.DAT[0x40000:0x68000]` equals `KANJI.BIN`.
- **Reloaded for the box.** In the session states the `KANJI.BIN` region of
  VDP2 VRAM equals the file in most states, but not at 5386 (77 of 80
  sectors differ). At checkpoint A, 10 frames later, sectors 0-17 are back
  and 18-79 are not; at B and C it is all back.
- **The read.** From state 5208, the CD command log shows Play Disc
  `1080 5C61 0080 0020` at frame 335: 32 sectors at LSN 23,499,
  `SCR10.PIX`. Then Play Disc `1080 1342 0080 0050` at frame 358: FAD
  `0x1342` − 150 = LSN 4,780, 80 sectors, which is `KANJI.BIN`. There is no
  read of `SE.DAT`.
- **The copy.** A write breakpoint on VDP2 VRAM `0x25E52C00`-`0x25E52C1F`
  catches 32 zero writes at frame 333 (PC `0x06039714`, a clear). At frame
  383 come 8 writes at PC `0x06041FB4`: the same CD-to-memory copy as
  EXP-0018, from R13 = `0x25818000`. The first word is `0x09C0099D`,
  `KANJI.BIN[0x12C00]`.
- **Format.** 1,280 glyphs of 16×16 at 4 bpp, as 8×8 VDP2 tiles (32 bytes)
  in a sheet 16 tiles wide.
  - Glyph `g` is tiles `t`, `t+1`, `t+16`, `t+17` with
    `t = (g // 8) × 32 + (g % 8) × 2`, so 8 glyphs make a 1,024-byte group
    and 160 groups make 163,840 bytes.
  - `tools/font/kanji.py --check` re-encodes the decoded glyphs
    **byte-identical** to the file.
  - Values used: 0-4 and 9-14. 60 glyphs are blank: the 58 slots past the
    table, and two table entries.
  - The sheet (agent-reviewed, in the ignored `local/font001/`) shows
    punctuation, **full-width digits and capitals A-Z** (no lower case),
    hiragana, katakana, kanji, and at the end the `Dr` and `!?` pair glyphs.
- **Mapping against the screen.** Decoded glyphs for the 25 box characters
  equal checkpoint B's WRAM-H shadow cells (25/25) and VDP1 cells at
  `0x1E200` (25/25).
- **Probe.** Glyph 600 (`0x8E9F`, the box's first character), set to value 14
  throughout, changes one sector: LSN 4,817 (predicted, the group at file
  offset `0x12C00`). All sectors pass EDC/ECC, and the Track 01 SHA-256 is
  `83650b3f…`. Replays from 5208, 12 × 50 frames, dialogue-strip hashes:

| Run | Steps 1-4 | Steps 5-8 (box typing, then complete) | Steps 9-12 |
| --- | --- | --- | --- |
| probe | e7afda e7afda 3d8fbe 3d8fbe | abced7 5bd189 c5ecbf **16c0bf** | 9f8f08 3891a4 2109ec |
| original | same | 0efd14 79a223 780fdc **ead786** | same |

  Agent-reviewed step 8: on the probe image the first character is a solid
  16×16 block of one gray, and the other 24 characters are unchanged. The
  original shows the original box. The probe image was deleted afterwards
  (user rule; `probe.py` rebuilds it).
- Source manifests are unchanged, and so are both home configs.

## Conclusion

**CONFIRMED:**

- The dialogue font is `KANJI.BIN`. It is read from the CD into VDP2 VRAM
  `0x40000` as each box scene starts, by the same raw loader as the script.
- It holds 1,280 4 bpp 16×16 glyphs made of 8×8 VDP2 tiles. The layout is
  proven by a byte-identical repack.
- A character's glyph is its position in a 1,222-entry code table in the
  resident `STG0AS.BIN` (`0x060AAD7C`). The routine at `0x06011224` copies
  the glyph's four tiles into the WRAM-H cell that VDP1 draws.
- The mapping predicts all 25 rendered cells. A one-glyph probe image changes
  exactly that character on screen.

## Uncertainty and Alternatives

- Text is read two bytes per glyph, with `0x0A` a line break
  (`0x0606E76C`). This is SUPPORTED from the disassembly; single half-width
  bytes outside the table's pairs were not tested (`FONT-002`).
- What else `SE.DAT`, which contains `KANJI.BIN` at `0x40000`, is used for is
  not known; it was not read in these scenes.
- Values 1-4 occur in some glyphs; the palette behind 0-14 was not read. The
  probe's value 14 drew a mid gray.
- The table has 26 unused slots (39 × 32 − 1,222) and the font 58 free
  glyphs; whether the game reads the slots past entry 1,222 is not tested.

## Reproduction

Run the procedure. Expect PC `0x0601123C` at the first cell write, 25 calls
matching the table, Play Disc FAD `0x1342` for 80 sectors, a byte-identical
repack, 25/25 cells, and the probe's block in place of the first character.
