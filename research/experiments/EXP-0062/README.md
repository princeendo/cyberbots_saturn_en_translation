# EXP-0062: The Options Screen, Its Settings and Their Save

Task: OPT-001
Status: DONE
Confidence: CONFIRMED (layout, variables, save and load, by one-variable
changes and a cold boot); SUPPORTED (code reading only, marked below)

## Observation

- The `OPTION MODE` screen (`docs/text_surfaces.md`) has eight English rows
  above `PRESS START TO EXIT`; how it is built and saved was unknown.
- D-048: the game's save is checked at boot with a checksum; a bad save
  shows `WARNING0`.

## Hypothesis

The menu is printed from plain strings by code; its settings are a small
RAM block copied into the game's save; the block has a byte that nothing
else uses, which the game saves, checksums and loads like the others.

## Controlled Change

One RAM write per run (or one save-file byte), from saved states; one cold
boot with one save.

## Prediction

Each write shows on screen as its row's value; a spare settings byte
survives save, checksum and boot load; a changed byte with a stale
checksum gives `WARNING0`.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched image | `local/disc_images/cyberbots_saturn_jp_2m/` |
| Session states | `local/ref005/session/states/` (27173: the Options screen; 384: before the boot check; all 166 for the watch) |
| `free6.bkr` | `EXP-0051` fixture: formatted, no save |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/sh2/disasm.py` | `OPDEMO.BIN` as loaded (`0x06060000`) and WRAM-H at state 27173 |
| [`session.py`](session.py) | A paused session from a state (dumps, reads) |
| `EXP-0056/poke.py` | One write, screenshot |
| [`watch.py`](watch.py) | Read/write log of a range over all 166 states → [`watch_spare.json`](watch_spare.json) |
| [`save_test.py`](save_test.py) | From the Options state, sets the menu state to 4 (where Start leads), lets the game save; a scratch copy of the silent home; extracts `CYBERBOTS01` |
| [`load_test.py`](load_test.py) | From state 384, the internal backup memory replaced (agent `backup` space), through the boot check |
| [`cold_load.py`](cold_load.py) | Cold boot with a given save (asked first) |
| [`results.json`](results.json) | The save, load, cold-boot and write runs, summarized |

## Procedure

```bash
E=research/experiments/EXP-0062; ST=local/ref005/session/states; P=research/experiments/EXP-0056/poke.py
./invenv.sh python $E/session.py launch $ST/f00027173.mcs local/opt001/s27173   # dumps: OPDEMO.BIN, WRAM-H
./invenv.sh python $P local/opt001/poke/diff --state $ST/f00027173.mcs --write 060D9290=07 --frames 30 --shots 30
#   likewise cur 0606BE8C=00000003, ram 0606BE90=00, time 060D9291=01, test 060D9294=15,
#   font1-3 06065A44=<hex of "ABCDEFGHIJKLMNOPQRS" / "TUVWXYZ0123456789&-" / "abcdefghijklmnopqrs">
./invenv.sh python $E/watch.py local/opt001/watch-spare 060D9295-060D929F --out-json $E/watch_spare.json
./invenv.sh python $E/save_test.py local/opt001/save-ctl
./invenv.sh python $E/save_test.py local/opt001/save-spare --write 060D9295=01
C=local/opt001/save-ctl/home/sav/*.bkr; S=local/opt001/save-spare/home/sav/*.bkr
./invenv.sh python $E/load_test.py local/opt001/load-ctl $C
./invenv.sh python $E/load_test.py local/opt001/load-spare $S
./invenv.sh python $E/load_test.py local/opt001/load-badsum $C --set 9=01
./invenv.sh python $E/load_test.py local/opt001/load-fixsum $C --set 9=01 --fix-sum
./invenv.sh python $E/load_test.py local/opt001/load-byte15 $C --set 19=FF --fix-sum
./invenv.sh python $E/load_test.py local/opt001/load-nosave local/boot001/fixtures/free6.bkr
cp $S local/opt001/spare.bkr; ./invenv.sh python $E/cold_load.py local/opt001/cold-spare local/opt001/spare.bkr
```

2026-11-06, 11:55-12:20 local. One cold boot, no key, asked first: "Yes,
run it now (Recommended)".

## Actual Result

### How the screen is built (code; each variable confirmed by a write)

- `OPDEMO.BIN` loads at `0x06060000` (RAM equals the file but for one data
  byte, `0x5EB3`). The labels and values are C strings at file
  `0x59E8`-`0x5B58`.
- **Drawing** (`0x060623A4`, every frame): the title by `0x0602A766`
  (`OPTION MODE`, x 10, row 4); each label by `0x0602A82A` (r4 x cell,
  r5 row, r6 colour: 31 selected, 20 not, r7 string), x 6, rows 8, 10, …
  20; `3M RAM MODE` at row 22 **only when the byte `0x0606BE90` is set**;
  `PRESS START TO EXIT` at x 12, row 24. Values at x 21 and 30 (the
  difficulty stars by `0x0602A7FA`, the sound-test number by `0x0602A86C`
  with `%02d`). The text layer is not cleared between frames, so a label
  stops showing only if overdrawn (the write of `0x0606BE90` = 0 left the
  row on screen).
- **Rows on screen:** text row r is at screenshot y = 8r + 12 (7 pixels
  high); the visible area is screenshot rows 8-231 (`BOOT-002`). Title y
  44-59; `DIFFICULTY` y 76-82; `3M RAM MODE` 188-194; `PRESS START TO
  EXIT` 204-210.
- **Cursor** `0x0606BE8C` (long; 3 highlighted `SOUND`). Up and down move
  it; it wraps at 7 when `0x0606BE90` = 1, else at 6 (SUPPORTED, code).
- **Menu states** (word `0x060CFEE0`, table `0x06067624`): 0 setup
  (`0x06062630`: `0x0606BE90` = 1 when the cart ID byte `0x24FFFFFF` is
  `0x5A` or `0x5C`), 1 draw setup, 2 input (`0x06062704`), 3 `KEY CONFIG`
  sub-screen (`0x06063FD0`), 4 leave and save (`0x06062B02`).
- **Values:** the settings block `0x060D9290`: +0 difficulty 0-7 (7 drew
  eight stars), +1 time limit (1 = OFF, seen), +2 short cut, +3 sound
  (1 = monaural; calls `0x060407EA`), +4 sound test 0-40 (`0x15` drew
  `21`). `DATA RESET` (A+B+C) calls `0x060372A4`; `KEY CONFIG` moves to
  state 3; `3M RAM MODE` flips the long `0x06047ED4`.
- **Start** (code): copies difficulty to `0x060CFE60` and short cut to
  `0x060D928C`, then state 4, which waits for the fade flag `0x060CFEA0`,
  sets `0x060D934D` = 1 and jumps to the save routine `0x06036A58`.
- **`3M RAM MODE`** (SUPPORTED, code): the long `0x06047ED4` is set to 1
  at start-up when a RAM cart is present (`0x06016938`, ID `0x5A`/`0x5C`),
  and the loaders at `0x06038790`/`0x06038924` then copy data through
  cart memory (`0x22400000`). It is not part of the save.
- **Font:** the menu's print routine draws `A`-`Z`, `0`-`9`, `&`, `-` and
  `a`-`s` (written over the `PRESS START TO EXIT` string, seen).

### The save

- **Layout** (`0x06036F10` builds it, `0x06037064` reads it back): 256
  bytes, `CYBERBOTS01`: +0 `CYB\0`; **+4-19 the settings block**
  (`0x060D9290`-`9F`, 16 bytes, by the copy routine `0x060396C4`); +20-35
  single bytes from `0x060D924B`-`0x060D9287` (low bytes of longs); +36 102 bytes from
  `0x060D92A0`; +138 5 bytes from `0x060D9306`; +143 one byte
  (`0x060D930E`); +144 80 bytes from `0x060CFF14`; zeros; **+254-255 the
  16-bit sum of bytes 0-253**.
- **Leaving Options saves** (both forced exits hit `0x06036A58`, then
  `0x06036F10`). The control save equals the `EXP-0051` fixture byte for
  byte; with `0x060D9295` = 1 it differs only at +9 and in the sum
  (`0739` → `073a`).
- **Loads** (from state 384, through the boot check; `results.json`):

  | Save | Boot path | Settings after |
  | --- | --- | --- |
  | control | check, accepted | `03 00 00 00 01 00…` |
  | game-made, +9 = 1 | accepted | +5 = 1 |
  | +9 = 1, stale sum | **`WARNING0`** (`0x06036DA8`, R4 0) | defaults |
  | +9 = 1, sum fixed | accepted | +5 = 1 |
  | +19 = `FF`, sum fixed | accepted | +15 = `FF` |
  | no save (`free6`) | check, no save | `03 00 00 00 00 00…` |

- **Cold boot** with the game-made save: check at frame 1,369, accepted at
  1,375, no warning, `0x060D9295` = 1 at frame 2,000, the opening playing.

### Who touches bytes +5-15 (`watch_spare.json`, all 166 states)

Only: at start-up, a clearing loop (`0x060A06A0`, writes 0) and an
initialiser (`0x060A78C0`, `0x060B0F72`) over `0x060D928C`-`9F` before the
boot check; and the copy routine (`0x060396F8`) in the three saves of the
session. Nothing else in the session (attract, title, Options, select, VS,
fights, continue, game over, initials) reads or writes them. `DATA RESET` clears them to 0 (code:
`0x06039708` fill of 11 bytes from `0x060D9295`).

## Conclusion

Prediction met. A new setting can live in the settings block's spare bytes
(`0x060D9295`-`9F`): saved, checksummed and loaded by the game's own code,
0 with no save, with an old save and after a data reset (so 0 should mean
Latin). A ninth row can go at row 24 with `PRESS START TO EXIT` moved to
row 26 (y 220-226, inside the visible area), or the rows can be moved up;
the `KEY CONFIG` sub-screen is a model for a sub-menu.

## Uncertainty and Alternatives

- The cursor wrap and the `3M RAM MODE` row's condition are read from code;
  writing `0x0606BE90` could not show them (the text layer is not
  cleared).
- Row 26 is near the bottom edge; how much of it a CRT shows is not known.
- What the start-up initialiser at frame 93 writes was not traced (the
  save or the defaults overwrite it before use).
- The watch covers one arcade session (title to game over, plus
  Options); versus mode and the endings were not in it (`OPT-003`'s logs
  cover them).

## Reproduction

Run the procedure. Expect `watch_spare.json` and `results.json` as
committed (screenshot hashes as listed).
