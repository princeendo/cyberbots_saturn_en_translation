# EXP-0078: Devilotte's New English, Drafted, Checked and Approved (SPECIAL-013)

Task: SPECIAL-013
Status: DONE
Confidence: CONFIRMED (coverage and fit by script; the user's approval,
verbatim). Not yet built or seen on screen (`SPECIAL-017`).

## Observation

`SPECIAL-012` set the method: Claude translates in the US arcade's tone;
one review page per pilot with a literal gloss; new names by US Capcom
conventions. List 6 (Devilotte) has 119 story boxes, 7 win quotes, 9 VS
captions and 15 ending boxes (`data/text/special_census.json`), none with
official English except shared items already English (D-066).

## Hypothesis

Every list-6 box can be put into arcade-toned English that fits the box
rules the roster's English uses, with only the arcade font's characters.

## Controlled Change

None to the game. A new text file, `data/translations/special_list6.json`.

## Prediction

150 boxes, all within 3 rows and 60 cells (captions 26 characters), no
character outside the arcade font.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `STG0AS.BIN`, `END.BIN` | Untouched (`local/extracted/saturn_jp`); hashes in the output |
| `data/text/special_census.json` | The boxes (`EXP-0076`) |
| The US arcade English (`cybotsu` `0x0B33AA`) | Terms: "Earth Corps" (14 uses), "cyberbot", "mistress" for Devilotte's henchmen; Devilotte appears as a guest there |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| [`check_drafts.py`](check_drafts.py) → [`fit_list6.json`](fit_list6.json) | `9dafb63d…` → `547b9c6c…` | Coverage, characters, rows and cells |
| [`review.py`](review.py) | `c8f42ddc…` | The review page (local only: it holds glosses) |

## Procedure

```bash
# Private: list 6's Japanese per box, in play order -> local/sp013/list6_ja.json (never committed)
# Drafts (speaker, gloss, English, notes) -> local/sp013/drafts.json (never committed)
./invenv.sh python research/experiments/EXP-0078/check_drafts.py local/sp013/drafts.json
./invenv.sh python research/experiments/EXP-0078/review.py local/sp013/drafts.json local/sp013/devilotte_review.html
# sent to the user; approval asked; then the English only:
./invenv.sh python research/experiments/EXP-0078/check_drafts.py data/translations/special_list6.json \
  --out research/experiments/EXP-0078/fit_list6.json
```

2026-11-07, local.

## Actual Result

- **The arcade font's characters** (`tools.font.pairs`): letters, digits,
  space and `! " ' , - . : ?` only. Hearts (`▼` in the Japanese), brackets
  and asterisks have no glyph: hearts are dropped and a bracketed aside
  becomes a quoted thought, each with a note.
- **First check:** 4 boxes wrapped to 4 rows (885, 932, 973, 996); each was
  shortened. **Final:** 150 boxes, 0 failures, at most 3 rows and 46 cells.
- **Names** (on the page for approval): Heldorado, the Dark Emperor,
  Castle/House Deathsatan, Princess Devilotte de Deathsatan IX, Ambassador
  Hell (her old retainer), Dr. Stein, Earth Corps, cyberbot, Demon Empress
  Lovely Devilotte.
- **Box 974** begins with Japanese line 661, which a roster box shares and
  whose official English is that box's (D-066). Box 974 gets its own
  English record in the build; line 661's English stays for the roster.
- **The user's answers** (verbatim, 2026-11-07): "Approve all
  (Recommended)"; for the retainer, "Ambassador Hell (Recommended)".

## Conclusion

Prediction met. Devilotte's 150 boxes have an approved new English
translation in `data/translations/special_list6.json`.

## Uncertainty and Alternatives

- Fit is by the wrap rule; the glyph pairs and room are measured in
  `SPECIAL-016` and the boxes are seen on screen only after `SPECIAL-017`.
- Speakers on the page are inferred from context (the boxes carry
  portraits, not names); a wrong guess does not change the English.

## Later change

`EXP-0079` taught both scripts boxes that keep official English
(`official_slot`); their hashes are now `d76bd0d5…` and `92c4c33e…`. List 6's
check output is unchanged (`fit_list6.json` `547b9c6c…`).
