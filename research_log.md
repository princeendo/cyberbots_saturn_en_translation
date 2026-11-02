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
