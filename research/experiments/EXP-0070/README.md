# EXP-0070: The Ruined-City Signs: Layer, Storage and the Arcade's Version (UI-002)

Task: UI-002
Status: DONE
Confidence: CONFIRMED (the Saturn layer, VRAM address, file and offset, by
a one-block VRAM change and a one-byte test image; the arcade's region
branches, by forcing them both ways in both sets); SUPPORTED (the sign
rectangles, read from renders by the agent)

## Observation

`UI-001` (`EXP-0067`) found one Japanese attract item: painted signs in the
ruined-city stage of the first attract demo (BLODIA vs REPTOS). `cybotsj`
shows them; `cybotsu` shows the same building with the signs blank. The
demo loads `ST00_FNT.BIN` (VDP2 `0x19000`) and `ST00_SPR.BIN` (VDP1
`0x20000`) (`EXP-0067` load log, frames 4792 and 4865).

## Hypothesis

The signs are tiles of one VDP2 layer, raw in `ST00_FNT.BIN`; the US arcade
draws the same building with other tiles or colours, chosen by its region
byte, and has no English for them.

## Controlled Change

- Saturn (untouched image, saved states, no keys): zeroed VDP2 VRAM ranges,
  then one 128-byte block; a test image from the untouched source with one
  byte of `ST00_FNT.BIN` changed.
- Arcade (MAME 0.289, headless, no input): tile RAM dumps, write logs, a
  read tap on the map table, and the two region branches forced each way.

## Prediction

Only the sign's pixels change for the block and the byte; forcing the US
arcade's branches to the Japanese path shows Japanese signs, and the
reverse blanks them in `cybotsj`.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Attract state | `local/ref005/session/states/f00025772.mcs` (before the first demo) |
| Checkpoints | `local/ui002/s1/city.mcs` (about 110 frames before the signs show, `SHA-256` in the probe records) and `local/ui002/s2/signs.mcs` (signs on screen; its VDP2 registers, VRAM and CRAM are the render's input) |
| Untouched image, `ST00_FNT.BIN` | `local/disc_images/cyberbots_saturn_jp_2m/`, `local/extracted/saturn_jp/` (SHA-256 in `signs.json`) |
| Test image | `build/ui002/sign` (`tools.disc.patch_image`, `ST00_FNT.BIN` byte `0x1F20D` `0x7A` → `0x00`) |
| Arcade | `cybotsu`, `cybotsj`; listings `local/win002/mame/cybotsu-0-c0000.asm`, `local/ui003/mame/cybotsj-0-c0000.asm`; fresh NVRAM copies of `local/mame_arcade/nvram/<set>` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`probe.py`](probe.py) → `probe-*.json` | Saturn: load a state, one fill per variant, N frames, screenshot, dumps, pixel box against the control |
| [`nbg2.py`](nbg2.py) → [`signs.json`](signs.json) | Offline render of one VDP2 tile layer from a state's registers, VRAM and CRAM, with a block grid and each block's tile address |
| [`map_tap.lua`](map_tap.lua) | MAME: logs each block the scroll-map copier reads, with its list pointer |
| [`timelines/`](timelines/) | MAME runs: `tiles-*`, `writes-*`, `maps-*`, `list-*`, and the forced `jpmap`, `jpboth`, `usmap`, `usboth` |

Mednafen 1.32.1 with the agent patch; MAME 0.289; Python 3.13.

## Procedure

