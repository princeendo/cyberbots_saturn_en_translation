# EXP-0012: Pilot and Mech Names Across the Releases

Task: REF-007
Status: DONE
Confidence: CONFIRMED (names in the scripts, where names are art, the Saturn VS name art's source file); UNKNOWN (Latin name art on the Saturn disc; voices)

## Observation

Both siblings found names that differ between conventions (Vega/Bison,
Gouki/Akuma), with both conventions' art and voice on their discs. The user
chose "Both variants, US default" (`DOC-002`). In the play session (D-012)
the Saturn showed pilot and mech names as katakana art on the pilot select
and VS screens.

## Hypothesis

Cyberbots' Japanese and US releases use different names for some characters,
and the Saturn shows them as katakana art whose Latin counterparts exist in
the US arcade.

## Controlled Change

None. Static comparison of the scripts, MAME snapshots of the arcade sets on
the `EXP-0009` route, and one session state's VRAM.

## Prediction

At least one pilot or mech name differs between the arcade English and the
Saturn Japanese.

## Inputs and Provenance

- Arcade English text (D-009, decoded to the ignored `local/ref003/`), the
  Saturn script (D-008).
- MAME runs of `cybotsj` ([`timelines/`](timelines/)); `EXP-0009` run 2's
  `cybotsu` snapshots.
- Session state `local/ref005/session/states/f00006805.mcs` (SHA-256
  `96cba2c8…`), VS screen 1; `SELECT.VAD` (`c1b467cf…`).

## Tools and Environment

`tools/memory/mcs_extract.py` (VDP1 VRAM validated, D-006),
`tools/memory/vdp1_sprites.py` (copied from XvSF; first use here: it walked
150 commands and rendered them recognizably, which re-validates it for
listing and identification), scratch searches.

## Procedure

1. Speaker labels (English slots ending in `:`) and frequent capitalized
   words in the arcade English; candidate katakana spellings counted in
   Saturn lines 0-898 and 899-1850.
2. MAME snapshots: `cybotsu` pilot select and VS screen (`EXP-0009` run 2,
   frames 1300-4800); `cybotsj` pilot select (run 1, frame 1000) and VS
   screen (run 2, frames 3560-3780).
3. VDP1 sprites of the state at frame 6805 (VS screen); the pilot-name and
   mech-name sprites' pixel data searched as bytes in all 264 data-track
   files.

## Actual Result

- **Names** (`docs/names.md`): every pilot named in both scripts has the
  same name in both, only in a different script; no name differs. Arcade
  speaker labels: Arieta, Bao Mao, Bao, Chiyomaru, Customer, Devilotte, Gary,
  Gawaine, Jin, Mao, Mary, SHADE, Santana, Xavier. Tessan has no arcade
  English; Chiyomaru and Devilotte appear in the arcade English though they
  are not arcade pilots.
- **Art:** the US arcade shows Latin names on its pilot select ("Jin") and VS
  screen ("Jin", "SHADE", "BLODIA", "R-LIGHTNING"); the Japanese arcade and
  the Saturn show katakana there. The Japanese arcade's VS screen also shows
  the chapter caption seen on the Saturn; the US arcade shows none. The HUD
  is Latin everywhere.
- **Saturn VS name art:** VDP1 sprites (150 commands at frame 6805), e.g. the
  pilot name 64×15 4 bpp at VRAM `0x096E0`, a mech name 104×23 at
  `0x09900`. Their pixel bytes occur verbatim in `SELECT.VAD` at `0x1EE80`
  and `0x1F0A0`, so the art is stored uncompressed there.
- **Latin name art on the Saturn disc:** not found. Rendering `SELECT.VAD`
  around `0x1EE80` as 64×15 blocks or 64-pixel strips shows no readable name
  list. Not concluded either way.

## Conclusion

The hypothesis is **DISPROVEN** for names: no name differs between the
Japanese and US releases. Names differ only in script, on the pilot select
and VS screens. The Saturn's VS name art is raw sprite data in `SELECT.VAD`.
Whether Latin name art exists on the disc is **UNKNOWN** (`LOC-001`).

## Uncertainty and Alternatives

- Name spellings were counted for guessed katakana forms; Gary, Xavier and
  Murdock were not found and may be spelled differently or absent.
- The arcade's own Latin name art lives in the CPS-II graphics ROMs (not
  decoded here); it could serve as a model if the Saturn has none.
- Voices were not checked.

## Reproduction

Run the procedure; expect the tables in `docs/names.md`.
