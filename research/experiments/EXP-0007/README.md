# EXP-0007: Static Census of the Shift-JIS Script Blocks

Task: TXT-001
Status: DONE
Confidence: CONFIRMED (file contents); HYPOTHESIS (what the game draws)

## Observation

SESSION-0001 found about 1,760 Shift-JIS strings in each of `END.BIN`,
`VICTORY.BIN` and `STG0AS.BIN`, with the same opening lines at different
offsets and slightly different character counts, after an ASCII `SsCB`
marker. Whether the three copies are identical, how strings are delimited,
and what addresses them were unknown.

## Hypothesis

The three files hold one shared table of NUL-terminated Shift-JIS lines,
addressed by 32-bit pointers from the same files at a common load address;
no other file on the data track holds such a table.

## Controlled Change

None. Static analysis of the extracted files (`local/extracted/saturn_jp/`,
264 files from track 01, `ENV-006`); the source image is not read.

## Prediction

One block per file of aligned NUL-terminated lines; equal line sequences in
the three files; a load base at which nearly every line has a pointer; no
block elsewhere.

## Inputs and Provenance

The 264 files extracted by `tools.disc.iso9660 --extract` in SESSION-0001
(hashes in `references/saturn_jp/iso_listing.json`): `END.BIN`
`a4868d8d…`, `STG0AS.BIN` `3fabb4db…`, `VICTORY.BIN` `11ecc97d…` (full hashes
in `data/text/script_census.json`).

## Tools and Environment

`tools/text/script_census.py` (new, 9 unit tests on synthetic data). It finds
blocks by layout (4-byte-aligned, NUL-terminated, zero-padded Shift-JIS
lines, mostly double-byte, at least one line of 4+ characters), brute-forces
a 256-byte-aligned load base in WRAM-H and WRAM-L that maximizes 32-bit words
pointing at line starts, and writes offsets, lengths, 16-hex-digit SHA-256
prefixes and reference counts, never text. Hand exploration used scratch
scripts first (not committed).

## Procedure

```bash
./invenv.sh python -m tools.text.script_census local/extracted/saturn_jp/* \
  --out data/text/script_census.json
```

## Actual Result

Run 2026-11-02 15:09 local, about 2 s for 264 files.

- **Blocks.** Only `END.BIN`, `STG0AS.BIN` and `VICTORY.BIN` have one. A first
  run without the longest-line rule also matched `SELECT.VAD` (120 "lines" of
  `AA`/`BB`/`CC` bytes) and `ST08_FNT.BIN` (16 lines of at most 3 half-width
  characters): graphics data; the rule (`--min-longest 4`) was added for them.
  `CYB_ABS.TXT` (the ISO abstract file) holds Japanese in newline-separated
  form and is not a block (SESSION-0001).

| File | Block | Lines | Load base | Pointer words | Lines pointed to |
| --- | --- | ---: | --- | ---: | ---: |
| `VICTORY.BIN` | `0x01CE8`-`0x0E0BC` | 1,855 | `0x06060000` | 1,878 | 1,854 |
| `END.BIN` | `0x0AECC`-`0x175A4` | 1,927 | `0x06060000` | 1,933 | 1,909 |
| `STG0AS.BIN` | `0x0F01C`-`0x1B3DC` | 1,852 | `0x06060000` | 1,875 | 1,851 |

- **Format.** Each line starts on a 4-byte boundary, ends with one `00`, and
  is zero-padded to the next 4-byte boundary. No control bytes occur inside
  lines: each string is one line. The block is preceded by ASCII string
  literals (file names, `SsCB`), as in a compiled program's constant data.
- **Shared dialogue.** The first 1,852 lines have equal hashes in all three
  files, and those 50,112 bytes are byte-identical (SHA-256 prefix
  `f69902f8d27f98d2`). Line 1,852 (index 1851) is the ASCII literal `SsCB`;
  lines 0-1850 are the 1,851 dialogue lines (44,336 bytes). After them,
  `VICTORY.BIN` has 3 more ASCII literals and `END.BIN` 75 (file names).
- **Pointers.** At base `0x06060000`, every dialogue line (0-1850) is pointed
  to in each file; 19 lines are pointed to more than once. The pointer words
  are 4-byte aligned and lie after the block (in `VICTORY.BIN`, 3 before it
  and 1,875 from `0xFF64` to `0x18484`), spaced mostly 8, 16, 24 or 32 bytes
  apart (810, 181, 447, 435 gaps), and their targets rise in file order:
  records, not a flat table. A sample record reads
  `00 8C 00 AC 00 0E 06 06 27 BC FF FF 00 00 06 06 27 D0`: small numbers, a
  line pointer, `FFFF 0000`, another line pointer (meaning not established).
- **Characters** (dialogue lines): at most 16 full-width characters, or 25
  characters counting half-width ones; at most 34 bytes (half-width cells),
  32 for all but one line. 909 distinct double-byte characters, 729 of them
  kanji (lead byte `0x88` or higher). Single-byte characters inside dialogue:
  ASCII space (140), `!` (47), `?` (45), and the letters of a few words
  (`D`, `r`, `S`, `s`, `C`, `B`).

## Conclusion

**CONFIRMED as file facts:** the three program files, each loaded at
`0x06060000` judging by their pointers, carry one byte-identical table of
1,851 NUL-terminated Shift-JIS dialogue lines, each line pointed to by
32-bit addresses in record-like structures after the table; no other file on
the data track has such a table. That the game draws these lines, which file
is resident when, and what the records mean are **HYPOTHESIS** until a
runtime test (`DBG-004`, `DISC-001`, `RE-002`).

## Uncertainty and Alternatives

- The load base is inferred from pointer counts, not observed in RAM.
- Half-width ASCII inside dialogue suggests the renderer handles single-byte
  characters; that is a lead for `FONT-002`, not a finding.
- One line is 34 bytes while the rest are at most 32: a box-width exception,
  or a line that wraps. Not checked.
- Lines pointed to more than once may be shared between pilots or routes.

## Reproduction

Run the procedure; expect `data/text/script_census.json` byte-identical to
the committed file (same extracted files, same tool).
