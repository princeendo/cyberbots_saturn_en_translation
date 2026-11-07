# EXP-0075: Forcing the Rare Paths: the Arcade's Location-Test Screen (TXT-011)

Task: TXT-011
Status: DONE
Confidence: CONFIRMED (the flag bytes, the screen, its slots and readers in
both arcade sets, forced and repeated; slot reuse in the tables; list 7's
scenes by script reading and by forcing); SUPPORTED (that no Saturn code
posts list 10: no constant does, computed posts were not traced)

## Observation

`TXT-010` (`EXP-0074`, D-063) left one lead: the US arcade's slot 609 holds a
"coming soon" style message, and list 7 is posted at `0x631AC` with its
scene from a byte table indexed by an object's `+0xC`. On the Saturn, 12
boxes have no path (D-063).

## Hypothesis

A rarely met condition creates the list 7 object; forcing it shows slot
609 in the US set, and the Japanese set's scene for the same index.

## Controlled Change

MAME 0.289, headless, each run from a fresh copy of `EXP-0040`'s NVRAM base
(`cybotsu` `7264edf9…`, `cybotsj` `31b0e6e6…`), with `EXP-0040`'s route to
Jin's ending (coin, start, two presses; one round-end breakpoint: P1 two
wins, P2 none, the ending flag). One change per run on top:

| Run | Change |
| --- | --- |
| `flag-u`, `flag-j` | ROM data byte `0x55B` = 1 (0 in both retail sets) |
| `flag561-u` | ROM data byte `0x561` = 1 instead |
| `flag-j1`-`flag-j7` | as `flag-j`; at `0xEC72` the ending number `0xFFEB2C` set to 1-7 |
| `flag-u0` | as `flag-u`; at `0xEC78` (the region test) the PC moved to `0xEC8A` |
| `title-{u,j}-{none,55B,561}` | the first 3,000 frames with no byte, `0x55B` or `0x561` set |

The byte is written into the `:maincpu` ROM region before the first frame
by [`rom_flag.lua`](rom_flag.lua), which then runs the unchanged
`tools/reference/mame_timeline.lua`; each run's log shows the program
space reading the new byte (`ROM_POKE 0x00055B: program 00 -> 01`).

## Prediction

`flag-u` opens slot 609 and shows the "coming soon" message; `flag-j` opens
list 7's scene for Jin's ending number (0), and `flag-j6` slot 609.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `local/arcade` | `cybotsu.zip`, `cybotsj.zip`, `qsound.zip` (REF-002) |
| `local/ref003/cybots{u,j}-maincpu.bin` | Data images (`18e8827d…`, `2d1e6b25…`) |
| Listings | `local/win002/mame/cybotsu-0-c0000.asm`, `local/end004/mame/dasm-j/cybotsj-0-c0000.asm` |
| `data/text/arcade_jp_map.json` | Arcade Japanese code map (`REF-006`) |
| `local/extracted/saturn_jp` | Untouched Saturn files |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| [`rom_flag.lua`](rom_flag.lua) | `dcd225db…` | One ROM byte, then the timeline player |
| [`timelines/`](timelines/) | `route-flag-u.txt` `518916e2…`, `route-flag-j.txt` `f784be19…`, `route-flag-j6.txt` `f98c14d0…`, `route-flag-u0.txt` `e6522686…`, `route-flag561-u.txt` `04daa005…`, `title.txt` `01f879e4…` | Routes, taps, snapshots |
| [`thanks.py`](thanks.py) → [`thanks.json`](thanks.json) (`8a348c7d…`) | | List 7's scenes, every scene's slots, table records 600-623, Saturn line search |

## Procedure

