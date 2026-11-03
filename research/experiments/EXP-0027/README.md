# EXP-0027: The Pilot Lists Named; Santana Chosen; His Story Boxes

Task: RE-004
Status: DONE
Confidence: CONFIRMED (list-to-pilot names for the arcade pilots, Saturn list = arcade pilot 0-5, Santana's story scenes, route and forcing); SUPPORTED (scene-post blocks k = pilot list k for lists 2-8)

## Observation

The Saturn has 11 per-pilot scene lists (`0x060AAD24`, D-021).
`STG0AS.BIN`'s stage code posts 187 scenes, in blocks that each open with a
narration scene and then scene 0 (EXP-0022). The choice of second pilot is
the user's (`RE-004`).

## Hypothesis

- Saturn lists 0-5 are the arcade pilots 0-5, in the same order.
- Each block of scene posts is one pilot's story, in list order.
- The stage byte `0x060CFF88` starts at a pilot-specific stage group.

## Controlled Change

None to the game:
- scene-list redirects from state 4138 (EXP-0026's `other_pilot.py`), on the
  original image;
- cold boots driven with pad keys and a log of scene posts.

## Prediction

- Each forced list's scene 0 shows a different pilot's opening.
- The arcade's scene scripts for pilot k equal the Saturn list k's.
- A cold boot with Santana posts block 1's scenes in order.

## Inputs and Provenance

- REF-005 state `f00004138.mcs` (`3eb789da…`).
- `STG0AS.BIN` and the `cybotsu` program image (`local/ref003/`).
- The arcade English decode (ignored; counts only).
- `data/text/saturn_arcade_pairing.json`.
- Untouched image; all 63 components unchanged
  (`local/logs/re004-source-after.json`). Patched binary `2fc3d547…eaaf`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`scene_posts.py`](scene_posts.py) | The scene posts in an overlay, grouped into blocks |
| [`candidates.py`](candidates.py) | The candidate table for lists 1-5 (counts only) |
| [`play_route.py`](play_route.py) | Cold boot, pilot chosen by pad moves, scene posts logged, fights forced (D-025) |
| [`check_first_box.py`](check_first_box.py) | A forced scene's first box against the original font |
| `research/experiments/EXP-0026/other_pilot.py` | Scene-list redirect, with an added step count |
| `research/experiments/EXP-0022/box_list.py` | `data/text/santana_boxes.json` (`--pilot 1`) |

## Procedure

```bash
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
for p in 0 1 2 3 4 5 6 7 8 9 10; do
  ./invenv.sh python research/experiments/EXP-0026/other_pilot.py "$ORIG" local/re004/list-$p $p 0 70
done
./invenv.sh python research/experiments/EXP-0027/scene_posts.py local/extracted/saturn_jp/STG0AS.BIN
./invenv.sh python research/experiments/EXP-0027/candidates.py local/ref003/text-cybotsu.json
./invenv.sh python research/experiments/EXP-0027/play_route.py "$ORIG" local/re004/select1 --moves right --until-stage 0
./invenv.sh python research/experiments/EXP-0027/play_route.py "$ORIG" local/re004/santana1 --moves right,right --until-stage 2
./invenv.sh python research/experiments/EXP-0022/box_list.py local/extracted/saturn_jp/STG0AS.BIN \
  --pilot 1 --out data/text/santana_boxes.json   # then the story scenes are added from block 1
for s in 4 9 24; do
  ./invenv.sh python research/experiments/EXP-0026/other_pilot.py "$ORIG" local/re004/force-$s 1 $s 80
  ./invenv.sh python research/experiments/EXP-0027/check_first_box.py data/text/santana_boxes.json $s local/re004/force-$s
done
```

2026-11-02 21:00 to 2026-11-03 11:13 local, the user present for the
choice and the cold boots.

## Actual Result

### Names

- **Scripts:** the arcade's scene scripts (`0x12150`) for pilot k equal the
  Saturn list k's for k = 0-5: 19, 21, 19, 25, 20 and 22 identical scenes
  of 22, 27, 22, 29, 22 and 29. The others are ending scenes.
- **Saturn-only lists:** list 9 matches the arcade's pilot 6 (48 of its
  scenes) and list 10 the arcade's pilot 7 (6 scenes). Lists 6-8 match no
  arcade pilot: they are the Saturn-only pilots.
