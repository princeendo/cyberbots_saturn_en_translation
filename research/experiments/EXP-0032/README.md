# EXP-0032: How Each Game Picks a Versus Win Quote, and the Pairing

Task: WIN-002
Status: DONE
Confidence: CONFIRMED (the quote tables and lists, box for slot, the Saturn's random entry, US records per level); SUPPORTED (the arcade's level and bit, the 7 unmapped boxes, the caption boxes)

## Observation

A versus win shows one dialogue line on a `VICTORY!` screen (`EXP-0031`,
D-029): Saturn line 959 after Jin's win. The arcade's dialogue tables run to
624 slots and the US set has English in slots 494-623. The US slot 558,
the slot WIN-001 matched to line 959, is a Jin line worded differently.
`EXP-0031` described slots 494-623 as "slot k = Saturn line k + 405".

## Hypothesis

Both games choose the quote with the same rule and the same scene scripts,
so the Saturn box shown in a situation is the arcade slot shown in the same
situation, and that slot's US record is the official English for the box.

## Controlled Change

None to either game's files. Two kinds of runs:
- MAME (`cybotsu`, headless): a 2-player match won by player 1, with write
  taps; then the same match with the selector's table offset forced by a
  debugger breakpoint (`0x630B8`, `D0`).
- Mednafen (the untouched image, one cold boot): a versus match won by
  holding the vitality pairs in RAM (D-025), a state saved at the Saturn
  selector, then that state reloaded with the winner's row of the quote
  table rewritten in RAM.

## Prediction

- Each game posts one script message for the quote: the Saturn list 9, the
  arcade list 6, whose scripts show box N and slot N for the same scene.
- Forcing a table entry in either game shows that entry's box or slot.

## Inputs and Provenance

- The untouched image: `VICTORY.BIN` (`2bd396bc…` block in
  `data/text/script_census.json`), `STG0AS.BIN`, extracted under
  `local/extracted/saturn_jp/`.
- `local/ref003/cybotsu-maincpu.bin`, `cybotsj-maincpu.bin` (`REF-003`).
- WRAM-H of REF-005 state `f00012788` (`local/win001/ram/wram_h.bin`,
  `adc316e7…`; extractor validated, D-006): the Saturn main program.
- MAME NVRAM: a copy of `local/mame_arcade/nvram/cybotsu` taken before these
  runs (`eeprom` `7264edf9…`) and copied fresh into each run. Runs that
  shared one NVRAM folder drifted (the quote came at frame 5521, then 5260);
  from a fixed copy two runs gave identical logs.

## Tools and Environment

| Tool | Use |
| --- | --- |
| MAME 0.289 debugger `dasm` (headless) | `cybotsu` program listing `0x0`-`0xC0000` |
| `tools/reference/mame_timeline.lua` | Inputs, snapshots, `logwrites`, `logreads`, `debug` |
| [`create_tap.lua`](create_tap.lua) | Logs tasks made by trap #7 (`0xB0C`) with D1, D2 and the user stack |
| [`post_tap.lua`](post_tap.lua) | Logs messages posted through `0x163E` with the caller's stack |
| [`pair_quotes.py`](pair_quotes.py) | Both selection tables, both scripts, box and slot records → `data/translations/win_quotes_pairing.json` |
| [`saturn_quote.py`](saturn_quote.py) | Saturn: hold the win in RAM, halt at the selector, save a state; reload it with a forced entry |
| `tools/sh2/disasm.py` | `VICTORY.BIN`, `STG0AS.BIN` and WRAM-H code |
| `research/experiments/EXP-0019/drive.py` | Cold boot and the menu keys |

Python 3.13.13; Mednafen 1.32.1 with the agent interface (D-007).

## Procedure

Static (Saturn):

