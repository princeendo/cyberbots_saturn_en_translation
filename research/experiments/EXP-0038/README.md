# EXP-0038: How Jin's Ending Draws Each Surface, and With Which Font

Task: END-002
Status: DONE
Confidence: CONFIRMED (dialogue font and path; cast roll, credits and QSound layers and sources); SUPPORTED (the cast roll's names are whole-name images, not glyphs)

## Observation

`EXP-0037` listed the ending's surfaces. Its boxes matched cells predicted
from the dialogue font, yet the M5 image's replaced `KANJI.BIN` glyph did
not reach the ending. The ending reads `SE.DAT` (512 KiB, an exact copy of
`KANJI.BIN` at `0x40000`-`0x67FFF`) and no `KANJI.BIN`. The cast roll,
credits and QSound notice were not traced.

## Hypothesis

1. The ending's dialogue boxes (scenes 16-19) use the story's path: the
   Shift-JIS lines in `END.BIN` in RAM, the code table, and glyph cells at
   `0x060FE200` (D-019, D-020). Their glyphs come from VDP2 VRAM
   `0x40000`, which holds `SE.DAT`'s copy of the font, not `KANJI.BIN`.
2. Each later surface is on one layer with one pixel source in one file.

## Controlled Change

One change per run. Every run starts from a saved state and has a no-change
control from the same state.

| Run | State | Change | Purpose |
| --- | --- | --- | --- |
| `font` | END-001 checkpoint | Image `build/end002/sedat_probe/`: `SE.DAT` file offsets `0x509C0`-`0x50BFF` (128 bytes, glyph 535's four tiles in the font copy) set to `0xEE`, the solid block `EXP-0020` used. `KANJI.BIN` and every other byte are unchanged; one sector (LSN 4,685) differs. | Font source |
| `line` | END-001 checkpoint | RAM `0x0607017C` (line 752, first character, in `END.BIN` at `0x06060000`): `8D A1` (glyph 535) to `8E 9F` (glyph 600), one frame before box 408 opens | Text path |
| `qsd` | `s13113` (QSound notice) | VDP2 VRAM `0x200B4`+`0x200`×k, k = 0-9, 217 bytes each set to 0: bitmap rows 180-189, x 84-300 | The Japanese line |
| `credits` | `s09106` (staff credits) | VDP2 VRAM `0x820`-`0x83F` set to 0: character `0x41` | One font character |
| `thanks` | `s12488` (`THANK YOU FOR PLAYING!`) | The same | The same, second screen |
| `cast` | `s07284` (cast roll) | VDP1 VRAM `0x9140`-`0x92F7` set to 0: Arieta's katakana name sprite | One name sprite |
| `cast-source` | `s07284` | WRAM-L `0x002BFF79`-`0x002BFF88` set to 0: `KEND_1.BIN` offsets `0x3FF79`-`0x3FF88`, the decoder's command stream when it writes that sprite's shadow | The name's source |

Glyph 535 is the first character of line 752 (box 408, Jin's first ending
box) and is used once in Jin's ending lines. Glyph 600 is `EXP-0020`'s probe
glyph.

## Prediction

- `font`: only box 408's first cell becomes the probe block, only while the
  box is open; the screen differs only in that 16×16 character. Disc reads,
  scene posts and box calls are unchanged.
- `line`: only that cell changes, to glyph 600's cell.
- `qsd`: only the Japanese line disappears.
- `credits`, `thanks`: every small `A` disappears and nothing else does.
- `cast`: only Arieta's katakana disappears, until the game refreshes it.
- `cast-source`: Arieta's katakana changes after the next copy from its
  shadow; the yellow Latin names do not.

## Inputs and Provenance

- Untouched image, `local/disc_images/cyberbots_saturn_jp_2m/` (`ENV-005`).
- END-001 checkpoint `local/end001/checkpoint/jin_ending_a16503.mcs`
  (`7e314718…64f2`).
- `local/extracted/saturn_jp/`: `END.BIN` `a4868d8d…`, `SE.DAT` `0430d5e7…`,
  `KANJI.BIN` `898de5bc…`, `FIX.BIN`, `QSD.PIX`, `KEND.BIN`, `KEND_0.BIN`,
  `KEND_1.BIN`, `ST09_FNT.BIN`; `data/text/script_census.json`.
- Probe image `build/end002/sedat_probe/image/` (Track 01 `167d5534…1202`;
  edited `SE.DAT` `79efeccc…74d8`). Built from the untouched source; not a
  release.
- States saved by the control run (while running, so their frames are
  approximate; ignored, `local/end002/control/`): `s07284.mcs`
  (`bd90ddad…0725`), `s09106.mcs` (`49eca1ec…96b4`), `s12488.mcs`
  (`25162f1a…176c`), `s13113.mcs` (`bdaae1e2…3d40`).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`sedat_probe.py`](sedat_probe.py) (`c0540549…`) | Builds the probe image: checks `SE.DAT` against the listing and its copy against `KANJI.BIN`, replaces one glyph in the copy, calls `tools.disc.patch_image` |
| [`ending_probe.py`](ending_probe.py) (`66b9a844…`) | From the checkpoint: disc reads, scene posts, `END.BIN` box calls, the 60 glyph cells at every poll, screenshots every 50 frames, full VDP1/VDP2 VRAM at given frames, save states, one RAM write after a scene post, optional log-mode write breakpoints |
| [`compare_runs.py`](compare_runs.py) (`7932b79b…`) | A test run against its control: events, cells at the same frame, each box's last cell dump, screenshot pixel differences |
| [`vram_probe.py`](vram_probe.py) (`86c3b216…`) | From a saved state: region dumps, fills, screenshots after 2, 30 and 120 frames, optional write breakpoints |
| `tools/memory/vdp1_sprites.py`, `tools/memory/vdp2_plane.py` (`load_vdp2`) | VDP1 command lists; VDP2 VRAM, CRAM and registers from states |
| `tools/sh2/disasm.py` | The decoder at `0x0601446C` |

Python 3.13.13; Mednafen 1.32.1 with the agent interface, silent home,
`MEDNAFEN_ALLOWMULTI=1` for parallel runs. After the runs, `ruff format`
reflowed the scripts and `compare_runs.py` got type annotations and a
corrected screenshot count. The `--write-bp` options were added before the
two runs that use them (`castwrite`, `cast-trace`).

## Procedure

```bash
E=research/experiments/EXP-0038
CP=local/end002/control
PROBE="build/end002/sedat_probe/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $E/sedat_probe.py build/end002/sedat_probe
./invenv.sh python $E/ending_probe.py $CP --frames 13400 \
  --vram-at 2050,3630,4410,7280,8060,9100,12480,13110 --save-at 7280,9100,12480,13110
./invenv.sh python $E/ending_probe.py local/end002/font --cue "$PROBE" --vram-at 2050
./invenv.sh python $E/ending_probe.py local/end002/line --write 0607017C=8E9F
./invenv.sh python $E/compare_runs.py $CP local/end002/font --glyph 535
./invenv.sh python $E/compare_runs.py $CP local/end002/line --glyph 535 --glyph 600
V=$E/vram_probe.py; O=local/end002/probe
for s in qsd:s13113 credits:s09106 thanks:s12488 cast:s07284; do
  ./invenv.sh python $V $CP/${s#*:}.mcs $O/${s%:*}-control; done
./invenv.sh python $V $CP/s13113.mcs $O/qsd $(for y in $(seq 180 189); do
  printf -- '--fill vdp2vram:%X:D9:00 ' $((0x20000 + y * 512 + 84)); done)
./invenv.sh python $V $CP/s09106.mcs $O/credits --fill vdp2vram:820:20:00
./invenv.sh python $V $CP/s12488.mcs $O/thanks --fill vdp2vram:820:20:00
./invenv.sh python $V $CP/s07284.mcs $O/cast --fill vdp1vram:9140:1B8:00
./invenv.sh python $V $CP/s07284.mcs $O/cast-trace --shots 2,30 \
  --write-bp 060E9140-060E9141,260E9140-260E9141
./invenv.sh python $V $CP/s07284.mcs $O/cast-source --fill workraml:BFF79:10:00
./invenv.sh python $E/ending_probe.py local/end002/castwrite --frames 6700 \
  --step 25 --cells-until 0 --write-bp 060E9140-060E92F7,260E9140-260E92F7
```

The `cast-control` run also took `--dump workraml:0:100000 --dump
workramh:0:100000 --dump vdp1vram:0:80000`. In zsh, the `qsd` fills are
passed through `${=Q}`. 2026-11-05, 08:20-09:40 local; no cold boot and no
key press. The control run takes about 15 minutes, a 6,300-frame run 7, a
state probe 15 seconds.

## Actual Result

### Dialogue boxes, scenes 16-19

| Check | Result |
| --- | --- |
| Events | `font` and `line` log the same disc reads, scene posts and box calls as the control up to their end, frame for frame. The control's 44 box calls (39 on `END.BIN`'s table) equal `EXP-0037` run C's, 65 frames earlier |
| VDP2 VRAM | At frames 2055, 3639 and 4420 (scenes 16, 18 and 19) all 512 KiB of VDP2 VRAM equal `SE.DAT` (SHA-256 `0430d5e7…`). In `font` at 2055 they equal the edited `SE.DAT` (`79efeccc…`). `SE.DAT` is a whole VDP2 VRAM image, read raw; its font copy sits where `KANJI.BIN` does in the stages (`0x40000`, D-019) |
| `font`, cells | At 403 polls at the same frame as the control (frames 1620-6300), one cell differs: cell 0, at 18 polls from 1637 to 1824 (box 408 is open 1635-1828), glyph 535 to the probe block. Of 16 boxes with a full open-close window, only box 408 differs in its last dump, in cell 0 only |
| `font`, screen | 3 of 80 same-frame screenshots differ, by 250 pixels in x 12-27, y 164-179: box 408's first character, a solid gray block (`f01791.png`, `8904880c…`; control `795f89ad…`) |
| `line` | Written at 1634 (before `8D A1`, read back `8E 9F`). Only box 408 differs in its last dump, in cell 0 only: glyph 535 to glyph 600. Its screenshot at 1744 differs from the control's at 1736 by 99 pixels in x 12-24, y 164-174, and shows glyph 600 (`c8bd1229…`; control `053738d0…`) |

