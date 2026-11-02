# EXP-0006: Agent Interface Built and Validated on Cyberbots (V1-V4)

Task: EMU-021
Status: DONE
Confidence: CONFIRMED

## Observation

`EMU-020` (`docs/mednafen_agent_interface.md`) found stock Mednafen
insufficient for agent-driven work: three silent key-driven failures in
`EXP-0003` to `EXP-0005`, and registers read by eye. The sibling projects'
frontend-only patch was validated on MSHvSF and XvSF, which is no evidence
for Cyberbots.

## Hypothesis

The patch applies unchanged to stock 1.32.1 and builds; the patched binary
behaves like stock without `MEDNAFEN_AGENT_DIR` (V1), and with it, `read`
equals validated extraction of a same-poll state (V2), `write` round-trips
under halt control (V3), and write breakpoints log without stopping and halt
on request (V4).

## Controlled Change

A separate patched build (`vendor/mednafen/build-agent/`); the stock tree and
binary are unchanged. Each validation varies only what it tests. The user was
present ("Yes, build it", 2026-11-02).

## Prediction

- V1: with the agent directory unset, 119 of 119 cold-boot frames equal
  D-001; with it set, `status`, `spaces` and `regs` answer.
- V2: `read` of `workraml`, `workramh`, `vdp1vram`, `vdp2vram` equals
  `mcs_extract` (validated, D-006) of the state saved in the same poll.
- V3: the 16-byte write reads back, the restore reads back the original;
  `pause`, `step`, `run` and `frames N` behave as named.
- V4: log mode on game-variable ranges records hits while frames advance;
  halt mode on all of WRAM-H stops the CPU with registers as text.

## Inputs and Provenance

- Patch `vendor/mednafen/patches/0001-agent-interface.patch`, SHA-256
  `c30146ef…5244` (MSHvSF `b9a6593`, unchanged in XvSF).
- Stock source `vendor/mednafen/src/` from the verified archive
  (`de7eb94a…3832`, `EMU-001`).
- Image, BIOS and silent home as `EXP-0001` (home config `aad9a7ef…57cf`).
- V4 ranges: WRAM-H bytes outside the stack that differ between the title
  freezes `EXP-0004` A2 (`fc70d589…8b10`) and `EXP-0005` H (`7ebf334e…5b63`):
  `060CFED0-060CFEFF`, `060D3150-060D3153`, `060DF7E0-060DF7EB`, and their
  `2…` cache-through mirrors.

## Tools and Environment

Build host as `EMU-001` (macOS 26.7.2, Apple clang 21.0.0).
`tools/mednafen/agent.py` and `tools/mednafen/cold_boot.py` (copied from
XvSF); [`validate.py`](validate.py), copied from XvSF's `EXP-0006` with the
image, title frame, V4 ranges and V4 report changed (provenance in its
docstring).

## Procedure

```bash
cp -R vendor/mednafen/src vendor/mednafen/src-agent
patch -d vendor/mednafen/src-agent -p1 < vendor/mednafen/patches/0001-agent-interface.patch
mkdir -p vendor/mednafen/build-agent && cd vendor/mednafen/build-agent
PKG_CONFIG=/opt/homebrew/bin/pkg-config CC=/usr/bin/clang CXX=/usr/bin/clang++ \
  ../src-agent/configure --prefix="$PWD/install" --enable-debugger --enable-ss
make -j12
cd ../../..
env -u MEDNAFEN_AGENT_DIR ./invenv.sh python -m tools.mednafen.cold_boot \
  "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" \
  local/emu021/v1-stock-equiv --seconds 120 --mednafen vendor/mednafen/build-agent/src/mednafen
./invenv.sh python research/experiments/EXP-0006/validate.py local/emu021/run1
./invenv.sh python -m tools.memory.mcs_extract local/emu021/run1/v2.mc0 \
  --region wram_l --region wram_h --region vdp1_vram --region vdp2_vram \
  --out-dir research/memory_dumps/emu021/run1-v2
cmp local/emu021/run1/wram_l.bin research/memory_dumps/emu021/run1-v2/wram_l.bin  # and the others
```