```bash
B=local/end004/mame/nvram_base; T=research/experiments/EXP-0075/timelines
run() { s=$1; n=$2; poke=$3; tl=$4; O=local/txt011/mame/$n
  rm -rf $O; mkdir -p $O/snap $O/nvram; cp -R $B/cybots$s $O/nvram/
  MAME_TIMELINE=$tl ROM_POKE=$poke mame cybots$s -rompath local/arcade \
    -autoboot_script research/experiments/EXP-0075/rom_flag.lua -snapshot_directory $O/snap \
    -cfg_directory local/mame_arcade/cfg -nvram_directory $O/nvram -skip_gameinfo \
    -nothrottle -video none -sound none -seconds_to_run 600 -debug -debugger none > $O/mame.log 2>&1; }
run u flag-u 55B=01 $T/route-flag-u.txt;  run j flag-j 55B=01 $T/route-flag-j.txt
for i in 1 2 3 4 5 6 7; do run j flag-j$i 55B=01 $T/route-flag-j$i.txt; done
run u flag-u0 55B=01 $T/route-flag-u0.txt; run u flag561-u 561=01 $T/route-flag561-u.txt
for s in u j; do run $s title-$s-none "" $T/title.txt; run $s title-$s-55B 55B=01 $T/title.txt
  run $s title-$s-561 561=01 $T/title.txt; done      # title runs: -seconds_to_run 120, no -debug
./invenv.sh python research/experiments/EXP-0075/thanks.py
```

The repeat (`flag-u2`) is `route-flag-u.txt` with its output paths
changed. 2026-11-07, local; about 30 seconds a run. No cold boot, no keys,
no focus taken.

## Actual Result

### The flags (code, both sets)

At boot `0x472` copies ROM bytes `0x55A`-`0x55E` to `($A0,A5)`-: byte
`0x55A` is the region byte `0xFF80A0` (2 in `cybotsu`, 0 in `cybotsj`). The
code reads `0x55B` and `0x561` directly (`movea.l #$55A,A0`):

| Where | `0x55B` (`+1`) | `0x561` (`+7`) |
| --- | --- | --- |
| `0xAA12` boot banner | adds a message (`0x04000028`) | adds a message (`0x04000074`) |
| `0x2094` | — | sets the ending flag `($6A2B,A5)` early (a short game, not run) |
| `0xE464`, `0xE4C0` | skip the ending | the same |
| `0xEA42` | run `0xEB5A`: the list 7 screen | the same |

`0xEB5A` creates the screen's objects, among them type `0x93` (`0xEC72` in
`cybotsu`, `0xEC5A` in `cybotsj`; its routine `0x6317E` is entry `0x93` of
the object table `0x4E04A`). Its scene index `+0xC` is 6 when the region
byte is non-zero, else the ending number `($6B2C,A5)` (the winner's pilot,
D-037). The object posts `0x14000007` with the scene from the byte table
`0x631BC` (`00 02 01 03 04 05 06`).

### Seen (agent-reviewed snapshots)

| Run | Slots opened (after the ending number) | Reader | Screen |
| --- | --- | --- | --- |
| `flag-u` | 609 at 9300 | `0x011F6A`, English table only | `THANK YOU FOR PLAYING!`, Jin and Blodia, one English box (`f09500`, `44907bf9…`) |
| `flag561-u` | 609 at 9300 | same | identical frames (`f09500` `44907bf9…`) |
| `flag-u0` | 602, 603, 604, 605 | same | four boxes, each the same English as 609 (`f09530`, `61e2aabe…`) |
| `flag-j` (index 0) | 602, 603, 604, 605 | `0x011E7A`/`0x011F0E`, Japanese only | the same picture, a Japanese thank-you message in four boxes (`f09650`, `ccbfde05…`) |
| `flag-j1`-`j5`, `j7` | 602-605 | same | every snapshot identical to `flag-j` (set `882f810b…`) |
| `flag-j6` | 609 at 9477 | same | one short Japanese thank-you line (`f09650`, `7eeda23a…`) |
| `title-u-55B`, `title-j-55B` | — | — | boot banner plus `LOCA TEST VERSION` (`4eb42b9b…`, `af16c3ed…`) |
| `title-u-561`, `title-j-561` | — | — | boot banner plus `SHOW VERSION` (`65ad2ea2…`, `46200b6d…`) |

