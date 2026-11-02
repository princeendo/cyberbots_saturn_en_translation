# EXP-0019: M2, the M1 Change From a Rebuilt Image

Task: DISC-002
Status: IN_PROGRESS (the user's cold-boot play check is pending)
Confidence: CONFIRMED by the agent runs; the play check closes the task

## Observation

The M1 box's text is loaded raw from `STG0AS.BIN` to `0x06060000` when the
first story stage starts, so Saturn line 4 is at file offset `0xF09C` (D-017).
Writing the M1 test string there in RAM changes the box (D-016).

## Hypothesis

An image built from the untouched source, with only those 26 bytes of
`STG0AS.BIN` changed (same size, in place, EDC/ECC regenerated), shows the M1
change with no RAM write.

## Controlled Change

One file, `STG0AS.BIN`, 26 bytes at file offset `0xF09C`:

- original `8e9f82cd83548343837b815b834f95ba82a98145814581458142`
  (Saturn line 4);
- new `82a082a282a482a682a882a982ab82ad82af82b182b382b582b7`
  (あいうえおかきくけこさしす, the M1 string).

The control is the same replay on the original image.

## Prediction

Only LSN 22,568 (file sector 30, bytes `0x09C`-`0x0B5`) changes, and it passes
EDC/ECC. From the pre-load state 4138 on the rebuilt image, the load copies
the test string, and the completed box hashes `1d501a` (EXP-0017's write run).
The original image gives `ead786`. A cold boot is unchanged.

## Inputs and Provenance

- `STG0AS.BIN` extracted from the untouched data track
  (`local/extracted/saturn_jp/`, SHA-256 `3fabb4db…ac45`, equal to
  `references/saturn_jp/iso_listing.json`). Edited file SHA-256
  `df84061e…f919`.
- Source image Redump 58190, the 63 components in `references/saturn_jp/README.md`; all
  still hash to those values after the work
  (`local/logs/disc002-source-after.json`).
- Session state `local/ref005/session/states/f00004138.mcs` (`3eb789da…a437`,
  EXP-0018). Patched binary `2fc3d547…eaaf` for the replays; stock Mednafen
  1.32.1 for the cold boot.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`build.py`](build.py) | Checks the extracted file and the original bytes, writes the edited file, calls `tools.disc.patch_image`. `--identity` writes the file unchanged |
| `tools/disc/patch_image.py` | Same-size in-place replacement, Mode 1 EDC/ECC regenerated (copied from XvSF `a1c82ba`) |
| `tools/disc/sector.py` | EDC/ECC check of every sector |
| `tools/mednafen/replay_state.py` | State replay on a chosen image, with a write-breakpoint log |
| `tools/mednafen/cold_boot.py` | Stock cold boot, one frame per second |

A dialogue-strip crop `352x72+0+168` is hashed as raw RGB:
`ffmpeg -i X.png -vf crop=352:72:0:168 -f rawvideo -pix_fmt rgb24 - | shasum -a 256`.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0019/build.py build/disc002/identity --identity
./invenv.sh python research/experiments/EXP-0019/build.py build/disc002/m2a
./invenv.sh python research/experiments/EXP-0019/build.py build/disc002/m2b
T="Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
./invenv.sh python -m tools.disc.sector "build/disc002/m2a/image/$T"
S=local/ref005/session/states/f00004138.mcs
BP=write:0606F09C-0606F0D3,2606F09C-2606F0D3
./invenv.sh python -m tools.mednafen.replay_state \
  "build/disc002/m2a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" $S \
  local/disc002/rebuilt --steps 36 --step-frames 50 --bp $BP --agent-dir local/disc002/agent-r
./invenv.sh python -m tools.mednafen.replay_state \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" $S \
  local/disc002/original --steps 36 --step-frames 50 --bp $BP --agent-dir local/disc002/agent-o
# a fresh home (config copied from local/mednafen_quiet, firmware linked), so
# backup RAM starts empty as in EXP-0001
./invenv.sh python -m tools.mednafen.cold_boot \
  "build/disc002/m2a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/disc002/boot1 --seconds 120 --home local/mednafen_disc002
```

17:20-17:25 local, 2026-11-02, the user present.

## Actual Result

- **Tool re-validation.** The identity build changes no sector, and all 63
  output components equal the source hashes.
- **Build.** The replacement is `STG0AS.BIN;1` at LSN 22,538, 320,724 bytes.
  Only LSN 22,568 changed (`013932ca…` → `6a91ccbc…`). A byte diff of the track
  finds 24 user-data bytes at sector offsets `0x9C`-`0xB5` (2 of the 26 bytes
  are equal in both strings) and 130 EDC/ECC bytes, all in that sector. All
  43,793 sectors pass EDC/ECC. Two builds are identical: Track 01 SHA-256
  `739a58e23b230372eedf3212039fa3ba8368f635d6a5a98abdb57adce0bf764a`; the
  other 62 components equal the source.
- **Replays from state 4138** (36 × 50 frames). Each run has 14 writes at
  `0x06041FB4`. On the rebuilt image they carry あいうえおかきくけこさしす
  (frame 331); on the original they carry Saturn line 4 (frame 330).
  Dialogue-strip hashes per step:

| Steps | Rebuilt | Original |
| --- | --- | --- |
| 1-25 | identical to the original | adc342 64a26d 3d8fbe… e7afda 3d8fbe 3d8fbe |
| 26-29 (box typing) | 7f1c3e 4dc9d3 a6a193 b481c7 | ccf645 6b08c9 788571 36dc78 |
| 30 (box complete) | **1d501a** | **ead786** |
| 31-36 | identical to the original | cfe69e 59926b 570885 51fc96 570885 187aa9 |

  Agent-reviewed screenshots of step 30: on the rebuilt image the box reads
  あいうえおかきくけこさしす on line 1 and Saturn line 5 unchanged on line 2;
  the original shows Saturn lines 4-5. The hashes equal EXP-0017's write run
  and control.
- **Cold boot** (stock, 120 s, empty backup RAM). `SGID: T-1217G`, 1 MiB
  cart. All 119 per-second frames are byte-identical to the original image's
  boot (`local/emu003/boot1`, EXP-0001).
- **Burnable copy** for the user's check: `build/disc/cyberbots_m2_disc002/`
  (ignored, a copy of `build/disc002/m2a/image/`).
- Source manifests are unchanged, and so are both home configs. A scratch home
  `local/mednafen_disc002` was added (ignored).

## Conclusion

**CONFIRMED (agent):** an image rebuilt from the untouched source, with 26
bytes of `STG0AS.BIN` changed in one sector, shows the M1 change in Jin's first
pre-fight box with no RAM write, and matches the original everywhere else that
was observed. The user's cold-boot play check is pending. M2 is recorded once
it passes.

## Uncertainty and Alternatives

- The replays start from a state saved on the original image. Every disc read
  after it comes from the rebuilt image, which the logged load confirms. The
  cold-boot route through story mode is the user's play check.
- Only one of the three byte-identical script copies is patched. The scenes
  that load `VICTORY.BIN` or `END.BIN` (not yet observed) would still show the
  original text.

## Reproduction

Run the procedure. Expect one changed sector (LSN 22,568), Track 01
`739a58e2…`, step 30 strip hashes `1d501a` (rebuilt) and `ead786` (original),
and a boot identical to EXP-0001's.
