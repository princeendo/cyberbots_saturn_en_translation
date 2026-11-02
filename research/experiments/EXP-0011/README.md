# EXP-0011: Recorded Play Session and the Saturn Text Surfaces

Task: REF-005
Status: DONE
Confidence: CONFIRMED (surfaces seen and their language); UNKNOWN (surfaces not reached)

## Observation

The boot and attract captures (`EXP-0001`, `EXP-0002`) showed no Japanese
except stage signage. The story dialogue is a Shift-JIS table (D-008), but
which other surfaces show Japanese in play was unknown. XvSF's single session
missed five surfaces (`docs/lessons_from_xvsf.md`, lesson 6), so this record
also lists what was not reached.

## Hypothesis

In one ordinary arcade-mode run (title, pilot and mech select, two fights,
a loss, the continue countdown, game over, options), Japanese text appears
only in the story dialogue boxes; other screens are English.

## Controlled Change

None to the game. The user played; the agent only recorded.

## Prediction

Japanese only in dialogue boxes; English menus, HUD, result and continue
screens.

## Inputs and Provenance

- Untouched image (Redump 58190), stock-identical patched binary
  (`2fc3d547…eaaf`, D-007), interactive home `local/mednafen/` (config
  `cb1c2d3b…a1e9`, sibling pad bindings), BIOS `sega_101.bin`.
- Source manifests before and after: `local/ref005/source-*.json`
  (identical).

## Tools and Environment

`tools/mednafen/session_recorder.py --keep-states 0` (copied from XvSF,
`ENV-003`; first use here, and it re-validates it on Cyberbots: every
screenshot and state was written, the STOP file ended it cleanly) attached
through the agent interface (`local/ref005/agent`). ffmpeg 9.0.1 contact
sheets for review.

## Procedure

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" MEDNAFEN_AGENT_DIR="$PWD/local/ref005/agent" \
  vendor/mednafen/build-agent/src/mednafen \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" &
./invenv.sh python -m tools.mednafen.session_recorder local/ref005/session \
  --agent-dir local/ref005/agent --keep-states 0 &
# the user plays the ten-step route below, then: touch local/ref005/session/STOP
```

The route given to the user (2026-11-02): boot; Start at the title; the
first menu item; Jin and any mech; let every box finish; win fight 1 trying
each button; lose fight 2; let the continue countdown reach zero; at the
title open the options and move through every row; leave Mednafen open. The
user's report: "done" (no button reported as unresponsive).

Review: consecutive identical screenshots dropped (484 → 367 unique), then
8 contact sheets of 48, every tile reviewed by the agent; picks re-checked
at full size.

## Actual Result

- Session 16:22:43-16:31:03 local, frames 384-29,445: 484 screenshots, 166
  states (all kept, 346 MB, ignored `local/ref005/session/`). Mednafen
  closed by SIGTERM; the interactive config hash is unchanged; the game
  wrote backup RAM to `local/mednafen/sav/`.
- Route as played: title → `ARCADE MODE` → `PILOT SELECT` (Jin, 10
  portraits) → `MACHINE SELECT` (BLODIA) → introduction → pre-fight
  exchange (Jin and Shade) → VS screen → fight 1 won (`TARGET DESTROYED`,
  `BONUS`) → post-fight exchange → scene with Gawaine → VS screen → fight 2
  lost (`MISSION TERMINATED`) → `CONTINUE?` 20 → 0 → `GAME OVER` →
  initials → title → `OPTION MODE`.
- Surfaces and their language: `docs/text_surfaces.md`. **Japanese text
  appeared on three surfaces**, not one:
  1. story dialogue boxes (introduction, pre- and post-fight);
  2. a caption box on the VS screen naming the chapter (Saturn lines 899
     and 900 in this run);
  3. pilot and mech names drawn as katakana art on the pilot select and VS
     screens.
  Everything else seen is English: menus, select labels, HUD, banners,
  round results, bonus, continue, game over, initials, options (including a
  `3M RAM MODE` row).
- **The VS captions are dialogue-table lines.** The two captions are, byte
  for byte, Saturn script lines 899 and 900, found in the same place in
  `VICTORY.BIN`, `END.BIN` and `STG0AS.BIN`. Lines 899-952 are 54 short
  lines (6-12 characters) like them. So the Saturn-only block (D-011) begins
  with chapter captions; Chiyomaru and Tessan are named only from line 1141.

## Conclusion

**CONFIRMED for the surfaces seen:** Japanese appears in dialogue boxes, VS
chapter captions (lines of the same table, with no arcade counterpart) and
katakana name art. The prediction (dialogue boxes only) is **DISPROVEN**.
Endings, versus mode, option sub-screens, warnings and the console-only
pilots were not reached.

## Uncertainty and Alternatives

- That lines 899-952 are all chapter captions rests on two observed lines
  and the lengths of the rest.
- The name art may come in several sizes; whether English or other name art
  exists on the disc (as both siblings found) is `REF-007`.
- Which Saturn button does what in play was not noted beyond "no button
  unresponsive".

## Reproduction

Run the procedure with a player. Evidence stays in the ignored
`local/ref005/` (`session/shots`, `session/states`, `session/index.tsv`,
`review/` sheets and `picks.json`).
