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

## 2026-11-03 — EXP-0030: Jin and Santana in English (RE-007, M4)

Action: built Jin + Santana from the untouched source (twice), forced every
story box of both pilots, checked Mary's scene 0 on both images, and
cold-booted Santana into stage 2 and Jin into his first scene. 13:00-14:12;
the user present for the cold boots ("Yes, go ahead (Recommended)").

Result:
- **Build:** 85 sectors, all 43,793 valid; two builds identical (Track 01
  `a63ba806…`); the source's 63 components unchanged.
- **Forced:** Jin 63/63, Santana 64/64 boxes; original-image controls 0 of
  233 and 0 of 178 cells.
- **Mary:** boxes 130 and 132 unchanged; box 131's `0x8BC1` (sacrificed)
  shows its pair glyph. A first predictor counted the full-width space
  `0x8140` as a cell (EXP-0027's `check_first_box.py` did; its boxes had no
  space) and matched only 3 and 2 cells on both images; the typing routine
  draws no cell for it. Fixed in `japanese_check.py`.
- **Santana's cold boot:** stage 9 → 10 → 11; posts 23, 0-4; 21 of 22 boxes
  complete, box 67 caught mid-typing (complete when forced).
- **Jin's cold boot:** posts 21, 0; 6 of 6 boxes complete. His predicted
  cells equal his Jin-only build's (`394f745c…`).
- A draft claim that the first 18 sacrificed codes differed from Jin-alone's
  was checked and is false: they are the same 18, in order.
- Commands: `./invenv.sh ruff check tools tests research/experiments`
  (clean), `mypy` on the new scripts (clean), `./invenv.sh pytest -q tests`
  (161 passed).

Conclusion: **CONFIRMED (M4)**, D-028.

Next action: write up M5 (`RE-005`); it is outline-only, so it needs "Write
up M5" first.

## 2026-11-03 — M5 tasks written up

Action: wrote Phase J in `TASKS.md` from the playbook's Phase 3 (MSHvSF
`RE-041`-`RE-047`: census, roster, pairing, capacity, build, regression),
re-anchored on story dialogue. Tasks: `RE-005` (census and roster),
`WIN-001` (is there a win-quote surface?), `PAIR-003`, `CAP-001` (capacity
and the trade-off decision), the gate extension, `RE-008` (roster image).
`RE-005`'s outline row is replaced.

Survey (an estimate, scratch extension of `EXP-0027/candidates.py` to lists
0-5): 404 story boxes; 551 distinct pairs (Jin + Santana 408), so about 216
sacrificed codes under the current rule; 23,812 line bytes needed against
20,720 in the pilots' own unshared lines, before dead ending lines; no box
over 3 rows. Not evidence; `RE-005` and `CAP-001` measure it.

Next action: `RE-005` or `WIN-001` (both `READY`).

## 2026-11-03 — WIN-001 in progress (EXP-0031, paused)

Action: `EXP-0031/loads.py` logs CD Play Disc commands (CR1 `0x10xx`; FAD
when bit `0x80` is set, else track and index) and scene posts from a state.
Validated from 4138: `STG0AS.BIN` at FAD `0x58A0`, `KANJI.BIN` at `0x1342`
(EXP-0018). Runs from REF-005 states, no input:
- **Win** (12788, 3,000 frames): `STG0AS.BIN` reloads, demo files, scenes 1
  and 2 posted (post-fight and next pre-fight dialogue), next stage. Screens:
  bonus tally, loading, story boxes, VS screen. No `VICTORY.BIN`.
- **Loss** (23142, 3,000): `CONTI_0.BIN`, continue countdown, game over,
  `OPDEMO.BIN`. No `VICTORY.BIN`.
- **Attract** (25772, 12,000): intro, ranking, Capcom logo, title, two demo
  fights (stages 00 and 01). No `VICTORY.BIN`.
- **Static:** in the game's file table (`0x060DCB98`) `VICTORY.BIN` is entry
  318, request `0x140` (`STG0AS.BIN` `0x124`). A load script of (handler,
  argument) pairs at `0x0604C1A0`-`0x0604C3A0` has a sequence at `0x0604C320`:
  `VICTORY.BIN`, `VRAM00.DAT`, `VADEMC`-`VADEME.MAC`. Nothing refers to the
  sequence's address directly.
- **Versus mode** (cold boot, the user present; pad 2 bound in the scratch
  home: `drive.py` `KEYS_2`): Jin against Arieta, set-up screen, then
  `STG0AS.BIN` and stage `STG07.BIN` load. Stopped during the fight's load at
  the user's request: the watcher's A press every 1.5 s kept taking focus.
  User's words: "Please take a break as soon as possible. It's becoming
  impossible to use this computer because you keep switching focus".

Next action: when the user says, finish versus mode with RAM-only forcing (no
repeated key presses), then the arcade's readers. Nothing committed yet.

## 2026-11-03 — EXP-0031: versus win quotes (WIN-001)

Action: resumed with a watcher that forces the win by memory only (no key
presses during the fight). Cold boot into versus mode (18:19-18:35, the user
present): Jin against Arieta, both Blodia; fight to time-out. Then matched
the arcade table's slots past 493 to Saturn lines (`extra_slots.py`).

Result:
- After the versus win: `VICTORY.BIN`, then `KANJI.BIN`; a `VICTORY!` screen
  with Jin's portrait and Saturn line 959; then an English `RESULT` tally.
- The arcade tables have 624 pointers; slots 494-623 follow Saturn lines
  from 899 (slot k = line k + 405; 79 exact matches); line 959 is slot 558;
  the US set has English in all 130 slots. D-011 corrected.
- Not traced: the arcade reader of slots 494-623 and how a quote is chosen.
  The US slot 558 is worded differently from the Japanese.
- Commands: `ruff check`, `mypy` on the new scripts (clean).

Conclusion: **CONFIRMED**, D-029. A separate surface exists.

Question, verbatim: "Versus mode has a separate win-quote screen (VICTORY.BIN: the winner's portrait and a one-line Japanese quote, e.g. Saturn line 959). The arcade tables hold them in slots 494-623 (slot k = Saturn line k+405), with US English in all 130 slots. Should versus win quotes join M5?"
Answer, verbatim: "Add to M5 (Recommended)"

Next action: `RE-005` (`READY`); `WIN-002` is added to Phase J.


## 2026-11-04 — EXP-0032: how a win quote is picked, and the pairing (WIN-002)

Action: read `VICTORY.BIN`'s code and tables, and the arcade's
(`cybotsu`, MAME `dasm`); traced the arcade's quote in a 2-player match
with write taps (`create_tap.lua`, `post_tap.lua`, `logwrites`); forced
three table entries in MAME; one Saturn versus cold boot (09:52-10:07, the
user present; asked first, answer verbatim: "Yes, go ahead (Recommended)")
with menu presses only, the win held in RAM, a halt at the selector, and
three boxes forced from the saved state. Paired with `pair_quotes.py`.

Result:
- Saturn: `0x06060B46` picks (scene, byte) from `0x0606FAA0`[winner][random
  & 7] and posts list 9 (72 one-box scripts). The two player bytes it loads
  go to `0x06026F5E`, which does not read them (code only).
