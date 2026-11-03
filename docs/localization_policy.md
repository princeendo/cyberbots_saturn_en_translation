# Localization Policy

The user's policy decisions for Cyberbots. Each was put to the user as a
carried-over sibling decision under `DOC-002` and answered on 2026-11-02; the
"Answer" column is the option the user chose, quoted. These are policy, not
facts: whether each one is achievable on Cyberbots is found by experiment.

## Decisions (2026-11-02)

| Topic | Answer | Meaning for Cyberbots | Sibling precedent |
| --- | --- | --- | --- |
| English source | "Official; fixes opt-in (Recommended)" | The release uses Capcom's official arcade English, paired to each Saturn line by the game's own logic, with no rewording. Grammar fixes may exist only behind an opt-in build flag. | MSHvSF `TR-001`, `TXT-004`; XvSF `DOC-002` (same answer) |
| Text with no official English | "Recorded new translation (Recommended)" | A new translation, with the translator named and source hashes kept, approved by the user surface by surface. Absence of official English must first be shown by tracing the arcade code, not only by a data search. | MSHvSF `EXP-0078`, `EXP-0087`; XvSF boot warnings and boss boxes |
| Pilot and VA mech names | "Both variants, US default" | Two English variants: US arcade names (text, art and voice, consistent) by default, Saturn names as the alternative. Which names differ, what each convention costs on this disc, and whether the variants ship as two images or an in-game toggle are found by `REF-007` and decided in `LOC-001`. | MSHvSF `LOC-001`-`LOC-005` (two images); XvSF `LOC-008`-`LOC-010` (toggle only shipped) |
| Eventual scope beyond ordinary story dialogue and endings | "Boss & hidden pilots", "Menus, UI art & warnings", "Attract & opening demos", "Rare & region-gated text" | All four are in eventual scope. Each stays gated behind the ordinary-pilot pipeline (`AGENTS.md` rule 24, M9) and gets its own task when its turn comes. Boot, cart and save warnings (`UI-004`) are scheduled early after M5. | MSHvSF `SPECIAL-*`, `UI-*`, `TXT-*`; XvSF `UI-004`, `SPEC-*`, `CAP-*` |
| Release formats | "xdelta + SSP (Recommended)" | An xdelta3 patch and a Sega Saturn Patcher `.ssp` patch for track 01, published as GitHub Release assets, never committed. The system area stays unchanged (RetroAchievements hash). | MSHvSF `REL-001`-`REL-003`; XvSF `REL-001`, `RA-001` |
| Release timing | "After open tasks (Recommended)" | Nothing is published until every `IN_PROGRESS` and `BACKLOG` task is done, or deferred by the user by name. | Both siblings |
| Patched Mednafen | "Yes, reuse it (Recommended)" | After a stock boot, a short `EMU-020` record citing the sibling evidence suffices; validations V1-V4 are re-run on Cyberbots states (`EMU-021`). | MSHvSF `EMU-012`/`020`/`021`; XvSF `EMU-020`/`021` |
| Workflow | "Play check closes tasks", "Silent unattended runs", "Ask before downloads/installs", "Hardware check before push" | A task that changes the image is `DONE` only after the user's cold-boot play check, after the agent's forced trials. Scripted Mednafen runs use a separate silent home. Every download, install, gate change or scope change waits for approval. Image-changing commits stay local, with a burnable copy under `build/disc/`, until the user has tried it; doc-only commits push as usual. | Both siblings; MSHvSF hardware rule 2026-10-29 |
| PlayStation reference | "No, arcade only (Recommended)" | The arcade sets are the only oracle; `REF-002` is `REJECTED`. | XvSF `REF-006` (PS1 equal to the arcade) |
| Workflow, refined (2026-11-02, `DISC-002`) | The user's words: "Yeah, I don't want to do that at all. Why can't you just boot the machine and take regular screenshots like I did with the XvSF and MSHvSF translations?" | The cold-boot play check is the agent's own: a cold boot of the built image, driven to the changed text by pad keys sent through System Events (a scratch home with keyboard bindings), and closed on agent-reviewed screenshots. The user is asked only for gameplay the agent cannot reach. "No cold boots without me" is unchanged. | XvSF `tools/mednafen/route.py` |
| Workflow, refined (2026-11-02, after M2) | The user's words: "Let's push now. In general, I'm not going to want to burn a disc until we're much, much closer to finished. Mednafen does a fantastic job of replicating real hardware so I don't feel the need to constantly check." | "Hardware check before push" is retired for routine work: image-changing commits push after the agent's cold-boot play check in Mednafen passes. A real-Saturn check comes only near the end, before a release. |  |
| Capacity route (2026-11-02, `LAYOUT-001`, `EXP-0024`) | "Pair glyphs (Recommended)" | English is drawn two characters per 16×16 glyph, mixed case, re-wrapped to rows of up to 32 characters, 4 rows and 60 glyph cells per box. New glyphs take table codes no Japanese line uses first (336 available); until every pilot is English, any further glyphs are a recorded trade-off. No renderer code change. | MSHvSF `LAYOUT-001`/`FONT-003` (pair glyphs) |
| Gate for Jin's story (2026-11-02, `GATE-TRANSLATION`) | "GATE-TRANSLATION: may Jin's official arcade English go on the disc, as paired, with pair glyphs?" → "GO (Recommended)" | The official US arcade English goes on disc for Jin's 63 story boxes, as paired (D-022), unchanged; fixes stay opt-in. |  |
| Glyph gap (2026-11-02, `GATE-TRANSLATION`) | "If Jin's English still needs more glyphs than the 336 unused slots after optimising pair splits, what should give?" → "Rarest Japanese glyphs (Recommended)" | After pair splits are optimised, any pairs beyond the codes no Japanese uses take the glyph slots of the least-used Japanese characters (by line count). Each sacrificed glyph is recorded in the build's record, and those characters break in other pilots' Japanese until they are English (by M5). |  |
| XvSF standing rules | "No cold boots without me", "Time estimates on jobs", "Rebuild only new references", "Delete finished build images" | All four stay in force, as written in `local_agent_guidance.md`. | XvSF agent memory, 2026-10-31 and 2026-11-01 |

