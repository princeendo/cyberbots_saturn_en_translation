# EXP-0049: What All Six Roster Endings Need, Together

Task: END-022
Status: DONE
Confidence: CONFIRMED (rows, cells, pairs, codes and room as measured; lists 6-8's boxes as seen); SUPPORTED (that the unshown lines stay unread in lists 2-8; END-023 checks every list live)

## Observation

- END-021 paired lists 1-5 (D-044). END-011 set the timing rule (D-045);
  its dry runs on lists 0-5 hold 45 frames or more.
- D-039's room ("lines no ending box shows") came from the posted
  scripts' box lists, which D-043 showed are incomplete. The marker test
  covered only Jin's and Santana's endings.
- Lists 6-8 (the Saturn-only pilots) stay Japanese in M8. Which lines they
  show was known only from their posted scripts.

## Hypothesis

All six endings' English fits together:
- one `END.BIN` code table and `SE.DAT` font, with no Japanese glyph that
  stays on screen given up;
- room in `END.BIN`'s own and unshown lines;
- the box limits.

Lists 6-8 show only their posted boxes.

## Controlled Change

None to the game. Lists 6-8 were forced from the END-001 checkpoint as
`EXP-0046` forced lists 1-5 (no key, no cold boot), and the rest is static.

## Prediction

- Rows and cells within 3 and 60, and no row wider than the Saturn's own
  lines.
- Pairs within the codes no visible Japanese uses.
- Row bytes within the own + unshown lines.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Pairing files of lists 0-5 | `data/translations/*_ending_pairing.json` |
| `data/text/ending_surfaces.json` | `772653c4…` (lists 0-5, EXP-0046) |
| `data/text/ending_surfaces_others.json` | `e6561394…` (lists 6-8, made here) |
| `END.BIN` (untouched) | `a4868d8d…f3fa` |
| `cybotsu` program | `18e8827d…52fd` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `EXP-0042/probe.py` | Lists 6-8 forced |
| `EXP-0046/survey.py --others` (new option) | → `data/text/ending_surfaces_others.json` (numbers only; the default output is unchanged) |
| [`capacity_all.py`](capacity_all.py) | → [`capacity.json`](capacity.json) (numbers only) |
| `EXP-0048/check_all.py`, `rule.json` | The timing rule's holds |

## Procedure

```bash
P=research/experiments/EXP-0042/probe.py; export MEDNAFEN_ALLOWMULTI=1
for n in 6 7 8; do ./invenv.sh python $P local/end020/list$n --frames 14200 \
  --cells-until 0 --onhit 06018E0C:060CFF7E=0$n --watch 060CFF7E:1 & done; wait
./invenv.sh python research/experiments/EXP-0046/survey.py --others \
  --out data/text/ending_surfaces_others.json
./invenv.sh python research/experiments/EXP-0049/capacity_all.py \
  local/ref003/cybotsu-maincpu.bin --out research/experiments/EXP-0049/capacity.json
```

2026-11-05, 17:15-17:40 local.

## Actual Result

### Lists 6-8

| List | Posts | Openings (run / posts) | Boxes outside the posts | Reached |
| --- | --- | --- | --- | --- |
| 6 | 19, 20, 20 | 15 / 15 | none | the cast roll and the QSound notice |
| 7 | 22-26 | 28 / 28 | none | the cast roll; not the QSound notice within 14,200 frames |
| 8 | 32, 33, 34 | 19 / 17 (names reopened) | none | the cast roll and the QSound notice |

They show only their posted boxes, 114 lines in all. All three show the
shared cast roll (`KEND*.BIN`), so the hidden Japanese names apply to them
too, as the user chose ("Hide in every ending").

### Capacity (`capacity.json`)

- **English boxes:** 100 (boxes 601, 604, 605, 606, 607 and 610 are shown by
  more than one roster ending and are built once).
- **Rows and cells:** at most 3 rows and 47 glyph cells a box (limits 3 and
  60). No row is wider than the widest Saturn line of its kind (16 cells
  for dialogue boxes, captions and narration; 6 for names).
- **Pairs and codes:**

  | Rows | Pairs | Codes no line uses + new (335) | Codes no staying line uses + new (930) |
  | --- | --- | --- | --- |
  | As is | 388 | 53 short | fits |
  | Half-cell indent (`shift_rows`, as M5) | 330 | fits | fits |

  The lines that stay Japanese on screen after M8 are those of lists 6-8
  (less boxes 601 and 605, which are English) and the blank 1072. 905 of
  the table's codes are used by none of them. So the 53 extra codes the
  as-is rows need would be codes only the roster's (now English) or
  never-shown lines use; no Japanese on screen would change.
- **Box 608:** both choices give the same pairs. Slot 617 ("both twins")
  adds 4 row bytes over slot 615.
- **Room:**

  | | Lines | Bytes |
  | --- | --- | --- |
  | Rows needed | — | 4,920 as is; 4,976 with the indent |
  | Own (only English or never-shown boxes point to them) | 163 | 4,232 |
  | Unshown (no box any of lists 0-8 is seen to open) | 1,575 | 42,844 |

  - The own lines are 690-745 bytes short, and the rest comes from the
    unshown room. All 42,844 unshown bytes lie in `EXP-0042`'s
    marker-tested spans.
  - That test's room included 16 lines Mary's and Bao and Mao's run-on
    boxes show (806-819, 888, 1007). They are excluded here, and M7's rows
    (`0x0AECC`) are not among them.
- **Timing** (`EXP-0048/rule.json`): every cued English box holds 45 frames
  or more, and scene ends move at most 5 frames. Boxes typed slower than
  the Japanese: Arieta's 455 (5 frames a glyph), Gawaine's 472 (16), Bao
  and Mao's 482, 483 (6) and 487 (10).

## Conclusion

Prediction met. All six endings' English fits:
- with the indent, in the 335 codes no line uses;
- as is, by also using codes no line that stays Japanese uses;
- room in the own lines plus about 750 bytes of the unshown lines.

No visible Japanese is touched either way.

Options for the gate (`TASKS.md`):
1. **Rows:** with the half-cell indent, as M5 (no code taken from any
   Japanese character; Recommended); or as is, plain rows, taking 53 codes
   only now-English or never-shown lines use.
2. **Box 608:** slot 617, the same Japanese, "both twins" (Recommended);
   or slot 615, what the arcade shows there.
3. **Timing:** the rule as chosen, including the five slowed boxes.

## Uncertainty and Alternatives

- That `END.BIN` never reads the unshown lines in lists 2-8 is SUPPORTED
  only: the marker test ran in lists 0 and 1. END-023 forces all nine
  endings on the built image and checks every box.
- Whether `SE.DAT` is loaded outside endings is not recorded (D-035 saw it
  in Jin's ending). With the indent no code of any Japanese character is
  used, so that does not matter for the recommended option.

## Reproduction

Run the procedure. Expect both data files byte for byte and the numbers
above.