- Arcade: `0x6301C` picks from `0x630CE`[winner][2 x level + bit] (read
  through the decrypted program space; the raw ROM bytes there differ) and
  posts list 6 (48 scripts, the Saturn's scenes 0-47 box for slot).
- Halt: R0 & 7 = 7 for Jin; the replay showed box 560 (line 961). Forced
  boxes 599, 558, 556 showed lines 1004, 959, 957. MAME entries 2, 5, 7 gave
  slots 599, 558, 560.
- The US set has one English record per pilot and level: 46 boxes, 24
  records (22 pairs of boxes share one).
- VS captions: `STG0AS.BIN` `0x0606CAE8` shows box `0x0609CC22`[pilot x 10
  + stage]; the arcade's `0x62D4C` uses the same table (code only).
- D-029's "slot k = line k + 405" is wrong past slot 494 (558 is line 959);
  corrected. Box for slot holds.

Failed or corrected along the way (do not retry):
- The arcade queue is at A5 - `0x6DCC` = `0xFF1234`, not `0xFF9234`; a tap
  there logged nothing.
- MAME's Lua state names the stack pointer `SP` (and `USP`), not `A7`; a
  tap that read `A7` failed without an error message.
- MAME's debugger reads `d0=10` as hex `0x10`; the first forced runs showed
  Santana's slots 569 and 571.
- Runs sharing one MAME NVRAM folder are not repeatable (the quote moved
  from frame 5521 to 5260); each run now copies a fixed base.
- The agent refuses `savestate` while halted at a breakpoint; resume, then
  save. That state is after the selection, so the Saturn forcing rewrites
  the script's box word, not the table entry.
- The scene-task byte cannot be forced from that state: the task had read
  it and was waiting.
- The first Start press came late (frame 4418), in the attract demo; a
  press on the title's fade-in was ignored. Three extra presses in all.

Commands: `ruff format`, `ruff check`, `mypy` on `EXP-0032/*.py` (clean);
`pytest -q`: 161 passed.

Conclusion: **CONFIRMED** (D-030) except the arcade's level meaning, the 7
`unmapped` boxes and the caption boxes (SUPPORTED). `WIN-002` is `DONE`.

Next action: `RE-005` (`READY`). The gate extension gains one question: what
the two Japanese quotes of a level show.

## 2026-11-04 — EXP-0033: census of the pilot lists; the M5 roster (RE-005)

Action: wrote `census.py` (all 11 lists from the game's tables and posts)
and `roster.py`; ran 8 cold boots of the untouched image to the first scene
posts with different pilot select moves (10:17-10:54, the user present;
answers, verbatim: "Yes, go ahead (Recommended)", then "Yes, 2 more
(Recommended)" twice); asked the roster question.

Result:
- Blocks 3, 4, 5 and 6 open as predicted when their pilot is chosen; the
  stage byte starts at 9 x list (D-031). Routes: right x1-x5 Mary, Santana,
  Gawaine, Bao and Mao, Arieta; left x1 list 6 (Devilot by the name art),
  left x2 list 8 (Shade).
- Lists 0-5: 404 story boxes, 756 lines, all paired except Mary's line 258.
- List 10 is speaker-name boxes only; its arcade twin is posted at
  `0x6319C`; no Saturn post found (literal search).

Failed or corrected along the way (do not retry):
- `play_route.py` pressed the first move before the select cursor appeared
  (run `right3` chose Santana with 3 moves); now `--select-wait 10`.
- Moves 1 s apart after the third were lost while a portrait loaded (runs
  `right4`, `right5` stayed on Gawaine); 3 s apart they work
  (`--move-wait 3`).
- `box_list.py` raised an error on list 10 (no later list bounds it); it now
  ends at the list table. Its scan past a script's `0xE000` put box 0 into
  list 10; `census.py` reads scripts to `0xE000` for sharing.
- `left2` (list 8) logged 0 and 1 first, not block 8's 21. Not followed.

Question, verbatim: "Which pilots make up the M5 roster? The six arcade pilots (Jin, Santana, Mary, Arieta, Gawaine, Bao and Mao) have 404 story boxes plus 46 win-quote boxes, all with official arcade English except Mary's line 258. The three Saturn-only pilots (lists 6-8, e.g. Devilot and Shade) add 339 story boxes with no official English and are special cases under rule 24."
Answer, verbatim: "Six arcade pilots (Recommended)"

Commands: `ruff format`, `ruff check`, `mypy` on the changed scripts
(clean); `pytest -q` (see below).

Conclusion: **CONFIRMED**, D-031. `RE-005` is `DONE`; `PAIR-003` and
`CAP-001` are `READY`.

Next action: `PAIR-003` (pair Mary, Arieta, Gawaine, Bao and Mao) or
`CAP-001`; the user picks.

## 2026-11-04 — EXP-0034: the roster's code budget; the user's trade-off (CAP-001)

Action: estimate pairings for pilots 2-5 (`pair_pilot.py`, slot for slot);
the compiler's budget; `capacity.py` over the story and win quotes for
options (a) the current rule, (b) ranking by shown lines that stay
Japanese, (c) 33 more codes, (d) a half-cell indent or capitals; the
question; then `--indent` and `--rank staying` in `dialogue.py`.

Result:
- 556 pairs, 335 free codes. (a) 221 codes, 133 lines touched; (b) 221,
  106; indent + (b) 152, 51; capitals + (b) 115, 16; (c) an untested upper
  bound (with indent and (b): 119, 20).
- The English fits `STG0AS.BIN`'s room (23,812 of 25,272 bytes). The quotes
  need 4 bytes more than their own `VICTORY.BIN` lines; that file's story
  copy is unshown there (code only).
- Option (c) needs the data after the table moved (2 literals, 9 pointers)
  in three files; not tried.

Question, verbatim: "M5 needs 556 pair glyphs for the six pilots' stories and win quotes (an estimate until PAIR-003), but only 335 codes are free. The rest must take over codes of rare Japanese characters, and Japanese lines that stay after M5 (mostly the Saturn-only pilots', plus a few roster endings and VS captions) will show a wrong glyph wherever one is used. This lasts, since that Japanese stays Japanese. Which trade-off?"
Answer, verbatim: "Indent + rank (Recommended)"

Regression: defaults rebuilt Jin + Santana and Jin to `re007` and `re003`
byte for byte (builds deleted). With the new options the compiler's story
budget is 480 pairs, 145 codes, 52 lines.

Commands: `ruff format`, `ruff check`, `mypy tools/ tests/` and the new script (clean); `pytest -q`: 164 passed.

Conclusion: `CAP-001` is `DONE`. Numbers are estimates until `PAIR-003`.

Next action: `PAIR-003` (`READY`).

## 2026-11-04 — EXP-0035: Mary, Arieta, Gawaine, and Bao and Mao paired (PAIR-003)

Action: `pair_pilot.py` for lists 2-5; `check_lines.py` (each line against
its own slot's Japanese line); MAME forced scenes (2 per pilot, headless,
fixed NVRAM); Saturn forced scenes on the untouched image from state 4138
(`force_check.py --control`, `japanese_check.py`). No cold boots, no keys.

Result:
- Story scripts match the arcade's for all four pilots; only ending scenes
  differ.
- 519 lines: 489 exact and 30 edited against their own slot. The
  irregular REF-006 labels were lines shared with earlier boxes and Mary's
  short line 258 (punctuation edit). No new translation is needed.
- MAME slots equal the Saturn boxes in all eight scenes; Saturn cells
  757/757.
- The pairs equal `CAP-001`'s estimate.

Corrected: D-011 and RE-005's coverage register listed line 258 as
Saturn-only; it is slot 140's edited line (D-032).

Commands: `ruff format`, `ruff check`, `mypy` on `check_lines.py` (clean);
`pytest -q`: 164 passed.

Conclusion: **CONFIRMED**, D-032. `PAIR-003` is `DONE`.

Next action: the `GATE-TRANSLATION` extension for the roster (the user's
GO), then `RE-008`.

## 2026-11-04 — GATE-TRANSLATION extended to the M5 roster

Action: put the roster's gate to the user after `PAIR-003`, `WIN-002` and
`CAP-001`.

Question, verbatim: "Roster GO: put the official US arcade English, as paired and unchanged, on all six pilots' story (404 boxes) and win quotes (46 boxes), drawn as pair glyphs with the indent + rank rule? The estimate is 152 borrowed font codes, touching 51 Japanese lines that stay (43 Saturn-only, 3 roster endings, 5 VS captions). The build stops and asks again if it needs more than the cap."
Answer, verbatim: "GO, cap 160 (Recommended)"

Question, verbatim: "The US arcade has one English win quote per pilot and level, so 22 pairs of different Japanese quotes share one English line. On the Saturn, which shows when either quote of a pair is picked?"
Answer, verbatim: "Shared official line (Recommended)"

Result: the gate covers lists 0-5's story and win quotes in official US
arcade English, no new translations, up to 160 sacrificed codes with
`--indent --rank staying`. Recorded in `TASKS.md` (gate block) and
`docs/localization_policy.md`. `RE-008` is `READY`.

Next action: `RE-008` (the roster image), which needs cold boots with the
user present.

## 2026-11-04 — EXP-0036: M5, the roster image (RE-008)

Action: extended `dialogue.py` (`--roster`, `--quotes`, `VICTORY.BIN`,
`changes.json`); built the roster image twice; untouched-byte, sector and
source checks; forced all 114 story scenes on the built image (unattended,
12:24-14:22) and controls on the original; a Saturn-only scene; one versus
cold boot (all quotes forced from its selector state); a cold boot per
roster pilot with no keys during fights (14:45-16:53, the user present;
"Yes, at ~14:30 (Recommended)", "Yes, rerun both (Recommended)").

Result:
- 487 pairs, 152 codes, 51 lines touched; two builds identical; every
  changed byte accounted for; 102 changed sectors, all valid.
- Forced: 404/404 story boxes (10,529 cells), 46/46 quotes (615 with box
  1023); controls 0/905; list 6's box 896 shows its pair glyph as recorded.
- Play: five pilots to stage 2 of their groups; Mary to her stage 1.
- The old references still reproduce byte for byte.

Failed or corrected along the way (do not retry):
- `--steps 100` is too few for Jin's scene 9 (8 boxes); 160 shows box 40.
- A `quote_boxes` field in every record changed the old builds' records; now
  only quote builds write it, and the summary's row counts are the story's.
- `play-santana` lost an A at machine select; `play_route.py` now presses A
  again if no scene posts within 45 s (at most twice).
- Mary's stage 19 is a cockpit stage (step 22): no input means game over.
  The 20-minute cap had hidden this in the first run.

Question, verbatim: "Five roster pilots reached stage 2 of their groups in cold boots with their English boxes shown. Mary reached only her stage 1 (twice): stage 19 is a cockpit stage, not a fight, and with no input it ends in GAME OVER, so the RAM win doesn't apply there. Her English showed in play in 5 scenes (stages 18-19), and every one of her 69 boxes passed the forced check. How should RE-008 close?"
Answer, verbatim: "Accept, record why (Recommended)"

Commands: `ruff format`, `ruff check`, `mypy tools/ tests/` and the new
scripts (clean); `pytest -q`: 164 passed.

Conclusion: **CONFIRMED**, D-033. M5 is reached.

Next action: write up M6 (endings) when the user asks; nothing past M5
starts before that.


## 2026-11-04 — M6 tasks written up (Phase K)

Action: the user asked "Write up M6". Wrote `END-001`-`END-005` in
`TASKS.md` (Phase K): reach Jin's ending and list its surfaces; renderers
and fonts; text in RAM and on disc and what selects the ending; the
arcade's ending English; pairing Jin's ending (closes M6). The outline rows
became `END-010` (M7) and `END-020` (M8). No experiment was run.

Next action: `END-001` (`READY`), when the user starts it; it needs cold
boots with the user present.


## 2026-11-04 — END-001: Jin's ending reached by RAM writes (EXP-0037)

Action: the user said "Start END-001". From REF-005 state 4138, no cold
boot and no key: `research/experiments/EXP-0037/ending_route.py` writes the
progress bytes, holds the vitality through the last fight (time-out win)
and logs disc reads, scene posts (with callers), `END.BIN` box calls, polls,
screenshots and glyph cells. Runs under `local/end001/`.

Failed or corrected along the way (do not retry):
- `route1`: stage byte `0x060CFF88` = 8 after the stage start. Stage 8's
  scenes and fight played, but the win went to stage 1: the stage start
  sets the stage from `0x0607B440`[pilot x 10 + index] and a win adds 1 to
  the index (record + `0x2E3`, `0x06018EE6`).
- `route2`: index 8 too. The win went to index 9 (entry 0) and Jin's story
  restarted; the opponent was still index 0's (Shade, machine 5), set at
  arcade start by `0x06027834` from `0x0604B5C0`/`0x0604B650`.
- `route3`: opponent written (pilot 8, machine 11). Still back to stage 0:
  the win only ends the story via `0x060CFF04` (`0x060185A2`), which needs
  the last-fight flag `0x060CFF07`, set by `0x06027950` when the opponent
  row's next entry is negative.
- `route5`/`route6`: flag written: the ending played (`END.BIN` scenes
  16-19). But the stage was written after one stage-0 step had run, so
  scene 21 was posted alongside scene 14. `run8` (M5 image) drew the two
  scenes' English over each other and stalled: an artifact of the route,
  not an M5 defect (the final route plays those scenes cleanly on M5).
- A second Mednafen on the same silent home is refused (lockfile);
  `MEDNAFEN_ALLOWMULTI=1` runs two at once.
- The first glyph comparison used each box's last 50-frame dump and failed
  its own untouched-vs-untouched control (boxes caught mid-typing); the
  final check matches each dump against predicted cells.
- Checkpoints saved while running land a few frames after the poll; two
  runs' checkpoints are different instants (route5/6 at the same frame had
  identical memory; final A/B did not land on the same frame).

Final route (writes at frame 318, before the stage start): index 8, player
2 `08 0B 0B 0B`, opponent word `0008`, flag `01`; the game sets stage 8
itself. Runs A and B: identical posts, 96 disc reads and 39 box calls,
frame for frame. Checkpoint A, frame 16503, `7e314718…64f2`. Run C from it
reproduces A's 43 reads and 39 box calls, 16,317 frames earlier.

Result:
- Mode 5 (`0x06017CAE`) loads `END.BIN`; scenes 16-19 show boxes 408-422,
  493, 601, 605, 1072 from `END.BIN`'s table `0x060817B4`; scene 20 (box
  550) is not posted on this route.
- Japanese surfaces: ending dialogue boxes, narration, captions with
  speaker names, cast-roll names, one QSound line. Credits English.
- M5 image: predicted one pair glyph (line 770); the original glyph shows.
  `SE.DAT` (read before scene 16) holds `KANJI.BIN` at `0x40000`; the
  ending reads no `KANJI.BIN`. SUPPORTED: the ending's font is `SE.DAT`'s
  copy (`END-002` to confirm).

Conclusion: **CONFIRMED**, D-034. `END-001` is done; `END-002`, `END-003`,
`END-004` are `READY`.

## 2026-11-05 — END-002: how Jin's ending draws each surface (EXP-0038)

Action: the user said "Start END-002". Every run starts from a saved state
(the END-001 checkpoint, or states the control run saved at the cast roll,
credits, thank-you and QSound screens); no cold boot, no key. One change per
run, each against a no-change control. Runs under `local/end002/`.

- Probe image `build/end002/sedat_probe/`: glyph 535 (line 752's first
  character) replaced by a solid block in `SE.DAT`'s font copy only; one
  sector changed.
- `font` run: only box 408's cell 0 differs from the control (glyph 535 to
  the probe block, while the box is open); the screen differs only in that
  16×16 character. VDP2 VRAM equals `SE.DAT` in full (control) and the
  edited `SE.DAT` (probe) during the ending scenes.
