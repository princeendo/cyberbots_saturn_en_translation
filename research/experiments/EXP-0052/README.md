# EXP-0052: Where the Boot Warnings Are Stored and How They Are Drawn

Task: BOOT-002
Status: DONE
Confidence: CONFIRMED (file per screen, format, palette source, layer, visible area)

## Observation

- `EXP-0051` (D-048): each warning is drawn by `0x06036DA8`, which loads
  `WARNINGn.PIX` raw to VDP2 VRAM `0x20000` (0x20000 bytes). At each
  capture VRAM there equals the file.
- The routine also clears VDP2 VRAM from `0x19000` to the end (`0x06011FC6`,
  0x19C00 longs) and copies 16 colours from `CYBER.BIN` `0x06053AAC` to
  colour bank 32 (`0x0600F334`, R5 = 32).
- Every file holds bytes 0-15 only; files 0-3 have 38,400 zero bytes
  (160 × 240), file 4 another 8,192 (16 rows × 512).

## Hypothesis

Each picture is a 512-wide, one-byte-a-pixel VDP2 bitmap; the program's
16-colour table is its palette; 352 columns and the rows the display reaches
are visible; each screen shows its own file and nothing else changes.

## Controlled Change

1. None (static): decode each file with the hypothesized format and compare
   it with `EXP-0051`'s screenshot pixel for pixel; read the VDP2 registers
   and colour RAM from `EXP-0051`'s warning states.
2. One test image from the untouched source (`mark.py`, never shipped) with
   markers in all five files, booted under each `EXP-0051` condition.

## Prediction

1. 0 differing pixels at one offset for all five.
2. On each warning screen, against the untouched one, only the marker's
   visible pixels change: the ID block of that file (screen rows 8-11,
   columns 16n to 16n+15, cyan) and the bottom band (screen rows 236-239,
   yellow). No red pixel (the marks in hidden rows and columns). The normal
   boot is unchanged.
3. Added after the first result (the band did not show): from the untouched
   `WARNING1` state, VRAM writes show file rows 220-223 and hide 224-227
   (`edge.py`).

## Inputs and Provenance

| Input | SHA-256 (first 16) | Notes |
| --- | --- | --- |
| `WARNING0`-`4.PIX` (untouched) | as `references/saturn_jp/iso_listing.json` | checked by `mark.py` |
| `CYBER.BIN` | as the listing | the palette at file offset `0x46AAC` |
| `EXP-0051` screenshots and states | `local/boot001/<case>/w01457.png`, `s01457.mcs` | the untouched reference |
| Marked Track 01 | `9899db92af2bb9e3` (full in `build/boot002/marked`) | 29 sectors changed, regenerated EDC/ECC (`tools.disc.patch_image`) |
| Marked files | `08e781af49e93216`, `5e83554513e8a59d`, `5ba163d1ad2296d4`, `b9325e91fdf40817`, `b0e09e0b86fd61de` | `WARNING0`-`4`; 116 ranges with original bytes in `build/boot002/marked/changes.json` |
| Fixtures | as `EXP-0051` | `local/boot001/fixtures/` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`decode.py`](decode.py) | Draw each file with the program's palette; compare with the screenshot → [`decode.json`](decode.json) |
| `tools.memory.vdp2_plane.load_vdp2` | VDP2 registers and colour RAM from the `EXP-0051` states |
| [`mark.py`](mark.py) | The marked test image (never ships) |
| `EXP-0051/boot_case.py --cue` | The six cold boots of the marked image |
| [`compare.py`](compare.py) | → [`compare.json`](compare.json) |
| [`edge.py`](edge.py) | VDP2 VRAM writes from a warning state |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0052/decode.py \
  --png-dir local/boot002/decoded --out research/experiments/EXP-0052/decode.json
