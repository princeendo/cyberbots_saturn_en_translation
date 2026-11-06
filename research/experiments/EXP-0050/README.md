# EXP-0050: All Roster Endings in English (M8)

Task: END-023
Status: DONE
Confidence: CONFIRMED

## Observation

- END-020-END-022 surveyed, paired and measured the six roster endings
  (D-043, D-044, D-046). END-011's rule times them (D-045).
- The gate (2026-11-05) chose:
  - "GO (Recommended)";
  - "Indent, as the story (Recommended)";
  - "Bao Mao: (Recommended)";
  - "Accept the rule (Recommended)".

## Hypothesis

`tools.text.dialogue --endings data/text/m8_endings.json` builds one image,
from the untouched source, with the M5 story and win quotes and all six
roster endings in English. Forced from the END-001 checkpoint:
- every ending draws its predicted cells, with its scene changes and music
  on the Japanese frames;
- lists 6-8 are unchanged apart from the shared boxes.

The image plays from a cold boot.

## Controlled Change

The compiler, generalized:
- `ending.compile_endings`: several pairings in one code allocation, one
  room and one font, plus the half-cell indent, slot overrides and the
  observed boxes of all nine lists;
- `--endings` and `--ending-record-dir`.

`ending.compile_ending` is now a one-pairing call of it. END-011's build
reproduces byte for byte with the refactored code (every output, the
image, the record).

## Prediction

- Two builds identical, every changed byte accounted for, the M5 files
  unchanged, all sectors valid.
- Lists 0-5 forced: every box draws its predicted cells, the timing matches
  the untouched runs, and the cued boxes hold 42 frames or more.
- Lists 6-8 forced: their boxes draw as before, and 601/605 in English.
- A cold boot plays in English.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `data/text/m8_endings.json` | the six pairings and the gate's choices |
| Pairings, surfaces | `data/translations/*_ending_pairing.json`, `data/text/ending_surfaces*.json` |
| Checkpoint | `local/end001/checkpoint/jin_ending_a16503.mcs` |
| Controls (untouched image) | `local/end002/control` (list 0), `local/end020/list1`-`list8` |
| Play state | `local/ref005/session/states/f00004138.mcs` (REF-005, machine select with Jin) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/ending.py`, `tools/text/dialogue.py --endings` | The build |
| `EXP-0045/check_build.py`, `EXP-0036/untouched.py`, `tools.disc.sector` | Build checks |
| `EXP-0042/probe.py` | The nine forced endings (cells every 5 frames) |
| [`check_m8.py`](check_m8.py) → [`live.json`](live.json) | Cells, timing against the controls, holds (numbers only) |
| [`check_others.py`](check_others.py) → [`others.txt`](others.txt) | Lists 6-8 against the built `KANJI.BIN` |
| [`ending_route.py`](ending_route.py) | `EXP-0037/ending_route.py` with `--ending N` (and on-hit action lines filtered) |
| `EXP-0027/play_route.py`, `EXP-0036/play_summary.py` | Cold boot |

Agent Mednafen 1.32.1. The forced runs used the silent home with no key.
The cold boot was run with the user present and asked first: "Yes, run it
now (Recommended)".

## Procedure

```bash
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --endings data/text/m8_endings.json"
$B --out build/end023/m8 --ending-record-dir build/end023/rec-a
$B --out build/end023/m8-again --ending-record-dir build/end023/rec-b
# check_build.py reads OUT/../NAME-record.json: copy rec-a/jin_ending.json and rec-b's there
./invenv.sh python research/experiments/EXP-0045/check_build.py build/end023/m8 build/end023/m8-again
./invenv.sh python research/experiments/EXP-0036/untouched.py build/end023/m8
./invenv.sh python -m tools.disc.sector "build/end023/m8/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
CUE="build/end023/m8/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"; export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python research/experiments/EXP-0042/probe.py local/end023/list0 --cue "$CUE" \
  --frames 14200 --step 5 --cells-until 7500
