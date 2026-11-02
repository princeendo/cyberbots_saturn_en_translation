# EXP-0005: Save-State Extractor Validated Against Debugger Dumps

Task: DBG-001
Status: DONE
Confidence: CONFIRMED (WRAM-L, WRAM-H, VDP1 VRAM, VDP2 VRAM); cart RAM not validated

## Observation

`tools/memory/mcs_extract.py` (copied from XvSF, `ENV-003`) reads regions out
of Mednafen 1.32.1 save states. Both siblings found every stored 16-bit
element byte-swapped relative to the Saturn bus, and validated the tool only
against same-instant stock debugger dumps. On Cyberbots, `EXP-0004` run A2
left a state and WRAM-L/WRAM-H dumps of one title freeze; no VRAM dumps
existed.

## Hypothesis

For a state and debugger dumps of the same frozen instant, the extractor's
default `saturn` byte order reproduces each dump byte for byte, for WRAM-L,
WRAM-H, VDP1 VRAM and VDP2 VRAM; the `state` order (no swap) does not.

## Controlled Change

None to the extractor or the game. The comparison varies only the byte order
(`--byte-order saturn` against `state`). Run H was input only, in the silent
home, with the user present.

## Prediction

`saturn` output equals the dumps for all four regions; `state` output differs
from every dump.

## Inputs and Provenance

- Instant A2 (`EXP-0004`): state `local/emu007/run-a2-state/*.mc0`
  (`52ce80ae…b311`), dumps `research/memory_dumps/emu007/wraml-1.bin`
  (`bb0628a5…517c`) and `wramh-1.bin` (`fc70d589…8b10`).
- Instant H (this experiment): state
  `local/dbg001/run-h-state/Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2.mc0`,
  1,099,577 bytes, SHA-256
  `0e64b358b57595902278d339c178489c1ed7911be2a9d69c0653eacaafe33913`, and the
  four dumps in `research/memory_dumps/dbg001/` (table below).
- Emulator, BIOS, image, home as `EXP-0001` to `EXP-0004`.

## Tools and Environment

`tools/memory/mcs_extract.py`, `tools/mednafen/hotkeys.py --keep-focus
--script`, `cmp`, `shasum`.

## Procedure

Instant A2 (no emulator run):

```bash
S=local/emu007/run-a2-state/*.mc0
./invenv.sh python -m tools.memory.mcs_extract $S --region wram_l --region wram_h \
  --out-dir research/memory_dumps/dbg001/a2-saturn
./invenv.sh python -m tools.memory.mcs_extract $S --region wram_l --region wram_h \
  --byte-order state --out-dir research/memory_dumps/dbg001/a2-state
cmp research/memory_dumps/dbg001/a2-saturn/wram_l.bin research/memory_dumps/emu007/wraml-1.bin  # and wram_h
```

Instant H: freeze the title, save a state, open the memory editor, and after
each `.` (next address space) capture the window; dump spaces 1, 2, 9 and 12
([`steps/run-h.steps`](steps/run-h.steps)):

```bash
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/dbg001/run-h.log --script research/experiments/EXP-0005/steps/run-h.steps --keep-focus
./invenv.sh python -m tools.memory.mcs_extract STATE --region wram_l --region wram_h \
  --region vdp1_vram --region vdp2_vram --out-dir research/memory_dumps/dbg001/h-saturn
# the same with --byte-order state --out-dir research/memory_dumps/dbg001/h-state
cmp research/memory_dumps/dbg001/h-saturn/wram_l.bin research/memory_dumps/dbg001/h-wraml.bin  # and the others
```

## Actual Result

**Run G failed first** (2026-11-02 20:44:23 UTC,
[`steps/run-g.steps`](steps/run-g.steps): all keys sent within about 0.4 s of
each other). `option+3` did not open the memory editor: the capture right
after it already shows the CPU view, and no dump was written. The typed
commands went to the CPU view; no stray file was created, and the CPU view's
PC read `00000000` (emulator session only). Run G's files are kept in
`local/dbg001/run-g-failed/`.

**Run H** (20:46:43 UTC, exit 0): `option+a` 64.22 s, `F5` 64.55, `option+d`
65.38, `option+3` 66.42 (keys one second apart). Captures confirm the editor
names: space 1 "Low Work RAM", 2 "High Work RAM", 9 "VDP1 VRAM", 12 "VDP2
VRAM", as in XvSF.

| Instant | Region | Debugger dump SHA-256 | `saturn` | `state` order |
| --- | --- | --- | --- | --- |
| A2 | WRAM-L | `bb0628a515c1877ab27f2b8b90464c554426e19a7c284b5fcc51ea287c48517c` | identical | differs in 712,044 bytes |
| A2 | WRAM-H | `fc70d589f2d8288c2baf6f594d0933ba919544d7c77d084cd20ebac136698b10` | identical | differs in 512,558 bytes |
| H | WRAM-L | `bb0628a515c1877ab27f2b8b90464c554426e19a7c284b5fcc51ea287c48517c` | identical | differs in 712,044 bytes |
| H | WRAM-H | `7ebf334e4d43015344fafbbd15adc272c65b9afa1261adfec2e6ba3a0d5a5b63` | identical | differs in 512,552 bytes |
| H | VDP1 VRAM | `be799aa78a7f2fc496c2df3f4af3bebe73e6627d356e11e630593dead28a1bec` | identical | differs in 17,034 bytes |
| H | VDP2 VRAM | `311fcb6db87ebdca45600263e554adc1dfb061b5cde8fd4527a6dc11b9bba080` | identical | differs in 51,266 bytes |

- Dump sizes: 1,048,576 bytes (work RAMs), 524,288 bytes (VRAMs). Non-zero
  bytes at H: WRAM-L 867,119, WRAM-H 542,163, VDP1 VRAM 19,841, VDP2 VRAM
  127,053.
- WRAM-H differs between instants A2 and H in 73 bytes; WRAM-L is the same at
  both. The two instants are independent checks for WRAM-H.
- Cart RAM: the state's `CART_EXTRAM` section holds `LO` and `HI` of 524,288
  bytes each (1 MiB, matching `Cart: 1MiB Extended RAM`). The extractor's
  `cart_ram` entry expects 4 MiB (XvSF's cart) and refuses:
  `cart_ram: expected 4194304 bytes, found 1048576`. So the default (all
  regions) fails on Cyberbots states; name regions with `--region`. The stock
  memory editor has no cart space to validate against (sibling finding).
- Source manifests identical before and after; quiet config `aad9a7ef…57cf`.

## Conclusion

**CONFIRMED** for Cyberbots: `mcs_extract` with the default `saturn` byte
order reproduces stock debugger dumps exactly for WRAM-L and WRAM-H (two
instants) and VDP1 and VDP2 VRAM (one instant), and the swap is required (the
unswapped order differs everywhere). These regions extracted from states may
be used as evidence. Cart RAM stays **HYPOTHESIS** and the tool cannot yet
read Cyberbots' 1 MiB cart.

## Uncertainty and Alternatives

- VDP1 and VDP2 VRAM were checked at one instant only.
- Run G's failure is the second silent debugger failure in two experiments
  (`EXP-0004` run A lost two dumps). Both happened with keys sent within a
  fraction of a second; spacing the first debugger keys one second apart
  worked. That timing is the cause is **HYPOTHESIS**. Always capture the
  editor before typing, and check every dump file exists.
- The agent interface (`EMU-021`) will replace hotkey-driven debugger work.

## Reproduction

Run the procedure above from the repository root, with the user present for
run H. Expect the six `identical` results in the table.
