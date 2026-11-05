# EXP-0047: The Roster Endings Paired With the Arcade English

Task: END-021
Status: DONE
Confidence: CONFIRMED (the pairing of every unit of lists 1-5; the box kinds from the record header); the choice for box 608 is the gate's

## Observation

- `END-020` (D-043) recorded the boxes each roster ending is seen to open
  and the slots each arcade set's story reader reads in a forced run of the
  same ending (`data/text/ending_surfaces.json`).
- `END-005` paired Jin's ending scene by scene with
  `EXP-0041/pair_ending.py`, labelling surfaces by Jin's scene numbers.

## Hypothesis

In every roster ending, the Saturn's openings (less the blank 1072) and the
arcade's slot reads are the same sequence:
- dialogue box N is slot N;
- each speaker name stands where the arcade reads a name slot;
- each box pairs with one slot everywhere.

The box record's header tells the kinds of box apart.

## Controlled Change

None. Static readings of `END.BIN`, the two arcade programs and the
recorded runs; the on-screen pairs reuse `EXP-0046`'s frames.

## Prediction

- Every list's sequences align with no conflict, and `cybotsj` reads the
  same slots as `cybotsu`.
- List 0 reproduces `jin_ending_pairing.json`'s units.
- One pair per list shows the same picture and speaker in both games.

## Inputs and Provenance

| Input | SHA-256 / notes |
| --- | --- |
| `local/ref003/cybotsu-maincpu.bin`, `cybotsj-maincpu.bin` | as EXP-0041 |
| `data/text/ending_surfaces.json` | EXP-0046 |
| `END.BIN` (untouched) | `a4868d8d…f3fa` |
| `data/text/arcade_jp_map.json`, `data/text/script_census.json` | as before |

## Tools and Environment

`tools/text/ending_pairing.py` (new; generalized from
`EXP-0041/pair_ending.py`, commit `ea2e69c`), Python 3.13.13; ffmpeg for
the side-by-side frames (scratch only).

## Procedure

```bash
P="./invenv.sh python -m tools.text.ending_pairing local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin"
$P --list 1 --out data/translations/santana_ending_pairing.json
$P --list 2 --out data/translations/mary_ending_pairing.json
$P --list 3 --out data/translations/arieta_ending_pairing.json
$P --list 4 --out data/translations/gawaine_ending_pairing.json
$P --list 5 --out data/translations/baomao_ending_pairing.json
$P --list 0 --out /tmp/jin.json   # compared with jin_ending_pairing.json
```

2026-11-05, local; no emulator run.

## Actual Result

### Box kinds (the record header)

Each box record in `END.BIN` (table `0x060817B4`) starts with 4 words:

| Kind | Header | Boxes seen |
| --- | --- | --- |
| Dialogue box with portrait | `0000 008C 00AC 000E` | 1072, 408-413, 423-424, 437-439, 448-452, 479-480 |
| Narration | `0000 0050`/`0070 0050 000E` | 414-415, 430-431, 455, 473-474 |
| Caption | `0030 0088 00AC 000E` (`0x30`: the caption column) | 416-422, 425-429, 432-436, 440-447, 453-464 (less 455), 465-472, 475-478, 481-492, 551 |
| Speaker name | `0000 0028`-`004C 00AC 000E` | 601-614 |

They agree with Jin's scene-based labels and with every screen reviewed in
`EXP-0046`, including Gawaine's caption 472, which has no name.

### Alignment

| List | Pilot | Saturn openings / arcade reads | Units | Exact | Same wording | No counterpart | No official English |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Jin | 20 / 20 | 31 | 15 | 3 | 13 | 11 (images) |
| 1 | Santana | 23 / 22 | 22 | 13 | 8 | 1 (1072) | 0 |
| 2 | Mary | 16 / 16 | 15 | 11 | 3 | 1 (1072) | 0 |
| 3 | Arieta | 26 / 26 | 24 | 14 | 9 | 1 (1072) | 0 |
| 4 | Gawaine | 20 / 20 | 17 | 12 | 5 | 0 | 0 |
| 5 | Bao and Mao | 27 / 27 | 28 | 13 | 14 | 1 (1072) | 0 |

