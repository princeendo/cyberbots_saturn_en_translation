# EXP-0088: Does the Patch Change the Game's Sound? (Mednafen)

Task: none (the user's report, 2026-11-12)
Status: DONE
Confidence: SUPPORTED. In Mednafen the patched image adds no sound: its
audio is the original's, sample for sample, except where single sounds
start up to about 3,000 samples (63 ms) apart. Real hardware not tested.

## Observation

The user (2026-11-12, verbatim): "when I burned the disc, I think there's
something wrong on real hardware. I feel like I'm getting problems in the
sound. It's making like a buzzing sound when running. I can't 100% verify
that it's not my TV or something, but is there a way to check through and
verify that we don't expect sound issues? Maybe by trying a different
emulator?"

The release changes no audio track (tracks 02-62 are the player's own) and
none of the 22 changed or added track 01 files is sound data in any
discovery (`SE.DAT` is the endings' font, D-035). With default settings
(`NAMES ENGLISH`, `SIGNS BLANK`) the hooks load no tail file (D-058, D-062).

## Hypothesis

From the same cold boot with no input, the original and patched images
give the same audio, apart from timing where the game runs different code
(text drawing).

## Controlled Change

The disc image only: the untouched original vs the patched builds, in the
same Mednafen home (same backup memory and settings), same recorder.

## Prediction

Identical samples where both games do the same thing; elsewhere the same
sounds at the same level, shifted; no added steady tone or noise; silent
passages exactly zero in both.

## Procedure

```bash
# A cold boot of the untouched image, no input, 7,600 frames (the user: "Yes, run it now (Recommended)")
MEDNAFEN_ALLOWMULTI=1 ./invenv.sh python research/experiments/EXP-0067/attract.py local/snd001/original \
  --cue "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" --frames 7600
# compared with the earlier no-input cold boots of patched builds:
#   local/ui007/attract/run.mov (build/ui006/b, 7,600 frames, EXP-0073)
#   local/rel002/boot/run.mov   (the 0.1.0 release image from the xdelta, EXP-0084)
./invenv.sh python research/experiments/EXP-0088/compare_audio.py local/snd001/original/run.mov local/ui007/attract/run.mov
./invenv.sh python research/experiments/EXP-0088/compare_audio.py local/snd001/original/run.mov local/rel002/boot/run.mov
./invenv.sh python research/experiments/EXP-0088/compare_audio.py local/ui007/attract/run.mov local/rel002/boot/run.mov
```

2026-11-12, local; the agent-interface Mednafen build (D-007), 48 kHz
stereo. The original's run logs a missing `.sbi` (none exists for the
untouched image; Mednafen goes on).

## Actual Result

- **Patched vs patched** (release vs `ui006/b`, 62.8 s): identical.
- **Original vs release** (62.8 s) and **original vs `ui006/b`** (127.6 s):
  identical up to 59.127 s (boot, logos, title music). Then, per second
  (left channel):
  - 60-63 s: the same sound 61 samples later (difference RMS 1,240 → 5
    aligned);
  - 69-72 s and 90-105 s: some seconds differ, their neighbours (70, 73 s)
    are identical; RMS within 2% (e.g. 5,041 vs 5,072); a lag of tens of
    samples leaves a residual of about half the signal, as when separate
    sounds move by different amounts;
  - 108-127 s: identical again.
  - Every silent second is exactly zero in all three recordings.
- Disc loads (`loads.json`): the same 91 loads; only `M3PL00_0.BIN` opens
  one frame later in the patched run (frame 4,994 vs 4,993).
- The release recording: peak -1.6 dBFS, no clipped runs (flat factor 0),
  DC offset 0.001.

## Conclusion

Prediction met. Emulated, the patch changes when a few sounds play, by
milliseconds, and nothing else; no buzz or noise is added. Which sounds
move is not identified (HYPOTHESIS: the text-typing sound, as the English
text has other glyph counts).

## Uncertainty and Alternatives

- **Emulation only.** An analog buzz (console, cables, TV), or one from
  reading a CD-R's audio tracks, cannot show in Mednafen's output.
  Discriminating checks on the user's console: the burned disc's audio
  tracks in the Saturn's own CD player (no game code runs); the retail
  disc, or an unpatched burn made the same way, in the same setup.
- Covered: 128 s of boot, title and attract. Not covered: story scenes,
  menus, select, endings, the NAMES/SIGNS tail-file loads.
- One emulator. A second emulator would test Mednafen, not the patch.
