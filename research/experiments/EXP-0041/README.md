# EXP-0041: Jin's Ending Paired With the Arcade English

Task: END-005
Status: DONE
Confidence: CONFIRMED (the pairing by both games' scripts and readers; five pairs on screen; rows, cells and codes); SUPPORTED (that lines no ending box shows are free room in `END.BIN`)

## Observation

- `END-003` (D-036) listed the boxes `END.BIN` opens for each ending list:
  Jin (list 0) posts scenes 16-19.
- `END-004` (D-037) read the arcade's ending scripts and readers. Its
  US English covers the dialogue, narration, captions and speaker names.
  The US cast roll has no Japanese line, and the arcade ending has no
  QSound notice.
- `END-002` (D-035) found the drawing paths:
  - the dialogue draws through the story's box path, with `END.BIN`'s code
    table and `SE.DAT`'s copy of `KANJI.BIN`;
  - the cast-roll names are images;
  - the QSound line is pixels.

## Hypothesis

Each Saturn box of Jin's ending, less the blank box 1072, has one arcade
slot at the same position of the same scene script, as in the story
(D-022). The arcade shows that slot's English while the Saturn shows the
box. Only the image surfaces have no official English. The English fits
the box limits, and the ending's own code table has enough free codes.

## Controlled Change

None to either game. The pairing and the capacity are static readings of
the two arcade programs and the untouched `END.BIN`, `SE.DAT`,
`STG0AS.BIN` and `KANJI.BIN`. The on-screen check reuses frames of forced
runs already recorded:
- Saturn: `local/end002/control` (EXP-0038), from the END-001 checkpoint
  `jin_ending_a16503.mcs`;
- arcade: `local/end004/mame/route-u` (EXP-0040), headless `cybotsu` with
  the round-end breakpoint.

## Prediction

- Each scene's Saturn boxes (without 1072) and arcade slots have the same
  count and order.
- Each pair's Japanese is the same or nearly so.
- The arcade reads each slot while the Saturn shows its box.
- No box exceeds 3 rows or 60 cells.
- Fewer than 335 pairs are needed (310 unused codes and 25 new ones, the
  story's rule).

## Inputs and Provenance

| Input | SHA-256 |
| --- | --- |
| `local/ref003/cybotsu-maincpu.bin` | `18e8827d…52fd` (as `jin_pairing.json`) |
| `local/ref003/cybotsj-maincpu.bin` | `2d1e6b25…928e` |
| `END.BIN`, `SE.DAT` (untouched image) | in `jin_ending_pairing.json` and `capacity.json` |
| `data/text/ending_posts.json` | `4aa3e3ae…` (EXP-0039) |
| `data/arcade/ending_scripts.json` | `20285407…` (EXP-0040) |
| `local/end002/control/route.json` | `5cc1a161…` (box open and close frames) |
| `local/end004/mame/route-u/reads-en-ptr.txt` | `f845ca1c…` (slot reads) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`pair_ending.py`](pair_ending.py) | Units, pairs and labels → `data/translations/jin_ending_pairing.json` (`6e9f2988…`; no text) |
| [`capacity.py`](capacity.py) | Rows, cells, pairs, codes and room → [`capacity.json`](capacity.json) (`985946d5…`; numbers only) |

Python 3.13.13; ffmpeg for the side-by-side frames (scratch only).

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0041/pair_ending.py \
  local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
  --out data/translations/jin_ending_pairing.json
./invenv.sh python research/experiments/EXP-0041/capacity.py \
  local/ref003/cybotsu-maincpu.bin --out research/experiments/EXP-0041/capacity.json
```

On screen: the Saturn frame is taken while the box is open (its open and
close words in `route.json`). The arcade frame is taken between the
reader's two reads of the slot (`0x011F6A`, then `0x012014`, in
`reads-en-ptr.txt`). The agent placed each pair side by side and reviewed
it.

2026-11-05, local; no emulator run, no key pressed.

## Actual Result

### Pairing (`jin_ending_pairing.json`)

31 units:
- 18 dialogue units paired with a slot (15 `exact`, 3 `edited`);
- 13 `no-counterpart`.

Every scene's boxes and slots matched in count and order.

| Scene | Surface | Saturn boxes → arcade slots | Lines |
| --- | --- | --- | --- |
| 16 | Dialogue box | 1072 (blank), 408, 409, 493, 410, 411, 412 → —, 408, 409, 493, 410, 411, 412 | 10 |
| 17 | Dialogue box | 1072 (blank), 413 → —, 413 | 1 |
| 18 | Narration | 414, 415 → 414, 415 | 4 |
| 19 | Captions and speaker names | 605, 416, 417, 418, 601, 419, 420, 421, 422 → 614, 416, 417, 418, 610, 419, 420, 421, 422 | 15 |

Of the 30 dialogue lines, 27 are `exact` against the `cybotsj` slot's
Japanese. The 3 `edited` lines have the same wording:
- **Box 408:** the arcade writes its two ellipses as middle dots
  (similarity 0.812).
- **Boxes 605 and 601 (speaker names):** the arcade name uses code
  `0x549`, which `arcade_jp_map.json` does not map. It stands where the
  Saturn has a full-width colon, and the US record ends in a colon
  (0.833, 0.667).

Against slots 605 and 601, the slots with the boxes' own numbers, the same
lines score 0.0 and 0.083: those slots hold other text.

The arcade's English for some boxes (for example 493, 416 and 419) is a
free localization, not a translation of the Japanese. It is still the
official English the policy uses (`docs/localization_policy.md`).

No-counterpart units:

| Unit | Count | Why there is no English | Handling (the user, 2026-11-05) |
| --- | --- | --- | --- |
| Box 1072 | 2 (scenes 16, 17) | A full-width space; the arcade opens no slot | Nothing to show |
| Cast roll, Japanese name images | 10 | Sprites decoded from `KEND_1.BIN` (D-035). The same 10 entries and Latin names show in both games. `cybotsu` draws no line over the Latin name; `cybotsj` draws Japanese as the Saturn does | "Hide, as US arcade (Recommended)" |
| QSound notice, Japanese line | 1 | Pixels of `QSD.PIX`, bitmap rows 180-189 (D-035). It says QSound is a registered trademark of QSound Labs, as the English lines above it do. The arcade ending has no QSound notice | "Erase the line (Recommended)" |

So no unit needs new text.

Shared boxes: the speaker-name boxes 605 and 601 (lines 1010 and 1006) are
also posted by lists 3, 4 and 8. Box 1072 is posted by lists 1-5 and 7. No
other box or line of Jin's ending is used by another ending.

### On screen (agent-reviewed)

| Pair | Saturn frame (box open) | Arcade frame (slot read) | Review |
| --- | --- | --- | --- |
| 408 = slot 408, dialogue | `f01791` (1635-1828), `795f89ad…eb0f` | `cybotsu_f09380` (9273-9413), `c92fb5fa…a678` | Same background and portrait. Jin says he remembers everything, in Japanese and in English |
| 493 = slot 493, dialogue | `f02341` (2100-2368), `d8fb3866…dcd3` | `cybotsu_f10040` (9753-10076), `eee8a62e…f130` | Same scene. Both lines are about his best friend: the Saturn names him Saotome, the English calls him Ken (free localization) |
| 414 = slot 414, narration | `f03551` (3217-3607), `7242307e…dde8` | `cybotsu_f11210` (10949-11234), `2161fa40…9b81` | White text on black. Both say Shade's explosion changed the falling power station's path |
| 605 + 416 = slots 614 + 416, caption | `f03991` (3819-4027), `0aa5ab86…5767` | `cybotsu_f11750` (11598-11778), `a6b5c499…d8e5` | Same picture. Gawaine's name leads the line in both; the English is a free localization. The arcade wraps its second row under the caption column |
| 601 + 419 = slots 610 + 419, caption | `f04926` (4749-4957), `6b2797cb…733a` | `cybotsu_f12260` (12210-12285), `11ef6f7f…e3ae` | Same picture. Jin's name leads in both; the English is shorter |

Speaker names open with their caption in both games: Saturn 605 at 3817
with 416, and 601 at 4747 with 419; arcade 614 at 11596 with 416, and
610 at 12208 with 419.

### Capacity (`capacity.json`)

| Measure | As is | With the half-cell indent | Limit and evidence |
| --- | --- | --- | --- |
| Rows a box | at most 3 | at most 3 | 3 (records hold 3 lines in place, D-023) |
| Glyph cells a box | at most 45 (box 409) | at most 46 | 60 (`0x060FE200`, D-020; the ending uses the same cells, D-035). A name stays open over its captions (605 over 416-418, 601 over 419-420); together at most 33 |
| Cells a row | at most 16 | at most 16 | The widest Saturn line of each surface: story box 16, narration 16, caption 16, name 6. No row is wider |
| Distinct pairs | 179 | 160 | 310 unused codes + 25 new = 335 by the story's rule; 801 if only the lines the ending shows count |
| Sacrificed Japanese codes | 0 | 0 | — |
| Row bytes | 872 | 880 | Jin's own ending lines: 828 bytes (not enough alone). Lines no ending box shows: 44,124 bytes |

The code table and font are the ending's own:
- `END.BIN`'s code table (file `0x26EAC`) equals `STG0AS.BIN`'s: 1,222
  codes.
- `SE.DAT` `0x40000`-`0x67FFF` equals `KANJI.BIN`.
- The M5 image changed neither file, so the story's sacrificed codes and
  pair glyphs are not in the ending's table or font. The ending's pairs
  need their own codes there.

## Conclusion

Prediction met. Jin's ending pairs box for slot by both games' scripts:
- 18 dialogue units have official English (15 exact, 3 with the same
  wording);
- the speaker names are the slot − 9;
- the 13 units without English are the blank box, the 10 cast-roll name
  images and the QSound line. The user chose to hide the name images and
  erase the line, as the US arcade has neither.

The English fits:
- 3 rows and 60 cells a box, 16 cells a row;
- no sacrificed code;
- the room needs lines beyond Jin's own.

## Uncertainty and Alternatives

- **Room.** That `END.BIN` never reads the lines no ending box shows is
  SUPPORTED by its posts and scripts only. Jin's own lines (828 bytes)
  are 44 bytes short. M7 must check the room it uses, or find other room.
- **Caption rows.** The width of caption rows 2-3 on the Saturn (where they
  start) is not measured. The arcade starts them under the caption
  column.
- **Shared name boxes.** Changing 605 and 601 also changes the names in
  lists 3, 4 and 8, whose other text stays Japanese until M8.
- **Hiding the cast names.** No method is tested yet: `KEND_1.BIN`'s format
  is not decoded (D-035). A VDP1 command change or a shadow change are the
  candidates.

## Reproduction

Run the procedure. Expect both data files byte for byte, and the frames in
the on-screen table with their hashes.
