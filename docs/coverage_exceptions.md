# Coverage and Exceptions

The register of what is in English and what is left out, with evidence:
the M5 roster (`RE-005`), the M8 endings and the boot warnings (`UI-004`).

## M5 Roster

Decided by the user on 2026-11-04 (`RE-005`). Question: "Which pilots make
up the M5 roster? The six arcade pilots (Jin, Santana, Mary, Arieta,
Gawaine, Bao and Mao) have 404 story boxes plus 46 win-quote boxes, all with
official arcade English except Mary's line 258. The three Saturn-only
pilots (lists 6-8, e.g. Devilot and Shade) add 339 story boxes with no
official English and are special cases under rule 24." Answer, verbatim:
"Six arcade pilots (Recommended)".

### In Scope

`data/text/m5_roster.json`: pilot lists 0-5, each list's story scenes (its
block of `STG0AS.BIN`'s scene posts) and the pilot's versus win quotes.

| List | Pilot | Story scenes | Boxes | Lines | Box file |
| --- | --- | --- | --- | --- | --- |
| 0 | Jin | 17 | 63 | 120 | `jin_boxes.json` (story scenes from D-021) |
| 1 | Santana | 20 | 64 | 117 | `santana_boxes.json` |
| 2 | Mary | 18 | 69 | 119 | `mary_boxes.json` |
| 3 | Arieta | 21 | 66 | 127 | `arieta_boxes.json` |
| 4 | Gawaine | 17 | 70 | 137 | `gawaine_boxes.json` |
| 5 | Bao and Mao | 21 | 72 | 136 | `baomao_boxes.json` |

Win quotes: the 46 boxes that the quote table's rows 0-5 reach
(`data/translations/win_quotes_pairing.json`, `roster_quote_boxes`; D-030).

### Excluded, With Evidence

| What | Boxes / lines | Evidence | Why |
| --- | --- | --- | --- |
| Pilot lists 6-8 (Saturn-only pilots: list 6 is one move left of Jin, Devilot by the name art; list 8 two moves left, Shade by the name art; list 7 not played) | 339 story boxes; lines 1020-1215, 1249-1445, 1510-1751 and others | `data/text/pilot_census.json` (no line paired with an arcade slot); cold boots `left1`, `left2` (`EXP-0033`) | No official English; special cases (rule 24, `SPECIAL-001`) |
| Their win quotes (quote-table rows 6-8) | boxes 1023-1044, lines 1790-1821 | D-030 | Same |
| Ending scenes of every list | each list's posts in `data/text/ending_posts.json` (replaces `ending_scenes_by_number`, which listed unposted scenes) | `END.BIN`'s routine for the winner's pilot posts them (`EXP-0039`, D-036) | M6-M8 (rule 23) |
| List 10 | 7 scenes of speaker-name boxes 602-605 and 609 (lines 1007-1010, 1014) | No Saturn file holds a list-10 post; the arcade's list 7 is the same and is posted at `0x6319C` (`EXP-0033`) | Never shown by the Saturn as far as the code shows |
| Mary's and Gawaine's scene 15 | none of their own: the same boxes as scene 14 | Scene 15 is not in either pilot's block; Mary's scene 15 is scene 14's script, Gawaine's a copy of it | Nothing to translate beyond scene 14 |
| Win-quote box 555 (line 956) | 1 box | No quote-table entry names scene 1 (D-030) | Never shown |
| VS-screen chapter captions | boxes 494-549 (lines 899-952) | `STG0AS.BIN` `0x0606CAE8` (`EXP-0032`) | A separate surface, outside M5; translated in `UI-006` (see "UI Text and Art") |

### For the Gate

- ~~Mary's line 258 (box 140) has no arcade counterpart (D-011): a new
  translation.~~ Corrected 2026-11-04 (`PAIR-003`, D-032): line 258 is slot
  140's second line, edited; slot 140's English covers it. No roster line
  needs a new translation.
- Win quotes: the two Japanese quotes of a level share one US line (22 pairs
  of boxes, D-030).
- Lines a roster box shares with another list's box (the census's
  `lines_shared_with_other_lists`: Jin 57, 75; Santana 144; Arieta 386;
  Gawaine 57, 144, 538, 562, 584; Bao and Mao 75, 386, 538, 661). A shared
  line changed for one pilot changes for the other; line 661 is also in
  list 6's box 974.

