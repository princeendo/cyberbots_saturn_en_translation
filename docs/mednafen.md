# Mednafen

Stock Mednafen first (`AGENTS.md` rule 16). The sibling projects'
agent-interface patch is built only after `EMU-003` and `EMU-020`
(user decision 2026-11-02, `DOC-002`: "Yes, reuse it (Recommended)").

## Selected Stock Release (`EMU-001`, 2026-11-02)

Mednafen `1.32.1`, the release both MSHvSF and XvSF used, so the
agent-interface patch (`vendor/mednafen/patches/0001-agent-interface.patch`)
can apply unchanged.

- Upstream project: <https://mednafen.github.io/>; releases:
  <https://mednafen.github.io/releases/>.
- Source archive URL:
  <https://mednafen.github.io/releases/files/mednafen-1.32.1.tar.xz>.
- Not downloaded again. The archive XvSF downloaded on 2026-10-28 (its
  `EMU-001`) was copied (`cp -c`) from that repository's ignored
  `local/downloads/mednafen-1.32.1/` into this repository's ignored
  `local/downloads/mednafen-1.32.1/`.
- Archive: `mednafen-1.32.1.tar.xz`, 3,571,236 bytes, SHA-256
  `de7eb94ab66212ae7758376524368a8ab208234b33796625ca630547dbc83832`, equal to
  the size and hash both siblings recorded.
- License: GNU GPL version 2 (`COPYING` in the archive).

`bsdtar -tf` lists one top-level folder, `mednafen/`. It was extracted with
`bsdtar -xf` into an empty scratch folder under `local/`, then moved to the
ignored `vendor/mednafen/src/`. It is not modified.

## Exact Stock Build

Host: macOS 26.7.2 (25G332), Darwin 25.6.0 arm64 (12 CPUs), Apple clang
21.0.0 (clang-2100.3.34.2), GNU Make 3.81, `pkg-config` 3.0.10, Homebrew
7.0.11, SDL2 2.32.74, libFLAC 1.5.0, zlib 1.2.12. These build dependencies were
already installed; nothing was installed for this task. This is XvSF's
toolchain, on a newer macOS point release (XvSF: 26.7.1, 25G241).

From the ignored `vendor/mednafen/build/`:

```bash
PKG_CONFIG=/opt/homebrew/bin/pkg-config \
CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

Both exited 0. `configure` took 30 s and `make -j12` 2 min 46 s
(13:37:37-13:40:23 local time). Logs: ignored
`local/logs/emu001-configure.log` and `local/logs/emu001-make.log`. The make
log's only warnings at the end are the linker's `-no_pie ignored for arm64`
and `ignoring duplicate libraries: '-liconv'`.

Binary: `vendor/mednafen/build/src/mednafen`, Mach-O 64-bit arm64, 21,327,272
bytes, SHA-256
`077ac658c8e773bca58508cf7bacc4f180a6bf492419bfe0b8ddf3e7415d669f`. It differs
from the XvSF stock binary (`892bb60a…29dd`, 21,328,328 bytes) built from the
same archive with the same flags on macOS 26.7.1; a byte-identical binary is
not expected across host builds.

## `-help` Banner

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" vendor/mednafen/build/src/mednafen -help
```

Output (ignored `local/logs/emu001-help.log`) begins:

```text
Starting Mednafen 1.32.1
 Build information:
   Compiled with gcc Apple LLVM 21.0.0 (clang-2100.3.34.2)
   Compiled against zlib 1.2.12, running with zlib 1.2.12(flags=0x000002a9)
   Compiled against libiconv 11.1, running with libiconv 11.1
   Compiled against SDL 2.32.74(SDL-release-2.32.74-0-ge4df8a5), running with SDL 2.32.74(SDL-2.32.74-no-vcs)
   Running with libFLAC 1.5.0
 Base directory: <checkout>/local/mednafen
 Emulation modules: apple2 nes snes gb gba pce lynx md pcfx ngp psx ss ssfplay vb wswan sms gg sasplay snes_faust pce_fast demo cdplay
```

The Saturn module `ss` is present. The process prints the usage text and exits
with status 255, as both siblings' 1.32.1 builds do for `-help` with a fresh
`MEDNAFEN_HOME`; this is not a build fault. The run created a default
`local/mednafen/mednafen.cfg` and its folders; project settings are
`EMU-002`'s work. No disc image was loaded.

## Cartridge Database Entry (static, for `EMU-004`)

Mednafen 1.32.1's `src/ss/db.cpp`, line 102:

```text
{ "T-1217G", NULL, CART_EXTRAM_1M, "Cyberbots (Japan)" },
```

So with `ss.cart auto`, Mednafen should give this disc the **1 MiB**
extended-RAM cart. Unlike XvSF's entry (`CART_EXTRAM_4M`, "Game
requirement."), the line carries no requirement note. This is the emulator
authors' database, not a test: which cart the game needs, and what it does
without one, is `EMU-004`'s experiment.

