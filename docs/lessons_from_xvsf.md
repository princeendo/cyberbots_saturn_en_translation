# Lessons From XvSF (the second game)

XvSF (X-Men vs. Street Fighter, Saturn JP T-1226G) was the second project to use
the MSHvSF method. It never wrote a cross-game playbook of its own, so this
digest fills that gap for Cyberbots. It was compiled on 2026-11-02 (`DOC-001`)
from the XvSF repository at commit `a1c82ba`: its `TASKS.md`,
`research_log.md`, `docs/discoveries.md`, `docs/known_unknowns.md`,
`docs/text_surfaces.md`, `docs/localization_policy.md`, and `tools/`.

**Every game fact here is an XvSF or MSHvSF fact and, for Cyberbots, at most a
HYPOTHESIS** (`AGENTS.md` rule 13). XvSF IDs (`EXP-`, `D-`) refer to that
repository.

## Scale

| | MSHvSF | XvSF |
| --- | --- | --- |
| Active days | about 14 | about 6 (2026-10-27 to 11-02) |
| Experiments | about 105 | 74 |
| Commits | 214 | 120 |
| Tests | about 55 files | 272 tests |

XvSF's speed-up came from three things: the copied method, the copied Mednafen
agent patch, and one lucky game fact (a leftover arcade English mode in the
Saturn renderer). Do not plan on the third.

## The Rule That Held: Methods Transfer, Formats Do Not

Generic search methods worked on both games:

- **Equality-pattern search** (`tools/text/pattern_search.py`) finds a text
  record in RAM by which cells share a glyph, whatever the encoding. XvSF found
  its quote table in one hit.
- **Write breakpoint on the RAM text**, from a checkpoint taken before it
  loads, halts inside the loader or decompressor and names the disc file,
  whatever the compression.
- **Write breakpoint on a glyph cell** finds the font routine and base. Prove a
  font format with a byte-identical repack before changing it.
- **Same-size in-place file replacement** with regenerated EDC/ECC
  (`tools/disc/patch_image.py`). Neither game checksummed its files.
- **MAME forcing** (vitality to 0, forced indexes, `logreads` read taps via
  `tools/reference/mame_timeline.lua`) reaches any arcade text with no play.
- **Trace the arcade's readers** to find official English. "No English exists"
  from a data search was wrong in both games.

Formats differed every time:

| MSHvSF | XvSF reality |
| --- | --- |
| LZSS `.PAC`, MSB-first flags | 4-byte count + LZ77, LSB-first control bits, two copy forms (`.SHP`, `.PRS`) |
| Font in cart RAM (`MEMFIX.PAC` entry 4) | `FIX.PRS`, raw, loaded to WRAM-L |
| Arcade English as 16-bit codes in `mvs.07b` | ASCII tile-sheet layout with pointer tables in `xvs.06a` (found by an offset histogram of common words) |
| Leftover arcade language word crashes to BIOS | The renderer's arcade English mode (2 × 25 cells at 12 px) works when gated per slot: no font capacity work at all |
| Endings in `ME.PAC`, boss dialogue boxes | Records after the quotes in each `MCxx`; `MCED.SHP` overlay with Japanese and English scene scripts |
| Attract captions on NBG2 | NBG1, and a ring-buffer LZ the MSHvSF decoder "decoded to size" as garbage |
| No cart → `ERR5` | No cart → `ERR4`; a 1 MB cart passes the check |
| Name toggle infeasible (58 KB of font) | Variants differ by 243 bytes; full Options toggle built |

Things that did match across both (still only HYPOTHESIS for Cyberbots):
Mednafen 1.32.1 with the agent patch; the extractor's 16-bit byte swap; the
4 MiB cart; VDP1 16×16 4bpp sprite text; the font file format (`font.py` /
`font_pack.py` worked unchanged); arcade work RAM mirrored R11-relative in the
Saturn port, still read by region and language branches; every US-name asset
already on the disc; the `.ST2` container; `ERRn.BIN` boot warnings.

### What this means for Cyberbots

Cyberbots (1995 arcade, 1997 Saturn) is a different engine generation from the
two Vs. games, and not a tag game. Expect nothing from them about formats,
renderer modes, selection logic, team buffers, or endings. An early first look
(`research_log.md`, SESSION-0001) already shows a difference: whole Shift-JIS
story scripts sit in plain files on the disc, which neither sibling had.

## Process Lessons (do these differently from the start)

1. **Probe for a native English path before font capacity work.** XvSF's
   "only 59 of 161 quotes fit" and pair-glyph measurements were made moot by
   the leftover English mode. Right after the font is found, look for
   language/region branches around the text renderer.
2. **Do the cheap identity and reference tasks in Phase A.** The Redump check
   (`ENV-007`) and the reference catalog (`DOC-003`) were done the day before
   release.
3. **Put the RetroAchievements guard in the release tools from day one.**
   rcheevos hashes a Saturn disc as the MD5 of the first 512 bytes of track 1
   sector 0's user data; keep the system area unchanged. XvSF's `make_patch`
   and `make_ssp` refuse a build that changes it (`RA-001`, after release).
