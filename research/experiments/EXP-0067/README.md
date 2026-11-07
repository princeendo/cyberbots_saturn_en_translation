# EXP-0067: Census of the Remaining Japanese UI (UI-001, part 1)

Task: UI-001 (the census; the font inventory is part 2)
Status: DONE (part 1)
Confidence: CONFIRMED for the screens recorded; SUPPORTED (code only) for
`SOUND TEST` and `DATA RESET` having no screen of their own

## Observation

`docs/text_surfaces.md` listed the option sub-screens and the attract loop
beyond two minutes as never seen, and only two VS captions as seen.

## Hypothesis

Outside the story dialogue and the endings, the current image
(`data/regression/opt006_names_switch.json`) still shows Japanese only on
the VS chapter captions and in stage art.

## Controlled Change

None to the disc. One no-input cold boot of the current image (recorded,
every frame); saved-state runs with RAM writes; MAME runs of both arcade
sets.

## Prediction

No Japanese UI text beyond the captions; the candidate attract files named
by the outline may not load at all.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Current image | `build/opt005/a` (Track 01 `357f5b65…`) |
| Untouched image | for state runs whose files the builds do not change |
| Session states | `local/ref005/session/states/` (6448 before a VS screen, 25772 attract, 27173 Options) and its 484 screenshots |
| Versus states | `local/win002/*/post.mcs` (`EXP-0032`) |
| Arcade | `cybotsu`, `cybotsj`, MAME 0.289 (`references/arcade/README.md`) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`attract.py`](attract.py) | No-input cold boot, `-qtrecord` (every frame), CD and named-load log |
| [`attract_long.py`](attract_long.py) | 48,000 attract frames from state 25772, a screenshot every 60 → [`attract_long.json`](attract_long.json) |
| [`captions.py`](captions.py) | Every VS caption by forcing pilot and stage, with a font and code table written in → [`captions.json`](captions.json) |
| [`screens.py`](screens.py), `EXP-0056/poke.py` | KEY CONFIG, versus `VICTORY!`/`RESULT` → [`screens.json`](screens.json) |
| Agents (read-only) | Review of the 484 session shots (17 sheets) and the 980 attract scene changes; MAME attract runs of both sets → [`arcade_attract.json`](arcade_attract.json) |

## Procedure

```bash
E=research/experiments/EXP-0067
./invenv.sh python $E/attract.py local/ui001/attract            # 9 min, no key (asked first)
#   the log was decoded by streaming local/ui001/attract/agent/events.log -> attract_loads.json
ffmpeg -i local/ui001/attract/run.mov -an -vf "scale=352:240:flags=area,select='gt(scene\,0.10)+eq(n\,0)',showinfo" \
  -fps_mode vfr local/ui001/attract/scenes/s%05d.png
./invenv.sh python $E/attract_long.py local/ui001/attract_long
./invenv.sh python $E/captions.py local/ui001/captions
./invenv.sh python $E/captions.py local/ui001/captions-untouched --build local/ui001/untouched_build
./invenv.sh python $E/screens.py local/ui001/screens
./invenv.sh python research/experiments/EXP-0056/poke.py local/ui001/kc2 --state local/ref005/session/states/f00027173.mcs \
  --write 0606BE8C=00000006 --write 060CFEE4=0000 --write 060CFEE0=0003 --frames 600 --shots 120,300,600
```

2026-11-06, 18:20-19:30 local. One cold boot with no key, asked first:
"Yes, run it now (Recommended)".

## Actual Result

### Attract loop

- **Cold boot** (32,012 frames recorded; load log to frame 30,044): boot
  (BIOS, SEGA licence, CAPCOM logo), then the cycle: CAPCOM logo, intro
  (3D shots, pilot portraits, a mech-blueprint parade with English part
  labels), title with `PRESS START BUTTON`, the two demo mechs' blueprints,
  `NOW LOADING`, a CPU demo fight, `NOW LOADING`, `RANKING`. Cycles start
  about every 5,530-5,860 frames; five cycles recorded. All text English.
- **Long run** (48,000 frames from state 25772): eight cycles; the demo pair
  rotates through six: BLODIA vs REPTOS, KILLERBEE vs LIGHTNING, JACKAL vs
  FORDY, SWORDSMAN vs CYCLONE, RIOT vs VICE, TALANTURA vs GULDIN; cycles 7-8
  repeat 1-2, so two cycles in a row added no new screen. The blueprint
  parade alternates between two sets of six mechs.
