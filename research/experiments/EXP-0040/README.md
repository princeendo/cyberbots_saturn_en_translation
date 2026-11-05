# EXP-0040: The Arcade's English for Jin's Ending

Task: END-004
Status: DONE
Confidence: CONFIRMED (route in both sets, readers and slots, scripts by code, surfaces matched); SUPPORTED (that the arcade credits and cast-roll names are drawn without a text table)

## Observation

`END-001`-`END-003` found:
- what Jin's Saturn ending shows;
- how it draws (scenes 16-19 through `END.BIN`'s copy of the box routine;
  cast roll, credits, QSound notice);
- that the winner's pilot byte selects the ending.

The arcade's English for these surfaces had not been seen. REF-004
(D-010) showed the story boxes read the English table by slot. EXP-0023
read the arcade's ending scripts for Jin statically but never showed them.

## Hypothesis

The arcade selects and plays its ending as the Saturn does:
- an ending number from the winner's pilot;
- one routine per pilot posting fixed scenes;
- the story's box reader showing slot N's record from the region's table.

Forcing the last-fight path at the first round end in headless MAME reaches
Jin's ending with no play.

## Controlled Change

MAME 0.289, headless, each run from a fresh copy of a fixed NVRAM base:
- `cybotsu` `7264edf9…` (`local/win002/mame/nvram_base`, EXP-0032);
- `cybotsj` `31b0e6e6…` (copied from `local/mame_arcade/nvram/cybotsj`).

Inputs are menu presses only: coin, start and two button presses for the
default pilot (Jin) and machine. One debugger breakpoint at the round end
`0xDAE4`, in both sets, makes three writes:

| Address | Value | What it is (from the code) |
| --- | --- | --- |
| `0xFF84AD` (P1 struct `0xFF81A0` + `0x30D`) | 2 | P1's round wins |
| `0xFF88AD` (P2 struct `0xFF85A0` + `0x30D`) | 0 | P2's round wins |
| `0xFFEA28` (`($6A28,A5)`, A5 = `0xFF8000`) | 1 | The flag that sends the round end to the ending path (`0xDAF4`) |

Logged:
- writes to the dialogue slot `0xFF2F7A` (D-010) and to the ending number
  `0xFFEB2C`;
- reads of the three dialogue tables (624 pointers each, and their records
  up to the next table);
- snapshots every 30 frames from 9200 to 13200, then every 60 to 26000.

## Prediction

At the first round end the game copies Jin's pilot byte (0) to the ending
number and plays list 0's ending: scenes 16-19, the slots of EXP-0023's
script reading, in English in `cybotsu` and Japanese in `cybotsj`. Then the
cast roll and credits. Two runs from the same NVRAM copy are identical.

## Inputs and Provenance

- `local/arcade/`: `cybotsu.zip`, `cybotsj.zip`, `qsound.zip` (REF-002).
- Program images `local/ref003/cybotsu-maincpu.bin` (`18e8827d…`, data
  reads) and `cybotsj-maincpu.bin` (`2d1e6b25…`).
- MAME debugger disassemblies of `0x0`-`0xC0000` (decrypted opcodes):
  `local/win002/mame/cybotsu-0-c0000.asm` (`3aa6ad8e…`, EXP-0032) and
  `local/end004/mame/dasm-j/cybotsj-0-c0000.asm` (`da4c3c8c…`, made here
  with `debug dasm`).
- `data/text/ending_posts.json` (EXP-0039).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`timelines/route-u.txt`](timelines/route-u.txt) (`35675085…`), [`timelines/route-j.txt`](timelines/route-j.txt) (`0c00edb5…`) | The route, taps and snapshots |
| [`timelines/probe-u.txt`](timelines/probe-u.txt) (`f603e253…`) | The first probe (slot and ending-number writes, snapshots every 120 frames) |
| `tools/reference/mame_timeline.lua` | Timeline player (`logwrites`, `logreads`, `debug`, `snap`) |
| [`compare_scripts.py`](compare_scripts.py) (`7d8bb35e…`) | Arcade dispatchers, ending posts and scene scripts for lists 0-5 in both sets, against the Saturn's; writes `data/arcade/ending_scripts.json` (`20285407…`) |

## Procedure

