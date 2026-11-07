# EXP-0085: The Release Zip, Its Check and the Release Docs (REL-003)

Task: REL-003
Status: DONE
Confidence: CONFIRMED (the zip built twice byte-identical, and again by the
documented commands from a clean rebuild; `check_zips` applies the patch
from the unpacked zip to the reference's Track 01)

## Observation

`REL-002` (`EXP-0084`) made and proved the xdelta patch; the user chose
xdelta only. `tools.release.make_zips` and `check_zips` (ported in
`REL-001`) always made and checked both an xdelta and an SSP zip.

## Hypothesis

With a `--kinds` option, the tools make and check one reproducible xdelta
zip whose readme names the source, the patch and the patched track's
hashes; the documented commands rebuild it byte for byte.

## Controlled Change

`--kinds` in `tools/release/make_zips.py` and `check_zips.py` (default both,
so earlier behaviour and tests are unchanged; two new tests). The release
record `release/cyberbots_en.json` (`make_patch`'s `STEM.json`). New docs:
`release/README.md`, `release/RELEASING.md`, `release/notes_v0.1.0.md`; the
top-level `README.md`.

## Prediction

Two identical zips; `check_zips --expect f6789cae…` exits 0; the documented
route gives the same zip.

## Procedure

```bash
for k in a b; do ./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0-$k \
  --variant cyberbots_en run1 "English translation (all pilots, endings, UI; NAMES and SIGNS settings)" \
  --patches build/rel002 --kinds xdelta; done
cmp build/release/v0.1.0-a/*.zip build/release/v0.1.0-b/*.zip
./invenv.sh python -m tools.release.check_zips 0.1.0 build/release/v0.1.0-a local/rel003/check \
  --kinds xdelta --expect f6789cae74814ab82d8060db3b50a99906b668bacfe950d1e0850ac4d01d25e0
# then, from clean folders, the commands in release/README.md "Rebuild the Patch" (steps 1-3)
```

2026-11-07, local.

## Actual Result

- **Zip:** `cyberbots_saturn_en_0.1.0_xdelta.zip`, 245,322 bytes, SHA-256
  `b0188f0e3baf7d93608e1c923f153bbb315d5308760762fc1c9505034775154c`; both
  builds identical. Members (date 1980-01-01): `README.txt` (946 bytes: the
  image, the untouched track 01 `758fa795…`, the patch's size and
  `202f6e0e…`, the patched track 01 `f6789cae…`, the apply command, the
  docs' URL) and `cyberbots_en.Track01.xdelta` (265,407 bytes).
- **Check:** `check_zips` printed the source `758fa795…` and the patched
  `f6789cae…`; exit 0.
- **Documented route:** the regression rebuild of `special018_saturn_only`
  (all match), `make_patch` (the record unchanged), `make_zips` and
  `check_zips` gave the same zip, `b0188f0e…`.
- **Tests:** 269 pass (2 new: an xdelta-only release, an unknown kind
  refused).

## Conclusion

Prediction met. The 0.1.0 zip is ready for `REL-004` (tag and publish).

## Uncertainty and Alternatives

- The zip and docs are untested by anyone outside this machine; the apply
  steps use only `xdelta3 -d`, as tested in `REL-002`.