`validate.py` runs to frame 3700 (`frames`), resumes, and sends one command
file with four `read`s, `savestate`, `screenshot` and `status` (V2); pauses
and writes `EMU-021 WRITE OK` at WRAM-H `0xF0000`, reads back, restores,
steps, runs, and runs `frames 30` (V3); sets `bpmode log` with the six
ranges for 1,800 frames (V4); then halt mode on all of WRAM-H (V4b).

## Actual Result

**Build.** `patch` applied all four files with no fuzz or offsets
(`local/logs/emu021-patch.log`). Configure 30 s, `make -j12` 2 min 40 s
(14:54:46-14:57:56 local), both exit 0. Binary
`vendor/mednafen/build-agent/src/mednafen`, Mach-O arm64, 21,378,040 bytes,
SHA-256 `2fc3d547354b4506c59da282d0aeedda63ac02b515d9c5150648ed738b0aeaaf`.
The stock binary still hashes `077ac658…669f`.

- **V1 equivalence.** Without the agent directory, 119 of 119 per-second
  frames equal `EXP-0001` boot 1; log `SGID: T-1217G`, `Cart: 1MiB Extended
  RAM`.
- **V1 smoke.** `status` answered at frame 4; `spaces` listed 13 spaces
  (`physical`, `workraml`, `workramh`, `scspram`, `scspmprog`, `scsptemp`,
  `scspmems`, `dspprog`, `backup`, `vdp1vram`, `vdp1fb0`, `vdp1fb1`,
  `vdp2vram`); `regs` returned 50 SH-2 and on-chip registers.
- **V2.** Halted at frame 3701, then in one poll: `read` of the four spaces,
  `savestate`, `screenshot`. Each read is byte-identical to `mcs_extract` of
  that state (`0d9dda2c…3620`, 1,098,460 bytes): WRAM-L `bb0628a5…`,
  WRAM-H `f3eb1224…`, VDP1 VRAM `be799aa7…`, VDP2 VRAM `c16d7b70…`. The
  screenshot (352x240) shows the title.
- **V3.** Round trip exact (before `00000000B2BB9A00…`, written = pattern,
  restored = before). `pause` halted at frame 3706, PC `06000944`; `step`
  moved PC to `06000946`; `run` resumed; `frames 30` from 3708 halted at
  3739; `savestate` while halted was refused ("not allowed while halted").
- **V4.** Log mode, frames 3739-5539: 10,822 hits, frames kept advancing,
  48 distinct PCs. Examples: PC `0603E100` with R2 `060DF7E0`, PC `060609DC`
  with R2 `060CFEDC`, PC `0603DA1A` with R2 `060DF7E0`.
- **V4b.** Halt mode on all of WRAM-H halted at frame 5540, PC `060008F0`,
  R15 `06008000`, with `regs` as text. This is the store that `EXP-0004`
  run F halted on, and its by-eye reading (PC `060008F0`, R15 about
  `06008000`) is now confirmed.
- Source manifests identical before and after; validate exited 0; quiet
  config unchanged.

## Conclusion

**CONFIRMED.** The sibling agent-interface patch applies unchanged and builds
for Cyberbots; without `MEDNAFEN_AGENT_DIR` the patched binary is
frame-identical to stock, and with it reads, writes, halt control, log-mode
and halt-mode write breakpoints work, with machine-readable registers. Agent
output may be used as evidence (D-007).

## Uncertainty and Alternatives

- V4 ranges were chosen because their bytes changed between two title
  freezes; the hits show which code writes them, not what they mean.
- `status` reports `pc=00000000` while halted at a frame boundary (frame 4
  and 3701); `regs` gives the real PC. The stock CPU view in `EXP-0005` run G
  also showed PC `00000000`, plausibly the same boundary state (HYPOTHESIS).
- Agent writes do not reach cart RAM (sibling finding; not re-tested).

## Reproduction

Run the procedure from the repository root, with the user present. Evidence
stays in the ignored `local/emu021/` and `research/memory_dumps/emu021/`.
Expect V1 frame equality, four identical V2 reads, an exact V3 round trip,
V4 hits with advancing frames, and a V4b halt with registers.
