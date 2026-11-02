# EXP-0004: Stock Debugger Dumps, a Memory Write, and a Write Breakpoint

Task: EMU-007
Status: DONE
Confidence: CONFIRMED

## Observation

`EXP-0003` drove Mednafen hotkeys unattended. The stock 1.32.1 debugger is
keyboard-only: Alt+A frame advance, Alt+D debugger, Alt+3 memory editor
(`.`/`,` change address space, `d` dump, `l` load), and in the CPU view
Shift+W write breakpoints. XvSF's `EXP-0004` found that `hotkeys.py` must post
Option chords as left-Option events; the copied tool already does. Nothing
about Cyberbots' memory was known.

## Hypothesis

Driven by `tools/mednafen/hotkeys.py`, the stock debugger can (1) dump WRAM-L
and WRAM-H at a frozen instant, repeatably; (2) write a prepared file into
WRAM-H and restore it; (3) halt the CPU on a write breakpoint.

## Controlled Change

No change to binary, BIOS, configuration or source. Input only, in the silent
home with `sav/` emptied before each run. Memory was written only while
frozen and restored before any frame ran. The user was present ("Run
EMU-007", 2026-11-02). Kept to the three acceptance items (no running-dump
control or frame-counter breakpoint, which XvSF also ran).

## Prediction

- Two dumps of each work RAM taken during one freeze are byte-identical,
  1,048,576 bytes each.
- After `l` of a 16-byte pattern, a dump of the same range equals the
  pattern; after `l` of the saved original, it equals the original.
