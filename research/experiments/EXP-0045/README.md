# EXP-0045: Jin's Ending in English, Built From the Source Image

Task: END-010
Status: DONE
Confidence: CONFIRMED

## Observation

- `END-005` paired every unit of Jin's ending (`jin_ending_pairing.json`,
  D-038). The gate GO (2026-11-05) covers the official English as paired,
  the shared name boxes translated in place, and no sacrificed code.
- `EXP-0042`: the lines no ending box shows are never read. `EXP-0043`: how
  to erase the QSound line. `EXP-0044`: how to hide the cast roll's
  Japanese names.

## Hypothesis

`tools.text.dialogue --ending` builds, from the untouched source, one image
with the M5 roster unchanged and Jin's ending in English. Every unit draws
its predicted cells from the END-001 checkpoint, the image units appear as
the user chose, and the image plays from a cold boot.

## Controlled Change

The compiler's new `--ending` step (`tools/text/ending.py`), on top of the
RE-008 roster build:
- `END.BIN`: rows, records, no new table codes;
- `SE.DAT`'s font copy: 179 pair glyphs;
- `KEND_1.BIN`: 16 size words;
- `QSD.PIX`: 11 rows.

## Prediction

- Two builds are identical.
- The story files equal RE-008's.
- Every changed byte lies in a recorded range, and all sectors are valid.
- From the checkpoint, all 18 units draw their predicted cells.
- Another list's ending shows the shared names in English and its own boxes
  unchanged.
- Agent-reviewed screenshots show the English, the cast roll's Latin names
  only, and the QSound notice without its Japanese line.
- A cold boot plays Jin's story in English.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Source image | Track 01 `758fa795…dbd1` (`references/saturn_jp/README.md`) |
| `data/translations/jin_ending_pairing.json` | `6e9f2988…` (EXP-0041) |
| `cybotsu` program | built from the ROM zips at build time (`18e8827d…52fd`) |
| Checkpoint | `local/end001/checkpoint/jin_ending_a16503.mcs` (EXP-0037) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/ending.py`, `tools/text/dialogue.py --ending` | The build |
| [`check_build.py`](check_build.py) | Two builds, M5 against RE-008, ending bytes against their ranges |
| `tools.disc.sector`, `EXP-0036/untouched.py` | Sectors; the story files' bytes |
| `EXP-0042/probe.py` | Forced runs from the checkpoint |
| [`check_live.py`](check_live.py) | Each opened box against the build's prediction (translated) or its original cells (others) |
| `EXP-0027/play_route.py`, `EXP-0036/play_summary.py` | Cold boot |

Agent Mednafen 1.32.1, silent home for forced runs; the cold boot with the
user present and asked first.

## Procedure

```bash
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-010 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade \
  --ending data/translations/jin_ending_pairing.json"
$B --out build/end010/jin --ending-record build/end010/jin-record.json
$B --out build/end010/jin-again --ending-record build/end010/jin-again-record.json
E=research/experiments/EXP-0045
./invenv.sh python $E/check_build.py build/end010/jin build/end010/jin-again
./invenv.sh python research/experiments/EXP-0036/untouched.py build/end010/jin
./invenv.sh python -m tools.disc.sector "build/end010/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
CUE="build/end010/jin/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
P=research/experiments/EXP-0042/probe.py; export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $P local/end010/live-jin --cue "$CUE" --frames 13400 --cells-until 7000
./invenv.sh python $P local/end010/live-list4 --cue "$CUE" --frames 12000 --cells-until 9000 \
  --onhit 06018E0C:060CFF7E=04 --watch 060CFF7E:1
./invenv.sh python $E/check_live.py local/end010/live-jin build/end010/jin
./invenv.sh python $E/check_live.py local/end010/live-list4 build/end010/jin
./invenv.sh python $E/check_live.py local/end002/control build/end010/jin   # negative control
# per-frame timing of the longest boxes
./invenv.sh python $P local/end010/timing-pre --cue "$CUE" --frames 5100 --cells-until 0 --save-at 1800,5060
./invenv.sh python $P local/end010/timing-409 --cue "$CUE" --state local/end010/timing-pre/s01800.mcs \
  --frames 600 --step 1 --cells-until 600
./invenv.sh python $P local/end010/timing-420 --cue "$CUE" --state local/end010/timing-pre/s05061.mcs \
  --frames 240 --step 1 --cells-until 240
# cold boot (user present)
./invenv.sh python research/experiments/EXP-0027/play_route.py "$CUE" local/end010/play-jin \
  --stop-after-posts 3 --no-fight-keys --select-wait 10 --move-wait 3
./invenv.sh python research/experiments/EXP-0036/play_summary.py build/end010/jin/prediction.json \
  local/end010/play-jin data/text/jin_boxes.json
