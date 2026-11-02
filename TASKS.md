# Dependency-Controlled Research Plan

This is an evidence gate, not a generic backlog. `AGENTS.md` is authoritative.
Statuses are `BACKLOG`, `BLOCKED`, `READY`, `IN_PROGRESS`, `DONE`, and `REJECTED`.
At most one reverse-engineering experiment may be `IN_PROGRESS`.

The task order follows the "Verify on X" checklist in
`docs/playbook_from_mshvsf.md`, corrected by `docs/lessons_from_xvsf.md`.
Task IDs are this project's own; where a task repeats a sibling task, the note
names it for its method only.

## Current State

- **2026-11-02: repository set up** (`SESSION-0001`). Phase A is done except
  the database check (`ENV-007`): Python project, rules, ignore list, the
  game-independent sibling tools with provenance, and the identity of the
  Saturn source image (`references/saturn_jp/README.md`). The arcade sets are
  hashed and verify in MAME 0.289 (`REF-001`, partly done).
- A first static look at the disc is in `research_log.md` (SESSION-0001). All
  of it is **HYPOTHESIS** until a runtime experiment confirms it. The most
  important observation: about 23,000 characters of plain Shift-JIS story
  dialogue sit in three files, `END.BIN`, `VICTORY.BIN` and `STG0AS.BIN`.
- **2026-11-02: user decisions recorded** (`DOC-002`, `SESSION-0002`,
  `docs/localization_policy.md`): official arcade English with fixes opt-in;
  recorded new translations where none exists; both name variants, US default;
  all four extra scopes eventually; xdelta + SSP after open tasks; patched
  Mednafen reuse approved; arcade-only references (`REF-002` `REJECTED`).
- Reverse-engineering experiments in progress: none.
- **2026-11-02: stock Mednafen 1.32.1 built** (`EMU-001`, `SESSION-0003`,
  `docs/mednafen.md`), from XvSF's archive (hash checked, no download).
  Mednafen's database gives `T-1217G` the 1 MiB cart (`EMU-004` tests it).
- **2026-11-02: project-local Mednafen homes pinned** (`EMU-002`,
  `SESSION-0004`): interactive and silent homes, Japanese and US BIOS
  verified against Mednafen's documented hashes.
- **2026-11-02: Cyberbots boots** (`EMU-003`, `EXP-0001`, D-001): three
  silent cold boots reach the title at about 57 s, identical frames;
  Mednafen gives it the 1 MiB cart. D-002: each audio track has one ISO
  entry. No Japanese text in the first two minutes of boot and attract.
- **2026-11-02: no cart needed for boot and attract** (`EMU-004`,
  `EXP-0002`, D-003): `none` and a save cart give the same screens with
  ~1 s shifts; 1 MiB and 4 MiB carts identical. `ss.cart auto` (1 MiB) kept.
