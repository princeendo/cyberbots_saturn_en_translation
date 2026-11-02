# EXP-0001: Unattended Cold Boots of Cyberbots to the Title Screen

Task: EMU-003
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-002` pinned a project-local Mednafen home with the Japanese BIOS
(`sega_101.bin`, matching Mednafen 1.32.1's documented hash). The game had not
been run. Stock Mednafen has no scripted screenshot, and the agent interface
may not be used before `EMU-020`. XvSF's `EXP-0001` used the same method on
its game; that result is no evidence here.

## Hypothesis

Stock Mednafen 1.32.1, with the silent project home and no input, cold-boots
the untouched Cyberbots Saturn image to a stable title screen, and does so the
same way each time.

## Controlled Change

None to the game, BIOS, binary or configuration. Each run adds only the
command-line option `-qtrecord FILE` (not a saved setting; config hashes are
unchanged afterwards) so the agent can see the screen without sending input.
Before each run the silent home's `sav/` is emptied, so every boot starts with
no backup RAM. The user was present (standing rule "No cold boots without
me"; the user answered "Yes, boot it now", 2026-11-02).

## Prediction

Each of three boots logs `SGID: T-1217G`, shows the title screen within 120
seconds with no input, and leaves all 63 source components unchanged.

## Inputs and Provenance

- Source: `local/disc_images/cyberbots_saturn_jp_2m/` (63 components,
  `references/saturn_jp/README.md`), via
  `Cyberbots - Fullmetal Madness (Japan) (2M).cue`.
- BIOS: `local/mednafen/firmware/sega_101.bin`, SHA-256 `dcfef4b9…deac`
  (`docs/mednafen.md`).
- Emulator: `vendor/mednafen/build/src/mednafen`, stock 1.32.1, SHA-256
  `077ac658…669f`.
- Home: `local/mednafen_quiet/` (config SHA-256 `ef897288…5019`), firmware
  linked to `local/mednafen/firmware/`.

## Tools and Environment

- macOS 26.7.2, Darwin 25.6.0 arm64; ffmpeg 9.0.1 (Homebrew).
- `tools/mednafen/cold_boot.py` (copied from XvSF, `ENV-003`): runs Mednafen
  with `-qtrecord`, sends SIGTERM after `--seconds`, extracts one frame per
  second scaled to 352x240 (`scale=352:240:flags=area`), builds 5x5 contact
  sheets, writes `run.json` with log, video and frame hashes, then deletes the
  video. Frames are scaled from the recording canvas, so they are not native
  emulator screenshots. This run is the tool's re-validation on Cyberbots: the
  pilot and all three boots stopped cleanly and produced the expected files.

## Procedure

Pilot (20 s, `local/emu003/pilot/`): SIGTERM is caught ("Signal has been
caught and dealt with: SIGTERM"), the process exits 0, 19 frames are written.
The pilot showed only the BIOS animation, SEGA licence and Capcom logo by
second 19, so the runs use 120 s (XvSF's 90 s was not assumed to be enough).

```bash
D=local/disc_images/cyberbots_saturn_jp_2m
./invenv.sh python -m tools.disc.hash_source --json $D/* > local/emu003/source-before.json
for n in 1 2 3; do
  rm -f local/mednafen_quiet/sav/*
  ./invenv.sh python -m tools.mednafen.cold_boot \
    "$D/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
    local/emu003/boot$n --seconds 120
done
./invenv.sh python -m tools.disc.hash_source --json $D/* > local/emu003/source-after.json
cmp local/emu003/source-before.json local/emu003/source-after.json
```

Each boot took 2 min 15 s wall time, recording and frame extraction included.

## Actual Result

| Boot | Start (UTC) | Exit | Log SHA-256 | Video size / SHA-256 (deleted) |
| ---: | --- | ---: | --- | --- |
| 1 | 2026-11-02 19:54:33 | 0 | `b6b2754e…9206` | 1,264,850,510 / `ee3a399d…5845` |
| 2 | 2026-11-02 19:56:48 | 0 | `38bdc2e4…2b46` | 1,265,101,541 / `e573299f…6210` |
| 3 | 2026-11-02 19:59:03 | 0 | `f931bde3…e55b` | 1,264,347,696 / `ae1768fc…0d0b` |

- Every log (6,911 bytes) shows `SGID: T-1217G`, `SGNAME: CYBER BOTS`,
  `SGAREA: J`, `Region: 0x1`, `Cart: 1MiB Extended RAM`. The logs differ only
  in the line naming the output file. Other "Error"/"Failed" lines are absent
  optional files: the `.sbi`, `ss.cfg`, the per-game `pgconfig` file, and
  `cheats/ss.cht`.
- All 119 per-second frames are byte-identical across the three boots. The
  video container hashes differ; the frames do not.
- Sequence (agent-reviewed, frame N ≈ second N-1):
  - 001-019: BIOS 1.01 animation and logo, SEGA licence, Capcom logo.
  - 026-027: `NOW LOADING`.
  - 029-050: intro: Capcom logo, pilot portraits, a red VA in 3D, then VA
    schematic screens with English part labels (`BIT`, `POWER KNUCKLE`,
    `COMMAND WALKER`, `LASER CANNON`, `HOMING MISSILE`, ...).
  - **058-060: the title logo `CYBERBOTS FULLMETAL MADNESS` with
    `©CAPCOM CO., LTD. 1994,1995,1997 ALL RIGHTS RESERVED.`**;
    **062-067: the same with `PRESS START BUTTON`**.
  - 068-075: black, then the VA schematics again with `PRESS START BUTTON`.
  - 076-088 and 107-116: `NOW LOADING`.
  - 090-106: an attract fight, `BLODIA` vs `REPTOS`, `PHASE 1`, `PROCEED`,
    `4 HIT COMBO!`, English HUD (`BOOST`, `POWER`).
  - 117-119: `RANKING` (English).
- Title frames (352x240), equal in all three boots: `frames/058.png` SHA-256
  `180aa26a30400ad6b75d124324b2da9d6d35758bd378789c9bbcfe69b55bf998`;
  `frames/064.png` (with `PRESS START BUTTON`, equal to 062)
  `e9f124745843f7a93dafd6308a0d4dc3e875f393120d2a67dcdae51f6bcaee24`.
- The 63 source components are identical before and after (`cmp` of the two
  manifests); the binary and both config files hash as before.
- Backup RAM: each boot wrote
  `Cyberbots - Fullmetal Madness (Japan) (2M).ee043c21f235a796453c19a841e691e2.bkr`
  and `.smpc` to the quiet home's `sav/` (emptied before each boot).

Side observations (recorded for `REF-005` and `END-001`, not part of the
hypothesis):

- In 119 s of boot and attract, no Japanese text appears apart from signage
  painted into the attract stage's background. Every other label shown is
  English.
- Mednafen's table of contents (log lines 22-84) lists 61 audio tracks. Each
  track's start LBA equals the LSN of exactly one ISO 9660 entry beyond
  track 01: `01`-`32` are tracks 2-33, `45`-`52` tracks 34-41, and the 21
  per-pilot entries are tracks 42-62 (`JIN_END1`-`3` 42-44, `SAN_END1`-`3`
  45-47, `MA_END1`-`2` 48-49, `ARI_END1`-`2` 50-51, `GA_END1`-`3` 52-54,
  `BAO_END` 55, `DE_END1`-`2` 56-57, `TI_END1`-`3` 58-60, `SYE_END1`-`2`
  61-62).

## Conclusion

**CONFIRMED.** Stock Mednafen 1.32.1 with the project's silent home and the
Japanese BIOS cold-boots the untouched image to a stable title screen with no
input, about 57 s after launch, identically in three runs at one-second
sampling. `ss.cart auto` gives the game the 1 MiB extended-RAM cart.

## Uncertainty and Alternatives

- Identical per-second frames do not prove frame-exact determinism between
  samples, or with input. The three boots ran within 7 minutes of each other;
  XvSF found that frames late in a boot can depend on when the boot runs (its
  `EXP-0018`), so these hashes may reproduce only for boots close in time.
- `Cart: 1MiB Extended RAM` comes from `ss.cart auto` (Mednafen's database).
  Whether the game needs a cart, or uses a 4 MiB one, is `EMU-004`.
- Whether emulation stalls when the display sleeps was not tested.
- A Mednafen window opens during each run; the runs are silent, not hidden.
- What tracks 42-62 hold (ending music, or voiced narration) is not known.

## Reproduction

Run the procedure above from the repository root, with the user present.
Evidence stays in the ignored `local/emu003/` (`pilot/`, `boot*/run.json`,
`mednafen.log`, `frames/`, `sheet-*.png`; source manifests). Expect frame 064
to hash `e9f12474…ee24`.
