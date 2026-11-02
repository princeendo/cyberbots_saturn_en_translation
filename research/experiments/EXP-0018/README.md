# EXP-0018: The M1 Box's Text Comes From `STG0AS.BIN`, Loaded Raw

Task: DISC-001
Status: DONE
Confidence: CONFIRMED (source file, raw load, no relocation); UNKNOWN (the 10 bytes changed after the load; when `VICTORY.BIN` and `END.BIN` load)

## Observation

The M1 box's text is Shift-JIS at WRAM-H `0x0606F09C` (line 4) and
`0x0606F0B8` (line 5) (D-015, D-016). The same dialogue table is in
`STG0AS.BIN`, `VICTORY.BIN` and `END.BIN` (D-008), and WRAM-H from
`0x06060000` equals `STG0AS.BIN` in all but about 30 bytes at the M1
checkpoints (EXP-0016). Line 4 is at file offset `0xF09C` in `STG0AS.BIN`,
`0x1D68` in `VICTORY.BIN` and `0xAF4C` in `END.BIN`.

## Hypothesis

The text is loaded when the story's first stage starts, raw (no compression),
from `STG0AS.BIN` to `0x06060000`, so that file offset = address −
`0x06060000`.

## Controlled Change

None to the game. Two variables between runs, one at a time:

- **The state.** The trial starts before the load; the control starts after
  it. Both have the same write breakpoint and no input.
- **The breakpoint set.** One trial adds the CD block command registers to
  the log.

## Prediction

The trial hits the breakpoint in a copy routine whose source is the CD block.
The CD command just before it reads `STG0AS.BIN`'s sectors (FAD = LSN 22,538
\+ 150 = `0x58A0`), and RAM up to the hit equals the file. The control has no
hit.

## Inputs and Provenance

- REF-005 session states (`local/ref005/session/states/`, EXP-0011):
  `f00004138.mcs` (`3eb789da…a437`, 1,526,195 bytes; machine select, before
  the load) and `f00004493.mcs` (`0b52c695…5169`; after it).
- M1 checkpoint dumps `research/memory_dumps/dbg004/{a-box-open,b-box-complete,c-after-box}/wram_h.bin` (EXP-0016).
- Data-track files extracted to the ignored `local/extracted/saturn_jp/`;
  listing `references/saturn_jp/iso_listing.json`.
- Untouched image (Redump 58190); after the work all 63 components still hash
  to the recorded values (`local/logs/disc001-source-after.json`). Patched
  binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`scan_states.py`](scan_states.py) | WRAM-H of every session state (validated extractor, D-006): line 4 present or not, and bytes differing from each script copy at `0x06060000` |
| [`trace.py`](trace.py) | Agent run from a state with no input: write breakpoint on lines 4-5 (`0x0606F09C`-`0x0606F0D3` and the `0x2606…` mirror), halt on the first hit and dump both work RAMs, then log every hit; `--extra` adds ranges, `--log` logs from the start |
| `tools/sh2/disasm.py` | SH-2 disassembly of the halt dump |
| `tools/disc/hash_source.py` | Source hashes after the work |

## Procedure

```bash
S=local/ref005/session/states
./invenv.sh python research/experiments/EXP-0018/scan_states.py $S local/extracted/saturn_jp
./invenv.sh python research/experiments/EXP-0018/trace.py $S/f00004138.mcs local/disc001/trial1
./invenv.sh python research/experiments/EXP-0018/trace.py $S/f00004138.mcs local/disc001/trial2
./invenv.sh python research/experiments/EXP-0018/trace.py $S/f00004493.mcs local/disc001/control1
./invenv.sh python research/experiments/EXP-0018/trace.py $S/f00004138.mcs local/disc001/cdcmd1 \
  --frames 150 --log --extra 25890018-25890027 --extra 05890018-05890027
./invenv.sh python -m tools.sh2.disasm local/disc001/trial1/workramh.bin \
  --base 0x06000000 --start 0x06041F8C --end 0x06041FC8
./invenv.sh python -m tools.disc.hash_source --json \
  local/disc_images/cyberbots_saturn_jp_2m/* > local/logs/disc001-source-after.json
```

17:14-17:17 local, 2026-11-02, the user present.

## Actual Result

