# EXP-0087: Official Sega Saturn Patcher Applies `._NEW` Files

Task: REL-004 follow-up
Status: DONE
Confidence: SUPPORTED that Sega Saturn Patcher 1.91 reads the `._NEW`
entries and places all four added files in its rebuilt image. DISPROVEN as a
usable full-disc patch for this multi-file-audio BIN/CUE set: its rebuilt BIN
is too large for a normal CD.

## Observation

The release SSP contains 18 `._DFR` entries and four `._NEW` entries for the
NAMES and SIGNS files. The official Windows patcher was previously untested.
The untouched user-supplied source set is:

`C:\Users\white\Downloads\Cyberbots - Fullmetal Madness (Japan) (2M)`

Its Track 01 SHA-256 is
`758fa7956aa6139460c391ec5225e69cc9cde13dfe2281e8c544e594d201dbd1`.

## Hypothesis

Sega Saturn Patcher 1.91 can apply `cyberbots_en.ssp` to this multi-track
BIN/CUE set and include all four `._NEW` files in the rebuilt image.

## Controlled Change

Install the official Sega Saturn Patcher 1.91 and .NET 5 Windows Desktop
Runtime. Apply the published SSP to a copy of the source set only. The source
image is not modified.

## Procedure

1. Installer archive: SegaXtreme resource
   `https://segaxtreme.net/resources/sega-saturn-patcher.73/`, downloaded
   through its `/download` endpoint. Archive SHA-256:
   `23dd668fa2a06761f421b8e2a7eb108a4320a1b04a6fad9f789ade351c89fa50`.
2. Installed to `C:\Users\white\Tools\Sega Saturn Patcher 1.91`.
3. Installed `Microsoft.DotNet.DesktopRuntime.5` version `5.0.17` with
   `winget`.
4. Downloaded `cyberbots_saturn_en_0.1.0_ssp.zip` from the v0.1.0 release;
   extracted it under `build/official_ssp/`.
5. Copied the source set to `build/official_ssp/source/` and ran:

```powershell
& "C:\Users\white\Tools\Sega Saturn Patcher 1.91\CLR\CLR.exe" `
  -image "build\official_ssp\source\Cyberbots - Fullmetal Madness (Japan) (2M).cue" `
  -patch "build\official_ssp\patch\cyberbots_en.ssp" `
  -o "build\official_ssp\patched\Cyberbots - Fullmetal Madness (Japan) (2M)"
```

6. Checked the rebuilt BIN with `tools.disc.iso9660` and extracted its ISO
   entries under `build/official_ssp/patched_extract/`.

## Prediction

The patcher completes, and the four new root files appear in the rebuilt ISO
with the recorded target hashes.

## Actual Result

The CLI reported `Finished.` and created a single-BIN/CUE rebuilt image. The
ISO check succeeded. All 22 changed or new files matched their recorded target
SHA-256 values, including:

- `ZNAMES1.BIN` (8,640 bytes)
- `ZNAMES2.BIN` (38,700 bytes)
- `ZSIGNS1.BIN` (63,872 bytes)
- `ZSIGNS2.BIN` (63,872 bytes)

The source Track 01 still hashes to
`758fa7956aa6139460c391ec5225e69cc9cde13dfe2281e8c544e594d201dbd1`.
The patcher's rebuilt BIN hash is
`1037d5c934a7f5c123a6993248ed664185ffcfa40274f63e84c0d67adfd9c905` and is
not expected to equal the sector-preserving build hash because the official
patcher lays out a new single-BIN image.

The original 63-file set totals 591,012,003 bytes (about 55:50), while the
rebuilt BIN is 1,050,753,648 bytes (446,749 sectors, about 99:17). The
generated CUE places the short source audio tracks at minute-scale offsets, so
this output does not fit on a normal 80-minute CD.

## Conclusion

The hypothesis is only partially supported. The official patcher accepts this
SSP and carries the four `._NEW` files into its rebuilt image, but its output
does not preserve this disc's usable size/layout. The SSP is therefore not a
validated full-disc distribution for this input and patcher combination.
The root cause remains UNKNOWN: source-layout handling, SSP metadata, or
their interaction. Next: rebuild the same original image without `-patch`.
If that also expands, test a byte-verified merged input; otherwise inspect
the SSP's `driveOrder.txt`, particularly its audio-referencing ISO entries.
These follow-up experiments have not been run.
