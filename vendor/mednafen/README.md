# Mednafen Vendor Area

The stock Mednafen 1.32.1 source and build stay unmodified in the ignored
`vendor/mednafen/src/` and `vendor/mednafen/build/` (`EMU-001`,
`docs/mednafen.md`). Do not commit source archives, binaries, runtime state,
BIOS files, or game data.

## Agent-Interface Patch (`EMU-021`)

- `patches/0001-agent-interface.patch`, SHA-256
  `c30146efab0cb60bfb7a4465bc95d9935c63c0d7bf172b02f886b4ae2cff5244`, 592
  lines, against 1.32.1. Copied unchanged from the MSHvSF repository
  (`vendor/mednafen/patches/0001-agent-interface.patch`, added in MSHvSF
  commit `b9a6593`; unchanged at `69c666c`). GPL-2.0, like Mednafen.
- Frontend only: adds `src/drivers/agent.inc` and hooks in
  `src/drivers/debugger.cpp`, `debugger.h`, and `main.cpp`. The Saturn core is
  unchanged. Active only when `MEDNAFEN_AGENT_DIR` is set.
- Copied into this repository from the XvSF repository (same path, commit
  `a1c82ba`; identical bytes to MSHvSF's). Reuse here follows `AGENTS.md`
  rule 16: build it only after stock Mednafen boots Cyberbots (`EMU-003`),
  then re-run validations V1-V4 on Cyberbots (`EMU-021`).

Build, from the repository root, with the stock source already extracted:

```bash
cp -R vendor/mednafen/src vendor/mednafen/src-agent
patch -d vendor/mednafen/src-agent -p1 < vendor/mednafen/patches/0001-agent-interface.patch
mkdir -p vendor/mednafen/build-agent && cd vendor/mednafen/build-agent
PKG_CONFIG=/opt/homebrew/bin/pkg-config CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src-agent/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
```

Run, from the repository root:

```bash
MEDNAFEN_HOME="$PWD/local/mednafen_quiet" MEDNAFEN_AGENT_DIR="$PWD/local/RUN/agent" \
  vendor/mednafen/build-agent/src/mednafen \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
```

The client is `tools/mednafen/agent.py`. Validation on Cyberbots: not yet run (`EMU-021`). For the method, see the
XvSF record `research/experiments/EXP-0006/README.md` in that repository.
