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

## 2026-11-02 — EXP-0015: named checkpoints around the M1 box

Task: DBG-003

Goal: states before, with and after the M1 box for memory comparison.

Action: `research/experiments/EXP-0015/capture.py` loads the session state,
runs to each offset, screenshots, resumes, saves; each saved state replayed
for 300 frames.

Result (`research/experiments/EXP-0015/README.md`): run 1's "box complete"
state was saved just after the box closed (offset 300 too late) and its
"box open" screenshots were blank; run 2 (offsets 10, 200, 420) gave A box
open, B box complete, C after the box, each confirmed by replay. Copied to
`local/checkpoints/m1/`.

Conclusion: **CONFIRMED**. Screenshots taken within ten frames of a state
load are blank; use replays as evidence for such states.

Next action: `DBG-004`: in checkpoint B, search WRAM-L/WRAM-H for lines 4-5
as Shift-JIS; then identify the renderer (VDP1 or VDP2) by a controlled
change; check whether `KANJI.BIN` supplies the glyphs.

## 2026-11-02 — EXP-0016: the M1 box's renderer and RAM text

Task: DBG-004

Goal: find the RAM text behind the M1 box and identify the renderer by a
controlled change.

Action: extracted the three checkpoints' regions; Shift-JIS search of WRAM;
compared `STG0AS.BIN` with WRAM-H; listed VDP1 sprites; zeroed one glyph cell
through the agent and screenshotted; searched for the glyph in RAM and in
`KANJI.BIN`.

Result (`research/experiments/EXP-0016/README.md`, D-015):

- Lines 4-5 once in WRAM-H as Shift-JIS, inside resident `STG0AS.BIN` at
  `0x06060000`.
- VDP1: 25 per-character 16×16 4 bpp sprites from cells at VRAM `0x1E200`;
  zeroing cell 0 blanked `次` on screen; cells are refilled within frames,
  apparently from a WRAM-H shadow at `0x060FE200`.
- `KANJI.BIN` shares the glyph palette but not in any simple layout tried.

Disproven: "the font is 16×16 1-bit" (my SESSION-0001 arithmetic guess for
`KANJI.BIN`).

Conclusion: **CONFIRMED** text and renderer; font source open. Every
`GATE-M0` dependency is `DONE`.

Next action: ask the user for `GATE-M0`; on GO, `RE-001`: from checkpoint A,
write different Shift-JIS into line 4 in WRAM-H before the box types, with a
no-write control replay.

## 2026-11-02 — GATE-M0 passed

Question (2026-11-02): "GATE-M0: go for the first live RAM change
(RE-001)?" The user's answer, verbatim: "GO for M1". `GATE-M0` is `DONE`;
`RE-001` is written out in `TASKS.md` and `IN_PROGRESS`.

## 2026-11-02 — EXP-0017: M1, the target box changed in live RAM

Goal: `RE-001`; show the M1 box (Saturn lines 4-5) is drawn from its
Shift-JIS bytes in WRAM-H.

Action: `research/experiments/EXP-0017/ram_write.py` from checkpoint A, once
with a 26-byte write of 13 hiragana to WRAM-H `0x0606F09C` while paused, once
as a no-write control; 6 × 50 frames with screenshots each
(17:03:52-17:04:11, the user present).

Result: read-back equals the written bytes, and they still hold at the end of
the run. Completed box: `1d501a` with the write, `ead786` in the control (as
in every earlier replay); at step 6 both show the same next box (`3a956a`).
The agent reviewed the screenshots: the write run's first line is the test
string, its second line unchanged. Source manifests unchanged.

Conclusion: **CONFIRMED (M1)**, D-016.

Next action: write up the M2 tasks (`DISC-001`, `DISC-002`, `FONT-001`) in
full in `TASKS.md` before starting them.

## 2026-11-02 — M2 tasks written up

`DISC-001` (`READY`), `DISC-002` and `FONT-001` (blocked on `DISC-001`) are
written out in full in `TASKS.md`, Phase G. Three offline checks made while
writing them, with scratch commands only:

- WRAM-H from `0x06060000` at checkpoint B differs from `STG0AS.BIN` in 29
  bytes (EXP-0016 recorded 30), from `VICTORY.BIN` in 121,327 and from
  `END.BIN` in 285,494. `STG0AS.BIN` stays the SUPPORTED source.
