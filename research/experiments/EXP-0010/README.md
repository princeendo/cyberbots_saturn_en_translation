# EXP-0010: The Saturn Script Against the Arcade Script

Task: REF-006
Status: DONE
Confidence: CONFIRMED (arcade Japanese map and record layout, line pairs, shared slot numbers for one scene); SUPPORTED (shared slot numbers for every scene, the Saturn-only block's content)

## Observation

The Saturn dialogue is 1,851 Shift-JIS lines (D-008). The arcade has a
494-slot Japanese table of 2-byte codes, not decoded, and a 624-slot English
table (D-009). `cybotsj`'s first box opens like Saturn line 0 (D-010), and
the arcade draw code passes one slot number to whichever table the region
selects.

## Hypothesis

The Saturn script reuses the arcade Japanese text line for line, so (1) the
arcade's character codes can be learned from the two scripts alone, (2) most
Saturn lines equal a line of an arcade Japanese record, and (3) the arcade
English slot with the same number is the official English for that record.

## Controlled Change

None to the game. Static analysis plus one headless MAME run of the untouched
`cybotsj` (run 7) to check (3).

## Prediction

A code map with no conflicting votes; most Saturn lines paired in order to
arcade lines; `cybotsj` reading the same slot numbers, at the same moments of
the same scene, as `cybotsu` did in `EXP-0009`.

## Inputs and Provenance

- Saturn `VICTORY.BIN` (SHA-256 `11ecc97d…d7f6`), lines 0-1850 (D-008).
- Arcade `cybotsj` program region from the held zips and the pinned driver
  (D-009); Japanese table at `0x0A30F6` (494 slots).

## Tools and Environment

`tools/text/arcade_pairing.py` (new, 6 unit tests on synthetic data); MAME
0.289 with `tools/reference/mame_timeline.lua` for run 7
([`timelines/run7-cybotsj.txt`](timelines/run7-cybotsj.txt)). Scratch
scripts first explored the layout (not committed).

## Procedure

```bash
./invenv.sh python -m tools.text.arcade_pairing \
  --driver local/mame_src/cps2.cpp --set cybotsj --rompath local/arcade \
  --saturn local/extracted/saturn_jp/VICTORY.BIN \
  --map-out data/text/arcade_jp_map.json \
  --out data/text/saturn_arcade_pairing.json
```

Run 7: `cybotsj` with `EXP-0009` run 2's input route to frame 3800, read
taps on the Japanese table, write log on the slot variable `0xFF2F7A`.

## Actual Result

- **Record layout.** Japanese records have the same 8-byte header as the
  English ones, then 16-bit big-endian codes (`0x10xx`-`0x14xx`), `0xFFFF`
  as a line break, ended by a word with high byte `0x00`. Record 0's two
  lines are 16 and 14 codes; Saturn lines 0 and 1 are 16 and 14 characters,
  and code `0x1018` sits exactly where `の` does, twice.
- **Map.** 579 distinct codes in 876 lines of 490 distinct records; 573
  mapped, **0 codes with conflicting votes**; 6 codes unmapped (`101B`,
  `1141`, `1229`, `1260`, `1383`, `13C6`), each in lines that have no
  identical Saturn line. Map: `data/text/arcade_jp_map.json` (code →
  Shift-JIS bytes).
- **Pairs** (`data/text/saturn_arcade_pairing.json`):
  - 787 Saturn lines equal an arcade line, in order (longest common
    subsequence); 38 more pair as edited lines (similarity ≥ 0.6) between
    paired neighbours: 825 paired lines in 450 arcade slots.
  - 449 of the 450 slots have their Saturn lines consecutive and in order;
    439 have every line paired, 11 only some.
  - Saturn lines with no arcade line: 74 in 50 short runs within lines
    0-898, and **one block of 952 lines, 899-1850**.
  - Arcade lines with no Saturn line: 51 (40 slots have no Saturn line at
    all, 2 of them empty).
- **The 952-line block** (corrected by `EXP-0011`: its first lines,
  899-952, are VS-screen chapter captions; Chiyomaru and Tessan appear only
  from line 1141). The names Chiyomaru (千代丸) and Tessan (鉄山)
  occur only there (16 and 8 lines); Devilotte, Gawaine, Arieta and others
  occur in both parts. Secondary sources say the console ports add four
  pilots (`docs/references.md`), so the block is **SUPPORTED** as their
  stories (and perhaps other Saturn-only scenes), with no arcade line and so
  no official English.
- **Run 7.** `cybotsj` writes slots 0, 1, 2, 3, 4, 5 to `0xFF2F7A` (from
  PC `0x011D30`, its copy of `cybotsu`'s `0x011D48`) at frames 2733, 2949,
  3196, 3387, 3578, 3754: the same slot sequence as `cybotsu` in the same
  scene. Japanese slot 0 (Jin's father's death a year ago) and English slot 0
  (an elite unit destroyed a year ago) are the same scene, freely localized.
- **Slot ranges.** Paired slots run up to 493; English slots 494-623 (130)
  have no Japanese record.

## Conclusion

**CONFIRMED:** the Saturn reuses the arcade Japanese script: 825 of its first
899 lines pair with arcade record lines, in order, through a code map learned
without conflicts. For the scene observed, both regions show the same slot
numbers, so a Saturn record's arcade slot is also its English slot; for all
other scenes this rests on the shared draw code and script (**SUPPORTED**).
Lines 899-1850 have no arcade counterpart.

## Uncertainty and Alternatives

- Only one scene's slot sequence was compared at runtime.
- The 38 edited pairs are similarity matches; each should be read before its
  English is used.
- The official English is a localization: a slot's English record is the
  translation by game logic, not a line-for-line rendering, and its line
  breaks differ from the Japanese record's.
- Why the English table has 130 more slots (the centered one-line records
  552-582 and speaker labels 600-623 among them) is open.
- The 952-line block's content is inferred from names, not from play.

## Reproduction

Run the procedure; expect the counts above and identical output files.