Poll frames drift by a few frames between runs (the frame count at which
`frames N` returns varies); game events do not. So `line`'s polls rarely
fall on the control's frames, and its boxes are compared by last dump.

### Other surfaces

VDP2 registers from the states (`load_vdp2`): at the cast roll, credits and
thank-you screen NBG0-3 are on (2-word pattern names; NBG0 at
`0x7C000`, NBG1 at `0x78000`, NBG3 at `0x76000`); at the QSound notice only
NBG1 is on, as a 256-colour 512×256 bitmap at `0x20000`.

| Surface | Layer | Pixel source | Change | Result (screenshot after 2 frames, against its control) |
| --- | --- | --- | --- | --- |
| Cast roll, Japanese names | VDP1, one normal sprite per name line (colour word `0x40E0`, 11 px high; Latin names `0x41E0`, 8 px high) | Each frame the decoder at `0x0601446C` writes a shadow at WRAM-H `0x060E0000` + the sprite's VDP1 offset, from command and literal streams in `KEND_1.BIN`, which is loaded raw at WRAM-L `0x00280000` (`KEND_0.BIN` at `0x00200000`, `KEND.BIN`, code, at `0x06060000`). The shadow is copied to VDP1 VRAM | `cast`: sprite zeroed | Arieta's katakana gone, her Latin name kept; 172 pixels in x 176-250, y 74-83. Restored by 30 frames (`still_filled` false) |
| | | | `cast-source`: 16 command bytes zeroed | At 2 frames the names are unchanged. At 30 frames Arieta's katakana is other, katakana-like shapes; Gawaine's two names and the portraits of Arieta and of Bao and Mao, decoded later from the same streams, also change. The yellow Latin names do not |
| Staff credits | VDP2 NBG0 | `FIX.BIN`, loaded raw at VDP2 VRAM `0x0` (all 58 characters in use equal `FIX.BIN` at the same offset). Character n is at n × `0x20`; the small font is ASCII-indexed (`0x41` = `A`), the headings use characters `0x181`-`0x1B5` | `credits`: character `0x41` zeroed | Every small `A` gone (`SHOCH N`, `TOB NJ N`); headings unchanged (`bace1980…`; control `f31b31a2…`) |
| `THANK YOU FOR PLAYING!`, `PRODUCED BY` | VDP2 NBG0 | `FIX.BIN`, as above (56 characters) | `thanks`: the same | `TH NK YOU FOR PL YING!`; 74 pixels in x 96-214, y 64-71 (`a2236876…`; control `e3db07a1…`) |
| QSound notice, Japanese line | VDP2 NBG1, 256-colour bitmap | `QSD.PIX` loaded raw: VDP2 VRAM `0x20000`-`0x3FFFF` equals the file (131,072 bytes = 512 × 256). Screen (x, y) is bitmap (x − 16, y + 8) | `qsd`: rows 180-189 zeroed | Only the Japanese line is gone; 1,074 pixels in x 100-301, y 172-181 at 2 and 30 frames; the English lines and the logo are unchanged (`4e64e5c3…`; control `d46c3202…`) |

