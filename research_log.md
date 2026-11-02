# Research Log

This chronological journal preserves both successful and failed work. Durable,
confirmed findings are separately summarized in `docs/discoveries.md`.

## Entry Template

```markdown
## YYYY-MM-DD HH:MM TZ — EXP-NNNN or SESSION-NNNN

Task: TASK-ID

Goal:

Observation:

Hypothesis:

Action:

Result:

Conclusion:

Next action:
```

## 2026-11-02 — SESSION-0001: repository set up

Task: ENV-001 to ENV-006, DOC-001, REF-001 (partial)

Goal: create the repository from the two sibling projects' method (MSHvSF and
XvSF, both released 0.1.0), read their task lists and research logs for
lessons, and record the source images before any research.

User request (2026-11-02, verbatim excerpt): "I would like to set up this
repository to produce an English translation of the Sega Saturn game
Cyberbots. I want to follow the pattern set up in the
`msh_vs_sf_saturn_en_translation` and `xmen_vs_sf_saturn_en_translation`
directories. In addition, I would like you to go through their `TASKS.md`
list and their research logs to set us up for success."

Action:

- Rules: `AGENTS.md` adapted from XvSF. Rule 13 now names both siblings; rule
  16 carries the XvSF patch-reuse decision, to be confirmed in `DOC-002`; rules
  23 and 24 re-anchor on story dialogue and Cyberbots' own special cases; rule
  25 protects both sibling repositories; rule 26 (provenance) kept.