```bash
B=local/end004/mame/nvram_base   # cybotsu/eeprom, cybotsj/eeprom (hashes above)
run() { s=$1; n=$2; O=local/end004/mame/$n; mkdir -p $O/snap $O/nvram
  cp -R $B/cybots$s $O/nvram/
  sed "s#local/end004/mame/route-$s/#$O/#g" research/experiments/EXP-0040/timelines/route-$s.txt > $O/timeline.txt
  MAME_TIMELINE=$O/timeline.txt mame cybots$s -rompath local/arcade \
    -autoboot_script tools/reference/mame_timeline.lua -snapshot_directory $O/snap \
    -cfg_directory local/mame_arcade/cfg -nvram_directory $O/nvram -skip_gameinfo \
    -nothrottle -video none -sound none -seconds_to_run 600 -debug -debugger none; }
run u route-u; run u route-u2; run j route-j; run j route-j2
./invenv.sh python research/experiments/EXP-0040/compare_scripts.py \
  local/ref003/cybotsu-maincpu.bin local/win002/mame/cybotsu-0-c0000.asm \
  local/ref003/cybotsj-maincpu.bin local/end004/mame/dasm-j/cybotsj-0-c0000.asm \
  --out data/arcade/ending_scripts.json
```

The `cybotsj` disassembly: a timeline `1 debug dasm OUT,0,c0000` / `2 exit`
run with `-debug -debugger none -seconds_to_run 5`. 2026-11-05; a route
takes about 30 seconds. No focus is taken (`-video none`).

Corrected on the way:
- **Odd end addresses.** MAME refuses a read tap whose end address is even,
  and the error cancelled every later tap installed on that frame. All
  ranges now end on odd addresses.
