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
- Next unblocked tasks: `EMU-020` (record why stock is insufficient;
  offline), then `EMU-021` (build the agent interface, validate V1-V4 with
  the user present); offline: `REF-001`, `TXT-001`, `DOC-003`
  (finish: boot the US set), `TXT-001` (offline census of the Shift-JIS
  script blocks), `DOC-003` (reference catalog), `ENV-007` (retry Redump).
- Confirmed so far: D-001 (boot), D-002 (audio-track layout), D-003 (no cart
  needed for boot and attract), D-004 (screenshots and states by hotkey),
  D-005 (stock debugger dumps, writes, breakpoints), D-006 (state extractor
  valid for work RAM and VRAM). Nothing about
  the text, font or renderer is confirmed.

## Milestones

Cyberbots' Japanese text is mostly pilot story dialogue between fights, not
win quotes, so the sibling milestones are re-anchored on dialogue lines. The
exact unit ("line", "box", "exchange") is fixed by `REF-008` from evidence.

| ID | Required outcome |
| --- | --- |
| M0 | Mednafen runs; Cyberbots boots with the right cartridge setting; pad, screenshots, save states, debugger, agent interface, validated extraction, documentation, and Python tooling work. |
| M1 | One ordinary pilot's story dialogue line is visibly modified in live Saturn RAM. |
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

- **Status:** `BLOCKED`
- **Milestone:** M0 (do early; XvSF did this the day before release)
- **Dependencies:** ENV-006.
- **Blockers:** `redump.org` refused the connection on 2026-11-02 (`ECONNREFUSED` from the web fetcher). Retry in the built-in browser, as XvSF did.
- **Objective:** Raise the image identity from **SUPPORTED** to **CONFIRMED**, and learn what "(2M)" in the Redump name distinguishes.
- **Acceptance criteria:** Track hashes match a named database entry (size, CRC-32, MD5, SHA-1 per track), or a mismatch is recorded with its consequence; any other Redump entries for this title are listed with how their track 01 differs.
- **Notes:** The release patch must name the exact image it applies to either way.

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

- **Status:** `READY`
- **Milestone:** M0 (do early)
- **Dependencies:** DOC-001.
- **Blockers:** None.
- **Objective:** Reuse the sibling platform references and list Cyberbots-specific prior art.
- **Acceptance criteria:** `docs/references.md` lists the platform references (Saturn, SH-2, CD/ISO 9660, Mednafen, CPS-II, MAME) with their sibling source, and separately any Cyberbots prior art: translation projects, text dumps, script comparisons, official English releases.
- **Notes:** 2026-11-02 quick web search found no Saturn English patch for Cyberbots. Candidates to read: the Lost In Translation page on Cyberbots (exotica.org.uk) for regional text differences; Capcom Fighting Collection (2022) as a modern official English release of the arcade game (not supplied; reference only).

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

- **Status:** `READY`
- **Milestone:** M0
- **Dependencies:** EMU-007, DOC-002.
- **Blockers:** None.
- **Objective:** Satisfy `AGENTS.md` rule 16 before using the patched build.
- **Acceptance criteria:** A short record cites MSHvSF `EMU-012`/`EMU-020` and XvSF `EMU-020` and confirms the same limits apply here; the user's `DOC-002` answer on reusing the patch is cited.
- **Notes:** `DOC-002` answer (2026-11-02): "Yes, reuse it (Recommended)".

### EMU-021 - Build and validate the agent interface

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** EMU-020.
- **Blockers:** EMU-020.
- **Objective:** Drive Mednafen from Python so the user only plays.
- **Acceptance criteria:** `vendor/mednafen/patches/0001-agent-interface.patch` (`c30146ef…5244`) applies to the pinned version and builds; validations V1-V4 (`docs/mednafen_agent_interface.md`) pass on Cyberbots states; `tools/mednafen/agent.py` tests pass.

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

