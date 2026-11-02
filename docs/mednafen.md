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