```bash
D="./invenv.sh python tools/sh2/disasm.py --base 0x06060000"
$D --start 0x06060000 --end 0x06061CE8 local/extracted/saturn_jp/VICTORY.BIN   # code
$D --start 0x0606CA90 --end 0x0606CB80 local/extracted/saturn_jp/STG0AS.BIN    # captions
./invenv.sh python tools/sh2/disasm.py --base 0x06000000 \
  --start 0x06026F5E --end 0x06026F74 local/win001/ram/wram_h.bin              # random
```

Arcade (MAME 0.289, headless; each run gets a fresh copy of the NVRAM base):

```bash
printf '1 debug dasm local/win002/mame/cybotsu-0-c0000.asm,0,c0000\n2 exit\n' > dasm.txt
MAME_TIMELINE=dasm.txt mame cybotsu -rompath local/arcade \
  -autoboot_script tools/reference/mame_timeline.lua -debug -debugger none \
  -cfg_directory local/mame_arcade/cfg -nvram_directory NVRAM_COPY \
  -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 5
# the match, with each tap (CREATE_TAP_* / POST_TAP_* set, FROM=4000):
MAME_TIMELINE=research/experiments/EXP-0032/timelines/match.txt mame cybotsu ... \
  -autoboot_script research/experiments/EXP-0032/create_tap.lua
# three forced entries (add -debug -debugger none):
for e in 2 5 7; do MAME_TIMELINE=research/experiments/EXP-0032/timelines/forced-jin-$e.txt \
  mame cybotsu ... -debug -debugger none; done
./invenv.sh python research/experiments/EXP-0032/pair_quotes.py \
  local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
  local/win002/mame/cybotsu-0-c0000.asm --out data/translations/win_quotes_pairing.json
```

Saturn (one cold boot of the untouched image, 2026-11-04 09:52-10:07 local,
the user present and asked first: "Yes, go ahead (Recommended)"):

```bash
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python research/experiments/EXP-0019/drive.py launch "$ORIG" local/win002/saturn
# menu keys only (drive.py key): start on the title, down, a (VERSUS MODE);
# a, p2a three times (pilots, body types, machines); start at SET UP.
S=research/experiments/EXP-0032/saturn_quote.py
./invenv.sh python $S catch local/win002/saturn 480
./invenv.sh python $S replay local/win002/saturn
./invenv.sh python $S force local/win002/saturn 599 558 556
./invenv.sh python research/experiments/EXP-0019/drive.py stop local/win002/saturn
```

In the session, `catch` stopped at `savestate` (the agent refuses it while
halted, `err savestate: not allowed while halted`), and the halt, resume,
save, replay and force steps were run as the same agent calls inline. The
script was then changed to do that and rerun from the saved state in a
second launch (`local/win002/saturn2b`, no key presses): the same boxes.

## Actual Result

### The Saturn's choice (`VICTORY.BIN`, static)

- `VICTORY.BIN` loads at `0x06060000`. Its box table is at `0x0607849C`
  (1,074 entries); box N's record holds the same kind of entries as the
  story's (D-020). Its per-pilot scene lists are at `0x0607DB3C`, the same
  11 lists as `STG0AS.BIN`'s `0x060AAD24`, script for script. **List 9** is
  72 one-box scripts (`E33C E202 box E33C E000`).
- The selector (`0x06060B46`-`0x06060BF8`) takes the winner's pilot,
  loads two bytes of the winner's player block (`+0x2E7`, `+0x2E8`; 0 when
  `+0x2EB` >= 2) into R6 and R7, and calls `0x06026F5E`. That routine
  returns `(rand() >> 8) + @0x060D9F60` (an LCG at `0x06039A00`) and does
  not read R6 or R7. The caller takes the result & 7 as the entry, reads
  (scene, byte) from **`0x0606FAA0`** + 16 x pilot + 2 x entry, posts
  `0x14000009` (list 9) with the scene through `0x0602C13C`, and stores the
  byte in the task (`+12`).
