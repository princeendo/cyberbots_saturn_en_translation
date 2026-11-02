# EXP-0016: The M1 Box's Renderer and Its RAM Text

Task: DBG-004
Status: DONE
Confidence: CONFIRMED (Shift-JIS text in RAM, resident overlay, VDP1 per-character sprites, glyph shadow in WRAM-H); UNKNOWN (KANJI.BIN's glyph layout)

## Observation

The M1 box (Saturn lines 4-5) has three checkpoints (`EXP-0015`). The script
is plain Shift-JIS in three program files that all point at `0x06060000`
(D-008). Both siblings drew their quote text as VDP1 sprites from a 16-bit
code table, not Shift-JIS; for Cyberbots that is only a hypothesis.

## Hypothesis

At checkpoint B, lines 4-5 are in work RAM as Shift-JIS inside one resident
overlay, and the box is drawn by VDP1 sprites, one per character.

## Controlled Change

One write: the 128 bytes of the first glyph cell in VDP1 VRAM set to zero
while halted at checkpoint B, then restored.

## Prediction

A Shift-JIS search of WRAM finds lines 4-5 once; the zeroed cell blanks the
box's first character on screen.

## Inputs and Provenance

`local/checkpoints/m1/{a-box-open,b-box-complete,c-after-box}.mcs`
(`EXP-0015`); regions extracted with the validated extractor (D-006) to the
ignored `research/memory_dumps/dbg004/` (checkpoint B: WRAM-H
`06f115a0…`, WRAM-L `10dd14fd…`, VDP1 VRAM `01e0abc6…`). Untouched image;
patched binary `2fc3d547…eaaf`.

## Tools and Environment

`tools/memory/mcs_extract.py`, `tools/memory/vdp1_sprites.py`,
[`glyph_write.py`](glyph_write.py) (agent: load, run, read, write VDP1 VRAM,
screenshot, restore), scratch searches.

## Procedure

```bash
for c in a-box-open b-box-complete c-after-box; do
  ./invenv.sh python -m tools.memory.mcs_extract local/checkpoints/m1/$c.mcs \
    --region wram_l --region wram_h --region vdp1_vram --region vdp2_vram \
    --out-dir research/memory_dumps/dbg004/$c
  ./invenv.sh python -m tools.memory.vdp1_sprites \
    research/memory_dumps/dbg004/$c/vdp1_vram.bin --json
done
./invenv.sh python research/experiments/EXP-0016/glyph_write.py \
  local/checkpoints/m1/b-box-complete.mcs local/dbg004/write1
```

## Actual Result

- **RAM text.** In all three checkpoints, lines 4 and 5 occur once in work
  RAM, as Shift-JIS: WRAM-H `0x0606F09C` and `0x0606F0B8`; the dialogue
  table starts at `0x0606F01C`; nothing in WRAM-L.
- **Resident overlay.** `STG0AS.BIN` (320,724 bytes) equals WRAM-H from
  `0x06060000` in all but 30 bytes (pages `0x06063xxx`-`0x06064xxx`), and its
  dialogue region is byte-identical. So in a stage scene the resident copy of
  the script is `STG0AS.BIN`'s.
- **Renderer.** At checkpoint B, VDP1 draws the box text as 25 normal
  sprites, color word `0x70E0`, 16×16 at 4 bpp, 13 at Y 156 and 12 at Y 172,
  14 pixels apart from X 116, with glyph cells at VDP1 VRAM `0x1E200` +
  `0x80` × n (`0x1E200`-`0x1EE7F`). The render of those sprites alone shows
  the two lines. Checkpoint A has none (box empty); at C the same cell buffer
  holds Shade's reply (12 + 13 sprites at X 12).
- **Controlled change.** Zeroing cell 0 (49 non-zero bytes before) blanked
  `次`, the box's first character, on the screen two frames later
  (dialogue-strip hash `9197a449` against `ead786a2` before); by 62 frames
  it was drawn again (`ead786a2`), and the VRAM read-back was no longer zero
  after 2 frames: the cells are refilled continually. Restoring the bytes
  left the box as before.
- **Glyph source.** The cell's bytes also sit in WRAM-H at `0x060FE200`
  (VRAM offset `0x1E200` above `0x060E0000`), a likely shadow copied to VDP1
  every frame. The glyph is anti-aliased (4 bpp values 0 and 9-14), about
  12×11 pixels. `KANJI.BIN` has the same value palette (nibbles 0 and 9-14
  dominate) but does not contain this glyph as a 16×16 1-bit image, nor as
  4 bpp rows of 10-16 pixels at shifts 0-3; its layout is **UNKNOWN**.
- Source manifests identical before and after; both home configs unchanged.

## Conclusion

**CONFIRMED:** unlike both siblings, Cyberbots keeps its dialogue in RAM as
plain Shift-JIS (in the resident `STG0AS.BIN` overlay at `0x06060000`), and
draws each box as one VDP1 sprite per character from 4 bpp anti-aliased
glyph cells, refilled from WRAM-H. Whether `KANJI.BIN` is the glyph source
is tested and still open.

## Uncertainty and Alternatives

- That the WRAM-H copy is a per-frame shadow (not a font cache) is inferred
  from the refill; the writer of the VDP1 cells was not traced.
- Because glyphs are rendered into cells as the box types, an M1 RAM edit of
  the Shift-JIS text should be made before the box draws (checkpoint A or
  earlier), not after (`RE-001`).
- `END.BIN` and `VICTORY.BIN` presumably replace `STG0AS.BIN` in other
  scenes; not observed.

## Reproduction

Run the procedure; expect the RAM hits, the 25 sprites, and the dialogue-strip
hashes above.
