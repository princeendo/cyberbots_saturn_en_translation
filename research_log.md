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