- **The only Japanese:** painted signs (banners, shop signs, a sale banner)
  in the background of the first demo's ruined-city stage. `cybotsj` shows
  the same signs; **`cybotsu` shows the same stage with those signs blank**
  (the red vertical banner and the shop signs are there, without writing:
  `cybotsu_f01500` against `cybotsj_f01500`, checked by the agent).
- **Ranking:** the same five entries every cycle (the names `CAP`, `COM`,
  `CP`, `SYS`, `TEM`), as in both arcade sets.
- **Files loaded** (`attract_loads.json`): `OPDEMO.BIN`, `OPS0_0/1.BIN`,
  `OPS00.PIX`, `OPS10.PIX`, `CAPCOM.PIX`, `RANKBG.PIX`, `FIX.BIN`,
  `SOUND.LF`, the demo stages' and mechs' files, audio tracks. **Not
  loaded:** `STDEM*`, `VADEM*`, `STDEMO.*`, `OPDEMO_0.BIN`, `CYB_ABS.TXT`.
- The scene detector missed fades (logo, title, loading, ranking); the
  reviewers also read every 15th frame. The scene index's frame numbers
  drift slightly (the recording runs at about 59.83 fps, not 59.94).

### Menus and modes

- **Session screenshots** (484, title to game over and Options): Japanese
  only on the known surfaces (story boxes, the VS caption, katakana names on
  the untouched image). Continue, game over, initials, title, `OPTION MODE`,
  the fights and the bonus tally are English; no Japanese stage signs in the
  stages played.
- **`KEY CONFIG`** (state 27173, menu state 3 with the cursor on row 6):
  English only (title, `PLAYER 1`/`2`, the buttons with `ATTACK1`,
  `ATTACK2`, `BOOST`, `WEAPON`, `PRESS START TO EXIT`). A first try that
  also wrote the whole `OPDEMO.BIN` hung in a fade (the overlay's live
  variables were overwritten).
- **`SOUND TEST`, `DATA RESET`** (code, `EXP-0062`): their row handlers play
  a sound or call `0x060372A4` and draw nothing of their own (SUPPORTED).
- **Versus `RESULT`**: English (state runs, `screens.json`). The
  `VICTORY!` quote in these old states is Japanese; the M5 build makes it
  English (D-030).
- **`EXTRA OPTIONS`**, versus select, `SET UP`, VS: as seen on the
  `EXP-0066` cold boots, English (names per the switch).

### VS chapter captions (`captions.json`)

All 81 forced (pilots 0-8 × stages 0-8) on the current image, with its font
and code table: the reader drew exactly the table's box each time
(`0x0609CC22`, boxes 496-549 and 1045-1071), which confirms the mapping.
Compared with the same captions drawn with the untouched font, exactly five
differ in the caption box: **512** (Mary, stage 7), **539** (Gawaine,
stage 7), **1070**, **1052**, **1053** (Saturn-only pilots 6 and 8). In
each, one character draws an English pair glyph (for example, box 512's
first character reads "Hi"). This is the effect the user accepted at the M5
gate ("5 VS captions"). Boxes 494-495 are not in the table.

### Arcade (`arcade_attract.json`)

Headless MAME, no input: `cybotsu` 40,021 frames (6 cycles), `cybotsj`
45,000 frames (8 cycles). Every overlay and screen is English in both (the
region warnings too). The city stage's signs are Japanese in `cybotsj` and
blank in `cybotsu`: the US release removed that writing from the art. The
US arcade shows no VS caption (`EXP-0012`).

## Conclusion

Prediction met. Outside story dialogue and endings, the current image shows
Japanese only on the VS chapter captions (five of them with one wrong
glyph each, as accepted at M5) and in stage art: the first demo's city
signs, which the Japanese arcade shares and the US arcade shows blank. None of the outline's other attract candidates
load. Part 2 (the English art in the fonts) follows.

## Uncertainty and Alternatives

- Stage art was seen only for the stages in the demos and the session; the
  other stages' signs are not inventoried.
- The arcade's select, continue and ranking screens were not run beyond the
  attract (no Japanese surface needs them so far).

## Reproduction

Run the procedure. Expect the committed JSON records (screenshot hashes
vary between runs).
