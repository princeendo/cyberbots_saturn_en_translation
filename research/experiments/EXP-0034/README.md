# EXP-0034: What the M5 Roster Needs in Codes and Room; the Trade-Off

Task: CAP-001
Status: DONE
Confidence: CONFIRMED (the counts, from the game's tables and the arcade English; the compiler's options reproduce the old references); estimate (pilots 2-5 paired slot for slot, before `PAIR-003`); HYPOTHESIS (option c's 33 codes)

## Observation

Jin + Santana needed 73 sacrificed codes (`EXP-0029`). The M5 survey put
lists 0-5 at about 216 (`TASKS.md`, Phase J). After M5 the Japanese that
stays is the Saturn-only pilots', the endings', the VS captions' and the
Saturn-only win quotes', so a sacrificed code shows a wrong glyph there for
good.

## Hypothesis

Some option needs clearly fewer codes, or touches clearly fewer lines that
stay, than the current rule.

## Controlled Change

None to the game. Measurements over the same boxes, one option at a time.

## Prediction

Not stated in numbers beforehand; each option is measured.

## Inputs and Provenance

- `data/translations/jin_pairing.json`, `santana_pairing.json`;
  `local/cap001/pairing/{mary,arieta,gawaine,baomao}_pairing.json` from
  `EXP-0028/pair_pilot.py` (slot for slot, labelled an estimate: `PAIR-003`
  makes the real ones); `data/translations/win_quotes_pairing.json` (46
  roster quote boxes, D-030).
- The `cybotsu` program built from the ROM zips (English at `0x0B33AA`).
- `STG0AS.BIN`, `KANJI.BIN` of the untouched image.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`capacity.py`](capacity.py) | Pairs, codes and touched lines per option, story and win quotes in one pool → [`capacity.json`](capacity.json) (`5d249b75…`, line numbers only) |
| `tools/text/dialogue.py --budget` | The compiler's own budget; new options `--rank staying` and `--indent` |

Python 3.13.13.

## Procedure

```bash
for spec in 2:mary 3:arieta 4:gawaine 5:baomao; do p=${spec%%:*}; n=${spec#*:}
  ./invenv.sh python research/experiments/EXP-0028/pair_pilot.py \
    local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin \
    --pilot $p --boxes data/text/${n}_boxes.json --out local/cap001/pairing/${n}_pairing.json
done
P=(--pairing data/translations/jin_pairing.json --pairing data/translations/santana_pairing.json)
for n in mary arieta gawaine baomao; do P+=(--pairing local/cap001/pairing/${n}_pairing.json); done
C=(--font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp --rompath local/arcade)
./invenv.sh python -m tools.text.dialogue "${P[@]}" "${C[@]}" --out local/cap001/x --budget
./invenv.sh python research/experiments/EXP-0034/capacity.py "${P[@]}" \
  --quotes data/translations/win_quotes_pairing.json --kept 562 584 661 \
  --out research/experiments/EXP-0034/capacity.json
./invenv.sh python -m tools.text.dialogue "${P[@]}" "${C[@]}" --out local/cap001/x \
  --indent --rank staying --budget
# regression, default options:
./invenv.sh python -m tools.text.dialogue --pairing data/translations/jin_pairing.json \
  --pairing data/translations/santana_pairing.json "${C[@]}" --out build/cap001/js
./invenv.sh python -m tools.text.dialogue --pairing data/translations/jin_pairing.json \
  "${C[@]}" --out build/cap001/jin --max-sacrifice 18
```

2026-11-04, local; no emulator runs.

## Actual Result

### Budget (the compiler, story only, current rule)

404 boxes, 551 pairs; 310 unused codes and 25 new ones; **216** codes to
sacrifice (73 approved); 133 Japanese lines touched; text 23,812 bytes
against 25,272 of room (own lines less 3 kept lines, plus 159 dead ending
lines). The rows fit.

### Win quotes

The 46 roster quote boxes add 5 pairs (556 in all). Each quote is one row
of at most 15 cells. Their rows need 1,324 bytes; their own lines in
`VICTORY.BIN` hold 1,320. `VICTORY.BIN` shows only list 9 (its only post is
`0x14000009`, D-030), so its copies of the story lines are room too
(SUPPORTED, code only); `RE-008` places the quotes.

