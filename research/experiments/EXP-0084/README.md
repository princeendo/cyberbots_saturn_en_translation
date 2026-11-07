# EXP-0084: The Release Patch Built, Applied and Booted (REL-002)

Task: REL-002
Status: DONE
Confidence: CONFIRMED (built twice byte-identical; applied with a plain
`xdelta3` to the reference's Track 01; the header hash computed; the patched
disc booted to the title); SUPPORTED (that RetroAchievements lists the
header hash: a third-party mirror only)

## Observation

The final image is `data/regression/special018_saturn_only.json` (Track 01
`f6789cae…`). The release tools (`REL-001`) were ported from XvSF and
untried on Cyberbots. The image adds four files to Track 01, which an SSP
applier cannot express (`research/notes/rel002_research.json`).

## Hypothesis

`tools.disc.make_patch` makes an xdelta patch that any VCDIFF applier turns
an untouched Track 01 into the reference's, keeping the disc header.

## Controlled Change

None to the image. The user's decisions, asked first (verbatim in
`docs/localization_policy.md`, "Release Decisions"): "xdelta only
(Recommended)", "Record as untested (Recommended)"; the cold boot: "Yes,
run it now (Recommended)".

## Prediction

Two identical patches; `xdelta3 -d` gives `f6789cae…`; header MD5
`37674ab0…`; the patched disc boots to the title.

## Inputs and Provenance

| Input | SHA-256 |
| --- | --- |
| Untouched Track 01 (`local/disc_images/cyberbots_saturn_jp_2m`) | `758fa795…` |
| Built image `build/sp017/a/image` | Track 01 `f6789cae…`, cue `9f1248ad…` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/disc/make_patch.py` | The patch and its record (xdelta3 3.2.2, `-e -9 -S none -A -W 16777216 -f`) |
| `xdelta3 -d` (Homebrew 3.2.2) | The independent apply |
| `research/experiments/EXP-0067/attract.py`, `ffmpeg` | The no-input cold boot and its frames |

## Procedure

```bash
for k in 1 2; do ./invenv.sh python -m tools.disc.make_patch --built-dir build/sp017/a/image \
  --reference data/regression/special018_saturn_only.json --stem cyberbots_en \
  --out-dir build/rel002/run$k --record build/rel002/record$k.json; done
cmp build/rel002/run1/cyberbots_en.Track01.xdelta build/rel002/run2/cyberbots_en.Track01.xdelta
cp "<source Track 01>" SCRATCH/source_track01.bin
xdelta3 -d -s SCRATCH/source_track01.bin build/rel002/run1/cyberbots_en.Track01.xdelta SCRATCH/patched_track01.bin
shasum -a 256 SCRATCH/patched_track01.bin
python3 -c "import hashlib;d=open('SCRATCH/patched_track01.bin','rb').read(2352);print(hashlib.md5(d[16:528]).hexdigest())"
# local/rel002/patched: the patched Track 01, links to the untouched Tracks 02-62, the untouched cue
./invenv.sh python research/experiments/EXP-0067/attract.py local/rel002/boot \
  --cue "local/rel002/patched/Cyberbots - Fullmetal Madness (Japan) (2M).cue" --frames 3700
ffmpeg -i local/rel002/boot/run.mov -vf "select=eq(n\,3650)" -vframes 1 f3650.png   # then scaled to 352x240
```

2026-11-07, local.

## Actual Result

([`release/rel002_xdelta.json`](../../../release/rel002_xdelta.json))

- **Patch:** `cyberbots_en.Track01.xdelta`, 265,407 bytes, SHA-256
  `202f6e0e…`; the other 61 tracks and the cue unchanged. Both runs gave
  the same bytes and equal records; `make_patch`'s own decode round trip
  passed.
- **Independent apply:** `xdelta3 -d` on a copy of the untouched Track 01
  gave `f6789cae…`, the reference's.
- **Header:** the MD5 of the first 512 user-data bytes of sector 0 is
  `37674ab0fe794821dfd080116e1a10ba` for both the source and the patched
  track (`SEGA SEGASATURN `).
- **Cold boot** (no key): the Capcom logo (frame 1,700) and the title
  screen with "PRESS START BUTTON" (frame 3,650, `e9f12474…` as 352x240);
  8 named file opens and 14 audio starts by frame 3,700.

## Conclusion

Prediction met. The xdelta patch is the release patch; there is no SSP for
this image.

## Uncertainty and Alternatives

- RetroAchievements: the header hash is unchanged; that RA lists it is
  SUPPORTED by a mirror only, and whether achievements trigger on the
  patched game is untested (the user's choice).
- The boot went only to the title; the image's play was checked in
  `SPECIAL-018` and earlier play checks.
- Real hardware: deferred by the user.