## Project-Local Configuration (`EMU-002`, 2026-11-02)

Mednafen never reads the user's global configuration here: every run sets
`MEDNAFEN_HOME` to an ignored folder in this checkout.

| Home | Use |
| --- | --- |
| `local/mednafen/` | Interactive runs (the user plays, hears the game). |
| `local/mednafen_quiet/` | Unattended runs: `sound.volume 0`, `video.glvsync 0`, `video.blit_timesync 0`; `firmware/` is a symlink to `../mednafen/firmware`; own `sav/` and `mcs/`. |

The silent home follows the user's `DOC-002` answer "Silent unattended runs".
Sound stays enabled at volume 0, so emulation timing is unchanged. Both
siblings found that, with vsync on, emulation stalls while the display
sleeps; that is a **HYPOTHESIS** here until an unattended Cyberbots run shows
it.

The interactive configuration is the file Mednafen 1.32.1 generated on its
first run (`EMU-001`'s `-help`). Both homes are pinned by
`tools/mednafen/home.py` (copied from XvSF, `ENV-003`), which creates the
quiet home from the interactive one if it is missing:

```bash
./invenv.sh python -m tools.mednafen.home
```

The tool rewrites only existing `key value` lines and fails on a key with no
line. Mednafen saves command-line settings into the configuration on exit, so
rerun it after any run that passed settings on the command line. Its first run
reported `local/mednafen: no change` and `local/mednafen_quiet: sound.volume,
video.blit_timesync, video.glvsync`; a second run reported `no change` for
both.

Pinned settings (both homes), all equal to the 1.32.1 defaults; pinning guards
against settings saved from a command-line run:

| Setting | Value | Purpose |
| --- | --- | --- |
| `filesys.path_firmware` | `firmware` | BIOS files below the home. |
| `filesys.path_sav` | `sav` | Saturn backup RAM. |
| `filesys.path_savbackup` | `b` | Backup-RAM backups. |
| `filesys.path_state` | `mcs` | Save states. |
| `filesys.path_snap` | `snaps` | Screenshots. |
| `filesys.path_movie` | `mcm` | Movies. |
| `filesys.path_pgconfig` | `pgconfig` | Per-game overrides. |
| `filesys.path_cheat` | `cheats` | Cheats. |
| `filesys.fname_state` | `%f.%M%X` | Stable state filenames. |
| `filesys.fname_snap` | `%f-%p.%x` | Stable screenshot filenames. |
| `autosave` | `0` | No implicit state at load or exit. |
| `debugger.autostepmode` | `0` | No debugger step mode at launch. |
| `ss.bios_jp` | `sega_101.bin` | Japanese BIOS. |
| `ss.bios_na_eu` | `mpr-17933.bin` | North American/European BIOS. |
| `ss.bios_sanity` | `1` | BIOS sanity checks on. |
| `ss.cart` | `auto` | Cart chosen by Mednafen's database: `CART_EXTRAM_1M` for `T-1217G` (above). Whether that is what the game needs is `EMU-004`'s test. |
| `ss.region_autodetect` | `1` | Region taken from the disc. |

Result: with each home, `-help` reports `Base directory:` that home and
`Loaded 7904 valid settings and 0 unknown settings` (ignored
`local/logs/emu002-help-mednafen.log`, `emu002-help-mednafen_quiet.log`), and
both files' SHA-256 are unchanged afterwards:

| File | Size | SHA-256 |
| --- | ---: | --- |
| `local/mednafen/mednafen.cfg` | 652,752 | `48a7cf6b03224ab6fc485965ec13a0a9d657f678b3f187d3791469686ab228fc` |
| `local/mednafen_quiet/mednafen.cfg` | 652,750 | `ef89728844860b8334411d3bbd6195b84828956c5e446744efdc9e59ea305019` |

`diff` between the two shows only the three quiet settings. Both hashes equal
XvSF's pinned files (its `docs/mednafen.md`, `EMU-002`): Mednafen's generated
default holds no host- or game-specific content. Pad bindings are not set yet
(`EMU-005`).

### Saturn BIOS

Copied unchanged (`cp -p`, `cmp` clean) from the XvSF ignored
`local/mednafen/firmware/` (itself a copy of MSHvSF's) into
`local/mednafen/firmware/`. Each matches the SHA-256 that Mednafen 1.32.1's
own `Documentation/ss.html` (from the verified archive) gives for its default
filename:

| File | Size | SHA-256 | Mednafen use |
| --- | ---: | --- | --- |
| `sega_101.bin` | 524,288 | `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac` | `ss.bios_jp`, "Required for Japan-region games" |
| `mpr-17933.bin` | 524,288 | `96e106f740ab448cf89f0dd49dfbac7fe5391cb6bd6e14ad5e3061c13330266f` | `ss.bios_na_eu` |

MSHvSF records `sega_101.bin` as a copy of the user-supplied
`Bios Saturn 1.01 (J) [!].bin`. Whether the BIOS boots Cyberbots is
`EMU-003`'s test.

### Launch Commands

Interactive, from the repository root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen" \
  vendor/mednafen/build/src/mednafen \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
```

Unattended: the same with `MEDNAFEN_HOME="$PWD/local/mednafen_quiet"`, with
stdout and stderr redirected to a file under the ignored `local/logs/`. Stock
Mednafen has no log-directory setting. No disc has been loaded yet; the first
boot is `EMU-003`, run with the user present.

## Pad Mapping (`EMU-005`, 2026-11-02)

The user's instruction (2026-11-02): "You should be able to use the same
configuration for the pad you had in MSHvSF and XvSF." The 13 port 1 gamepad
bindings are identical in both siblings' interactive configurations, so they
were copied from XvSF's (the more recent, modified 2026-11-01; SHA-256
`cb1c2d3b…a1e9`) into both homes:

```bash
./invenv.sh python -m tools.mednafen.home --bindings-from \
  ../xmen_vs_sf_saturn_en_translation/local/mednafen/mednafen.cfg
```

The first run changed the 13 binding lines in each home; a second reported
`no change`. Both homes then loaded `7904 valid settings and 0 unknown
settings`.

| Saturn control | Binding (joystick `0xecccd365fc40db2f0006000c00010000`) |
| --- | --- |
| Up / Down | `abs_1-` / `abs_1+` |
| Left / Right | `abs_0-` / `abs_0+` |
| A / B / C | `button_0` / `button_1` / `button_10` |
| X / Y / Z | `button_2` / `button_3` / `button_9` |
| L / R | keyboard `0x0 19` (Mednafen's default) |
| Start | `button_6` |

The configurations are now byte-identical to XvSF's current ones, so the
hashes recorded under `EMU-002` above are superseded:

| File | Size | SHA-256 |
| --- | ---: | --- |
| `local/mednafen/mednafen.cfg` | 653,154 | `cb1c2d3b8bf5bde19613fdd19d917350838114d9ce390df5db7e87872019a1e9` |
| `local/mednafen_quiet/mednafen.cfg` | 653,152 | `aad9a7ef68d31d249fcb12383bf6e3323d04b0d3986d355ed8cf9faa303c57cf` |

After any run that passes settings on the command line, rerun
`./invenv.sh python -m tools.mednafen.home`; the quiet config should return
to `aad9a7ef…57cf`.

Which game action each Saturn button performs in Cyberbots (the arcade uses
two weapon buttons, boost and jump) has not been observed yet; it is noted at
the first play session (`REF-005`).

## Hotkeys: Screenshots and States (`EMU-006`, `EXP-0003`)

`tools/mednafen/hotkeys.py` launches stock Mednafen and presses its hotkeys
at fixed times through macOS System Events (Accessibility permission, already
granted for the sibling projects). Use `--keep-focus`:

```bash
./invenv.sh python -m tools.mednafen.hotkeys \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/RUN/run.log --keep-focus --at 62:F9 --at 64:F5
```

| Key | Effect (1.32.1 default) | Output |
| --- | --- | --- |
| F9 | Screenshot | `snaps/<image>-NNNN.png`, numbered by `snaps/<image>-counter.txt` across runs |
| F5 | Save state, slot 0 | `mcs/<image>.ee043c21f235a796453c19a841e691e2.mc0` (about 1.1 MB) |
| F7 | Load state, slot 0 | — |
| F12 | Exit (sent by the tool after the last step) | — |

Without `--keep-focus` the tool hands focus back after each key, and one F9
was lost that way (`EXP-0003`, run 1). Check the snapshot counter after each
run. Key times slip about 1-1.9 s behind the schedule while the window is
brought forward.

## Runbook: Show Any Story Scene From a Checkpoint (`RE-002`, `EXP-0022`)

A debug harness only; it never ships.
- A story scene starts when the stage code posts its number. The scene task
  then reads the pilot from the byte at task + `0x1F` and the scene from the
  byte at task + `0x23`.
- From REF-005 state 5208 (Jin's opening narration), the next scene task is
  at `0x06008268`, so its scene byte is `0x0600828B`.
- A log-mode write breakpoint on that byte, plus a one-shot `onhit` write of
  the wanted scene, replaces the game's value just after it is written.

```bash
./invenv.sh python research/experiments/EXP-0022/force_scene.py local/re002/force-N N
./invenv.sh python research/experiments/EXP-0022/check_cells.py local/re002/force-N N
```

- `check_cells.py` predicts the first box's cells from
  `data/text/jin_boxes.json` and the font, and reports the best match per
  step.
- Check that the run's `result.json` has the breakpoint events. From another
  state the task may be elsewhere; trace it first (EXP-0022, "Uncertainty").

