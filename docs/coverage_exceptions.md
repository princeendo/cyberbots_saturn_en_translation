# Coverage and Exceptions

The register for M5 (`RE-005`). Endings (M6-M8) get their own section when
those milestones begin.

## M5 Roster

Decided by the user on 2026-11-04 (`RE-005`). Question: "Which pilots make
up the M5 roster? The six arcade pilots (Jin, Santana, Mary, Arieta,
Gawaine, Bao and Mao) have 404 story boxes plus 46 win-quote boxes, all with
official arcade English except Mary's line 258. The three Saturn-only
pilots (lists 6-8, e.g. Devilot and Shade) add 339 story boxes with no
official English and are special cases under rule 24." Answer, verbatim:
"Six arcade pilots (Recommended)".

### In Scope

`data/text/m5_roster.json`: pilot lists 0-5, each list's story scenes (its
block of `STG0AS.BIN`'s scene posts) and the pilot's versus win quotes.

| List | Pilot | Story scenes | Boxes | Lines | Box file |
| --- | --- | --- | --- | --- | --- |
| 0 | Jin | 17 | 63 | 120 | `jin_boxes.json` (story scenes from D-021) |
| 1 | Santana | 20 | 64 | 117 | `santana_boxes.json` |
| 2 | Mary | 18 | 69 | 119 | `mary_boxes.json` |
| 3 | Arieta | 21 | 66 | 127 | `arieta_boxes.json` |
| 4 | Gawaine | 17 | 70 | 137 | `gawaine_boxes.json` |
| 5 | Bao and Mao | 21 | 72 | 136 | `baomao_boxes.json` |

Win quotes: the 46 boxes that the quote table's rows 0-5 reach
(`data/translations/win_quotes_pairing.json`, `roster_quote_boxes`; D-030).

### Excluded, With Evidence

| What | Boxes / lines | Evidence | Why |
| --- | --- | --- | --- |
| Pilot lists 6-8 (Saturn-only pilots: list 6 is one move left of Jin, Devilot by the name art; list 8 two moves left, Shade by the name art; list 7 not played) | 339 story boxes; lines 1020-1215, 1249-1445, 1510-1751 and others | `data/text/pilot_census.json` (no line paired with an arcade slot); cold boots `left1`, `left2` (`EXP-0033`) | No official English; special cases (rule 24, `SPECIAL-001`) |
| Their win quotes (quote-table rows 6-8) | boxes 1023-1044, lines 1790-1821 | D-030 | Same |
| Ending scenes of every list | each list's posts in `data/text/ending_posts.json` (replaces `ending_scenes_by_number`, which listed unposted scenes) | `END.BIN`'s routine for the winner's pilot posts them (`EXP-0039`, D-036) | M6-M8 (rule 23) |
| List 10 | 7 scenes of speaker-name boxes 602-605 and 609 (lines 1007-1010, 1014) | No Saturn file holds a list-10 post; the arcade's list 7 is the same and is posted at `0x6319C` (`EXP-0033`) | Never shown by the Saturn as far as the code shows |
| Mary's and Gawaine's scene 15 | none of their own: the same boxes as scene 14 | Scene 15 is not in either pilot's block; Mary's scene 15 is scene 14's script, Gawaine's a copy of it | Nothing to translate beyond scene 14 |
| Win-quote box 555 (line 956) | 1 box | No quote-table entry names scene 1 (D-030) | Never shown |
| VS-screen chapter captions | boxes 494-549 (lines 899-952) | `STG0AS.BIN` `0x0606CAE8` (`EXP-0032`) | A separate surface; the US arcade shows none (`EXP-0012`); outside M5 unless the user adds it |

### For the Gate

- ~~Mary's line 258 (box 140) has no arcade counterpart (D-011): a new
  translation.~~ Corrected 2026-11-04 (`PAIR-003`, D-032): line 258 is slot
  140's second line, edited; slot 140's English covers it. No roster line
  needs a new translation.
- Win quotes: the two Japanese quotes of a level share one US line (22 pairs
  of boxes, D-030).
- Lines a roster box shares with another list's box (the census's
  `lines_shared_with_other_lists`: Jin 57, 75; Santana 144; Arieta 386;
  Gawaine 57, 144, 538, 562, 584; Bao and Mao 75, 386, 538, 661). A shared
  line changed for one pilot changes for the other; line 661 is also in
  list 6's box 974.
