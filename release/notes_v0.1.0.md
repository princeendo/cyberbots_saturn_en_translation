# Cyberbots: Fullmetal Madness (Saturn) English 0.1.0

An English patch for the Japanese Sega Saturn release of Cyberbots:
Fullmetal Madness (Redump disc 58190, T-1217G, version 1.002; the Limited
Edition disc 3669 shares its track 01).

## What's in English

- Every pilot's story, versus win quotes and ending:
  - the six arcade pilots (Jin, Santana, Mary, Arieta, Gawaine, Bao and Mao)
    in the official US arcade English;
  - the three Saturn-only pilots (Devilotte, Chiyomaru, SHADE) in a new
    translation, as there is no official one.
- The VS chapter captions before each fight, and the boot warnings about
  the save memory.
- Pilot and mech names on the select and VS screens, including the
  unlockable ZERO-AKUMA.
- **Two new settings** in OPTION MODE, `EXTRA OPTIONS`, saved with your
  options:
  - `NAMES`: English name art (default) or the original Japanese.
  - `SIGNS`: the ruined-city shop signs blank (default, as the US arcade),
    in English, or the original Japanese.

## Download

| File | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `cyberbots_saturn_en_0.1.0_xdelta.zip` | 245,322 | `b0188f0e3baf7d93608e1c923f153bbb315d5308760762fc1c9505034775154c` |

The zip holds the patch and a `README.txt` with the source and target
hashes. Only track 01 changes.

## Apply

See [`release/README.md`](https://github.com/princeendo/cyberbots_saturn_en_translation/blob/main/release/README.md):
xdelta3, or any VCDIFF patcher, on the original track 01.

### Why there is no .ssp patch

The English image adds four files to track 01 (the `NAMES` and `SIGNS`
settings' data), which a Sega Saturn Patcher (`.ssp`) patch must create:

- the open-source saturn-patcher-egui cannot add files;
- the official Sega Saturn Patcher 1.91 (Windows) did add them, but for this
  62-track disc its rebuilt image was about 99 minutes (1.05 GB, against
  about 56 minutes for the original), too long for a CD, with the music
  tracks moved.

An `.ssp` was briefly attached to this release and has been withdrawn. Details:
[`release/README.md`](https://github.com/princeendo/cyberbots_saturn_en_translation/blob/main/release/README.md).

## Known Limits

- Played in Mednafen, and on a real Saturn from a Satiator. A burned CD-R
  has not been confirmed.
- The RetroAchievements disc hash is unchanged; whether achievements still
  trigger was not tested.
- A few name banners whose screen was never found, and text the game never
  shows, stay Japanese. Full list:
  [`docs/coverage_exceptions.md`](https://github.com/princeendo/cyberbots_saturn_en_translation/blob/main/docs/coverage_exceptions.md).