```bash
E=research/experiments/EXP-0070
# checkpoints: 25772 + 5400 frames → city.mcs (saved while running); city.mcs + 118 → signs.mcs
./invenv.sh python $E/probe.py local/ui002/b1 --fill vdp2vram:19000:9C80:00 ...   # eighths of ST00_FNT's range
./invenv.sh python $E/nbg2.py local/ui002/s2/signs.mcs nbg2.png nbg2.json          # screen
./invenv.sh python $E/nbg2.py local/ui002/s2/signs.mcs plane2.png plane2.json --plane
./invenv.sh python $E/probe.py local/ui002/one --state local/ui002/s2/signs.mcs --frames 2 \
  --fill vdp2vram:38280:80:00 --fill workramh:FFFFF:1:00
./invenv.sh python -m tools.disc.patch_image --source-dir local/disc_images/cyberbots_saturn_jp_2m \
  --manifest references/saturn_jp/README.md --track "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin" \
  --file "ST00_FNT.BIN;1" --data local/ui002/test/ST00_FNT.BIN --out-dir build/ui002/sign
./invenv.sh python $E/probe.py local/ui002/disc-control --state local/ref005/session/states/f00025772.mcs \
  --frames 5530 --dump vdp2vram:19000:4E400                        # untouched image
./invenv.sh python $E/probe.py local/ui002/disc-test ... --cue "build/ui002/sign/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
# arcade, per set, fresh NVRAM copy each run (add -debug -debugger none for the forced runs):
MAME_TIMELINE=$E/timelines/tiles-SET.txt mame SET -rompath local/arcade \
  -autoboot_script tools/reference/mame_timeline.lua -cfg_directory local/mame_arcade/cfg \
  -nvram_directory NV -snapshot_directory SNAP -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 900
MAP_TAP_OUT=... MAP_TAP_PC=018E26 (cybotsu) / 018E0E (cybotsj) MAME_TIMELINE=$E/timelines/maps-SET.txt \
  mame SET ... -autoboot_script $E/map_tap.lua
```

2026-11-06, 20:15-21:45 local. No cold boot, no keys.

## Actual Result

### The Saturn

- **Determinism first.** Loading a state with `run`, `loadstate`, `pause`
  as three agent exchanges lets a few frames pass in between, so variants
  of one state differed by tens of thousands of pixels (a one-byte fill of
  an unused byte: 42,507). `probe.py` sends `loadstate` and `pause` in one
  exchange; two unused-byte fills then match the control exactly.
- **VRAM:** at the sign, `ST00_FNT.BIN` equals VDP2 VRAM `0x19000`-
  `0x673FF` byte for byte, and `ST00_SPR.BIN` VDP1 VRAM `0x20000`-
  `0x37FFF`. Zeroing eighths of the first range: `0x36580`-`0x40200`
  removed a whole layer of buildings, signs included.
- **Layer:** the VDP2 registers of `signs.mcs` (NBG0 1×1 cells, map
  `0x7C000`, the HUD; NBG1 1×1, `0x70000`; NBG2 and NBG3 2×2 cells, maps
  `0x7A000` and `0x78000`; 16 colours; 2-word pattern names; planes 2×1)
  render NBG2 (offline, `nbg2.py`) exactly as the screen's buildings, signs
  included. NBG2 stores its 16 × 16 blocks column by column with no reuse,
  so each sign is a few contiguous 128-byte runs.
- **The signs** (`signs.json`, plane pixels, agent-read): a red vertical
  banner (block column 28, rows 15-20), a white vertical banner with a small
  sign under it (column 30, rows 14-21), and a horizontal sale sign on the
  facade (columns 26-30, rows 25-26): 24 blocks, palettes `0x41` and
  `0x42`. NBG3's far skyline has a few boards about 5 pixels high whose
  marks are not readable; NBG1 (the railing) has none.
- **One-variable RAM change** (`probe-one.json`, from `signs.mcs`, 2
  frames): zeroing the block at VRAM `0x38280` (128 bytes) changed 140
  pixels, x 56-71, y 45-55, all in the white banner where the HUD does not
  cover it; an unused-byte fill changed none.
- **Test image** (`probe-disc-*.json`): from state 25772 with the test
  image, 5,530 frames, the game read the new file (VRAM equals it; the only
  VRAM difference from the control run is `0x1F20D`), and the screen
  differs from the control in exactly 2 pixels (x 68-69, y 27), in the
  white banner.
- **Codec:** none. The file is copied raw to VRAM and the tiles are plain 4
  bpp cells (VRAM matches the file byte for byte).

### The arcade