```

2026-11-05, 15:05-15:40 local. The `ending_prediction.json` the live check
reads is the build's; `data/translations/jin_ending.json` is
`build/end010/jin-record.json`.

## Actual Result

### Build

- **Ending:**
  - 18 boxes, 34 rows, 179 pairs, all on codes no line uses; no new code
    and no sacrifice.
  - 872 row bytes. Jin's own free lines hold 828: 26 of his lines, lines
    897-898, and the shared names' lines 1006 and 1010, which only boxes
    601 and 605 use. Two rows (64 bytes) go to `END.BIN` `0x0AECC`, the
    first span `EXP-0042` showed is never read.
- **Two builds:** identical: every output, Track 01, both records.
- **M5:**
  - `STG0AS.BIN`, `KANJI.BIN`, `VICTORY.BIN`, `prediction.json` and
    `changes.json` have `re008_roster.json`'s hashes;
  - `untouched.py`: STG0AS 25,492 and VICTORY 1,438 bytes, KANJI 487 cells,
    all inside their ranges.
- **Ending files:** every changed byte is inside a range of
  `ending_changes.json`; `SE.DAT` outside `0x40000`-`0x67FFF` is unchanged.

  | File | Bytes changed | Ranges |
  | --- | --- | --- |
  | `END.BIN` | 910 | 52 |
  | `SE.DAT` | 14,558 | 716 (179 glyphs × 4 tiles) |
  | `KEND_1.BIN` | 32 | 16 |
  | `QSD.PIX` | 798 | 11 |

- **Image:** 7 files replaced, 158 sectors changed, all 43,793 valid. Track
  01 is `f2be320d…2ffb`; the source's `758fa795…dbd1` is unchanged.
  `data/regression/end010_jin_ending.json` holds the rest.

### Live, from the END-001 checkpoint

| Run | Boxes opened | Full | Notes |
| --- | --- | --- | --- |
| Jin, built image | 21 | 20 | All 20 translated openings full except 420 (30 of 31 at the 11-frame polls; 31 of 31 at 1-frame polls) |
| Gawaine (list 4 forced), built image | 20 | 20 | 605 and 601 (6 openings) draw the English names; his 14 boxes draw their original Japanese cells |
| Control (untouched), against the build | 21 | 1 | Only box 1072; all 20 translated openings short (negative control) |

The box timing was measured at 1-frame polls (frames counted from each
state). The scene script fixes each box's time, and it is the same in both
languages within ±8 frames. Typing runs at about 6 frames a glyph (two
letters).

| Box | Glyphs (Japanese → English) | Full English drawn | Box closes | Full line held |
| --- | --- | --- | --- | --- |
| 409 | 30 → 45 | 478 | 485 | 7 frames |
| 493 | 30 → 43 | 746 | 753 | 7 frames |
| 420 | 25 → 31 | 394 | 398 | 4 frames |

Every other box holds the full line for 80-300 frames (412, 416, 417, 418
at the 11-frame polls). Nothing is cut off. These three boxes' timers were
set for the shorter Japanese.

Screenshots, agent-reviewed:
- **Scenes 16-19:** every box shows its English, typed into the original
  boxes and portraits:
  - box 413 in English where the control shows the Japanese;
  - the narration, white on black;
  - the captions with their English speaker names (605, 601) before them.
- **Captions:** rows 2-3 start under the caption's column, after the
  speaker name, as in the arcade.
- **Cast roll** (`KEND_1.BIN` from disc): all ten Latin names, the
  portraits, the roll's English lines and Jin's closing shot; no Japanese name.
- **QSound notice** (`QSD.PIX` from disc): five English lines and the logo;
  no Japanese line, no gap.
- **Gawaine's ending:** the speaker names 605 and 601 in English beside his
  Japanese captions, as the gate chose.

### Play (cold boot of the built image)

Asked first: "Yes, run it now (Recommended)".
- Jin is the default pick; 5 keys were pressed, all at menus. The two
  retry presses were not sent because Mednafen was not in front, and the
  run did not need them.
- Scenes 21, 0 and 1 were posted (1 after the stage 0 fight timed out).
- Scene 21 drew 2 of 2 boxes complete, scene 0 4 of 4. Scene 1's boxes are
  not counted: the run stops at its post.
- The screenshots show Jin's English story boxes in play (`p0016`,
  `p0026`).

## Conclusion

Prediction met. One image, built twice identically from the untouched
source, holds the M5 roster unchanged and Jin's ending in the official US
arcade English: all 18 units, drawn as predicted from the checkpoint. The
cast roll's Japanese names are hidden in every ending, and the QSound line
is erased. The shared names are English in the other endings that show
them, and the image plays from a cold boot. M7 is met.

The user accepted the three boxes' short hold time ("Accept now, follow-up
task (Recommended)"); the follow-up is `END-011`.

## Uncertainty and Alternatives

- Only lists 0 and 4 were forced on the built image. The other endings'
  boxes are untouched except 605/601; their room use rests on `EXP-0042`.
- The box timers come from the scene scripts; that they can be lengthened
  is not tested (`END-011`).

## Reproduction

Run the procedure. Expect the build hashes in
`data/regression/end010_jin_ending.json` and the results above.