- Scaffolding copied from XvSF commit `a1c82ba`: `pyproject.toml` (renamed),
  `setup_venv.sh`, `invenv.sh`, `.gitignore`, `LICENSE`,
  `docs/research_protocol.md`, `research/README.md`,
  `research/experiments/README.md`, `vendor/mednafen/README.md` (paths
  changed to Cyberbots) and the agent-interface patch (SHA-256
  `c30146ef…5244`, identical to MSHvSF's). From MSHvSF `be1e18e`:
  `research/artifact_manifest.schema.json` (schema ID renamed) and
  `docs/mednafen_agent_interface.md` (with a header note).
- Method documents: `docs/playbook_from_mshvsf.md` is MSHvSF
  `docs/playbook_cross_game.md` at `447e573` with a header note.
  `docs/lessons_from_xvsf.md` is new: XvSF never wrote its own playbook, so
  two read-only subagents read both repositories' `TASKS.md`, research logs,
  discoveries and tools, and the digest records what transferred, what did
  not, process lessons, and which tool copy to use.
- `local_agent_guidance.md` (ignored): the user preferences from both
  projects, including four XvSF rules that were kept only in that project's
  agent memory and would otherwise have been lost (emulator consent, progress
  estimates, regression scope, deleting finished `build/` images), plus
  MSHvSF's hardware-check-before-push rule.
- Tools (`ENV-003`): the game-independent tools and their tests were copied
  from XvSF `a1c82ba` with a provenance note appended to each docstring
  (`TASKS.md` `ENV-003` lists them). XvSF-format tools (`prs`, `font`,
  `font_pack`, `route`) were copied first, then removed, because they encode
  XvSF facts. This departs from XvSF's "copy when first needed" habit; the
  safeguard is that no copied tool's output counts as Cyberbots evidence until
  the task using it re-validates it (`AGENTS.md` rule 26).
- Checks: `./setup_venv.sh` (uv 0.11.7); `./invenv.sh pytest -q` 119 passed;
  `ruff check .` and `ruff format --check .` clean; `mypy` (strict) no issues
  in the copied files.

Source image (`ENV-006`):

- `~/Downloads/cyberbots/saturn_cue_bin/` (63 files) copied with `cp -c` into
  the new ignored folder `local/disc_images/cyberbots_saturn_jp_2m/`.
- Hashed with `tools.disc.hash_source --json` (log: ignored
  `local/logs/env002-hashes.json`); CUE and track 01 rechecked with
  `shasum -a 256`. Table in `references/saturn_jp/README.md`.
- `ENV-007`: `WebFetch` of `http://redump.org/discs/system/ss/quicksearch/cyberbots/`
  failed with `connect ECONNREFUSED 62.141.35.244:443`. Not retried; the task
  is `BLOCKED` until a retry in the built-in browser.

Arcade sets (`REF-001`, partial):

- Five zips copied to the ignored `local/arcade/`. `mame -verifyroms` (MAME
  0.289) first failed on every set: `dl-1425.bin ... NOT FOUND (qsound_hle)`.
  With `qsound.zip` copied from `~/Downloads/mshvsf/` (SHA-256 equal to
  MSHvSF's copy), all five sets verify. `references/arcade/README.md`.

First look at the disc (static, no emulator; every item **HYPOTHESIS** or
plain observation):

- **Header.** `T-1217G V1.002 19970219`, area `J`, peripherals `JW`. The
  meaning of `W` and of "(2M)" in the Redump name, and therefore the cart
  requirement, are open (`EMU-004`, `ENV-007`).
- **ISO 9660** (`tools.disc.iso9660 --check`, log ignored
  `local/logs/env004-iso.txt`): track 01 is clean; 325 entries, no
  directories; 61 entries point past track 01 and match CD-DA track
  positions (`references/saturn_jp/README.md`). 264 files extracted to the
  ignored `local/extracted/saturn_jp/` (`--extract`).
- **File families by name** (names only; contents unknown): `M2PL*`/`M3PL*`
  and `M2CB*`/`M3CB*` (per-slot pairs, numbered `00`-`10` hex), `ST00`-`ST0A`
  `_FNT`/`_SPR`, `STG00`-`STG0F`, `SCR*.PIX`, `WARNING0`-`4.PIX`,
  `KANJI.BIN` (163,840 bytes; 5,120 × 32 bytes would fit 16×16 1-bit glyphs —
  arithmetic only), `FIX.BIN`, `CYBER.BIN` and `0.BIN` (SH-2 code by their
  byte patterns), `STDEMO.*`, `STDEM*.PIR`, `VADEM*.MAC`, `OPDEMO*`, `END.BIN`,
  `KEND*.BIN`, `VICTORY.BIN`, `CONTI_0.BIN`, `SEL00.BIN`.
- **Plain Shift-JIS dialogue.** A scan for runs of two-byte Shift-JIS
  characters containing kana (scratch script, not committed) found about
  1,763 strings and about 23,000 characters in each of `END.BIN`,
  `VICTORY.BIN` and `STG0AS.BIN`. The first strings are the same story text
  (a pilot's motive for entering the "VA battle", then pre-fight lines) at
  offsets `0x0AECC`, `0x01CE8` and `0x0F01C` respectively, each preceded by an
  ASCII `SsCB` marker. The character counts differ slightly (22,927, 22,926,
  22,925), so the three copies may not be identical. A stricter rescan of
  all 264 files (runs of 4+ characters, at least 3 kana) found Japanese
  sentences only in these three files (1,692 strings, 20,680 characters
  each) and in `CYB_ABS.TXT`, the ISO 9660 abstract file (11 lines, a product
  description, presumably never shown in game). `CYBER.BIN` and `0.BIN` hold
  only Shift-JIS punctuation and iteration-mark tables; the `*_FNT.BIN`,
  `*.LF`, `LOGO.CPK` and `SE.DAT` hits are binary data that happens to decode.
  So menus, warnings, story demos and endings, if they show Japanese, store it
  in another form (graphics, or another encoding).
- **Arcade program.** The decrypted US program image has only a few ASCII
  strings (`references/arcade/README.md`); the arcade's English dialogue is
  in another encoding or location.

Hypotheses this raises (to test, not to assume):

1. The story dialogue is drawn from these Shift-JIS strings directly, with
   glyphs from `KANJI.BIN`. If so, the M1 RAM search is a plain Shift-JIS
   search, and the sibling equality-pattern search is the fallback, not the
   first tool. (Both siblings' quote text was **not** Shift-JIS in RAM.)
2. Each of the three files is a program overlay for a different game phase
   (stage, victory, ending) that carries its own copy of the script, so a
   patch must change every copy the game reads. `DISC-001` must learn which
   copy is read when.
3. Cyberbots is one engine generation older than the two Vs. games, so
   nothing about their formats should be expected here.

Translation scope implication: about 23,000 Japanese characters of story
dialogue is far more text than either sibling's win quotes, but if it is
plain Shift-JIS addressed by pointers, relocation may be possible and the
font route may be the main difficulty. Recorded as context for `LAYOUT-001`,
not as a plan.

Web search (2026-11-02): no Saturn English patch for Cyberbots was found;
prior-art candidates are listed in `TASKS.md` `DOC-003`.

Conclusion: Phase A is done except `ENV-007`. Nothing about Cyberbots'
internals is confirmed.

Next action: `DOC-002` (put the carried-over decisions to the user),
`EMU-001` (Mednafen 1.32.1, reusing the XvSF archive after a hash check),
`TXT-001` (offline census of the script blocks), finish `REF-001`.

## 2026-11-02 — SESSION-0002: carried-over decisions confirmed

Task: DOC-002

Goal: confirm, change or defer each sibling user decision for Cyberbots.

Action: three rounds of multiple-choice questions, each option describing the
MSHvSF and XvSF precedent, with a "(Recommended)" option. Evidence-dependent
decisions (pairing unit, capacity route, dialogue layout, roster and
exceptions, ending layout, name-variant delivery, caption and UI style) were
not asked; `docs/localization_policy.md` "Deferred To Evidence" names the
task that will ask each.

Result (the user's chosen options, verbatim):

- English source: "Official; fixes opt-in (Recommended)".
- Text with no official English: "Recorded new translation (Recommended)".
- Pilot and VA mech names: "Both variants, US default".
- Eventual scope: "Boss & hidden pilots", "Menus, UI art & warnings",
  "Attract & opening demos", "Rare & region-gated text".
- Release formats: "xdelta + SSP (Recommended)".
- Release timing: "After open tasks (Recommended)".
- Patched Mednafen reuse: "Yes, reuse it (Recommended)".
- Workflow: "Play check closes tasks", "Silent unattended runs", "Ask before
  downloads/installs", "Hardware check before push".
- PlayStation reference: "No, arcade only (Recommended)".
- XvSF standing rules: "No cold boots without me", "Time estimates on jobs",
  "Rebuild only new references", "Delete finished build images".

Note on names: the user chose two variants from the start, unlike the
recommended "US names, variants only if the census finds differences". Both
siblings ended with US names by default; MSHvSF shipped two images and XvSF
an Options toggle only. How Cyberbots delivers its two variants waits for the
`REF-007` name census (`docs/lessons_from_xvsf.md`, lesson 9).

Conclusion: recorded in `docs/localization_policy.md`; `AGENTS.md` rules 16
and 21 cite the answers; `local_agent_guidance.md` notes the confirmed rules;
`DOC-002` is `DONE`; `REF-002` is `REJECTED` by the user's answer. Scope
answers do not lift any gate: special surfaces still wait for M9 and their own
tasks (rule 24).

Next action: `EMU-001` (Mednafen 1.32.1; copy XvSF's archive after a hash
check, so no download), `REF-001` (pin `cps2.cpp`, boot `cybotsu`),
`TXT-001`, `DOC-003`, `ENV-007`.

## 2026-11-02 — SESSION-0003: stock Mednafen built

Task: EMU-001

Goal: a pinned stock Mednafen build under ignored `vendor/`, recorded well
enough to reproduce.

Action:

- Copied XvSF's `local/downloads/mednafen-1.32.1/mednafen-1.32.1.tar.xz`
  (`cp -c`) instead of downloading. Size 3,571,236 bytes and SHA-256
  `de7eb94a…3832`, equal to both siblings' records.
- `bsdtar -tf` (one top folder, `mednafen/`), extracted into an empty scratch
  folder under `local/`, moved to `vendor/mednafen/src/`.
- Configured and built in `vendor/mednafen/build/` with the siblings' exact
  commands (`docs/mednafen.md`). Configure 30 s, `make -j12` 2 min 46 s, both
  exit 0.
- Ran `-help` with `MEDNAFEN_HOME=local/mednafen` (no disc loaded).

Result:

- Binary SHA-256 `077ac658c8e773bca58508cf7bacc4f180a6bf492419bfe0b8ddf3e7415d669f`,
  21,327,272 bytes; differs from XvSF's (`892bb60a…29dd`), as expected across
  host builds (macOS 26.7.2 here, 26.7.1 there).
- `-help`: "Starting Mednafen 1.32.1", the `ss` module listed, exit 255 (same
  as both siblings). A default `local/mednafen/mednafen.cfg` was created.
- Static lead for `EMU-004`: `src/ss/db.cpp` line 102 lists `T-1217G`
  "Cyberbots (Japan)" as `CART_EXTRAM_1M`, without the "Game requirement."
  note that XvSF's 4 MiB entry carries. This is a **HYPOTHESIS** source for
  the cart question, not evidence of what the game needs.

Conclusion: `EMU-001` is `DONE`; `EMU-002` is `READY`.

Next action: `EMU-002` (pin the interactive and quiet homes with
`tools/mednafen/home.py`; copy the Japanese BIOS `sega_101.bin` from a
sibling's `local/mednafen/firmware/` and record its hash).

## 2026-11-02 — SESSION-0004: project-local Mednafen homes

Task: EMU-002

Goal: run Mednafen only with configuration and BIOS local to this checkout.

Action:

- BIOS: `sega_101.bin` and `mpr-17933.bin` copied with `cp -p` from XvSF
  `local/mednafen/firmware/` into `local/mednafen/firmware/`; `cmp` clean.
  SHA-256 `dcfef4b9…deac` and `96e106f7…266f`, each equal to the hash
  Mednafen 1.32.1's `Documentation/ss.html` lists for that filename.
- `./invenv.sh python -m tools.mednafen.home`, twice. First run: interactive
  `no change` (every pinned value is a default), quiet home created with three
  settings changed. Second run: `no change` for both.
- `-help` with each home (no disc loaded): each reports its own base
  directory and `Loaded 7904 valid settings and 0 unknown settings`; both
  config hashes unchanged afterwards.

Result: config SHA-256 `48a7cf6b…28fc` (interactive, 652,752 bytes) and
`ef897288…5019` (quiet, 652,750 bytes); `diff` shows only the three quiet
settings. Both equal XvSF's pinned files, so the generated default holds no
host- or game-specific content. `tools/mednafen/home.py` behaved as on XvSF;
its role here is pinning, so this run is its re-validation on Cyberbots.

Conclusion: `EMU-002` is `DONE`. `EMU-003` is `READY` but waits for the user
to be present (standing rule "No cold boots without me").

Next action: `EMU-003` with the user present (three silent cold boots of the
untouched image to the title with `tools/mednafen/cold_boot.py`); meanwhile
offline tasks `TXT-001`, `DOC-003`, `REF-001` (pin `cps2.cpp`).

## 2026-11-02 — EXP-0001: unattended cold boots to the title

Task: EMU-003

Goal: show that stock Mednafen boots the untouched image, the same way each
time, before any further emulator work.

Observation: `EMU-002` homes and BIOS in place; the game had never run.

Hypothesis: with the silent home and no input, three cold boots reach a stable
title screen within 120 s, log `T-1217G`, and leave the source unchanged.

Action: with the user present ("Yes, boot it now"), a 20 s pilot, then three
120 s boots with `tools/mednafen/cold_boot.py`, emptying `sav/` before each;
source hashed before and after (`research/experiments/EXP-0001/README.md`).
Started 13:53:58 local time, finished 14:01:18 (2 min 15 s per boot).

Result: all exit 0; `SGID: T-1217G`, `SGNAME: CYBER BOTS`, `SGAREA: J`,
`Cart: 1MiB Extended RAM`; 119 of 119 frames byte-identical across boots;
title logo from frame 058, `PRESS START BUTTON` on 062-067; source, binary
and configs unchanged. No Japanese text in boot or attract apart from
background signage in the demo stage. Mednafen's table of contents matches
every out-of-track ISO entry to exactly one audio track (D-002).

Conclusion: **CONFIRMED** (D-001, D-002). `cold_boot.py` is re-validated on
Cyberbots. `EMU-003` `DONE`; `EMU-004`, `EMU-005`, `EMU-006` `READY`, all
needing the user present.

Next action: `EMU-004` cart controls (`ss.cart none`, `extram1`, `extram4`)
with `cold_boot.py --setting`, then `tools.mednafen.home` to restore the
config; `EMU-005` with the user's controller.

## 2026-11-02 — EXP-0002: cartridge controls

Task: EMU-004

Goal: find which cart setting the game needs, with controls.

Hypothesis: the cart changes nothing the game shows in a no-input boot and
attract run; `extram1` reproduces D-001 exactly.

Action: with the user present ("Yes, run EMU-004"), one 120 s cold boot each
with `ss.cart` `extram1`, `none`, `backup` and `extram4` (`backup`, a 512 KiB
save cart, added as a common real-hardware setup), restoring the config with
`tools.mednafen.home` after each. 14:04:32-14:13:32 local time.

Result: all exit 0, no warning screen in any. `extram1` and `extram4`: 119 of
119 frames equal to D-001. `none`: equal up to frame 087, then the attract
fight about 1 s earlier. `backup`: same sequence with ~1 s shifts in the intro
and title text (title frames 058 and 064 still equal). Config restored to
`ef897288…5019` every time; source unchanged.

Conclusion: **CONFIRMED for boot and attract** (D-003). Unlike both siblings,
Cyberbots does not stop without a cart. The shifts suggest the game uses the
cart during loading, but that is not shown. `ss.cart auto` (1 MiB) stays.
Play with no cart was not tested; recorded in `docs/known_unknowns.md`.

Next action: `EMU-005` (pad bindings; needs the user and their controller),
`EMU-006` (screenshots and save/load states by hotkey).

## 2026-11-02 — SESSION-0005: pad bindings copied

Task: EMU-005

User instruction (2026-11-02, verbatim): "You should be able to use the same
configuration for the pad you had in MSHvSF and XvSF."

Action: compared the `ss.input.port1.gamepad.*` lines of the MSHvSF
(modified 2026-10-28) and XvSF (2026-11-01) interactive configurations:
identical, 13 lines, one joystick ID. Copied them from XvSF with
`./invenv.sh python -m tools.mednafen.home --bindings-from
../xmen_vs_sf_saturn_en_translation/local/mednafen/mednafen.cfg` (13 lines
changed per home; a second run: `no change`). `-help` with each home: 7,904
valid, 0 unknown settings.

Result: both configurations are byte-identical to XvSF's current ones
(`cb1c2d3b…a1e9` interactive, `aad9a7ef…57cf` quiet), superseding the
`EMU-002` hashes.

Conclusion: `EMU-005` `DONE` on the user's instruction; no in-game button
check was run. Which Saturn button does what in Cyberbots is noted at the
first play session (`REF-005`).

Next action: `EMU-006` (hotkey screenshot, save and load state), with the user
present.

## 2026-11-02 — EXP-0003: screenshots and states by hotkey

Task: EMU-006

Goal: show that screenshots and save/load states work and stay under ignored
paths.

Hypothesis: F9, F5 and F7 work in stock 1.32.1; a reloaded title state shows
the screen it was saved on, in-session and after a fresh cold boot.

Action: with the user present ("Run EMU-006"), three runs of
`tools/mednafen/hotkeys.py` (14:27-14:32 local time): run 1 as XvSF did it
(focus returned after each key), run 1b with `--keep-focus` and wider gaps,
run 2 a cold boot loading run 1b's state at about 22 s.

Result:

- Run 1: two of three screenshots; the F9 1.85 s after F7 wrote nothing, and
  the log cannot show whether F7 loaded. Kept as evidence, not explained.
- Run 1b: all four screenshots. 1.3 s after F7 the screen is byte-identical
  to run 1's title shot (`b7286b3c…a1a9`); 4.4 s after, black, as in the
  normal attract order.
- Run 2: black at 21 s; 2.0 s after F7 the title, byte-identical to run 1b's
  save-time shot (`e39d8e2e…70c7`); 5 s after, the next attract screen. State
  `a904685f…1a69` unchanged by loading.
- Source, binary and configs unchanged; states and screenshots ignored.

Conclusion: **CONFIRMED** (D-004). Use `--keep-focus` for hotkey runs; the
lost key's cause is open (recorded in `EXP-0003`). `EMU-006` `DONE`;
`EMU-007` `READY`.

Next action: `EMU-007`, kept minimal (stock debugger: WRAM-L and WRAM-H dumps
at one paused instant, one memory write, one write breakpoint), then
`EMU-020`/`EMU-021` to build the agent interface.

## 2026-11-02 — EXP-0004: stock debugger dumps, a write, a breakpoint

Task: EMU-007

Goal: the minimum stock-debugger evidence before the agent interface:
repeatable work-RAM dumps at a paused instant, one memory write, one write
breakpoint.

Hypothesis: `tools/mednafen/hotkeys.py` drives all three unattended, using
XvSF's working step scripts with Cyberbots' title timing.

Action: with the user present ("Run EMU-007"), runs A, A2 and F,
14:34-14:40 local time (`research/experiments/EXP-0004/`).

Result:

- Run A: WRAM-H dumps and the write test worked; both WRAM-L dumps were
  silently not written (no file, no log error), though the capture shows the
  editor on Low Work RAM.
- Run A2 (run A plus two captures around the first WRAM-L dump): every file
  written. WRAM-L dumps identical (`bb0628a5…517c`), WRAM-H dumps identical
  (`fc70d589…8b10`); write test reads back the pattern, then the original.
  State `52ce80ae…b311` saved at the same freeze.
- Run F: breakpoint on all WRAM-H; identical captures after it; CPU view at
  PC `060008F0`, `mov.l r0,@-r15` (stack push, `[INT42]` in the trace).
- Source and configs unchanged.

Conclusion: **CONFIRMED** (D-005). The lost WRAM-L dumps are unexplained;
recorded as "check every dump file exists". `EMU-007` `DONE`; `EMU-020` and
`DBG-001` `READY`.

Next action: `EMU-020` (offline record citing the siblings' evidence), then
`EMU-021` (apply the patch, build, validate V1-V4 with the user present);
`DBG-001` (extract WRAM-L/WRAM-H from the run A2 state and compare with the
dumps; add VDP1/VDP2 VRAM dumps).

## 2026-11-02 — EXP-0005: save-state extractor validated

Task: DBG-001

Goal: show that `mcs_extract.py` reproduces same-instant debugger dumps on
Cyberbots before any extracted region is used as evidence.

Hypothesis: the default `saturn` byte order (16-bit swap) reproduces WRAM-L,
WRAM-H, VDP1 VRAM and VDP2 VRAM exactly; the unswapped order does not.

Action: offline comparison for `EXP-0004` instant A2 (work RAMs); then, with
the user present ("DBG-001 first"), a new freeze dumping all four regions
with a state saved at the same instant. Run G (14:44 local) failed: the
memory editor never opened, the typed commands went to the CPU view, no dump
was written (kept in `local/dbg001/run-g-failed/`). Run H (14:46), keys a
second apart and a capture after `option+3`, wrote all four dumps; captures
confirmed the four address-space names.

Result: `saturn` output identical to every dump (six comparisons, two
instants for WRAM-H); `state` order differs in every region (17,034 to
712,044 bytes). The extractor refuses the cart section: 1 MiB present, 4 MiB
expected. Also a shell slip: an unquoted `$R` holding several `--region`
flags was passed as one argument under zsh; rerun with the flags written out.

Conclusion: **CONFIRMED** (D-006). Work RAM and VRAM from states are usable
evidence; cart RAM is not, and the default all-regions extraction fails on
this game. Silent hotkey/debugger failures are now three; recorded in
`docs/known_unknowns.md`, to be retired by the agent interface.

Next action: `EMU-020` (offline), then `EMU-021` with the user present.

## 2026-11-02 — EMU-020 and EXP-0006: agent interface built and validated

Task: EMU-020, EMU-021

EMU-020: the record is the "Why Stock Is Not Enough" section at the top of
`docs/mednafen_agent_interface.md` (the MSHvSF protocol copy kept below it).
It cites MSHvSF `EMU-012`/`EMU-020`, XvSF `EMU-020`, the user's `DOC-002`
reuse answer, and Cyberbots' own evidence: three silent key-driven failures.

EXP-0006 (user present: "Yes, build it"):

- Copied `vendor/mednafen/src` to `src-agent`, applied the patch (four files,
  clean), built in `build-agent` (14:54:46-14:57:56): binary `2fc3d547…eaaf`;
  stock binary unchanged.
- V1: patched binary with no agent directory, 120 s cold boot: 119 of 119
  frames equal D-001 (14:58-15:00). Smoke: `status`, 13 `spaces`, 50 `regs`.
- `research/experiments/EXP-0006/validate.py` (XvSF's script; image, title
  frame 3700 and V4 ranges changed), 15:00:40-15:02:14:
  - V2: four reads equal `mcs_extract` of the same-poll state.
  - V3: exact write round trip; pause/step/run/frames behave; savestate
    refused while halted.
  - V4: log mode on three game-variable ranges (bytes that changed between
    the `EXP-0004` and `EXP-0005` title freezes): 10,822 hits over 1,800
    frames, 48 PCs, frames advancing.
  - V4b: halt mode on all WRAM-H stopped at PC `060008F0`, R15 `06008000`,
    which confirms `EXP-0004`'s by-eye reading of the stock CPU view.
- Source, stock binary and configs unchanged.

Conclusion: **CONFIRMED** (D-007). M0's emulator work is complete; the agent
replaces hotkey-driven debugger runs. Observation (HYPOTHESIS): `status`
shows `pc=00000000` while halted at a frame boundary, which may also explain
the stock CPU view's PC `00000000` in `EXP-0005` run G.

Next action: `REF-005`, a recorded play session with the user (boot, attract,
story mode through at least two fights with dialogue, a continue, options),
with `session_recorder.py --keep-states 0`. Offline meanwhile: `TXT-001`,
`REF-001`, `DOC-003`, `ENV-007`. `GATE-M0` still needs `DBG-002` to
`DBG-004` and `REF-008`.

## 2026-11-02 — EXP-0007: static census of the script blocks

Task: TXT-001

Goal: describe the Shift-JIS dialogue in `END.BIN`, `VICTORY.BIN` and
`STG0AS.BIN` without assuming it is what the game draws.

Action: hand exploration with scratch scripts (layout, load base, pointer
spacing, copy comparison, character inventory), then a reusable tool,
`tools/text/script_census.py` (9 tests), run over all 264 extracted files into
`data/text/script_census.json` (offsets, lengths, hash prefixes, counts).

Result (`research/experiments/EXP-0007/README.md`, D-008):

- One block per file; the dialogue part (1,851 lines plus the literal
  `SsCB`, 50,112 bytes) is byte-identical in all three.
- Lines: 4-byte aligned, NUL-terminated, zero-padded, no control bytes, at
  most 16 full-width characters (34 bytes).
- Load base `0x06060000` for all three (found by maximizing pointers to line
  starts). Every dialogue line is pointed to in each file, from record-like
  structures after the table.
- 909 distinct double-byte characters (729 kanji); some half-width ASCII.
- Disproven along the way: SESSION-0001's "slightly different character
  counts" meant different trailing ASCII literals, not different dialogue.
  My first base histogram (sampled offsets, all candidate words) gave junk
  bases for `END.BIN` and `STG0AS.BIN`; restricting to WRAM-H and testing
  every aligned base found `0x06060000` for all three. A first tool run also
  matched graphics data in `SELECT.VAD` and `ST08_FNT.BIN`; a
  longest-line rule removed them.

Conclusion: **CONFIRMED** as file facts. Runtime use stays **HYPOTHESIS**.
For later layout work: 16 full-width cells per line, and the presence of
half-width ASCII in the script.

Next action: `REF-005` (recorded play session with the user) to see these
lines on screen; offline `REF-001`, `DOC-003`, `ENV-007`.

## 2026-11-02 — SESSION-0006: offline references (REF-001, ENV-007, DOC-003)

Task: REF-001, ENV-007, DOC-003

REF-001:

- `mame -listxml 'cybots*'` (MAME 0.289) saved to the ignored
  `local/logs/ref001-listxml.xml` (`7a8c40be…c669`).
  `tools.reference.listxml_match` matched every member of the five zips by
  SHA-1, none unmatched; written to `references/arcade/manifest.json`.
- `cps2.cpp` copied from MSHvSF's ignored `local/mame_src/` (`a8c09ef8…1602`,
  the siblings' pin). `tools.reference.mame_audit`: `cybots.zip` 21/21.
  Clone zips report the parent's shared ROMs as missing because that tool
  matches by member name within one zip; not a defect of the sets.
- Headless boots of `cybotsu` and `cybotsj` with `mame_snap_frames.lua`
  (frames 1800 and 3000): both exit 0; attract fight and `INSERT COIN`
  (agent-reviewed).

ENV-007:

- Built-in browser: redump.org search lists two Saturn entries, 58190
  (Original, T-1217G) and 3669 (Limited Edition, T-1216G). `curl` fetched
  their SHA-1, MD5, SFV and cue lists (the web-fetch tool's earlier
  `ECONNREFUSED` was that tool's network, not the site).
- Scripted comparison: all 62 tracks plus the CUE equal 58190 in SHA-1, MD5
  and CRC-32; our CUE is byte-identical to Redump's. 3669 shares track 01
  and differs in all 61 audio tracks. "(2M)"/"(1M)" are Redump's names for
  the two masterings (`2MB1`, `1M2` in the ring code). Records:
  `references/saturn_jp/redump_58190.json`, `redump_3669.json`.
- Consequence: identity **CONFIRMED**; a track-01 patch applies to both
  editions' data track.

DOC-003:

- `docs/references.md`: platform sections copied unchanged from XvSF
  `9cb01ad` (verified identical by `diff`), plus "Cyberbots Prior Art".
- Read: Wikipedia (console ports 1997, Japan only; four console-only pilots;
  Akuma-mech code; "requires" the 1 MB cart; voiced story mode, citation
  needed). Not read: TCRF's arcade page and Lost In Translation (bot checks,
  not bypassed), Hardcore Gaming 101 (maintenance). No Saturn translation
  found.
- New scope hypotheses recorded: the four console-only pilots have no arcade
  English; ending tracks 42-62 may be voiced.

Next action: `REF-003` (locate the arcade English; offline with MAME) or
`REF-005` (play session with the user).

## 2026-11-02 — EXP-0008: arcade English dialogue located and decoded

Task: REF-003

Goal: find where and how the arcade stores its English dialogue.

Action: rebuilt the 4 MiB program region of each set from the pinned driver;
listed long ASCII runs (system text only); relative search by value
differences at 8 and 16 bits; built a character map from context; searched
for pointer tables; wrote `tools/reference/cybots_text.py` (5 tests); ran it
on all five sets (15:56, 3 s).

Result (`research/experiments/EXP-0008/README.md`, D-009):

- English: one byte per character, capitals ASCII + 9 and lowercase ASCII + 3
  (two offsets in the relative search: names +9, words +35, i.e. uppercased
  lowercase), digits `40`-`49`, `?`/`!` `7E`/`7F`, punctuation `14`, `1B`,
  `F8`, space `F0`, line break `FF`.
- Records: four 16-bit words (fourth `000E`), text, `00`. Table of 624
  pointers at `0x0B33AA` → 530 records; up to 4 lines, 38 characters per line.
- Two more tables, Spanish (624) and Japanese (494, 2-byte codes); all three
  identical in content across the five sets.
- Four rare English codes left (`09`, `0B`, `18`, `1C`), hypotheses only.

Disproven: my SESSION-0001 reading that English might sit only in ROMs
`03`/`04` as ASCII; it is in that area, but not ASCII. Also, a first
table-finder ran past a table's end into its first record's header
(caught by a synthetic test); a run now ends where a slot is itself a record.

Conclusion: **CONFIRMED** location, layout and map. The arcade English is
roughly 530 records against the Saturn's 1,851 lines, with up to 38
characters per English line against 16 full-width cells per Saturn line:
pairing (`REF-006`) and layout (`LAYOUT-001`) are the next hard parts.

Next action: `REF-004` (MAME: show a predicted record on screen and settle
the four codes) or `REF-005` (play session with the user).

## 2026-11-02 — EXP-0009: the arcade draws the decoded records

Task: REF-004

Goal: show that the arcade draws the records `EXP-0008` decoded, find what
selects one, and settle the four context-only codes.

Action: headless MAME runs with `mame_timeline.lua` (16:00-16:20 local):
attract only; a 1-player start; slot-variable write log; breakpoint actions
replacing slots; the same route in `cybotsj` and `cybots`. Disassembly with
MAME's own debugger headless (`-debug -debugger none`, `dasm`) on the
decrypted `cybotsud` image: no new tool installed.

Result (`research/experiments/EXP-0009/README.md`, D-010):

- Attract mode never reads dialogue. A 1-player start reads slots 0-5 at
  known frames, and snapshots show exactly those records typed into boxes.
- Slot variable `0xFF2F7A`, written by `0x011D48` with exactly those values
  and frames; script table at `0x12150`; region byte `0xFF80A0` picks the
  table (US `02`, EU `08` → English; Japan `00` → Japanese).
- Forced slots render `09` `:`, `0B` `-`, `18` `"`, `1C` `.`; the decoder now
  covers 100% of the English. A first forced run drew one record at its own
  box position over leftover text (illegible); rerun on the blank intro
  screen.
- `cybotsj` draws its Japanese table; its first line opens like Saturn line 0.

Conclusion: **CONFIRMED**. The arcade English is now a verified oracle for
story dialogue. Endings were not reached.

Next action: `REF-006` (decode the arcade Japanese table and pair it with
the Saturn script; offline) or `REF-005` (play session with the user).

## 2026-11-02 — EXP-0010: the Saturn script against the arcade script

Task: REF-006

Goal: decide whether the arcade English is a line-for-line oracle for the
Saturn dialogue, and which Saturn lines have none.

Action: read the arcade Japanese record layout; learned its code map from
the Saturn script; aligned the two scripts; checked shared slot numbers with
one MAME run of `cybotsj` (run 7, 16:12 local); wrote
`tools/text/arcade_pairing.py` (6 tests) and ran it (16:14, 1 s).

Result (`research/experiments/EXP-0010/README.md`, D-011):

- Arcade Japanese: 16-bit codes, `FFFF` line break, same header as English.
  Map learned with no conflicting votes: 573 of 579 codes.
- 787 exact and 38 edited line pairs, in order, in 450 slots; slots' Saturn
  lines consecutive in 449 of 450.
- Saturn-only: 74 lines in 50 runs, and lines 899-1850 (952). Chiyomaru and
  Tessan appear only in that block.
- `cybotsj` shows slots 0-5 in the first scene, as `cybotsu` does; Japanese
  and English slot 0 are the same scene in free translation.

Disproven: a strict in-order walk of equal-length lines (it stopped at line
13, where the Saturn splits a line differently). The final method aligns by
content. My first scratch matcher was too loose (agreement on known codes
only); the tool's pairs require identical decoded lines or a similarity
threshold inside the gap between neighbours.

Conclusion: **CONFIRMED** for the map and the pairs; the per-slot English
is the arcade English by game logic, consistent with the user's policy
("Official; fixes opt-in"). About half the Saturn script (952 lines) has no
official English: under "Recorded new translation", that is new
translation work, gated as special cases (rule 24).

Next action: `REF-005` (play session with the user), or `REF-007` after it.

## 2026-11-02 — EXP-0011: recorded play session and text surfaces

Task: REF-005

Goal: list every surface where the Saturn shows Japanese, from a real play
session, and keep checkpoints for `REF-008`.

Action: launched the patched build in the interactive home with
`session_recorder.py --keep-states 0`; gave the user a ten-step route; the
user played 16:22-16:31 and reported "done". Stopped the recorder, closed
Mednafen with SIGTERM, reviewed 367 unique screenshots in 8 contact sheets,
re-checked picks at full size.

Result (`research/experiments/EXP-0011/README.md`, D-012,
`docs/text_surfaces.md`):

- 484 screenshots and 166 states kept (346 MB, ignored).
- Japanese on three surfaces: dialogue boxes, a VS-screen chapter caption,
  and katakana pilot and mech name art. The rest is English, including the
  options screen.
- The two VS captions are Saturn script lines 899 and 900, so the Saturn-only
  block of D-011 begins with chapter captions; D-011 and `EXP-0010` amended.

Disproven: "Japanese only in dialogue boxes" (the prediction). Also a review
slip: my first screenshot picks assumed the contact sheets tiled in list
order; three picks were wrong and were replaced after a full-size check.

Conclusion: **CONFIRMED** for what was seen; endings, versus mode, option
sub-screens, warnings and console-only pilots not reached.

Next action: `REF-008` (pick the M1 pilot and line; Jin's introduction or
pre-fight lines have checkpoints in this session) and `REF-007` (names).

## 2026-11-02 — EXP-0012: names across the releases

Task: REF-007

Goal: list every pilot and mech name, where it is art, and how the arcade
English differs; put the options to the user.

Action: speaker labels and frequent names from the arcade English; katakana
spellings counted in the Saturn script; MAME snapshots of the US and Japanese
pilot select and VS screens; VDP1 sprites of the session's VS-screen state;
the name sprites' bytes searched on the disc.

Result (`research/experiments/EXP-0012/README.md`, D-013, `docs/names.md`):

- No name differs between Japan and the US; only katakana versus Latin.
- Name art: pilot select and VS screen (katakana on Saturn and arcade Japan,
  Latin on the US arcade); HUD Latin everywhere.
- The Japanese arcade's VS screen shows the same chapter caption as the
  Saturn; the US arcade shows none. Correction to my play-session report,
  where I called the captions a Saturn addition.
- Saturn VS name art: raw VDP1 sprites in `SELECT.VAD`. Latin name art on the
  disc: not found, not ruled out (`LOC-001`).

Disproven: "some names differ between the releases" (the sibling pattern).

User decision (2026-11-02, verbatim, to "How should the English build handle
names?"): "I definitely want the toggle and I want it placed in the options
screen. We may need an expanded options screen like I'm currently working on
in the MSHvSF repo." Recorded in `docs/localization_policy.md`; `LOC-001`
and a new `OPT-001` outline added (models: MSHvSF `OPT-003`-`OPT-005`,
read-only).

Next action: `REF-008` (pick the M1 pilot and line from the session).

## 2026-11-02 — EXP-0013: M1 target line and checkpoint

Task: REF-008

Goal: pick the M1 target, fix the milestone unit, and prove a checkpoint.

Action: listed the pairing of Saturn lines 0-13; located the session frames
of Jin's first pre-fight box; replayed the session state at frame 5386 for
300 frames in the silent home; compared box regions.

Result (`research/experiments/EXP-0013/README.md`): target Saturn lines 4-5,
exact pairs with arcade slot 2; box on screen at session frames 5386-5693;
the replay's completed box equals the session's byte for byte (box-region
hash `c10179ad2f7af072`). `replay_state.py` re-validated.

Conclusion: **CONFIRMED**. Milestone unit is the box. `DBG-002` is `READY`.

Next action: `DBG-002` (replay the checkpoint several times and check the
same box appears each time), then `DBG-003` and `DBG-004`.

## 2026-11-02 — EXP-0014: dialogue selection from one checkpoint

Task: DBG-002

Goal: learn whether the target box varies when one checkpoint is replayed.

Action: three more replays of `f00005386` (8 × 50 frames) and two of
`f00005208` (12 × 50 frames), 16:49-16:51 local; dialogue-strip hashes per
step; differing frames reviewed.

Result (`research/experiments/EXP-0014/README.md`, D-014): every run shows
the same completed Jin box and the same Shade reply; two timing variants a
few frames apart, differing only in typing progress and mouth frames.

Conclusion: **CONFIRMED**: script-driven, not random (unlike the siblings'
quotes). Compare completed boxes, not aligned frames.

Next action: `DBG-003` (named checkpoints before, with and after the box),
then `DBG-004` (find the box's text in RAM).
