# EXP-0074: Census of the Text Tables and Their Readers (TXT-010)

Task: TXT-010
Status: DONE
Confidence: CONFIRMED (the box classification, by reading the game's own
tables; the arcade readers seen in play, by read taps); SUPPORTED (no
random or region condition in the arcade's story posting, by code reading;
the third arcade reader is a test-mode viewer)

## Observation

The outline asks for "rare, random, or region-gated text: trace every
reader of every text table". In MSHvSF such text appeared only behind a
1-in-64 roll in one region (playbook step 7). Cyberbots' Saturn script has
1,074 box records, three copies of its lines (`STG0AS.BIN`, `END.BIN`,
`VICTORY.BIN`) and eleven scene lists; the arcade has three 624-slot
dialogue tables per set (Japanese, Spanish, English, D-009).

## Hypothesis

Every box the Saturn can show is in a scene that some known path posts,
or in the caption or win-quote tables; any other box, and any arcade slot
read only under a rare or region condition, is the rare text.

## Controlled Change

None. Static reading of the tables and code; two headless MAME runs with
read taps.

## Prediction

A short list of boxes with no path, and the arcade's readers matching the
known ones (`EXP-0009`, `EXP-0032`, `EXP-0069`).

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| `STG0AS.BIN`, `VICTORY.BIN` | untouched, `local/extracted/saturn_jp` |
| `data/text/pilot_census.json` | each list's posted scenes (`RE-005`) |
| Listings | `local/win002/mame/cybotsu-0-c0000.asm`, `local/ui003/mame/cybotsj-0-c0000.asm` |
| Arcade | `cybotsu`, `cybotsj`, MAME 0.289, fresh NVRAM copies |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`census.py`](census.py) → `data/text/reachability.json` | Box classes, lists, scripts, command counts, arcade reader PCs |
| [`timelines/`](timelines/) | Coin, start, two presses, 9,000 frames; `logreads` on each table's 624 pointers |
| `tools/sh2/disasm.py` | The script interpreter `0x0606E230` |

## Procedure

```bash
for s in cybotsu cybotsj; do  # fresh NVRAM copy each
  MAME_TIMELINE=research/experiments/EXP-0074/timelines/readers-$s.txt mame $s -rompath local/arcade \
    -autoboot_script tools/reference/mame_timeline.lua -cfg_directory local/mame_arcade/cfg \
    -nvram_directory NV -snapshot_directory SNAP -skip_gameinfo -nothrottle -video none -sound none -seconds_to_run 900
done
./invenv.sh python research/experiments/EXP-0074/census.py --arcade local/txt010/mame
./invenv.sh python tools/sh2/disasm.py --base 0x06060000 --start 0x0606E230 --end 0x0606E504 local/extracted/saturn_jp/STG0AS.BIN
grep -n -E '#\$140000[0-9a-f]|\$a310a|\$b33aa|\$ab956' local/win002/mame/cybotsu-0-c0000.asm   # and cybotsj's
```

2026-11-07, local. No cold boot, no keys.

## Actual Result

### The Saturn

- **The scene table** (`0x060AA840`) has 313 entries (307 distinct
  scripts), ending at the list table `0x060AAD24`. The count 335 used by
  `EXP-0022` and `tools.text.dialogue` (`SCENE_COUNT`) runs 22 words past
  it (the eleven list heads and 44 more bytes); read as script starts those
  only set where a script's scan stops, so earlier box lists are unchanged.
  Parsed to their `0xE000` end words instead, every script ends and names
  boxes 0-1,072 only.
- **The interpreter** (`0x0606E230`) has no jump: `E2`-`EA` set typing,
  cues, music, portrait and player state, `C0xx`-`DFxx` portraits. A
  posted scene shows every box in it, so rare Saturn text can only be a
  scene or box that nothing posts.
- **Every box classified** (`reachability.json`): 913 posted; 81 captions;
  68 win quotes (`VICTORY.BIN`'s table picks 71 of list 9's 72 scenes);
  box 555 (list 9 scene 1, never picked); box 609 (only in list 10, the
  speaker names, which no Saturn code posts); 10 boxes in no scene or table:
  63, 283, 290, 335, 494, 495, 552, 553, 938, 1073. Mary's and Gawaine's
  unposted scene 15 hold only boxes other posted scenes show.
- Read privately (no text committed): 63 and 335 are pilot introduction
  narrations, 283 and 290 short story lines, 494/495 the first caption
  (494 shares 496's record), 552/553/555 win quotes, 609 a speaker name,
  938 no line, 1073 a line of full-width spaces.

### The arcade

- **Readers by the listings' literals** (both sets, the same code 0x14
  apart where it moved): the caption drawer (`0x116F2`/`0x116DA`, Japanese
  only, UI-003); the dialogue reader (`0x11D52` `cybotsu`, `0x11D3A`
  `cybotsj`), which picks the table by region (`0x11D4C`); and a third
  (`0x97236`, both), which takes a slot and a language (0-2) from
  `0xFF44D2`/`0xFF44D0` and draws any slot from any table. It sits in a
  jump table of menu screens at `0x970A6` and is entered from a screen whose
  init clears both variables: a test-mode message viewer (SUPPORTED, not
  reached).
- **Read taps** (`reachability.json` `arcade_reader_pcs`): `cybotsu` read
  only its English table (`0x11F6A`, `0x12014`); `cybotsj` only its
  Japanese table (`0x11E7A`, `0x11F0E`, and the caption at `0x116E8`).
- **Posters:** every scene-message constant (`#$140000LL`) lies in the
  story code (`0x47380`-`0x4A5EE`, lists 0-5), the endings
  (`0x4BA1A`-`0x4D5E4`), the win quotes (`0x630C2`, list 6) and the speaker
  names (`0x631AC`, list 7: scene from a byte table `00 02 01 03 04 05 06
  00` indexed by an object's `+0xC`). No region test lies in any of them
  (the region tests are at the caption, the sign tiles and the table
  choice, UI-002/UI-003), and the story code calls no random routine (its
  most called, `0x1B9A`, resets objects).
- **A lead:** the US English slot 609 is not a speaker name but a
  "coming soon" style message (agent-read), while Saturn box 609 is a
  speaker name in list 10 (the arcade's list 7). When the arcade posts list
  7 scene 6, the US set would show that message.

## Conclusion

Prediction met. Saturn text no path shows: 12 boxes (10 with no reference,
555, 609). No random or region-gated story posting was found in the
arcade; its region choices are the dialogue table, the caption and the
city signs. One arcade lead remains: what the US set shows through list 7
scene 6 (slot 609). `TXT-011` forces it.

## Uncertainty and Alternatives

- "No random condition" rests on reading the posting code's calls and
  variables, not on a trace of every route; the `0xFF6B3x` variables the
  posts test (93-279 reads) were not all decoded.
- The test viewer is not reached; whether the Saturn has one was not
  searched beyond the box tables.
- `SPECIAL-001`'s lists 6-8 were classified but not examined further.
