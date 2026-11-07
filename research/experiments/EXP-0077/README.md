# EXP-0077: No Official English for the Saturn-Only Pilots (SPECIAL-011)

Task: SPECIAL-011
Status: DONE
Confidence: CONFIRMED (the arcade's six-pilot bounds by code and data in
both sets; no Saturn-only box has an arcade counterpart, by a test that
matches all 61 of Jin's multi-line boxes)

## Observation

`SPECIAL-010` (`EXP-0076`, D-065) listed the text of lists 6-8: 339 story
boxes, 22 win quotes, 27 captions and three endings. The policy asks that
the absence of official English be shown by tracing the arcade's code, not
only by a data search (`docs/localization_policy.md`, 2026-11-02).

## Hypothesis

The arcade has no table, list or route for a pilot beyond 5, and no arcade
record holds any Saturn-only box except those already shared with the
roster.

## Controlled Change

None. Static reading of both arcade sets and a comparison of every
Saturn-only line with every arcade Japanese record, with Jin's lines as
the control.

## Prediction

Six-pilot bounds everywhere; only the shared items (line 661, the speaker
names of boxes 601 and 605) match.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `local/ref003/cybots{u,j}-maincpu.bin` | Data images (`18e8827d…`, `2d1e6b25…`) |
| `local/win002/mame/cybotsu-0-c0000.asm`, `local/end004/mame/dasm-j/cybotsj-0-c0000.asm` | Listings |
| `data/text/special_census.json` (`2f0b2a0d…`) | The lines (`EXP-0076`) |
| `data/text/arcade_jp_map.json`, `data/text/jin_boxes.json` | Code map (`REF-006`), control |
| `local/extracted/saturn_jp` | `STG0AS.BIN`, `END.BIN` |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| [`official.py`](official.py) → `data/text/special_official.json` | `67433ed6…` → `b674cbfd…` | Bounds, line and box matching, control |
| `research/experiments/EXP-0075/thanks.py` `every_scene` | | Every arcade scene's slots |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0077/official.py
grep -n -A8 '^00CD80:' local/win002/mame/cybotsu-0-c0000.asm   # the select ring's reader
```

2026-11-07, local. No emulator run.

## Actual Result

### The arcade has six pilots (both sets)

| Where | What |
| --- | --- |
| Pilot select `0xCD80`-`0xCDB8` | Left and Right step through `(left, right)` pairs at `0xCE00` (read through `A0`, so plain data): `03 02 02 04 00 01 05 00 01 05 04 03`, a ring of pilots 0-5 only; the same bytes in `cybotsu` and `cybotsj` |
| Scene scripts (`0x12150` / `0x12138`) | Eight lists: 0-5 the pilots (22, 27, 22, 29, 22, 29 scenes), 6 the win quotes (48 = 6 pilots × 8), 7 the thank-you screen (7, D-064) |
| Endings | Six dispatch entries (`0xE496` / `0xE480`, D-037) |
| Win quotes | `0x630CE` for pilots 0-5 (D-030) |

So the arcade has no story, quote, caption or ending path for a seventh to
ninth pilot. SHADE appears only inside pilots 0-5's stories, as the boss.

### Line and box matching

- **Control:** Jin's 152 story lines: 143 exact, 8 edited (ratio at
  least 0.6), 1 below. Jin's 61 boxes of two or more lines: **61 of 61**
  match one arcade record line for line.
- **Saturn-only lines:** 809 distinct lines (9,487 characters) of story,
  win quotes, captions (`STG0AS.BIN`) and endings (`END.BIN`). One exact
  match and 67 partial matches (ratio 0.6-0.91), searched across all 624
  slots in any order; the best unmatched line reaches 0.588.
- **Saturn-only boxes:** **0 of 259** multi-line boxes match one arcade
  record line for line.
- **Read** (the 14 strongest, privately; no text committed): every partial
  match is a short shout, name or stock phrase found inside a different,
  longer arcade line or in another character's scene. They are
  coincidences, not counterparts.

### What already has official English

| Saturn line | Where | Arcade | On the disc now |
| --- | --- | --- | --- |
| `STG0AS.BIN` 661 | list 6's story (and the roster's) | slot 359, exact | English since M5 (the roster box shares it) |
| `END.BIN` 1006, 1010 | list 8's ending, speaker names (boxes 601, 605) | slots 610, 614 | English since M8 (D-047) |
| (box 1072, list 7's ending) | blank | — | blank |

All other 806 lines need a new translation.

## Conclusion

Prediction met. The arcade's code has room for six pilots only, and no
arcade record is a counterpart of any Saturn-only box. Of the Saturn-only
pilots' 809 lines, the three with official English are already English on
the disc; the remaining 806 (about 9,470 characters) are a new translation
under the user's policy.

## Uncertainty and Alternatives

- The comparison runs through a learned code map; a few arcade characters
  have no mapping (`REF-006`), which can only lower a ratio. The box test
  does not depend on single characters, and its control passed fully.
- Official English outside the arcade (later Capcom releases) is not in
  scope: the arcade is the only oracle (`REF-002` rejected, 2026-11-02).