- With a write breakpoint on all of WRAM-H the game stops: window captures
  taken seconds apart are identical, and the CPU view shows a store
  instruction.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/cyberbots_saturn_jp_2m/` (63
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock 1.32.1 binary
(`077ac658…669f`), home `local/mednafen_quiet/` (`aad9a7ef…57cf`, unchanged
after all runs). Pattern file `research/memory_dumps/emu007/w-pattern.bin`:
the 16 ASCII bytes `EMU-007 WRITE OK` (SHA-256 `b0771fd5…a3fe`).

## Tools and Environment

`tools/mednafen/hotkeys.py` with `--keep-focus` and `--script`; `window=FILE`
captures Mednafen's window alone (`screencapture -o -l <window id>`), since
Mednafen's own screenshots leave out the debugger. Screen Recording was
already permitted; no dialog appeared.

## Procedure

Step files are in [`steps/`](steps/) (copies of the ignored
`local/emu007/run-*.steps`; outputs go to ignored paths). Each run:

```bash
find local/mednafen_quiet/sav -type f -delete
./invenv.sh python -m tools.mednafen.hotkeys \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/emu007/run-X.log --script local/emu007/run-X.steps --keep-focus
```

- Run A (`run-a.steps`, freeze at 63 s on the static title): `option+a`,
  `F5`, `option+d`, `option+3`, `period` (Low Work RAM), two `d` dumps
  `00000000 000fffff …/wraml-N.bin`; `period` (High Work RAM), two dumps
  `wramh-N.bin`; then on `000f0000 000f000f`: `d` before, `l` pattern, `d`
  after, `l` before, `d` revert.
- Run A2 (`run-a2.steps`): run A with window captures before and after the
  first WRAM-L dump's `return`.
- Run F (`run-f.steps`): captures at 63 s and 65 s; `option+d`, `shift+w`,
  type `06000000-060fffff 26000000-260fffff`, `return`, `option+d`; captures
  at 73 s and 77 s; `option+d`; captures at 79 s and 81 s.

Before run A, EXP-0003's state was moved to `local/emu006/run1b_state/`, and
each run's state was moved out of `mcs/` before the next.

## Actual Result

All runs exited 0 (F12): run A 2026-11-02 20:34:50 UTC, A2 20:37:04, F
20:39:10. Source manifests identical before and after.

**Run A:** the capture shows the editor on Low Work RAM and "State 0 saved."
The two WRAM-H dumps and the write test files were written, but **no
`wraml-*.bin` was written anywhere**, and the log has no error. Kept in the
ignored `research/memory_dumps/emu007/run-a/` and
`local/emu007/run-a-state/` (1,099,597 bytes, `d18d8304…06fb`).

**Run A2** (all files written):

| File | Size | SHA-256 |
| --- | ---: | --- |
| `wraml-1.bin`, `wraml-2.bin` | 1,048,576 | `bb0628a515c1877ab27f2b8b90464c554426e19a7c284b5fcc51ea287c48517c` (both) |
| `wramh-1.bin`, `wramh-2.bin` | 1,048,576 | `fc70d589f2d8288c2baf6f594d0933ba919544d7c77d084cd20ebac136698b10` (both) |
| `w-before.bin`, `w-revert.bin` | 16 | `24747cbe…a4c9` (both) |
| `w-pattern.bin`, `w-after.bin` | 16 | `b0771fd5…a3fe` (both) |

- WRAM-L and WRAM-H differ. WRAM-L begins
  `00 00 00 02 00 00 00 00 00 04 19 DD 02 01 00 84`, as the editor showed
  (capture `a1-wraml.png`); WRAM-H begins `06 00 09 4A 06 00 09 4A`.
- Write test at WRAM-H offset `0xF0000`: before
  `00000000B2BB9A000000000000000000`, after = the pattern, after revert = the
  original. Run A's write test gave the same three results.
- The capture before `return` shows the prompt "Dump Memory(start end
  filename)" holding the typed path, so the keys reach it.
- State saved during the run A2 freeze: `local/emu007/run-a2-state/Cyberbots
  - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2.mc0`,
  1,098,387 bytes, SHA-256
  `52ce80ae04af0c87a3ba1730229e2ea97e0ad09ecb201edb9ca89c640be2b311`. It and
  the four work-RAM dumps are the same instant, for `DBG-001`.
- Run A's and A2's WRAM-H dumps differ (first at byte 32,432): different
  instants, as expected.

**Run F:** captures at 63 s and 65 s differ (running). After the
breakpoint, captures at 73 s and 77 s are identical (`ceca8d93…`), and with
the debugger shown, captures at 79 s and 81 s are identical (`e7bc2f13…`).
The CPU view shows PC `060008F0`, highlighted `mov.l r0,@-r15` (a stack
push), R15 about `06008000`, and a branch trace through `[INT42]` (read from
the capture's small font; a digit may be misread). The store target, R15 − 4,
lies in the watched WRAM-H range.

## Conclusion

**CONFIRMED.** Unattended, the stock debugger dumps WRAM-L and WRAM-H
repeatably at a frozen instant, writes and restores WRAM-H bytes exactly, and
halts on a write breakpoint at a store into WRAM-H.

## Uncertainty and Alternatives

- Run A lost both WRAM-L dumps silently; run A2, identical except for two
  window captures around the first dump's `return`, wrote them. The cause
  (key timing right after the save message, or something else) is
  **UNKNOWN**. Check that every dump file exists after a debugger run.
- The editor's "Low/High Work RAM" offsets `0x00000-0xFFFFF` are taken to be
  bus `0x00200000-0x002FFFFF` and `0x06000000-0x060FFFFF` by name; the
  breakpoint's store into WRAM-H is consistent but does not prove the offset
  mapping. `DBG-001` compares these dumps with the state extractor.
- The first write the breakpoint caught is an interrupt handler's stack push,
  not game data; breakpoints on a narrow range are needed for anything
  specific.
- Whether the dump hashes repeat across cold boots was not tested.

## Reproduction

Use the procedure with `--script research/experiments/EXP-0004/steps/run-X.steps`
(delete earlier outputs first; dumps overwrite, captures need Screen
Recording). Expect run A2's repeat dumps to match each other, the write test
to read back the pattern and then the original, and run F to show a halted
CPU view at a store into WRAM-H.
