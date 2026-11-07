# EXP-0086: An SSP Patch That Adds Files (REL-004)

Task: REL-004
Status: DONE
Confidence: CONFIRMED that the `.ssp` holds a complete description of the
built track 01 (built twice byte-identical; every entry checked two ways).
UNKNOWN whether any patcher applies it: only the official Sega Saturn
Patcher could, and it was not run.

## Observation

The user (2026-11-07, verbatim): "I actually want to create the SSP patch. I
know we can't test it fully. But let's try it anyway." `REL-002` had chosen
xdelta only because the release image adds four root files to track 01
(`ZNAMES1.BIN` LSN 43643, 8,640 bytes; `ZNAMES2.BIN` 43648, 38,700;
`ZSIGNS1.BIN` 43667, 63,872; `ZSIGNS2.BIN` 43699, 63,872) and
`make_ssp.changed_files` refuses a changed directory. A sector census of the
source and built track 01 (same length) found every differing sector inside
a changed existing file, a new file, or LSN 27, the root directory.
MSHvSF's decompile of the official patcher (its `EXP-0084`) lists a `._NEW`
entry kind beside `._DFR`; its format is not documented there (HYPOTHESIS:
the whole file).

## Hypothesis

An `.ssp` with one `._DFR` per changed file, one `._NEW` per added file
(whole file bytes), `driveOrder.txt` from the built listing and
`changes.md5` for the `._DFR` sources describes the built track 01
completely: applying the `._DFR`s, writing the `._NEW` files at their built
positions and copying the built root directory gives the built track.

## Controlled Change

`--add-new` in `tools/disc/make_ssp.py` (default behaviour unchanged):
`changed_and_new_files` (the built listing must contain every source entry
unchanged and may add root files only; a differing sector must be in a
changed or new file or the root directory), `._NEW` members in
`build_ssp(..., new=...)`, `read_new`, and `rebuild_check` in place of the
in-place apply check. `make_zips` gives an `.ssp` with added files its own
apply text (official patcher only, untested); `check_zips` refuses it
(`apply_ssp` cannot add files). Four new synthetic tests.

## Prediction

Two identical `.ssp` files; `rebuild_check` true; each `._DFR` applied by an
independent bspatch to the source file gives the built file; each `._NEW`
equals the built file; the xdelta zip unchanged (`b0188f0e…`).

## Procedure

```bash
D="English translation (all pilots, endings, UI; NAMES and SIGNS settings)"
./invenv.sh python -m tools.disc.make_ssp --built-dir build/regress/special018_saturn_only/image \
  --reference data/regression/special018_saturn_only.json --stem cyberbots_en \
  --out-dir build/release/patch --release-version 0.1.0 --description "$D" --add-new \
  --record release/cyberbots_en.ssp.json
# again with --out-dir build/release/patch-again and no --record; then cmp the two .ssp files
# independent check: unzip the .ssp; for each NAME._DFR,
#   bspatch local/extracted/saturn_jp/NAME out/NAME NAME._DFR (macOS /usr/bin/bspatch)
#   and cmp out/NAME with NAME extracted from the built track 01 (tools.disc.iso9660 --extract);
#   md5 of the source file against changes.md5; cmp each NAME._NEW with the built NAME
./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0 --patches build/release \
  --variant cyberbots_en patch "$D"   # and again into build/release/v0.1.0-again
```

2026-11-07, local.

## Actual Result

- **Patch:** `cyberbots_en.ssp`, 197,313 bytes, SHA-256
  `509accc5143bdf6d71767301a6da7dbaecb270d8b2f466cda8ad77f3047d3470`; both
  builds identical. 18 `._DFR` entries, 4 `._NEW` (stored whole: 8,640,
  38,700, 63,872, 63,872 bytes), `driveOrder.txt` with 268 lines (the four
  new files last, indexes 264-267), `changes.md5` for the 18 sources.
  `rebuild_check` true. Record `release/cyberbots_en.ssp.json`.
- **Independent check:** 18 of 18 `._DFR` applied by `/usr/bin/bspatch`
  give the built files; 18 of 18 source MD5s match `changes.md5`; 4 of 4
  `._NEW` byte-identical to the built files.
- **Zips:** `cyberbots_saturn_en_0.1.0_ssp.zip`, 196,460 bytes,
  `df1a7a8bed26af63978c93eb6160a2896bb76438aced9eeccddc25d1c0cf8b4d`, built
  twice identically; the xdelta zip is still `b0188f0e…`, and `check_zips
  --kinds xdelta --expect f6789cae…` passes.
- **Tests:** 273 pass.

## Conclusion

Prediction met for the patch's content. The user chose to attach the `.ssp`
zip to the v0.1.0 release beside the xdelta zip ("Add to v0.1.0
(Recommended)").

## Uncertainty and Alternatives

- **Not applied by any patcher.** The official patcher (Windows, closed
  source) was not run. Whether it reads `._NEW` as whole-file bytes, where it
  places the new files, and whether the rebuilt disc boots are UNKNOWN. Its
  rebuilt track will probably not hash `f6789cae…`, since it lays files out
  itself.
- `saturn-patcher-egui` ignores `._NEW` (its source); with it, the NAMES and
  SIGNS files would be missing and those settings would fail.
- The 61 directory entries that point at audio tracks are listed in
  `driveOrder.txt` like any other entry; how the official patcher treats
  them is UNKNOWN (as in `REL-001`).