- `STG0AS.BIN` holds line 4's original 26 bytes at file offset `0xF09C`
  (sector 30, LSN 22,568, bytes `0x09C`-`0x0B5`): the `DISC-002` prediction.
- None of glyph cell 0's non-blank 8-byte rows (checkpoint B, WRAM-H
  `0x060FE200`) occurs raw in any of the 264 data-track files.

Next action: `DISC-001`.

## 2026-11-02 — EXP-0018: the M1 text's disc file (DISC-001)

Goal: `DISC-001`; find which file the M1 box's text is loaded from, and how.

Action: scanned WRAM-H of the 166 REF-005 states (`scan_states.py`); agent
runs with a write breakpoint on lines 4-5 from state 4138 (machine select,
twice), from 4493 (control), and once with the CD block command registers
logged (`trace.py`), 17:14-17:17, the user present; disassembled the hit.

Result: the load happens between 4138 and 4316, in file order. 14 hits at
`0x06041FB4`, a raw longword copy from the CD data register; the values
equal `STG0AS.BIN[0xF09C:0xF0D4]`, and the two runs are identical. The
control has no hit. One Play Disc command, for FAD `0x58A0` and 157 sectors,
which is `STG0AS.BIN`; the game's own file table agrees (file 292). After the
load, 10 bytes outside the table differ from the file. Source hashes
unchanged.

Conclusion: **CONFIRMED**, D-017. Not seen: when `VICTORY.BIN` and `END.BIN`
load (moved to `docs/known_unknowns.md`).

Next action: `DISC-002`. Build an image with line 4 changed in `STG0AS.BIN`
only (offset `0xF09C`, LSN 22,568). Check it from state 4138 with the
rebuilt image mounted, against the original as control. Then a cold boot and
the user's play check.

## 2026-11-02 — EXP-0019: the M2 image (DISC-002)

Goal: `DISC-002`; reproduce the M1 change from an image rebuilt from the
untouched source.

Action: `research/experiments/EXP-0019/build.py`: an identity build, then two
builds with line 4 of `STG0AS.BIN` (offset `0xF09C`) replaced by the M1
string. Then the EDC/ECC check and a track diff; replays from state 4138 on
the rebuilt and the original image (36 × 50 frames, line 4 write log); a
stock cold boot of the rebuilt image (120 s, fresh home). 17:20-17:25, the
user present.

Result: the identity build is byte-identical. The M2 builds are identical,
with only LSN 22,568 changed, and every sector passes. The load carries the
test string; the completed box is `1d501a` (rebuilt) against `ead786`
(original), and every step outside the box is identical. The cold boot is
frame-identical to EXP-0001's. Source hashes unchanged.

Failed attempt: clearing `local/mednafen_quiet/sav/` before the cold boot was
refused by a safety check (a glob removal). Nothing was deleted. A fresh home,
`local/mednafen_disc002`, gave the empty backup RAM instead. The spare builds
`build/disc002/identity` and `build/disc002/m2b` were deleted (user rule;
`build.py` regenerates them).

Conclusion: **CONFIRMED** by the agent runs. `DISC-002` stays `IN_PROGRESS`
until the user's cold-boot play check of `build/disc/cyberbots_m2_disc002/`.
The commit stays local until then.

Next action: the user's play check; on a pass, record M2 (D-018), push, and
start `FONT-001`.

## 2026-11-02 — DISC-002 play check and M2

The user's first manual check (17:28-17:30, the patched image, confirmed in
the terminal) stopped at the narration box before Jin's box. It ends in
"・・・。" on every disc, so the result was inconclusive. Asked to repeat it
with an F9 screenshot, the user declined, verbatim: "Yeah, I don't want to do that at all. Why can't you just boot the machine and take regular screenshots like I did with the XvSF and MSHvSF translations?"

Decision recorded in `docs/localization_policy.md` and in the ignored local
guidance: the agent runs cold-boot play checks itself, with pad keys through
System Events and agent-reviewed screenshots.

Action: `research/experiments/EXP-0019/drive.py`, a cold boot of
`build/disc/cyberbots_m2_disc002/` under the agent build. Eight keys were sent:
Start ×4 through the attract loop, A on ARCADE MODE, A on Jin, and A on
Blodia twice (the first press was not taken). 17:33-17:37, the user present.