- `line` run: line 752's first code written in RAM a frame before box 408
  opens (`8DA1` to `8E9F`): only that cell changes, to glyph 600.
- Cast roll, credits, thank-you, QSound: layers and sources found from VDP2
  registers, VRAM dumps and work-RAM dumps. One VRAM or RAM change each
  removed exactly the predicted item.

Failed or corrected along the way (do not retry):
- Same-frame comparison of cell dumps between runs: poll frames drift by a
  few frames between runs even though game events do not, so only some
  polls align. Boxes are also compared by their last dump while open.
- The name sprites' pixels are not in any file as raw bytes; they are
  decoded each frame by `0x0601446C` from `KEND_1.BIN` in RAM.
- Zeroing 16 command bytes where the decoder was writing Arieta's name slot
  changed nothing on screen at 2 frames. At 30 frames her katakana, and
  everything decoded after it in the same call (Gawaine's names, two
  portraits), had changed. The write breakpoint shows where the stream was
  when it reached the slot, not where the call began; one call decodes
  several sprites.
- In zsh a `$Q` holding several `--fill` arguments is passed as one word;
  use `${=Q}`.

Result: **CONFIRMED**, D-035.
- The ending's dialogue font is `SE.DAT`'s copy of `KANJI.BIN`.
- The cast-roll names are images from `KEND_1.BIN` (SUPPORTED: whole-name
  images; format not decoded).