- `cybotsj` reads the same slots as `cybotsu` in every list.
- Every box pairs with one slot: dialogue box N with slot N. Speaker names
  pair with arcade name slots, by D-038's rule (box + 9) except box 608.
- Mary's run-on scenes (440-447, D-043) and Bao and Mao's 486 pair like any
  other box.
- **"Same wording" (`edited`), checked by the agent line by line** (not
  committed):
  - punctuation: `!?` where the arcade has `？`;
  - the arcade's unmapped colon code `0x549` in names;
  - unmapped arcade kanji codes: `0x1383` and `0x13C6` in box 613's name,
    `0x101B` in box 464.

  No edited pair differs in meaning.
- **List 0** reproduces `jin_ending_pairing.json`'s 31 units: same order,
  boxes, slots, labels, similarities and English hashes. The differences
  are a new `evidence` wording on the 18 dialogue units (the observed runs
  in place of the posted scripts) and a new `name_rule_slot` field on the
  two name units. The committed file is kept, since END-010's build and
  records cite it.

### The cases

- **Box 603, list 1 (scene 22).** The Saturn opens 603 ("Santana", slot 612
  everywhere else) once more, before caption 435, where the arcade opens no
  name. Caption 435 is `exact`. Box 603 has official English, and the extra
  opening shows that same English name; the file records
  `openings_without_an_arcade_slot: 1`. No new text.
- **Box 608, list 5 (scenes 18, 19, 28).** The Saturn names both twins.
  - At the same place the arcade shows slot 615, Bao alone, whose Japanese
    is a different name (similarity 0.444).
  - Slot 617, box + 9 as for every other name, holds the same two names in
    Japanese (`edited`, the colon code only), with its own official
    English.
  - Both are official English; which one shows is for the gate (the file
    records both: `arcade_slot` 615 and `name_rule_slot` 617).
- **Box 606, list 3 and 5** is Bao alone, slot 615 by both the place and
  the rule.

### On screen (agent-reviewed, `EXP-0046` runs)

| List | Box (slot) | Saturn shot | Arcade snapshot | Review |
| --- | --- | --- | --- | --- |
| 1 | 425 (425), after name 603 | `list1/f02116` `ee9c50ef…7cda` | `cybotsu_f09860` `65a6aac7…` | Same picture; Santana's caption in both; the English is a free localization |
| 2 | 440 (440), Mary's run-on scene | `list2/f02287` `af8e197e…22f4` | `cybotsu_f09950` `b3eecd77…` | Same picture; Chiyomaru's caption in both |
| 3 | 456 (456), after name 606 | `list3/f03771` `2e5584ab…c0c7` | `cybotsu_f11330` `e5837b77…` | Black screen; Bao waking Arieta in both |
| 4 | 466 (466), after name 601 | `list4/f02119` `d5fe58a8…0c76` | `cybotsu_f09710` `3c8fd300…` | Same picture; Jin's caption in both |
| 5 | 482 (482), after name 608 | `list5/f02338` `767321b7…0517` | `cybotsu_f09920` `21f61d45…` | Same scene; the Saturn's name is both twins, the arcade's Bao alone (the 608 case) |

## Conclusion

Prediction met. Every text unit of lists 1-5 has official English at the
same place in the arcade:
- 102 text units, plus four blank 1072 units, with no new translation
  needed;
- the box kinds come from the record header;
- `tools/text/ending_pairing.py` reproduces Jin's pairing.

One choice is for the gate: box 608 can show the English of the slot at the
same place (615, one twin) or of the slot with the same Japanese (617, both
twins).

## Uncertainty and Alternatives

- The alignment rests on one forced run per list; the posts and box
  sequences are constant code and script (D-036, D-043).
- The header rule covers the four headers seen in lists 0-5 and fails on
  any other.

## Reproduction

Run the procedure. Expect the five pairing files byte for byte and the
results above.