`ST09_FNT.BIN` is not a font: it is loaded raw at VDP2 VRAM `0x19000` and
holds the cast roll's space background (NBG1, 833 characters, and NBG3, 312
characters).

`castwrite` (from the checkpoint, write breakpoints on the name's shadow)
logged 193,715 writes, all inside the decoder (return address
`0x060144B8`), from frame 187 on. The shadow area is rewritten throughout
the ending, not only for the cast roll. `cast-trace` (from `s07284`) logged
one write per frame to `0x060E9140`, at `0x060144DA` with R4 =
`0x060E9140`, R5 = `0x002BFF79` (later `0x002BFF81`) and R6 = `0x002BFFB8`.

### The decoder

`0x0601446C` loads R11-R13 from a table at `0x060CE688` and enters a loop at
`0x060144B8`: while R4 < R7, it reads a command byte from R5 and branches
to a 16-byte handler (`braf`). The first handlers copy 1, 2 or 3 longwords
from R6 to R4. R4 is the destination, R5 the command stream, R6 the
literal stream and R7 the end. One call decodes several sprites in a row,
so zeroing commands also changes what is decoded after them.

### Font capacity

| Font or image | Glyphs | Codes | Story's font? |
| --- | --- | --- | --- |
| `SE.DAT` `0x40000`-`0x67FFF` (VDP2 `0x40000`) | 1,280 16×16, 4 bpp (D-019 layout) | `END.BIN`'s table at file offset `0x26EAC`, 1,222 codes, equal to `STG0AS.BIN`'s original | Yes, byte for byte, as a second copy that a build must change too |
| `FIX.BIN` (VDP2 `0x0`) | 8×8 4 bpp characters; in use: `0x10`, ASCII `0x20`-`0x6E` (capitals, digits, punctuation, some lower case) and a heading set at `0x181`-`0x1B5` | ASCII code = character number (no table) | No |
| `QSD.PIX` | A bitmap, no glyphs | — | No |
| Cast-roll names | Whole-name images in `KEND_1.BIN`, compressed (format not decoded) | — | No |

## Conclusion

**CONFIRMED** (`font`, `line`, against a no-change control): Jin's ending
dialogue boxes go through the story's text path and glyph cells: one cell
per character, chosen by `END.BIN`'s code table from the Shift-JIS in
`END.BIN` in RAM. Their glyphs come from VDP2 VRAM `0x40000`, filled by
`SE.DAT`, which is read raw as a whole VDP2 VRAM image. `KANJI.BIN` is not
used. A change to `SE.DAT`'s font copy shows in exactly the predicted cell.

**CONFIRMED** (one change each, against controls):
- The cast roll's Japanese names are VDP1 sprites, refreshed from shadows
  that the decoder at `0x0601446C` writes from `KEND_1.BIN` in RAM.
- The staff credits and the thank-you screen are VDP2 NBG0, drawn with
  `FIX.BIN`'s ASCII-indexed characters.
- The QSound notice's Japanese line is pixels in `QSD.PIX`, a raw
  256-colour bitmap on NBG1.

**SUPPORTED:** the names are whole-name images, not glyphs from a font:
the decoder copies longwords of pixels, and no table of codes is involved.

For later milestones:
- A translated ending must change `SE.DAT`'s copy of the font as well as
  `KANJI.BIN`. A pair glyph placed only in `KANJI.BIN` draws the original
  glyph in the ending (`EXP-0037`).
- The cast-roll names need new images in `KEND_1.BIN`'s format, which is
  not decoded yet.
- The QSound line needs an edited bitmap.

## Uncertainty and Alternatives

- Only box 408 was changed. That all ending boxes share the path rests on
  `EXP-0037` (every box's predicted cells, in full) and on VDP2 VRAM
  equalling `SE.DAT` through scenes 16-19.
- The decoder's command set beyond the first three handlers, the start of
  each name's data in `KEND_1.BIN`, and whether `KEND_0.BIN` holds any
  names are not known. Write breakpoints show only where the decoder was
  when it reached the name's slot, not where that call began.
- Other pilots' cast rolls and endings are not checked (`END-003`, `END-020`).
- Not traced, because they are not ending surfaces and are already English:
  the win tally (after every win), game over, initials and ranking (after
  every game over; `UI-003`).
- The four states were saved while running; their frames are approximate.
  They are local checkpoints: the route reproduces them, not their bytes.

## Reproduction

Run the procedure. Expect `font` and `line` to differ from the control only
in box 408's cell 0 (probe block; glyph 600), the VDP2 dumps to equal
`SE.DAT` at frames 2055-4420, and each state probe to change only the area
in the table.