- The credits use `FIX.BIN`.
- The QSound line is `QSD.PIX` pixels.

The win tally, game over and ranking are not ending surfaces (shared UI,
English) and were not traced. `END-002` is done; `END-003`, `END-004` are
`READY`; `END-005` waits on them.

Commands: `ruff check .` and `ruff format --check .` (clean, 178 files), `mypy tools tests` and the EXP-0038 scripts (clean, 66 files), `pytest -q`: 164 passed.

## 2026-11-05 — END-003: ending text in RAM and on disc; what selects it (EXP-0039)

Action: the user said "Start END-003". Static reading of `END.BIN` and the
resident round-end code; five runs from the END-001 checkpoint (no cold
boot, no key). Runs under `local/end003/`.

Result:
- The last-fight round end copies the winner's pilot byte to `0x060CFF7E`.
  `END.BIN` dispatches on it (`0x060775B4`, 9 lists), and each list's step
  routines post fixed scenes with R4 = the list.
- Forcing 1 into that byte, or into player 1's pilot byte before the copy,
  played Santana's ending (posts 16-22, R4 = 1, 22 of 22 boxes as
  predicted).
- `data/text/ending_posts.json` replaces `ending_scenes_by_number`, which
  listed scenes never posted:
  - Jin's 20;
  - Mary's 17 and 18;
  - Bao and Mao's 20;
  - list 6's 17.
- `KEND.BIN` (credits text, ASCII), `KEND_1.BIN` and `QSD.PIX` are loaded
  raw by the CD copy loop. RAM markers in `KEND.BIN`'s strings showed on
  screen.

Failed or corrected along the way (do not retry):
- EXP-0033 read the post's R5 only and concluded the posts name no list;
  R4 is the list number.
- `scene_boxes` first listed boxes a script only closes. These are carried
  over from the previous scene, so they do not belong to it. Only opened
  boxes are listed now (Jin's then match END-001 exactly).
- The first `santana` and `pilot` runs crashed: an on-hit action is logged
  as an event line without `PC`. Action lines are now filtered and logged
  apart.
- The first thank-you marker (`0x06063240`) was in `SPECIAL THANKS`, not in
  `THANK YOU FOR PLAYING!` (`KEND.BIN` holds both; the latter at `0x34EC`).
  It showed as `SPECIAL THINKS`; a second run marked the right string.
- In zsh, a failed `&&` chain left two runs unstarted once; start
  background runs with `;`.

Conclusion: **CONFIRMED**, D-036. `END-003` is done; `END-004` is `READY`;
`END-005` waits on it.

Commands: `ruff check .` and `ruff format --check .` (clean, 182 files),
`mypy tools tests` and the EXP-0039 scripts (clean, 65 files), `pytest -q`:
164 passed; `end_scenes.py` reproduces `data/text/ending_posts.json` byte
for byte.

## 2026-11-05 — END-004: the arcade's English for Jin's ending (EXP-0040)

Action: the user said "Start END-004". Static reading of both arcade
sets' disassemblies (MAME `debug dasm`; `cybotsj`'s made here), then
headless MAME 0.289 routes from fixed NVRAM copies, menu presses only. Runs
under `local/end004/mame/`.

Result:
- The arcade mirrors the Saturn:
  - round-end flag `0xFFEA28` (set from `0xFFEA2B`);
  - the winner's pilot copied to the ending number `0xFFEB2C`;
  - 6 ending routines (`0xE496`), with the same post form.
- One breakpoint at `0xDAE4` (P1 2 wins, P2 0, flag) reaches Jin's ending
  in `cybotsu` (ending number at 9259) and `cybotsj` (9436). Repeat runs
  are byte-identical.
- The story readers read the ending slots from the English (U) or
  Japanese (J) table. No table is read after scene 19.
- Scripts are equal in both sets. Against the Saturn:
  - box 1072 is added;
  - speaker names are the slot − 9;
  - Mary's 17-18 and Bao and Mao's 20 are arcade-only.
- The US cast roll shows Latin names only. The arcade ending has no QSound
  notice.

Failed or corrected along the way (do not retry):
- MAME refuses a read tap with an even end address. The error cancelled
  every later tap installed on that frame, so only the first tap logged.
  Use odd ends.
- `cybotsj`'s first taps covered 494 Japanese pointers (D-009). Speaker
  names 610/614 went unseen, and it looked as if `cybotsj` read no name
  slots. The table has 624 pointers. D-009 now carries a correction.
- The dispatch table read from `cybotsu-maincpu.bin` came out as garbage:
  PC-relative reads go through the decrypted opcode space. The words are
  now taken from the disassembly.
- Searching the encrypted `cybotsu-maincpu.bin` for code bytes fails; use
  the disassembly, or `cybotsud` for a quick search.

Conclusion: **CONFIRMED**, D-037. `END-004` is done; `END-005` is `READY`.

Commands: `ruff check .` and `ruff format --check .` (clean, 184 files),
`mypy tools tests` and the EXP-0040 script (clean, 63 files), `pytest -q`:
164 passed; `compare_scripts.py` reproduces `data/arcade/ending_scripts.json`
byte for byte.

## 2026-11-05 — END-005: Jin's ending paired with the arcade English (EXP-0041)

Hypothesis: each Saturn box of Jin's ending, less the blank 1072, has the
arcade slot at the same position of the same scene script. The arcade
shows that slot's English while the Saturn shows the box. Only the image
surfaces lack English, and the English fits the ending's own table and
box limits.

Method:
- `pair_ending.py` reads `ending_posts.json` (D-036) and
  `ending_scripts.json` (D-037), and labels each line against `cybotsj`.
- `capacity.py` measures rows, cells, pairs, codes and room as CAP-001 did.
- On screen: frames of the recorded forced runs (`local/end002/control`,
  `local/end004/mame/route-u`), picked by box open frames and slot reads,
  reviewed side by side.
- No emulator run, no key.

Result:
- 31 units: 18 paired (15 exact, 3 edited with the same wording) and 13
  without a counterpart (box 1072 twice, 10 cast-name images, the QSound
  line).
- Five pairs reviewed on screen. Some US English is a free localization
  (493, 416, 419).
- Capacity: 3 rows and 46 cells at most; 179 pairs, or 160 with the indent,
  against 335 free codes; rows need 872-880 bytes against 828 in Jin's own
  lines.
- The speaker-name boxes 605 and 601 are also posted by lists 3, 4 and 8.
- The user decided the two image units: "Hide, as US arcade (Recommended)"
  and "Erase the line (Recommended)".

Corrected along the way (do not retry):
- The first pairing file carried the cast roll's on-screen Latin names
  (game text). They were replaced by the project's own labels for each
  entry.
- The name and caption cell count was first summed as name + longest
  caption (35). A name stays open over its captions (605 over 416-418,
  601 over 419-420), so the real maximum is 33.