./invenv.sh python research/experiments/EXP-0052/mark.py build/boot002/marked
F=local/boot001/fixtures; P=research/experiments/EXP-0051/boot_case.py; O=local/boot002
CUE="build/boot002/marked/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python $P $O/control --cue "$CUE" --bkr $F/save.bkr --frames 1800
./invenv.sh python $P $O/damaged --cue "$CUE" --bkr $F/damaged.bkr --frames 1800
./invenv.sh python $P $O/zero --cue "$CUE" --bkr $F/zero.bkr --frames 1800
./invenv.sh python $P $O/cart-zero --cue "$CUE" --bkr $F/save.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python $P $O/both-zero --cue "$CUE" --bkr $F/zero.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python $P $O/free4 --cue "$CUE" --bkr $F/free4.bkr --frames 1800
./invenv.sh python research/experiments/EXP-0052/compare.py --out research/experiments/EXP-0052/compare.json
./invenv.sh python research/experiments/EXP-0052/edge.py local/boot002/edge
```

2026-11-06, 08:00-08:50 local. Six cold boots, asked first: "Yes, run all 6
(Recommended)". No key was pressed.

## Actual Result

### Format (static, `decode.json`)

- All five pictures redraw with **0 differing pixels**: 512 bytes a row, one
  byte a pixel; colour = entry *value* of the program's 16-colour table
  (RGB555, shown as `c << 3`); value 0 transparent (the black back screen);
  screen row = file row + 8, screen column = file column.
- The first colour rule tried, `(c << 3) | (c >> 2)`, mapped each value to
  one wrong-by-a-few-levels colour; `c << 3` matches all.

### Registers and colour RAM (the `EXP-0051` states, `load_vdp2`)

`TVMD 8001` (display on, 352 wide, 224 lines), `BGON 0002` (only NBG1),
`CHCTLA 1200` (NBG1: bitmap, 512 × 256, 256 colours), `MPOFN 2212` (NBG1
bitmap at `0x20000`), `BMPNA 0200` (bitmap palette 2: colour RAM from entry
512), `CRAOFA 0000`, `RAMCTL 1000` (2,048 RGB555 colours). Colour RAM
entries 512-527 equal `CYBER.BIN`'s table, and no other entry is set. Same
in the `zero`, `free4` and `damaged` states.

### The marked image (`compare.json`)

| Case | Warning (marked / untouched) | ID block pixels as predicted | Other pixels changed | VRAM = marked file |
| --- | --- | --- | --- | --- |
| damaged | 0 / 0 | 64 of 64 | 0 | yes |
| zero | 1 / 1 | 64 of 64 | 0 | yes |
| cart-zero | 2 / 2 | 64 of 64 | 0 | yes |
| both-zero | 3 / 3 | 64 of 64 | 0 | yes |
| free4 | 4 / 4 | 64 of 64 | 0 | yes |

- Each screen shows only its own file's ID block (columns 16n to 16n+15).
- **The bottom band did not show** (1,408 predicted pixels stayed black),
  and no hidden red mark showed. The 71 red pixels on the `WARNING4` screen
  are its own (value 9, also on the untouched screen).
- Control: all 6 screenshots equal the untouched control's at the same
  frames; the check's routine sequence is the same.
- Screens: `5c8fab47…`, `b20dc7a3…`, `06a3d153…`, `433cbe58…`, `e3fd1760…`
  (pictures 0-4).

### The visible edge (`edge.py`, from the untouched `WARNING1` state)

The screenshot before the writes equals `EXP-0051`'s (`3d044f4e…`). After:
file rows 220-223 show yellow on screen rows 228-231 (352 pixels each);
rows 224-227 show nothing; file columns 348-351 of rows 50-53 show cyan on
screen rows 58-61. So the display's 224 lines show file rows 0-223, and
Mednafen's 240-row screenshot pads 8 black rows above and below.

## Conclusion

Prediction met, except the bottom band: the visible picture ends at file row
223, not 231. Each warning screen draws its own `WARNINGn.PIX` whole, as an
NBG1 256-colour bitmap at VDP2 VRAM `0x20000`, with the 16-colour palette
from `CYBER.BIN` (not from the file). Room for an English picture:

- 352 × 224 visible pixels (file columns 0-351, rows 0-223); the rest of
  each row and the rows below are loaded but never shown;
- 16 colours fixed by the program: 0 transparent (black), 1-7 a grey ramp
  to white, 8-9 red, 10-12 a yellow ramp, 13-14 a cyan ramp, 15 black (the
  Japanese pictures' background); value 0's table entry (white) is never
  seen;
- the file size fixed (122,880; `WARNING4` 131,072), one byte a pixel,
  no header;
- the Japanese text uses file columns 24-328 and rows 20-210.

## Uncertainty and Alternatives

- Changing the palette would mean changing `CYBER.BIN`'s table, which only
  these screens use as far as seen (the colour RAM at the warnings holds
  nothing else); not needed if the English uses the same 16 colours.
- A real television may crop more than the 224 lines; the Japanese stays
  within rows 20-210.

## Reproduction

Run the procedure (six cold boots: ask the user first). Expect
`decode.json` and `compare.json` as committed and the edge rows above.