- **Pilots:** forced scene 0 of each list (agent-reviewed; portraits are not
  loaded outside the pilot's own stage), with the pilot names in each list's
  English records:

| List | Pilot | Evidence |
| --- | --- | --- |
| 0 | Jin | D-021 |
| 1 | Santana | a mercenary asking for a way into an Earth Corps colony; "Santana" the most frequent name |
| 2 | Mary | addressed as an Earth Corps young lady; a soldier's challenge |
| 3 | Arieta | a girl just arrived on Earth |
| 4 | Gawaine | greeted as "Captain Gawaine" and answers Mary |
| 5 | Bao and Mao | Mao calls her big brother; "Bao" the most frequent name |

### Candidates and the user's choice

`candidates.py`, story scenes only (each pilot's block of posts):

| List | Story scenes | Boxes | Boxes paired slot for slot | Shared lines | Pairs | New beyond Jin's | Union with Jin | Bytes needed / own room |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 Santana | 20 | 64 | 63 | 121, 122, 123, 144 | 306 | 55 | 408 | 3,324 / 3,208 |
| 2 Mary | 18 | 69 | 68 | — | 353 | 90 | 443 | 4,060 / 3,328 |
| 3 Arieta | 21 | 66 | 66 | 386 | 348 | 77 | 430 | 4,192 / 3,548 |
| 4 Gawaine | 17 | 70 | 66 | 8 lines, incl. 57 | 352 | 77 | 430 | 4,488 / 3,552 |
| 5 Bao and Mao | 21 | 72 | 68 | 7 lines, incl. 75 | 342 | 71 | 424 | 3,756 / 3,708 |

No box needs more than 3 rows. Asked (2026-11-03): "Which pilot should be
the second one in English (M4)?"; the user's answer, verbatim: "Santana
(Recommended)".

### Santana's route and scenes

- **Pilot select:** Jin is the first portrait. One move right selects Mary:
  the cold boot posted scenes 19 then 0, which is block 2, with the stage
  byte at 18. **Two moves right select Santana.**
- **Cold boot with Santana** (`santana1`, original image): the posts were
  23 (frame 6225), 0 (7062), 1 (11353), 2 (12621), 3 (28829) and 4 (29849).
  That is block 1's order. The stage byte read 9, then 10 and 11 after the
  forced wins. So block k is pilot list k (k = 0-2 seen), and each pilot's
  stages start at their own group of the shared stage table (`0x0609353C`
  and beyond): Jin 0, Santana 9, Mary 18. 100 keys were sent; a few were
  refused while Mednafen was not in front, which only delayed the second
  fight's end.
- **Story scenes** (block 1): 23, 0, 1, 2, 3, 4, 5, 24, 6, 7, 25, 8-14, 26
  and 15. That is 20 scenes, boxes 64-127, Saturn lines 121-237. His ending
  is scenes 16-22, which are not posted by `STG0AS.BIN`.
- **Box list:** `data/text/santana_boxes.json` (SHA-256 `d6ea9fa9…`): all 27
  scenes, plus `story_scenes` and the posted order. It holds no text.
- **Forcing** (scene-list redirect from 4138, original image): the first
  boxes of scenes 4, 9 and 24 draw their predicted cells, 29/29, 29/29 and
  30/30. As a control, scene 9's box does not appear in scene 4's run (0).

The source is unchanged.

## Conclusion

**CONFIRMED:**

- Saturn pilot lists 0-5 are the arcade's pilots 0-5: Jin, Santana, Mary,
  Arieta, Gawaine, and Bao and Mao. Lists 6-8 are Saturn-only, and lists 9
  and 10 match the arcade's pilots 6 and 7.
- The user chose Santana. He is two moves right of Jin on the pilot select
  screen.
- His story is 20 scenes, posted in block 1's order from stage group 9 on,
  and any of them can be forced.

## Uncertainty and Alternatives

- That block k is list k for k = 3-8 is not yet seen in play (SUPPORTED by
  the narration-then-0 pattern).
- The four shared lines (121-123, 144) belong to Santana's opening and one
  other box. Which other boxes use them is for `RE-006`'s kept-line rule.
- One of Santana's 64 boxes is not slot-for-slot in REF-006's pairing; that
  is `PAIR-002`'s to resolve.

## Reproduction

Run the procedure. Expect the tables above, block 1's posts in the cold
boot, and 29, 29 and 30 cells.