Conclusion: **CONFIRMED**, D-038. `END-005` is done and M6 is closed.
`END-010` is written up and `BLOCKED` on the gate extension (the user's GO).

Commands: `ruff check .` and `ruff format --check .` (clean, 187 files),
`mypy tools tests` and the EXP-0041 scripts (clean, 64 files), `pytest -q`:
164 passed. Both data files reproduce byte for byte (`6e9f2988…`,
`985946d5…`).

## 2026-11-05 — SESSION: local data backed up to the homelab, unused data deleted

User request (verbatim): "Please take a moment to back up any data to the
homelab the same way that XvSF and MSHvSF did and delete any data not
currently in use. I'm low on disk space." Ignored paths only; no tracked
game file changed.

- **Backup:** `local/` copied to the homelab archive
  `/mnt/HD/Seagate22TB/filebrowser-inbox/Archives/Cyberbots-Saturn-EN`
  (File Browser `/Inbox/Archives/Cyberbots-Saturn-EN`): 86,298 files,
  1,791,645,194 bytes, all 189 save states, with `MANIFEST.tsv` (path,
  bytes, SHA-256), `SYMLINKS.tsv` and a README holding the restore
  commands. Left out: the source image (`disc_images/`), `extracted/`, the
  arcade zips (`arcade/`), the four ROM program images
  `ref003/*-maincpu.bin`, the BIOS (`mednafen/firmware/`) and the 4
  `firmware` links (in `SYMLINKS.tsv`). No file in it equals a BIOS file.
  Server-side `sha256sum -c` passed for every row; no symlinks; owner and
  modes as the Inbox; Plex health passed. Access and logging followed
  `remote_server_maintenance` (its research_log entry of 2026-11-05).
- **Kept on the Mac (in use by END-010, the tools or the regression):**
  `disc_images`, `extracted`, `arcade`, `ref003`, `mame_src`,
  `mame_arcade`, the five Mednafen homes, `downloads` (Mednafen tarball),
  `checkpoints`, `layout001` (the arcade font), `cap001`, `end001` (the
  END-001 checkpoint), `end002` (`control/route.json`), `end004`, `ref005`
  (session states) and `win002` (disassembly); `research/memory_dumps`
  (`mcs_extract` validation).
- **Deleted after the check:**
  - from `local/`, 42 finished-task entries (1.07 GiB): `dbg001`-`dbg004`,
    `disc001`, `disc002`, `emu003`, `emu004`, `emu006`, `emu007`, `emu021`,
    `end003`, `env007`, `font001`, `font002`, `logs`, `pair001`-`pair003`,
    `re001`-`re008`, `ref001`, `ref004`, `ref007`, `ref008`, `win001` and
    nine loose logs. All are in the archive.
  - the M5 build images `build/re007/js` and `build/re008/roster`
    (rebuild: the `rebuild` command in `data/regression/re007_jin_santana.json`
    and `re008_roster.json`; standing permission for finished images).
  - the Mednafen source trees and objects (`vendor/mednafen/src`,
    `src-agent`, and everything in `build` and `build-agent` except the two
    executables). Both executables kept in place, hashes unchanged
    (`077ac658…669f` stock, `2fc3d547…aaf` agent, as recorded). Rebuild
    from `local/downloads/mednafen-1.32.1/mednafen-1.32.1.tar.xz`
    (`docs/mednafen.md`, `vendor/mednafen/README.md`; a rebuilt agent
    binary needs V1-V4 again).
- **Disk:** `local/` 2.5 GB → 1.4 GB, `build/` 1.1 GB → 1.6 MB, `vendor/`
  595 MB → 41 MB; free space 8.7 GiB → 12 GiB.

Checks: `./invenv.sh python -m pytest -q`: 164 passed. Both EXP-0041 data
files reproduce byte for byte from the kept inputs; the END-001 checkpoint
and `end002/control/route.json` are in place; the stock executable starts.

## 2026-11-05 — GATE-TRANSLATION extended to Jin's ending

User request (verbatim): "Let's begin the gate GO." Shown: the `END-005`
pairing and capacity (`EXP-0041`, D-038) and the shared speaker-name boxes.
No emulator run, no build.

- Asked: "GATE-TRANSLATION extension for Jin's ending: may the official US arcade English go on the disc as paired by END-005, unchanged and drawn in pair glyphs? That means 18 dialogue units (30 lines), the cast roll's Japanese names hidden and the QSound line erased, as you chose. No Japanese glyph is expected to be sacrificed (160-179 pairs needed, 335 free codes in the ending's own table); if one is needed, the build stops and asks."
  Answer, verbatim: "GO (Recommended)"
- Asked: "In Jin's ending, two speaker-name boxes (Gawaine's and Jin's names before a caption) are also shown in three other pilots' endings (lists 3, 4 and 8). Translating them turns those names English in the other endings too, next to Japanese text, until all endings are done (M8). The alternative gives Jin's ending its own copies of the two name boxes, which changes the ending's script and uses more of the scarce room (Jin's own lines are already 44 bytes short). Which?"
  Answer, verbatim: "Share, English everywhere (Recommended)"

Result: `END-010` is `READY` (not started). Boxes 605 and 601 are
translated in place; no sacrificed code is approved, so the build stops and
asks if it needs one. Recorded in `TASKS.md` (the gate block and
`END-010`) and `docs/localization_policy.md` (decisions and gate tables;
the two `END-005` decisions were added there too, as they were missing).

## 2026-11-05 — END-010: Jin's ending in English (M7) (EXP-0042 to EXP-0045)

User request (verbatim): "Start END-010". Forced runs from saved states in
the silent home; one cold boot with the user present and asked first.

Decisions (verbatim, also in `TASKS.md` and `docs/localization_policy.md`):
- the cast roll is the same in every ending: "Hide in every ending
  (Recommended)";
- the cold boot: "Yes, run it now (Recommended)";
- three boxes finish typing just before they close: "Accept now, follow-up
  task (Recommended)" (`END-011`, `BACKLOG`).

Results:
- **EXP-0042 (D-039), the room.** 1,591 lines no ending box shows (18 spans,
  43,304 bytes), filled with a marker. Read breakpoints log no hit while
  `END.BIN` is resident, in Jin's and Santana's endings; a positive control
  on line 752 hits at the character reader. The Santana control run was
  fetched back from the homelab archive (all 1,146 files matched).
- **EXP-0043 (D-041), the QSound line.** Rows 180-190, x 89-300 of
  `QSD.PIX` set to 255; only the line changes on screen.
- **EXP-0044 (D-040), the cast names.**
  - Traced from the VDP1 command to the main program's sprite-part routine
    `0x060113F0`, bank 16 in `KEND.BIN`, `KEND_0.BIN` and `KEND_1.BIN`.
  - Size 0 skips a part. The roll's even frames `0x1B6`-`0x1C8` are the
    Japanese names (16 records).
  - From a pre-roll state, zeroing them hides only the names.
- **EXP-0045 (D-042), the build.** `tools.text.dialogue --ending`:
  - two builds identical; RE-008's story hashes kept;
  - 179 pairs on unused codes;
  - 158 sectors changed, all valid;
  - live: all 18 units drawn, Gawaine's ending with English names and his
    Japanese boxes;
  - play: scenes 21 and 0 in English.

Corrected along the way (do not retry):
- **The room count.** `EXP-0041`'s 44,124 bytes counted the ASCII file names
  after line 1850 (`KANJI.BIN`, `SCR00.PIX`, ...), which the game does
  read. The room now counts only lines a box record points to.
- **Read hits outside `END.BIN`.** The first look at the room runs counted
  14,499 hits. They are reads of other files at the same addresses: before
  `END.BIN` loads, and inside `KEND.BIN` after it loads (`0x06060000`-
  `0x0606C8A7`).
- **EXP-0038's QSound test.** It zeroed the line with index 0, which is
  transparent: the layer behind showed through. It also cut the logo's edge
  and missed row 190. Its README's `0x200B4` should read `0x20000` + 180 ×
  512 + 84. The disc change uses index 255.
- **Screenshot comparisons.** Poll frames drift by a frame between runs,
  and one frame already changes animated scenes, so screenshots were not
  evidence for the room. The read breakpoints and the cell checks were.
- **`SE.DAT` change ranges.** First recorded as 128-byte blocks per glyph.
  A glyph is four 32-byte tiles (`tools.font.kanji.tiles`), so 9,044 bytes
  fell outside; the ranges are now per tile.
- **The record derivation hung.** It used the cache-through part pointer
  (`0x20200000`) unmasked; the address is masked now.
- **Box 420 short (30 of 31).** The 11-frame polls missed the last glyph;
  1-frame polls show it drawn 4 frames before the box closes. That timing
  is END-011.
- **The cold boot.** Two retry key presses were not sent because Mednafen
  was not in front; the run did not need them.

Commands: in each EXP README. `ruff check .`, `ruff format --check .`,
`mypy tools tests`, `pytest -q`: see the closeout below.

## 2026-11-05 — M8 tasks written up (Phase M)

User request (verbatim): "Write up M8". Documentation only; no run.

- Phase M in `TASKS.md`:
  - `END-020`: survey the roster endings' surfaces, lists 1-5, forced
    from the END-001 checkpoint and in headless MAME;
  - `END-021`: pair lists 1-5 with a generalized `tools/text/ending_pairing.py`;
  - `END-022`: capacity of all six endings together;
  - the gate extension;
  - `END-023`: the M8 image, coverage register and play check.
- `END-011` (box timing) moves from `BACKLOG` to `READY` in M8's order:
  `END-022` and `END-023` use its hold rule.
- Facts gathered for the phase introduction, from `ending_posts.json` and
  `ending_scripts.json`:
  - 91 distinct roster boxes; 601, 605 and 1072 shared with lists 6-8;
  - 604, 606 and 607 shared between roster lists;
  - pairing cases to resolve: 608 ↔ 615 (list 5, scenes 18 and 28), 603
    (list 1, scene 22), and the arcade-only scenes (Mary 17-18, Bao and
    Mao 20).
- `END-020` and `END-011` are `READY`; nothing started.

## 2026-11-05 — END-020: the roster endings surveyed (EXP-0046)

User request (verbatim): "Start END-020". Forced Mednafen runs from the
END-001 checkpoint (five in parallel, silent home, no key), and headless
MAME; no cold boot.

- Saturn, lists 1-5: every list posts D-036's scenes. All Japanese before
  the cast roll is `END.BIN` boxes, and the post-dialogue screens are
  shared (roll, credits, thank-you screen, QSound notice).
- Arcade: the ending number set at `0xDBBC`/`0xDC12` (after the round end's
  copy) plays each list's ending. All 10 routes read their scripts' slots.
- `data/text/ending_surfaces.json`: observed box sequences, open and close
  frames, screenshot hashes, arcade slot reads.

Corrected (do not retry):
- **D-036's box lists are incomplete** (now D-043). EXP-0039's reader
  stopped each script at `0xE000`, but a posted script runs on into the
  next scenes. Mary's ending (one post) shows the arcade's scenes 17-18
  (440-447, names 602, 604, 610), and Bao and Mao's shows scene 20's 486.
  The Phase M introduction and `END-021` were corrected; the "Saturn never
  posts these scenes" row of `docs/known_unknowns.md` is answered.
- **A first "no box open" check** treated boxes with no logged close as
  open until the end, so it proved nothing. The standalone lines were
  matched to box windows by frame instead.
- **The first `cybotsu` list-3 MAME run** stayed in attract mode and its
  taps logged nothing; the rerun was normal. The cause is unknown (one in
  ten runs).

## 2026-11-05 — END-021: the roster endings paired (EXP-0047)

User request (verbatim): "Start END-021". Static; no emulator run.

- `tools/text/ending_pairing.py`:
  - aligns each list's observed openings (`ending_surfaces.json`) with the
    arcade's slot reads;
  - takes box kinds from the record header (dialogue `0000 008C`,
    narration `xx50` in the third word, caption `0x30` in the first, names
    otherwise).
  - List 0 reproduces Jin's units; only the evidence wording and the new
    `name_rule_slot` field differ.
- Lists 1-5: 102 text units, all with official English (63 exact, 39 with
  the same wording, agent-checked); no new translation. Pairing files in
  `data/translations/`.
- Cases:
  - 603: one extra Santana name opening, with official English;
  - 608: both twins, where the arcade shows 615 (Bao alone) but 617 has the
    same Japanese and its own English. 608 is added to the gate block.
- One pair per list reviewed side by side.

Notes:
- The scene-number surface labels of `EXP-0041` were Jin-specific. The
  header rule replaces them and gives the same labels for Jin.
- `jin_ending_pairing.json` is not regenerated: END-010's records cite its
  hash, and the tool reproduces its units.

## 2026-11-05 — END-011: ending box timing (EXP-0048)

User request (verbatim): "Start END-011". Forced runs from the END-001
checkpoint and saved states; no cold boot, no key.

Decision (verbatim, also in `TASKS.md` and the policy): "Faster typing +
move cues (Recommended)".

Results:
- `EAnn` waits for cue `nn` of the list's table (pointers `0x060879A0`).
  Jin's cue 2 at 540 closed box 409 60 frames later, and box 493 kept its
  close.
- `E2nn` sets typing frames per glyph: `E203` typed box 409 in 91 frames
  instead of 181.
- The script waits for each box's typing. Posts follow the box before a
  wait or the scene end, and each scene's music starts with its post.
- `tools/text/ending_timing.py` (`--retime`): on Jin's build, every post,
  track start and file load falls on the Japanese frames, and the cued
  English boxes hold 113-269 frames. Box 415 holds 31 (scene end, as in
  the Japanese).
- Dry runs on lists 1-5: smallest hold 45-86 frames; scene ends within 5
  frames.

Corrected along the way (do not retry):
- **The first cue write** went to `0x06067872` (code) instead of
  `0x06087872`; it had no effect. The table is at file `0x2786E`, so RAM
  `0x0608786E`.
- **"Posts never move" was wrong.** The first rule (3 frames a glyph
  everywhere) moved posts 17-19 by −21, −54 and −6 frames and the cast
  roll by −94 (`local/end011/live-jin`). The script waits for typing
  before its waits and scene ends. The rule now keeps those times.
- **The script walk stopped at the last opening**, so the last box's waits
  (box 422) were missed and the cast roll came 123 frames early
  (`live-jin2`). The walk now reads on to the timing words.
- **Runs joined by frame gaps** split Santana's 432-433 at a 14-frame
  `CA00` and left 433 a 20-frame hold. Runs are now joined by the script.
- **Arieta's 455** has its typing word two words back; the rule looks back
  up to three words.
- **Counting non-blank cells** to measure typing failed (the cell buffer
  keeps old glyphs); matching predicted cells works.

## 2026-11-05 — END-022: capacity of all roster endings (EXP-0049)

User request (verbatim): "Start END-022". Lists 6-8 forced from the
END-001 checkpoint (three in parallel, silent home, no key); the rest
static.

- Lists 6-8 show only their posted boxes and the shared cast roll
  (`data/text/ending_surfaces_others.json`; `survey.py --others`).
- 100 English boxes: 3 rows and 47 cells at most, and no row wider than the
  Saturn's own.
- Pairs: 330 with the indent (fits the 335 free codes), 388 as is (fits the
  930 codes no staying line uses).
- Room: 4,920-4,980 bytes needed; 4,232 in own lines, 42,844 in lines no
  list 0-8 shows.
- Options written for the gate: indent (Recommended), box 608 → 617
  (Recommended), the timing rule.

Corrected (do not retry): D-039's room included 16 lines Mary's and Bao and
Mao's run-on boxes show (806-819, 888, 1007). The room now excludes every
line any list 0-8 is seen to show; M7's rows were not in them (checked).
Survey: lists 6-8 load no `QSD.PIX` within the window for list 7, so the
survey's last file is now optional.

## 2026-11-05 — GATE-TRANSLATION extended to the roster endings

User request (verbatim): "Ask the gate GO". Four questions (verbatim in
`TASKS.md` and the policy). Answers, verbatim:
- "GO (Recommended)";
- "Indent, as the story (Recommended)";
- "Bao Mao: (Recommended)";
- "Accept the rule (Recommended)".

`END-023` is `READY`: lists 0-5 with the half-cell indent across the ending
rows, box 608 from slot 617, and `--retime` on every ending. Nothing built.

## 2026-11-05 — END-023: the M8 image, all roster endings in English (EXP-0050)

User request (verbatim): "Start END-023". Forced runs from saved states
(silent home, no key), one play-state run, and one cold boot with the user
present and asked first.

Decisions, verbatim (also in `TASKS.md` and the policy):
- "Add the one glyph (Recommended)", then, corrected because no invisible
  code was left, "Use M5's 153rd code (Recommended)";
- "Yes, run it now (Recommended)" (the cold boot).

Results:
- `ending.compile_endings` and `--endings`. END-011's build reproduces byte
  for byte with the refactored code.
- M8 build: 330 pairs, no `END.BIN` sacrifice; two builds identical; 202
  sectors valid. RE-008's files are unchanged except `KANJI.BIN`'s one
  glyph.
- All nine endings forced on the build: every box as expected; timing
  within 6 frames of the Japanese; cued holds of 42 frames or more.
- Arieta's ending from the REF-005 play state: 26/26 boxes. Cold boot:
  scenes 21 and 0 in English.

Faults found and fixed (do not retry):
- **Lists 6-8 draw with `KANJI.BIN`**, not `SE.DAT`. The shared names
  601/605 were garbled in list 8 from M7 on; END-010's shared-box check
  used list 4, which uses `SE.DAT`. They now take story codes, and one pair
  (": ") takes the 153rd sacrifice code.
  - Corrected along the way: an "invisible" code does not exist; M5's 152
    sacrifices took all 96 zero-visible-use codes.
  - The row variants of the two names are now chosen jointly (one at a time
    they needed two codes).
- **Typing spends time on spaces**: Arieta's 455 (3 full-width spaces) put
  her scene 27 23 frames early. The M8 build counts every code.
- **`check_live` expected a glyph for `0x2020`.** It draws none, so the
  boxes of lists 6-8 only seemed short.
- **`EXP-0050/ending_route.py` crashed** on the on-hit action lines. It now
  filters them, as EXP-0039's probe does.
- A first live check on a pre-fix image was stopped and rerun on the final
  image (`local/end023`).

## 2026-11-05 — UI-004 written up (Phase N, no experiment)

User request (verbatim): "Write up UI-004". Tasks only; nothing run in an
emulator.

- Phase N in `TASKS.md`: `BOOT-001` (`READY`) to `BOOT-005`, modelled on
  XvSF's Phase O for method only (rule 13).
- Static facts gathered for the phase intro (read-only):
  - `WARNING0`-`3.PIX` are 122,880 bytes, `WARNING4.PIX` 131,072 (the
    size of `QSD.PIX`); hashes in the phase intro. The format is
    arithmetic only (HYPOTHESIS).
  - `grep -a` over `local/extracted/saturn_jp/`: only `CYBER.BIN` names
    the five files, in 16-byte entries from offset `0x39168`.
  - No `ERR*.BIN` on the disc.
- D-003 tested boot and attract only, so `BOOT-001` starts from the code
  (the readers of that table) rather than from cart settings.

## 2026-11-06 — BOOT-001: the boot warnings and their conditions (EXP-0051)

User request (verbatim): "Start BOOT-001". Nine cold boots, asked first
("Yes, run all 9 (Recommended)"); no key pressed. Button tests from saved
states only.

- Static first: `CYBER.BIN` (resident at `0x0600D000`) holds the
  `WARNINGn.PIX` pointer table at `0x06053ACC`; the picture routine
  `0x06036DA8` has three `bsr` callers, all in the save check
  `0x06036C3E`, which the start-up code calls once.
- Each of the five pictures came up under its predicted condition (D-048):
  damaged save `0`, unformatted internal `1`, unformatted cart `2`, both
  `3`, no save and too little room `4`. VRAM at `0x20000` equals the file
  each time.
- Statuses observed: 0 ready, 1 not connected, 2 unformatted.
- Free space: 5 free blocks still warn (BIOS free size 260 < 0x120).

Corrected or failed (do not retry):
- **A first static note had `WARNING4` call the BIOS like `1`-`3`.** Its
  screen says the game starts, and it has its own wait loop
  (`0x06036CD6`).
- **Predicted `WARNING3` then `1` then `2` when both are unformatted.**
  Only `3` shows: the wait never returns.
- **A button by RAM write does not work here.** Halting at the pad read
  (`mov.w @(8,Rn)`, Rn `0x060CC00E`) and writing `0100` to `0x060CC016`
  changed nothing on three screens; probably the SH-2 reads that word from
  its cache. The agent has no register write or cache space. Use a real
  press (`BOOT-005`), or halt earlier where the line is not cached.
- `mcs_extract --out-dir` also writes `manifest.json` and `preview.png`;
  pick `wram_h.bin` by name.

Checks: ruff, ruff format and mypy on `EXP-0051`'s scripts (below).

## 2026-11-06 — BOOT-002: how the boot warnings are stored and drawn (EXP-0052)

User request (verbatim): "Start BOOT-002". Six cold boots of a marked test
image, asked first ("Yes, run all 6 (Recommended)"); no key pressed. One
state-based run (VRAM writes).

- Format: 512 × 8-bit rows, values 0-15; VDP2 NBG1 256-colour bitmap at
  `0x20000`, bitmap palette 2; the 16 colours are `CYBER.BIN`'s table at
  `0x06053AAC`. All five redraw with 0 differing pixels (D-049).
- Each screen reads its own file: the marked image changed only that
  screen's ID block; a normal boot is unchanged.
- Visible: file columns 0-351, rows 0-223.

Corrected (do not retry):
- **Colour expansion `(c << 3) | (c >> 2)`** is not what Mednafen's
  screenshots show; they show `c << 3`.
- **A marker band at file rows 228-231 did not show.** The display has 224
  lines (`TVMD` VRESO 0); Mednafen's 240-row screenshot pads 8 black rows
  above and below. The edge is between file rows 223 and 224 (VRAM writes,
  `edge.py`). XvSF found the same edge late (its `EXP-0056`).

Checks: ruff, ruff format, mypy on `EXP-0052`'s scripts; pytest (below).

## 2026-11-06 — BOOT-003: English for the boot warnings (EXP-0053)

User request (verbatim): "Start BOOT-003". No emulator run.

- Official English: none. The arcade has no save message (only its region
  screen's title "WARNING"); the BIOS files give "Memory Manager",
  "Manage Memory", "Cartridge", "Clear", "Not Formatted". XvSF's screens of
  the same BIOS files add "System Memory".
- Drafts by the agent, rendered in the arcade letters and in `FIX.BIN`'s;
  sheets sent to the user.
- Decisions, verbatim: "Approve the drafts (Recommended)", "control panel
  (Recommended)", "6, what the game checks", "Arcade font, Japanese colours
  (Recommended)". Recorded in `TASKS.md` and the policy;
  `data/translations/boot_warnings.json` holds the approved text.

Notes (do not retry):
- A first wrap at 27 characters overflowed two screens in the arcade font;
  38 characters fit everything.
- `FIX.BIN` draws comma and apostrophe as dots.
- The arcade font has no parentheses.

Checks: ruff, ruff format and mypy on `EXP-0053/render.py`; pytest.

## 2026-11-06 — BOOT-004: the English boot warnings built (EXP-0054)

User request (verbatim): "Start BOOT-004". Six cold boots of the built
image, asked first ("Yes, run all 6 (Recommended)"); no key pressed.

- `tools/text/boot_warnings.py` (promoted from `EXP-0053/render.py`, with
  tests) and `dialogue.py --boot-warnings`. The generator reproduces the
  approved renders exactly.
- Build: two identical; M8 outputs and records unchanged; 208 sectors
  changed, all in the pictures; 0 invalid.
- Screens: each condition shows its English picture, 0 pixels differing;
  the normal boot is unchanged.

Notes (do not retry):
- **Pairing control screenshots by frame label fails** when the polls drift
  by one frame (`f00311` against `f00310`); pair them in poll order.
- `build/boot004/b`'s image was deleted after the check (rebuildable);
  `build/boot004/a` is the current image.

Checks: ruff, ruff format, mypy; pytest (190 passed).

## 2026-11-06 — BOOT-005: play check and register; UI-004 done (EXP-0055)

User request (verbatim): "Start BOOT-005". Six cold boots with one A press
each in five, asked first ("Yes, run all 6 (Recommended)").

- A on `WARNING0`: the game goes on and rewrites the save; on `WARNING4`:
  the game goes on, no save; on `WARNING1`-`3`: the BIOS routine at the
  `0x0600026C` vector (`0x0000186C`), the Saturn control panel. Normal boot:
  the title. Warning screens equal `BOOT-004`'s.
- Regression: five earlier references rebuild to their hashes
  (`regress.py`, outputs and records redirected so nothing committed is
  overwritten).
- Coverage ("Boot Warnings"), README (What's Changed, Still Japanese, Build
  the Patch), regression README, D-048's button row now CONFIRMED.

Notes (do not retry):
- **After a BIOS call, work-RAM breakpoints keep firing**: the BIOS's own
  code runs at those addresses (1.2 million hits in one run). Stop reading
  hits at the BIOS call.
- `0x06036A1C` and `0x06036D8A` are on the normal path too; they mean "the
  check went on", not "a warning was left".
- The reference rebuild commands write records into `data/translations`;
  redirect them when rebuilding (`regress.py`).
- The regression builds and the boots ran at the same time; the boots ran
  slower but frame-exact.

Checks: ruff, ruff format, mypy, pytest (below).

## 2026-11-06 — LOC-001 written up (Phase O, no experiment)

User request (verbatim): "Write up LOC-001". Tasks only; nothing run.

- Phase O in `TASKS.md`: `LOC-001` (`READY`) to `LOC-006`, modelled on
  XvSF's name-variant phase for method only (rule 13). The Options switch
  stays `OPT-001`; this phase builds the Latin default and keeps the
  katakana addressable for it.
- Facts carried in: D-013 (one set of names; only the select and VS name
  art differs), the VS art's place in `SELECT.VAD`, the cast roll's Latin
  names (D-040) as a candidate source, Tessan's missing arcade spelling.
  Unknown: the pilot-select art's storage, Latin art on the disc, voice.

## 2026-11-06 — LOC-001: name-art census (EXP-0056)

User request (verbatim): "Start LOC-001". No key, no cold boot: Saturn from
saved states with RAM writes; arcade in headless MAME.

- The select and VS screens draw names as frames of pose records (D-051);
  writing a record's frame shows any pilot's or mech's name on the real
  screen.
- Name art only on the pilot select and VS screen. US arcade: mixed-case
  pilots, capital mechs and SHADE, no model codes.
- `CYBER.BIN` has Latin lists of 17 mechs and 8 pilots beside the versus
  `SET UP` labels.

Failed or corrected (do not retry):
- **The fighter record's pilot byte (`0x060D02B2`) is not the select
  cursor**: writing it changed nothing.
- **VDP1 command writes are not CPU writes**: the list is built at WRAM-H
  `0x060E1000` and copied; break there instead.
- **Parallel `poke.py` runs race on `configure()`** (one read a half-written
  `mednafen.cfg`; the file itself stayed intact). Stagger starts, or run
  `configure()` once first.
- **A ffmpeg `xstack` grid needs exactly cols × rows inputs**; a scratch
  Python montage was used instead.
- At `MACHINE SELECT` in the arcade, Buttons 2-4 pick the same base body as
  Button 1; variants were not reached.
- First tied the VS table's 17th entry to ZERO-GOUKI by list order; that is
  only a HYPOTHESIS and is recorded as one.

Checks: ruff, ruff format, mypy on `EXP-0056`'s scripts; pytest.

## 2026-11-06 — LOC-002: where the name art is stored (EXP-0057)

User request (verbatim): "Start LOC-002". Saved-state runs, one marked test
image (deleted after use), and one versus-mode cold boot with 13 single
presses, asked first ("Yes, run it now (Recommended)").

- Select names: raw in `SELECT.VAD` (copied to VDP1 VRAM `0x20000`). VS
  names: type-2 compressed records in `PL3F_0.BIN`. Controlled change
  confirmed both.
- No Latin pilot or mech name in banks 56 or 63 (every frame drawn).
- Room: see D-052; the Options switch needs storage outside both files.

Failed or corrected (do not retry):
- **Session states replay without the user's keys**: from the title-menu
  state the game stays in attract, so no select-screen loads appear. Use
  a state after the mode choice (2538).
- **A one-launch walk of bank 63 blanked after 7 frames** (probably the
  pattern cache); draw each frame in its own run.
- **`locate.py` found no VS mech pixels on the disc**: they are compressed;
  trace `0x06010552`'s source instead.
- **`drive.py key` sometimes finds Mednafen not in front** and sends
  nothing; retry the single press (no loop of presses).
- The first Start at the title came as the title timed out into the
  attract demo; check the screen just before each press.
- `/var/folders` (`$TMPDIR`) is not the scratchpad; scratch files go to the
  session scratchpad.

Checks: ruff, ruff format, mypy; pytest (below).

## 2026-11-06 — LOC-003: names in voice (EXP-0058)

User request (verbatim): "Start LOC-003". Six recordings from saved states
and one cold boot (5 single presses; the user's choice "Run one more cold
boot"). Eight clips heard by the user, one at a time.

- No announcer calls a name; the story, victory quotes and endings are
  voiced in Japanese; "jin" is heard in Jin's narration.
- `-qtrecord` captures sound even with the silent home's volume at 0.

Notes (do not retry):
- A recording from state 7160 caught only loading; the round start begins
  after state 7339.
- `-qtrecord` files are about 8.5 MB a second; cut clips and delete them.
- `ffmpeg -sseof` is an input option: place it before `-i`.
- `drive.py shot` fails if the screenshot name exists; use new names.

## 2026-11-06 — LOC-004: the user's plan for the name art (EXP-0059)

User request (verbatim): "Start LOC-004". Samples drawn on the real select
and VS screens from saved states (no key, no cold boot); three sheets sent.

Decisions, verbatim: "Arcade letters in the banners (Recommended)", "As
the US arcade (Recommended)", "Keep, moved after the name (Recommended)",
"Devilotte (Recommended)". Spellings: `data/translations/name_art.json`.

Notes (do not retry):
- Name parts can be drawn flipped (select: vertical; VS mech right part:
  horizontal); read the flip bits from the command word.
- On the VS screen, write the WRAM-H copy (`0x060F0000` up), not VDP1
  VRAM `0x10000` up: it is refreshed every frame.
- Colour variants of the pilot banner look alike (pale yellow is the
  lightest colour).

## 2026-11-06 — LOC-005: the Latin name art built (EXP-0060)

User request (verbatim): "Start LOC-005". No key, no cold boot.

- Type-2 format read in full (D-053); `tools/text/pattern_t2.py` decodes
  every bank-63 record and encodes valid ones.
- `tools/text/name_art.py` and `--name-art`: one part per select name, one
  record per VS pilot, two per mech; VS records 12,316 of 21,712 bytes.
- Build clean (two identical, three files changed, all sectors valid); all
  34 names on screen as built.

Failed or corrected (do not retry):
- **Word 1 bit 1 of a part ends the frame's part list.** Copying the left
  mech part's words into the first slot hid the right half; set the bit
  on the last part only.
- **Part x is word 0 >> 6**, not >> 5 (fitted against every on-screen part).
- **`STG0A.BIN` is resident in every saved state**, so a state cannot test
  its built table from the disc; the select check writes it into RAM, and
  the cold boot is `LOC-006`'s.
- **The VS screen lasts a few seconds**: reload the state per name.
- **Stepping one frame per agent call is slow** (about a minute for 340
  frames); step in one call when nothing is written each frame.
- The `--ending-record-dir` folder must exist before the build.
- My first unit-test expectations for the halfword fill and a shadow
  position were wrong; the code was right.

Checks: ruff, ruff format, mypy, pytest (below).
