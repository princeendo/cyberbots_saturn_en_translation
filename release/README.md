# Release Patch: Cyberbots: Fullmetal Madness (Saturn) in English

This folder describes the English patch for the Japanese Sega Saturn release
of **Cyberbots: Fullmetal Madness** (Capcom, 1997, T-1217G): what it changes,
how to apply it, and how to rebuild it from this repository.

**The patch files are not in the repository.** Their bytes include
game-derived data, which this project never commits (`AGENTS.md` rule 21).
They are published as GitHub Release assets.

[`cyberbots_en.json`](cyberbots_en.json) is the xdelta patch's record
(hashes, sizes, xdelta3 version and flags), and
[`rel002_xdelta.json`](rel002_xdelta.json) the checks it passed: metadata
only. [`cyberbots_en.ssp.json`](cyberbots_en.ssp.json) records the withdrawn
`.ssp` (see "Why there is no .ssp patch").

## What the Patch Changes

One image (regression reference
[`special018_saturn_only`](../data/regression/special018_saturn_only.json)):

- **Story dialogue, versus win quotes and endings of the six arcade pilots**
  (Jin, Santana, Mary, Arieta, Gawaine, Bao and Mao): the official US arcade
  English. The cast roll's Japanese name images are hidden and the QSound
  notice's Japanese line is removed, as the US arcade has neither.
- **The three Saturn-only pilots** (Devilotte, Chiyomaru and SHADE): their
  stories, win quotes, VS captions and endings in a new English translation
  (there is no official one), made by Claude and approved by the project's
  owner pilot by pilot. Chiyomaru is three moves left of Jin on the pilot
  select.
- **VS chapter captions** of every pilot: new English (the US arcade showed
  none).
- **Boot warnings** (damaged save, unformatted memory, no room to save): new
  English pictures.
- **Pilot and mech names** on the pilot-select, `SET UP` and VS screens:
  Latin art in the arcade's letters, including the unlockable ZERO-AKUMA.
- **Two new settings** in OPTION MODE's new `EXTRA OPTIONS` row, both saved
  with the other options:
  - `NAMES  ENGLISH / JAPANESE`: `JAPANESE` brings back the original katakana
    and kanji name art. `ENGLISH` is the default.
  - `SIGNS  BLANK / ENGLISH / JAPANESE`: the ruined-city stage's shop signs
    without writing (`BLANK`, the default, as the US arcade), lettered in
    English, or as the original.

Everything else plays as the original game.

## Apply the Patch

### You need

1. **The original disc image**, as BIN/CUE with 62 tracks: Redump disc 58190
   ("(2M)", T-1217G, version 1.002). Only track 01 is patched, and it must be
   the original:

   | Component | Size (bytes) | SHA-256 |
   | --- | ---: | --- |
   | `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin` | 103001136 | `758fa7956aa6139460c391ec5225e69cc9cde13dfe2281e8c544e594d201dbd1` |
   | `Cyberbots - Fullmetal Madness (Japan) (2M).cue` | 8499 | `9f1248adc58b225fa55aa2960df36113212ff200c26917a8c40f22f2cb9c5f14` |

   Tracks 02-62 are listed in
   [`references/saturn_jp/README.md`](../references/saturn_jp/README.md).
   Redump's Limited Edition disc 3669 ("(1M)") has the same track 01 and
   different audio tracks, so the patch applies to it too: keep your own
   audio tracks and CUE.
2. **A VCDIFF patcher:** xdelta3 (3.2.2 is tested), or any program that
   applies xdelta / VCDIFF patches.

### Steps

```bash
xdelta3 -d -s "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin" \
  cyberbots_en.Track01.xdelta "Track 01 patched.bin"
```

1. Run it in the folder with the original image. The patch is plain VCDIFF:
   no secondary compression, a 16 MiB window, no application header.