## Names, Refined (2026-11-02, `REF-007`)

`EXP-0012` found that Cyberbots has one set of names: the Japanese and US
releases differ only in the name art on the pilot select and VS screens
(katakana or Latin). Asked how the English build should handle names (options:
Latin art in one build; keep katakana art; both with a toggle), the user
answered, verbatim: "I definitely want the toggle and I want it placed in the
options screen. We may need an expanded options screen like I'm currently
working on in the MSHvSF repo."

| Topic | Decision | Evidence |
| --- | --- | --- |
| Names in text | The arcade English names (one set) | `docs/names.md` |
| Name art | Both conventions, chosen by an in-game switch on the Options screen; US (Latin) by default, as in the `DOC-002` answer | `docs/names.md`, `LOC-001` |
| Where the switch lives | The Options screen, expanded if needed, modelled on MSHvSF's EXTRA OPTIONS sub-menu (MSHvSF `OPT-003`-`OPT-005`, commits `08fe732`-`c6c9ae8`) and XvSF's names toggle (XvSF `LOC-009`/`LOC-010`) | `OPT-001` |

## Deferred To Evidence

Not asked under `DOC-002`, because each depends on what an experiment finds.
Each is put to the user when its task has the evidence.

| Decision | Deciding task |
| --- | --- |
| Pairing rule from Saturn lines to arcade English lines (the milestone unit: line, box or exchange) | `REF-006`, `REF-008`, then `GATE-TRANSLATION` |
| Capacity route (native English path, narrower glyphs, pair glyphs, relocated longer strings) | `FONT-002`, `LAYOUT-001` |
| Dialogue box layout for English lines | `LAYOUT-001` |
| Roster and exceptions for M5 | `RE-005` |
| Ending layout and labels | `END-001`, `END-002` |
| ~~Name-variant delivery~~ Decided 2026-11-02: an Options-screen toggle (above) | — |
| Caption, UI-art and attract style | `UI-001`, `UI-002` |

## Translation Gates

None yet. Each `GATE-TRANSLATION` GO and each later scope extension is
recorded here, verbatim and dated, with a scope / pairing / wording / names
table.