- The title runs differ from the unflagged runs (`998d52b4…`,
  `6beae25d…`) at frames 90-240 only, the banner; the banner is ASCII in
  both sets.
- `flag-u` and its repeat `flag-u2`: every snapshot and log byte-identical.
- The US English for the slots was read by the agent from the snapshots
  (not committed): one three-line "coming soon" message.

### Records and scenes (`thanks.json`)

- **List 7 has seven scenes:** 0-5 each open 602-605, 6 opens 609, in both
  sets.
- **Shared records:** in both sets the English and Spanish tables point
  slots 601-609 at one record (`cybotsu` English `0x0BB876`). The Japanese
  table has records of its own for 601 (= 602), 603-609.
- **Never opened:** reading all 206 scenes of lists 0-7, slots 601, 606,
  607, 608, 617 and 618 are opened by no scene in either set.
- **Saturn:** none of the nine Japanese lines of 602-605 and 609 is a Saturn
  line (best `difflib` ratio 0.68 for 602-605; 0.84 for 609, against an
  ordinary story line with a similar phrase). Three use codes the learned
  map never met (`unmapped_codes`).

### The Saturn

- No Saturn file holds `0x1400000A` (a list 10 post): code files post lists
  0, 2, 5, 6 and 9 by constant.
- **List 10 is list 7's copy.** It opens boxes 602-605 and 609 (`EXP-0033`),
  the same numbers. The Saturn has no thank-you lines; its boxes
  601-614 are the arcade's speaker names 610-623 (D-037), nine numbers
  down. So list 10 points at speaker names.
- Box 609 is the arcade's slot 618, which no arcade scene opens: it is dead
  on both machines.

### Every rare path

| Text | Machine | Path | Shown |
| --- | --- | --- | --- |
| Thank-you screen, slots 602-605 and 609 | arcade | ROM flag `0x55B` or `0x561` (no retail set has them) | Forced here; Japanese in `cybotsj`, the one English message in `cybotsu` |
| `LOCA TEST VERSION`, `SHOW VERSION` | arcade | the same flags | forced here; ASCII |
| Slots 601, 606-608, 617, 618 | arcade | none (no scene) | dead |
| Boxes 63, 283, 290, 335, 494, 495, 552, 553, 938, 1073 | Saturn | none (D-063) | dead |
| Box 555 | Saturn | list 9 scene 1, in no table entry (D-030, D-063) | dead |
| Box 609 | Saturn | list 10, no post | dead |

No path above shows Japanese on the Saturn: every Saturn rare box is dead,
so there is nothing to force there.

## Conclusion

Prediction met, with a correction to `TXT-010`. The arcade's one rare
path is a build mode: ROM flags (location test, show version) that skip the
ending for a thank-you screen. In it the US set shows its single English
message, and the Japanese set shows a per-ending thank-you message. The
Saturn did not carry that screen: its thank-you lines are gone, its list
10 is a leftover copy pointing at speaker names, and nothing posts it.

**Corrections to D-063 and `EXP-0074`:** list 7 is the location-test
thank-you screen, not speaker names (those are slots 610-623), and the
region test that picks its scene is in the object's creator (`0xEC78`),
not in the posting code.

## Uncertainty and Alternatives

- Only Jin's route was run; the screen's picture for other pilots and the
  `0x561` short game were not run (code reading only).
- "No Saturn post of list 10" rests on the constant search; a computed
  post (`0x14000000` plus a register) was not traced. The 1,074-box census
  (D-063) found no other path.
- The Japanese thank-you lines were compared through a learned code map
  with some unmapped codes, so an exact Saturn copy with those characters
  cannot be excluded by the ratio alone; the map has no character for those
  codes because no paired Saturn line uses them.