## M8 Endings

The roster's endings (`END-023`), decided at the gate on 2026-11-05: the
official US arcade English of lists 0-5 as paired (D-038, D-044), built
from `data/text/m8_endings.json`.

### In Scope

Every box each roster ending is seen to open, forced from the END-001
checkpoint (`data/text/ending_surfaces.json`, D-043). That includes the
scenes the arcade posts and the Saturn reaches only through run-on scripts
(Mary's 17-18, Bao and Mao's 20).

| List | Pilot | Distinct boxes shown | English boxes | Blank (1072) |
| --- | --- | --- | --- | --- |
| 0 | Jin | 19 | 18 | yes |
| 1 | Santana | 18 | 17 | yes |
| 2 | Mary | 15 | 14 | yes |
| 3 | Arieta | 23 | 22 | yes |
| 4 | Gawaine | 16 | 16 | no |
| 5 | Bao and Mao | 22 | 21 | yes |

That is 100 English boxes, with boxes 601, 604, 605, 606, 607 and 610 shared
between roster endings. Every ending also shows the cast roll (its Japanese
name images hidden, D-040) and, where the run reaches it, the QSound
notice (its Japanese line erased, D-041). The staff credits and thank-you
screen are already English.

### Excluded, With Evidence

| What | Boxes | Evidence | Why |
| --- | --- | --- | --- |
| The Saturn-only pilots' endings (lists 6-8) | their boxes in `data/text/ending_surfaces_others.json` (114 lines), less 601 and 605 | Forced runs (`EXP-0049`): they open only their posted boxes | No official English; special cases (rule 24, `SPECIAL-001`) |
| Boxes 601 and 605 in list 8's ending | 2 speaker names | Shared with lists 0, 3 and 4 (D-036) | English since M7: the gate's "Share, English everywhere (Recommended)" |
| Box 1072 | 1 (lists 0-3, 5 and 7) | A full-width space (D-038) | Nothing to show |
| Jin's scene 20 (box 550) | 1 | Never posted, and no script runs into it (D-036, D-043) | Never shown |

## Boot Warnings

The five boot-time warnings (`UI-004`, `BOOT-001`-`BOOT-005`), decided at
the gate on 2026-11-06: a new translation by the agent, approved by the
user, in `data/translations/boot_warnings.json`.

### In Scope

| Picture | Shown when (D-048) | English | Seen in English |
| --- | --- | --- | --- |
| `WARNING0.PIX` | The game's save fails its checksum | yes | cold boot, damaged save (`EXP-0054`, `EXP-0055`) |
| `WARNING1.PIX` | System Memory unformatted | yes | cold boot, zeroed memory |
| `WARNING2.PIX` | A save cartridge, unformatted | yes | cold boot, zeroed save cart |
| `WARNING3.PIX` | Both unformatted | yes | cold boot, both zeroed |
| `WARNING4.PIX` | No save and fewer than 6 free blocks | yes | cold boot, 4 blocks free |

No boot-time message stays Japanese: the save check's picture routine has
no other caller (D-048).

### Excluded, With Evidence

| What | Evidence | Why |
| --- | --- | --- |
| A read failure of an intact save; internal memory "not connected" | The code sends both to pictures above (`WARNING0`; `WARNING1`/`3`), D-048 | Not producible in Mednafen; their pictures are already English |
| The Saturn BIOS's own screens (memory manager, control panel) | The `WARNING1`-`3` button leads into the BIOS (`EXP-0055`) | Not the game's text |
| The number on `WARNING4` | The Japanese says 05; the game needs 6 (`EXP-0051`) | The user's opt-in fix: "6, what the game checks" |

## Name Art

The pilot and mech names drawn as art (`LOC-001`-`LOC-006`), decided at
the gate on 2026-11-06 (`LOC-004`): the arcade's letters, the US arcade's
spellings, model codes after the mech names, "Devilotte".
`data/translations/name_art.json`; built by `--name-art` (D-053).

### In Scope