- **Japanese table size.** The first `cybotsj` taps covered 494 Japanese
  pointers (D-009's count). The table has 624, like the others (below).

## Actual Result

### Code (both sets)

| | `cybotsu` | `cybotsj` |
| --- | --- | --- |
| Round end, ending path | `0xDAF4` tests `($6A28,A5)`; `0xDBB6` copies the winner's `($370,A6)` (pilot) to `($6B2C,A5)`, then mode `0x14` | same addresses and code (one call target differs) |
| `($6A28,A5)` set | `0xDA90`, when `($6A2B,A5)` is set and the winner has 2 rounds (or round 4) and is not the CPU: the Saturn's `0x060CFF04`/`0x060CFF07` pair | same |
| Ending dispatch | `0xE47C`: `@(0xE496 + 4 × ending number)`, 6 routines `0x4B88C`, `0x4BCBE`, `0x4C1B2`, `0x4C586`, `0x4CB9A`, `0x4D0B2` | `0xE466`, table `0xE480` |
| Posts | `move.l #$1400000k,D1`, `moveq #s,D2`, `jmp 0x163E` | same |
| Scene scripts | `0x12150` | `0x12138` |

The dispatch table is read PC-relative, so through the decrypted opcode
space; its words are taken from the disassembly, not from the plain image.

### Route (`route-u`, `route-j`, each twice)

| | `cybotsu` | `cybotsj` |
| --- | --- | --- |
| Opening scene slots (scene 21) | 0-5 from 2733 | same |
| Ending number written (`0xDBB6`) | 0 at 9259 | 0 at 9436 |
| Ending slots opened, in order | 408, 409, 493, 410, 411, 412, 413, 414, 415, 614, 416, 417, 418, 610, 419, 420, 614, 421, 610, 422 (9273-12702) | the same slots (9450-12618) |
| Repeat run | slot, ending-number and read logs byte-identical; all 347 snapshots identical (set hash `43871d7c…`) | identical (`9f007b5e…`) |

### Readers during the ending

| Set | Table read | Pointer readers (slot N at table + 4N) | Record readers |
| --- | --- | --- | --- |
| `cybotsu` | English `0x0B33AA` only | `0x011F6A` (each box opened: 20 slots above), `0x012014` (13 of them again) | `0x011F70`-`0x011FAE` (header), `0x011FBC` (characters), `0x01201A`/`0x012036` |
| `cybotsj` | Japanese `0x0A30F6` only | `0x011E7A`, `0x011F0E` (same slots) | `0x011E80`-`0x011EBE`, `0x011ECA`, `0x011F14`/`0x011F30` |

- No read of the Spanish table, and none by `0x97222`, in either set.
- The last table read is at 12744 (`cybotsu`) and 12810 (`cybotsj`), the
  end of scene 19. The cast roll, credits and thank-you screen read no
  dialogue table.
- In `cybotsj`, `0x0116DA` (the Japanese table hard-coded) read slot 496
  once at 3933, before the ending.
- **Correction to D-009.** The Japanese table has 624 pointers, like the
  Spanish and English ones. Slots 494-623 (speaker names among them) sit
  at `0x0A38AE`-`0x0A3AB5` in `cybotsj` and point past `0x0AA8D4`.

### Scripts: arcade against Saturn (`data/arcade/ending_scripts.json`)

The two arcade sets have the same ending posts and the same opened slots in
every scene of lists 0-5. Against the Saturn's boxes (EXP-0039):

| List | Posts (arcade) | Posts (Saturn) | Differences in the shared scenes |
| --- | --- | --- | --- |
| 0 Jin | 16, 17, 18, 19 | same | 16, 17: Saturn adds box 1072 first. 19: speaker names Saturn 605, 601 = arcade 614, 610 |
| 1 Santana | 16-22 | same | 16: + 1072. Names: Saturn 603, 604, 611 = arcade 612, 613, 620 |
| 2 Mary | 16, 17, 18 | 16 | 16: + 1072. **Scenes 17-18 (slots 440-447 and names) are not posted on the Saturn** |
| 3 Arieta | 16-21, 27, 28 | same | 16: + 1072. Names: Saturn 604-607, 610 = arcade 613-616, 619 |
| 4 Gawaine | 16-19 | same | Names: Saturn 601, 605 = arcade 610, 614 |
| 5 Bao and Mao | 16, 17, 28, 18, 19, 20, 21, 22 | the same without 20 | 16: + 1072. **Scene 20 (slot 486) is not posted on the Saturn.** Names: Saturn 606, 607, 612-614 = arcade 615, 616, 621-623; Saturn 608 = arcade 615 |

Every other box equals its slot number. Speaker-name box N on the Saturn is
arcade slot N + 9, except Saturn 608, which is arcade 615.

### Surfaces (agent-reviewed snapshots, `route-u` unless noted)

| Saturn surface (`END-001`) | Arcade (`cybotsu`) | Sample (SHA-256) |
| --- | --- | --- |
| Dialogue boxes, scenes 16-17 | English boxes with the same portraits and layout, slots 408-413, 493; no blank first box | `f09740` (`855c35e1…`), `f10910` (`3cc5ec93…`) |
| Narration, scene 18 | English, typed on black, slots 414-415 | `f11210` (`2161fa40…`) |
| Captions with speaker names, scene 19 | English, under the same picture, each line led by an English name (`Gawaine:`, `Jin:`; slots 614, 610) | `f12200` (`13c7e79d…`) |
| Cast roll: katakana names over Latin names | **Latin names only**, no line above them; `cybotsj` shows katakana over Latin, as the Saturn | `f14340` (`22ed1f75…`); `cybotsj` `f14340` (`fde88156…`) |
| Staff credits (`ARCADE STAFF`, `CONSUMER STAFF`) | `STAFF` and the arcade staff only | `f16500` (`a2080915…`) |
| `THANK YOU FOR PLAYING!`, `PRODUCED BY` | The same English | `f19020` (`91b1d9aa…`) |
| QSound notice with a Japanese trademark line | **None in the ending.** The arcade shows a different QSound screen in its attract loop, all English, no trademark line | `f23700` (`f48c403a…`) |
| Game over, ranking | `GAME OVER`, then attract | `f19740` (`9e70eae9…`) |

`cybotsj`'s captions show Japanese speaker names (`f12200`, `680edde6…`),
read from its Japanese table at slots 614 and 610.

## Conclusion

**CONFIRMED.**
- **Route.** In both `cybotsu` and `cybotsj`, three writes at the first
  round end reach Jin's ending: two round wins for player 1, none for
  player 2, and the ending flag. The ending is the one selected by the
  winner's pilot byte, through code that mirrors the Saturn's. Two runs
  from a fixed NVRAM copy are identical.
- **Readers.** The ending's dialogue, narration and captions are read
  slot by slot, by the story box readers (`0x011F6A`/`0x012014` in
  `cybotsu`), from the English table, or from the Japanese table in
  `cybotsj`. The slots are those the scripts predict.
- **Scripts.** Jin's ending scripts equal the Saturn's box for slot, except
  the Saturn's added box 1072 and its renumbered speaker names (+9).
  - Mary's scenes 17-18 and Bao and Mao's scene 20 exist in the arcade
    (both sets) but are never posted on the Saturn.
- **Counterparts.**
  - The US arcade has English for every Saturn dialogue box of Jin's
    ending and for the speaker names.
  - It has no counterpart for the cast roll's katakana line (it shows the
    Latin names only).
  - It has no counterpart for the QSound trademark line (no QSound notice
    in the ending).

**SUPPORTED:** the arcade's credits and cast-roll names are drawn without a
text table. No dialogue table is read after scene 19, and the strings are
not in the program in ASCII or in the dialogue encoding.

## Uncertainty and Alternatives

- The route skips stages 0-7, as the Saturn route does; the ending code
  reads only the ending number, but anything earlier stages set is not
  reproduced.
- Only Jin's ending was played. The other lists' arcade scripts are read
  statically (and match between sets).
- Box 1072 (a blank first box on the Saturn) has no arcade slot; what it
  shows is the empty box seen in END-001.

## Reproduction

Run the procedure. Expect the ending number 0 at 9259 (`cybotsu`) and 9436
(`cybotsj`), the slot sequence above, byte-identical logs and snapshots in
the repeat runs, and `compare_scripts.py` to reproduce
`data/arcade/ending_scripts.json`.
