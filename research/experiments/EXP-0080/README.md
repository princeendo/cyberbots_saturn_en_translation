# EXP-0080: Chiyomaru's New English, Drafted, Checked and Approved (SPECIAL-015)

Task: SPECIAL-015
Status: DONE
Confidence: CONFIRMED (coverage and fit by script; the user's approval,
verbatim). Not yet built or seen on screen (`SPECIAL-017`).

## Observation

List 7 (Chiyomaru) has 103 story boxes, 8 win quotes, 9 VS captions and 27
ending boxes (`data/text/special_census.json`); one ending box, 1072, is
the blank box the roster endings also open (D-065). His route is the one
`SPECIAL-010` found (three moves left of Jin); nothing else only an unlock
reaches is text (D-065: the unlock mech adds name art, decided apart).

## Hypothesis

Every list-7 box fits the box rules in arcade-toned English.

## Controlled Change

None to the game. A new text file, `data/translations/special_list7.json`.

## Prediction

147 boxes covered, all within 3 rows and 60 cells; box 1072 blank.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `STG0AS.BIN`, `END.BIN` | Untouched; hashes in the output |
| `data/text/special_census.json` | The boxes (`EXP-0076`) |
| The US arcade English | "Earth Corps", "Chiyomaru", "Captain Mary Miyabi" (the arcade's rank for Mary) |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| `research/experiments/EXP-0078/check_drafts.py` → [`fit_list7.json`](fit_list7.json) | `d76bd0d5…` → `8dd506f0…` | Coverage, characters, rows and cells |
| `research/experiments/EXP-0078/review.py` | `92c4c33e…` | The review page (local only) |

## Procedure

```bash
# Private: list 7's Japanese per box, in play order -> local/sp015/list7_ja.json (never committed)
# Drafts -> local/sp015/drafts.json (never committed)
./invenv.sh python research/experiments/EXP-0078/check_drafts.py local/sp015/drafts.json --list 7
./invenv.sh python research/experiments/EXP-0078/review.py local/sp015/drafts.json local/sp015/chiyomaru_review.html
# sent to the user; approval asked; then the English only:
./invenv.sh python research/experiments/EXP-0078/check_drafts.py data/translations/special_list7.json --list 7 \
  --out research/experiments/EXP-0080/fit_list7.json
```

2026-11-07, local.

## Actual Result

- **First check:** 147 boxes, 0 failures, at most 3 rows and 44 cells.
- **Names:** Tessan and Tatsunoshin (Chiyomaru's late father) by plain
  romanization; GOD as written in the Japanese.
- **Mary's rank:** the Saturn Japanese calls her lieutenant (少尉) in boxes
  832-838; the US arcade English calls her captain elsewhere. Asked; the
  user chose "Lieutenant (Recommended)".
- **The user's answers** (verbatim, 2026-11-07): "Approve all
  (Recommended)"; "Lieutenant (Recommended)".

## Conclusion

Prediction met. Chiyomaru's 146 text boxes have an approved English
translation in `data/translations/special_list7.json`; box 1072 stays
blank. With lists 6 and 8, every Saturn-only pilot's text is translated.

## Uncertainty and Alternatives

- Speakers on the page are inferred from context (the officers and
  soldiers are unnamed). The English does not depend on them.
- Glyph pairs and room: `SPECIAL-016`; on screen: `SPECIAL-017`.

## Later change

`SPECIAL-016` (`EXP-0081`): box 879 is open for only 57 frames; the approved
line would hold 18. The user chose "\"WHAT!?\" (Recommended)"; the file and
`fit_list7.json` (`f09e767f…`) were updated.