Result: Jin's box shows あいうえおかきくけこさしす on line 1 and the original
line 2 (frame 13982, agent-reviewed). The narration before it and Shade's
reply after it are unchanged. Source hashes unchanged.

Conclusion: **M2 CONFIRMED**, D-018; `DISC-002` is `DONE`.

Next action: `FONT-001`. Pushing the image-changing commits waits for the
user's OK (hardware check before push).

## 2026-11-02 — Push rule for image changes

Asked whether to push the M2 commits, the user answered, verbatim: "Let's push now. In general, I'm not going to want to burn a disc until we're much, much closer to finished. Mednafen does a fantastic job of replicating real hardware so I don't feel the need to constantly check."
Image-changing commits now push after the agent's cold-boot play check, like
doc-only commits. A real-Saturn check comes near the end, before a release.
Recorded in `docs/localization_policy.md`.

## 2026-11-02 — EXP-0020: the dialogue font (FONT-001)

Goal: `FONT-001`; find the glyph data and routine, the font's disc source
and its format.

Action: a write trace on the WRAM-H glyph shadow from checkpoint A; a PC log
of the cell routine; disassembly of it and its caller. A scan of VDP2 VRAM
across the 166 session states; CD command and VDP2 write traces from state
5208. The new `tools/font/kanji.py` (decode, encode, code table, sheet). A
probe image with glyph 600 replaced, replayed with the original as control.
17:47-17:52, the user present.

Result: the routine `0x06011224` copies four VDP2 tiles per glyph. The caller
maps each two-byte code through a 1,222-entry table in `STG0AS.BIN`
(`0x060AAD7C`); 25/25 tile indices are predicted. `KANJI.BIN` is read (FAD
`0x1342`, 80 sectors) into VDP2 VRAM `0x40000` as each box scene starts. The
repack is byte-identical, and 25/25 decoded glyphs equal the rendered cells.
The probe shows a block in place of the first character only. The earlier
failed searches (EXP-0016, the 8-byte-row recheck) failed because each cell
row is split across two 4-byte tile rows. Source hashes unchanged; the probe
image was deleted.

Conclusion: **CONFIRMED**, D-019. For `FONT-002`: the font already has
full-width A-Z and 0-9, no lower case, 58 free glyphs, 26 free table slots,
and two half-width pair glyphs.