- The table: 9 pilots x 8 entries. Scenes: Jin 0, 0, 2-7; Santana 16-23;
  Mary 8-15; Arieta 24, 26, 25, 27-31; Gawaine 32-39; Bao and Mao 40-47;
  pilots 6-8: 48-71. No entry names scene 1 (box 555).

### The arcade's choice (`cybotsu`, static and runs)

- The script interpreter (`0x11CC6`) is a task (scheduler entry 5 of
  `0x0D16`), reading the list from task `+0x15` and the scene from
  `+0x19`. Tasks are made by trap 7 from queued messages (`0xFF1234`,
  `0x163E` posts; `0xCC2` dispatches).
- The match run (`timelines/match.txt`): at frame 5199 a message
  `0x14000006` / `0` is posted, at 5200 the task is made (`create_tap`:
  D1 `14000006`, D2 `00000000`, from the dispatcher, user-stack top
  `0x0CC8`), and at 5260 the interpreter writes slot `0x022A` (554) to
  `0xFF2F7A`; the `VICTORY!` screen shows Jin and slot 554's English
  (`match/snap/cybotsu_f05420.png`, `38ce0753…`). The post tap's stack words
  are not return addresses (the poster is a task that jumps to `0x163E`).
- The only code that builds `0x14000006` is `0x6301C`-`0x630C8`: D0 = 16 x
  the pilot in byte `+0x0C` of the screen's task; one of two player blocks
  (A5 + `0x52E`/`0x52F`, or A5 + `0x92E`/`0x92F`, chosen by the byte at A5 +
  `0x6B2E`) gives two bytes, or 0 and 0 when A5 + `0x531` (`0x931`) >= 2;
  D0 += 4 x the smaller; D0 += 2 x (the byte at A5 + `0x1D` & 1); (scene,
  byte) = table **`0x630CE`**[D0]. It posts list 6 with the scene. The two
  bytes are set to 3 by `0x1F9A`; their other writers are not traced. Here
  "level" means the smaller byte (0-3).
- The table is read PC-relative, which on CPS-2 goes through the decrypted
  program space: the raw ROM bytes there differ. Its scenes for pilots 0-5
  are the Saturn's, entry for entry; the second bytes differ.
- **Forced** (breakpoint at `0x630B8`, `D0` = 2 x entry; MAME's debugger
  reads hex): entries 2, 5 and 7 of Jin's row wrote slots 599, 558 and 560,
  and the `VICTORY!` screen showed three different English lines
  (agent-reviewed): `forced-jin-2` `5105ca68…`, `forced-jin-5` `facf2539…`,
  `forced-jin-7` `89efb564…` (`snap/cybotsu_f05420.png`). A first try with
  decimal values gave slots 569 and 571 (entries 8 and 10: Santana's row).

### The scripts and the records (`pair_quotes.py`)

- Arcade list 6 has 48 scripts; they equal Saturn list 9's first 48, box
  for slot. `cybotsj`'s list 6 (its scripts at `0x12138`) equals
  `cybotsu`'s.
- The 48 entries of pilots 0-5 reach 46 boxes (554, 556-600), 50 Saturn
  lines (955, 957-1005; line 982 is in boxes 579, 580 and 585). Box N's
  lines against slot N's Japanese record: 37 `exact`, 7 `unmapped` (codes
  not in `arcade_jp_map.json`; each has as many codes as the Saturn line
  has characters), 2 `differs` (boxes 579 and 580: the Saturn adds line 982
  after the arcade's one line).
- **The US set has one English record per (pilot, level)**: 24 of 24
  level pairs share their record, so 46 Japanese boxes have 24 English
  records. Jin's level 0 is box 554 twice and Bao and Mao's level 1 box 595
  twice, so 22 pairs of different boxes share an English record.
- Pilots 6-8 reach boxes 1023-1044 (lines 1790-1821), which no arcade
  pilot has.
- Unused by any script: boxes 494-549 and 552-553. The **VS caption**
  reader (`STG0AS.BIN` `0x0606CAE8`) shows box `0x0609CC22`[pilot x 10 +
  stage] (player block `+0x2D2` and `+0x2E3`): boxes 494-549 for pilots 0-5
  (Jin 496-504, Santana 514-522, Mary 505-513, Arieta 523-531, Gawaine
  532-540, Bao and Mao 541-549) and 1045-1071 for pilots 6-8. The arcade's
  reader `0x62D4C` uses the same table (`0x62D9A`) and draws the Japanese
  table only (`0x116F2`).

### On the Saturn's screen (cold boot)

- Versus, Jin (pad 1) against Arieta (pad 2), Blodia against Blodia, stage
  `STG07.BIN`; two rounds to time-out with the vitality held; `VICTORY.BIN`
  at frame 33988.
- Halt at `0x06060BCE` (frame 34272): R8 = 0 (Jin), R0 = `0xDF`, so entry
  7, scene 7, predicted box 560. R6 = R7 = 1.
- Replay from `post.mcs` (`42640c74…`): the box routine got box 560, and
  the screen shows line 961 (`replay-36492.png`, `13bedc70…`).
- Forced by rewriting the box word of scene 7's script (`0x0607D398`,
  `0230`) in the saved state: boxes 599, 558 and 556 were shown, with
  lines 1004 (`force599-40409.png`, `233ba621…`), 959 (`force558-40672.png`,
  `0a91427b…`) and 957 (`force556-40936.png`, `4acdbb7c…`). Agent-reviewed
  against the decoded lines; no text is committed.