2. The result's SHA-256 must be
   `f6789cae74814ab82d8060db3b50a99906b668bacfe950d1e0850ac4d01d25e0` (also in
   the zip's `README.txt`, "patched track 01").
3. Replace track 01 with it under its original file name, so the CUE still
   finds it. Keep tracks 02-62 and the CUE.

The game needs the same hardware as the original. It was played in Mednafen
(`ss.cart auto`).

### Why there is no .ssp patch

There is no Sega Saturn Patcher (`.ssp`) patch. One was built, attached to
the 0.1.0 release on 2026-11-07, and withdrawn on 2026-11-13:

- **The English image adds four files to track 01** (`ZNAMES1.BIN`,
  `ZNAMES2.BIN`, `ZSIGNS1.BIN`, `ZSIGNS2.BIN`: the `NAMES` and `SIGNS`
  settings' data). An `.ssp` must create them as new-file (`._NEW`)
  entries. The `.ssp` built holds them, and its entries together give
  exactly the English track 01 (`EXP-0086`).
- **The open-source `saturn-patcher-egui` cannot add files.** With it the
  `NAMES` and `SIGNS` settings would fail.
- **The official Sega Saturn Patcher 1.91 (Windows) adds them, but its
  output is not a usable disc.** Applied to the untouched 62-track BIN/CUE,
  it wrote a single-BIN image whose 22 changed and added files all match,
  but which is 1,050,753,648 bytes (446,749 sectors, about 99 minutes)
  against 591 MB (about 56 minutes) for the original set, too long for a
  CD; its CUE puts the short music tracks minutes apart (`EXP-0087`). Why
  is not known (a likely cause, untested: it copies the 61 directory
  entries that point at music tracks into the data track as files).

The xdelta patch has neither problem: it changes track 01's bytes in place
and keeps every track where it was.

## Known Limits

- **Real hardware:** played in Mednafen, and on a real Saturn from a
  Satiator (the patched BIN/CUE on its SD card). A burned CD-R has not been
  confirmed: one report of a buzzing sound from a burned disc is unresolved,
  and in Mednafen the patch adds no sound (`EXP-0088`).
- **RetroAchievements:** the disc header RetroAchievements identifies the
  game by is unchanged (MD5 `37674ab0fe794821dfd080116e1a10ba`). Whether the
  achievements still trigger on the patched game has not been tested.
- **Still Japanese:** six story-only name banners in the VS screen's bank
  whose screen was never found; text the game never shows (dead boxes). Full
  register: [`docs/coverage_exceptions.md`](../docs/coverage_exceptions.md).
- **Not seen:** whether an unlocked machine select draws a label for the
  extra bodies.

## Rebuild the Patch from This Repository

You supply the original image, the MAME arcade sets and driver source, and
the arcade glyph capture; see the top-level [`README.md`](../README.md),
"Files You Need". Then:

```bash
# 1. The release image, checked against its regression reference (all hashes must match).
./invenv.sh python research/experiments/EXP-0055/regress.py special018_saturn_only
# 2. The patch, checked against the reference (the image is in build/regress/special018_saturn_only/image).
./invenv.sh python -m tools.disc.make_patch --built-dir build/regress/special018_saturn_only/image \
  --reference data/regression/special018_saturn_only.json --stem cyberbots_en \
  --out-dir build/release/patch --record release/cyberbots_en.json
# 3. The zip, and a check that applies the patch from it.
./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0 --kinds xdelta \
  --patches build/release --variant cyberbots_en patch \
  "English translation (all pilots, endings, UI; NAMES and SIGNS settings)"
./invenv.sh python -m tools.release.check_zips 0.1.0 build/release/v0.1.0 local/rel/v0.1.0-check \
  --kinds xdelta --expect f6789cae74814ab82d8060db3b50a99906b668bacfe950d1e0850ac4d01d25e0
```

Every step refuses a source or build whose hashes differ from the records.
The withdrawn `.ssp` was made with `tools.disc.make_ssp --add-new`; its
command is in `research/experiments/EXP-0086/README.md`.
The full procedure for publishing is [`RELEASING.md`](RELEASING.md).
