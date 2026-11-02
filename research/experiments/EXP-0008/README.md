# EXP-0008: Locate and Decode the Arcade English Dialogue

Task: REF-003
Status: DONE
Confidence: CONFIRMED (location, table and record layout, letter/digit map, regional sameness); HYPOTHESIS (codes `09`, `0B`, `18`, `1C`; header meaning; which table each region shows)

## Observation

The arcade is the translation oracle (`docs/localization_policy.md`). A first
look (SESSION-0001) found no English dialogue as plain ASCII in the decrypted
US program ROMs `03`/`04`. MSHvSF's arcade English was 16-bit codes
(`A` = `0x0140`); XvSF's was a 16-bit tile-sheet layout. Both are only
hypotheses here. CPS-II encryption covers opcode fetches, so data reads as
stored.

## Hypothesis

Cyberbots' English story dialogue is stored as fixed character codes in the
68000 program region (`03`-`10`), findable by a relative search that assumes
nothing about the code values.

## Controlled Change

None; read-only analysis of the held zips (`REF-001`).

## Prediction

A constant-offset run for pilot names and common English words at 8- or
16-bit width, then a character map that decodes whole records with few or no
leftover codes.

## Inputs and Provenance

Zips in `local/arcade/` (`references/arcade/manifest.json`), set definitions
from the pinned MAME 0.289 `cps2.cpp` (SHA-256 `a8c09ef8…1602`). The
`maincpu` region (4 MiB) is rebuilt from the `ROM_LOAD16_WORD_SWAP` entries,
each 16-bit word swapped into 68000 order (the order in which the region
names at `0x8DB4` read as ASCII).

## Tools and Environment

Scratch scripts for exploration (not committed); then
`tools/reference/cybots_text.py` (new, 5 unit tests on synthetic images;
`find_member`/`build_program` copied unchanged from XvSF
`tools/reference/xvsf_text.py` at `a1c82ba`).

## Procedure

```bash
for s in cybotsu cybots cybotsj cybotsud cybotsjd; do
  ./invenv.sh python -m tools.reference.cybots_text --driver local/mame_src/cps2.cpp \
    --set $s --rompath local/arcade \
    --report local/ref003/report-$s.json --text-out local/ref003/text-$s.json
done
```

Exploration, in order:

1. Long ASCII runs (16+ characters) in the whole program: region names,
   test menu, exception names, legal notices. No dialogue.
2. Relative search (differences of consecutive values, so any constant
   offset matches) at 8- and 16-bit width: pilot names (`GAWAINE`,
   `SANTANA`, `ARIETA`, `DEVILOTTE`, `SHADE`) hit only at 8 bits with offset
   +9; common words (`YOUR`, `WITH`, `THAT`, `FATHER`, `BATTLE`) only at
   8 bits with offset +35. No 16-bit hits except two stray `WITH`.
3. The two offsets are one map in mixed case: capitals are ASCII + 9,
   lowercase ASCII + 3. Hits cluster at `0xB3F99`-`0xBB700`.
4. Context fixed the rest: `40`-`49` digits, `7E` `?`, `7F` `!`, `14` `.`,
   `1B` `,`, `F8` `'`, `F0` space, `FF` line break, `00` end. Accented
   letters (`F1`-`F5`), `¿`/`¡` (`89`/`8A`) and `ñ` (`8B`) occur in a
   Spanish block just before the English one.
5. Pointer tables: no long points at an individual text start; a run of
   624 longs at `0xB33AA` points 8 bytes before each text. That fixed the
   record layout.

## Actual Result

**Record.** Four big-endian 16-bit words, then one byte per character, then
`00` (zero-padded to an even address). The fourth word is always `000E`; the
first is `0000` or `0050`; the second and third vary (most often `007C 00A8`
and `005C 00A8`), like screen coordinates (meaning not established).

**Tables.** Every set has three tables of pointers to such records, found by
layout:

| Table (US/EU) | Slots | Distinct records | Records | Content |
| --- | ---: | ---: | --- | --- |
| `0x0A310A` | 494 | 490 | `0x0A3ACA`-`0x0AA8E8` | Japanese, 2-byte tile codes (`10 xx`, `11 xx`, …); Latin map covers 17%; not decoded |
| `0x0AB956` | 624 | 531 | `0x0AC316`-`0x0B339A` | Spanish; map covers 94% (15 other codes: accents, `¿`, `¡`, `ñ`, …) |
| `0x0B33AA` | 624 | 530 | `0x0B3D6A`-`0x0BB9A6` | **English**; map covers 99.87% |

- All three tables sit in the region ROM `03`/`04` area (`0x000000`-
  `0x0FFFFF`), not in the shared ROMs.
- **English:** 530 distinct records behind 624 slots (29 records are shared,
  one by 58 slots). At most 4 lines per record and 38 characters per line;
  773 lines exceed 25 characters. Slots 620-623 are speaker names followed by
  code `09`.
- **Leftover English codes** (counts in distinct records, with context):
  `09` 14 (after each pilot's or speaker's name: `:` is the HYPOTHESIS),
  `1C` 11 (at line ends such as "…never lose"), `18` 8 (on both sides of a
  word: `"` is the HYPOTHESIS), `0B` 2 (between two word parts: `-` is the
  HYPOTHESIS).
- **Punctuation, statistically:** `,` follows a letter 166/166 times, `'`
  252/252; `.` 423/578 (the rest inside `..` runs), `!` 246/296 and `?`
  119/129 (the rest after other punctuation, as in `?!`).
- **Regions:** in all five sets (`cybotsu`, `cybots`, `cybotsj`, `cybotsud`,
  `cybotsjd`) the three tables have identical record content (record-content
  SHA-256 prefixes `0b118d2d`, `a8a0bae1`, `2196c5dc`); in `cybotsj` they sit
  `0x14` bytes lower. The shared ROMs `05`-`10` are identical across sets;
  the region ROMs differ elsewhere. So every set, including Japan's, carries
  the same English, Spanish and Japanese dialogue.
- The four-pointer table at `0xBB9B6` (after the English records) points at
  zero-filled data.

## Conclusion

**CONFIRMED:** the arcade English dialogue is 530 records behind a 624-slot
pointer table at `0x0B33AA` (US/EU program region), one byte per character in
a tile-sheet map (`0x40` `0` … `0x4A` `A` … `0x64` `a` … `0x7F` `!`) plus
punctuation, decoded by `tools/reference/cybots_text.py` with four rare codes
left. Every held set carries the same English. MSHvSF's and XvSF's maps do
not apply.

## Uncertainty and Alternatives

- `09`, `0B`, `18` and `1C` are read from context only; rendering their
  tiles (MAME graphics or on-screen, `REF-004`) would settle them.
- That the arcade draws these records, which table each region selects, and
  whether endings are among the 624 slots are not observed (`REF-004`).
- The Japanese table (494 slots) is not decoded; pairing it with the English
  (624 slots) is not a simple index match (`REF-006`).
- The header words are not interpreted.

## Reproduction

Run the procedure; expect three tables per set with the record-content
hashes above and four unmapped English codes. Committed metadata:
`data/arcade/dialogue_tables.json`. Decoded text stays in the ignored
`local/ref003/`.