- **2026-11-02: pad bindings copied from the siblings** (`EMU-005`, the
  user's instruction); both homes now equal XvSF's configurations.
- **2026-11-02: screenshots and states work by hotkey** (`EMU-006`,
  `EXP-0003`, D-004): a title state reloads byte-identically in-session and
  in a fresh cold boot.
- **2026-11-02: the stock debugger works unattended** (`EMU-007`,
  `EXP-0004`, D-005): repeatable WRAM-L/WRAM-H dumps at a freeze, an exact
  write and restore, a write breakpoint that halts. The dumps and a state of
  the same instant are ready for `DBG-001`.
- **2026-11-02: save-state extraction validated** (`DBG-001`, `EXP-0005`,
  D-006) for WRAM-L, WRAM-H, VDP1 and VDP2 VRAM; cart RAM not validated.
- **2026-11-02: agent interface built and validated** (`EMU-020`,
  `EMU-021`, `EXP-0006`, D-007): reads, writes, halt control and
  breakpoints are scriptable; the M0 emulator work is complete.
- **2026-11-02: offline references done** (`SESSION-0006`): the source image
  equals Redump 58190 (`ENV-007`); the arcade sets are identified by SHA-1
  and boot headless (`REF-001`); `docs/references.md` catalogs platform
  references and Cyberbots prior art (`DOC-003`). Secondary sources say the
  console ports add four pilots with no arcade English, and voiced story.
- **2026-11-02: arcade English found and decoded** (`REF-003`, `EXP-0008`,
  D-009): 530 English records behind a 624-slot table, one byte per
  character; the same English (and Spanish and Japanese tables) in every
  held set.
- **2026-11-02: arcade English confirmed on screen** (`REF-004`,
  `EXP-0009`, D-010): the slot variable `0xFF2F7A`, the region byte that
  picks the table, and the last four codes; the decoder now covers all
  English records. The Japanese arcade's first line opens like the Saturn's.
- **2026-11-02: Saturn script paired with the arcade** (`REF-006`,
  `EXP-0010`, D-011): 825 of Saturn lines 0-898 pair with arcade slots, and
  so with official English; Saturn lines 899-1850 (952) have no arcade
  counterpart (console-only stories, SUPPORTED) and so no official English.
- **2026-11-02: play session recorded and reviewed** (`REF-005`,
  `EXP-0011`, D-012): Japanese appears in dialogue boxes, VS-screen chapter
  captions (Saturn-only lines 899-952) and katakana name art; everything
  else seen is English. 166 states kept as checkpoints.
- **2026-11-02: names inventoried** (`REF-007`, `EXP-0012`): one set of
  names in both regions; only the pilot-select and VS-screen name art differs
  (katakana or Latin). User decision: an Options-screen toggle, Latin by
  default (`docs/localization_policy.md`).
- **2026-11-02: M1 target chosen** (`REF-008`, `EXP-0013`): Jin's first
  pre-fight box, Saturn lines 4-5 (arcade slot 2), checkpoint
  `local/ref005/session/states/f00005386.mcs`, replayed exactly. Milestone
  unit: the box.
- **2026-11-02: dialogue fixed from a checkpoint** (`DBG-002`, `EXP-0014`,
  D-014): six replays, same box and reply; timing varies by a few frames.
- **2026-11-02: M1 checkpoints saved** (`DBG-003`, `EXP-0015`): box open,
  box complete, after the box, in the ignored `local/checkpoints/m1/`; each
  verified by replay.
- **2026-11-02: renderer and RAM text found** (`DBG-004`, `EXP-0016`,
  D-015): lines 4-5 are plain Shift-JIS in WRAM-H inside the resident
  `STG0AS.BIN`; VDP1 draws one sprite per character from refilled glyph
  cells.
- **2026-11-02: `GATE-M0` passed.** The user's words: "GO for M1".
- **2026-11-02: M1 CONFIRMED** (`RE-001`, `EXP-0017`, D-016): Shift-JIS
  written to WRAM-H `0x0606F09C` before the box typed changed the box's first
  line on screen; the no-write control showed the original. Next: M2, with
  `DISC-001`, `DISC-002` and `FONT-001` written up in full before they start.
- **2026-11-02: M2 tasks written up** (`DISC-001`, `DISC-002`, `FONT-001`).
- **2026-11-02: M1 text traced to its disc file** (`DISC-001`, `EXP-0018`,
  D-017): `STG0AS.BIN`, loaded raw to `0x06060000` when the first stage
  starts; line 4 is at file offset `0xF09C`.
- **2026-11-02: M2 CONFIRMED** (`DISC-002`, `EXP-0019`, D-018): an image
  rebuilt from the untouched source, with one sector of `STG0AS.BIN`
  changed, shows the M1 box changed, in a replay and after a cold boot played
  by the agent with pad keys. User decision: the agent runs cold-boot play
  checks itself.
- **2026-11-02: dialogue font found** (`FONT-001`, `EXP-0020`, D-019):
  `KANJI.BIN`, 1,280 16×16 4 bpp glyphs (byte-identical repack), selected
  through a 1,222-code table in `STG0AS.BIN`; it has full-width A-Z and 0-9.
  Next: write up `FONT-002` in full.
- **2026-11-02: script census** (`TXT-001`, `EXP-0007`, D-008): one
  byte-identical table of 1,851 Shift-JIS dialogue lines in `VICTORY.BIN`,
  `END.BIN` and `STG0AS.BIN`, each line pointed to from records at base
  `0x06060000`; lines at most 16 full-width characters. Static facts only.
- Confirmed so far: D-001 (boot), D-002 (audio-track layout), D-003 (no cart
  needed for boot and attract), D-004 (screenshots and states by hotkey),
  D-005 (stock debugger dumps, writes, breakpoints), D-006 (state extractor
  valid for work RAM and VRAM), D-007 (agent interface), D-008 (shared
  dialogue table, static), D-009 (arcade English dialogue table), D-010
  (arcade dialogue on screen and its selection), D-011 (Saturn-arcade
  pairing), D-012 (text surfaces in an ordinary run), D-013 (names), D-014
  (dialogue fixed from a checkpoint), D-015 (Shift-JIS RAM text, VDP1
  per-character sprites), D-016 (M1: the box changed in live RAM), D-017
  (the M1 text's disc file), D-018 (M2: the change from a rebuilt image), D-019
  (the dialogue font and its code table). The font's
  layout is not confirmed.

## Milestones

Cyberbots' Japanese text is mostly pilot story dialogue between fights, not
win quotes, so the sibling milestones are re-anchored on dialogue lines. The
exact unit ("line", "box", "exchange") is fixed by `REF-008` from evidence.

| ID | Required outcome |
| --- | --- |
| M0 | Mednafen runs; Cyberbots boots with the right cartridge setting; pad, screenshots, save states, debugger, agent interface, validated extraction, documentation, and Python tooling work. |
| M1 | One ordinary pilot's story dialogue box is visibly modified in live Saturn RAM (unit fixed by `REF-008`: a box, one or two Saturn lines). |
| M2 | The same change is reproduced from an untouched source image. |
| M3 | All of that pilot's story dialogue is handled programmatically. |
| M4 | A second pilot works through the same generalized mechanism. |
| M5 | All ordinary story dialogue (and win quotes, if they are a separate surface) can be localized systematically. |
| M6 | Investigation of ending text begins only after M5. |
| M7 | One ending is localized. |
| M8 | A general ending-localization pipeline works. |
| M9 | Special cases (boss or hidden pilots, alternate routes, other surfaces) may be investigated, each with an explicit task. |

Two gates control the work, split from the start (`docs/lessons_from_xvsf.md`,
lesson 11): `GATE-M0` (technical prerequisites for the first live RAM
mutation) and `GATE-TRANSLATION` (reference and policy prerequisites before
English text goes on disc).

## Phase A: Repository And Environment

### ENV-001 - Create Python uv project

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Define an installable Python 3.12+ project managed by uv.
- **Acceptance criteria:** `pyproject.toml` declares the project, Python floor, build backend, and development dependency group; `uv.lock` is committed after synchronization.
- **Notes:** Done 2026-11-02, adapted from the XvSF `pyproject.toml` (renamed). uv 0.11.7; zero runtime dependencies.

### ENV-002 - Implement setup_venv.sh and invenv.sh

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001.
- **Blockers:** None.
- **Objective:** One command creates the environment; one wrapper runs tools in it.
- **Acceptance criteria:** `./setup_venv.sh` syncs all groups; `./invenv.sh CMD` runs `CMD` in the project environment without an activated shell.
- **Notes:** Copied unchanged from XvSF (`a1c82ba`). Both worked on 2026-11-02.

### ENV-003 - Add linting, formatting, typing, tests, and the game-independent tools

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Make `pytest`, `ruff check`, `ruff format --check`, and strict `mypy` pass from the first commit, with the sibling tools that hold no game facts.
- **Acceptance criteria:** All four commands pass through `./invenv.sh`; every copied file carries a provenance note (source repository, path, commit).
- **Notes:** 2026-11-02: copied from XvSF `a1c82ba`: `tools/disc/{hash_source,iso9660,sector,patch_image}`, `tools/mednafen/{agent,session_recorder,replay_state,home,hotkeys,cold_boot,frame_capture,backup_ram}`, `tools/memory/{mcs_extract,diff,vdp1_sprites,vdp2_plane}`, `tools/sh2/{asm,disasm}`, `tools/text/{search,pattern_search,code_search}`, `tools/reference/{mame_audit,listxml_match,*.lua}`, and their tests. Left out as XvSF-format-specific: `prs`, `font`, `font_pack`, `route`, `st2_*`, release and build tools (`docs/lessons_from_xvsf.md`, "Tools"). 119 tests passed; ruff and mypy clean. **Copied is not validated:** each tool is re-validated on Cyberbots by the first task that uses its output as evidence (`AGENTS.md` rule 26).

### ENV-004 - Create repository documentation skeleton

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Rules, protocol, task list, log, discoveries, unknowns, and experiment template exist.
- **Acceptance criteria:** `AGENTS.md`, `README.md`, `TASKS.md`, `research_log.md`, `docs/research_protocol.md`, `docs/discoveries.md`, `docs/known_unknowns.md`, `research/README.md`, and `research/experiments/README.md` exist and are non-empty.

### ENV-005 - Create .gitignore and local guidance

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Keep game data, evidence, and machine-local guidance out of git.
- **Acceptance criteria:** `git check-ignore` reports `local/`, disc formats, archives, states, and `local_agent_guidance.md` as ignored.
- **Notes:** The ignore list is XvSF's. `local_agent_guidance.md` carries the user preferences from both siblings, including the four XvSF rules that had lived only in that project's agent memory (emulator consent, progress estimates, regression scope, deleting finished images).

### ENV-006 - Record immutable source identity

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Record filename, size, SHA-256, and release description of every Saturn source component.
- **Acceptance criteria:** Every component is hashed with `tools/disc/hash_source.py` and recorded with a release description.
- **Notes:** 2026-11-02: 63 components of `Cyberbots - Fullmetal Madness (Japan) (2M)` in `references/saturn_jp/README.md`. Header `T-1217G V1.002 19970219`. Identity is **SUPPORTED**, not database-verified (see `ENV-007`).

### ENV-007 - Verify the source image against a database

- **Status:** `DONE`
- **Milestone:** M0 (do early; XvSF did this the day before release)
- **Dependencies:** ENV-006.
- **Blockers:** None.
- **Objective:** Raise the image identity from **SUPPORTED** to **CONFIRMED**, and learn what "(2M)" in the Redump name distinguishes.
- **Acceptance criteria:** Track hashes match a named database entry (size, CRC-32, MD5, SHA-1 per track), or a mismatch is recorded with its consequence; any other Redump entries for this title are listed with how their track 01 differs.
- **Notes:** The release patch must name the exact image it applies to either way. Done 2026-11-02 (`SESSION-0006`): all 62 tracks and the CUE equal Redump 58190 ("(2M)", T-1217G, Original, mastering `T-1217GP-01438 2MB1`) in SHA-1, MD5 and CRC-32. The other entry, 3669 ("(1M)", T-1216G, Limited Edition, mastering `…1M2`), has the same track 01 and different audio tracks. "(2M)"/"(1M)" mark the masterings. `references/saturn_jp/redump_*.json`. The earlier refusal came from the web-fetch tool; `curl` and the built-in browser worked.

## Phase B: Documentation And Decisions

### DOC-001 - Carry over the sibling playbooks

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** None.
- **Blockers:** None.
- **Objective:** Give every session the sibling method, pitfalls, and tools list without treating any of it as Cyberbots fact.
- **Acceptance criteria:** `docs/playbook_from_mshvsf.md` is a copy of the current MSHvSF `docs/playbook_cross_game.md` with its source commit; `docs/lessons_from_xvsf.md` digests what did and did not transfer to XvSF.
- **Notes:** 2026-11-02: playbook from MSHvSF `447e573`; XvSF digest from XvSF `a1c82ba`. Re-copy when either source changes; record the new commit.

### DOC-002 - Confirm the sibling user decisions for Cyberbots

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** DOC-001.
- **Blockers:** None.
- **Objective:** Ask the user to confirm, change, or defer each decision in the playbook's "The User's MSHvSF Localization Decisions" table and `docs/lessons_from_xvsf.md` "User Decisions Worth Re-asking".
- **Acceptance criteria:** Each decision has a recorded Cyberbots answer (verbatim, dated) or an explicit deferral to the task that produces its evidence, in `research_log.md` and `docs/localization_policy.md` (created by this task, on the XvSF file's structure: answered / deferred / per-gate tables).
- **Notes:** Done 2026-11-02 (`SESSION-0002`): three rounds of multiple-choice questions, ten decisions answered, seven evidence-dependent decisions deferred to named tasks. All in `docs/localization_policy.md`; `AGENTS.md` rules 16 and 21 now cite the answers.

### DOC-003 - Build the reference catalog

- **Status:** `DONE`
- **Milestone:** M0 (do early)
- **Dependencies:** DOC-001.
- **Blockers:** None.
- **Objective:** Reuse the sibling platform references and list Cyberbots-specific prior art.
- **Acceptance criteria:** `docs/references.md` lists the platform references (Saturn, SH-2, CD/ISO 9660, Mednafen, CPS-II, MAME) with their sibling source, and separately any Cyberbots prior art: translation projects, text dumps, script comparisons, official English releases.
- **Notes:** Done 2026-11-02: `docs/references.md`, platform sections copied unchanged from XvSF `9cb01ad` (identical to MSHvSF `abd3fa6`), plus "Cyberbots Prior Art". No Saturn translation found. TCRF's arcade page and Lost In Translation's page are behind bot checks and stay unread leads for `REF-003`; Hardcore Gaming 101 was in maintenance.

### DOC-004 - Start the README in its final layout

- **Status:** `BACKLOG`
- **Milestone:** before REL-001
- **Dependencies:** DOC-002.
- **Blockers:** None.
- **Objective:** Avoid XvSF's post-release README reorganization.
- **Acceptance criteria:** `README.md` follows the MSHvSF README's section layout, with placeholders for what is not done.

## Phase C: Emulator

### EMU-001 - Pin and build stock Mednafen

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-002.
- **Blockers:** Ask before downloading source or installing build dependencies.
- **Objective:** Have a stock Mednafen build under ignored `vendor/` with its exact version, source URL, hash, and build commands recorded.
- **Acceptance criteria:** `docs/mednafen.md` records the version, source hash, configure and build commands, and the binary's `-help` banner.
- **Notes:** Done 2026-11-02 (`SESSION-0003`). Archive copied from XvSF `local/downloads/mednafen-1.32.1/`, SHA-256 `de7eb94a…3832` as both siblings recorded, so nothing was downloaded. Configure and `make -j12` exited 0 (2 min 46 s). Binary `vendor/mednafen/build/src/mednafen`, 21,327,272 bytes, SHA-256 `077ac658…669f`; `-help` shows 1.32.1 with the `ss` module. Homebrew's `mednafen` is not the pinned build.

### EMU-002 - Create the project-local Mednafen configuration

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-001.
- **Blockers:** None.
- **Objective:** Run Mednafen with a configuration and BIOS path local to this checkout, never the user's global configuration.
- **Acceptance criteria:** The launch command, base directory, BIOS identity (filename, size, SHA-256), and forced settings are recorded; `tools/mednafen/home.py` pins the interactive and quiet homes.
- **Notes:** Done 2026-11-02 (`SESSION-0004`, `docs/mednafen.md`). Homes `local/mednafen/` and `local/mednafen_quiet/` pinned by `tools/mednafen/home.py` (17 settings; quiet adds volume 0, no vsync, no blit timesync); config SHA-256 `48a7cf6b…28fc` and `ef897288…5019`, equal to XvSF's. Both load 7,904 valid settings, 0 unknown. BIOS `sega_101.bin` (`dcfef4b9…deac`) and `mpr-17933.bin` (`96e106f7…266f`) copied from XvSF, equal to the hashes in Mednafen's `Documentation/ss.html`.

### EMU-003 - Boot Cyberbots

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-002, ENV-006.
- **Blockers:** Needs the user present (`local_agent_guidance.md`, "Emulator Consent").
- **Objective:** Reach the title screen from a cold boot of the untouched image.
- **Acceptance criteria:** Three cold boots reach a stable title screen; the boot log shows `T-1217G`; source hashes match before and after; screenshots kept locally.
- **Notes:** Done 2026-11-02 (`EXP-0001`, D-001). Three 120 s boots, exit 0, 119 of 119 per-second frames identical; `SGID: T-1217G`, `Cart: 1MiB Extended RAM`; title logo from about 57 s, `PRESS START BUTTON` 61-66 s (frame 064 `e9f12474…ee24`); 63 source components unchanged. `tools/mednafen/cold_boot.py` re-validated here. Side result D-002: the 61 ISO entries past track 01 are the 61 audio tracks, one each.

### EMU-004 - Determine the cartridge requirement

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** Needs the user present (emulator consent).
- **Objective:** Find which cartridge setting the game needs, with controls.
- **Acceptance criteria:** Boots with `ss.cart` set to `none`, `extram1` and `extram4` are each recorded (log line, what the game shows, how far it gets); the project setting is chosen from that evidence.
- **Notes:** Done 2026-11-02 (`EXP-0002`, D-003): `none`, `backup`, `extram1`, `extram4`, one 120 s boot each. No warning with any; `extram1`/`extram4` byte-identical to D-001; `none`/`backup` same screens with ~1 s timing shifts. Only boot and attract tested; a check at Start or in play is not excluded. Project setting stays `ss.cart auto`. Before the test: both siblings needed the 4 MiB cart; Cyberbots was **UNKNOWN**. Mednafen 1.32.1's database lists `T-1217G` as `CART_EXTRAM_1M` with no "Game requirement" note (`docs/mednafen.md`), so `ss.cart auto` should give it 1 MiB; the header's peripheral field reads `JW`, and the Redump name carries "(2M)", whose meaning is not yet known (`ENV-007`). The `WARNING0-4.PIX` files may be the cart or save warnings (`UI-004`).

### EMU-005 - Configure and document the pad

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** None.
- **Objective:** The user's controller drives every button the game uses, and Start, in game.
- **Acceptance criteria:** A mapping table is recorded and each button is observed in the game's button configuration or in play.
- **Notes:** Done 2026-11-02 (`SESSION-0005`, `docs/mednafen.md` "Pad Mapping"). The user said: "You should be able to use the same configuration for the pad you had in MSHvSF and XvSF." The 13 port 1 bindings, identical in both siblings, were copied from XvSF's interactive configuration into both homes; both now equal XvSF's files (`cb1c2d3b…a1e9`, `aad9a7ef…57cf`). The in-game button check is replaced by the user's instruction and the mapping's use in both siblings (XvSF: "Everything worked as expected"); which game action each button performs in Cyberbots (the arcade has two weapons, boost and jump) is recorded at the first play session (`REF-005`).

### EMU-006 - Verify screenshots and save states

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-003.
- **Blockers:** None.
- **Objective:** Screenshots and save/load states work and are stored under ignored paths.
- **Acceptance criteria:** A state saved and reloaded reproduces the same screen; files are ignored by git.
- **Notes:** Done 2026-11-02 (`EXP-0003`, D-004). With `tools/mednafen/hotkeys.py --keep-focus`: F9 screenshots, F5 state (1,099,526 bytes, `a904685f…1a69`), F7 load in-session and into a fresh cold boot; the reloaded title equals a screenshot taken at save time byte for byte; state unchanged by loading; files under ignored `local/`. One F9 was lost in a run without `--keep-focus` (cause unknown). `hotkeys.py` re-validated here.

### EMU-007 - Verify debugger access and memory dumps

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-006.
- **Blockers:** None.
- **Objective:** Dump WRAM-L and WRAM-H at a paused instant with the stock debugger.
- **Acceptance criteria:** Dumps of `0x00200000-0x002FFFFF` and `0x06000000-0x060FFFFF` are saved with sizes and hashes recorded; a memory write and a write breakpoint are each observed once.
- **Notes:** Done 2026-11-02 (`EXP-0004`, D-005), unattended, in three runs (about 6 minutes). Run A2: WRAM-L `bb0628a5…517c` and WRAM-H `fc70d589…8b10`, each dumped twice identically at the title freeze; write test at WRAM-H `0xF0000` exact; state `52ce80ae…b311` saved at the same freeze (for `DBG-001`). Run F: breakpoint on all WRAM-H halted at PC `060008F0`, `mov.l r0,@-r15`. Run A silently lost its WRAM-L dumps (cause unknown). Kept minimal, as planned: both siblings lost time to stock-debugger GUI automation.

### EMU-020 - Record why stock Mednafen is insufficient

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-007, DOC-002.
- **Blockers:** None.
- **Objective:** Satisfy `AGENTS.md` rule 16 before using the patched build.
- **Acceptance criteria:** A short record cites MSHvSF `EMU-012`/`EMU-020` and XvSF `EMU-020` and confirms the same limits apply here; the user's `DOC-002` answer on reusing the patch is cited.
- **Notes:** `DOC-002` answer (2026-11-02): "Yes, reuse it (Recommended)". Done 2026-11-02: `docs/mednafen_agent_interface.md`, "Why Stock Is Not Enough": the sibling limits apply, plus three silent key-driven failures here (`EXP-0003` run 1, `EXP-0004` run A, `EXP-0005` run G).

### EMU-021 - Build and validate the agent interface

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-020.
- **Blockers:** None.
- **Objective:** Drive Mednafen from Python so the user only plays.
- **Acceptance criteria:** `vendor/mednafen/patches/0001-agent-interface.patch` (`c30146ef…5244`) applies to the pinned version and builds; validations V1-V4 (`docs/mednafen_agent_interface.md`) pass on Cyberbots states; `tools/mednafen/agent.py` tests pass.
- **Notes:** Done 2026-11-02 (`EXP-0006`, D-007). Patch applied cleanly; build 3 min 10 s; binary `2fc3d547…eaaf`. V1 119/119 frames equal D-001 without the agent directory; V2 four reads equal same-poll extraction; V3 exact round trip and halt control; V4 10,822 log-mode hits on game-variable ranges with frames advancing; V4b halt with registers (PC `060008F0`, confirming `EXP-0004`'s by-eye reading). Agent tests pass (119 total).

### DBG-001 - Validate the save-state extractor on Cyberbots

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** EMU-007.
- **Blockers:** None.
- **Objective:** Extract WRAM-L, WRAM-H, VDP1 and VDP2 VRAM from states, validated byte for byte against debugger dumps of the same instant on Cyberbots.
- **Acceptance criteria:** Each region matches a stock debugger dump exactly; the result goes to `docs/discoveries.md`; cart RAM stays `HYPOTHESIS`.
- **Notes:** Both siblings found each stored 16-bit element byte-swapped. Re-tested, not assumed. Done 2026-11-02 (`EXP-0005`, D-006): with the swap, WRAM-L and WRAM-H (instants A2 and H) and VDP1/VDP2 VRAM (instant H) equal the debugger dumps; without it, every region differs. Cart RAM: the state holds 1 MiB (`LO`/`HI` 512 KiB each); the tool's `cart_ram` entry expects XvSF's 4 MiB and refuses, so the no-`--region` default fails on Cyberbots. Run G failed silently first (`option+3` not taken); run H, keys one second apart, worked.

## Phase D: References And The Translation Oracle

### REF-001 - Intake the arcade sets

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Identify every arcade zip and key against a pinned MAME, and boot the sets needed for capture.
- **Acceptance criteria:** Each file is hashed and matched to a MAME set name; the pinned MAME version and driver source are recorded; the US set boots headless.
- **Notes:** 2026-11-02 (`references/arcade/README.md`): all five supplied zips hashed; with `qsound.zip` added, all five verify in MAME 0.289 (`cybots` Europe 950424, `cybotsu` USA 950424, `cybotsj` Japan 950420, `cybotsud` and `cybotsjd` decrypted bootlegs). Done 2026-11-02 (`SESSION-0006`): every member matched by SHA-1 against `mame -listxml 'cybots*'` (`references/arcade/manifest.json`); `cps2.cpp` pinned (`a8c09ef8…1602`, as the siblings), `mame_audit` 21/21 on `cybots.zip`; `cybotsu` and `cybotsj` boot headless (exit 0) into attract mode with `INSERT COIN`.

### REF-002 - Intake a PlayStation image (optional)

- **Status:** `REJECTED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** DOC-002.
- **Blockers:** None.
- **Objective:** Decide whether a PS1 release adds a reference.
- **Acceptance criteria:** Either every component is hashed with an identity status, or the task is `REJECTED` with the user's reason.
- **Notes:** Rejected 2026-11-02 by the user's `DOC-002` answer "No, arcade only (Recommended)": the PS1 release is Japanese-only and adds no official English.

### REF-003 - Locate and decode the arcade English text

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-001.
- **Blockers:** None.
- **Objective:** Find where the arcade stores its English story dialogue, win quotes (if any) and ending text, and how it is encoded.
- **Acceptance criteria:** A decoder reproduces known English strings from the local ROM; the table shape, pointer tables and regional differences are recorded; punctuation mappings are tested statistically.
- **Notes:** The decrypted program image (`cybotsud`: `cybu_d.03` + `cybu_d.04`, word-swapped) holds only a few ASCII strings (region names, RAM test, `WON LOST CONTINUE ENDING`). The dialogue is therefore in another encoding or in another ROM; XvSF found its English with an offset histogram of common words, MSHvSF as 16-bit codes. Trace the arcade's readers (`mame_timeline.lua` `logreads`), do not stop at a data search. Done 2026-11-02 (`EXP-0008`, D-009) by relative search: the English is one byte per character (ASCII + 9 for capitals, + 3 for lowercase) in the region ROMs, 530 records behind a 624-slot table at `0x0B33AA`, plus Spanish and Japanese tables of the same layout; identical in all five sets. Decoder `tools/reference/cybots_text.py`. Open: codes `09`/`0B`/`18`/`1C`, header meaning, whether endings are in the table; these and the reader trace move to `REF-004`.

### REF-004 - Confirm the decoded arcade text on screen

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-003.
- **Blockers:** None.
- **Objective:** Show that the decoded table is what the arcade draws.
- **Acceptance criteria:** A scripted MAME route shows a predicted entry on screen, with the RAM pointer that selects it.
- **Notes:** Also settle from the screen or the tiles: codes `09`, `0B`, `18`, `1C`; which of the three tables each region draws; whether endings come from the 624-slot table. Done 2026-11-02 (`EXP-0009`, D-010): records 0-5 shown on screen as predicted; slot variable `0xFF2F7A` (written by `0x011D48`); region byte `0xFF80A0` picks the table; the four codes are `:`, `-`, `"`, `.`. Endings not reached: moved to `END-001`.

### REF-005 - Inventory the Saturn text surfaces

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** EMU-021.
- **Blockers:** None.
- **Objective:** List every place the Saturn release shows Japanese text.
- **Acceptance criteria:** `docs/text_surfaces.md` holds a table of surfaces (screen, when shown, sample screenshot path and hash, whether the arcade has English for it) from screenshots the agent reviewed, built from several captures: a cold boot left on the attract loop (sampled at least every frame of the shortest event), boot without cart and with a corrupt save (`UI-004`), one story run through at least two fights with a continue, options and other menus.
- **Notes:** XvSF's single session missed five surfaces (`docs/lessons_from_xvsf.md`, lesson 6). Keep every state (`--keep-states 0`). Done 2026-11-02 (`EXP-0011`, D-012, `docs/text_surfaces.md`) from the boot/attract captures plus one 8-minute session (title, select, two fights, a loss, continue, game over, options; 484 screenshots and 166 states kept). The cart-less and corrupt-save boots in the criteria were not run: no warning screen appeared without a cart (D-003), and save warnings stay with `UI-004`. Not reached and listed as such: endings, versus mode, option sub-screens, console-only pilots.

### REF-006 - Compare the Saturn script with the arcade script

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** TXT-001, REF-003.
- **Blockers:** None.
- **Objective:** Decide whether the Saturn dialogue is the arcade Japanese dialogue unchanged, and so whether the arcade English is a line-for-line oracle.
- **Acceptance criteria:** Per pilot and route, the Saturn lines (from `TXT-001`) are compared with the arcade Japanese lines; Saturn-only and arcade-only lines are listed.
- **Notes:** Done 2026-11-02 (`EXP-0010`, D-011) with `tools/text/arcade_pairing.py`: arcade Japanese map learned from the two scripts (573/579 codes, no conflicts); 787 exact and 38 edited line pairs in 450 slots; Saturn-only: 74 lines in 50 short runs, and lines 899-1850; arcade-only: 51 lines. `cybotsj` shows the same slot numbers as `cybotsu` in the first scene, so slot = English slot. Per-pilot and per-route breakdown needs the Saturn record structures (D-008) or play: left to `RE-002`.

### REF-007 - Inventory pilot and mech names across releases

- **Status:** `DONE`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-004, REF-005.
- **Blockers:** None.
- **Objective:** List every pilot and VA (mech) name the Saturn shows as art or text or speaks, and where the arcade English differs.
- **Acceptance criteria:** A name table with sources; whether both conventions' assets are already on the disc; options and costs presented to the user; the toggle question decided right after (`docs/lessons_from_xvsf.md`, lesson 9).
- **Notes:** Done 2026-11-02 (`EXP-0012`, D-013, `docs/names.md`). Names are the same in both regions; only the name art differs. The Saturn's VS name art is raw sprite data in `SELECT.VAD`; whether Latin name art is on the disc is UNKNOWN and moved to `LOC-001` (a full answer needs the VS-screen draw code). Options and costs put to the user; decision: Options-screen toggle.

### REF-008 - Choose the first pilot and line

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** REF-005, TXT-001.
- **Blockers:** None.
- **Objective:** Pick one ordinary pilot and one dialogue line as the M1 target, and fix the milestone unit (line, box, or exchange).
- **Acceptance criteria:** The choice and reason are recorded; the Japanese is captured on screen, transcribed, and matched to its `TXT-001` record; a checkpoint shortly before the line exists.
- **Notes:** Done 2026-11-02 (`EXP-0013`): Jin's first pre-fight box to Shade, Saturn lines 4-5 (exact pairs with arcade slot 2), chosen as the first ordinary-pilot box with official English. On screen at session frames 5386-5693; transcription in the ignored `local/ref008/transcription.txt`. Checkpoint `f00005386.mcs` (`1e8adce3…9b56`): replay matches the session's box byte for byte. Unit fixed: the box (one arcade record, one or two Saturn lines).

## Phase E: Text, Checkpoints And Memory Analysis

### TXT-001 - Offline census of the plain Shift-JIS script blocks

- **Status:** `DONE`
- **Milestone:** M1 (static analysis only; no image change)
- **Dependencies:** ENV-003.
- **Blockers:** None.
- **Objective:** Describe the Shift-JIS dialogue found in `END.BIN`, `VICTORY.BIN` and `STG0AS.BIN` (SESSION-0001) without assuming it is what the game draws.
- **Acceptance criteria:** A script (`tools/text/`) lists every string in each file with its offset, byte length, terminator and the bytes around it; the three copies are compared (identical or not, and where each block starts and ends, e.g. the `SsCB` marker seen before it); any pointer or index table that addresses the strings is located; control bytes (line breaks, speaker, waits, name placeholders) are tabulated with counts; every other data-track file is scanned the same way and the results recorded. Committed output: offsets, lengths, hashes and counts only, no game text (`AGENTS.md` rule 21).
- **Notes:** Whether the game reads these bytes as Shift-JIS at runtime, and which copy it reads when, are **runtime questions** for `DBG-004` and `DISC-001`. Done 2026-11-02 (`EXP-0007`, D-008) with the new `tools/text/script_census.py` (9 tests) instead of `search.py`; output `data/text/script_census.json`. The three copies' 50,112-byte dialogue regions are byte-identical (1,851 lines plus `SsCB`); no control bytes inside lines (one string = one line); pointers at base `0x06060000` in records after the table (gaps of 8/16/24/32 bytes); all 264 files scanned, no other block.

### DBG-002 - Observe dialogue selection behaviour

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** EMU-021, REF-008.
- **Blockers:** None.
- **Objective:** Learn whether the dialogue shown from one checkpoint is fixed or varies, before planning checkpoints.
- **Acceptance criteria:** Several replays of one pre-dialogue state, with the lines shown recorded.
- **Notes:** Done 2026-11-02 (`EXP-0014`, D-014): 4 replays of `f00005386` and 2 of `f00005208`; all show Saturn lines 4-5 then Shade's reply; two timing variants a few frames apart.

### DBG-003 - Capture dialogue checkpoints

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** DBG-002.
- **Blockers:** None.
- **Objective:** States and screenshots before the dialogue starts, with the target line visible, and after it is gone.
- **Acceptance criteria:** Each checkpoint is reproducible from its state and named in an experiment record.
- **Notes:** Done 2026-11-02 (`EXP-0015`): `a-box-open` (`236c610e…`), `b-box-complete` (`b32db0c2…`), `c-after-box` (`e21021b1…`) in `local/checkpoints/m1/`, each replayed and checked by dialogue-strip hash. A first capture at 300 frames was too late (the box had closed by the save) and was discarded.

### DBG-004 - Find the dialogue renderer and its RAM text

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** DBG-001, DBG-003.
- **Blockers:** None.
- **Objective:** Determine whether the dialogue is VDP1 sprites or VDP2 tiles, and find the RAM text that drives it.
- **Acceptance criteria:** The renderer is identified by a controlled change; the RAM text is located, first by a Shift-JIS search for the `TXT-001` line, then (if absent) by equality-pattern search; whether `KANJI.BIN` is the glyph source is recorded as tested or open.
- **Notes:** Done 2026-11-02 (`EXP-0016`, D-015). Shift-JIS search found lines 4-5 once (WRAM-H `0x0606F09C`, `0x0606F0B8`, in resident `STG0AS.BIN`); no equality-pattern search needed. VDP1: 25 per-character sprites from cells at VRAM `0x1E200`; zeroing a cell blanked its character. `KANJI.BIN`: tested, layout open (`FONT-001`). For `RE-001`: write the Shift-JIS before the box types (checkpoint A).

## Gates

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `DONE`
- **Milestone:** M0
- **Dependencies:** ENV-001 to ENV-006, EMU-001 to EMU-007, EMU-020, EMU-021, DBG-001 to DBG-004, REF-008 (all `DONE` 2026-11-02).
- **Blockers:** None.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Acceptance criteria:** Every dependency is `DONE`; no unresolved workflow blocker can invalidate M1 evidence; the user's GO is recorded verbatim.
- **Notes:** Passed 2026-11-02. Asked "GATE-M0: go for the first live RAM change (RE-001)?", the user answered: "GO for M1". Open items that cannot invalidate M1 evidence: `KANJI.BIN`'s layout (`FONT-001`), cart RAM extraction (not used).

## Phase F: M1

### RE-001 - Change the target box in live RAM

- **Status:** `DONE`
- **Milestone:** M1
- **Dependencies:** GATE-M0.
- **Blockers:** None.
- **Objective:** Show that the Saturn draws the M1 box (Saturn lines 4-5, D-015) from its Shift-JIS bytes in WRAM-H, by changing them in a live session.
- **Acceptance criteria:** From checkpoint A (`local/checkpoints/m1/a-box-open.mcs`), before the box types, line 4's bytes at WRAM-H `0x0606F09C` are replaced by a same-length test string (original and new bytes recorded, written bytes read back); the completed box shows the test string and an unchanged second line, by screenshot reviewed by the agent; a no-write control replay from the same checkpoint shows the original box; source image hashes unchanged.
- **Notes:** Test string: 13 full-width hiragana (あいうえおかきくけこさしす), 26 bytes like the original, so line length and layout cannot change. Glyphs are rendered as the box types (D-015), so the write must precede the typing. Done 2026-11-02 (`EXP-0017`, D-016): read-back exact; completed box `1d501a` with the write against `ead786` in the control (as in every earlier replay); the next box (`3a956a`) the same in both; source manifests unchanged. **M1 is CONFIRMED.**

## Phase G: M2

M2: the M1 change is reproduced from an image built from the untouched
source. The order is `DISC-001`, then `DISC-002` (the M2 outcome), then
`FONT-001` and `FONT-002` (font facts that M3's layout choice needs). No
English text goes on disc in M2; the test string is the M1 hiragana.

### DISC-001 - Trace the M1 box's text to its disc file

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** RE-001 (done).
- **Blockers:** None.
- **Objective:** Find which disc file, and which offset in it, the M1 box's text (WRAM-H `0x0606F09C`, D-016) is loaded from, and how it is stored.
- **Acceptance criteria:**
  - The latest REF-005 session state before the text is in RAM, and the first one after, are found by extracting WRAM-H from the session states (validated extractor, D-006); the scene between them is described from the session screenshots.
  - From the pre-load state, a controlled trace links the bytes at `0x0606F09C` to one file: an agent write breakpoint (log mode) on `0x0606F09C`-`0x0606F0D3` records the PC, registers and frame of each write, and the loader's source (file entry, LSN or CD-buffer address) is read from those registers or the code around the PC. A no-input control replay from the same state is recorded.
  - The storage format is tested: raw or compressed; load address; whether any pointer is relocated (file offset = address − `0x06060000` predicts `0xF09C` for line 4); what the bytes that differ between the file and RAM are.
  - All three script copies (`STG0AS.BIN`, `VICTORY.BIN`, `END.BIN`) are compared with WRAM-H at the M1 checkpoints, and which one is resident there is stated with its confidence.
  - Facts, uncertainty and any copy not yet seen loaded are recorded; the source image is unchanged.
- **Notes:**
  - Already SUPPORTED, not CONFIRMED: `STG0AS.BIN` equals WRAM-H from `0x06060000` in all but about 30 bytes (EXP-0016; 29 at checkpoint B in a recheck during this write-up), while `VICTORY.BIN` and `END.BIN` differ in most bytes there. So the file is probably loaded raw, without relocation. The trace is the discriminating test.
  - If the load is by DMA (SCU or CD block), an SH-2 write breakpoint may not fire. The fallback is a break on the code that starts the load (a read of the file's directory entry or the CD block's FAD), bracketed by the two session states.
  - When `VICTORY.BIN` and `END.BIN` load is not needed for M2. Note it if seen; otherwise it stays in `docs/known_unknowns.md` for `RE-002` and `END-001`.
  - Candidates by name from `references/saturn_jp/iso_listing.json`: `STG0AS.BIN` (LSN 22,538, 320,724 bytes); the per-stage `STG00`-`STG0F.BIN` and `ST00`-`ST08_FNT.BIN` load nearby and may come with it.
- **Evidence:** `EXP-0018`, D-017, 2026-11-02.
  - **Bracket:** session states 4138 (machine select) and 4316 (the load in progress, in file order); 10 bytes differ by 4493.
  - **Trace:** 14 hits at `0x06041FB4`, a raw longword copy from the CD data register `0x25818000`; two runs identical; the control from 4493 has no hit.
  - **Source:** one Play Disc for FAD `0x58A0`, 157 sectors, which is `STG0AS.BIN`. The game's file table entry 290 and request record (file `0x124`) agree.
  - **Format:** raw, loaded at `0x06060000`, no relocation; line 4 at file offset `0xF09C`. The 10 bytes changed after the load are outside the table, and their meaning is UNKNOWN.
  - **Copies:** `STG0AS.BIN` is resident at checkpoints A, B and C. `VICTORY.BIN` and `END.BIN` were never resident at `0x06060000` in the 166 session states.

### DISC-002 - Reproduce the M1 change from a rebuilt image

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** DISC-001 (done).
- **Blockers:** None.
- **Objective:** Make the same あいう… change on a disc image built from the untouched source, and see it in the game.
- **Acceptance criteria:**
  - `tools/disc/patch_image.py` is re-validated on Cyberbots (rule 26): a rebuild with the original file is byte-identical to the source track.
  - A scripted build writes, into a new image under `build/`, the file `DISC-001` found with line 4's 26 bytes replaced by the M1 test string (same size, in place, Mode 1 EDC/ECC regenerated). Original bytes, new bytes, file offset, LSN and sector offset are recorded (rule 12).
  - Only the predicted sector(s) differ from the source, and each passes EDC/ECC. Two builds are identical; the source hashes are unchanged.
  - Unattended (agent): from the `DISC-001` pre-load session state with the rebuilt image mounted, the M1 box completes with the test string on line 1 and Saturn line 5 on line 2 (dialogue-strip hash as `EXP-0017`'s write run, `1d501a`, or an agent-reviewed screenshot). The same run with the original image is the control (`ead786`).
  - A cold boot of the rebuilt image reaches the title like the original's (run with the user present, per policy).
  - The user's cold-boot play check (Jin, story mode, first pre-fight box) shows the test string. The image-changing work stays local, with a burnable copy, until the user has tried it (hardware check before push).
- **Notes:**
  - `DISC-001` confirmed `STG0AS.BIN` raw at `0x06060000` (D-017), so line 4 is at file offset `0xF09C`. That is sector 30 of the file (LSN 22,568), bytes `0x09C`-`0x0B5`, so one sector would change. The file does hold line 4's original 26 bytes at `0xF09C` (checked during this write-up); that the game reads them from there is `DISC-001`'s question.
  - Single variable: only the file `DISC-001` names is patched. The two other byte-identical copies stay untouched in M2; whether a translation patch keeps all three equal is decided in `LAYOUT-001` or `RE-002`, from evidence of when each loads.
  - Loading a state with a different image mounted worked in XvSF (its `DISC-002`); for Cyberbots that is a HYPOTHESIS, and the control run tests it.
  - Build images under `build/` may be deleted after the task (user rule).
- **Evidence:** `EXP-0019`, D-018, 2026-11-02.
  - **Tool:** the identity rebuild is byte-identical to the source.
  - **Build:** only LSN 22,568 changed (24 user-data bytes, 130 EDC/ECC bytes); all 43,793 sectors pass; two builds identical (Track 01 `739a58e2…`); source hashes unchanged.
  - **Replay** from state 4138: the load carries the test string. The completed box is `1d501a` on the rebuilt image and `ead786` on the original, as in EXP-0017, and the screenshots match the prediction.
  - **Cold boot:** all 119 per-second frames are identical to the original's (EXP-0001).
  - **Play check:** the user declined a manual play check (2026-11-02): "Yeah, I don't want to do that at all. Why can't you just boot the machine and take regular screenshots like I did with the XvSF and MSHvSF translations?" So the agent cold-booted `build/disc/cyberbots_m2_disc002/` and played it with pad keys through System Events: arcade mode, Jin, Blodia. Jin's box shows the test string (agent-reviewed screenshot). That criterion is met in the agent's form, per that decision (`docs/localization_policy.md`).
  - **M2 is CONFIRMED** (D-018).

### FONT-001 - Find the dialogue font and prove its format

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** RE-001 (done), DISC-001 (done).
- **Blockers:** None. Session state 4138 (EXP-0018) is a pre-load state to reuse.
- **Objective:** Find the glyph data behind the dialogue's Shift-JIS codes (in RAM and on disc) and the routine that renders it into the glyph cells, and prove the font's format.
- **Acceptance criteria:**
  - From checkpoint A, an agent write breakpoint (log mode) on the WRAM-H glyph shadow (`0x060FE200`-`0x060FE27F`, cell 0, D-015) as the box types records the writing PC; the routine is disassembled far enough to name its inputs (the Shift-JIS code, the source pointer) and its output.
  - The font's RAM location is found from that routine, and its disc source by a controlled test: a read correlation with a file, then a probe image that changes one glyph's bytes, with the original image as control.
  - The format is stated (bit depth, cell size, any compression or rendering step that makes the anti-aliased 4 bpp cells, and the code-to-index mapping). It is proven by a byte-identical repack of the original data, and by decoding the 25 glyphs of the M1 box and matching them to the rendered cells (25/25).
  - Facts and uncertainty are recorded; the source image is unchanged.
- **Notes:**
  - `KANJI.BIN` (163,840 bytes) has the cells' value palette but not the glyph in the layouts tried (EXP-0016). A recheck during this write-up found none of cell 0's non-blank 8-byte rows, raw, in any of the 264 data-track files. So the font is probably stored in another form (another bit depth, compressed, or rendered from an outline); a lead, not a fact.
  - Candidates by name: `KANJI.BIN`, `FIX.BIN`, `ST00`-`ST08_FNT.BIN` (per-stage, 318-418 KB).
  - The half-width and Latin questions are `FONT-002`'s, not this task's.
- **Evidence:** `EXP-0020`, D-019, 2026-11-02.
  - **Routine:** `0x06011224` copies four VDP2 tiles (from `0x25E00000` + index × 32) into the WRAM-H cell. Its caller `0x0606E7BC` maps each two-byte code through the 1,222-entry table at `0x060AAD7C` (`STG0AS.BIN` `0x4AD7C`).
  - **Disc:** `KANJI.BIN`, read as each box scene starts (Play Disc FAD `0x1342`, 80 sectors) by the raw CD loader to VDP2 VRAM `0x40000`. A probe image with glyph 600 replaced shows that character as a block; the original image is the control.
  - **Format:** 1,280 glyphs of 16×16 at 4 bpp, 2×2 VDP2 tiles each; byte-identical repack (`tools/font/kanji.py`).
  - **Mapping:** 25/25 tile indices predicted, and 25/25 decoded glyphs equal the rendered cells (WRAM-H and VDP1).

### GATE-TRANSLATION - Confirm reference and translation prerequisites

- **Status:** `BLOCKED`
- **Milestone:** M2
- **Dependencies:** DOC-002, REF-001, REF-003 to REF-007 (REF-002 rejected).
- **Blockers:** Dependencies not done.
- **Objective:** No English text goes on disc before the oracle, the pairing method, and the user's policy are settled.
- **Acceptance criteria:** Every dependency is `DONE`; the user gives a recorded GO. Each later scope extension (new pilot, endings, names) is its own dated block under this gate.

## Later Milestones (outline only)

Placeholders so the order is visible. Each becomes a full task, with its own
acceptance criteria, only when its prerequisites are done ("Write up the Mx
tasks" just in time). The method for each is in `docs/playbook_from_mshvsf.md`
and `docs/lessons_from_xvsf.md`.

| ID | Milestone | Outline |
| --- | --- | --- |
| FONT-002 | M2 | **First**, probe the renderer for a leftover arcade English path (language/region branches, half-width or ASCII handling); then measure Latin glyphs, line length and box size. From D-019: text is two bytes per glyph (`0x0A` a line break, SUPPORTED); the font already has full-width A-Z and 0-9 but no lower case; there are 58 free glyph slots and 26 free table slots; pair glyphs (`Dr`, `!?`) show two half-width characters per cell. |
| LAYOUT-001 | M3 | Choose a capacity route (native English path, half-width or variable-width glyphs, pair glyphs, longer strings with relocated pointers) from measured headroom; user decision. The arcade English record for a slot runs up to 4 lines of 38 characters, the Saturn's line up to 16 full-width cells (D-008, D-009). |
| RE-002 | M3 | Selection: what picks each line (pilot, opponent, route, branch), and forcing it from a checkpoint. Start from the record structures that point at the lines (D-008). |
| RE-003 | M3 | Script compiler for one pilot; every line verified live by forcing. |
| RE-004 | M4 | A second pilot through the same mechanism. |
| RE-005 | M5 | Census of every pilot's dialogue against the arcade; roster and exceptions (user decision); capacity; roster image; regression references. |
| END-001 | M6 | Reach, renderer, RAM, disc source (the `*_END*` entries and `KEND*.BIN` are candidates), arcade English (not yet seen; the second table reader at `0x97222` is a candidate, D-010), and indexing of one ending. |
| END-002 | M7 | One ending localized. |
| END-003 | M8 | All roster endings; combined image; coverage register (`docs/coverage_exceptions.md`). |
| UI-004 | after M5, early | Boot, cartridge and save warnings (`WARNING0-4.PIX` are candidates); in the first backlog this time (`docs/lessons_from_xvsf.md`, lesson 5). |
| UI-001 | after M8, user request | UI art: inventory English art already in every font before drawing anything. |
| UI-002 | after M8, user request | Attract and opening text (`OPDEMO*`, `STDEM*.PIR`, `VADEM*.MAC`, `STDEMO.*` are candidates): layer, container, codecs, oracles. |
| UI-003 | after M8, user request | Other UI text (select, continue, ranking, options): find the arcade English by tracing the arcade code. |
| TXT-002 | after M8, user request | Rare, random, or region-gated text: trace every reader of every text table. |
| LOC-001 | after REF-007 | Name art only (D-013): find the pilot-select and VS-screen name sprites' table (VS draw code, `SELECT.VAD`), check whether Latin name art is on the disc, otherwise model it on the US arcade's; census the difference between the two variants early (XvSF: 243 bytes; MSHvSF: 58 KB of font). Voices: check whether names are spoken. |
| OPT-001 | after LOC-001, user decision 2026-11-02 | An Options-screen switch for the name art, Latin by default, in an expanded Options screen if needed. Model: MSHvSF `OPT-003` (a proven home for new code), `OPT-004` (EXTRA OPTIONS sub-menu), `OPT-005` (names switch); XvSF `LOC-009`/`LOC-010`. Prove free RAM by read/write logs before placing code (XvSF's first toggle hung the title). |
| SPECIAL-001 | M9, user approval | Boss and hidden pilots, alternate routes, unlocks. Secondary sources (`docs/references.md`) say the console ports add four pilots (Chiyomaru Kagura, Tessan Hagure, Princess Devilotte, SHADE) with no arcade English, and an Akuma-mech code; their lines need recorded new translations under the user's policy. Size: Saturn lines 899-1850 (952 lines, about half the script) have no arcade counterpart (D-011), plus 74 shorter Saturn-only lines among the arcade pilots' stories. |
| REL-001 | after M5 | Copy XvSF `make_patch`/`make_ssp` (with the RetroAchievements header guard) and parameterize the source folder, manifest and author; xdelta and SSP; release zips via promoted `make_zips`/`check_zips`. Patches are Release assets only, never committed. |
