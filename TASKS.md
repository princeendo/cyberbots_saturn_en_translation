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
- **2026-11-02: no native English path; box capacity measured** (`FONT-002`,
  `EXP-0021`, D-020): 4 rows × 16 cells, 60 glyph cells per box; 33, 298 or
  488 of the 488 paired slots fit, depending on the route (revised in
  `EXP-0023`). All M2 tasks are
  done.
- **2026-11-02: M3 tasks written up** (Phase H): `RE-002` and
  `LAYOUT-001` Phases A-B are `READY`. `PAIR-001`, `GATE-TRANSLATION` and
  `RE-003` are blocked in that order.
- **2026-11-02: Jin's boxes listed and forcible** (`RE-002`, `EXP-0022`,
  D-021): 17 story scenes, boxes 0-62, Saturn lines 0-120, from
  `STG0AS.BIN`; any scene can be forced from state 5208. Next: `PAIR-001`
  (now unblocked) or `LAYOUT-001` Phases A-B.
- **2026-11-02: Jin's boxes paired with the arcade English** (`PAIR-001`,
  `EXP-0023`, D-022): both games run the same scene scripts, so box N is
  slot N. All 120 lines have official English, and none is Saturn-only.
  REF-006's reader was fixed: 897 of lines 0-898 now pair (D-011,
  corrected).
- **2026-11-02: layout route chosen: pair glyphs** (`LAYOUT-001` Phases A-B,
  `EXP-0024`, D-023): every Jin and roster box fits; Jin's text fits in place;
  353 glyphs for Jin against 336 free codes.
- **2026-11-02: pair glyphs proven after a cold boot** (`LAYOUT-001`
  Phase C, `EXP-0025`, D-024): the arcade's own letters, two per cell,
  draw exactly as predicted in the M1 box; Japanese elsewhere is unchanged.
  `LAYOUT-001` is `DONE`.
- **2026-11-02: `GATE-TRANSLATION` passed for Jin's story.** The user's
  words: "GO (Recommended)". If the glyph gap remains: "Rarest Japanese
  glyphs (Recommended)". Next: `RE-003`.
- **2026-11-02: M3 CONFIRMED** (`RE-003`, `EXP-0026`, D-025): all of Jin's
  story dialogue in official English, from an image built from the
  untouched source; 63/63 boxes exact; a cold boot played two fights; other
  pilots' Japanese unchanged except 16 recorded lines.
- **2026-11-02: M4 tasks written up** (Phase I): `RE-004` (choose the second
  pilot with the user; list the boxes) is `READY`; `PAIR-002`, `RE-006`, the
  gate extension and `RE-007` follow.
- **2026-11-03: second pilot chosen: Santana** (`RE-004`, `EXP-0027`, D-026):
  the user's words: "Santana (Recommended)". His story is 20 scenes, boxes
  64-127; two moves right on the pilot select screen; forcing works.
- **2026-11-03: Santana's boxes paired** (`PAIR-002`, `EXP-0028`, D-027):
  same scripts as the arcade; all 64 boxes and 117 lines have official
  English, and none needs a new translation. Next: `RE-006`.