- **When (session scan).** Line 4 is first in WRAM-H at state 4316. At 4138
  (machine select, Jin's machine being chosen) all 157 sectors' worth of
  `0x06060000`-`0x060AE7FF` differ from `STG0AS.BIN`. At 4316 (the screen
  goes black, then NOW LOADING) the first `0x39800` bytes equal the file and
  the rest do not: a load in progress, in file order. By 4493 only 10 bytes
  differ. Later in the session the region is partly overwritten during the
  fight (line 4 stays) and equals the file again at 13139, so the file is
  reloaded for the next stage. Neither `VICTORY.BIN` nor `END.BIN` is ever
  resident at `0x06060000` in the 166 states: they differ in at least
  94,938 and 241,525 bytes.
- **Trial (two runs).** From 4138 with no input, the replay shows the pick
  made, then NOW LOADING. The breakpoint is hit 14 times (56 bytes, lines 4
  and 5) at PC `0x06041FB4`, `mov.l r3,@r14`, with R13 = `0x25818000` (the CD
  block's data transfer register) and R14 = `0x0606F09C`…`0x0606F0D0`. The 14
  words in R3 equal `STG0AS.BIN[0xF09C:0xF0D4]`. Both runs have the same PCs,
  values and destinations; the frame differs by one (329 and 328). At the first
  hit WRAM-H `0x06060000`-`0x0606F09B` equals `STG0AS.BIN[0:0xF09C]` exactly,
  and the copy has not reached the bytes after it.
- **The routine.** `0x06041F8C`: a longword copy, `mov.l @r13,r3` /
  `mov.l r3,@r14`, with source stride 0 (the data register) and destination
  stride 4, 512 longwords per 2,048-byte sector. It is called through a
  transfer-mode table at `0x0604705C` (caller `0x060420F0`). No decoding:
  the load is raw.
- **CD commands.** In the 150 frames from 4138, the command routine at
  `0x0603D186` writes CR1-CR4 (`0x25890018`-`0x25890027`) 8,978 times; most
  are status and sector-count polls. Exactly one is Play Disc, at frame 305:
  `1080 58A0 0080 009D`, which is FAD `0x0058A0` for `0x9D` = 157 sectors.
  FAD `0x58A0` − 150 = LSN 22,538, the first sector of `STG0AS.BIN`
  (320,724 bytes = 157 sectors). Data transfer (`5300`/`0600` pairs) follows
  from frame 316, and the text hit is at 328.
- **File table.** WRAM-H `0x060DCB98` holds a table of 24-byte entries (FAD,
  size, 4 zero bytes, 12-byte name) in ISO directory order. Its entry 290 is
  `STG0AS.BIN`, FAD `0x58A0`, size `0x4E4D4` (320,724), at `0x060DE6C8`. A
  request record at `0x060DC824` holds `0x124` (292 = 290 + the two `.` and
  `..` entries), FAD `0x58A0`, size `0x4E4D4`, `0x800`, `0x9D`.
- **Control.** From 4493 (after the load), 400 frames with the same
  breakpoint: no hit; line 4 holds its original bytes.
- **Format.** After the load, `STG0AS.BIN` and WRAM-H differ in 10 bytes,
  all outside the dialogue table: `0x0609352D`-`0x06093532` (file `20 00 ..
  20 00`, RAM `2D 80 .. 2D 80`) and `0x060AB8C4`-`0x060AB8CA` (file `20 20
  00`, RAM `06 0B 88`, twice). They are the same in every state from 4493 to
  5386. At the three M1 checkpoints 29-30 bytes differ, all in
  `0x06092BE6`-`0x060AB8CA`, none in the table (`0x0606F01C`, 50,112
  bytes). Line 4 is at file offset `0xF09C` = address − `0x06060000`. The
  file's line pointers are absolute `0x0606xxxx` addresses (D-008) and are
  used as loaded: there is no relocation.
- **Copies at the M1 checkpoints.** A, B and C: `STG0AS.BIN` differs in
  30/29/29 bytes, `VICTORY.BIN` in 121,327, `END.BIN` in 285,494.
- Source manifests are unchanged, and so are both home configs.

## Conclusion

**CONFIRMED:**

- The M1 box's text is loaded when the first story stage starts, after
  machine select. It comes from `STG0AS.BIN` (LSN 22,538, 157 sectors).
- The load reads the CD block one sector at a time with an SH-2 longword
  copy at `0x06041F8C`, raw, to `0x06060000`, so file offset = RAM address −
  `0x06060000`. Line 4 is at file offset `0xF09C`.
- The game finds the file through its own copy of the ISO directory
  (file 292).

`STG0AS.BIN` is the resident copy in the M1 scene; `VICTORY.BIN` and
`END.BIN` were not seen loaded.

## Uncertainty and Alternatives

- The 10 changed bytes look like runtime values (two `0x2D80` halfwords, two
  24-bit `0x060B88` values) written into placeholders after the load. They
  are not traced. A same-size patch of the dialogue does not touch them.
- When `VICTORY.BIN` and `END.BIN` load (presumably after a win and in an
  ending) is not observed. It is left to `RE-002` and `END-001`.
- Whether the pick was already latched in state 4138 or made by the select
  timer is not distinguished. Either way it needs no input.
- The DMA transfer mode is not used here. Other loads may use it, and an SH-2
  write breakpoint would not see them.

## Reproduction

Run the procedure. Expect 14 hits at `0x06041FB4` in each trial, the Play
Disc command `1080 58A0 0080 009D`, and no hit in the control.