### Options (story and win quotes, `capacity.json`)

"Lines touched": lines that stay Japanese, that a box or a VS caption
shows, and that use a sacrificed code; of 1,050 such lines (806 Saturn-only,
165 roster endings, 81 captions, 3 kept, 5 other).

| Route | Pairs | (a) fewest lines | (b) fewest staying lines | (c) + (a) | (c) + (b) |
| --- | --- | --- | --- | --- | --- |
| as now | 556 | 221 codes, 133 lines | 221, 106 | 188, 118 | 188, 81 |
| (d) half-cell indent | 487 | 152, 101 | **152, 51** | 119, 77 | 119, 20 |
| (d) capitals | 450 | 115, 75 | 115, 16 | 82, 58 | 82, 0 |

- (b): rule b changes only which codes go: 106 lines instead of 133.
- (c): the table (`0x060AAD7C`, read through `0x0606EA40`) is followed at
  `0x060AB73C` by data that two literals (`0x0606A178`, `0x0606E478`) and a
  pointer table at `0x060AB870` (9 entries) read. Extending the table means
  moving that block or the 2,562-byte table, in `STG0AS.BIN` and in the
  copies of `VICTORY.BIN` and `END.BIN`. The 33 codes are an upper bound;
  not tested.
- (d) indent: 64 of 897 rows start with a space (half a cell in), chosen
  greedily so that rows share pairs; the words are unchanged. 69 fewer
  pairs.
- (d) capitals: the English drawn in capitals; changes the official text's
  look.
- With the touched lines grouped (indent + b): 43 Saturn-only, 3 roster
  endings, 5 captions.

### Decision

Asked (2026-11-04): "M5 needs 556 pair glyphs for the six pilots' stories
and win quotes (an estimate until PAIR-003), but only 335 codes are free.
The rest must take over codes of rare Japanese characters, and Japanese
lines that stay after M5 (mostly the Saturn-only pilots', plus a few roster
endings and VS captions) will show a wrong glyph wherever one is used. This
lasts, since that Japanese stays Japanese. Which trade-off?" The user's
answer, verbatim: "Indent + rank (Recommended)".

### Implementation

- `tools/text/dialogue.py`: `shift_rows` (the indent), `rank_codes` (rule
  `lines` or `staying`; shown = a scene's box or a caption box from
  `0x0609CC22`), options `--indent` and `--rank staying`, a cell check after
  the indent; the budget records both. Three synthetic tests
  (`tests/unit/test_dialogue.py`).
- Defaults unchanged: Jin + Santana rebuilt to `re007_jin_santana.json`'s
  hashes (STG0AS `cfe0945a…`, KANJI `bc414e4a…`, prediction `dd4b1235…`,
  Track 01 `a63ba806…`), and Jin alone to `re003_jin.json`'s (`41211301…`,
  `8fe36227…`, `394f745c…`). The builds were deleted afterwards.
- With `--indent --rank staying`, the compiler's budget for the six story
  pairings: 480 pairs, 145 codes, 52 lines touched (its count includes lines
  no box shows), text 23,904 bytes against 25,272.

The source image is unchanged.

## Conclusion

The roster needs about 152 sacrificed codes with the chosen option (story
and quotes; 221 under the old rule), touching about 51 shown lines that stay
Japanese instead of 133. The English fits the room. Final numbers come from
`PAIR-003`'s pairings and `RE-008`'s build.

## Uncertainty and Alternatives

- Pilots 2-5 are paired slot for slot here; `PAIR-003` may change a few
  boxes, and so the counts.
- Option (c) is untested and could be added later (119 codes, 20 lines with
  the indent); it is listed in `docs/known_unknowns.md`.
- The indent is greedy, not optimal; the rows indented depend on the set of
  boxes built.
- Whether a half-cell indent reads well on screen is checked in `RE-008`.

## Reproduction

Run the procedure; expect the numbers above and `capacity.json` byte for
byte.