- **Status:** `IN_PROGRESS`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** ENV-002.
- **Blockers:** None.
- **Objective:** Identify every arcade zip and key against a pinned MAME, and boot the sets needed for capture.
- **Acceptance criteria:** Each file is hashed and matched to a MAME set name; the pinned MAME version and driver source are recorded; the US set boots headless.
- **Notes:** 2026-11-02 (`references/arcade/README.md`): all five supplied zips hashed; with `qsound.zip` added, all five verify in MAME 0.289 (`cybots` Europe 950424, `cybotsu` USA 950424, `cybotsj` Japan 950420, `cybotsud` and `cybotsjd` decrypted bootlegs). Remaining: pin the `capcom/cps2.cpp` source (as the siblings' `local/mame_src/`) and run `tools.reference.mame_audit` against it; boot `cybotsu` headless with the user present.

### REF-002 - Intake a PlayStation image (optional)

- **Status:** `REJECTED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** DOC-002.
- **Blockers:** None.
- **Objective:** Decide whether a PS1 release adds a reference.
- **Acceptance criteria:** Either every component is hashed with an identity status, or the task is `REJECTED` with the user's reason.
- **Notes:** Rejected 2026-11-02 by the user's `DOC-002` answer "No, arcade only (Recommended)": the PS1 release is Japanese-only and adds no official English.

### REF-003 - Locate and decode the arcade English text

- **Status:** `BLOCKED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-001.
- **Blockers:** REF-001.
- **Objective:** Find where the arcade stores its English story dialogue, win quotes (if any) and ending text, and how it is encoded.
- **Acceptance criteria:** A decoder reproduces known English strings from the local ROM; the table shape, pointer tables and regional differences are recorded; punctuation mappings are tested statistically.
- **Notes:** The decrypted program image (`cybotsud`: `cybu_d.03` + `cybu_d.04`, word-swapped) holds only a few ASCII strings (region names, RAM test, `WON LOST CONTINUE ENDING`). The dialogue is therefore in another encoding or in another ROM; XvSF found its English with an offset histogram of common words, MSHvSF as 16-bit codes. Trace the arcade's readers (`mame_timeline.lua` `logreads`), do not stop at a data search.

### REF-004 - Confirm the decoded arcade text on screen

- **Status:** `BLOCKED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-003.
- **Blockers:** REF-003.
- **Objective:** Show that the decoded table is what the arcade draws.
- **Acceptance criteria:** A scripted MAME route shows a predicted entry on screen, with the RAM pointer that selects it.

### REF-005 - Inventory the Saturn text surfaces

- **Status:** `BLOCKED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** EMU-021.
- **Blockers:** EMU-021.
- **Objective:** List every place the Saturn release shows Japanese text.
- **Acceptance criteria:** `docs/text_surfaces.md` holds a table of surfaces (screen, when shown, sample screenshot path and hash, whether the arcade has English for it) from screenshots the agent reviewed, built from several captures: a cold boot left on the attract loop (sampled at least every frame of the shortest event), boot without cart and with a corrupt save (`UI-004`), one story run through at least two fights with a continue, options and other menus.
- **Notes:** XvSF's single session missed five surfaces (`docs/lessons_from_xvsf.md`, lesson 6). Keep every state (`--keep-states 0`).

### REF-006 - Compare the Saturn script with the arcade script

- **Status:** `BLOCKED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** TXT-001, REF-003.
- **Blockers:** REF-003.
- **Objective:** Decide whether the Saturn dialogue is the arcade Japanese dialogue unchanged, and so whether the arcade English is a line-for-line oracle.
- **Acceptance criteria:** Per pilot and route, the Saturn lines (from `TXT-001`) are compared with the arcade Japanese lines; Saturn-only and arcade-only lines are listed.

### REF-007 - Inventory pilot and mech names across releases

- **Status:** `BLOCKED`
- **Milestone:** GATE-TRANSLATION
- **Dependencies:** REF-004, REF-005.
- **Blockers:** REF-005.
- **Objective:** List every pilot and VA (mech) name the Saturn shows as art or text or speaks, and where the arcade English differs.
- **Acceptance criteria:** A name table with sources; whether both conventions' assets are already on the disc; options and costs presented to the user; the toggle question decided right after (`docs/lessons_from_xvsf.md`, lesson 9).

### REF-008 - Choose the first pilot and line

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** REF-005, TXT-001.
- **Blockers:** REF-005.
- **Objective:** Pick one ordinary pilot and one dialogue line as the M1 target, and fix the milestone unit (line, box, or exchange).
- **Acceptance criteria:** The choice and reason are recorded; the Japanese is captured on screen, transcribed, and matched to its `TXT-001` record; a checkpoint shortly before the line exists.

## Phase E: Text, Checkpoints And Memory Analysis

### TXT-001 - Offline census of the plain Shift-JIS script blocks

- **Status:** `READY`
- **Milestone:** M1 (static analysis only; no image change)
- **Dependencies:** ENV-003.
- **Blockers:** None.
- **Objective:** Describe the Shift-JIS dialogue found in `END.BIN`, `VICTORY.BIN` and `STG0AS.BIN` (SESSION-0001) without assuming it is what the game draws.
- **Acceptance criteria:** A script (`tools/text/`) lists every string in each file with its offset, byte length, terminator and the bytes around it; the three copies are compared (identical or not, and where each block starts and ends, e.g. the `SsCB` marker seen before it); any pointer or index table that addresses the strings is located; control bytes (line breaks, speaker, waits, name placeholders) are tabulated with counts; every other data-track file is scanned the same way and the results recorded. Committed output: offsets, lengths, hashes and counts only, no game text (`AGENTS.md` rule 21).
- **Notes:** Use `tools/text/search.py` for the scan. Whether the game reads these bytes as Shift-JIS at runtime, and which copy it reads when, are **runtime questions** for `DBG-004` and `DISC-001`.

### DBG-002 - Observe dialogue selection behaviour

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** EMU-021, REF-008.
- **Blockers:** EMU-021.
- **Objective:** Learn whether the dialogue shown from one checkpoint is fixed or varies, before planning checkpoints.
- **Acceptance criteria:** Several replays of one pre-dialogue state, with the lines shown recorded.

### DBG-003 - Capture dialogue checkpoints

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** DBG-002.
- **Blockers:** DBG-002.
- **Objective:** States and screenshots before the dialogue starts, with the target line visible, and after it is gone.
- **Acceptance criteria:** Each checkpoint is reproducible from its state and named in an experiment record.

### DBG-004 - Find the dialogue renderer and its RAM text

- **Status:** `BLOCKED`
- **Milestone:** M1
- **Dependencies:** DBG-001, DBG-003.
- **Blockers:** DBG-003.
- **Objective:** Determine whether the dialogue is VDP1 sprites or VDP2 tiles, and find the RAM text that drives it.
- **Acceptance criteria:** The renderer is identified by a controlled change; the RAM text is located, first by a Shift-JIS search for the `TXT-001` line, then (if absent) by equality-pattern search; whether `KANJI.BIN` is the glyph source is recorded as tested or open.

## Gates

### GATE-M0 - Confirm environment and checkpoint prerequisites

- **Status:** `BLOCKED`
- **Milestone:** M0
- **Dependencies:** ENV-001 to ENV-006, EMU-001 to EMU-007, EMU-020, EMU-021, DBG-001 to DBG-004, REF-008.
- **Blockers:** Dependencies not done.
- **Objective:** Make an explicit go/no-go decision before the first live RAM mutation.
- **Acceptance criteria:** Every dependency is `DONE`; no unresolved workflow blocker can invalidate M1 evidence; the user's GO is recorded verbatim.

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
| RE-001 | M1 | Change the chosen line in live RAM, with a no-write control. |
| DISC-001 | M2 | Trace the RAM text to its disc file by a write breakpoint from a pre-load checkpoint; identify the format; learn when each of `END.BIN`, `VICTORY.BIN`, `STG0AS.BIN` is loaded and whether the copies must stay identical. |
| DISC-002 | M2 | Reproduce the M1 change from a rebuilt image (same-size, in place, EDC/ECC regenerated with `tools/disc/patch_image.py`); cold boot. |
| FONT-001 | M2 | Find the glyph routine and font (`KANJI.BIN` and `FIX.BIN` are candidates); prove the format by a byte-identical repack. |
| FONT-002 | M2 | **First**, probe the renderer for a leftover arcade English path (language/region branches, half-width or ASCII handling); then measure Latin glyphs, line length and box size. |
| LAYOUT-001 | M3 | Choose a capacity route (native English path, half-width or variable-width glyphs, pair glyphs, longer strings with relocated pointers) from measured headroom; user decision. |
| RE-002 | M3 | Selection: what picks each line (pilot, opponent, route, branch), and forcing it from a checkpoint. |
| RE-003 | M3 | Script compiler for one pilot; every line verified live by forcing. |
| RE-004 | M4 | A second pilot through the same mechanism. |
| RE-005 | M5 | Census of every pilot's dialogue against the arcade; roster and exceptions (user decision); capacity; roster image; regression references. |
| END-001 | M6 | Reach, renderer, RAM, disc source (the `*_END*` entries and `KEND*.BIN` are candidates), arcade English, and indexing of one ending. |
| END-002 | M7 | One ending localized. |
| END-003 | M8 | All roster endings; combined image; coverage register (`docs/coverage_exceptions.md`). |
| UI-004 | after M5, early | Boot, cartridge and save warnings (`WARNING0-4.PIX` are candidates); in the first backlog this time (`docs/lessons_from_xvsf.md`, lesson 5). |
| UI-001 | after M8, user request | UI art: inventory English art already in every font before drawing anything. |
| UI-002 | after M8, user request | Attract and opening text (`OPDEMO*`, `STDEM*.PIR`, `VADEM*.MAC`, `STDEMO.*` are candidates): layer, container, codecs, oracles. |
| UI-003 | after M8, user request | Other UI text (select, continue, ranking, options): find the arcade English by tracing the arcade code. |
| TXT-002 | after M8, user request | Rare, random, or region-gated text: trace every reader of every text table. |
| LOC-001 | after REF-007 | Both variants, US default (`DOC-002`); whether both conventions' art and voice are already on the disc; two images or an Options toggle decided right after the census. |
| SPECIAL-001 | M9, user approval | Boss and hidden pilots, alternate routes, unlocks. |
| REL-001 | after M5 | Copy XvSF `make_patch`/`make_ssp` (with the RetroAchievements header guard) and parameterize the source folder, manifest and author; xdelta and SSP; release zips via promoted `make_zips`/`check_zips`. Patches are Release assets only, never committed. |