for n in 1 2 3 4 5 6 7 8; do ./invenv.sh python research/experiments/EXP-0042/probe.py \
  local/end023/list$n --cue "$CUE" --frames 14200 --step 5 --cells-until 7500 \
  --onhit 06018E0C:060CFF7E=0$n --watch 060CFF7E:1; done   # three at a time
./invenv.sh python research/experiments/EXP-0050/check_m8.py build/end023/m8 --out research/experiments/EXP-0050/live.json
./invenv.sh python research/experiments/EXP-0050/check_others.py build/end023/m8 > research/experiments/EXP-0050/others.txt
./invenv.sh python research/experiments/EXP-0050/ending_route.py local/end023/route-arieta \
  --cue "$CUE" --ending 3 --frames 24000
./invenv.sh python research/experiments/EXP-0045/check_live.py local/end023/route-arieta build/end023/m8
./invenv.sh python research/experiments/EXP-0027/play_route.py "$CUE" local/end023/play-jin \
  --stop-after-posts 3 --no-fight-keys --select-wait 10 --move-wait 3
./invenv.sh python research/experiments/EXP-0036/play_summary.py build/end023/m8/prediction.json \
  local/end023/play-jin data/text/jin_boxes.json
```

2026-11-05, 17:30-19:30 local.

## Actual Result

### What the first live check found, and the fixes

The first build's live check (all nine endings) found two faults, both
fixed in the build above:

1. **Lists 6-8 draw their ending text with `KANJI.BIN`, not `SE.DAT`.**
   - Their runs load `KANJI.BIN` (twice) and no `SE.DAT`, so the story font
     M5 changed is what they show.
   - The shared English names 601/605 used the ending's codes, which hold
     M5's story glyphs in `KANJI.BIN`. The Shade ending (list 8) showed a
     garbled glyph run for "Jin:".
   - This was in the image since M7: END-010 checked the shared names in
     Gawaine's ending only, which uses `SE.DAT`.
   - **Fix** (the user's choices, verbatim below): each pair of a box lists
     6-8 show takes the story's code for that pair, whose `KANJI.BIN` glyph
     is that pair, and the joint choice of row variants needs the fewest new
     pairs. One pair, ": ", is in no story code. It takes the story's next
     sacrifice code (153rd, `0x8CF7`, glyph 506) in `KANJI.BIN`, which
     touches one visible line (1052, list 6's story).
2. **Typing steps over full-width spaces too.** Arieta's box 455 has 3 in 13
   codes. Counting only glyphs, the rule typed it faster than the Japanese,
   and her scene 27 came 23 frames early. The M8 build counts every code
   (glyphs and spaces, Japanese and English). END-010 and END-011's builds
   keep their count.

Asked, then corrected (no invisible code was left):
- "The three Saturn-only pilots' endings draw their text with the story
  font (KANJI.BIN), not the endings' font. So the two speaker names shared
  with them since M7 ("Jin:" and "Gawaine:") show as garbled glyphs in the
  Shade ending (list 8): a bug that has been in the image since M7, found
  now by M8's live check. Story glyphs cover every pair except one: ": "
  (colon + space). Fixing it means adding that one glyph to the story font
  at the code of a Japanese character used only in lines that are already
  English or never shown, so nothing visible changes, but KANJI.BIN differs
  from M5's by one glyph. How should M8 handle it?" → "Add the one glyph
  (Recommended)"
- "Correction to my last question: no invisible code is left in the story
  font. M5's 152 sacrificed codes already took every code no visible line
  uses. The closest option is M5's own next code (153rd of the 160 you
  approved for M5, same rarest-first rule): it would put the ": " glyph in
  place of one kanji in one line (line 1052) of the first Saturn-only
  pilot's story, text that stays Japanese until those pilots are done.
  That makes "Jin:" and "Gawaine:" read correctly in the Shade ending.
  Which?" → "Use M5's 153rd code (Recommended)"

### Build

- **Ending:** 100 boxes, 189 rows, 330 pairs on 310 unused + 20 new codes in
  `END.BIN`'s table, with none sacrificed there. 4,980 row bytes: 760
  beyond the roster's own lines, in lines no list 0-8 shows.
- **Two builds:** identical, with the six records identical.
- **M5:** `STG0AS.BIN`, `VICTORY.BIN`, `prediction.json` and `changes.json`
  equal RE-008's. `KANJI.BIN` differs from an M5-only build in 61 bytes,
  all inside glyph 506's tiles, and the M5-only build equals RE-008.
- **Ending files:** every changed byte is in `ending_changes.json`:

  | File | Bytes changed |
  | --- | --- |
  | `END.BIN` | 5,355 |
  | `SE.DAT` | 27,000 |
  | `KEND_1.BIN` | 32 |
  | `QSD.PIX` | 798 |

- **Image:** 202 sectors changed, all 43,793 valid; the source is
  unchanged. `data/regression/end023_roster_endings.json`.

### Live (forced from the END-001 checkpoint, built image; `live.json`)

| List | Boxes drawn as predicted | Timing against the untouched run | Smallest hold of a cued English box |
| --- | --- | --- | --- |
| 0 Jin | 21/21 | equal (all +1, the run's offset) | 116 |
| 1 Santana | 22/22 | equal (all −1) | 42 |
| 2 Mary | 17/17 | equal | 89 |
| 3 Arieta | 26/26 | equal (+3) except scene 27, +6 more | 64 |
| 4 Gawaine | 20/20 | equal (+1) | 84 |
| 5 Bao and Mao | 26/26 | equal (−1) except two posts, ±3 more | 90 |
| 6 | 15/15 (built `KANJI.BIN`) | equal | — |
| 7 | 27/28 (882 opens 66 frames before the last dump, 14 glyphs typed) | equal (−2) | — |
| 8 | 19/19, 601/605 in English | equal | — |

- Lists 6-8 are checked against the built `KANJI.BIN` (`check_others.py`).
  Their boxes with M5-sacrificed codes (1011, 1019, 1021, 862, 734, 735)
  show the replaced glyphs the M5 gate approved.
- Code `0x2020` (two ASCII spaces) draws no glyph, like `0x8140`.
- Boxes right before a scene change hold only as the Japanese does: Jin's
  415 holds 31 frames, Bao and Mao's 482 holds 5 and 551 holds 18. Their
  scene changes stay on the Japanese frames. In the untouched run, box
  483's line is also gone at the post that follows it.
- **Agent review:**
  - sheets of every second screenshot of lists 1-5 (156): the English of
    every box, captions with English names, narration, Mary's run-on
    scenes, "Bao Mao:" with box 486;
  - list 8: "Jin:" and "Gawaine:" in English beside the Japanese captions.

### Play

- **Your REF-005 play state** (machine select with Jin), built image, the
  ending number set to 3 at the round end: Jin's last fight won by RAM
  writes (END-001's route), then Arieta's ending (posts 16-21, 27, 28). All
  26 box openings drew their predicted cells, 25 of them English.
- **Cold boot of the built image:**
  - 5 menu keys, all sent; scenes 21, 0 and 1 posted;
  - scenes 21 and 0 drew 6 of 6 English boxes;
  - screenshot `p0016` shows Jin's English in play.

## Conclusion

Prediction met after the two fixes. One image, built twice identically from
the untouched source, holds the M5 story and win quotes and all six roster
endings in the official US arcade English:
- every box draws as predicted in all nine endings;
- the scene changes and music match the Japanese within 6 frames;
- the cued English boxes hold 0.7 s or more;
- the Saturn-only endings keep their Japanese, with the shared names in
  English.

M8 is met.

## Uncertainty and Alternatives

- The M7 images (END-010, END-011) have the list 8 name fault; M8's image
  supersedes them.
- The unshown room is marker-tested in lists 0-1 only. All nine endings
  drew as expected on the built image, which uses 760 bytes of it.
- The "in that boot" ending of the play criterion was reached from a saved
  play state (REF-005), not the cold boot itself. Reaching an ending from a
  cold boot needs the whole game won.

## Reproduction

Run the procedure. Expect `data/regression/end023_roster_endings.json`'s
hashes and the results above.
