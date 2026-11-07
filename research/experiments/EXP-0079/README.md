# EXP-0079: SHADE's New English, Drafted, Checked and Approved (SPECIAL-014)

Task: SPECIAL-014
Status: DONE
Confidence: CONFIRMED (coverage and fit by script; the user's approval,
verbatim). Not yet built or seen on screen (`SPECIAL-017`).

## Observation

`SPECIAL-013` (`EXP-0078`) set the drafting and review tools. List 8
(SHADE) has 117 story boxes, 7 win quotes, 9 VS captions and 17 ending
boxes (`data/text/special_census.json`). Two ending boxes, the speaker
names 601 and 605, have official English on the disc since M8 (D-047,
D-066).

## Hypothesis

Every other list-8 box fits the box rules in arcade-toned English; the two
names stay official.

## Controlled Change

None to the game. A new text file, `data/translations/special_list8.json`;
`check_drafts.py` and `review.py` learn boxes that keep official English
(`official_slot`, English null).

## Prediction

150 boxes covered; 148 new, all within 3 rows and 60 cells; 2 official.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `STG0AS.BIN`, `END.BIN` | Untouched; hashes in the output |
| `data/text/special_census.json` | The boxes (`EXP-0076`) |
| The US arcade English | "Captain Gawaine", "Ken" (Jin's father), "Earth Corps", "Chiyomaru"; SHADE's name as a man is never written |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| `research/experiments/EXP-0078/check_drafts.py` → [`fit_list8.json`](fit_list8.json) | `d76bd0d5…` → `77842abd…` | Coverage, characters, rows and cells |
| `research/experiments/EXP-0078/review.py` | `92c4c33e…` | The review page (local only) |

## Procedure

```bash
# Private: list 8's Japanese per box, in play order -> local/sp014/list8_ja.json (never committed)
# Drafts -> local/sp014/drafts.json (never committed)
./invenv.sh python research/experiments/EXP-0078/check_drafts.py local/sp014/drafts.json --list 8
./invenv.sh python research/experiments/EXP-0078/review.py local/sp014/drafts.json local/sp014/shade_review.html
# sent to the user; approval asked; name applied; then the English only:
./invenv.sh python research/experiments/EXP-0078/check_drafts.py data/translations/special_list8.json --list 8 \
  --out research/experiments/EXP-0079/fit_list8.json
./invenv.sh python research/experiments/EXP-0078/check_drafts.py data/translations/special_list6.json --list 6   # unchanged
```

2026-11-07, local.

## Actual Result

- **First check:** 3 boxes wrapped to 4 rows (615, 659, 746); shortened.
  **Final:** 150 boxes, 0 failures, at most 3 rows and 43 cells; boxes 601
  and 605 kept official (slots 610, 614).
- **SHADE's name as a man** (アイヒマン, about 25 boxes): the katakana
  spells the German surname that many readers link to Adolf Eichmann. Asked
  separately; the user chose "Aichmann (Recommended)" (same length, so the
  fit is unchanged; rechecked).
- **The user's answers** (verbatim, 2026-11-07): "Approve all
  (Recommended)"; "Aichmann (Recommended)".
- List 6's file still passes unchanged (`fit_list6.json` hash equal).

## Conclusion

Prediction met. SHADE's 148 new boxes have an approved English translation
in `data/translations/special_list8.json`; two names keep official English.

## Uncertainty and Alternatives

- Speakers on the page are inferred from context; a few are marked
  uncertain (boxes 681, 686). The English does not depend on them.
- Glyph pairs and room: `SPECIAL-016`; on screen: `SPECIAL-017`.