| Surface | Names | Latin | Seen in Latin |
| --- | --- | --- | --- |
| Pilot select (bank 56, frames `0x14`-`0x1C`) | 9 pilots | yes | all 9 from saved states (`EXP-0060`); Jin, Mary, Santana, Gawaine, Arieta, Bao&Mao on cold boots (`EXP-0061`) |
| `SET UP` (same art as the select) | the two chosen pilots | yes | cold boots: Santana, Arieta, Gawaine, Bao&Mao |
| VS screen, pilots (bank 63, `0x02`-`0x0A`) | 9 pilots | yes | all 9 from saved states; Santana, Arieta, Gawaine, Bao&Mao on cold boots |
| VS screen, mechs (bank 63, `0x0C`-`0x1B`) | 16 mechs | yes | all 16 from saved states; REPTOS, BLODIA, F·KILLER BEE, G·CYCLONE on cold boots |

On the cold boots no katakana name part was on any screen checked
(`EXP-0061/play.json`).

### The Names Switch (`OPT-001`-`OPT-006`)

`EXTRA OPTIONS` (a new OPTION MODE row) holds `NAMES  ENGLISH / JAPANESE`
(D-058). With `JAPANESE`, the original katakana art is back on the pilot
select, `SET UP` and VS screens (all the names above); with `ENGLISH` (the
default, and after `DATA RESET`) the Latin art. Seen on two cold boots
(`EXP-0066`): katakana on all three screens after choosing `JAPANESE`, the
choice kept after a power cycle, Latin again after choosing `ENGLISH`.
The menu's new words (`EXTRA OPTIONS`, `NAMES`, `ENGLISH`, `JAPANESE`) are
a new translation approved at the gate (`OPT-004`).

### Excluded, With Evidence

| What | Evidence | Why |
| --- | --- | --- |
| Bank-63 frames `0x74`-`0x79`: story-only characters' names (one appears to read 鉄山, Tessan), katakana or kanji, a third banner style | `EXP-0057` (every bank-63 frame drawn) | Not seen on any screen yet; where they are shown is unknown (`TXT-002`, `SPECIAL-001`) |
| Bank-63 frame `0x70`, an unreadable small banner | `EXP-0057` | As above |
| Bank-63 frame `0x0B`, "G.O.D." | Already Latin (`EXP-0057`) | Kept; its records were moved by the repack, not redrawn (D-053) |
| The VS mech table's 17th entry (frame `0x1C`) | Draws a portrait, not a name (`EXP-0056`) | No name art |
| `MACHINE SELECT`, `BODY TYPE`, the fight HUD, the versus `RESULT` tally, the cast roll | Latin already (`EXP-0056`, D-040) | Nothing to change |
| The second row of the select grid (Devilotte, Chiyomaru, Shade) on a cold boot | A down press did not move either cursor there (`EXP-0061`) | Their names were seen from saved states only (`EXP-0060`); how the row is reached is not known (`SPECIAL-001`) |

## UI Text and Art

Decided at the `UI-005` gate (2026-11-06, `docs/localization_policy.md`,
"UI Text and Art, Decided"); built in `UI-006` (`EXP-0072`, D-062).

### In Scope

| Surface | Now | Seen |
| --- | --- | --- |
| VS captions, pilots 0-5 (boxes 496-549) | English, centred (`data/translations/vs_captions.json`) | all 54 from a saved state (`EXP-0072`); Jin's first on a cold boot (`EXP-0073`) |
| Ruined-city signs (`ST00_FNT.BIN`) | `SIGNS` setting: `BLANK` default, `ENGLISH`, `JAPANESE` (`data/translations/signs_switch.json`) | VRAM equal to each version from the attract state (`EXP-0072`); on cold boots `BLANK` and, after a power cycle with the saved setting, `ENGLISH`; the setting changed with real presses (`EXP-0073`) |

### Excluded, With Evidence

| What | Evidence | Why |
| --- | --- | --- |
| VS captions of pilots 6-8 (boxes 1045-1071) | No arcade slot (D-060) | The user: "With SPECIAL-001 (Recommended)" |
| One wrong English pair glyph in each of 12 lines of pilots 6-8 (lines 1054, 1117, 1187, 1217, 1247, 1335, 1352, 1433, 1590, 1693, 1762, 1837) | `EXP-0072` `caption_changes.json` | The captions' codes; the user: "Take the 13 codes (Recommended)"; until `SPECIAL-001` |
| Skyline boards on the city stage's NBG3 | About 5 pixels high, not readable (`EXP-0070`) | Not text that can be read |