Next action: write up `FONT-002` in full (M2's last outline task).

## 2026-11-02 — FONT-002 written up

`FONT-002` is written out in full in `TASKS.md` (`READY`). Phase A comes
first: look for a native English path in the text renderer (XvSF lesson 1).
Phase B then measures, by live RAM tests from checkpoint A with controls,
full-width Latin, unknown codes, line length, lines per box and the cell
limit, and ends in a capacity statement for `LAYOUT-001`. Nothing goes on
disc.

Next action: `FONT-002`, Phase A.

## 2026-11-02 — EXP-0021: no native English path; box capacity (FONT-002)

Goal: `FONT-002`. Phase A looks for a native English path; Phase B measures
Latin text and the box.

Action: disassembled the typing routine, the layout loop, the cell allocator
and `0x0603963E` (a shift by 8). Logged the layout loop's entries while the
box types. Searched the 264 files for the arcade's English. Ran six live RAM
tests from checkpoint A (control, capitals, unknown, long, breaks, rows), plus
rows for 24 steps. `capacity.py` over the 450 paired slots. 17:55-18:04, the
user present.

Result:
- **No native path:** no region or language branch, and no English dialogue
  on the disc.
- **Text:** full-width capitals draw; unknown codes leave blanks; there is no
  wrap. `0x0A` does nothing while typing, so the hypothesis that it is a line
  break there is DISPROVEN for typed boxes.
- **Box:** rows come from the record; 4 rows are visible; 60 cells are
  reserved, and going past them hangs the game.
- **Capacity:** 31, 272 and 450 of 450 slots fit for the three routes
  (single as written, single re-wrapped, pairs).

Source hashes unchanged.

Conclusion: **CONFIRMED**, D-020 (the hang SUPPORTED). M2's tasks are all
`DONE`.

Next action: write up the M3 tasks in full. `LAYOUT-001` puts the capacity
routes to the user as a decision.

## 2026-11-02 — M3 tasks written up

`TASKS.md` Phase H (Jin's story dialogue) is written out in full:
- `RE-002` (selector, Jin's box list, forcing), `READY`;
- `LAYOUT-001` (four routes; limits, the user's decision, then a proof on a
  rebuilt image), Phases A-B `READY`;
- `PAIR-001` (pairing by both games' logic; Saturn-only lines shown from the
  arcade code), blocked on `RE-002`;
- `GATE-TRANSLATION`, moved to M3, which now also depends on `PAIR-001`;
- `RE-003` (compiler, build, every box forced, agent cold-boot play check).

VS captions, name art and endings stay out of M3.

Next action: `RE-002`.

## 2026-11-02 — EXP-0022: box selection and Jin's boxes (RE-002)

Goal: `RE-002`; find what selects each box, list Jin's boxes, and force any
box.

Action: breakpoint logs from REF-005 states 4138, 4493 and 5208 (box
function, scene lists, task fields, message queue); disassembly of the stage
handlers, the scene start and the bytecode interpreter; a scan of the scene
posts in `STG0AS.BIN` and `END.BIN`; `box_list.py` to
`data/text/jin_boxes.json`; `force_scene.py` for the control and scenes 4, 9
and 15, checked by `check_cells.py`. 18:05-18:28, the user present.

Result:
- **Chain:** stage constants, then the scene task (pilot byte task + `0x1F`,
  scene byte task + `0x23`), the pilot's scene list, the script, the box
  index, the record table `0x060A5684`, and the lines.
- **Jin:** 17 story scenes in fixed order; boxes 0-62; lines 0-120, with line
  34 dead. Scenes 16-20 are the ending, from `END.BIN`.
- **Forcing:** 5/5, 20/20 and 14/14 cells; the control 25/25.
- First misreading, corrected in the same session: the box-list filter at
  first took `0x8000 | N` as the box and skipped the word after `0xE205`. The
  halt at `0x0606E504` (R6 = 2, no flag) showed that the plain word shows the
  box and the flagged one closes it.
- The per-pilot table at `0x060AB870`, first taken for box lists, holds
  frame-like values (multiples of 30): not boxes, and not used here.

Source hashes unchanged.

Conclusion: **CONFIRMED**, D-021. `PAIR-001` is unblocked.

Next action: `PAIR-001` or `LAYOUT-001` Phases A-B (the user's choice).

## 2026-11-02 — EXP-0023: Jin's pairing; REF-006 reader corrected (PAIR-001)

Goal: `PAIR-001`; pair each line of Jin's boxes with the arcade English by
both games' own logic.

Action: decoded the arcade's script table `0x12150` (the interpreter at
`0x11CC6`, saved disassembly from EXP-0009) for pilot 0. Ran MAME
`cybotsu`: one unforced run, and scenes 4, 9 and 15 forced at `0x11CEA`,
with slot logs and snapshots. Generated the pairing table with
`pair_jin.py`. 18:30-18:45, the user present.

Result: the arcade's Jin scenes 21 and 0-15 equal the Saturn's box lists.
Forced arcade scenes show slots 18, 33 and 59 in English, matching the
Saturn's forced boxes.

The first pairing run labelled 13 lines in 9 boxes "expanded". Checking that
against the English record lengths exposed a REF-006 bug: `read_jp_record`
stopped at the space code `0x0020`, which occurs 60 times inside arcade
Japanese records. The bug is fixed, with a test, and REF-006 was rerun:
- 897 of lines 0-898 now pair (852 exact, 45 edited), in 488 slots;
- all 120 of Jin's lines align (115 exact, 5 edited);
- there are no Saturn-only lines in Jin's story;
- capacity rerun: 33, 298 and 488 of 488 slots fit (579 pairs).

D-011 and D-020 carry dated corrections, and EXP-0010 and EXP-0021 have
notes. SPECIAL-001's "74 Saturn-only lines" is replaced: only line 258 is
Saturn-only, and line 34 is dead data. Source hashes unchanged.

Conclusion: **CONFIRMED**, D-022. `GATE-TRANSLATION` is now `READY`; it waits
on the user's GO.

Next action: `GATE-TRANSLATION` (the user's GO for Jin's official English) or
`LAYOUT-001` Phases A-B.

## 2026-11-02 — EXP-0024: layout limits and the route decision (LAYOUT-001 A-B)

Goal: `LAYOUT-001` Phases A-B; measure each route and put the choice to the
user.

Action: a code census of all three script copies; a search of all files for
the glyph routines; the record size; the text room, including dead ending
lines in `STG0AS.BIN`; `room.py` route counts; never-nonzero scans of WRAM
and VDP1 VRAM over the 166 states; a 12,000-frame write log over two
candidate regions. 18:44-18:55, the user present.

Result:
- **Codes:** 912 of 1,222 in use.
- **Font users:** story, endings and `VICTORY.BIN` share the font.
- **Records:** 3 lines in place.
- **Room:** 3,448 + 820 bytes.
- **Route fits:**
  - (a): 35 of Jin's boxes, 298 roster;
  - (b): 63, 488;
  - (c): 43, 372, or with (d) 63, 488.
- **Free RAM:** two 19.5 KB WRAM-H regions with no CPU writes.
- **Correction:** route (c) was first counted at 1 byte per character; the
  renderer reads 2 bytes per glyph, so it costs 7,448 bytes for Jin.

Question (multiple choice; pair glyphs marked "(Recommended)"). The user's
answer, verbatim (2026-11-02): "Pair glyphs (Recommended)". Recorded in
`docs/localization_policy.md`.

Conclusion: route (b), pair glyphs. Measurements CONFIRMED (D-023); the
dead-line room and the dialogue-time VDP1 room are SUPPORTED.

Next action: `LAYOUT-001` Phase C (a rebuilt image with synthetic pair
glyphs in the M1 box, agent cold boot), or `GATE-TRANSLATION`.

## 2026-11-02 — EXP-0025: pair glyphs proven (LAYOUT-001 Phase C)

Goal: prove the chosen route on a rebuilt image with synthetic text.

Action:
- captured the arcade's English font in MAME;
- added `tools/font/pairs.py` with tests;
- built an image with 48 test pairs and 3 rows in Jin's dead ending lines;
- replayed from state 4138 on it and on the original;
- cold-booted it and drove the route with pad keys.

18:58-19:30, the user present.

Failed attempts:
- **Cutting letters from running text:** outlines touch, so run
  segmentation failed. An 8-pixel grid failed too, because spaces are 5
  pixels.
- **Debugger writes to ROM:** no effect. Replaced by a RAM record and a
  pointer redirect at `0x11F6E`.
- **A 4-line sheet:** its fourth line overlapped the box border.
- **Capture window:** too wide for code `0x14`.
- **Unnarrowed 8-pixel letters at a 7-pixel advance:** they touched.
- **The first cold boot:** keys went missing while another Mednafen (MSHvSF)
  was open. The user closed it ("It's closed, retry"), and the rerun sent
  every key.

Result: 15 sectors changed, all valid; two builds identical. The replay drew
48/48 test cells and 25/25 cells of the following Japanese box. The
cold-boot box is pixel-identical to the replay's. Source hashes unchanged.

Conclusion: **CONFIRMED**, D-024. `LAYOUT-001` is `DONE`.

Next action: `GATE-TRANSLATION`: ask the user for the GO on Jin's official
English, with pair glyphs. Then `RE-003`.

## 2026-11-02 — GATE-TRANSLATION passed for Jin's story

Shown to the user: the oracle, the pairing method (D-022), Jin's coverage (63
boxes, 120 lines, all with official English, none needing a new
translation), the policy, the layout (D-024) and the exclusions, plus the
glyph gap (353 pairs against 336 codes free of Japanese).

Question 1, verbatim: "GATE-TRANSLATION: may Jin's official arcade English go on the disc, as paired, with pair glyphs?"
Answer, verbatim: "GO (Recommended)"

Question 2, verbatim: "If Jin's English still needs more glyphs than the 336 unused slots after optimising pair splits, what should give?"
Answer, verbatim: "Rarest Japanese glyphs (Recommended)"

Recorded in `TASKS.md` (a dated block under the gate) and in
`docs/localization_policy.md`. `RE-003` is `READY`.

Next action: `RE-003`.

## 2026-11-02 — EXP-0026: Jin's story in English (RE-003, M3)

Goal: `RE-003`; compile, build and verify all of Jin's story dialogue in
official English.

Action:
- wrote `tools/text/dialogue.py` with tests, and built twice;
- forced all 17 scenes and checked every box's cells, with a control on the
  original;
- found the fighters' vitality;
- cold-booted and played into stage 2 with forced fight wins;
- checked pilot 1's Japanese on both images.

20:20-20:50, the user present.

Result:
- **Build:** 63 boxes, 137 rows, 353 pairs (310 unused codes, 25 new, 18
  sacrificed per the user); 82 sectors, all valid; identical builds.
- **Forced:** 63/63 boxes exact; control 0/8.
- **Play:** stages 0-2 played; 20 boxes complete and exact, 1 mid-typing.
- **Pilot 1:** Japanese unchanged.

Failed attempts:
- Forcing from state 5208 showed Japanese: the state holds the old script in
  RAM. Fixed by starting from 4138, before the load.
- Vitality guesses: x positions at `+0x14`, and the words `0x060D45D8`/`46D4`/`47D0`
  and `0x060E1492`. The bar pair at `+0x44` is vitality.
- A Mednafen lockfile clash between two runs in one home. Fixed with a
  scratch home.

Decision note: the pair count could have been cut to 299 by indenting 43
rows one space, which would have sacrificed no Japanese. That was not done
(it would look ragged); the user's fallback was used instead.

Source hashes unchanged.

Conclusion: **CONFIRMED (M3)**, D-025.

Next action: write up the M4 tasks (a second pilot).

## 2026-11-02 — M4 tasks written up

`TASKS.md` Phase I (a second pilot) is written out in full:
- `RE-004`: name the 11 pilot lists, the user chooses the pilot, list its
  boxes;
- `PAIR-002`;
- `RE-006`: a multi-pilot compiler with a shared code pool and a budget stop,
  plus pilot-aware checks;
- the gate extension;
- `RE-007`: build both pilots, verify every box, and a cold-boot play.

A survey of `STG0AS.BIN`'s pilot lists is in `RE-004`'s notes:
- lists 0-5 are the arcade pilots, 141-164 paired lines each;
- lists 6-9 are the Saturn-only pilots, almost none paired;
- list 10 has 7 scenes.

Next action: `RE-004`.

## 2026-11-03 — RE-004: the second pilot is Santana

Shown to the user: a table of the five arcade pilots (lists 1-5), with story
boxes, slot-for-slot pairing, new pairs beyond Jin's, the total sacrifice
with Jin, bytes against their own lines' room, and shared lines. The lists
were named from their scene-0 dialogue (forced on the original image) and
from the counts of pilot names in their English records:
1 Santana, 2 Mary, 3 Arieta, 4 Gawaine, 5 Bao and Mao.

Question, verbatim: "Which pilot should be the second one in English (M4)?"
Answer, verbatim: "Santana (Recommended)"

## 2026-11-03 — EXP-0027: lists named; Santana's route and boxes (RE-004)

Action:
- forced scene 0 of all 11 lists;
- compared the lists with the arcade's scripts;
- wrote `scene_posts.py`, `candidates.py` and `play_route.py`;
- made two cold boots (one move right, then two);
- wrote Santana's box list, and forced three of his scenes.

Result:
- **Lists:** 0-5 are Jin, Santana, Mary, Arieta, Gawaine, and Bao and Mao
  (arcade pilots 0-5); 6-8 are Saturn-only.
- **Choice:** the user chose Santana (recorded above).
- **Route:** Santana is two moves right on the pilot select screen; the
  cold boot posted 23, 0-4 from stage group 9 (Mary's run started at 18).
- **Story:** scenes 0-15 and 23-26, boxes 64-127.
- **Forcing:** 29/29, 29/29 and 30/30.

Failed attempts:
- The first select run lost the ARCADE MODE press (pressed right as the menu
  appeared). The route now checks that the menu is gone and retries.
- The tiling scratch commands hit zsh word-splitting and the `$f[...]`
  subscript. They are now built in Python.
- The scratchpad was cleared between sessions, which lost RE-002's scratch
  post scan. It is now `EXP-0027/scene_posts.py`.

Source hashes unchanged.

Conclusion: **CONFIRMED**, D-026. `PAIR-002` and `RE-006` are `READY`.

## 2026-11-03 — EXP-0028: Santana's pairing (PAIR-002)

Action: generalized the pairing script (`pair_pilot.py`; it reproduces
Jin's), paired Santana's boxes, examined the exception, and forced three of
his scenes in MAME with the pilot set to 1. 11:20-11:30.

Result:
- **Scripts:** the same in both games for all 20 story scenes.
- **Lines:** 114 exact and 3 edited of 117; all 64 boxes have English.
- **Exception:** box 64's lines aligned to slot 63, and slots 63 and 64 share
  one record. The script now recognizes shared records.
- **MAME:** scenes 4, 9 and 24 played slots 81-84, 99-105 and 87-88, with
  Santana's English on screen.

Conclusion: **CONFIRMED**, D-027. No new translations are needed for
Santana.

Next action: `RE-006`.

## 2026-11-03 — EXP-0029: the compiler and checks for a set of pilots (RE-006)

Action: generalized `tools/text/dialogue.py` (several `--pairing` files, one
code pool, kept and dead lines from the scene scripts, `--max-sacrifice`,
`--budget`, `--record-dir`, `--task`); added tests; added
`EXP-0029/force_check.py` (any pilot, by the redirect). 12:07-12:10 forced
runs.

Result:
- **Jin alone:** derived kept lines 57, 75 and dead lines 752-777, 897, 898,
  953, EXP-0024's list. Image, files, prediction and record identical to
  `re003_jin.json` (Track 01 `904402b6…3f01`).
- **Jin + Santana:** 408 pairs; **73** sacrificed codes needed, 18 approved;
  the build stopped with exit 1 and wrote nothing. Touched: 62 lines in
  `STG0AS.BIN`, 198 with the other copies. Room 8,088 bytes for 7,316.
- **Determinism:** two builds each, identical (pair at `--max-sacrifice 73`,
  comparison only).
- **Checks:** Jin scene 9 8/8 boxes; Santana scene 4 on the original 29/29
  Japanese cells; both from state 4138, named in the output.
- **Measured, not adopted:** ranking sacrifices by uses that stay Japanese
  touches 184 lines instead of 198 but changes Jin's image.
- Commands: `./invenv.sh ruff check tools/ tests/ research/experiments/`
  (clean), `./invenv.sh mypy` on the changed files (clean), `./invenv.sh
  pytest -q tests/unit` (161 passed).

Conclusion: **CONFIRMED** for the tooling. Santana's ending lines are dead in
`STG0AS.BIN` as Jin's are (SUPPORTED).

Next action: the `GATE-TRANSLATION` extension for Santana: the user decides
the 73-code budget (or an alternative) before `RE-007`.

## 2026-11-03 — GATE-TRANSLATION extended to Santana

Shown to the user: Santana's pairing (EXP-0028: 64 boxes, 117 lines, 114
exact and 3 edited, no new translations) and the budget (EXP-0029: 408
pairs, 73 sacrificed codes against 18 approved). The 62 touched lines in
`STG0AS.BIN`, by whose scenes show them: lists 6-8 (Saturn-only) 44, Mary 6,
no scene 5, Bao and Mao 3, Gawaine 1, list 9 1, and one line each of Jin's
and Santana's dead ending copies; 198 with the other files' copies. The
alternatives: ranking by the uses that stay Japanese (184 lines; changes
Jin's image), and moving the code table to reach the font's 33 unreachable
glyphs (the table is followed by data at `0x060AB73C`; one pointer at
`0x0606EA40`; at best about 41 sacrifices; unknown result).

Question 1, verbatim: "GATE-TRANSLATION extension: may Santana's official arcade English go on the disc, as paired, with pair glyphs?"
Answer, verbatim: "GO (Recommended)"

Question 2, verbatim: "Jin + Santana need 73 sacrificed Japanese glyphs (18 approved so far). What should give?"
Answer, verbatim: "Approve 73, same rule (Recommended)"

Recorded in `TASKS.md` (a dated block under the extension) and in
`docs/localization_policy.md`. The compiler's default limit is now 73.
`RE-007` is `READY`.

Next action: `RE-007`.
