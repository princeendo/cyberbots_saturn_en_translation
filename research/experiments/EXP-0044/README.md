# EXP-0044: The Cast Roll's Japanese Names, Hidden by Their Size Words

Task: END-010
Status: DONE
Confidence: CONFIRMED (the drawing path, the 16 records, and the hiding from a saved state); the on-disc change is checked in the END-010 build's live run (`EXP-0045`)

## Observation

- Each cast-roll name is a VDP1 sprite: Japanese names use colour word
  `0x40E0` and are 11 pixels high; Latin names use `0x41E0` (D-035).
- The cast roll is the same in every ending (Santana's control run,
  `local/end003/santana`, shows the same entries and names). The user chose
  "Hide in every ending (Recommended)" (2026-11-05), on top of "Hide, as US
  arcade (Recommended)" (`END-005`).

## Hypothesis

The sprites come from the main program's sprite-part routine. Each Japanese
name is a part whose pattern record, on disc, starts with a size word. A
part of width or height 0 is skipped, so zeroing the records' size words
removes the Japanese names and nothing else.

## Controlled Change

From the pre-roll state, the size words of the 16 Japanese-name records in
the RAM copy of `KEND_1.BIN` (WRAM-L `0x00280000` + offset) are set to 0.
Nothing else changes.

## Prediction

Through the roll, each shot differs from the control only where a Japanese
name was. The Latin names, portraits and background are unchanged.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `local/end002/control/s07284.mcs` | `EXP-0038`, mid-roll |
| `local/end010/cast-pre/s06450.mcs` | made here: `EXP-0042/probe.py` from the END-001 checkpoint, saved at frame 6452 (after `KEND_1.BIN` loads at 6352, before the roll); SHA-256 `dca32215…d207` |
| `KEND.BIN`, `KEND_0.BIN`, `KEND_1.BIN` | untouched; equal to their RAM copies at `s07284` |

## Tools and Environment

[`trace.py`](trace.py) (every register at PC breakpoints) and
`EXP-0038/vram_probe.py` (fills, write breakpoints, shots). Agent Mednafen
1.32.1, silent home, no key, no cold boot.

## Procedure

```bash
V=research/experiments/EXP-0038/vram_probe.py; T=research/experiments/EXP-0044/trace.py
C=local/end002/control/s07284.mcs
# 1. Who writes a Japanese-name command (VDP1 0xA0, colour 0x40E0)?
$V $C local/end010/cast-cmd3 --shots 3 \
  --write-bp 060E10A0-060E10BF,260E10A0-260E10BF,060E00A0-060E00BF,260E00A0-260E00BF
# 2. Bank, parts, pattern records and colours of one frame
$T $C local/end010/cast-trace2 --pc 060113F0,0601152A,06011654,0601166A \
  --dump workramh:60000:D000 --dump workraml:0:80000
# 3. Which frames the whole roll draws
./invenv.sh python research/experiments/EXP-0042/probe.py local/end010/cast-pre \
  --frames 6500 --cells-until 0 --save-at 6450
$T local/end010/cast-pre/s06450.mcs local/end010/cast-roll --pc 060113F0 --frames 2700
# 4. Control and test: the 16 size words set to 0 in RAM
S=local/end010/cast-pre/s06450.mcs; SH=100,450,600,750,900,1050,1200,1350,1500,1650,1800,1950,2100,2300,2500
$V $S local/end010/cast-ctl --shots $SH
$V $S local/end010/cast-hide --shots $SH \
  --fill workraml:BEC58:2:00 --fill workraml:BF268:2:00 --fill workraml:BF3A8:2:00 \
  --fill workraml:BF63C:2:00 --fill workraml:BF760:2:00 --fill workraml:BF9C8:2:00 \
  --fill workraml:BFB1C:2:00 --fill workraml:BFD9C:2:00 --fill workraml:BFF74:2:00 \
  --fill workraml:C012C:2:00 --fill workraml:C0250:2:00 --fill workraml:C0538:2:00 \
  --fill workraml:C06C4:2:00 --fill workraml:C0818:2:00 --fill workraml:C0C04:2:00 \
  --fill workraml:C0D30:2:00
```

(All through `./invenv.sh python`, with `MEDNAFEN_ALLOWMULTI=1`.)
2026-11-05, 14:58-15:20 local.

## Actual Result

1. **The command source.** No CPU writes go to VDP1 VRAM. The command at
   `0xA0` is copied from WRAM-H `0x060E10A0`, which the main program's
   sprite-part routine writes: entry `0x060113F0`, command store
   `0x0601165E`-`0x06011682`.
2. **The routine.** R11 is the sprite bank; its header is at `@(0x06047D50 +
   4 × bank)`. For bank 16 that is `0x0606A704`, which is `KEND.BIN` +
   `0xA704`. In the header:
   - +4 is a table of 16-bit part indexes, one per frame (frame − 1);
   - +8 is the parts, 6 bytes each, at `0x20200000` (`KEND_0.BIN`).

   A part's second word holds bit 1 ("last part") and bit `0x20`, which
   picks the record table: `@(0x060CE718 + 4 × (bank + 0x20))` =
   `0x20280000`, `KEND_1.BIN`. The record is at 4 × (bit 0 << 16 | third
   word), and its first word is the size: width = (word & `0x0F00`) >> 5,
   height = word & `0x7F`. A size of width 0 or height 0 branches past the
   command (`0x0601157C`, `0x06011584`), and the pattern decoder
   `0x060107EA` is not called.
3. **The roll.** It draws frames `0x1B6`-`0x1C9` of bank 16; frames
   `0x1B2`-`0x1B5` are never drawn. Even frames are the Japanese names
   (colour `0x40E0`), odd frames the Latin names (`0x41E0`). The ten even
   frames use 16 records in `KEND_1.BIN`, all 10 or 11 pixels high:
   `0x3EC58`, `0x3F268`, `0x3F3A8`, `0x3F63C`, `0x3F760`, `0x3F9C8`,
   `0x3FB1C`, `0x3FD9C`, `0x3FF74`, `0x4012C`, `0x40250`, `0x40538`,
   `0x406C4`, `0x40818`, `0x40C04`, `0x40D30`. The same list comes
   statically from `KEND.BIN`, `KEND_0.BIN` and `KEND_1.BIN`
   (`tools.text.ending.cast_name_records`).
4. **Control and test**, shots after N frames from `s06450`:

   | Shot | Pixels differing | Box |
   | --- | --- | --- |
   | 100, 1800, 2300, 2500 | 0 | — |
   | 450 | 350 | x 136-290, y 138-148 |
   | 600-1650 (8 shots) | 428-764 | inside x 116-322 |
   | 1950, 2100 | 285, 304 | x 200-305 (Jin's closing shot) |

   Agent-reviewed (`cast_all.png`, scratch): in the test, every Japanese
   name is gone, from Santana to G.O.D. and Jin's closing shot. Each
   portrait and yellow Latin name is unchanged, and nothing else differs.

## Conclusion

Prediction met. The cast roll's Japanese names are the 16 pattern records
in `KEND_1.BIN` that the even frames `0x1B6`-`0x1C8` use. Setting each
record's size word to 0 makes the game skip those parts, so only the Latin
names remain, as in the US arcade. `tools.text.ending.hide_cast_names`
makes this change on disc. Every ending's cast roll shows it, as the user
chose.

## Uncertainty and Alternatives

- The Latin names keep their places, so a blank line stands where each
  Japanese name was. The US arcade's layout is not copied.
- Record `0x3EC58` is also used by the undrawn frame `0x1B2`.

## Reproduction

Run the procedure. Expect the trace and shot results above.
