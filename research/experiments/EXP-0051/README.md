# EXP-0051: Which Boot-Time Message Shows Under Which Condition

Task: BOOT-001
Status: DONE
Confidence: CONFIRMED (each picture's condition, the statuses, the VRAM copy, the free-space limit); SUPPORTED (what a button does)

## Observation

- D-003 (`EXP-0002`): no warning in boot or attract with any cart, with the
  homes' normal backup memory.
- `CYBER.BIN` names `WARNING0`-`4.PIX` in 16-byte entries from file offset
  `0x39168`, next to the save's name `CYBERBOTS01` (static search).

## Hypothesis

From a static reading of `CYBER.BIN` (resident at `0x0600D000`; 331,205 of
its 331,376 bytes equal the END-001 checkpoint's WRAM-H there):

- The start-up code (`0x060169D4`) calls one save check, `0x06036C3E`,
  once, before the title.
- The check calls `0x060367F4`, which initializes the BIOS backup library
  (vector `0x06000358`) and stores the status of the internal memory
  (`0x060DBA94`) and of a cart (`0x060DBA98`), then shows:
  - `WARNING3` if the internal status is 1 or 2 and the cart's is 2;
  - `WARNING1` if the internal status is 1 or 2;
  - `WARNING2` if the cart's status is 2.
- It then looks for `CYBERBOTS01` on each device (`0x060DBA9C`, bit 0
  internal, bit 1 cart). With no save, it records where 0x120 bytes are
  free (`0x060DBA9D`) and shows `WARNING4` if nowhere.
- With a save, it reads it (`0x060368FC`, 10 tries) and sums its first
  0xFE bytes against the word at 0xFE. A failed read or a wrong sum shows
  `WARNING0`.
- `0x06036DA8` loads `WARNINGn.PIX` (n = R4) through `0x060385A0` to VDP2
  VRAM `0x20000`, 0x20000 bytes.
- `WARNING1`-`3` wait in `0x06036754`; any of seven pad bits calls the
  BIOS vector at `0x0600026C`. `WARNING0` waits in `0x06036974`; a button
  continues the game, which rewrites the save from defaults. `WARNING4`
  waits in its own loop (from `0x06036CD6`); a button continues
  (`0x06036D8A`). (First read as calling the BIOS like `1`-`3`; corrected
  by the free4 screen's own words and a second look at the code.)

All of this is HYPOTHESIS until the boots below.

## Controlled Change

One backup-memory condition per cold boot of the untouched image, from a
fresh copy of the silent home; nothing else changes.

## Prediction

| Case | Condition | Warning |
| --- | --- | --- |
| control | the interactive home's real save, 1 MiB cart (`auto`) | none; save accepted |
| zero | internal memory all zero (unformatted) | `WARNING1` |
| free4 / free5 / free6 | formatted, a dummy file, 4/5/6 blocks free, no save | `WARNING4` where under 0x120 bytes are free |
| damaged | the real save with one data byte inverted | `WARNING0` |
| cart | the real save, a backup cart (Mednafen's own) | none |
| cart-zero | the real save, an all-zero backup cart | `WARNING2` |
| both-zero | zero internal, all-zero cart | `WARNING3`, then `1`, `2` |

## Inputs and Provenance

| Input | SHA-256 (first 16) | Notes |
| --- | --- | --- |
| Track 01 of the untouched image | as `references/saturn_jp/README.md` | `local/disc_images/cyberbots_saturn_jp_2m/` |
| `save.bkr` | `050d517b921328ef` | the interactive home's internal memory, one save `CYBERBOTS01` (256 bytes, blocks 2-6) |
| `damaged.bkr` | `8db23429b3e149a5` | `backup_ram corrupt --from save.bkr` (block 5, byte 20 inverted: file offset 340, `00` → `FF`, inside the checksummed data) |
| `zero.bkr` | `c35020473aed1b46` | `backup_ram zero` |
| `free4.bkr` / `free5.bkr` / `free6.bkr` | `b385ae5f196987f7` / `2b0c29b40e475ff2` / `d5a863ccecfb9a60` | `backup_ram freeN` |
| `cart_zero.bcr` | `a484aacc8eb1d497` | 512 KiB of zero, gzip (`gzip -n`), the form Mednafen writes its save cart in (`cart` case: `858c34ae…`, 524,288 bytes of "BackUpRam Format" unpacked) |

Fixtures and runs are in the ignored `local/boot001/`. `backup_ram.py`'s
layout matches the real Cyberbots save (34-byte header, block list, 4-byte
tags).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`boot_case.py`](boot_case.py) | One cold boot per case in a fresh copy of the silent home (patched Mednafen 1.32.1, D-007), log-mode PC breakpoints, screenshots, VDP2 VRAM and a state 60 frames after each warning |
| [`summarize.py`](summarize.py) | → [`cases.json`](cases.json) (numbers only) |
| [`button.py`](button.py) | From a warning state: halt at the pad read, write a button bit, run on |
| `tools.sh2.disasm`, `tools.memory.mcs_extract` | Static reading; WRAM-H of the free4/free5 states (validated region, D-006) |

## Procedure

```bash
F=local/boot001/fixtures; P=research/experiments/EXP-0051/boot_case.py
B="./invenv.sh python -m tools.mednafen.backup_ram"
cp "local/mednafen/sav/Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2.bkr" $F/save.bkr
for k in zero free4 free5 free6; do $B $k $F/$k.bkr; done
$B corrupt $F/damaged.bkr --from $F/save.bkr
head -c 524288 /dev/zero | gzip -n > $F/cart_zero.bcr
./invenv.sh python $P local/boot001/control --bkr $F/save.bkr --frames 1800
for c in zero free4 free5 free6 damaged; do
  ./invenv.sh python $P local/boot001/$c --bkr $F/$c.bkr --frames 1800; done
./invenv.sh python $P local/boot001/cart --bkr $F/save.bkr --cart backup --frames 1800
./invenv.sh python $P local/boot001/cart-zero --bkr $F/save.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python $P local/boot001/both-zero --bkr $F/zero.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python research/experiments/EXP-0051/summarize.py \
  local/boot001/{control,damaged,zero,cart-zero,both-zero,free4,free5,free6,cart} \
  --out research/experiments/EXP-0051/cases.json
for c in zero damaged free4; do ./invenv.sh python research/experiments/EXP-0051/button.py \
  local/boot001/$c --read $(case $c in zero) echo 06036798;; damaged) echo 060369BA;; *) echo 06036D18;; esac); done
```

2026-11-06, 07:00-07:40 local. Nine cold boots, asked first: "Yes, run all
9 (Recommended)". No key was pressed.

## Actual Result

Every prediction held but one (`cases.json`): with both memories
unformatted only `WARNING3` shows, because `WARNING1`-`3` wait without
returning (the prediction said `3`, then `1`, `2`).

| Case | Warning | Internal, cart status | Save found / room flags |
| --- | --- | --- | --- |
| control | none; the save is read and accepted (`0x06037064`) | 0, 1 | 1, 0 |
| damaged | `WARNING0` | 0, 1 | 1, 0 |
| zero | `WARNING1` | 2, 1 | 0, 0 |
| cart-zero | `WARNING2` | 0, 2 | 0, 0 |
| both-zero | `WARNING3` only | 2, 2 | 0, 0 |
| free4 | `WARNING4` | 0, 1 | 0, 0 |
| free5 | `WARNING4` | 0, 1 | 0, 0 |
| free6 | none | 0, 1 | 0, 1 |
| cart | none | 0, 0 | 1, 0 |

- The check starts at frame 1,369 of each boot; the picture routine is
  called at frame 1,372 (1,375 for `WARNING0`, after the save is read),
  and each screen was captured at frame 1,457.
- At each capture, VDP2 VRAM from `0x20000` equals `WARNINGn.PIX` byte for
  byte, with n the R4 of the call.
- Screens (352 × 240 screenshots): `WARNING0` `1904dbaf…387c`,
  `WARNING1` `3d044f4e…e5f0`, `WARNING2` `177e54ed…3bb2`, `WARNING3`
  `27518ac1…7e0d`, `WARNING4` `3f358756…cdf4` (free4 and free5 identical).
  The agent's transcriptions and translations are kept locally
  (`local/boot001/transcriptions.md`, never committed); the meanings are in
  D-048.
- The BIOS free size at the free4/free5 warnings (WRAM-H `0x060DBA64`,
  `totalsize, totalblock, blocksize, freesize, freeblock`): 32768, 512, 64,
  202, 4 and 32768, 512, 64, 260, 5. The game needs 0x120 (288). So 5 free
  blocks warn, although the save itself takes 5 blocks and `WARNING4` asks
  for "05".
- Buttons: `button.py` halted at each pad read and wrote `0100`; the
  screen did not change and no later routine was reached in 900 frames, on
  all three screens. The write is in RAM but the CPU's next read did not see
  it, most likely because it reads the word through its data cache, which
  the agent's write bypasses (HYPOTHESIS). The agent has no register write
  and no cache space (`spaces`).

## Conclusion

Prediction met for every picture (the both-unformatted sequence aside): the game's only boot-time messages are
the five `WARNINGn.PIX` pictures, shown by one save check before the
title, each under the condition in D-048. `WARNING1`-`3` stop the game
(the code calls the BIOS on a button; the screens say "go on to the
multiplayer screen"); `WARNING0` and `WARNING4` let it start. Those button
effects are SUPPORTED by the code and the screens' words, not by a press.

## Uncertainty and Alternatives

- A press on each screen is left to `BOOT-005`'s cold boots, with the user
  present.
- Two conditions the code tests cannot be made in Mednafen: a read failure
  of an intact save (shows `WARNING0` too) and internal status 1 (would
  show `WARNING1` or `3`). They use pictures already captured.
- How the BIOS computes the free size (202 and 260 for 4 and 5 blocks) is
  not known; only the observed values are.
- `0x06036C74` tests the internal status before looking for a save on the
  cart; why is not known and changes no picture.

## Reproduction

Run the procedure (nine cold boots: ask the user first). Expect the table
above, the five screenshot hashes, and the VRAM equalities.