4. **Start the README in its final layout** (MSHvSF's), not reorganize after
   release.
5. **Boot, cartridge and save warnings belong in the first backlog.** The user
   added them mid-project in both games.
6. **Inventory text surfaces with several captures, not one session.** XvSF's
   single session missed boss boxes, endings, boot warnings, a 16-frame attract
   flash skipped by a 20-frame sample, and a sign the user spotted. Capture each
   condition from a cold boot and sample at least as often as the shortest
   event.
7. **Keep every state in the first user session** (`--keep-states 0`): the
   recorder's default keeps about 3 minutes, and XvSF had to switch its M1
   target to the quote that had checkpoints.
8. **Design per-slot feature flags once**, after the ending investigation.
   XvSF's code patch went through four versions, and old references stayed
   pinned to old versions.
9. **Decide a name-variant toggle right after the name census.** XvSF built two
   separate variant images, then shipped the toggle only.
10. **Build the agent interface right after the stock debugger is proven.**
    Both projects lost time to stock-debugger GUI automation (XvSF `EMU-007`:
    `option+3` was not seen as SDL left-Alt, so typed paths went to the wrong
    prompt).
11. **Split `GATE-M0` (technical) from `GATE-TRANSLATION` (policy) from the
    start.** MSHvSF's original `GATE-M0` blocked M1 on documentation tasks.
12. **No-input replays across a fight diverge.** Force vitality instead; one
    XvSF claim was withdrawn for this.
13. **Free RAM must be proven by read/write logs** across boot, title, attract,
    play and an ending. Zero bytes may be the interrupt-handler table: XvSF's
    first toggle build put code there, hung the title, and wiped test backup
    RAM.
14. **The pixel-diff control for a rebuilt image is the previous build**, not
    the original disc; stream timing drifts.
15. **Copy tools when a task needs them and re-validate each on the new game.**
    This repository copied the game-independent ones up front (`ENV-003`) with
    provenance notes; each is still unvalidated on Cyberbots until the task
    that first uses it says so.

## User Decisions Worth Re-asking (XvSF dates)

Put each to the user as a multiple-choice question in `DOC-002`; never carry
one over silently.

- Official English where it exists, paired by game logic, grammar fixes only as
  an opt-in flag (10-27).
- Recorded new translations where no official English exists (10-27, 10-30).
- Reuse the patched Mednafen (10-27).
- American names by default, consistent across text, art and voice (10-28).
- xdelta + SSP as Release assets; release only after open tasks are done or
  deferred by name (10-27, 11-01).
- Standing rules now in `local_agent_guidance.md`: emulator consent, progress
  estimates, regression scope, deleting finished `build/` images.

## Tools: Which Copy to Use

Copy from XvSF rather than MSHvSF where both exist. Already copied (`ENV-003`):
`disc/hash_source`, `iso9660`, `sector`, `patch_image`; `mednafen/agent`,
`session_recorder`, `replay_state`, `home`, `hotkeys`, `cold_boot`,
`frame_capture`, `backup_ram`; `memory/mcs_extract`, `diff`, `vdp1_sprites`,
`vdp2_plane`; `sh2/asm`, `disasm`; `text/search`, `pattern_search`,
`code_search`; `reference/mame_audit`, `listxml_match`, both Lua scripts.

Copy when a task needs them:

| Need | Source |
| --- | --- |
| Release patches with RA guard | XvSF `tools/disc/make_patch.py`, `make_ssp.py` (parameterize the source folder, manifest, author) |
| Regression references | XvSF `tools/disc/regression.py` (structure; flags are XvSF's) |
| Release zips | XvSF `research/experiments/EXP-0071/make_zips.py`, `check_zips.sh` (promote into `tools/`) |
| Font decode/repack, if the format matches | XvSF `tools/text/font.py`, `font_pack.py` |
| Pair glyphs, caption compiler, if no English mode | MSHvSF `tools/text/pair_font.py`, `caption_compiler.py` |
| Live breakpoint logging during play | MSHvSF `tools/mednafen/bp_log.py`, `write_trial.py` |
| State patching (cart RAM) | MSHvSF `tools/memory/mcs_patch.py` |
| CPS-II graphics ROM decode | MSHvSF `tools/reference/cps2_gfx.py` |
| Voice/ADPCM | MSHvSF `tools/audio/*` |
| No-play route to an ending | XvSF `tools/mednafen/route.py` (pattern only; addresses are XvSF's) |
| A compressor template | XvSF `tools/disc/prs.py` (`compress` with lazy matching) |

## Open Questions Both Siblings Left

- Whether RetroAchievements memory conditions survive a patch; whether the site
  lists the header hash.
- Slave-SH-2 and DMA writers are invisible to stock write breakpoints.
- Cart-RAM extraction from save states was never validated.
- Cold-boot frame divergence that depends on the host clock (try a pinned RTC).
- Graphical xdelta patchers and the official SSP GUI on Windows are untested.