- Key presses: 14, all on the title and menus, before the fight
  (`local/win002/saturn/log.jsonl`); a first Start press landed in the
  attract demo and one on the title's fade-in.

The source image is unchanged.

## Conclusion

- **CONFIRMED:** both games choose a win quote from a per-pilot table of 8
  (scene, byte) entries and post it to the list that holds the quote
  scripts (Saturn list 9, `0x0606FAA0`; arcade list 6, `0x630CE`). The
  scenes and the scripts are the same for pilots 0-5, so Saturn box N is
  shown where the arcade shows slot N. Forcing the table entry in MAME and
  the box word on the Saturn showed the predicted slot and box; the
  Saturn's own pick matched the prediction from its random value.
- **CONFIRMED:** the Saturn's entry is its random value & 7 (the halt's R0
  predicted the box shown). **SUPPORTED** (code only): the two player bytes
  it loads go to a routine that does not read them, so the Saturn's pick is
  random among 8.
- **SUPPORTED** (code only): the arcade's entry is 2 x a level (0-3, the
  smaller of two player-block bytes) plus the low bit of the byte at A5 +
  `0x1D`. The table step itself is CONFIRMED by the forced runs.
- **CONFIRMED:** the US set has one English record per pilot and level, so
  the two Japanese quotes of a level share one official English line.
- **SUPPORTED** (code, and lines 899 and 900 seen as Jin's first two
  captions in `EXP-0012`): VS captions are boxes 494-549 (pilots 0-5), from
  the same table in both games.
- **SUPPORTED:** the 7 `unmapped` boxes have the slot's text (equal
  lengths, same position); the meaning of the arcade's level bytes is not
  decoded.

## Uncertainty and Alternatives

- The Saturn forcing replaced the box word of the script, not the table
  entry; the table step is shown by the natural pick (R0 & 7 = 7 → box
  560) and WIN-001's (line 959, entry 5), and by the code.
- What the arcade's level bytes measure (finishing move, round result) is
  not decoded; it does not affect the pairing.
- Only Jin's row was forced; the other pilots' rows rest on the tables and
  the scripts.
- Which English line a Saturn quote shows when its level-mate's Japanese
  differs is a translation choice for the gate, not a fact here.

## Reproduction

Run the procedure. Expect the counts above from `pair_quotes.py`, slot 554
at frame 5260 of the match timeline, slots 599, 558 and 560 from the three
forced timelines, and on the Saturn the selector's halt with R0 & 7 giving
the box the replay shows.