- **Same frame:** at attract frame 1500 both sets show the city demo
  (`cybotsu_f01500.png` `a9addc0f…e852`, the census's frame). Their tile
  RAM (`0x900000`-`0x93FFFF`) differs in 36 words only: 19 cells of the
  layer at `0x90C000` (US tiles `0x3350`-`0x3362`, Japanese `0x2DD6`-
  `0x2F41`) and 17 palette words (`0x90030C`-`0x90031E`, `0x900828`-
  `0x90083E`, `0x900A32`-`0x900A3E`).
- **Writers:** the cell is written by the map copier (`0x18E26` `cybotsu`,
  `0x18E0E` `cybotsj`), which copies 1 KB blocks from the shared table
  `0x296542` (identical in both programs) by a list at the object's
  `+0x32`. The read tap shows `cybotsu` using list `0x0BC27E` (blocks …,
  1, 14, 3, 4, 5, 15, 7, 8) and `cybotsj` list `0x0BBF0A` (…, 1-8 in
  order). Both programs hold both lists.
- **Region branches** (same code in both sets, `cybotsj` 0x18 lower in the
  first): the map selector `0x1882C` reads the stage (`0xFF6A1A`); for stage
  0, if the region byte `0xFF80A0` is not 0 it uses entry `0x13` instead
  (`cmpi.b #0,($A0,A5)`, `beq`, `moveq #$13,D0` at `0x18832`), whose list
  swaps blocks 2 and 6 for 14 and 15. The city stage's set-up (`0x156B6`)
  also loads three US palette blocks (to `0x900820`, `0x900A20`,
  `0x900300`) when the region byte is not 0. Another stage's set-up
  (`0x17E82`) has the same palette test; which stage is not traced.
- **Forced:** `cybotsu` with both branches taken the Japanese way, and
  `cybotsj` the US way: each one's tile RAM then equals the other set's
  word for word, and the screens show Japanese signs in `cybotsu` and blank
  ones in `cybotsj` (agent-read). The map branch alone leaves the 17 palette
  words, and with the US palette the Japanese tiles' writing is invisible.
- **Oracle:** the US arcade has no English for the signs. It blanks them
  with other tiles and colours. Nothing to transcribe.

### Room

| Sign | Size (plane pixels) | Blocks | File offsets (`ST00_FNT.BIN`) | Colours |
| --- | --- | --- | --- | --- |
| Red vertical banner | about 11 × 85 inside a 16 × 96 column | 6 | `0x0FD00`-`0x0FD7F`; `0x1E200`-`0x1E47F` | 16-colour palette `0x41` (index 0 transparent) |
| White vertical banner and small sign | about 16 × 112 | 8 | `0x0FE80`-`0x0FF7F`; `0x1F100`-`0x1F3FF` | palette `0x41` |
| Horizontal sale sign | about 75 × 17 inside 80 × 32 | 10 | `0x1D780`-`0x1D87F`, `0x1DF00`-`0x1DFFF`, `0x1E680`-`0x1E77F`, `0x1EE00`-`0x1EEFF`, `0x1F580`-`0x1F67F` | palettes `0x41`, `0x42` |

Storage is raw and uncompressed, so a change is a same-size splice of
those blocks into `ST00_FNT.BIN` (`tools.disc.patch_image`); no stream
budget applies. The signs share their blocks with the facade around them,
so a redraw edits only the sign's pixels.

## Conclusion

Predictions met. The city signs are NBG2 tiles of `ST00_FNT.BIN`, copied
raw to VDP2 `0x19000`; a one-byte test image changed exactly two pixels.
Both arcade sets hold both versions of the building; outside Japan the
program picks blank-sign tiles and palettes. There is no official English.

## Uncertainty and Alternatives

- The sign rectangles were read from renders; edges may be off by a pixel.
- The skyline boards (NBG3) are not readable at their size; whether the US
  blanks them is not checked; the arcade's tile RAM differs only in 19
  cells of one layer and 17 palette words.
- Other stages' art was not inventoried; `0x17E82` suggests one more stage
  with a US palette change.
- `ST00_SPR.BIN` (VDP1) was not rendered; the sign removal tests did not
  touch it, and no sign changed with it unchanged.
