# EXP-0046: What Every Roster Ending Shows

Task: END-020
Status: DONE
Confidence: CONFIRMED (the boxes each ending opens; every Japanese text is an `END.BIN` box; the shared post-dialogue sequence; the arcade's slots per list)

## Observation

- `END-001`-`END-005` covered Jin's ending only. D-036 lists each list's
  posts and, from a static reading of the scripts, their boxes
  (`data/text/ending_posts.json`). By that reading, the Saturn never shows
  Mary's scenes 17-18 or Bao and Mao's scene 20, which the arcade does.
- The ending number can be forced on the Saturn (`0x060CFF7E`, D-036). In
  the arcade, the round end copies the winner's pilot byte into the ending
  number `0xFFEB2C` at `0xDBB6`/`0xDC0C` (`move.b ($370,A6),($6b2c,A5)`,
  the same in both sets).

## Hypothesis

Each of lists 1-5 can be played to the end of its QSound notice by forcing
the ending number. Its Japanese text is the boxes D-036 lists, drawn as
`END.BIN` boxes, and the screens after the dialogue are Jin's. Forcing the
arcade's ending number the same way plays each list's arcade ending.

## Controlled Change

None to either game. Saturn: from the END-001 checkpoint, an on-hit write
of the list number to `0x060CFF7E` at `0x06018E0C` (`EXP-0039`'s method),
one run per list. Arcade: EXP-0040's route, with breakpoints at `0xDBBC`
and `0xDC12` that set `0xFFEB2C` to the list.

## Prediction

- Saturn: each list's posts as D-036 lists them, and its boxes opened.
  Every text on screen before the cast roll is an open box. The roll,
  credits, thank-you screen and QSound notice are as in Jin's ending.
- Arcade: each run reads exactly the slots its list's script opens
  (`data/arcade/ending_scripts.json`).

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Checkpoint | `local/end001/checkpoint/jin_ending_a16503.mcs` (EXP-0037) |
| Saturn image | untouched source |
| Arcade | `local/arcade` zips; NVRAM base `local/end004/mame/nvram_base` (EXP-0040) |
| `data/text/ending_posts.json` | `4aa3e3ae…` (EXP-0039) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0042/probe.py` | Saturn forced runs (screenshots every 50 frames, box calls, loads, posts) |
| [`make_timelines.py`](make_timelines.py) → [`timelines/`](timelines/) | Arcade routes `route-{u,j}-{1..5}` from EXP-0040's |
| `tools/reference/mame_timeline.lua` | MAME 0.289, headless (`-video none`) |
| [`survey.py`](survey.py) | → `data/text/ending_surfaces.json` (numbers and labels only) |

No key pressed, no cold boot, no focus taken.

## Procedure

```bash
P=research/experiments/EXP-0042/probe.py; export MEDNAFEN_ALLOWMULTI=1
for n in 1 2 3 4 5; do
  ./invenv.sh python $P local/end020/list$n --frames 14200 --cells-until 0 \
    --onhit 06018E0C:060CFF7E=0$n --watch 060CFF7E:1 &
done; wait
./invenv.sh python research/experiments/EXP-0046/make_timelines.py research/experiments/EXP-0046/timelines
B=local/end004/mame/nvram_base
for s in u j; do for n in 1 2 3 4 5; do name=route-$s-$n; O=local/end020/mame/$name
  mkdir -p $O/snap $O/nvram; cp -R $B/cybots$s $O/nvram/
  MAME_TIMELINE=research/experiments/EXP-0046/timelines/$name.txt mame cybots$s -rompath local/arcade \
    -autoboot_script tools/reference/mame_timeline.lua -snapshot_directory $O/snap \
    -cfg_directory local/mame_arcade/cfg -nvram_directory $O/nvram -skip_gameinfo \
    -nothrottle -video none -sound none -seconds_to_run 600 -debug -debugger none
done; done
./invenv.sh python research/experiments/EXP-0046/survey.py --out data/text/ending_surfaces.json
```

2026-11-05, 15:48-16:20 local. The five Saturn runs took about 7 minutes
in parallel; each arcade route took about 30 seconds.

## Actual Result

### Saturn

Every list posted exactly D-036's scenes. The boxes each run opened,
against the posted scripts:

| List | Pilot | Openings (run / posts) | Boxes opened but in no post's script |
| --- | --- | --- | --- |
| 0 | Jin (END-010's control run) | 22 / 20 | none |
| 1 | Santana | 24 / 22 | none |
| 2 | Mary | 17 / 4 | 440-447, 602, 604, 610 |
| 3 | Arieta | 27 / 24 | none |
| 4 | Gawaine | 20 / 17 | none |
| 5 | Bao and Mao | 28 / 26 | 486 |

- In lists 0, 1, 3 and 4 the extra openings are speaker names reopened for
  each caption; EXP-0039 listed each box once per scene.
- Mary's scene 16 and Bao and Mao's scene 19 run on into the next scenes'
  words. The scripts do not end at `0xE000`: Mary's scene-16 script,
  `0x060837E0`, goes on past it into the words where scenes 17 and 18
  start (`0x06083814`, `0x06083850`). So the boxes of the arcade's "Saturn
  never posts" scenes are shown: Mary's 17-18 (440-447) and Bao and Mao's
  20 (486).
- **Surfaces** (agent review of every second screenshot, from the first post
  to `KEND.BIN`'s load, 178 shots):
  - all Japanese text is dialogue boxes with portraits, captions with
    speaker names, a caption without a name (Gawaine's 472) and narration
    (Santana, Arieta, Gawaine);
  - each short standalone line falls in an open box's window (Arieta's 455
    at 3551, open 3513-3671; Gawaine's 472 at 2999, open 2919-3134);
  - no picture carries text.
- **After the dialogue:** every list loads `FIX.BIN`, `KEND.BIN`,
  `KEND_0.BIN`, `KEND_1.BIN` and `QSD.PIX`, and shows the same cast roll,
  staff credits, thank-you screen and QSound notice (sampled at 5 points
  per list). The pictures come from `STDEM1`/`2`/`4`/`5.PIR` and
  `STDEM7.PIR`; Gawaine's loads none.
- Each opening's open and close frames and its last screenshot (frame,
  SHA-256) are in `ending_surfaces.json`.

### Arcade (headless MAME)

- Each run's ending number became the list at frame 9259 (the debugger
  write after the game's copy).
- All 10 routes read exactly the slots their list's script opens: 17, 14,
  22, 16 and 20 for lists 1-5, in both sets.
- The first `cybotsu` list-3 run never left attract mode, and none of its
  taps logged anything. The rerun was normal; the cause is not known.
- The US snapshots (sheets of every fourth, agent-reviewed) show the same
  kinds of surface in English. Mary's ending has scenes 17-18, Bao and
  Mao's has scene 20, and the cast roll has Latin names only.

## Conclusion

Prediction partly met.
- All text in the five endings is `END.BIN` boxes of D-035's kinds, and
  the post-dialogue screens are shared and already handled (D-040,
  D-041). No new surface needs a drawing path.
- D-036's box lists are incomplete. A posted scene's script runs on into
  the following scenes until the next post, so Mary's ending shows the
  arcade's scenes 17-18 and Bao and Mao's shows scene 20.
- The authoritative per-list box sequence is the observed one,
  `data/text/ending_surfaces.json` (D-043). M8's pairing must use it.

## Uncertainty and Alternatives

- What `0xE000` does, and what ends a script's run (the next post, or the
  ending routine moving on), is not decoded. The observed sequences don't
  depend on it.
- One run per list: the sequences come from forced endings from Jin's
  checkpoint. D-036 forced Santana's ending two ways (the ending number
  after the copy, or the pilot byte before it) with the same result; no
  played ending other than Jin's has been compared.

## Reproduction

Run the procedure. Expect `data/text/ending_surfaces.json` byte for byte
from the same runs, and the counts above.