- **2026-11-03: the compiler and checks handle a set of pilots** (`RE-006`,
  `EXP-0029`): Jin's M3 image reproduced byte for byte; Jin + Santana need
  73 sacrificed codes against 18 approved, so the build stops. Next: the
  `GATE-TRANSLATION` extension for Santana (the user's GO and budget).
- **2026-11-03: `GATE-TRANSLATION` extended to Santana.** The user's words:
  "GO (Recommended)" and, for the 73-code budget, "Approve 73, same rule
  (Recommended)". `RE-007` is `READY`.
- **2026-11-03: M4 CONFIRMED** (`RE-007`, `EXP-0030`, D-028): Jin and
  Santana in official English from one image built from the untouched
  source; 127/127 boxes forced; cold boots of both; Mary's Japanese as
  recorded. Next: write up M5 (`RE-005`, outline only so far).
- **2026-11-03: M5 tasks written up** (Phase J): `RE-005` (census and
  roster, with the user) and `WIN-001` (is there a win-quote surface?) are
  `READY`; `PAIR-003`, `CAP-001`, the gate extension and `RE-008` follow.
  The estimate: 404 boxes and 551 pairs for lists 0-5, about 216 sacrificed
  codes under the current rule.
- **2026-11-03: versus win quotes found and added to M5** (`WIN-001`,
  `EXP-0031`, D-029): a versus win loads `VICTORY.BIN` and shows the
  winner's quote; the arcade tables have 624 slots, with US English for
  slots 494-623. The user: "Add to M5 (Recommended)". `WIN-002` is `READY`;
  so is `RE-005`.
- **2026-11-04: win quotes paired** (`WIN-002`, `EXP-0032`, D-030): both
  games pick from a per-pilot table of 8 entries and show box N = slot N;
  pilots 0-5 reach 46 boxes (lines 955-1005) with 24 US English records,
  one per pilot and level. The VS captions are boxes 494-549 (code). Next:
  `RE-005` (`READY`).
- **2026-11-04: M5 roster chosen** (`RE-005`, `EXP-0033`, D-031): the user
  chose the six arcade pilots ("Six arcade pilots (Recommended)"): lists
  0-5, 404 story boxes and 46 win-quote boxes. Every pilot's block was seen
  in play. `PAIR-003` and `CAP-001` are `READY`.
- **2026-11-04: code budget chosen** (`CAP-001`, `EXP-0034`): about 152
  sacrificed codes for the roster's story and win quotes, touching about
  51 shown Japanese lines, with half-cell indents and ranking by the lines
  that stay ("Indent + rank (Recommended)"). `dialogue.py --indent --rank
  staying`. Next: `PAIR-003` (`READY`).
- **2026-11-04: the roster is paired** (`PAIR-003`, `EXP-0035`, D-032):
  Mary, Arieta, Gawaine, and Bao and Mao pair box for slot; all 519 lines
  have official English, so no new translation is needed. `PAIR-003`,
  `WIN-002` and `CAP-001` are done: the gate extension for the roster is
  next (the user's GO).
- **2026-11-04: `GATE-TRANSLATION` extended to the roster.** The user's
  words: "GO, cap 160 (Recommended)" and, for win quotes, "Shared official line (Recommended)". `RE-008` is `READY`.
- **2026-11-04: M5 CONFIRMED** (`RE-008`, `EXP-0036`, D-033): one image
  from the untouched source with all six roster pilots' story and versus win
  quotes in official English; every box forced as predicted; cold boots to
  stage 2 (Mary's stage 1, a cockpit stage, accepted by the user). Next: M6
  (endings) needs its tasks written up first; `UI-004` (warnings) is in the
  outline.
- **2026-11-04: M6 tasks written up** (Phase K): `END-001` (reach Jin's
  ending, list its surfaces) is `READY`; `END-002`-`END-005` follow.
  Nothing started.
- **2026-11-04: Jin's ending reached** (`END-001`, `EXP-0037`, D-034):
  four RAM writes from REF-005 state 4138 and the vitality hold, no keys;
  checkpoint `local/end001/checkpoint/jin_ending_a16503.mcs`
  (`7e314718…64f2`). `END.BIN` scenes 16-19; Japanese in its dialogue,
  narration, captions, the cast roll's names and one QSound line. On the
  M5 image no ending line shows a pair glyph: the ending probably draws
  from `SE.DAT`'s copy of `KANJI.BIN` (SUPPORTED). Next: `END-002`,
  `END-003`, `END-004` are `READY`.
- **2026-11-05: how the ending draws** (`END-002`, `EXP-0038`, D-035):
  the ending's dialogue font is `SE.DAT`'s copy of `KANJI.BIN` (CONFIRMED
  by a one-glyph probe image), so a translated ending must change both.
  Cast-roll names are images in `KEND_1.BIN`, credits use `FIX.BIN`, the
  QSound line is pixels in `QSD.PIX`. Next: `END-003`, `END-004` are
  `READY`.
- **2026-11-05: what selects the ending** (`END-003`, `EXP-0039`, D-036):
  the winner's pilot byte, copied to `0x060CFF7E`; each list posts fixed
  scenes (`data/text/ending_posts.json`). Santana's ending was forced and
  matched its prediction. Jin's scene 20 is never shown. Credits text is
  ASCII in `KEND.BIN`. Next: `END-004` is `READY`.
- **2026-11-05: the arcade's ending English** (`END-004`, `EXP-0040`,
  D-037): headless MAME reaches Jin's ending in `cybotsu` and `cybotsj`
  with one round-end breakpoint. The arcade has English for every dialogue
  box of it; the US cast roll drops the katakana line; there is no QSound
  notice in the arcade ending. Next: `END-005` (closes M6) is `READY`.
- **2026-11-05: Jin's ending paired; M6 closed** (`END-005`, `EXP-0041`,
  D-038): 18 dialogue units pair box for slot (15 exact, 3 same wording);
  `data/translations/jin_ending_pairing.json`. The cast roll's 10 Japanese
  name images and the QSound line have no English. The user chose "Hide,
  as US arcade (Recommended)" and "Erase the line (Recommended)", so no new
  text is needed. The English fits, with no sacrificed code; room needs
  lines beyond Jin's own (SUPPORTED). Next: M7's gate extension (the user's
  GO), then `END-010`, written up in Phase L.
- **2026-11-05: `GATE-TRANSLATION` extended to Jin's ending.** The user's
  words: "GO (Recommended)" and, for the shared name boxes 605 and 601,
  "Share, English everywhere (Recommended)". `END-010` is `READY`.
- **2026-11-05: M7 CONFIRMED** (`END-010`, `EXP-0042`-`EXP-0045`, D-039-D-042): one image from the untouched source with the M5 roster unchanged and Jin's ending in official English. All 18 units are drawn as predicted; the cast roll's Japanese names are hidden in every ending (the user: "Hide in every ending (Recommended)"); the QSound line is erased. The shared names show English in lists 3, 4 and 8. A cold boot plays in English. Three long boxes finish typing just before they close: the user chose "Accept now, follow-up task (Recommended)" (`END-011`, `BACKLOG`). Next: M8 (`END-020`) needs its tasks written up first.
- **2026-11-05: M8 CONFIRMED** (`END-023`, `EXP-0050`, D-047): one image from the untouched source with the M5 story and win quotes and all six roster endings in official English. Every box of all nine endings draws as expected, the scene changes and music stay within 6 frames of the Japanese, and a cold boot plays in English. Two faults found and fixed on the way:
  - the Saturn-only endings use the story font, so the shared names (garbled in list 8 since M7) now use story codes plus one more sacrifice (the user: "Use M5's 153rd code (Recommended)");
  - typing counts spaces.

  Next: the outline's later milestones (`UI-004`, `REL-001`, `LOC-001`, ...) need their tasks written up.
- **2026-11-06: Names switch play-checked; Phase P done** (`OPT-006`, `EXP-0066`): two cold boots with real presses set `JAPANESE` (katakana on pilot select, `SET UP`, VS), kept it across a power cycle, and set `ENGLISH` (Latin again); new reference `opt006_names_switch.json`; all earlier references match. `REL-002` now waits only on the release-timing rule (every open task done or deferred by the user) and the user; the UI tasks start on request.
- **2026-11-06: Names switch built** (`OPT-005`, `EXP-0065`, D-058): `--names-switch` adds the `EXTRA OPTIONS` sub-menu (layout: title and rows up two lines, the user's choice) and the katakana tail files; from saved states the menu works and each setting shows its art on the pilot select and VS screens. `OPT-006` (cold-boot play check, with presses) is `READY`.
- **2026-11-06: Names switch decided** (`OPT-004`): an `EXTRA OPTIONS` sub-menu reached from a 9th OPTION MODE row (rows moved up a line), holding `NAMES  ENGLISH / JAPANESE`, saved; katakana in new tail files; SSP checked in `REL-002`. Answers verbatim in `docs/localization_policy.md`. `OPT-005` (build) is `READY`.
- **2026-11-06: Free RAM proven** (`OPT-003`, `EXP-0064`, D-057): 1,024 bytes inside `CYBER.BIN` (loaded with it) and 5,628 bytes above its BSS are unused once the program runs (logs, canaries, a cold boot, an independent review); the largest zero range is the VDP1 command list's open tail and is not free. `OPT-004` (the switch's design, with the user) is `READY`; option A of `OPT-002` is the one that fits.
- **2026-11-06: README layout and release tools** (`DOC-004`, `REL-001`, in parallel with `OPT-003`): the README follows MSHvSF's sections with placeholders; XvSF's `make_patch`, `make_ssp`, `make_zips` and `check_zips` are ported with provenance, Cyberbots parameters and synthetic tests. Phase R written up; `REL-002`-`REL-004` wait for `OPT-006`, the release-timing rule and the user.
- **2026-11-06: Storage and switch points found** (`OPT-002`, `EXP-0063`, D-056): the katakana set is 30,838 bytes; Track 01 has 150 unused sectors at its end, and a file placed there loads through the game's own loader; the game finds files by name, with room for more. The art goes in at two sites (after the `SELECT.VAD` load and after the `PL3F_0.BIN` load). Recommended for `OPT-004`: small files in the tail, loaded per screen. `OPT-003` (free RAM for the hooks) is `READY`.
- **2026-11-06: Options screen and save mapped** (`OPT-001`, `EXP-0062`, D-055): the menu prints C strings from `OPDEMO.BIN`; its settings are a 16-byte block (`0x060D9290`) saved in `CYBERBOTS01` with a byte sum; bytes +5-15 are unused, and one set there is saved and loaded at boot (one cold boot). A ninth row fits with EXIT moved down a row. `OPT-002` and `OPT-003` are `READY`.
- **2026-11-06: Phase P written up (names switch)**: `OPT-001` (Options screen and settings), `OPT-002` (where the katakana art can live, and the switch point) and `OPT-003` (free RAM proven by logs) are `READY` and independent; `OPT-004` (the user's choices and a gate extension), `OPT-005` (build) and `OPT-006` (verify) follow.
- **2026-11-06: Latin name art play-checked; Phase O done** (`LOC-006`, `EXP-0061`, D-054): two cold boots (arcade with a second player, versus) showed only the built Latin names on the pilot select, `SET UP` and VS screens; all eight regression references match. The build is `data/regression/loc005_name_art.json`. Next unblocked: `OPT-001` (the names switch), `REL-001`, or the UI tasks, on request.
- **2026-11-06: Latin name art built** (`LOC-005`, `EXP-0060`, D-053): the VS screen's compressed pattern format read in full; `--name-art` builds the nine select names and the nine pilot and sixteen mech VS names (model codes after the names). Two builds identical; only `SELECT.VAD`, `STG0A.BIN` and `PL3F_0.BIN` change; all 34 names show as built from saved states. A first build drew half of each mech name (a part list's end bit); fixed. `LOC-006` (cold-boot play check) is `READY`.
- **2026-11-06: `GATE-TRANSLATION` extended to the name art** (`LOC-004`, `EXP-0059`): from samples drawn into the real screens, the user chose the arcade letters in the Saturn banners, the US arcade's case, the mech model codes kept after each name, and "Devilotte". Spellings in `data/translations/name_art.json`. `LOC-005` (the build) is `READY`.
- **2026-11-06: names in voice checked** (`LOC-003`, `EXP-0058`): the user heard eight clips, one at a time. No announcer calls a name (select, VS, round start, win); names are spoken only inside voiced Japanese lines ("jin" in Jin's narration), so nothing in voice conflicts with Latin art. One cold boot covered the pilot pick (the user: "Run one more cold boot"). `LOC-004` (your plan per surface) is `READY`.
- **2026-11-06: name-art storage found** (`LOC-002`, `EXP-0057`, D-052): select names are raw art in `SELECT.VAD`, VS names compressed records in `PL3F_0.BIN` (confirmed by a marked test image read from saved states). No Latin pilot or mech name exists in either bank (every frame drawn); versus mode uses the same art (one cold boot, the user: "Yes, run it now (Recommended)"). Room: Latin select names fit in place; VS names need compression or more space; neither file can also keep the katakana for `OPT-001`. `LOC-003` (voice) is `READY`; `LOC-004` waits on it.
- **2026-11-06: name-art census done** (`LOC-001`, `EXP-0056`, D-051): name art appears only on the pilot select (9 pilot names) and the VS screen (9 pilot and 16 mech names); every other screen seen is Latin or nameless. Each name was shown on the real screen by a RAM write from a saved state (no key). The US arcade uses Latin in mixed case for pilots and capitals for mechs and SHADE. Versus mode's own screens were not reached (carried to `LOC-002`). `LOC-002` (storage, Latin art) and `LOC-003` (voice) are `READY`.
- **2026-11-06: `LOC-001` tasks written up** (Phase O, the user: "Write up LOC-001"): `LOC-001` (census of every name-art surface, Saturn and US arcade) is `READY`; `LOC-002` (storage, and whether Latin art is on the disc), `LOC-003` (voice), `LOC-004` (the user's plan, a gate extension), `LOC-005` (the Latin build) and `LOC-006` (verify) follow. The switch stays `OPT-001`. Nothing is started.
- **2026-11-06: `UI-004` DONE** (`BOOT-005`, `EXP-0055`): six cold boots with one A press each (the user: "Yes, run all 6 (Recommended)"). Every boot warning shows in English, and a button does what the English says: the game goes on after the damaged-save and out-of-space warnings, the Saturn control panel follows the three unformatted-memory ones. A normal boot reaches the title. All earlier regression references still rebuild. Coverage and README updated. Next: the outline's remaining items (`REL-001`, `LOC-001`, `UI-001`-`003`, `TXT-002`, `SPECIAL-001`) need their tasks written up first.
- **2026-11-06: the boot warnings built in English** (`BOOT-004`, `EXP-0054`, D-050): `--boot-warnings` adds the five English pictures to the M8 build; nothing else changes (two builds identical, every M8 output equal, 208 sectors changed, all in the pictures). Five cold boots (the user: "Yes, run all 6 (Recommended)") show each warning exactly as generated; a normal boot is unchanged. `BOOT-005` (play check and register) is `READY`.
- **2026-11-06: `GATE-TRANSLATION` extended to the boot warnings** (`BOOT-003`, `EXP-0053`): no official English exists, so the agent's translation, with the Saturn BIOS's terms, is approved. The user's words: "Approve the drafts (Recommended)", "control panel (Recommended)", "6, what the game checks" (an opt-in fix of the Japanese 05), "Arcade font, Japanese colours (Recommended)". `BOOT-004` (the build) is `READY`.
- **2026-11-06: how the boot warnings are drawn** (`BOOT-002`, `EXP-0052`, D-049): each is its own `WARNINGn.PIX`, a whole 512-wide, one-byte-a-pixel bitmap on VDP2 NBG1, drawn with 16 colours from the program (`CYBER.BIN`), not the file; 352 × 224 pixels show. A marked test image (six cold boots, the user: "Yes, run all 6 (Recommended)") changed only each screen's own marker. `BOOT-003` (English and lettering, a gate extension) is `READY`.
- **2026-11-06: the boot warnings found** (`BOOT-001`, `EXP-0051`, D-048): the game's only boot-time messages are five Japanese pictures, `WARNING0`-`4.PIX`, shown by one save check before the title: a damaged save (`0`), unformatted internal memory (`1`), an unformatted save cart (`2`), both (`3`), and no save with too little free space (`4`, fewer than 6 free blocks). Nine cold boots (the user: "Yes, run all 9 (Recommended)"), each picture on screen and in VRAM byte for byte. `BOOT-002` (storage and drawing) is `READY`.
- **2026-11-05: `UI-004` tasks written up** (Phase N, the user: "Write up UI-004"): `BOOT-001` (census, code first: the readers of `CYBER.BIN`'s `WARNING*.PIX` table) is `READY`; `BOOT-002` (storage and drawing), `BOOT-003` (English and lettering, a gate extension), `BOOT-004` (build on the M8 image) and `BOOT-005` (verify) follow. Nothing is started.
- **2026-11-05: `GATE-TRANSLATION` extended to the roster endings.** The user's words: "GO (Recommended)", "Indent, as the story (Recommended)", "Bao Mao: (Recommended)" and "Accept the rule (Recommended)". `END-023` (the M8 image) is `READY`.
- **2026-11-05: capacity of the roster endings measured** (`END-022`, `EXP-0049`, D-046): all six endings' English fits. With the half-cell indent the 330 pairs fit the 335 free codes, and nothing Japanese is touched. Room: the roster's own lines plus about 750 bytes of never-shown lines. Lists 6-8 show only their posted boxes. Next: the gate extension for the roster endings (the user's GO).
- **2026-11-05: ending box timing solved** (`END-011`, `EXP-0048`, D-045): cues (`EAnn`) close boxes, `E2nn` sets typing speed, and the script waits for typing, which sets the next scene and its music. The user chose "Faster typing + move cues (Recommended)". `--retime` gives Jin's English boxes 113+ frames with their full line, and every scene change and track start stays on the Japanese frame (built and live). `END-022` (capacity) is `READY`.
- **2026-11-05: the roster endings paired** (`END-021`, `EXP-0047`, D-044): every text unit of lists 1-5 (102) has official English at the same place in the arcade; no new translation. One choice for the gate: box 608 (both twins) can show slot 615 (the arcade's, one twin) or 617 (the same Japanese). `END-022` waits on `END-011`.
- **2026-11-05: the roster endings surveyed** (`END-020`, `EXP-0046`, D-043): lists 1-5 forced on the Saturn and in both arcade sets. All their Japanese is `END.BIN` boxes, and the post-dialogue screens are shared and already done. Correction: posted scripts run on into the next scenes, so Mary's and Bao and Mao's endings show the arcade's scenes 17-18 and 20. `END-021` (pairing) is `READY`.
- **2026-11-05: M8 tasks written up** (Phase M, the user: "Write up M8"):
  `END-020` (survey the roster endings) and `END-011` (box timing) are
  `READY`; `END-021` (pairing), `END-022` (capacity), the gate extension
  and `END-023` (the M8 image) follow. Nothing is started.
- **2026-11-05: local data backed up to the homelab** (user request):
  `local/` (86,298 files, all save states; no image, ROM or BIOS) is in
  `Archives/Cyberbots-Saturn-EN` with a manifest and restore commands. The
  finished-task folders, the M5 build images and the Mednafen sources and
  objects were then deleted here; what END-010 and the tools use was kept
  (`research_log.md`).
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
  (the dialogue font and its code table), D-020 (no native English path;
  box capacity), D-021 (box selection; Jin's scenes),
  D-022 (Jin's pairing), D-023 (font codes in
  use, font users, record size, free RAM), D-024 (pair glyphs work), D-025 (M3: Jin's story in
  English; fighter vitality), D-026 (pilot lists; stage groups), D-027 (Santana's pairing), D-028 (M4),
  D-029 (versus win quotes), D-030 (how a win quote is picked; box for
  slot; US English per level), D-031 (block k is list k; routes), D-032 (lists 2-5 paired), D-033 (M5). The font's layout is not confirmed.

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

- **Status:** `DONE` (2026-11-06)
- **Milestone:** before REL-001
- **Dependencies:** DOC-002.
- **Blockers:** None.
- **Objective:** Avoid XvSF's post-release README reorganization.
- **Acceptance criteria:** `README.md` follows the MSHvSF README's section layout, with placeholders for what is not done.
- **Notes:** Done 2026-11-06, in parallel with `OPT-003` (the user:
  "Begin OPT-003 and any other tasks you can do in parallel."). `README.md`
  now has MSHvSF's sections (Download; What's Changed with "Still
  Japanese"; Patch Files and Applying a Patch; Build the Patch with Files
  You Need, Set Up, Build the Release Patches, Build Options; Development
  with Further Files for Research, Python Tooling, Local Data, Project
  Guides), with "Not yet (`REL-001`)" placeholders. Every earlier fact and
  command kept (checked against the previous README); an independent
  review added the missing `local/extracted/saturn_jp/` input and its
  extraction command (tested: 264 files, identical to the existing copy).

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

### FONT-002 - Look for a native English path, then measure Latin text and box capacity

- **Status:** `DONE`
- **Milestone:** M2
- **Dependencies:** FONT-001 (done).
- **Blockers:** None.
- **Objective:** Before any font work, learn whether the Saturn renderer still has a way to draw arcade-style English (`docs/lessons_from_xvsf.md`, lesson 1). Then measure what the existing font and box can show in Latin text, so that `LAYOUT-001` chooses a capacity route from facts.
- **Acceptance criteria:**
  - **Phase A: native path.**
    - The text loop (`0x0606E7BC` and the code that calls it) is disassembled far enough to list every branch on a text byte, a flag, the region or a language variable. Each branch is recorded with what it does.
    - A search of the program files for reads of the region or language bytes near the text code is recorded, with its result.
    - Any candidate path that ordinary Japanese text does not take is tried live from checkpoint A (a RAM write of the flag or bytes, before the box types), with a no-write control. The result is recorded on screen, crash or not.
    - If no path is found, that is stated with what was searched.
  - **Phase B: Latin text in the existing font.** All live RAM tests run from checkpoint A, before the box types, each with a no-write control, as in `RE-001`:
    - **Full-width capitals:** a line-4 write of full-width capitals and digits (codes `0x8260`-`0x8279`, `0x824F`-`0x8258`) shows the predicted glyphs (`tools/font/kanji.py` mapping), checked by agent-reviewed screenshot.
    - **Codes not in the table:** a half-width ASCII pair that is not a table code (for example `AB`), and a full-width lower-case letter (not in the table), are written. What the box does is recorded: blank cell, skip, wrong glyph, or crash.
    - **Line length:** the most cells one line shows (wrap, clip or overrun), measured with a line longer than the longest Saturn line (16 cells, D-008).
    - **Lines per box:** the most lines one box shows, measured with `0x0A` line breaks inside one line's bytes.
    - **Cell limit:** the VDP1 cell buffer's limit per box (cells from `0x1E200`), measured or bounded from the code.
  - **Capacity statement.** From the measurements:
    - the box's capacity in full-width cells;
    - how many of the 450 paired arcade English slots (D-011) fit as written in capitals only, and how many after re-wrapping;
    - the font's free room (58 glyphs, 26 table slots) against the extra glyphs each capacity route needs: lower case, pair glyphs, a half-width path.
    These are inputs to `LAYOUT-001`; no route is chosen here.
  - Original and written bytes, addresses, purpose, expected and observed results are recorded for every write (rule 12). The source image is unchanged; nothing goes on disc.
- **Notes:**
  - Facts from D-019:
    - Text is read two bytes per glyph, with `0x0A` a line break (SUPPORTED, from the disassembly).
    - The font has full-width 0-9 and A-Z but no lower case.
    - The pair glyphs `Dr` and `!?` already draw two half-width characters in one cell, as MSHvSF's pair-glyph route did (playbook, "Capacity route: pair glyphs").
  - The arcade English record for a slot runs up to 4 lines of 38 characters (D-009). The Saturn box shows 2 lines of up to 16 full-width cells in the scenes seen so far.
  - In XvSF the leftover arcade language word crashed to the BIOS unless it was gated per slot (`docs/lessons_from_xvsf.md`). A crash in Phase A is a result, not a failure; record it and do not retry the same write.
  - Overlong test strings overwrite the bytes after line 4 (its NUL, then line 5). That is part of the measurement: line 5's own pointer then reads from the middle of the test string, and the record says so.
- **Evidence:** `EXP-0021`, D-020, 2026-11-02.
  - **Phase A:** no branch on region or language in the typing routine (`0x0606E5C0`) or the layout loop (`0x0606E734`). No English dialogue in any of the 264 files (ASCII, arcade code, full-width). There is no native path.
  - **Phase B** (live, checkpoint A, each with the control `ead786`):
    - full-width capitals and digits draw as mapped;
    - `AB` and `ａ` draw blank cells, and `Dr` and `!?` draw as pairs;
    - a 17th cell runs off-screen, with no wrap;
    - `0x0A` is not a break while typing;
    - a 5-entry record shows 4 rows in the box.
  - **Cell limit:** 60 cells reserved per box (`0x0601118E`), with no check; past it the game hangs (SUPPORTED).
  - **Capacity:** of 450 paired slots, 31 fit as written in capitals, 272 re-wrapped, and 450 with pair glyphs (571 distinct pairs). Revised in `EXP-0023` for 488 slots: 33, 298 and 488 (579 pairs). The font has 58 free glyphs and the table 26 free slots.

## Phase H: M3 (Jin's Story Dialogue)

M3: all of Jin's story dialogue boxes are handled programmatically, from the
untouched source image. Jin is the M1 pilot (`REF-008`). The order is:

1. `RE-002` and `LAYOUT-001` Phases A-B (no English needed);
2. `PAIR-001`;
3. `GATE-TRANSLATION`;
4. `LAYOUT-001` Phase C;
5. `RE-003`.

Out of scope: endings (rule 23); VS-screen chapter captions and pilot name art
(other surfaces: `SPECIAL-001`, `LOC-001`); and other pilots' stories (M4,
M5). The Saturn-only lines inside Jin's own story are in scope, under the
new-translation policy.

### RE-002 - Find what selects each box, list Jin's boxes, and force any box

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** RE-001, DISC-001, FONT-002 (done).
- **Blockers:** None.
- **Objective:** Learn which box record each story scene shows and what chooses it, list every box of Jin's story, and show any of them from one checkpoint, so that every box can be verified live without gameplay.
- **Acceptance criteria:**
  - **Selector:** the value that picks the M1 box's record (`0x0609D184`, D-020) is found by a controlled trace from checkpoint A or an earlier state: its address, its writer, and the table it indexes. When it is chosen (scene start, per box, per stage) is stated.
  - **Jin's boxes:** every story box Jin can reach is listed with evidence:
    - its record address and lines (Saturn line numbers, D-008);
    - its scene (stage, before or after the fight, any branch on win, loss or opponent);
    - the file it comes from: `STG0AS.BIN`, `VICTORY.BIN` or `END.BIN`, each loaded at `0x06060000` but with its own layout (D-017).

    The list comes from the code's own scene or record tables, not from reading the text. Endings are listed only as excluded.
  - **Forcing:** writing the selector shows a chosen record, for at least 3 distinct Jin boxes from one checkpoint. The cells are checked as in `EXP-0020`, against a no-write control. The method is written up as a runbook entry in `docs/mednafen.md` (a debug harness; it never ships).
  - **Rows and records:** the record format is confirmed on more than one box: the header (x, y, the attribute byte, and the 4/5 values that move x), and the entries (line pointer and word). Whether any record of Jin's has more than two lines is recorded.
- **Outputs:** an experiment, a forcing script, a box list (`data/text/jin_boxes.json`: record addresses, line numbers, scenes and files; no text), and the runbook entry.
- **Notes:**
  - Leads, at most HYPOTHESIS:
    - the layout entry `0x0606E6E0` reads a 16-bit index into a table of record pointers at `0x060A5684` (`STG0AS.BIN` `0x45684`), whose records hold x, y, an attribute and a text pointer;
    - the typing routine walks a record at `r13` (`0x0606E5C0`).
  - The arcade picks a slot through `0xFF2F7A`, written by `0x011D48`, and the script table `0x12150` (D-010). A Saturn twin of that logic would be a HYPOTHESIS to test, as XvSF's quote selector was.
  - Dialogue is fixed from a checkpoint (D-014), so forcing should not need RNG work, but any branch found must be tested.
- **Evidence:** `EXP-0022`, D-021, `data/text/jin_boxes.json`, the `docs/mednafen.md` runbook; 2026-11-02.
  - **Selector:** stage-code constants are posted as scenes (`0x0606DBEA`). The scene byte at task + `0x23` and the pilot byte at task + `0x1F` pick a script from `0x060AAD24` (Jin `0x060AA840`). Script words name boxes, and the record table is `0x060A5684`.
  - **Jin's boxes:** scenes 21 and 0-15, in fixed order over stages 0-8 (no branch in that code). They are boxes 0-62 and lines 0-120 (line 34 is dead data), all in `STG0AS.BIN`. Scenes 16-20 are the ending, posted from `END.BIN`, and excluded.
  - **Forcing:** scenes 4, 9 and 15 drew their predicted first boxes, 5/5, 20/20 and 14/14 cells; the control drew scene 0 (25/25).
  - **Records:** the header is (0, x, y, attribute), with x = 140 for dialogue and 80 for narration, and y = 172 and attribute 14 on all 63 boxes. 7 boxes have 3 lines. The side switch (`0xFF80`) comes from a script byte, not the header.
  - Not traced: losing a fight, continues and the 2P side.

### LAYOUT-001 - Choose how English fits the dialogue box

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** FONT-001, FONT-002, DISC-002 (done).
- **Blockers:** None for Phases A-B.
- **Objective:** Measure each way of fitting English in the box, put the routes to the user as a decision, and prove the chosen route on a rebuilt image.
- **Why:** The box holds 4 rows of 16 full-width cells and at most 60 glyph cells (D-020). The font has full-width capitals but no lower case, comma or apostrophe. Of the 488 paired arcade slots, 33 fit in capitals as written, 298 after re-wrapping, and all 488 with two characters per cell (revised in `EXP-0023`).
- **Candidate routes** (each a HYPOTHESIS until tested):
  - **(a) Full-width capitals, re-wrapped:** the existing font, plus a comma and an apostrophe. Up to 4 rows per box, which needs more record entries, so records must be relocated.
  - **(b) Pair glyphs:** two characters per 16×16 cell, mixed case, as the font's `Dr` already does. It needs new glyphs and table codes (579 for the paired roster, `EXP-0023`). They come from free slots, or from kanji and kana that the remaining Japanese text does not use.
  - **(c) Narrower drawing:** a code patch to the typing routine, for example half-width cells at an 8-pixel advance. It needs new glyph data, a change to the cell layout, and room for more sprites.
  - **(d) More cells per box:** a code patch raising the 60-cell reservation (`0x0601118E`). It needs proven free RAM below `0x060FE200` and room in VDP1 VRAM after `0x20000`. It can combine with (a)-(c).
- **Acceptance criteria:**
  - **Phase A: limits**, measured for each route:
    - a census of the 1,222 table codes: which ones the 1,851 Saturn lines use, and which are unused;
    - glyphs and codes needed, for Jin alone and for the paired roster;
    - room for longer records and lines in `STG0AS.BIN`, `VICTORY.BIN` and `END.BIN` (file slack, sector slack, and what follows each file in RAM: `0x060AE4F8` is used after `STG0AS.BIN`, D-020);
    - free RAM for (c)/(d), by write logs over a full stage, not by assumption (XvSF's first toggle hung the title);
    - whether other screens draw with `KANJI.BIN`, which would break if its glyphs are replaced.
  - **Phase B: decision.** A capacity model is recorded for each route: characters per row and per box, and the Jin and roster fit counts. The user chooses a route as a multiple-choice question with a "(Recommended)" option. The answer is recorded verbatim in `docs/localization_policy.md` and `research_log.md`.
  - **Phase C: proof.** On an image rebuilt from the untouched source, the chosen route shows synthetic test text in the M1 box, after an agent-driven cold boot. The text uses each new glyph or code path at least once, and fills a box to the route's limit. The original image is the control. Text drawn with the original glyphs (another pilot's box) still draws correctly. Every sector is valid, and the source hashes are unchanged.
- **Outputs:** an experiment; font-build tooling (glyph rendering and a repack with `tools/font/kanji.py`); the census; and the policy entry.
- **Notes:**
  - MSHvSF chose pair glyphs and repacked its font at the same size; XvSF used its native English mode, which Cyberbots does not have (D-020).
  - `KANJI.BIN` is reloaded from disc for each box scene (D-019), so a rebuilt image's font shows in a replay from a state before that load. The cold boot is still required (playbook: forced trials can show stale data).
  - Any route that removes Japanese glyphs breaks other pilots' Japanese until M5, unless only unused glyphs are reused. That trade-off is part of the user's decision.
- **Evidence (Phases A-B):** `EXP-0024`, D-023, 2026-11-02.
  - **Census:** 912 of 1,222 codes are in use; 336 codes and 368 glyphs are free without breaking Japanese.
  - **Font users:** story, endings and `VICTORY.BIN` share the font.
  - **Records:** 3 lines in place.
  - **Room:** Jin's Japanese takes 3,448 bytes, plus 820 bytes of dead ending lines in `STG0AS.BIN`'s copy (SUPPORTED).
  - **Free RAM:** WRAM-H `0x06002F00` (19,968 bytes) and `0x060E3300` (19,712), with no CPU writes over a full stage. VDP1 VRAM `0x16400`-`0x1E1FF` is free in dialogue (SUPPORTED).
  - **Route fits** (Jin / 488 roster boxes): (a) 35 / 298; (b) 63 / 488; (c) 43 / 372, or 63 / 488 with (d).
  - **Decision:** asked as one multiple-choice question, 2026-11-02. The user's answer, verbatim: "Pair glyphs (Recommended)". Recorded in `docs/localization_policy.md`.
- **Evidence (Phase C):** `EXP-0025`, D-024, 2026-11-02.
  - **Letters:** the arcade's English font was captured in MAME from test records drawn from work RAM: all 60 characters, plus `Q`, `Z` and the ten digits.
  - **Shades and width:** the shades map onto Saturn values 9-13; letters are narrowed to 7 pixels (`tools/font/pairs.py`).
  - **Image:** 48 test pairs in unused code slots, and 3 rows of 32 characters in dead lines 752-777 through an extended record. 15 sectors changed, all valid; two builds identical.
  - **Checks:** the replay drew 48/48 cells, and the following Japanese box 25/25. An agent cold boot played to the box, and its screen was pixel-identical to the replay's.

### PAIR-001 - Pair Jin's boxes with the arcade English by the games' own logic

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** REF-003, REF-004, REF-006, RE-002 (done).
- **Blockers:** None.
- **Objective:** For each line of each of Jin's boxes, find the arcade English record the arcade shows in the same scene, or show from the arcade code that none exists.
- **Why:** The policy pairs official English to each Saturn line by the game's own logic. Absence of official English must be shown by tracing the arcade code, not by a data search alone (`docs/localization_policy.md`). `REF-006` paired by text alignment (D-011), which is evidence, not the games' logic.
- **Acceptance criteria:**
  - **Arcade scenes:** the arcade's scene-to-slot choice for Jin's story is traced in MAME from the code: the script table `0x12150` and the slot variable `0xFF2F7A` (D-010). The result is Jin's slots in scene order.
  - **Pairing table:** it is compared with `RE-002`'s Saturn box list, and every Saturn line of Jin's boxes is paired with an arcade slot and line. Each pair is labelled with its evidence (scene order, code, `REF-006` alignment) and its confidence.
  - **On-screen check:** at least 3 pairs are confirmed by showing the same scene in both games: the arcade from a MAME state (US set for English), the Saturn by forcing (`RE-002`). Otherwise the experiment records why that is not possible.
  - **Saturn-only lines:** every Saturn line with no arcade counterpart is listed. Its absence is shown from the arcade's script for that scene. It is marked for a recorded new translation.
- **Outputs:** an experiment and `data/translations/jin_pairing.json`: Saturn line numbers, arcade slots and lines, labels, and source hashes. It holds no game text.
- **Notes:**
  - This reads English but writes none to disc, so it runs before the gate.
  - The arcade English slot can have up to 4 lines for a Saturn box of 2 (D-009). The pairing is per box, and the line split is `LAYOUT-001`'s.
  - The arcade's English and Japanese share slot numbers in the first scene (D-011). A second scene's check is in `docs/known_unknowns.md`.
- **Evidence:** `EXP-0023`, D-022, `data/translations/jin_pairing.json`; 2026-11-02.
  - **Arcade scenes:** the script table `0x12150` (read at `0x11CC6`) holds the same bytecode as the Saturn's. Jin's arcade scenes 21 and 0-15 name the Saturn's boxes number for number, so box N is slot N. The slot is stored at `0xFF2F7A` before the language table is chosen.
  - **On screen:** in MAME (`cybotsu`) the unforced run shows scenes 21 then 0 (slots 0-5); scenes 4, 9 and 15 forced at `0x11CEA` show slots 18, 33 and 59 in English. These are the Saturn's forced first boxes (EXP-0022), with the same portraits.
  - **Pairing table:** 63 boxes and 120 lines, each with an English record; 115 lines exact and 5 edited against the slot's Japanese.
  - **Saturn-only lines:** none in Jin's story.
  - **Correction:** REF-006's reader stopped at the space code `0x0020`. Fixed in `tools/text/arcade_pairing.py`, with a test, and rerun: 897 of lines 0-898 pair, in 488 slots (D-011, corrected). The 13 lines that first looked "expanded" were this bug.

### GATE-TRANSLATION - Confirm reference and translation prerequisites

- **Status:** `DONE` (Jin's story)
- **Milestone:** M3
- **Dependencies:** DOC-002, REF-001, REF-003 to REF-007 (done; REF-002 rejected), PAIR-001 (done).
- **Blockers:** The user's GO.
- **Objective:** No English text goes on disc before the oracle, the pairing method and the user's policy are settled.
- **Acceptance criteria:**
  - Every dependency is `DONE`.
  - The user gives a recorded GO for Jin's story, covering:
    - the official English as paired;
    - the recorded new translations for Jin's Saturn-only lines (translator named, each line listed);
    - the layout route, if it has been chosen by then.
  - Each later scope extension (a new pilot, endings, names, captions) is its own dated block under this gate.
- **2026-11-02: Jin's story.** Every dependency is `DONE`.
  - **Asked:** "GATE-TRANSLATION: may Jin's official arcade English go on the disc, as paired, with pair glyphs?"
  - **Answer, verbatim:** "GO (Recommended)"
  - **Covers:** the official US arcade English (`cybotsu`, table `0x0B33AA`) for Jin's 63 story boxes, paired slot for slot (D-022), unchanged, arcade slips included. No new translations are needed. Drawn with pair glyphs (D-024). Grammar fixes stay opt-in.
  - **Also asked:** "If Jin's English still needs more glyphs than the 336 unused slots after optimising pair splits, what should give?"
  - **Answer, verbatim:** "Rarest Japanese glyphs (Recommended)"

### RE-003 - Build all of Jin's story dialogue in English from the source image

- **Status:** `DONE`
- **Milestone:** M3
- **Dependencies:** GATE-TRANSLATION, LAYOUT-001, RE-002, PAIR-001, DISC-002 (all done).
- **Blockers:** None.
- **Objective:** Compile every line of Jin's boxes from its paired official English, or its approved new translation, through the chosen layout route. Build the image from the untouched source, and verify every box live and in a cold-boot play check.
- **Acceptance criteria:**
  - **Compiler:** a dialogue compiler turns the pairing table and the English into Shift-JIS lines, box records and glyphs (as the route needs) deterministically.
    - It rejects text that does not fit: rows, cells (≤ 60 per box) or codes.
    - It writes every copy that Jin's scenes load (`RE-002`), keeping their pointers valid.
    - It has synthetic tests.
  - **Build:** the image is built with `tools/disc/patch_image.py` from the untouched source.
    - Only the intended files' sectors change, with valid EDC/ECC.
    - Two builds are identical, and the source hashes are unchanged.
    - Rule 12 records are kept for every changed record and line.
  - **Live check:** every one of Jin's boxes is forced (`RE-002`) from a checkpoint. Each drawn cell equals the compiler's prediction. The original image is the control.
  - **Play check:** an agent-driven cold boot plays Jin's story through at least the first two stages, with pad keys and the fights won by forcing or play. The screenshots show the English boxes as compiled.
  - **Other pilots:** another pilot's first box is checked. It is still Japanese and draws correctly, or it is as the route's recorded trade-off says.
  - **Provenance:** `data/translations/jin_story.json` records, for each line:
    - the arcade source address and hash for official English (read from the ROM at build time, never committed, rule 21);
    - the text and translator for new translations;
    - the pairing and any opt-in grammar fix.
- **Outputs:** an experiment, the compiler and its tests, the translation record, and a regression reference.
- **Notes:**
  - Endings, VS captions and name art are untouched.
  - The image commit pushes after the agent's cold-boot check passes (user rule, 2026-11-02).
  - From `LAYOUT-001` (EXP-0025):
    - `tools/font/pairs.py` renders the cells; the arcade capture is rebuilt with `EXP-0025/capture_font.py` (code-sheet timelines).
    - `EXP-0025/build.py` shows how codes, lines and records are written; `replay_cells.py`, `check_cells.py` and `cold_route.py` are the checks to reuse.
    - Jin needs 353 pairs against 336 codes free of Japanese: choose pair boundaries to reduce them, or record the trade-off.
- **Evidence:** `EXP-0026`, D-025, `data/translations/jin_story.json`, `data/regression/re003_jin.json`; 2026-11-02.
  - **Compiler:** `tools/text/dialogue.py`, with tests. It reads the English from the ROM at build time, re-wraps it to 32 characters and 3 rows, and assigns codes: 310 unused, 25 new, and 18 sacrificed Japanese glyphs (user's decision). Lines 57 and 75, which other pilots share, are kept.
  - **Build:** 82 sectors, all valid; two builds identical (Track 01 `904402b6…`); source unchanged.
  - **Live:** every box of all 17 scenes forced from state 4138 matches its predicted cells (63/63); the original image matches none (scene 9, 0/8).
  - **Play check:** an agent cold boot played Jin's story into stage 2, with fights won by forcing the opponent's vitality (`0x060D0318`) and a time-out. Every English box seen matched its prediction (20 complete, 1 caught mid-typing).
  - **Other pilots:** pilot 1's scene 0 Japanese draws its original cells. The 16 lines that use a sacrificed glyph are listed in EXP-0026.
  - **M3 is CONFIRMED.**

## Phase I: M4 (A Second Pilot)

M4: a second pilot's story dialogue works through the same mechanism as
Jin's, built together with Jin's English, without changing Jin's result. The
order is:

1. `RE-004` (choose the pilot, with the user; list the boxes);
2. `PAIR-002` and `RE-006`, which are independent;
3. the user's gate extension;
4. `RE-007`.

Endings, VS captions, name art, the Saturn-only pilots and the rest of the
roster stay out of scope (rules 23 and 24; `RE-005` is M5).

### RE-004 - Choose the second pilot and list their boxes

- **Status:** `DONE`
- **Milestone:** M4
- **Dependencies:** RE-002, RE-003 (done).
- **Blockers:** None.
- **Objective:** Name the Saturn's 11 pilot lists, put a second pilot to the user as a decision, and list that pilot's story boxes from the game's own tables, as `RE-002` did for Jin.
- **Acceptance criteria:**
  - **Names:** each Saturn pilot list (`0x060AAD24`, entries 0-10) is tied to a pilot name and portrait by evidence: a forced scene from each list (the `RE-003` scene-list redirect) with an agent-reviewed screenshot. The list is matched to the arcade's pilot offsets at `0x12150` by comparing scene scripts.
  - **Candidates:** a table of the arcade pilots (lists 0-5), with for each:
    - story scenes and boxes (scenes posted by `STG0AS.BIN`'s stage code, versus ending scenes from `END.BIN`);
    - Saturn lines paired, Saturn-only and shared with other pilots' boxes;
    - the extra distinct pairs and bytes the compiler would need on top of Jin's;
    - the selection route on the pilot select screen.
  - **Decision:** the user chooses the pilot, asked as a multiple-choice question with a "(Recommended)" option. The answer is recorded verbatim in `research_log.md` and `docs/localization_policy.md`.
  - **Box list:** `data/text/<pilot>_boxes.json` (as `jin_boxes.json`) is generated by a generalized `box_list.py`. The scene order for that pilot's stage code is traced as in `EXP-0022`, including any branch, and the forcing method works for that pilot (at least 3 scenes forced, cells checked against predictions).
- **Outputs:** an experiment, the box list, and the generalized listing and forcing scripts.
- **Notes:**
  - Survey (2026-11-02, from `STG0AS.BIN`'s tables, all scenes including endings):

| List | Scenes | Boxes | Lines | Paired (REF-006 fixed) |
| --- | --- | --- | --- | --- |
| 0 (Jin) | 22 | 83 | 152 | 148 |
| 1 | 27 | 82 | 145 | 141 |
| 2 | 22 | 84 | 142 | 137 |
| 3 | 29 | 89 | 163 | 157 |
| 4 | 22 | 86 | 166 | 164 |
| 5 | 29 | 94 | 165 | 157 |
| 6-9 | 21-72 | 69-139 | 83-282 | 0-1 (Saturn-only pilots) |
| 10 | 7 | 6 | 7 | 2 |

    Lists 4 and 5 include lines 57 and 75: Jin's lines that `RE-003` kept, because boxes 315 and 388 share them.
  - The stage code posts scenes in blocks of about 17. In `STG0AS.BIN`, Jin's block holds stage groups 0-8. Whether the other blocks are other pilots' or other routes is open (`EXP-0022`), and this task settles it for the chosen pilot.
- **Evidence:** `EXP-0027`, D-026, `data/text/santana_boxes.json`; 2026-11-03.
  - **Names:** lists 0-5 are Jin, Santana, Mary, Arieta, Gawaine, and Bao and Mao, from scene scripts identical to the arcade's pilots 0-5 and from forced scene-0 dialogue. Lists 6-8 are Saturn-only.
  - **Decision:** the user answered "Santana (Recommended)" (verbatim, recorded).
  - **Route:** Santana is two moves right of Jin. A cold boot posted block 1's scenes in order, starting at stage group 9.
  - **Story:** 20 scenes (0-15, 23-26), boxes 64-127, lines 121-237. His ending is 16-22.
  - **Forcing:** his scenes 4, 9 and 24 drew their first boxes exactly (29, 29, 30 cells).

### PAIR-002 - Pair the second pilot's boxes with the arcade English

- **Status:** `DONE`
- **Milestone:** M4
- **Dependencies:** RE-004, PAIR-001 (done).
- **Blockers:** None.
- **Objective:** Pair each line of the chosen pilot's story boxes with the arcade English the arcade shows in the same scene, or show from the arcade code that none exists, as `PAIR-001` did for Jin.
- **Acceptance criteria:**
  - **Scripts:** the arcade's scripts for that pilot (`0x12150`) are compared scene by scene with the Saturn's, and any scene whose scripts differ is listed.
  - **Pairing table:** each box is paired slot for slot where the scripts agree, with each line labelled `exact` or `edited` against the slot's Japanese (`tools/text/arcade_pairing.py`, fixed in `EXP-0023`). Boxes or lines with no counterpart are labelled, with the arcade script as evidence.
  - **On screen:** at least 3 pairs are shown in both games from forced scenes (MAME at `0x11CEA`, the Saturn by `RE-004`'s forcing).
  - **Output:** `data/translations/<pilot>_pairing.json`, generated by a generalized `pair_jin.py`. It holds no text.
- **Notes:** lines with no official English need a recorded new translation (policy), each named at the gate extension.
- **Evidence:** `EXP-0028`, D-027, `data/translations/santana_pairing.json`; 2026-11-03.
  - **Scripts:** all 20 story scenes are the same in both games, so box N is slot N. All 64 boxes have English, and the 117 lines are 114 exact and 3 edited. None needs a new translation.
  - **Exception:** box 64's lines aligned to slot 63, because slots 63 and 64 share one record in both games (and Saturn boxes 63/64 one record; box 63 is unused).
  - **On screen:** forced in MAME, scenes 4, 9 and 24 play slots 81-84, 99-105 and 87-88, Santana's English beside his portrait. These are the same first boxes the Saturn showed (EXP-0027).
  - **Shared line:** line 144 is also used by box 292 (another pilot's), for `RE-006`'s kept-line rule.

### RE-006 - Let the compiler and checks handle a set of pilots

- **Status:** `DONE` (2026-11-03, `EXP-0029`)
- **Milestone:** M4
- **Dependencies:** RE-003, RE-004 (done).
- **Blockers:** None.
- **Objective:** Make `tools/text/dialogue.py` build several pilots' boxes into one image deterministically, and make the live checks work for any pilot.
- **Acceptance criteria:**
  - **Compiler:** it takes one or more pairing files and shares one pair-code pool across them, so a pair used by both pilots gets one code.
    - Room: each pilot's own lines, plus their dead ending lines (proved dead the `EXP-0024` way). Lines shared with a pilot not in the build are kept.
    - Codes: it reports the code budget (free, new, sacrificed). It stops before sacrificing more Japanese glyphs than the user has approved; the extension's count goes to the gate.
    - The same inputs give byte-identical outputs.
  - **Jin's regression:** built alone, it still reproduces `data/regression/re003_jin.json`, or the difference and its reason are recorded with a new reference.
  - **Checks:** `force_check.py` and `play_two_stages.py` take the pilot and use the scene-list redirect (`other_pilot.py`) or the pilot select. Each check names its starting state and why the script in RAM is the image's own (a pre-load state, `EXP-0026`).
  - **Tests:** synthetic tests cover the shared pool, the kept-line rule and the budget stop.
- **Notes:**
  - With two pilots, the distinct pairs will exceed the 335 free codes by more than Jin's 18. The extra sacrificed glyphs, or an alternative, are a decision for the gate extension.
  - Indenting rows to save pairs was rejected for looks (`EXP-0026`).
- **Results** (`EXP-0029`):
  - **Compiler:** repeatable `--pairing`, one pool; users are the boxes some scene shows; kept lines (57, 75, 144) and dead ending lines are derived. Jin alone reproduces `re003_jin.json` byte for byte, so its reference stands.
  - **Budget:** Jin + Santana need **73** sacrificed codes (18 approved), touching 62 Japanese lines in `STG0AS.BIN` (198 with the `END.BIN` and `VICTORY.BIN` copies). The build stops and writes nothing; `--budget` reports.
  - **Room:** 7,316 of 8,088 bytes; Santana's ending adds dead lines 778-800 and 1016 (SUPPORTED, as Jin's).
  - **Determinism:** two builds of each set identical.
  - **Checks:** `EXP-0029/force_check.py --boxes` (Jin scene 9: 8/8; Santana scene 4 on the original: 29/29 Japanese cells), naming state 4138. `EXP-0027/play_route.py` picks the pilot from a cold boot.
  - **Option for the gate:** ranking sacrifices by the uses that stay Japanese would touch 184 lines instead of 198, but changes Jin's image.

### GATE-TRANSLATION extension for the second pilot

A dated block under `GATE-TRANSLATION`, once `PAIR-002` and `RE-006` are
done. The user's GO covers:
- the pilot's official English as paired;
- any new translations, each listed with its translator;
- the code budget, that is, how many more Japanese glyphs may be sacrificed
  and which lines that touches.

**2026-11-03: GO for Santana.** Shown: his pairing (EXP-0028: 64 boxes, 117
lines, 114 exact and 3 edited, no new translations) and the budget
(EXP-0029: 73 sacrificed codes; 62 touched lines in `STG0AS.BIN`, 44 of them
the Saturn-only pilots', 198 with the copies), with two alternatives.
- "GATE-TRANSLATION extension: may Santana's official arcade English go on the disc, as paired, with pair glyphs?" → "GO (Recommended)"
- "Jin + Santana need 73 sacrificed Japanese glyphs (18 approved so far). What should give?" → "Approve 73, same rule (Recommended)"

So `RE-007` builds Jin + Santana with `--max-sacrifice 73`, by the same
rarest-glyph rule, and Jin's image is unchanged when built alone.

### RE-007 - Build Jin and the second pilot in English from the source image

- **Status:** `DONE` (2026-11-03, `EXP-0030`)
- **Milestone:** M4
- **Dependencies:** RE-006, PAIR-002, the gate extension (all done).
- **Blockers:** None.
- **Objective:** One image with both pilots' story dialogue in English, verified box by box and in play, with Jin's English unchanged in effect.
- **Acceptance criteria:**
  - **Build:** from the untouched source; only the intended sectors change, all valid; two builds identical; the source hashes unchanged; rule 12 records kept.
  - **Live:** every story box of both pilots is forced from a pre-load state and draws its predicted cells; the original image is the control.
  - **Play check:** an agent cold boot plays the second pilot's story into at least stage 2, with fights won by forcing (D-025). A cold boot of Jin's route shows his first scene as before.
  - **Other pilots:** a third pilot's box still draws its Japanese, or as the recorded trade-off says.
  - **Provenance:** `data/translations/<pilot>_story.json`, and an updated regression reference.
- **Notes:** The image commit pushes after the agent's cold-boot check passes (user rule, 2026-11-02).
- **Results** (`EXP-0030`):
  - **Build:** 85 sectors (76 `KANJI.BIN`, 9 `STG0AS.BIN`), all valid; two builds identical (Track 01 `a63ba806…`); source unchanged; 73 sacrificed codes, the first 18 Jin's.
  - **Forced:** Jin 63/63, Santana 64/64 boxes; controls 0 cells.
  - **Play:** Santana's cold boot into stage 11 (his third), scenes 23 and 0-4 shown (box 67 caught mid-typing); Jin's cold boot shows scenes 21 and 0 as before; Jin's predicted cells equal his Jin-only build's.
  - **Other pilots:** Mary's scene 0 Japanese unchanged except box 131's sacrificed `0x8BC1`, as recorded.
  - **Provenance:** `data/translations/jin_story.json`, `santana_story.json`; `data/regression/re007_jin_santana.json`.
  - **M4 is CONFIRMED.**

## Phase J: M5 (All Ordinary Story Dialogue)

M5: every ordinary pilot's story dialogue is localized by the same mechanism,
from one roster file, in one image built from the untouched source. Versus
win quotes are a separate surface (`WIN-001`, D-029) and are in M5 (the
user's decision, 2026-11-03). The order is:

1. `RE-005` (census and roster, with the user) and `WIN-001` (is there a
   win-quote surface?), which are independent;
2. `PAIR-003`, `WIN-002` and `CAP-001`, which are independent;
3. the user's gate extension for the roster;
4. `RE-008` (the roster image).

Endings (M6-M8), VS captions, name art and the Saturn-only pilots (rule 24,
`SPECIAL-001`) stay out of scope.

Survey (2026-11-03, an estimate, not evidence): `EXP-0027/candidates.py`'s
counting, extended in scratch to lists 0-5 with their story blocks.

| | Jin + Santana (built) | Lists 0-5 |
| --- | --- | --- |
| Story boxes | 127 | 404 (63, 64, 69, 66, 70, 72) |
| Distinct pairs, one pool | 408 | 551 |
| Codes to sacrifice (335 free) | 73 | about 216 |
| Line bytes needed / room in own unshared lines | 7,316 / 6,584 (8,088 with dead ending lines) | 23,812 / 20,720, before dead ending lines |
| Boxes over 3 rows | 0 | 0 |

### RE-005 - Census of every pilot list; choose the roster

- **Status:** `DONE` (2026-11-04, `EXP-0033`)
- **Milestone:** M5
- **Dependencies:** RE-007 (done).
- **Blockers:** None.
- **Objective:** Describe every Saturn pilot list from the game's own tables and runs, and put the M5 roster to the user as a decision, as MSHvSF's `RE-043` did.
- **Acceptance criteria:**
  - **Census:** a generated table (`data/text/pilot_census.json`, no text) of all 11 lists, with for each:
    - story scenes (the list's block of `STG0AS.BIN`'s scene posts), ending scenes (posted by `END.BIN`), and scenes posted by neither;
    - story boxes, lines, lines paired with the arcade slot of the same number, Saturn-only lines (line 258 is one, D-011), and lines shared with other lists' boxes;
    - the pilot select route (moves from Jin) and the first stage group.
  - **Blocks:** that block k is list k is seen in play for each arcade pilot not yet seen (lists 3-5; SUPPORTED so far, EXP-0027): an agent cold boot (`EXP-0027/play_route.py`) with that pilot posts its block's first scenes.
  - **Lists 9 and 10:** what they are (their scripts match the arcade's pilots 6 and 7, EXP-0027), from forced scenes with agent-reviewed screenshots and from where their scenes are posted.
  - **Decision:** the user chooses the roster (expected: lists 0-5) and any exceptions, asked as a multiple-choice question with a "(Recommended)" option and recorded verbatim in `research_log.md`, `docs/localization_policy.md` and a new `docs/coverage_exceptions.md` (MSHvSF's method: every excluded list or box with its evidence).
  - **Outputs:** `data/text/m5_roster.json` (lists, box-list files, story scenes, routes) and `data/text/<pilot>_boxes.json` for each roster pilot, with `story_scenes` and `story_scenes_posted`.
- **Notes:** `data/text/mary_boxes.json` exists (`EXP-0030`) without `story_scenes`.
- **Results** (`EXP-0033`, D-031):
  - **Census:** `data/text/pilot_census.json`. Lists 0-5 have 404 story boxes and 756 lines; all but Mary's line 258 pair with an arcade slot (14 lines pair with a slot other than their box's number, for `PAIR-003`). Lists 6-8 have 339 boxes, none paired. Mary's and Gawaine's scene 15 repeat scene 14 and are in no block. Ending scenes are matched to `END.BIN`'s posts by number only.
  - **Blocks:** cold boots posted 22, 0 (Arieta, stage 27), 20, 0 (Gawaine, 36), 27, 0 (Bao and Mao, 45) and 18, 0 (list 6, 54): block k is list k, the stage group 9 x k. Routes from Jin: right x1-x5 are Mary, Santana, Gawaine, Bao and Mao, Arieta (moves 3 s apart); left x1 and x2 are lists 6 and 8. 8 runs, 67 menu presses, none during a fight.
  - **Lists 9 and 10:** list 9 is the versus win quotes (D-030). List 10 shows only the speaker-name boxes 602-605 and 609; the arcade posts its twin (list 7) at `0x6319C`; no Saturn post found.
  - **Decision:** the user's answer, verbatim: "Six arcade pilots (Recommended)". Exceptions: `docs/coverage_exceptions.md`.
  - **Outputs:** `data/text/m5_roster.json`; `mary_boxes.json` (story scenes added), `arieta_boxes.json`, `gawaine_boxes.json`, `baomao_boxes.json`. `jin_boxes.json` is unchanged: it feeds the regression references, and Jin's story scenes are D-021's (the compiler's `JIN_STORY`).


### WIN-001 - Is there a win-quote surface?

- **Status:** `DONE` (2026-11-03, `EXP-0031`)
- **Milestone:** M5
- **Dependencies:** None open.
- **Blockers:** None.
- **Objective:** Decide from evidence whether Cyberbots has win quotes (or other per-fight dialogue) outside the story scenes, and what shows `VICTORY.BIN`'s copy of the dialogue table, so M5's scope is known.
- **Acceptance criteria:**
  - **When it loads:** the CD-command log (`EXP-0018/trace.py --log`) from a state before a fight's end, through the win and the next scene, shows whether `VICTORY.BIN` loads and where (open since `EXP-0018`, `docs/known_unknowns.md`).
  - **What it shows:** if it loads, the screen that uses it, with an agent-reviewed screenshot and the glyph routine's caller; if it never loads in story play, the modes tried (arcade win, loss and continue, versus) are listed.
  - **Arcade:** the arcade's text readers (`0x11CC6` for story scripts; the second reader at `0x97222`, D-010) are checked for a win-quote table.
  - **Result:** "no separate surface" closes the question for M5. A separate surface becomes its own task, which the user adds to M5 or defers (a decision, recorded verbatim).
- **Notes:** `docs/text_surfaces.md` lists the round-end and bonus screens as already English.
- **Results** (`EXP-0031`, D-029):
  - **Loads:** arcade-mode win, loss and the attract mode never load `VICTORY.BIN`. A versus-mode win loads it, then `KANJI.BIN`.
  - **Screen:** `VICTORY!` with the winner's portrait and one dialogue line (Saturn line 959 after Jin's win), then an English `RESULT` tally.
  - **Arcade:** the dialogue tables have 624 slots; slots 494-623 follow Saturn lines from 899 (slot k = line k + 405; corrected by `WIN-002`: the offset varies, and slot N is Saturn box N, D-030); the US set has English in all 130. The reader of those slots is not traced (`WIN-002`).
  - **Decision:** asked whether versus win quotes join M5; the user's answer, verbatim: "Add to M5 (Recommended)".

### WIN-002 - Pair the versus win quotes with the arcade English

- **Status:** `DONE` (2026-11-04, `EXP-0032`)
- **Milestone:** M5
- **Dependencies:** WIN-001 (done).
- **Blockers:** None.
- **Objective:** Pair every Saturn win-quote line with the arcade English the US arcade shows in the same situation, by game logic, and make the quote screen reachable for checks.
- **Acceptance criteria:**
  - **Selection:** how the Saturn (`VICTORY.BIN`) and the arcade choose a quote (winner, loser, random, round) is traced; the arcade reader of slots 494-623 is named.
  - **Lines:** the Saturn lines that are win quotes, and those that are VS captions, are listed from the code, not by meaning (lines 899-1028 are candidates).
  - **Pairing:** `data/translations/win_quotes_pairing.json` (no text): each quote line with its arcade slot and the US English record shown in the same situation; any line with no official English is listed for the gate. A US line worded differently from the Japanese is expected (slot 558, `EXP-0031`); pairing follows the game logic, as MSHvSF's did.
  - **On screen:** at least 3 quotes forced in both games (MAME and the Saturn), with agent-reviewed screenshots. The Saturn route is a state on the versus `VICTORY!` screen or a forced selection, with no key loops (user, 2026-11-03).
- **Notes:** the VS captions (`docs/text_surfaces.md`) are a separate question; the US arcade showed none (`EXP-0012`), though its table has English in their slots.
- **Results** (`EXP-0032`, D-030; `data/translations/win_quotes_pairing.json`):
  - **Selection:** the Saturn (`VICTORY.BIN` `0x06060B46`) reads table `0x0606FAA0`[winner][random & 7] and posts list 9; the arcade (`0x6301C`) reads `0x630CE`[winner][2 x level + bit] and posts list 6. Same scenes for pilots 0-5; the arcade's scripts are the Saturn's list 9 scenes 0-47, box for slot. Arcade readers: the script interpreter `0x11CC6` (slot written by `0x11D48`) for quotes, and `0x116F2` from `0x62D4C` for VS captions.
  - **Lines:** quotes are boxes 554 and 556-600 (lines 955, 957-1005) for pilots 0-5, and 1023-1044 (lines 1790-1821) for pilots 6-8; box 555 (line 956) is in no table entry. VS captions are boxes 494-549 (lines 899-952) from `0x0609CC22`[pilot x 10 + stage] (code; boxes 1045-1071 for pilots 6-8).
  - **Pairing:** every box of pilots 0-5 has its slot's US record: 46 boxes, 24 records, one per pilot and level. So the two Japanese quotes of a level share one official English line (22 pairs of boxes; Jin's level 0 and Bao and Mao's level 1 each have one box). 37 boxes match their slot's Japanese exactly, 7 hold codes the map lacks (same lengths), and 2 (579, 580) add Saturn line 982. No quote of pilots 0-5 lacks official English. Which line each shared pair shows is for the gate.
  - **On screen:** MAME, Jin's entries 2, 5 and 7 forced, giving slots 599, 558 and 560 with three English lines. Saturn, one versus cold boot with 14 menu presses and none during the fight: the natural pick (R0 & 7 = 7, box 560, line 961), then boxes 599, 558 and 556 forced in the script (lines 1004, 959, 957). All agent-reviewed.

### PAIR-003 - Pair the roster pilots' boxes with the arcade English

- **Status:** `DONE` (2026-11-04, `EXP-0035`)
- **Milestone:** M5
- **Dependencies:** RE-005 (done).
- **Blockers:** None.
- **Objective:** Pair every story box of every roster pilot not yet paired, as `PAIR-002` did for Santana.
- **Acceptance criteria:**
  - **Scripts:** for each pilot, the arcade's scripts (`0x12150`) are compared scene by scene with the Saturn's; differing scenes are listed.
  - **Pairing:** `data/translations/<pilot>_pairing.json` from `EXP-0028/pair_pilot.py`, each line `exact` or `edited`, with shared-record slots and boxes with no counterpart labelled and explained by the arcade script. The candidates had 0-4 boxes per pilot that are not slot for slot (Mary 1, Arieta 0, Gawaine 4, Bao and Mao 4; `EXP-0027`).
  - **On screen:** at least 2 pairs per pilot shown in both games from forced scenes (MAME at `0x11CDA`/`0x11CEA`, the Saturn by `EXP-0029/force_check.py`).
  - **New translations:** every line with no official English is listed with its box and context (no text committed), for the gate, where the user names the translator.
- **Notes:** no text is committed (rule 21).
- **Results** (`EXP-0035`, D-032):
  - **Scripts:** every story scene of lists 2-5 matches the arcade's; only ending scenes differ (Mary 16-18; Arieta 16, 20, 27, 28; Gawaine 16-19; Bao and Mao 16-22, 28).
  - **Pairing:** `data/translations/{mary,arieta,gawaine,baomao}_pairing.json`. Against each box's own slot, all 519 lines are exact (489) or edited (30). The candidates' irregular boxes hold lines other boxes share (REF-006 aligned them to the first box), or, for Mary's line 258, the slot's own line with its punctuation edited. Shared-record slots: 283/284, 290/291, 335/336, unused boxes 283, 290, 335.
  - **On screen:** two forced scenes per pilot: MAME played the slots of the Saturn's boxes (agent-reviewed English screenshots); the Saturn drew every box's Japanese cells, 757/757.
  - **New translations:** none; every roster line has official English (D-011's line 258 corrected). The pairs equal `CAP-001`'s estimate, so its budget stands.


### CAP-001 - Capacity for the roster, and the user's choice of trade-off

- **Status:** `DONE` (2026-11-04, `EXP-0034`)
- **Milestone:** M5
- **Dependencies:** RE-005 (done).
- **Blockers:** None.
- **Objective:** Measure what the roster needs in codes, glyphs and line bytes, story and win quotes together, test the options for the gap, and put them to the user.
- **Acceptance criteria:**
  - **Budget:** `dialogue.py --budget` over all roster pairings (after `PAIR-003`, or the census's slot-for-slot pairing for the estimate, labelled as such): pairs, sacrifices needed, line bytes against room (own lines plus dead ending lines, proved dead as in `EXP-0029`), and the Japanese lines touched, grouped by whose they are (Saturn-only pilots, endings, `VICTORY.BIN`, other).
  - **Options,** each measured, not assumed:
    - (a) the current rule (fewest lines, then table order);
    - (b) ranking by the uses that stay Japanese (184 against 198 lines for Jin + Santana, `EXP-0029`);
    - (c) reaching the 33 glyphs no table code can reach: the table is followed by data at `0x060AB73C` and read through one literal at `0x0606EA40`. Whether it can move, and where, is an experiment (`HYPOTHESIS` until then);
    - (d) any other route the evidence offers, such as a second glyph set for story scenes (`KANJI.BIN` loads per box scene, D-019). Proposed only with evidence.
  - **Room:** if the rows do not fit the room, the shortfall and the options for it are measured as well.
  - **Decision:** the user chooses, asked as a multiple-choice question with a "(Recommended)" option and recorded verbatim. The chosen option is implemented in `tools/text/dialogue.py` with synthetic tests. Jin + Santana either reproduce `re007_jin_santana.json` or get a new reference with the reason recorded.
- **Notes:** the user's earlier decisions accepted broken Japanese "until they are English (by M5)". After M5 the Japanese that stays is the Saturn-only pilots', the endings' and `VICTORY.BIN`'s, so the trade-off now lasts longer; the question says so.
- **Results** (`EXP-0034`; pilots 2-5 paired slot for slot, an estimate until `PAIR-003`):
  - **Budget:** 404 story boxes and 46 quote boxes, 556 pairs; 335 free codes; the current rule needs 221 sacrificed codes and touches 133 shown lines that stay Japanese. Text 23,812 bytes against 25,272 of room in `STG0AS.BIN`; the quotes need 1,324 bytes against 1,320 in their own `VICTORY.BIN` lines, with that file's unshown story copy as further room (code only).
  - **Options:** (b) ranking by staying lines: 221 codes, 106 lines. (c) 33 more codes: an upper bound, not tested (the data after the table is read by 2 literals and a 9-entry pointer table; three copies of the table). (d) a half-cell indent on 64 of 897 rows: 487 pairs; with (b) 152 codes, 51 lines. (d) capitals: 450 pairs; with (b) 115 codes, 16 lines.
  - **Decision:** the user's answer, verbatim: "Indent + rank (Recommended)".
  - **Implementation:** `dialogue.py --indent --rank staying`, with synthetic tests; the defaults still reproduce `re003_jin.json` and `re007_jin_santana.json` byte for byte. For the six story pairings the compiler gives 480 pairs, 145 codes, 52 lines touched, 23,904 bytes against 25,272.


### GATE-TRANSLATION extension for the roster

A dated block under `GATE-TRANSLATION`, once `PAIR-003`, `WIN-002` and
`CAP-001` are done. The user's GO covers, per roster pilot:
- the official English as paired, story and win quotes;
- any new translations, each listed with its translator;
- the code budget and the chosen trade-off (`CAP-001`: indent + rank by
  staying lines, about 152 codes and 51 shown lines touched, to be fixed by
  `RE-008`'s build), with the lines it touches;
- for win quotes, what the two Japanese quotes of a level show, since the
  US set has one English line per pilot and level (22 pairs of boxes, D-030):
  the shared official line for both, or a new translation for one.

**2026-11-04: GO for the roster.** Asked: "Roster GO: put the official US arcade English, as paired and unchanged, on all six pilots' story (404 boxes) and win quotes (46 boxes), drawn as pair glyphs with the indent + rank rule? The estimate is 152 borrowed font codes, touching 51 Japanese lines that stay (43 Saturn-only, 3 roster endings, 5 VS captions). The build stops and asks again if it needs more than the cap." The user's answer,
verbatim: "GO, cap 160 (Recommended)". Asked: "The US arcade has one English win quote per pilot and level, so 22 pairs of different Japanese quotes share one English line. On the Saturn, which shows when either quote of a pair is picked?" The user's answer, verbatim: "Shared official line (Recommended)".
Covered: lists 0-5's story scenes (404 boxes, pairings D-022, D-027, D-032)
and win quotes (46 boxes, D-030), official US arcade English, unchanged;
no new translations; up to 160 sacrificed codes under `--indent --rank
staying`; each pair of win quotes sharing a US record shows that record.

### RE-008 - Build the roster's story in English from the source image (M5)

- **Status:** `DONE` (2026-11-04, `EXP-0036`)
- **Milestone:** M5
- **Dependencies:** RE-005, PAIR-003, WIN-002, CAP-001, the gate extension (all done).
- **Blockers:** None.
- **Objective:** One image with every roster pilot's story dialogue in English, built from the roster file, verified box by box and in play.
- **Acceptance criteria:**
  - **Systematic:** `tools/text/dialogue.py --roster data/text/m5_roster.json` builds it; a new pilot needs only its pairing and roster entry.
  - **Build:** from the untouched source; two builds identical; all sectors valid; source hashes unchanged. Every changed byte range in `STG0AS.BIN` and `KANJI.BIN` is accounted for by a roster box's row or record, a table code or a glyph; all other bytes are checked equal to the source (MSHvSF's untouched-block check).
  - **Live:** every story box of every roster pilot is forced from a pre-load state and draws its predicted cells (about 114 scenes, about 3 hours unattended); the original image is the control.
  - **Play:** an agent cold boot of each roster pilot reaches at least stage 2 with forced fights (D-025) and shows its English boxes.
  - **Win quotes:** every roster pilot's versus win quotes draw their predicted cells (forced), and one versus win from a cold boot shows an English quote.
  - **Japanese left:** a Saturn-only pilot's box and, if reachable, a `VICTORY.BIN` screen draw as the recorded trade-off says.
  - **Provenance:** `data/translations/<pilot>_story.json` per pilot and `data/regression/re008_roster.json`.
- **Notes:** the gate allows up to 160 sacrificed codes (`--max-sacrifice 160`) with `--indent --rank staying`; more stops the build for the user. Win quotes go into `VICTORY.BIN` (its own line table, box records and code-table copy, D-030). The image commit pushes after the agent's cold-boot checks pass (user rule, 2026-11-02). Cold boots only with the user present.
- **Results** (`EXP-0036`, D-033; `data/regression/re008_roster.json`):
  - **Systematic:** `dialogue.py --roster data/text/m5_roster.json --indent --rank staying --max-sacrifice 160`; win quotes go into `VICTORY.BIN`. The old commands still reproduce `re003` and `re007`.
  - **Build:** 152 codes sacrificed (160 approved); two builds identical; 102 changed sectors, all valid; sources unchanged; every changed byte accounted for (`changes.json`, `untouched.py`).
  - **Live:** 404/404 story boxes, 10,529 cells, as predicted; controls 0 of 905.
  - **Play:** stage 2 of their groups for Jin, Santana, Arieta, Gawaine, and Bao and Mao; Mary her stage 1. Her stage 19 is a cockpit stage that ends in game over without input. Asked: "Five roster pilots reached stage 2 of their groups in cold boots with their English boxes shown. Mary reached only her stage 1 (twice): stage 19 is a cockpit stage, not a fight, and with no input it ends in GAME OVER, so the RAM win doesn't apply there. Her English showed in play in 5 scenes (stages 18-19), and every one of her 69 boxes passed the forced check. How should RE-008 close?" The user's answer, verbatim: "Accept, record why (Recommended)".
  - **Win quotes:** 46/46 forced, 615 cells; the cold boot's own pick shows in English.
  - **Japanese left:** list 6's box 896 and quote box 1023 draw as the trade-off records.
  - **Provenance:** `data/translations/<pilot>_story.json` for all six; `data/regression/re008_roster.json`.


## Phase K: M6 (Ending Investigation)

M6: one ending, from the start of the pilot's last scene to the end of its
credits, is understood well enough to localize it: how it is reached, what
it shows, how each surface is drawn and stored, what selects it, and what
English the arcade shows in the same place. Nothing is changed in M6; M7
(`END-010`) localizes one ending and M8 (`END-020`) all roster endings.

Assume nothing from the story or the win quotes; re-derive each fact
(`docs/playbook_from_mshvsf.md`, Phase 4). The roster is lists 0-5
(`RE-005`); Saturn-only pilots' endings stay out (rule 24). The order is:

1. `END-001` (reach Jin's ending and list its surfaces);
2. `END-002` (renderers and fonts), `END-003` (text in RAM, on disc, and
   what selects it) and `END-004` (the arcade's ending English), which are
   independent once `END-001` gives a route;
3. `END-005` (pair Jin's ending with the arcade English), which closes M6.

Known so far (facts and their confidence):
- `END.BIN` holds a copy of the dialogue table (D-008) and its own scene
  post routine `0x06066852` (EXP-0022); it posts scene numbers 16-34 with
  no list number (EXP-0033), so which ending scenes belong to which pilot
  is by number only (`data/text/pilot_census.json`, `ending_scenes_by_number`:
  Jin 16-20, Santana 16-22, Mary 16-18, Arieta 16-21, 27, 28, Gawaine
  16-19, Bao and Mao 16-22, 28). **Superseded** by D-036 (`END-003`): R4
  is the list number, and `data/text/ending_posts.json` lists each list's
  posts from the code.
- When `END.BIN` loads is open (`docs/known_unknowns.md`).
- `KEND.BIN`, `KEND_0.BIN` and `KEND_1.BIN`, and the 21 `*_END*` audio
  tracks (D-002), are candidates, not facts.
- The story's ending scenes differ from the arcade's scripts (`EXP-0035`).
- The M5 image's sacrificed codes reach `END.BIN`'s Japanese: Jin's ending
  is the first place to see them in play.

Rules for every run: cold boots only with the user present and asked first;
menu key presses only; fights and routes forced by RAM writes (the user,
2026-11-03); MAME runs headless with a fresh copy of the NVRAM base
(`EXP-0032`).

### END-001 - Reach Jin's ending and list what it shows

- **Status:** `DONE`
- **Milestone:** M6
- **Dependencies:** RE-008 (done).
- **Blockers:** None.
- **Objective:** A repeatable, no-key-loop route to Jin's ending on the Saturn, a checkpoint before it, and a list of every surface the ending shows.
- **Acceptance criteria:**
  - **Route:** from a cold boot of the untouched image (menu keys only) or a saved state, the stage byte (`0x060CFF88`) and the fights are forced to Jin's last stage and through it by RAM writes, with each write logged. The same route reaches the ending twice. The route is a script under `research/experiments/` (pattern: `EXP-0027/play_route.py`, `EXP-0036/versus_route.py`).
  - **Checkpoint:** a save state just before the ending starts (named, with its SHA-256), from which every later M6 run starts.
  - **Loads:** the CD Play Disc log (`EXP-0031/loads.py`) from the checkpoint to the end of the credits: every file and audio track read, in order (answers when `END.BIN` loads; shows whether `KEND*.BIN` or a `*_END*` track is used).
  - **Surfaces:** screenshots every 50 frames to the end, agent-reviewed; a table of every text surface the ending shows (dialogue boxes, narration, pages, credits, captions), each with its frames, language, and whether it looks like the story's box. Added to `docs/text_surfaces.md`.
  - **Scenes:** the scene posts (`0x06066852`, R5) with frames, matched to the boxes shown.
  - **M5 image:** the same route on the M5 image (`build/re008/roster`), to record which ending lines show the sacrificed codes' pair glyphs (the recorded trade-off).
- **Notes:** the user does not read Japanese; review every screenshot yourself. If Jin's last stage cannot be forced (a cockpit stage, as Mary's stage 19, `EXP-0036`), record it and ask before any other route.
- **Done:** 2026-11-04 (`EXP-0037`, D-034), from a saved state, with no cold boot and no keys. The route writes the stage index (8), player 2's pilot and machine for index 8, the opponent word and the last-fight flag `0x060CFF07` before the stage start, then holds the vitality; writing only the stage byte, or leaving out the opponent or the flag, does not end the story (`research_log.md`). Two runs agree frame for frame; checkpoint `jin_ending_a16503.mcs` (`7e314718…64f2`); the loads, scene posts (16-19, not 20) and boxes are in the README; surfaces in `docs/text_surfaces.md`. M5 image: one character predicted to show a pair glyph shows the original: the ending reads `SE.DAT` (which holds a `KANJI.BIN` copy) and no `KANJI.BIN`, so the sacrifice does not reach this ending (the font source is SUPPORTED, for `END-002`).

### END-002 - How each ending surface is drawn, and with which font

- **Status:** `DONE`
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None.
- **Objective:** For each surface of `END-001`'s table, the routine that draws it and the font or image data it uses, proven by a controlled change.
- **Acceptance criteria:**
  - **Dialogue boxes:** whether `END.BIN`'s boxes go through the same glyph cells (`0x060FE200`, D-020) and code table (`END.BIN`'s copy, D-019) with `KANJI.BIN`, shown by matching captured cells to the decoded font, and by one RAM write to a line that changes exactly the predicted cell.
  - **Other surfaces:** for each, the layer (VDP1 sprites or VDP2), the source of its pixels (a font file such as `KEND*.BIN`, an image file, or text drawn from codes), and one controlled change (zero one cell, sprite or tile) that removes exactly the predicted glyph.
  - **Font capacity:** for each font found, its glyph count and code table, and whether it is the story's font, so `END-020` can plan codes.
- **Notes:** `docs/playbook_from_mshvsf.md` step 2 (MSHvSF's ending text used the quote font; that is not a Cyberbots fact).
- **Done:** 2026-11-05 (`EXP-0038`, D-035), from saved states, no cold boot, no keys, each change against a no-change control. Dialogue boxes: the story's path (`END.BIN`'s lines and code table, cells at `0x060FE200`), glyphs from `SE.DAT`'s copy of `KANJI.BIN` (`SE.DAT` is the whole VDP2 VRAM image); a probe image with one `SE.DAT` glyph changed and a one-code RAM write each changed exactly box 408's first cell. Cast-roll names: VDP1 sprites from shadows decoded by `0x0601446C` from `KEND_1.BIN`. Credits and thank-you: VDP2 NBG0, `FIX.BIN` (ASCII-indexed). QSound line: pixels of `QSD.PIX` (NBG1 bitmap). One zeroed sprite, character or bitmap rows removed exactly the predicted item. Capacity: `SE.DAT` is the story's font (1,280 glyphs, 1,222 codes); `FIX.BIN` ASCII; names and QSound are images. Win tally, game over and ranking are shared English UI, not traced (`UI-003`).

### END-003 - Ending text in RAM and on disc; what selects it

- **Status:** `DONE`
- **Milestone:** M6
- **Dependencies:** END-001.
- **Blockers:** None.
- **Objective:** Where each ending surface's text lives in RAM and on the disc, how it gets there, and what selects which ending is shown.
- **Acceptance criteria:**
  - **Dialogue:** `END.BIN`'s scene lists and box records for Jin's ending scenes (16-20 by number), read from the code (as `EXP-0022/box_list.py` did for `STG0AS.BIN`), and checked against the boxes `END-001` saw.
  - **Other text:** for each other surface, the RAM range and the disc file and offset, found by a write breakpoint from a state before it loads, and confirmed by a marker edit in RAM that shows on screen.
  - **Selection:** the code that picks the ending (the pilot byte; whether the machine, the route or the result also matter), traced and checked by forcing one other value and seeing the ending change (no key loops).
  - **Per-pilot scenes:** which of `END.BIN`'s posts run for each roster pilot, from the code, so `ending_scenes_by_number` becomes a per-pilot list from evidence.
- **Notes:** an ending's dialogue copy in `END.BIN` is separate from `STG0AS.BIN`'s (EXP-0024: endings are shown from `END.BIN`'s own copy); `RE-008` left it unchanged except through shared glyphs.
- **Done:** 2026-11-05 (`EXP-0039`, D-036), from the END-001 checkpoint, no cold boot, no keys. Selection: the last-fight round end copies the winner's pilot byte to `0x060CFF7E`; `END.BIN` dispatches on it (`0x060775B4`, lists 0-8). Writing 1 there, or into player 1's pilot byte before the copy, plays Santana's ending (posts 16-22, 22 of 22 boxes as predicted). Dialogue: every list's posts (R4 = list, R5 = scene, 41 constant calls) and opened boxes in `data/text/ending_posts.json`; `END.BIN`'s scene data is `STG0AS.BIN`'s shifted by `0x23ED0` (234 scripts match); Jin's static boxes equal END-001's. Jin's scene 20 is never posted. Other text: `KEND.BIN` (credits and thank-you strings, ASCII, at `0x06060000`), `KEND_1.BIN` (WRAM-L `0x00280000`) and `QSD.PIX` (VDP2 `0x20000`), each loaded raw by `0x06041FB4` (write breakpoints); RAM markers in the strings showed on screen. Per-pilot scenes from code replace `ending_scenes_by_number` (lists 2-8 SUPPORTED, not run).

### END-004 - The arcade's English for the endings

- **Status:** `DONE`
- **Milestone:** M6
- **Dependencies:** END-001 (for the surface list; the MAME work can start alongside `END-002`/`END-003`).
- **Blockers:** None.
- **Objective:** What English the US arcade shows for each ending surface, reached with no play.
- **Acceptance criteria:**
  - **Route:** a headless MAME timeline that reaches Jin's ending in `cybotsu` and `cybotsj` by forcing the stage and the fights (debugger breakpoints or write taps, as `EXP-0032`), repeatable from a fixed NVRAM copy.
  - **Readers:** every reader of English or Japanese text during the ending (read taps on the dialogue tables `0x0A30F6`/`0x0B33AA` and any other table found), with the slots or records read. The reader at `0x97222` reads the three tables by a slot and a language word (seen in `WIN-002`'s listing, not traced); whether it runs in an ending is part of this.
  - **Scripts:** the arcade's ending scene scripts for Jin (list 0, scenes 16 and up, `0x12150`) against the Saturn's, scene by scene, with each difference listed.
  - **Snapshots:** agent-reviewed MAME snapshots of each English surface, matched to the Saturn's surfaces of `END-001`.
- **Notes:** headless MAME needs no focus; no new tool is installed or downloaded.
- **Done:** 2026-11-05 (`EXP-0040`, D-037), headless MAME 0.289, fixed NVRAM copies, menu presses only. Route: one breakpoint at the round end `0xDAE4` (P1 2 round wins, P2 0, ending flag `0xFFEA28`) reaches Jin's ending in `cybotsu` and `cybotsj`; repeat runs byte-identical. The arcade mirrors the Saturn: the winner's pilot byte becomes the ending number `0xFFEB2C`, dispatched to one of 6 routines (`0xE496`). Readers: the story box readers (`0x011F6A`/`0x012014` U, `0x011E7A`/`0x011F0E` J) read slots 408-422, 493, 614, 610 from the English (U) or Japanese (J) table; no table is read after scene 19; `0x97222` and the Spanish table are not used. Scripts: both sets equal; against the Saturn, box N is slot N except the Saturn's blank box 1072 and its speaker names (slot − 9); Mary's scenes 17-18 and Bao and Mao's 20 are arcade-only (`data/arcade/ending_scripts.json`). Surfaces: English dialogue, narration and captions; the US cast roll has Latin names only; no QSound notice in the arcade ending. D-009 corrected: the Japanese table has 624 slots.

### END-005 - Pair Jin's ending with the arcade English (closes M6)

- **Status:** `DONE`
- **Milestone:** M6
- **Dependencies:** END-002, END-003, END-004.
- **Blockers:** None.
- **Objective:** For every text unit of Jin's ending, the official English shown in the same place, by game logic, and what has none.
- **Acceptance criteria:**
  - **Pairing:** `data/translations/jin_ending_pairing.json` (no text): each Saturn unit (box or other surface) with its arcade counterpart, labelled `exact`, `edited` or `no-counterpart`, explained by both games' scripts or readers.
  - **On screen:** at least 3 pairs shown in both games, forced (MAME and the Saturn from the `END-001` checkpoint), agent-reviewed.
  - **Capacity:** the ending's rows, cells and glyph needs measured as `CAP-001` did, against the font and room `END-002`/`END-003` found; any limit stated with its evidence.
  - **New translations:** every unit with no official English listed with its context (no text committed), for the gate; the user decides how it is handled (MSHvSF's lesson: some ending dialogue has no arcade English).
  - **Plan for M7:** `END-010`'s acceptance criteria written from these results (not started).
- **Notes:** the M7 build also needs a `GATE-TRANSLATION` extension for endings (the user's GO).
- **Done:** 2026-11-05 (`EXP-0041`, D-038), static readings and recorded forced runs; no emulator run.
  - **Pairing:** `data/translations/jin_ending_pairing.json`, 31 units. 18 dialogue units are paired by position in both games' scene scripts: 15 `exact`, 3 `edited` with the same wording (box 408's ellipses; the names' unmapped arcade code `0x549`). Box N = slot N; names 605/601 = slots 614/610.
  - **No counterpart (13):** box 1072 (blank, twice), the cast roll's 10 Japanese name images, and the QSound notice's Japanese line.
  - **On screen:** five pairs reviewed side by side (408, 493, 414, 605 + 416, 601 + 419), each Saturn frame while the box is open and each arcade frame between the slot's two reads.
  - **Capacity:** at most 3 rows and 46 of 60 cells a box; 16 cells a row (the widest Saturn line of each surface). 179 pairs, or 160 with the indent, against 335 free codes in `END.BIN`'s own table: no sacrifice. Rows need 872-880 bytes, Jin's own lines hold 828, and lines no ending box shows hold 44,124 (SUPPORTED).
  - **New translations:** none needed. Asked: "Jin's ending cast roll shows 10 Japanese name images (katakana, one in kanji), each above a yellow Latin name such as "Santana=Laurence". The US arcade drops the Japanese line and shows only the Latin name. The Japanese arcade keeps it. There is no official English for these images. How should the translation handle them?" The user's answer, verbatim: "Hide, as US arcade (Recommended)". Asked: "After the credits, the Saturn's QSound notice has five English lines and one Japanese line, "QSound® is a registered trademark of QSound Labs." The English lines above it already say that QSound is a trademark of QSound Labs. The arcade ending shows no QSound notice. How should the translation handle the Japanese line?" The user's answer, verbatim: "Erase the line (Recommended)".
  - **Plan for M7:** `END-010` below.

## Phase L: M7 (One Ending Localized)

M7 puts Jin's ending in English on the disc: the official US arcade English
as paired by `END-005`, drawn as pair glyphs through the ending's own code
table and font copy, with the cast roll's Japanese names hidden and the
QSound line erased. The user gave the gate extension below its GO on
2026-11-05; `END-010` is `DONE` (M7 confirmed), and `END-011` (box timing) is
`BACKLOG`.

### GATE-TRANSLATION extension for Jin's ending

A dated block under `GATE-TRANSLATION`, asked before `END-010` starts. The
user's GO covers:
- the official English as paired (`jin_ending_pairing.json`): 18 units, 30
  lines, unchanged;
- the two handling decisions already given (cast names hidden, QSound line
  erased; `END-005`);
- the speaker-name boxes 605 and 601: lists 3, 4 and 8 post them too, so
  their names turn English while the rest of those endings stays Japanese
  until M8. The other option is a new pair of name boxes for Jin's ending
  alone;
- the budget: no sacrificed code expected (179 pairs, or 160 with the
  indent, against 335 free codes in `END.BIN`'s table). The build stops and
  asks if it needs any.

**2026-11-05: GO for Jin's ending.** Shown: the pairing and capacity of
`END-005` (`EXP-0041`, D-038) and the shared name boxes.
- "GATE-TRANSLATION extension for Jin's ending: may the official US arcade English go on the disc as paired by END-005, unchanged and drawn in pair glyphs? That means 18 dialogue units (30 lines), the cast roll's Japanese names hidden and the QSound line erased, as you chose. No Japanese glyph is expected to be sacrificed (160-179 pairs needed, 335 free codes in the ending's own table); if one is needed, the build stops and asks." → "GO (Recommended)"
- "In Jin's ending, two speaker-name boxes (Gawaine's and Jin's names before a caption) are also shown in three other pilots' endings (lists 3, 4 and 8). Translating them turns those names English in the other endings too, next to Japanese text, until all endings are done (M8). The alternative gives Jin's ending its own copies of the two name boxes, which changes the ending's script and uses more of the scarce room (Jin's own lines are already 44 bytes short). Which?" → "Share, English everywhere (Recommended)"

So `END-010` translates boxes 605 and 601 in place (every ending that
posts them shows the English names), with no sacrificed code. It is
`READY`.

### END-010 - Build Jin's ending in English from the source image (M7)

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M7
- **Dependencies:** END-005, the gate extension above (both done; GO 2026-11-05).
- **Blockers:** None.
- **Objective:** One image, built from the untouched source, that shows Jin's ending in English: every dialogue unit in its official English, the cast-roll names hidden and the QSound line erased, verified box by box from the `END-001` checkpoint.
- **Acceptance criteria:**
  - **Systematic:** the compiler (`tools/text/dialogue.py`, or a module beside it) takes `data/translations/jin_ending_pairing.json` and writes:
    - `END.BIN`'s rows, records (table `0x060817B4`, file `0x217B4`) and code table (file `0x26EAC`);
    - the pair glyphs into `SE.DAT`'s font copy (`0x40000`-`0x67FFF`, D-035).

    The M5 roster changes stay in the same image: `STG0AS.BIN`, `VICTORY.BIN` and `KANJI.BIN` are other files. A second ending later needs only its pairing.
  - **Room:** before the rows use lines beyond Jin's own, a test shows `END.BIN` never reads them. Fill them with a marker, and run Jin's ending and one other ending from their checkpoints: nothing may change (`docs/known_unknowns.md`). Otherwise, find other room.
  - **Cast names:** one controlled experiment finds how to hide a Japanese name image and keep its Latin name (`docs/known_unknowns.md`). The build hides all 10, and screenshots show each Latin name unchanged.
  - **QSound line:** `QSD.PIX` bitmap rows 180-189, over the line's columns only, are set to the background. A pixel diff shows that only the line changed, and a screenshot shows the English lines intact.
  - **Build:** from the untouched source; two builds identical; all sectors valid; source hashes unchanged. Every changed byte range in `END.BIN`, `SE.DAT`, `KEND*.BIN` (if changed) and `QSD.PIX` is accounted for; all other bytes are equal to the source.
  - **Live:** from the `END-001` checkpoint with the built image mounted (`END.BIN`, `SE.DAT`, `KEND*.BIN` and `QSD.PIX` all load after it: `local/end002/control/route.json`):
    - every one of the 18 units draws its predicted cells (`EXP-0039/check_cells.py`'s method);
    - the original image is the control;
    - agent-reviewed screenshots of each scene, the cast roll and the QSound notice;
    - the caption rows 2-3 start where they read correctly (`docs/known_unknowns.md`).
  - **Shared boxes:** per the gate's choice ("Share, English everywhere (Recommended)"), 605 and 601 are translated in place; one other list's ending (3, 4 or 8) is forced and shows those names in English, with its other boxes unchanged.
  - **Regression:** the M5 roster's predictions are unchanged (`data/regression/re008_roster.json`).
  - **Play:** a cold boot of the built image reaches play and shows English story boxes. Cold boots only with the user present, asked first.
  - **Provenance:** `data/translations/jin_ending.json` (no text) and `data/regression/end010_jin_ending.json`.
- **Notes:** endings draw through `END.BIN`'s own copies of the box path, code table and the `SE.DAT` font (D-035), so the story's sacrificed codes do not reach them. The image commit pushes after the agent's checks pass (user rule, 2026-11-02).
- **Done:** 2026-11-05 (`EXP-0042`-`EXP-0045`, D-039-D-042). M7 is met.
  - **Systematic:** `tools.text.dialogue --ending data/translations/jin_ending_pairing.json` (`tools/text/ending.py`): `END.BIN` rows, records and table, `SE.DAT`'s glyphs, and the two image decisions from the pairing's handling entries. 179 pairs, all on unused codes; no sacrifice.
  - **Room (`EXP-0042`, D-039):** marker image, read breakpoints and a positive control. No read of the 1,591 unshown lines while `END.BIN` is resident, in Jin's and Santana's endings. The build uses 64 bytes of it (two rows at `0x0AECC`) beyond Jin's own 828.
  - **Cast names (`EXP-0044`, D-040):** sprite parts of bank 16; the 16 Japanese-name records' size words set to 0 in `KEND_1.BIN`. Every name is hidden and every Latin name kept. The roll is shared by every ending. Asked: "The cast roll (10 portraits, each with a Japanese name image above a yellow Latin name) is the same in every pilot's ending, not just Jin's: Santana's ending shows the identical roll. You chose to hide the Japanese name images, as the US arcade does. Hiding them on disc hides them in every ending's cast roll. Hiding them only in Jin's ending would need a code patch that checks which ending is playing. Which?" The user's answer, verbatim: "Hide in every ending (Recommended)".
  - **QSound line (`EXP-0043`, D-041):** rows 180-190, x 89-300 of `QSD.PIX` set to the background index 255 (index 0 is transparent). The pixel diff is only the line, with no gap.
  - **Build (`EXP-0045`):** two builds identical; 158 sectors changed, all 43,793 valid; source hashes unchanged. Every changed byte of `END.BIN` (910), `SE.DAT` (14,558), `KEND_1.BIN` (32) and `QSD.PIX` (798) is in `ending_changes.json`; the story files equal RE-008's.
  - **Live:** from the END-001 checkpoint all 18 units draw their predicted cells (box 420 confirmed at 1-frame polls); the untouched image is the negative control. The screenshots of each scene, the cast roll and the QSound notice were agent-reviewed. Caption rows 2-3 start under the caption's column.
  - **Shared boxes:** Gawaine's ending (list 4, forced) shows 605/601 in English and his 14 boxes in their original Japanese.
  - **Regression:** RE-008's story files, `prediction.json` and `changes.json` hashes are unchanged.
  - **Play:** asked: "END-010's last check is a cold boot of the built image (M5 roster + Jin's ending): boot, start arcade, pick Jin, and stop once his first two story scenes have shown English. About 5 pad-key presses through System Events in the first 2 minutes (Mednafen comes to the front at each press), then it runs on its own; about 4-5 minutes in all, no key loops. May I run it now?" The user's answer, verbatim: "Yes, run it now (Recommended)". Scenes 21 and 0 drew 6 of 6 boxes in English.
  - **Box timing:** English boxes 409, 493 and 420 finish typing 7, 7 and 4 frames before their timed close (D-042). Asked: "In Jin's ending each dialogue box stays up for a fixed time set by the scene, and text types at about 20 letters a second. Three English boxes (409, 493, 420: 43-45 and 31 glyphs, longer than the Japanese) finish typing only 4-7 frames (under 0.1 s) before the box closes, so the full line is never held on screen; nothing is cut off, and every other box has 1.5-5 s to spare. How should this be handled?" The user's answer, verbatim: "Accept now, follow-up task (Recommended)". It is `END-011`.
  - **Provenance:** `data/translations/jin_ending.json` and `data/regression/end010_jin_ending.json`.

### END-011 - Hold ending boxes whose English barely finishes typing

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M7 follow-up, needed by M8 (`END-023` applies its rule)
- **Dependencies:** END-010 (done).
- **Blockers:** None; scheduled by the user's answer (2026-11-05), not started.
- **Objective:** English boxes 409, 493 and 420 of Jin's ending stay on screen long enough after they finish typing to be read (D-042), with the ending's music and pictures still in step.
- **Acceptance criteria:**
  - **Timer:** one controlled experiment finds the word that sets an ending box's time (in `END.BIN`'s scene scripts or the code that reads them), changing exactly it from the END-001 checkpoint (`docs/known_unknowns.md`).
  - **Effect:** the experiment measures the box's close, the next box's open, and when the scene and track change, against the control.
  - **Rule:** a rule for how long a box holds its finished line (for example, the Japanese box's hold time), applied by the compiler from the prediction, with the user's choice if it moves the ending's timing against its music.
  - **Build and live:** as `END-010`, with every English box holding its full line for at least the rule's time.
- **Done:** 2026-11-05 (`EXP-0048`, D-045).
  - **Timer:** `EAnn` waits for cue `nn` of the list's table (pointers at `0x060879A0`). Raising Jin's cue 2 by 60 moved only box 409's close and 493's open. `E2nn` sets the typing interval: `E203` drew box 409 in 91 frames instead of 181.
  - **Effect:** the script waits for each box's typing, so a box before a wait or the scene end sets when the next scene and its music start (END-010's English moved post 17 by +102 frames).
  - **Rule:** asked: "Ending boxes close on fixed cues, and English needs more glyphs than the Japanese. At today's typing speed (one glyph of two letters every 6 frames, ~20 letters a second), 33 of the 61 English boxes in the six roster endings would hold their finished line for under 1 second, and three scenes can't fit their English at all (the next box gets cut short). Moving the cues inside each scene (never the scene changes, so the music stays in step) fixes part of it; typing twice as fast in endings (~40 letters a second; the same total time) plus moving the cues lets every box hold its full line for at least 0.7 s. How should the endings handle it?" The user's answer, verbatim: "Faster typing + move cues (Recommended)". `tools/text/ending_timing.py` (`--retime`):
    - cued boxes type at 3 frames a glyph and share each run's spare time;
    - boxes before waits or the scene end keep the Japanese time to the next event;
    - leftovers go to the run before, or else to slower typing.
  - **Build and live** (Jin's ending + M5 roster):
    - two builds identical; RE-008's story files and END-010's other files unchanged; `END.BIN` differs only in its 30 timing words;
    - 21/21 boxes draw as predicted;
    - every post, track start and file load falls on the Japanese control's frame;
    - every English box closing on a cue holds its finished line 113-269 frames. Box 415, before the scene end, holds 31 while the screen fades, as in the Japanese.

    `data/regression/end011_jin_timing.json`.
  - **Lists 1-5 (dry runs):** smallest hold 45-86 frames; scene ends within 5 frames. The M8 build checks them live.

## Phase M: M8 (All Roster Endings)

M8: a general ending pipeline. Every roster pilot's ending (lists 0-5,
`RE-005`) is localized by the same mechanism as Jin's, from one roster of
ending pairings, in one image with the story and win quotes, built from the
untouched source. The Saturn-only pilots' endings (lists 6-8) stay out (rule
24, `SPECIAL-001`), except where they share a box with a roster ending.
Nothing in this phase is started. The order is:

1. `END-020` (survey every roster ending's surfaces) and `END-011` (box
   timing), which are independent;
2. `END-021` (pair lists 1-5 with the arcade English);
3. `END-022` (capacity of all six endings together, with `END-011`'s rule);
4. the user's gate extension for the roster endings;
5. `END-023` (the M8 image), which closes M8.

Known so far (facts and their confidence):
- **Posts (D-036, CONFIRMED):** each list's routine posts constant scenes
  (`data/text/ending_posts.json`):

  | List | Pilot | Scenes posted | Box openings | Distinct boxes | Lines |
  | --- | --- | --- | --- | --- | --- |
  | 0 | Jin | 16-19 | 20 | 19 | 31 |
  | 1 | Santana | 16-22 | 22 | 18 | 28 |
  | 2 | Mary | 16 | 4 | 4 | 6 |
  | 3 | Arieta | 16-21, 27, 28 | 24 | 23 | 36 |
  | 4 | Gawaine | 16-19 | 17 | 16 | 29 |
  | 5 | Bao and Mao | 16, 17, 28, 18, 19, 21, 22 | 26 | 21 | 28 |

  91 distinct boxes in all. Boxes 604, 606 and 607 are shown by more than
  one roster ending.
- **Shared with lists 6-8 (D-036):** 601 and 605 (list 8, already English
  since M7, the gate's choice) and the blank 1072 (list 7). No other box.
- **Arcade (D-037, `data/arcade/ending_scripts.json`, CONFIRMED):** both
  sets' scripts are equal. Against the Saturn, box N is slot N except:
  - the blank 1072;
  - most speaker names, which are slot − 9 (601 → 610, 603 → 612, ...).

  Cases a pairing must resolve (HYPOTHESIS until `END-021`):
  - list 5, scenes 18 and 28: Saturn 608 where the arcade opens 615
    (− 9 would be 617), and 606 also stands for 615 elsewhere;
  - list 1, scene 22: Saturn 603 with no arcade slot left over.

  Corrected by `END-020` (D-043): the "arcade-only" scenes are shown. A
  posted script runs on into the next scenes, so Mary's ending shows the
  arcade's scenes 17-18 (boxes 440-447) and Bao and Mao's its scene 20
  (box 486). The observed box sequences are in
  `data/text/ending_surfaces.json`.
- **Shared surfaces (D-040, D-041):** the cast roll and the QSound notice
  are already done for every ending. Whether any ending shows other
  Japanese images is UNKNOWN (only Jin's was surveyed, `END-001`).
- **Capacity (EXP-0041, SUPPORTED as an estimate):** `END.BIN`'s table has
  310 codes no line uses plus 25 new ones. M7 used 179. 816 codes are free
  if only the other endings' lines stay Japanese; for M8 the staying lines
  are lists 6-8's. Room: the roster endings' own lines plus D-039's 43,304
  bytes (less M7's 64).
- **Timing (D-042):** each box's time is set by its scene; longer English
  can finish typing just before the close (`END-011`).

### END-020 - Survey every roster ending's surfaces

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M8
- **Dependencies:** END-010 (done).
- **Blockers:** None.
- **Objective:** For lists 1-5, every surface the ending shows, as `END-001` did for Jin: which carry Japanese, how each is drawn, and whether any is new.
- **Acceptance criteria:**
  - **Reach:** each of lists 1-5 forced from the END-001 checkpoint (`0x060CFF7E`, D-036) on the untouched image, run to the end of the QSound notice. No cold boot.
  - **Surfaces:** every screen with text listed per list (scene, frames, layer, Japanese or English), with agent-reviewed screenshots and their hashes. Any surface not in D-035 gets its drawing path found as `END-002` did (one controlled change), or is recorded as an open question.
  - **Arcade:** the same lists reached in headless MAME (`EXP-0040`'s route with the ending number forced) and their surfaces listed, for the arcade English of each new surface.
  - **Boxes:** each list's box openings and closes, and each box's open time (for `END-011`'s rule).
  - **Records:** `docs/text_surfaces.md` (per list) and `data/text/ending_surfaces.json` (numbers and labels only).
- **Notes:** headless MAME and forced Mednafen runs need no focus.
- **Done:** 2026-11-05 (`EXP-0046`, D-043). No cold boot, no key.
  - **Reach:** lists 1-5 forced from the END-001 checkpoint (`0x060CFF7E`), each to past its QSound notice; every list posted D-036's scenes.
  - **Surfaces:** every second screenshot reviewed (178). All Japanese before the cast roll is `END.BIN` boxes (dialogue with portraits, captions with or without a name, narration); short standalone lines fall in open boxes' windows. After the dialogue every list loads the same `FIX.BIN`, `KEND*.BIN` and `QSD.PIX` and shows the same roll, credits, thank-you screen and QSound notice, which are already handled. No new surface, so no drawing path to find.
  - **Correction (D-043):** D-036's box lists are incomplete. A posted script runs on past `0xE000` into the next scenes, so Mary's ending shows boxes 440-447, 602, 604 and 610 (the arcade's scenes 17-18), and Bao and Mao's shows box 486 (the arcade's scene 20).
  - **Arcade:** EXP-0040's route with the ending number set after the round end's copy (`0xDBBC`/`0xDC12`) plays each list's ending. All 10 routes (both sets) read exactly their scripts' slots; one `cybotsu` run stayed in attract mode and was rerun. The US snapshots show the same kinds in English.
  - **Boxes:** every opening's open and close frames and its last screenshot's hash are in `data/text/ending_surfaces.json`.
  - **Records:** `docs/text_surfaces.md` (a section for lists 1-5) and `data/text/ending_surfaces.json`.

### END-021 - Pair lists 1-5 with the arcade English

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M8
- **Dependencies:** END-020 (done).
- **Blockers:** None.
- **Objective:** Every text unit of every roster ending with its official English, or recorded as having none, by both games' scripts.
- **Acceptance criteria:**
  - **Tool:** `EXP-0041/pair_ending.py` generalized into `tools/text/ending_pairing.py` (lists as an argument). For list 0 it reproduces `data/translations/jin_ending_pairing.json`'s units byte for byte, or every difference is explained.
  - **Pairing:** `data/translations/<pilot>_ending_pairing.json` for lists 1-5 (no text), with the same labels (`exact`, `edited`, `no-counterpart`). The units are the boxes each ending is seen to open (`data/text/ending_surfaces.json`, D-043), not only the posted scripts' boxes; the arcade order is the slots each route read (`EXP-0046`).
  - **Cases:** each case listed in the phase introduction resolved by evidence (the Japanese of both sides, the readers, or a forced run): 608 and 606 ↔ 615, and 603 in list 1's scene 22. Mary's and Bao and Mao's run-on scenes are paired like any other.
  - **On screen:** at least one pair per list shown in both games and agent-reviewed.
  - **New translations:** every unit with no official English listed with its context (no text committed), for the gate.
- **Done:** 2026-11-05 (`EXP-0047`, D-044). No emulator run.
  - **Tool:** `tools/text/ending_pairing.py` aligns the observed openings with the arcade's slot reads; box kinds come from the record header. List 0 reproduces `jin_ending_pairing.json`'s 31 units (slots, labels, similarities, English hashes). The new evidence wording and the `name_rule_slot` field differ; the committed file is kept for END-010's records.
  - **Pairing:** lists 1-5, 102 text units and 4 blank ones. All have official English: 63 exact and 39 with the same wording (punctuation, the colon code, unmapped kanji codes; agent-checked line by line). `cybotsj` reads the same slots as `cybotsu`.
  - **Cases:**
    - 603 (list 1, scene 22): one extra opening of the Santana name, before caption 435, where the arcade opens none. It has official English (slot 612); no new text.
    - 606: Bao, slot 615 by both rules.
    - 608 (list 5, scenes 18, 19, 28): both twins. At the same place the arcade shows slot 615 (Bao alone); slot 617 (box + 9) has the same Japanese and its own English. This is for the gate.
    - Mary's and Bao and Mao's run-on scenes pair like any other box.
  - **On screen:** one pair per list, the same picture and speaker in both games (agent-reviewed; frames and hashes in `EXP-0047`).
  - **New translations:** none.

### END-022 - Capacity of all roster endings together

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M8
- **Dependencies:** END-021, END-011 (both done).
- **Blockers:** None.
- **Objective:** Whether all six endings' English fits `END.BIN`'s table, `SE.DAT`'s font, the room and the box limits, and what it costs if not.
- **Acceptance criteria:**
  - **Measures:** `EXP-0041/capacity.py`'s, for lists 0-5 together:
    - rows, cells and the widest Saturn line per surface;
    - the pairs, as is and with the half-cell indent;
    - row bytes against the room (own lines, then D-039's);
    - each box's hold under `END-011`'s rule (`ending_timing.retime`; dry runs in `EXP-0048/rule.json`).
  - **Codes:** free codes counted by the story's rule, and with the codes only roster-ending lines use. If any Japanese code must be sacrificed, the lines of lists 6-8 it touches are listed (the gate decides).
  - **Options:** each limit stated with its evidence, and the options for the gate, with a recommendation.
- **Done:** 2026-11-05 (`EXP-0049`, D-046). Lists 6-8 forced (no key, no cold boot); the rest static.
  - **Measures:** 100 English boxes; at most 3 rows and 47 cells; no row wider than the Saturn's lines of the same kind (16 cells, names 6).
    - Pairs: 388 as is, 330 with the indent.
    - Rows need 4,920 bytes (4,976 with the indent) against 4,232 in the roster's own lines and 42,844 in lines no ending shows.
    - Every cued box holds 45 frames or more under `END-011`'s rule (`EXP-0048/rule.json`).
  - **Codes:** 335 codes no line uses (310 + 25 new); 930 that no line staying Japanese uses (lists 6-8's 114 lines and the blank 1072). With the indent nothing beyond the 335 is needed. As is, 53 codes of characters only now-English or never-shown lines use; no Japanese on screen changes, and lists 6-8 lose nothing.
  - **Lists 6-8:** they show only their posted boxes (`data/text/ending_surfaces_others.json`), and every ending shows the shared cast roll.
  - **Room correction:** D-039's room had 16 lines that Mary's and Bao and Mao's run-on boxes show; the room is now the lines no list 0-8 is seen to show. M7's rows were not among them.
  - **Options (for the gate):**
    1. Rows with the half-cell indent, as M5 (Recommended), or as is with 53 invisible codes.
    2. Box 608: slot 617, the same Japanese (Recommended), or 615, the arcade's at that place.
    3. The timing rule as chosen.

### GATE-TRANSLATION extension for the roster endings

A dated block under `GATE-TRANSLATION`, asked before `END-023` starts. The
user's GO covers:
- the official English of lists 1-5 as paired (`END-021`);
- box 608 (both twins, list 5): the English of the slot shown at the same
  place (615, Bao alone) or of the slot with the same Japanese (617, both
  twins; D-044);
- any new translations, each listed with its translator;
- the budget from `END-022`: with the half-cell indent no code is
  sacrificed (330 pairs in the 335 free codes); as is, 53 codes that only
  now-English or never-shown lines use, touching no line of lists 6-8;
- `END-011`'s hold rule for all endings (chosen 2026-11-05; it keeps every
  scene change and track start in place), and any box it slows (for
  example Gawaine's 472 at 16 frames a glyph).

**2026-11-05: GO for the roster endings.** Shown: the pairing (`END-021`, D-044), the capacity and options (`END-022`, D-046) and the timing rule (`END-011`, D-045).
- "GATE-TRANSLATION extension for the roster endings: may the official US arcade English go on the disc for the endings of Santana, Mary, Arieta, Gawaine, and Bao and Mao, as paired by END-021, unchanged and in pair glyphs? That is 102 text units (63 matching the arcade's Japanese exactly, 39 with the same wording), no new translations, built together with Jin's ending in one image." → "GO (Recommended)"
- "The six endings need 388 two-letter glyphs as plain rows, but only 335 codes are unused by any Japanese line. With the half-cell indent the story already uses (some rows start half a glyph in so rows share glyphs), they need 330 and fit with no Japanese character touched. Plain rows would take 53 codes whose Japanese characters appear only in lines that become English or are never shown, so nothing visible changes either way. Which?" → "Indent, as the story (Recommended)"
- "In Bao and Mao's ending, one Saturn speaker name reads "Bao Mao:" (both twins). At those three places the arcade shows "Bao:" instead, but the arcade also has an official "Bao Mao:" name line that matches the Saturn's Japanese exactly. Which English should the Saturn show there?" → "Bao Mao: (Recommended)"
- "The timing rule you chose (faster typing + moved cues) keeps every scene change and music start on its Japanese frame. To do that, five very short English lines type slower than the Japanese so their scenes keep their length: one in Arieta's ending (5 frames a glyph), one in Gawaine's (16 frames a glyph: a 5-glyph shout over about 1.3 s) and three in Bao and Mao's (6-10). Every other box holds its finished line at least 0.75 s. Accept the rule for all six endings?" → "Accept the rule (Recommended)"

So `END-023` builds lists 0-5 with the half-cell indent across the ending rows (330 pairs in the 335 free codes, no sacrifice), box 608 from slot 617, and `--retime` on every ending. It is `READY`.


### END-023 - Build all roster endings in English (M8)

- **Status:** `DONE` (2026-11-05)
- **Milestone:** M8
- **Dependencies:** END-021, END-022, the gate extension above (all done; GO 2026-11-05).
- **Blockers:** None.
- **Objective:** One image, built from the untouched source, with the M5 story and win quotes and all six roster endings in English, verified box by box.
- **Acceptance criteria:**
  - **Systematic:** the compiler takes a roster of ending pairings (`data/text/m8_endings.json`) in place of one `--ending`. One allocation over `END.BIN`'s table and `SE.DAT`'s font, one room. `END-011`'s rule is applied. No list-specific code.
  - **Build:** as `END-010`:
    - from the untouched source; two builds identical; all sectors valid; source hashes unchanged;
    - every changed byte accounted for;
    - RE-008's story files, prediction and changes unchanged.
  - **Live:** each of lists 0-5 forced from the END-001 checkpoint: every unit draws its predicted cells; agent-reviewed screenshots of each scene. Jin's units draw the same cells as in `end010_jin_ending.json`, unless the hold rule changed a row (listed).
  - **Others:** each of lists 6-8 forced: its boxes draw their original cells, except the shared boxes as recorded. Every one of lists 0-8 is forced on the built image, since the unshown room is marker-tested only in lists 0-1 (`EXP-0049`).
  - **Coverage:** `docs/coverage_exceptions.md` gains the endings: every box of every list's posts either built or excluded with evidence (lists 6-8, arcade-only scenes, blank boxes).
  - **Play:** a cold boot of the built image reaches play and shows English story boxes. One roster ending other than Jin's is reached in that boot by RAM writes, as `END-001` did, and shows its English. Cold boots only with the user present, asked first.
  - **Provenance:** `data/translations/<pilot>_ending.json` (no text) and `data/regression/end023_roster_endings.json`.
- **Notes:** M8's image supersedes M7's as the latest. The image commit pushes after the agent's checks pass (user rule, 2026-11-02).
- **Done:** 2026-11-05 (`EXP-0050`, D-047). M8 is met.
  - **Systematic:** `--endings data/text/m8_endings.json` (`ending.compile_endings`): one allocation (330 pairs, no `END.BIN` sacrifice), one room, the indent, box 608 → 617, `--retime` on every list, observed boxes of lists 0-8. END-011's build reproduces byte for byte with the refactored code.
  - **Build:** two builds and six records identical; every changed byte accounted for; 202 sectors changed, all valid. RE-008's story files, `prediction.json` and `changes.json` are unchanged; `KANJI.BIN` differs by one glyph (below).
  - **Fixes found by the live check:**
    - Lists 6-8 draw with `KANJI.BIN`, so the shared names were garbled in list 8, a fault since M7. The names now take the story's codes, plus one pair at the story's 153rd sacrifice code. Asked: "The three Saturn-only pilots' endings draw their text with the story font (KANJI.BIN), not the endings' font. So the two speaker names shared with them since M7 ("Jin:" and "Gawaine:") show as garbled glyphs in the Shade ending (list 8): a bug that has been in the image since M7, found now by M8's live check. Story glyphs cover every pair except one: ": " (colon + space). Fixing it means adding that one glyph to the story font at the code of a Japanese character used only in lines that are already English or never shown, so nothing visible changes, but KANJI.BIN differs from M5's by one glyph. How should M8 handle it?" The user's answer, verbatim: "Add the one glyph (Recommended)". Corrected and asked: "Correction to my last question: no invisible code is left in the story font. M5's 152 sacrificed codes already took every code no visible line uses. The closest option is M5's own next code (153rd of the 160 you approved for M5, same rarest-first rule): it would put the ": " glyph in place of one kanji in one line (line 1052) of the first Saturn-only pilot's story, text that stays Japanese until those pilots are done. That makes "Jin:" and "Gawaine:" read correctly in the Shade ending. Which?" The user's answer, verbatim: "Use M5's 153rd code (Recommended)".
    - Typing counts full-width spaces (Arieta's 455 had moved her scene 27 by 23 frames).
  - **Live:** all nine endings forced on the built image. Every box draws as expected (lists 6-8 against the built `KANJI.BIN`; 601/605 in English). Scene changes and track starts are on the Japanese frames within 6 frames, and the cued English boxes hold 42-116 frames at the least.
  - **Coverage:** `docs/coverage_exceptions.md`, "M8 Endings".
  - **Play:**
    - From the REF-005 play state with the ending number forced, Arieta's ending plays in English (26/26 boxes).
    - Asked: "END-023's play check is a cold boot of the M8 image (story, win quotes and all six roster endings): boot, start arcade, pick Jin, and stop once his first story scenes have shown English, as in END-010. About 5 pad-key presses through System Events in the first 2 minutes (Mednafen comes to the front at each press), then it runs on its own; about 6-7 minutes in all, no key loops. A separate run, already going and pressing no keys, plays from your REF-005 play state into Arieta's ending on the same image. May I run the cold boot now?" The user's answer, verbatim: "Yes, run it now (Recommended)". The cold boot reaches play: scenes 21 and 0, 6/6 English boxes.
  - **Provenance:** `data/translations/<pilot>_ending.json` (six) and `data/regression/end023_roster_endings.json`.

## Phase N: Boot-Time Messages (`UI-004`)

The outline scheduled `UI-004` early after M5, and lesson 5 of
`docs/lessons_from_xvsf.md` puts it in the first backlog: in both siblings
the user added boot, cartridge and save warnings mid-project. The user asked
for these tasks (verbatim, 2026-11-05): "Write up UI-004". All of it is done
(2026-11-06). The order is:

1. `BOOT-001` (census: which message shows under which condition);
2. `BOOT-002` (where each message is stored and how it is drawn);
3. `BOOT-003` (English text and lettering; the user's gate extension);
4. `BOOT-004` (the build, on top of the M8 image);
5. `BOOT-005` (verify and register), which closes `UI-004`.

Known so far (facts and their confidence):
- **No warning at boot or in attract** (D-003, `EXP-0002`, CONFIRMED for
  what was tested): `ss.cart` `none`, `backup`, `extram1` and `extram4`,
  one 120 s cold boot each, showed no warning. Only boot and attract were
  tested, with the homes' normal backup memory; a check at Start, at a
  save, or with other backup memory is not excluded.
- **Candidate files** (`references/saturn_jp/iso_listing.json`; names and
  sizes only):

  | File | Bytes | SHA-256 (first 12) |
  | --- | --- | --- |
  | `WARNING0.PIX` | 122,880 | `0524f6f8ddd3` |
  | `WARNING1.PIX` | 122,880 | `d7b190a19d38` |
  | `WARNING2.PIX` | 122,880 | `c3054ae2b8f0` |
  | `WARNING3.PIX` | 122,880 | `9a790f138f90` |
  | `WARNING4.PIX` | 131,072 | `66ff1b0d42b5` |

  - 122,880 is 512 × 240 bytes and 131,072 is 512 × 256, the size of
    `QSD.PIX`, a raw 512 × 256 256-colour VDP2 bitmap (D-035). That the
    `WARNING` files share its format is arithmetic only: **HYPOTHESIS**.
  - `CYBER.BIN` holds the five names in a table of 16-byte entries from
    file offset `0x39168` (static search, 2026-11-05). No other extracted
    file names them. Which code reads that table, and when, is **UNKNOWN**.
  - There are no `ERR*.BIN` files (the siblings' warnings).
- **Siblings (HYPOTHESIS for Cyberbots, rule 13):** MSHvSF and XvSF each
  showed five boot warnings as whole bitmaps: no cart or a backup cart, a
  1 MB cart, unformatted backup memory, a damaged save, too little free
  memory. Cyberbots runs with no cart (D-003), so its warnings may be about
  backup memory only, or something else.
- **Tools:** `tools/mednafen/backup_ram.py` (copied from MSHvSF via XvSF)
  writes backup-memory fixtures: unformatted, N blocks free, a damaged copy
  of a real save. Its layout was checked on the siblings' saves only, so it
  is re-checked on a Cyberbots save before use.
- **Policy** (`docs/localization_policy.md`): text with no official English
  gets a recorded new translation, the translator named and source hashes
  kept, approved by the user surface by surface. Absence of official
  English must be shown, not assumed. The references are arcade-only
  (`REF-002` `REJECTED`).
- **Scope:** only the game's own messages. The Saturn BIOS's screens
  (memory manager, CD player, "no disc") are not the game's and stay out.
- **Run rules:** each cold boot is asked first, with the user present. Key
  presses are menu keys only, never loops. Saves and backup-memory files
  stay under ignored paths, recorded by hash.

### BOOT-001 - Census of the boot-time messages

- **Status:** `DONE` (2026-11-06, `EXP-0051`, D-048)
- **Milestone:** Boot-time messages (`UI-004`)
- **Dependencies:** EMU-004, EMU-021 (done).
- **Blockers:** None.
- **Objective:** List every message the game can show about its cartridge
  or backup memory, with the condition that shows it.
- **Acceptance criteria:**
  - **Code first:** the readers of `CYBER.BIN`'s `WARNING*.PIX` table are
    found (static disassembly, then a read breakpoint on the table in a
    running game). Each branch that leads to a load is listed with the
    condition it tests (cart, backup memory, a save's contents, or other)
    and when it runs (boot, Start, a save, other).
  - **Triggers:** each condition the code tests is made in Mednafen, one
    change at a time from the untouched image, recorded by setting or
    fixture hash:
    - backup memory: unformatted, nearly full (around the code's limit),
      holding a damaged save of this game (made from a real save, the
      damage recorded), and a normal save (control);
    - cart: only if the code tests it (D-003 saw no warning with any cart);
    - any other condition the code tests.

    A condition that needs a cold boot is asked first. One that can be made
    from a saved state (for example by writing backup memory in RAM before
    the check runs) is made that way where the code shows it is equivalent.
  - **Screens:** each message screen is captured (screenshot hash, frame).
    The agent transcribes and translates it, and records what each button
    does there. A screen that is the BIOS's is recorded as such and left
    out.
  - **Unreachable:** a condition the code tests that Mednafen cannot make
    is listed with the reason, and its file is shown by forcing the branch.
  - **Record:** `docs/text_surfaces.md` gets one row per message, replacing
    the "Not Seen Yet" row.
- **Notes:** if the code reads no `WARNING` file in any reachable path,
  record that with the evidence and stop the phase there (the user
  decides). Method: XvSF `BOOT-001` (`EXP-0053`).
- **Done:** 2026-11-06 (`EXP-0051`, D-048).
  - **Code first:** one save check (`0x06036C3E`), called once by the
    start-up code before the title; the picture routine `0x06036DA8` has
    three callers, all in it. Its tests: the BIOS backup status of the
    internal memory and of a cart, the save's checksum (or read failure),
    and the free space where no save exists.
  - **Triggers:** nine cold boots of the untouched image, one fixture each
    (hashes in `EXP-0051`). Asked: "BOOT-001 needs cold boots of the
    untouched image, one per backup-memory condition, because the game
    checks its save only once at power-on. Planned: 9 boots, one at a time,
    in throwaway copies of the silent home: a normal save (control);
    unformatted memory; 4, 5 and 6 blocks free; a damaged save; then a save
    cartridge (normal, unformatted, and unformatted with unformatted
    internal memory). No key presses. Each opens a Mednafen window for
    about a minute; about 15 minutes in all. May I run them now?" The
    user's answer, verbatim: "Yes, run all 9 (Recommended)".
  - **Screens:** five, one per picture, each captured with its file in VDP2
    VRAM byte for byte; transcribed and translated by the agent (kept
    locally). No BIOS screen came up. `WARNING1`-`3` lead to the BIOS on a
    button, `WARNING0` and `WARNING4` let the game start: SUPPORTED by the
    code and the screens' words. A RAM-written button was not seen by the
    CPU (probably its cache), so a real press is left to `BOOT-005`.
  - **Unreachable:** a read failure of an intact save and internal status 1;
    both show pictures already captured, so no branch needed forcing.
  - **Record:** `docs/text_surfaces.md`, "Boot-Time Warnings".

### BOOT-002 - Where each message is stored and how it is drawn

- **Status:** `DONE` (2026-11-06, `EXP-0052`, D-049)
- **Milestone:** Boot-time messages (`UI-004`)
- **Dependencies:** BOOT-001.
- **Blockers:** None.
- **Objective:** For each message in `BOOT-001`, find the data the game
  draws and the drawing path, so that an English version can be built.
- **Acceptance criteria:**
  - **Location:** per message, the file and offset (or code address) of its
    text or picture, CONFIRMED by a controlled change: altering those bytes
    in a test build from the untouched source changes that screen and
    nothing else. The file a screen reads is shown by a load log or a
    single-file change, not by its name.
  - **Format:** for a picture, its size, pixel format and palette (where
    the palette comes from), decoded and drawn back out to match the
    screenshot pixel for pixel; how it reaches the screen (VDP1 or VDP2,
    layer, VRAM address). For text, its encoding and font.
  - **Room:** what an English version may use: the picture's size, visible
    rows and columns, and colours; or the text's space and glyphs.
- **Notes:** if a message is drawn from code or a font rather than a
  picture, record it here and adjust `BOOT-004` before it starts.
- **Done:** 2026-11-06 (`EXP-0052`, D-049).
  - **Location:** each screen draws its own `WARNINGn.PIX` whole. A test
    image from the untouched source with a marker in each file changed only
    that screen's marker under each condition, and a normal boot not at
    all. Asked: "BOOT-002's controlled change: a test image (built from the
    untouched source, never shipped) with a coloured marker in each of the
    five warning pictures. To show that each screen reads its own file, and
    where the visible edge is, I need 6 cold boots of that test image, one
    at a time with no key presses: the five warning conditions from
    BOOT-001 (same fixtures), plus one normal-save boot as a control to
    confirm nothing else changed. Each opens a Mednafen window for about a
    minute; about 8 minutes in all. May I run them now?" The user's
    answer, verbatim: "Yes, run all 6 (Recommended)".
  - **Format:** 512 bytes a row, one byte a pixel (values 0-15), no
    header; VDP2 NBG1, a 256-colour 512 × 256 bitmap at `0x20000`, the
    only layer on. The 16 colours come from `CYBER.BIN` `0x06053AAC`, not
    the file. All five redraw with 0 differing pixels.
  - **Room:** 352 × 224 visible pixels (file columns 0-351, rows 0-223; a
    marker at rows 228-231 did not show, and VRAM writes put the edge
    between rows 223 and 224); 16 fixed colours (0 transparent); the
    files' sizes fixed. The Japanese uses columns 24-328, rows 20-210.

### BOOT-003 - English text and lettering (gate extension)

- **Status:** `DONE` (2026-11-06, `EXP-0053`)
- **Milestone:** Boot-time messages (`UI-004`)
- **Dependencies:** BOOT-001, BOOT-002.
- **Blockers:** None.
- **Objective:** An English text for every message, from an official source
  where one exists, otherwise a recorded new translation the user approves.
- **Acceptance criteria:**
  - **Official English:** looked for, with each search recorded:
    - the arcade has no cartridge or backup memory; its boot and service
      messages are checked for any shared wording (`cybotsu` program,
      `local/ref003/`);
    - the US Saturn BIOS already in the homes (`EMU-002`) is checked for its
      backup-memory terms (for example the memory manager's name), by its
      own screens.
  - **New translation:** where no official English exists, a translation by
    the agent, with the translator named and each source screen's hash
    kept. Each line fits `BOOT-002`'s room. Stored in
    `data/translations/boot_warnings.json` (no Japanese text committed).
  - **Decision:** the user sees every message's meaning beside its proposed
    English and approves it in their own words, as a `GATE-TRANSLATION`
    extension recorded here and in `docs/localization_policy.md`. A
    sibling's approved wording may be offered as an option, labelled as
    that sibling's.
  - **Style:** the user also chooses the lettering (for a picture: font,
    size and colours) from rendered samples.
- **Done:** 2026-11-06 (`EXP-0053`).
  - **Official English:** none. The arcade has no cartridge or save
    message; its only shared word is its region screen's title, "WARNING".
    Both Saturn BIOS files (the same as XvSF's, whose screens it recorded)
    give "Manage Memory", "Memory Manager", "System Memory", "Cartridge",
    "Clear", "Not Formatted".
  - **New translation:** by Claude (the agent), every screen within the
    room (widest line 288 px, lowest row 207), with the source screens'
    hashes, in `data/translations/boot_warnings.json`.
  - **Decision:** recorded below and in `docs/localization_policy.md`.
  - **Style:** the arcade font in the Japanese colours, from rendered
    sheets.

### GATE-TRANSLATION extension for the boot warnings

- **Status:** `DONE` (2026-11-06)
- **Scope:** the five boot warnings, `WARNING0`-`4.PIX` (D-048, D-049).
- **Asked** (2026-11-06), after the sheets were sent (the Japanese beside
  the draft English in the arcade font; the same drafts in `FIX.BIN`'s
  font), and the user's answers, verbatim:
  - "The five boot warnings have no official English, so the English is a
    new translation by Claude (the agent), as your policy allows with your
    approval. The drafts in the sheet I just sent follow the Japanese
    closely, using the Saturn BIOS's own names ("Memory Manager", "System
    Memory", "Cartridge Memory") and the arcade's title word "WARNING". Do
    you approve the draft wording?" → "Approve the drafts (Recommended)"
  - "Three of the warnings (unformatted memory) end with "press any button
    to go to the multiplayer screen": the Japanese name for the Saturn's
    built-in screen you get with no game running (CD player, Manage
    Memory). XvSF's user chose "control panel" for the same screen. What
    should the English call it?" → "control panel (Recommended)"
  - "The out-of-space warning says this game needs "05" blocks free. But
    the game actually checks for a bit more: with exactly 5 free blocks it
    still shows the warning; 6 is the real minimum (measured in BOOT-001).
    Your policy makes fixes opt-in. Which number should the English show?"
    → "6, what the game checks"
  - "Which lettering for the English warning pictures? (Sheets sent just
    now.)" → "Arcade font, Japanese colours (Recommended)"

So `BOOT-004` builds the five pictures from `data/translations/
boot_warnings.json` in the arcade letters and the Japanese colours. It is
`READY`.

### BOOT-004 - Build the English messages

- **Status:** `DONE` (2026-11-06, `EXP-0054`, D-050)
- **Milestone:** Boot-time messages (`UI-004`)
- **Dependencies:** BOOT-002, BOOT-003, END-023 (done).
- **Blockers:** None.
- **Objective:** Every boot-time message in English, built from the
  untouched source on top of the M8 image's changes.
- **Acceptance criteria:**
  - **Generator:** a script makes each replacement (picture or text) from
    the approved data, with checks of its format against `BOOT-002`. The
    generated files' hashes are recorded. No game file or picture is
    committed (rule 21); the script, its tests and the approved English are.
  - **Build:** `dialogue.py` (or the build entry point then current) takes
    the messages as an option. Two builds are identical; every changed
    range is listed with its original and new bytes (rule 12); every
    changed file fits its sectors; all sectors pass EDC/ECC; the source
    hashes are unchanged.
  - **Screens:** every message `BOOT-001` triggered is shown in English on
    the built image (and a forced branch for any unreachable one) and
    checked by the agent against the generated file and the approved text,
    pixel for pixel.
  - **No other change:** apart from the message files, the image equals
    the M8 build (`data/regression/end023_roster_endings.json`), and a
    normal boot with a normal save is unchanged.
- **Notes:** both name variants (`LOC-001`, `OPT-001`) are not built yet;
  whichever comes later carries these changes.
- **Done:** 2026-11-06 (`EXP-0054`, D-050).
  - **Generator:** `tools/text/boot_warnings.py` (with tests), from the
    approved file; each picture checked for size, values and unchanged
    hidden bytes. Hashes: `WARNING0` `66c4d4b2…`, `WARNING1` `538c4902…`,
    `WARNING2` `580ef4d1…`, `WARNING3` `75c696a6…`, `WARNING4` `29da7ffc…`.
  - **Build:** `--boot-warnings` with the M8 options (Track 01
    `ef27ebc6…`); two builds identical; ranges with original and new hashes
    in `boot_changes.json`; 208 sectors changed against M8, all in the
    pictures; 0 invalid sectors.
  - **Screens:** five cold boots, one per condition, each 0 pixels from its
    built picture, read by the agent against the approved text. Asked:
    "BOOT-004's screen check: the built image (M8 plus the five English
    warnings) needs 6 cold boots, one at a time with no key presses: the
    five warning conditions (same fixtures as before), plus a normal-save
    boot to confirm nothing else changed. I compare each screen pixel for
    pixel with the generated picture. Each opens a Mednafen window for
    about a minute; about 8 minutes in all. May I run them now?" The
    user's answer, verbatim: "Yes, run all 6 (Recommended)".
  - **No other change:** every M8 output and record equal `end023`'s; the
    normal-save boot equals the untouched image's.
  - **Provenance:** `data/regression/boot004_boot_warnings.json`.

### BOOT-005 - Verify and register

- **Status:** `DONE` (2026-11-06, `EXP-0055`)
- **Milestone:** Boot-time messages (`UI-004`)
- **Dependencies:** BOOT-004.
- **Blockers:** None.
- **Objective:** Play-check the English messages and lock the build.
- **Acceptance criteria:**
  - **Play check:** cold boots of the built image under each condition
    `BOOT-001` could trigger, run by the agent with the user present and
    asked first, show the English screens; one normal boot reaches the
    title.
  - **Regression:** a reference in `data/regression/` with the build's
    hashes, and the earlier references still match.
  - **Coverage:** `docs/coverage_exceptions.md` lists any message left in
    Japanese, or only forced, and why.
  - **README:** the "Still Japanese" list and the build commands are
    updated.
- **Notes:** the image commit pushes after the agent's checks pass (user
  rule, 2026-11-02).
- **Done:** 2026-11-06 (`EXP-0055`). `UI-004` is done.
  - **Play check:** six cold boots of the built image, run by the agent
    with the user present. Asked: "BOOT-005's play check: 6 cold boots of
    the built image, one at a time. Five boots each show one English
    warning and then get exactly one pad-button press (A), to confirm what
    a button does there: the damaged-save and out-of-space warnings should
    let the game start, the three unformatted-memory warnings should go to
    the Saturn's control panel. Each press brings Mednafen to the front for
    about a second (System Events), then gives focus back; no key loops.
    The sixth boot is a normal save with no key, running to the title.
    About 12 minutes in all. May I run them now?" The user's answer,
    verbatim: "Yes, run all 6 (Recommended)". Each warning showed its
    English (the same screens as `BOOT-004`); A went on into the game on
    `WARNING0` (the save rewritten) and `WARNING4`, and to the control
    panel on `WARNING1`-`3`; the normal boot reached the title.
  - **Regression:** `data/regression/boot004_boot_warnings.json` (new);
    `re003`, `re007`, `re008`, `end010` and `end011` rebuild to their
    recorded hashes; `end023` is reproduced by `BOOT-004`.
  - **Coverage:** `docs/coverage_exceptions.md`, "Boot Warnings": no boot
    message left in Japanese.
  - **README:** "What's Changed", "Still Japanese" and "Build the Patch"
    updated.

## Phase O: Name Art (`LOC-001`)

The user asked for these tasks (verbatim, 2026-11-06): "Write up LOC-001".
`LOC-001` to `LOC-006` are done (2026-11-06). The order is:

1. `LOC-001` (census of every name-art surface, and what the US arcade
   shows on each);
2. `LOC-002` (storage and drawing, and whether Latin art is on the disc)
   and `LOC-003` (voice), which are independent;
3. `LOC-004` (the user's plan per surface; a gate extension for any new art
   or romanization);
4. `LOC-005` (the Latin-art build, the default);
5. `LOC-006` (verify and register).

The switch itself is `OPT-001` (outline), after this phase: this phase
gives the default Latin art and keeps the katakana art intact and
addressable, so that the switch can choose between them.

Known so far (facts and their confidence):
- **Names (D-013, CONFIRMED):** one set of names in both regions; the
  English text already uses the arcade's. Only the **art** differs: the
  pilot-select name under each portrait and the VS screen's pilot and mech
  names are katakana on the Saturn and the Japanese arcade, Latin on the US
  arcade (`docs/names.md`). The HUD and `MACHINE SELECT` are Latin
  everywhere.
- **VS-screen art (D-013, CONFIRMED):** VDP1 sprites stored uncompressed in
  `SELECT.VAD`, for example a pilot name (64 × 15, 4 bpp) at `0x1EE80` and a
  mech name (104 × 23) at `0x1F0A0`.
- **Pilot-select art:** where it is stored is **UNKNOWN** (not looked at).
- **Latin name art on the disc: UNKNOWN.** Not found next to the katakana in
  `SELECT.VAD` (`EXP-0012`, a render of the neighbouring data). Two leads,
  both **HYPOTHESIS**:
  - the ending cast roll has Latin pilot names as sprite parts
    (`KEND_1.BIN`, odd frames `0x1B6`-`0x1C9`, D-040), in its own style;
  - the US arcade's Latin art, in the CPS-II graphics ROMs (not decoded),
    as a model to draw from if the Saturn has none.
- **Pilots without arcade English:** Tessan has no arcade spelling; the
  other console-only pilots (Chiyomaru, Devilotte, SHADE) do (`docs/
  names.md`). Whether each shows name art on these screens is not yet
  recorded.
- **Voice: UNKNOWN.** Whether any name is spoken was never checked. Names
  are the same in both regions, so a spoken name would not conflict with
  the Latin art; it is checked for completeness.
- **Siblings (HYPOTHESIS for Cyberbots, rule 13):** in MSHvSF every US-name
  asset was already on the disc; in XvSF the US art was on the disc for
  some surfaces and spelled from existing letters for others. Their
  variants differed by 58 KB of font (MSHvSF) and 243 bytes (XvSF): the
  difference here is measured early (`LOC-002`).
- **Policy** (`docs/localization_policy.md`, "Names, Refined"): Latin art
  by default, katakana by an Options switch (`OPT-001`). New art or a new
  romanization is new work, approved by the user like a new translation.
- **Run rules:** cold boots and key presses only with the user present and
  asked first; no key loops; the agent reviews the screenshots.

### LOC-001 - Census of every name-art surface

- **Status:** `DONE` (2026-11-06, `EXP-0056`, D-051)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** REF-007 (done), BOOT-005 (done; the current image).
- **Blockers:** None.
- **Objective:** List every place the game shows a pilot or mech name as
  art, with what the Saturn shows and what the US arcade shows there.
- **Acceptance criteria:**
  - **Surfaces:** each with screen evidence (screenshot SHA-256 and frame),
    from saved states where one exists, otherwise from a cold boot with the
    user present:
    - the pilot select, for every portrait it shows (including any reached
      only by a code or a hidden cursor position, recorded as such);
    - `MACHINE SELECT` and `BODY TYPE`;
    - the VS screen, pilot and mech names, for both sides;
    - the versus mode's select and VS screens, if they differ;
    - win and continue screens, the ending and cast roll (Latin since
      D-040), rankings and initials, options and any menu that lists
      pilots or mechs.

    A surface is recorded as showing no name only after it has been seen.
  - **Both arcade conventions:** the same surfaces in `cybotsu` (US) and
    `cybotsj` (Japan) in MAME 0.289, headless, per surface, so the US
    arcade's Latin forms (spelling, case, which mechs are named) are known.
  - **Names without US art:** pilots or mechs the US arcade never shows
    (the console-only pilots, Tessan) are listed with what the Saturn shows.
  - **Output:** `docs/names.md` gains a surface × name table with the
    Saturn and US evidence; unobserved cells are UNKNOWN.
- **Notes:** observes only; changes nothing on the disc. Method: XvSF
  `LOC-001` (`EXP-0048`).
- **Done:** 2026-11-06 (`EXP-0056`, D-051), with one surface left open.
  - **Surfaces:** from session states with RAM writes of the drawn
    record's frame (no key, no cold boot): every pilot's select name (9),
    every VS pilot name (9) and mech name (16). Name art appears only on
    the pilot select and the VS screen; `MACHINE SELECT`, the HUD, round
    end, bonus, continue, game over, initials, options, `VICTORY!`,
    `RESULT` and the cast roll are Latin or nameless. Not reached:
    versus mode's own select, VS and `SET UP` screens (moved to `LOC-002`).
  - **Both arcade conventions:** MAME runs of `cybotsu` and `cybotsj`
    (select cursor, picks, body types): US Latin in mixed case for pilots,
    capitals for `SHADE` and the mechs, no model codes; Japanese like the
    Saturn. The US art for mech variants was not reached.
  - **Names without US art:** Devilotte (デビロット姫), Chiyomaru (千代丸);
    Tessan has no name art on these screens.
  - **Output:** `docs/names.md`, "Name-Art Census".

### LOC-002 - Where each name surface is stored, and whether Latin art exists

- **Status:** `DONE` (2026-11-06, `EXP-0057`, D-052)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** LOC-001.
- **Blockers:** None.
- **Objective:** For each surface in `LOC-001`, find the drawing path and
  the stored art, and whether a Latin version is on the disc.
- **Acceptance criteria:**
  - **Location:** per surface, the VDP1 command or VDP2 tile, then its VRAM
    data, then the file and offset it is loaded from, CONFIRMED by a
    controlled change (a RAM change from a saved state, or a test build)
    that alters only that name on screen.
  - **Table:** the code and table that choose each name's art (by pilot or
    mech number), so that a build can point it elsewhere.
  - **Latin art:** present or absent, per surface. "Present" needs the art
    found and shown on screen by a controlled change. "Absent" needs the
    reader traced to its table, showing that no entry holds Latin art; a
    data search alone is not enough. The cast-roll Latin names (D-040) are
    checked as a candidate source.
  - **Room:** for each surface, the size, colours and storage a Latin
    replacement may use, and whether the katakana art can stay on the disc
    beside it (needed for `OPT-001`).
  - **Variant difference:** the bytes that would differ between a Latin and
    a katakana build, counted early.
- **Notes:** if a surface turns out to be text in a font rather than art,
  record it here and adjust `LOC-005` before it starts. Carried from
  `LOC-001`: versus mode's own select, VS and `SET UP` screens were not
  reached; check them for name art first (a state there, or a cold boot
  with the user present). Leads: D-051's records and tables; `CYBER.BIN`'s
  Latin pilot and mech lists; the cast roll's Latin names (D-040).
- **Done:** 2026-11-06 (`EXP-0057`, D-052).
  - **Location:** select names are raw art in `SELECT.VAD` (`0x17840`-
    `0x19B20`); VS pilot and mech names are compressed type-2 records in
    `PL3F_0.BIN` (`0x4324`-`0x97..`). CONFIRMED by a test image marking
    Jin's select name and two VS records, read by the game from saved
    states before the loads: exactly those names changed.
  - **Table:** D-051's records → bank 56 / bank 63 frame tables → parts →
    patterns (`SELECT.VAD` offset, or `PL3F_0.BIN` record).
  - **Latin art:** absent for every pilot and mech name: all 149 frames of
    bank 56 and all 122 of bank 63 were drawn. Present elsewhere: the cast
    roll's Latin names (`KEND_1.BIN`), `CYBER.BIN`'s text lists, and a
    Latin "G.O.D." banner in bank 63 (use unknown).
  - **Room:** Latin select names fit in place; VS names need about 7.8 KB
    more than their records in a literal-only encoding, so in place they
    need compression (more of the type-2 format) or other space. Neither
    file can also keep the katakana for `OPT-001`.
  - **Variant difference:** about 29.7 KB if replaced in place (the two
    ranges).
  - **Versus mode** (carried from `LOC-001`): one cold boot, asked: "LOC-002
    still has to check versus mode's own screens (its pilot select, a "SET
    UP" screen with handicap and rounds, and its VS screen) for name art.
    No saved state reaches them, so it needs one cold boot of the untouched
    image with about 12 single pad-key presses for both players (Start,
    down to VERSUS MODE, pick a pilot and mech for each side, confirm the
    setup), one at a time, with a screenshot checked before each press.
    Each press brings Mednafen to the front for about a second; no key
    loops. About 5 minutes. May I run it now?" The user's answer,
    verbatim: "Yes, run it now (Recommended)". Same art, nothing new.

### LOC-003 - Names in voice

- **Status:** `DONE` (2026-11-06, `EXP-0058`)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** LOC-001.
- **Blockers:** None.
- **Objective:** Find whether any pilot or mech name is spoken, and when.
- **Acceptance criteria:**
  - **Moments:** select, VS screen, round start, win and the story's voiced
    scenes, from saved states, with sound, for at least two pilots.
  - **Listening:** the user is the sound oracle. Each candidate clip is
    given to the user one at a time, never several at once; the user says
    whether a name is spoken and which.
  - **Record:** `docs/names.md`, per moment. No change is planned: the
    names are the same in both regions (D-013), so speech cannot disagree
    with the art. If a spoken name ever differs from the text, it is
    recorded and put to the user in `LOC-004`.
- **Notes:** if no name is heard, close with that evidence.
- **Done:** 2026-11-06 (`EXP-0058`).
  - **Moments:** select pick (Jin, Arieta), VS screen, round start, win,
    Jin's story narration, a versus victory and Santana's ending, recorded
    with sound from saved states (the pick from one cold boot).
  - **Listening:** eight clips, one at a time. The user's answers,
    verbatim: "No speech" (VS), "No speech" (round start), "It says
    "TARGET DESTROYED" but no other speech is there" (win), "Japanese
    language is spoken, no idea what it's saying" (narration), "Yes, "jin"
    is said" (the narration line naming Jin), "I hear speech. MAYBE it says
    "Jin" at the very start of the phrase?" (versus victory; its text has
    no name), "Speech, no name" (Santana's ending), "No speech" (picks).
  - **Record:** `docs/names.md`, "Names in Voice": no announcer calls a
    name; names are spoken only inside Japanese lines, the same names.
  - **Cold boot:** asked whether to close with the pilot pick unchecked or
    run one more cold boot; the user's answer, verbatim: "Run one more
    cold boot".

### LOC-004 - The user's plan for each name surface

- **Status:** `DONE` (2026-11-06, `EXP-0059`)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** LOC-001, LOC-002, LOC-003.
- **Blockers:** None.
- **Objective:** The user decides, per surface, where the Latin art comes
  from.
- **Acceptance criteria:**
  - **Options and costs:** for every surface × name, the options are put to
    the user, with rendered samples beside the US arcade's:
    - point the game at Latin art already on the disc;
    - draw new art (modelled on the US arcade's, or set in a font already
      in the game), recorded as new work like a new translation;
    - keep the katakana and record an exception.
  - **Romanization:** a Latin spelling for every name with no arcade
    English (Tessan at least), as a recorded new translation.
  - **Gate:** the decisions, in the user's words, as a `GATE-TRANSLATION`
    extension here and in `docs/localization_policy.md` and
    `docs/names.md`.
  - **Build switch:** the build option for the Latin art is named (for
    example `dialogue.py --name-art latin`); Latin is the default, and the
    katakana stays available for `OPT-001`.
- **Done:** 2026-11-06 (`EXP-0059`).
  - **Options and costs:** pointing at existing Latin art is not possible
    (none exists, D-052). Put to the user, with samples drawn into the real
    select and VS screens beside the US arcade's: the arcade letters in the
    banners, new katakana-style lettering, or keeping the katakana.
  - **Romanization:** none needed for name art: every pilot and mech on
    these screens has an English spelling (US arcade art, the arcade
    English text, or the game's Latin list); Tessan has no name art and
    stays with `SPECIAL-001`.
  - **Gate:** below, and in `docs/localization_policy.md` and
    `docs/names.md`; spellings in `data/translations/name_art.json`.
  - **Build switch:** `tools.text.dialogue --name-art latin` (named by the
    agent); Latin is the default and the katakana stays available for
    `OPT-001` (which still needs storage for a second set, D-052).

### GATE-TRANSLATION extension for the name art

- **Status:** `DONE` (2026-11-06)
- **Scope:** the pilot names on the pilot select and the pilot and mech
  names on the VS screen (D-051, D-052).
- **Asked** (2026-11-06), after three sample sheets were sent (the VS
  screen: US arcade, Saturn now, Saturn with Latin names; the select
  banners in Latin; long mech names against the model code), and the
  user's answers, verbatim:
  - "No Latin version of the pilot or mech name art exists on the disc, so
    it has to be made (new art, recorded like a new translation). The
    samples I just sent set the names in the game's own arcade letters
    (the font the English story uses) inside the Saturn's red and blue
    name banners. Which lettering should the select and VS name art use?"
    → "Arcade letters in the banners (Recommended)"
  - "Which capitalization? The US arcade writes pilots in mixed case
    ("Jin", "Bao&Mao") but the boss "SHADE" and all mechs in capitals; the
    game's own Latin lists in the program are all capitals." → "As the US
    arcade (Recommended)"
  - "The Saturn shows a model code beside each mech name ("BX-02", already
    in Latin); the US arcade shows none. Longer names (R·LIGHTNING,
    F·KILLER BEE) run into the code where it sits now (third sheet). Keep
    the codes?" → "Keep, moved after the name (Recommended)"
  - "Spellings where the US arcade has no name art: Chiyomaru and
    Devilotte come from the arcade's English text, and the mech variants
    follow the Saturn's prefix letter plus the game's own Latin list
    (B·SWORDSMAN, B·RIOT, R·JACKAL, F·TALANTURA, F·KILLER BEE, G·VICE,
    G·CYCLONE), as the US arcade's R·LIGHTNING does. The Saturn's Devilotte
    art says "Princess Devilot". Which name for her?" → "Devilotte
    (Recommended)"

So `LOC-005` builds the 9 pilot names (select and VS) and 16 mech names
from `data/translations/name_art.json`. It is `READY`; the VS records'
room (D-052) is its first problem.

### LOC-005 - Build the Latin name art

- **Status:** `DONE` (2026-11-06, `EXP-0060`, D-053)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** LOC-004.
- **Blockers:** None.
- **Objective:** The current image with every name-art surface in Latin,
  as decided, built from the untouched source.
- **Acceptance criteria:**
  - **Generator:** a script makes each Latin asset (or pointer change) from
    the decided sources, with format checks against `LOC-002`. No game art
    is committed (rule 21); scripts, tests and any approved spellings are.
  - **Build:** the option is added to the current build (`dialogue.py`,
    with the M8 and boot-warning options). Two builds identical; every
    changed range listed with its original and new bytes (rule 12); every
    changed file fits its sectors; all sectors valid; the katakana art
    still on the disc where `LOC-002` says the switch needs it.
  - **Screens:** every surface of `LOC-001` shows its Latin name, from saved
    states (and a cold boot only where no state reaches it, asked first),
    checked by the agent against the generated art.
  - **No other change:** apart from the name art, the image equals the
    current reference (`data/regression/boot004_boot_warnings.json`).
- **Done:** 2026-11-06 (`EXP-0060`, D-053).
  - **Generator:** `tools/text/name_art.py` and `tools/text/pattern_t2.py`
    (the type-2 format read in full; both with tests), from
    `data/translations/name_art.json`.
  - **Build:** `--name-art` with the `boot004` options (Track 01
    `e1a88dc6…`); two builds identical; ranges with original and new hashes
    in `name_art_changes.json`; 18 sectors changed, all in `SELECT.VAD`,
    `STG0A.BIN` and `PL3F_0.BIN`; 0 invalid. The katakana is not kept in
    these files (D-052: no room); `OPT-001` must store it elsewhere.
  - **Screens:** all 34 names from saved states, every part equal to its
    built pattern, read by the agent. The select check wrote the built
    `STG0A.BIN` part table into RAM (it is resident in every state); the
    cold-boot read is `LOC-006`'s.
  - **No other change:** every `boot004` output equal.
  - **Provenance:** `data/regression/loc005_name_art.json`.

### LOC-006 - Verify and register

- **Status:** `DONE` (2026-11-06, `EXP-0061`, D-054)
- **Milestone:** Name art (`LOC-001`)
- **Dependencies:** LOC-005.
- **Blockers:** None.
- **Objective:** Play-check the Latin name art and lock the build.
- **Acceptance criteria:**
  - **Play check:** a cold boot with the user present (asked first) through
    the pilot select, `MACHINE SELECT` and one VS screen, for at least two
    pilots, run by the agent; the screens are the generated art.
  - **Regression:** a new reference in `data/regression/`; all earlier
    references still match.
  - **Coverage:** `docs/coverage_exceptions.md` lists any name left in
    katakana, and why.
  - **README:** "What's Changed", "Still Japanese" and the build command.
- **Done:** 2026-11-06 (`EXP-0061`, D-054).
  - **Play check:** two cold boots, asked first ("Yes, run both
    (Recommended)"): arcade mode (with a second player) and versus mode;
    pilot select, `MACHINE SELECT`, `SET UP` and VS screens; Jin, Mary,
    Santana, Gawaine, Arieta, Bao&Mao and four mechs (two variants) in
    Latin; every screen check found built name parts only, no katakana
    (`play.json`).
  - **Regression:** the image is `data/regression/loc005_name_art.json`'s
    (`LOC-005`), unchanged; all eight references rebuild and match
    (`regress.json`).
  - **Coverage:** `docs/coverage_exceptions.md`, "Name Art": no listed
    name stays katakana; six story-only banners (frames `0x74`-`0x79`) and
    one small one (`0x70`), never seen on a screen, are excluded.
  - **README:** "What's Changed", "Still Japanese", the build command.

## Phase P: Names Switch (`OPT-001`)

The user asked for these tasks (verbatim, 2026-11-06): "Let's begin
OPT-001". The user's decision behind them (2026-11-02, `DOC-002`,
verbatim): "I definitely want the toggle and I want it placed in the
options screen. We may need an expanded options screen like I'm currently
working on". The order is:

1. `OPT-001` (the Options screen: rows, drawing, settings and their save),
   `OPT-002` (where the katakana art can live and when to put it in place)
   and `OPT-003` (free RAM for code, proven by write logs), which are
   independent;
2. `OPT-004` (the user's choices: the row, its words, where it goes; a gate
   extension for the new menu words);
3. `OPT-005` (the switch build, Latin by default);
4. `OPT-006` (verify and register).

The siblings are a method only (rule 13): MSHvSF's EXTRA OPTIONS sub-menu
(`OPT-003`-`OPT-005`) and XvSF's names toggle (`LOC-009`, `LOC-010`, whose
first build put code in the interrupt-handler table, hung the title and
wrecked the test saves).

Known so far (facts and their confidence):
- **Options screen (`docs/text_surfaces.md`, seen, not traced):**
  `OPTION MODE` from the title menu, eight rows in English (`DIFFICULTY`,
  `TIME LIMIT`, `SHORT CUT`, `SOUND`, `SOUND TEST`, `DATA RESET`, `KEY
  CONFIG`, `3M RAM MODE`) above `PRESS START TO EXIT`, with little room
  below the last row (session screenshot `f00027081.png`; session states
  26998-27524 are near it). How it is drawn, where its settings live and
  whether they are saved: **UNKNOWN**.
- **Save (D-048, CONFIRMED):** the game's save is checked at boot
  (`0x06036C3E`), with a checksum; a damaged save shows `WARNING0`. Any
  change to what is saved must keep that check passing.
- **Name art (D-052, D-053, CONFIRMED):** the Latin build replaces the
  katakana in place: `SELECT.VAD` `0x17840`-`0x19B20` (8,928 bytes raw)
  with 36 changed bytes of `STG0A.BIN`'s part table, and `PL3F_0.BIN`'s
  name records (the katakana took 20,804 bytes compressed). Neither file
  has room for both sets (1,440 and 288 bytes of slack). The untouched
  files hold the katakana; `name_art_changes.json` records every range.
- **When the art is in RAM (D-052, CONFIRMED):** `SELECT.VAD` loads at the
  pilot select and is copied raw to VDP1 VRAM `0x20000`; `STG0A.BIN` is
  resident (`0x06060000`); `PL3F_0.BIN` loads to WRAM-L `0x00200000`
  before the VS screen. Where a switch could act (a load hook, the part
  table, the decoder) is **UNKNOWN**.
- **Free RAM: UNKNOWN.** Nothing is proven unused. XvSF's lesson 13 (zero
  bytes may be the interrupt-handler table) is a HYPOTHESIS for Cyberbots.
- **`3M RAM MODE`:** what it does is **UNKNOWN**; it may change what is
  loaded where, so free RAM must be checked in both settings.

### OPT-001 - The Options screen and its settings

- **Status:** `DONE` (2026-11-06, `EXP-0062`, D-055)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** LOC-006.
- **Blockers:** None.
- **Objective:** Know how the Options screen is built well enough to add a
  row or a sub-menu, and where a new setting can be kept and saved.
- **Acceptance criteria:**
  - **Rows:** the row text's location and format, the drawing routine,
    the cursor's row count and wrap, and each row's value handler, traced
    (addresses, CONFIRMED by a one-variable change seen on screen).
  - **Settings:** where each setting is held in RAM, found by comparing
    steady windows before and after one change (the MSHvSF method), and
    who reads `3M RAM MODE`'s value.
  - **Save:** whether and when the settings are written to backup memory,
    the save's layout around them, its checksum, and whether a spare byte
    exists that the boot check (D-048) tolerates; tested by a write and a
    cold boot of a fixture (asked first).
  - **Room:** the screen space below `3M RAM MODE` measured; whether a
    ninth row fits, or a sub-menu entry is needed; any hidden or unused
    row noted.
- **Notes:** From saved states first (no key); a cold boot only for the
  save test, asked first.
- **Done:** 2026-11-06 (`EXP-0062`, D-055).
  - **Rows:** `OPDEMO.BIN` at `0x06060000`; C strings printed by
    `0x0602A82A` (x 6, rows 8-20; `3M RAM MODE` row 22 only with a RAM
    cart, flag `0x0606BE90`; EXIT row 24); cursor `0x0606BE8C`, wrap at 7
    or 6; one handler per row in `0x06062704`; each value confirmed by a
    write seen on screen.
  - **Settings:** block `0x060D9290`-`9F`, +0-+4 used (difficulty, time
    limit, short cut, sound, sound test); `3M RAM MODE` is `0x06047ED4`
    (cart RAM as a load cache; set at start-up; not saved).
  - **Save:** leaving Options saves `CYBERBOTS01` (256 bytes; the block at
    +4-19; a 16-bit byte sum at +254). A byte in +5-15 is saved, summed and
    loaded at boot (states and a cold boot, asked first: "Yes, run it now
    (Recommended)"); a stale sum gives `WARNING0`; no save and `DATA
    RESET` give 0. Only start-up code and the save's copy touched +5-15 in
    the session.
  - **Room:** labels at y = 8r + 12; a ninth row fits at row 24 with EXIT
    at row 26 (y 220-226, inside the visible rows 8-231), or the rows move
    up a row; the menu font has `A`-`Z`, digits, `&`, `-` and lower case;
    `KEY CONFIG` is a sub-screen model. No hidden row besides `3M RAM
    MODE`.

### OPT-002 - Where the katakana art can live and when it goes in

- **Status:** `DONE` (2026-11-06, `EXP-0063`, D-056)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** LOC-006.
- **Blockers:** None.
- **Objective:** Find storage for the katakana name art beside the Latin,
  and the point where the game could put one set or the other in place.
- **Acceptance criteria:**
  - **Size:** the bytes the katakana set needs, measured (select block,
    part-table bytes, VS records; compressed with `pattern_t2` if smaller).
  - **Storage options,** each measured, not assumed: slack or unused data
    in files loaded at or before those screens (with what loads them); a
    file grown into its sector slack; a moved or new file (what the disc
    builder and the game's file table allow); RAM that already holds it.
  - **Switch point:** for each screen, the load or copy that puts the name
    art in place (`SELECT.VAD` to VDP1 VRAM, `PL3F_0.BIN` to WRAM-L, the
    `STG0A.BIN` part table), traced, with where a check of the setting
    could go; versus mode and `SET UP` included.
  - **Options** with costs, for `OPT-004`.
- **Notes:** `docs/known_unknowns.md` ("Where can both name-art sets
  live"). No key.
- **Done:** 2026-11-06 (`EXP-0063`, D-056).
  - **Size:** 30,838 bytes (the untouched bytes of the four Latin ranges);
    as loadable pieces 8,640 (select, 5 sectors), 38,700 (`PL3F_0.BIN`
    `0x90`-`0x97BC`, 19 sectors) and 124 (part table).
  - **Storage options:** Track 01's last 150 sectors are free (a copy of a
    file placed there loaded byte for byte through the game's loader);
    the directory's last sector has 1,532 bytes and the game's table 57
    entries spare; files are found by name, so a name sorting last
    changes nothing else. Slack in the files loaded at these screens:
    7,616 bytes (too little). Full alternate files do not fit the tail.
    No RAM already holds the katakana.
  - **Switch points:** pilot select, after `SELECT.VAD`'s load at
    `0x06038CD6` (`CYBER.BIN`; `STG0A.BIN` is already loaded); VS, after
    the `PL3F_0.BIN` wait loop at `0x060605C2` (`STG0AS.BIN`). Each name
    occurs once on the disc, so versus mode and `SET UP` share them
    (static). A load writes exactly the file's size.
  - **Options for `OPT-004`:** A, small files in the tail loaded per
    screen (recommended); B, one file loaded into about 31 KB of free RAM;
    C, a longer Track 01 with full alternate files (moves every audio
    track); D, slack (does not fit). Costs in `EXP-0063`.

### OPT-003 - Free RAM for the switch's code

- **Status:** `DONE` (2026-11-06, `EXP-0064`, D-057)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** LOC-006.
- **Blockers:** None.
- **Objective:** Prove a RAM range unused, for the switch's code and data,
  by logs, not by zeros.
- **Acceptance criteria:**
  - **Candidates:** ranges read as constant (zero or otherwise) across the
    session's states, WRAM-H and WRAM-L, `3M RAM MODE` on and off.
  - **Proof:** read and write watch logs over boot, title, attract, Options,
    pilot select, VS, a fight, a continue and an ending (states and one
    recorded cold boot, asked first): no access to the chosen range; what
    the zeros near it are (vectors, stacks, buffers) where traced.
  - **Result:** the range, its size, and its evidence, CONFIRMED, in
    `docs/discoveries.md`.
- **Notes:** XvSF lesson 13. A range used by the BIOS or by the CD block is
  excluded, not risked.
- **Done:** 2026-11-06 (`EXP-0064`, D-057).
  - **Candidates:** 28 constant WRAM-H runs over 174 states (none in
    WRAM-L); 19 watched, including six zero runs inside `CYBER.BIN`.
  - **Proof:** per-segment logs (addresses rebuilt from each instruction),
    `0xA5` canaries and a cold boot with no cart into a versus fight (asked
    first: "Yes, run it (Recommended)"), plus an independent static review
    (literals, loads, DMA, indexed tables). Unused once `CYBER.BIN` runs:
    `0x06055424`-`0x06055824` (1,024 bytes inside `CYBER.BIN`'s file, loaded
    with it) and `0x060DF8A8`-`0x060E0EA4` (5,628 bytes). Rejected: the
    VDP1 command list's open tail `0x060E32E4`-`0x060E8000` (the largest
    zero run), task and interrupt stacks, BSS, a boot load buffer.
  - **Result:** D-057, CONFIRMED. No 31 KB of free RAM, so `OPT-002`'s
    option B is out. The screenshot comparison was uninformative (two
    identical control runs differ).

### OPT-004 - The switch, decided with the user

- **Status:** `DONE` (2026-11-06)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** OPT-001, OPT-002, OPT-003.
- **Blockers:** None (the user's answers).
- **Objective:** Put the switch's design to the user with the facts.
- **Acceptance criteria:**
  - **Choices put to the user** (multiple choice, one recommended): where
    the switch goes (a ninth row, or an extra-options sub-menu); its words
    (for example `NAMES` with `LATIN`/`KATAKANA`) in the menu's own font;
    whether it is saved with the other settings; where the katakana art is
    kept (`OPT-002`'s options). Latin stays the default (`DOC-002`).
  - **Gate:** the new menu words recorded as a `GATE-TRANSLATION`
    extension in `docs/localization_policy.md`, answers verbatim with the
    date.
- **Notes:** No build before this gate.
- **Done:** 2026-11-06. The user's answers, verbatim, are in
  `docs/localization_policy.md` ("Names Switch, Decided"): a sub-menu
  ("Sub-menu"), reached from a 9th OPTION MODE row with every row moved up
  one line ("Rows up one line (Recommended)"), named `EXTRA OPTIONS`
  ("EXTRA OPTIONS (Recommended)"), holding `NAMES  ENGLISH / JAPANESE`
  ("NAMES  ENGLISH / JAPANESE (Recommended)"), saved in the settings block
  ("Save it (Recommended)"), with the katakana in new files in Track 01's
  tail and SSP checked in `REL-002` ("Tail files; check SSP later
  (Recommended)"). Recorded as a `GATE-TRANSLATION` extension for the new
  menu words.

### OPT-005 - Build the switch

- **Status:** `DONE` (2026-11-06, `EXP-0065`, D-058)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** OPT-004.
- **Blockers:** None.
- **Objective:** One image whose Options screen switches the name art,
  Latin by default.
- **Acceptance criteria:**
  - **Build:** a build option beside `--name-art`; code and data only in
    the proven ranges; every binary change recorded (original and new
    bytes, address, purpose); two identical builds; all sectors valid.
  - **Behaviour from saved states:** both settings show their own art on
    the pilot select, `SET UP` and VS screens (every part compared, as
    `EXP-0060`/`EXP-0061`); the row draws and changes; the setting is kept
    as decided; with the switch at Latin nothing else differs from the
    Latin build's behaviour.
  - **Save:** the boot check still passes with the new setting saved, and
    an old save (without it) still loads.
- **Design (from `OPT-004`):** OPTION MODE: every row and `PRESS START TO
  EXIT` one text row higher, a 9th row `EXTRA OPTIONS` that opens a
  sub-menu (as `KEY CONFIG` opens its screen); the sub-menu: title `EXTRA
  OPTIONS`, a row `NAMES  ENGLISH / JAPANESE`, a way back; the value in the
  settings block's spare byte `0x060D9295` (saved; 0 = English); the
  katakana pieces as new files in Track 01's tail (names sorting after
  `WARNING4.PIX`), loaded after `SELECT.VAD` (`0x06038CD6`) and after
  `PL3F_0.BIN` (`0x060605C2`) when the byte is set.
- **Notes:** Code only in `OPT-003`'s ranges: `0x06055424`-`0x06055824`
  (in `CYBER.BIN`'s file) and `0x060DF8A8`-`0x060E0EA4` (copied in at run
  time). The disc builder must write directory records and tail sectors
  (new tool work).
- **Layout (user, 2026-11-06):** "Title and rows up two lines
  (Recommended)" (the earlier "Rows up one line" freed only one line; see
  `docs/localization_policy.md`).
- **Done:** 2026-11-06 (`EXP-0065`, D-058).
  - **Build:** `--names-switch data/translations/names_switch.json`
    (`tools/text/names_switch.py`, `tools/disc/add_files.py`, both with
    tests); 740 bytes of code in D-057's range; 56 recorded changes in
    `CYBER.BIN`, `OPDEMO.BIN` and the built `STG0AS.BIN`; `ZNAMES1.BIN` and
    `ZNAMES2.BIN` in Track 01's tail; two builds identical (Track 01
    `357f5b65…`); 30 sectors changed against `loc005`, all expected; 0
    invalid.
  - **From saved states:** the boot loads the new entries (count 329, end
    flag moved) and code; OPTION MODE's layout and `EXTRA OPTIONS` row; the
    sub-menu and its value; back to OPTION MODE; byte 0: Latin, byte 1:
    katakana on the pilot select (1 / 2 parts) and VS (6 / 12 parts).
  - **Save:** a save with the byte and one without both pass the boot
    check.
  - **Not here:** pad presses in the menus, versus mode and `SET UP`, a
    cold boot (`OPT-006`).

### OPT-006 - Verify and register

- **Status:** `DONE` (2026-11-06, `EXP-0066`)
- **Milestone:** Names switch (`OPT-001`)
- **Dependencies:** OPT-005.
- **Blockers:** None.
- **Objective:** Play-check the switch and lock the build.
- **Acceptance criteria:**
  - **Play check:** a cold boot (asked first), driven by the agent: the
    switch changed in Options, then the pilot select and a VS screen in
    each setting; a second cold boot shows the saved setting kept, if it
    is saved.
  - **Regression:** a new reference in `data/regression/`; all earlier
    references still match.
  - **Coverage and README:** `docs/coverage_exceptions.md`, "What's
    Changed" and the build command.
- **Done:** 2026-11-06 (`EXP-0066`).
  - **Play check:** two cold boots, asked first ("Yes, run both
    (Recommended)"): boot 1 set `JAPANESE` with real presses (Up, A,
    Right, Start, Start) and showed katakana on the pilot select, `SET UP`
    and VS; boot 2, from boot 1's save, showed `JAPANESE` kept, set
    `ENGLISH` (Left) and showed Latin on the same screens. Both saves
    valid.
  - **Regression:** new reference `data/regression/opt006_names_switch.json`
    (rebuilds and matches); all eight earlier references match.
  - **Coverage and README:** `docs/coverage_exceptions.md` ("The Names
    Switch"), README "What's Changed" and the build command.

## Phase R: Release (`REL-001`)

The outline row (`REL-001`, "after M5"): "Copy XvSF `make_patch`/`make_ssp`
(with the RetroAchievements header guard) and parameterize the source folder,
manifest and author; xdelta and SSP; release zips via promoted
`make_zips`/`check_zips`. Patches are Release assets only, never committed."
The user's policy (`DOC-002`, 2026-11-02): release formats "xdelta + SSP
(Recommended)"; release timing "After open tasks (Recommended)": nothing is
published until every `IN_PROGRESS` and `BACKLOG` task is done or deferred by
the user by name; a real-Saturn check comes only near the end, before a
release (2026-11-02, after M2). The order is:

1. `REL-001` (the tool port), independent of the names switch;
2. `REL-002` (the release patches from the final image), after `OPT-006`
   and the release-timing rule;
3. `REL-003` (zips, release README and checks);
4. `REL-004` (publish), only on the user's explicit approval.

The siblings are a method only (rule 13): MSHvSF `REL-001`-`REL-004`
(`EXP-0084`, `EXP-0102`) and XvSF `REL-001`, `RA-001` (`EXP-0071`,
`EXP-0074`).

Known so far (facts and their confidence):
- **Source (ENV-006/007, CONFIRMED):** 62 tracks and the CUE equal Redump
  58190 "(2M)"; the "(1M)" edition (Redump 3669) has the same track 01.
- **Disc header:** track 01 sector 0 holds `SEGA SEGASATURN`, `T-1217G`,
  `V1.002` (`references/saturn_jp/README.md`). That rcheevos hashes its first
  512 user-data bytes is XvSF's reading of rcheevos; for Cyberbots a
  HYPOTHESIS, and no RetroAchievements entry has been checked.
- **Directory:** 325 root files, no subdirectories; 61 entries point at
  audio tracks (D-002); all 327 root records carry no system-use (XA)
  bytes (read for `REL-001`, logged 2026-11-06).
- **SSP limits:** `make_ssp` (as ported) builds a patch only when track 01's
  directory is unchanged and every changed sector lies in a source file;
  `OPT-004` option A (new files in track 01's tail) would be refused.
  Whether any SSP patcher can add files is UNKNOWN; xdelta handles it.

### REL-001 - Port the release tools

- **Status:** `DONE` (2026-11-06; tool port only)
- **Milestone:** Release (`REL-001`)
- **Dependencies:** None (the outline's "after M5" is met).
- **Blockers:** None.
- **Objective:** Release tools for xdelta and SSP patches and their zips,
  parameterized for Cyberbots, with the RetroAchievements header guard.
- **Acceptance criteria:**
  - **Copied with provenance:** `tools/disc/make_patch.py`,
    `tools/disc/make_ssp.py` (XvSF `e19a152`), `tools/release/make_zips.py`,
    `tools/release/check_zips.py` (XvSF `EXP-0071`, `9cb01ad`, promoted;
    `check_zips` rewritten in Python), each with source, path and commit.
  - **Parameterized:** source folder, track 01, manifest, regression
    reference (`data/regression/*.json` `output_sha256`), title, author,
    URL, image name, zip prefix and date; no XvSF name left.
  - **Guard:** both patch tools refuse a built track 01 whose sector 0
    first 512 user-data bytes differ from the source's; the records carry
    the computed `ra_md5`.
  - **Tests:** synthetic fixtures only; ruff, format, mypy and pytest clean.
- **Notes:** Done 2026-11-06 in parallel with `OPT-003`, at the user's
  request (verbatim): "Begin OPT-003 and any other tasks you can do in
  parallel." Nothing was built from the game image; 30 new tests (234 in
  all). An independent review found no blocker; its nits: the two
  header-refusal tests could write into the real `build/` (fixed: they use
  a temporary `build/`), `check_zips --expect` takes one hash for all
  variants, and `make_ssp` writes the `.ssp` before its round-trip check
  (inherited from XvSF). Every behaviour is a HYPOTHESIS for Cyberbots
  until `REL-002` applies the patches.

### REL-002 - Build and verify the release patches

- **Status:** `BLOCKED`
- **Milestone:** Release (`REL-001`)
- **Dependencies:** REL-001, OPT-006; the release-timing rule.
- **Blockers:** every open task done or deferred by the user by name
  (the release-timing rule); `OPT-006` is done (2026-11-06).
- **Objective:** xdelta and SSP patches that turn the untouched source into
  the final registered image, proven by applying them.
- **Acceptance criteria:**
  - **Build:** `make_patch` and `make_ssp` from the final regression
    reference (`--reference data/regression/<final>.json`), each built
    twice byte-identical, records in `release/`.
  - **Apply:** each patch applied to an untouched copy of the source,
    outside the repo's tools (`xdelta3 -d`; an SSP patcher, installed only
    with the user's approval), gives the reference's track 01 SHA-256; the
    patched image cold-boots in Mednafen to the title.
  - **Header:** the patched track 01's `ra_md5` equals the source's;
    whether RetroAchievements lists that hash is checked (a web fetch,
    asked first) or recorded as UNKNOWN.
  - **Route:** if the switch adds files to track 01 (`OPT-004` option A),
    the SSP route is decided with the user (no SSP, or a patcher that
    adds files, proven), before building it.
  - **Real hardware:** a burned disc tried by the user on a Saturn (the
    user's 2026-11-02 rule), or deferred by the user by name.
- **Notes:** Patches stay under `build/`; only the JSON records are
  committed.

### REL-003 - Release zips, README and checks

- **Status:** `BLOCKED`
- **Milestone:** Release (`REL-001`)
- **Dependencies:** REL-002.
- **Blockers:** `REL-002`.
- **Objective:** Reproducible zips with instructions a player can follow.
- **Acceptance criteria:**
  - **Zips:** `tools.release.make_zips` run twice, byte-identical; one
    zip per format, each with a readme naming the source image, its track
    01 hash, each patch's hash and the patched track 01 hash.
  - **Check:** `tools.release.check_zips --expect <track 01>` on the
    unpacked zips passes for every patch.
  - **Docs:** `release/README.md` (apply steps for both formats, the "(1M)"
    edition's shared track 01, known limits), `release/RELEASING.md`
    (exact commands) and release notes; the README's "What's Changed".
- **Notes:** The zips hold game-derived patches: under `build/` only.

### REL-004 - Publish

- **Status:** `BLOCKED`
- **Milestone:** Release (`REL-001`)
- **Dependencies:** REL-003.
- **Blockers:** `REL-003`; the user's explicit approval (asked, answer
  recorded verbatim with the date).
- **Objective:** A GitHub Release with the zips as assets.
- **Acceptance criteria:**
  - **Approval:** the user approves the version, the notes and the asset
    list, verbatim, in `docs/localization_policy.md`.
  - **Release:** a tag and a GitHub Release whose assets are the two zips
    (and, if approved, the bare patches); their SHA-256 equal `REL-003`'s.
  - **History:** no patch, zip, image or game data in git history
    (rule 21 exception: Release assets only).
- **Notes:** Nothing is published without the user's go-ahead.

## Later Milestones (outline only)

Placeholders so the order is visible. Each becomes a full task, with its own
acceptance criteria, only when its prerequisites are done ("Write up the Mx
tasks" just in time). The method for each is in `docs/playbook_from_mshvsf.md`
and `docs/lessons_from_xvsf.md`.

| ID | Milestone | Outline |
| --- | --- | --- |
| END-010 | M7 | `DONE` (2026-11-05, Phase L); follow-up `END-011` (`BACKLOG`). |
| END-020 | M8 | `DONE` (2026-11-05, Phase M: `END-020`-`END-023`, with `END-011`); M8 confirmed. |
| UI-004 | after M5, early | `DONE` (2026-11-06, Phase N: `BOOT-001`-`BOOT-005` and the gate extension). |
| UI-001 | after M8, user request | UI art: inventory English art already in every font before drawing anything. |
| UI-002 | after M8, user request | Attract and opening text (`OPDEMO*`, `STDEM*.PIR`, `VADEM*.MAC`, `STDEMO.*` are candidates): layer, container, codecs, oracles. |
| UI-003 | after M8, user request | Other UI text (select, continue, ranking, options): find the arcade English by tracing the arcade code. |
| TXT-002 | after M8, user request | Rare, random, or region-gated text: trace every reader of every text table. |
| LOC-001 | after REF-007 | `DONE` (2026-11-06, Phase O: `LOC-001`-`LOC-006` and the gate extension). |
| OPT-001 | after LOC-001, user decision 2026-11-02 | `DONE` (2026-11-06, Phase P: `OPT-001`-`OPT-006`). |
| SPECIAL-001 | M9, user approval | Boss and hidden pilots, alternate routes, unlocks. Secondary sources (`docs/references.md`) say the console ports add four pilots (Chiyomaru Kagura, Tessan Hagure, Princess Devilotte, SHADE) with no arcade English, and an Akuma-mech code; their lines need recorded new translations under the user's policy. Size: Saturn lines 899-1850 (952 lines, about half the script) have no arcade counterpart (D-011). Among the arcade pilots' stories only line 258 is Saturn-only (line 34 is dead data); the earlier count of 74 came from REF-006's reader bug (`EXP-0023`). |
| REL-001 | after M5 | Phase R (`REL-001`-`REL-004`): `REL-001` (tool port) `DONE` (2026-11-06); `REL-002`-`REL-004` `BLOCKED` on the release-timing rule and the user (`OPT-006` done 2026-11-06). |
