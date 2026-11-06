# Pilot and Mech Names

Names across the releases (`REF-007`, `EXP-0012`). The user's policy is "Both
variants, US default" (`docs/localization_policy.md`); this file is the
evidence for how that applies to Cyberbots.

## Finding: One Set of Names, Two Scripts

Unlike MSHvSF and XvSF (Vega/Bison, Gouki/Akuma), Cyberbots uses the **same
names in Japan and in the US**; only the writing differs (katakana or Latin
letters). In the arcade English (D-009) and the Saturn script (D-008):

| Pilot | Arcade English (speaker label / text) | Saturn script (katakana or kanji) | Lines in Saturn 0-898 / 899-1850 |
| --- | --- | --- | --- |
| Jin Saotome | `Jin:`, "Jin Saotome" | ジン, サオトメ | 5 / 6, 8 / 13 |
| Gawaine (Murdock) | `Gawaine:`, "Captain Gawaine" | ガウェイン | 15 / 16 |
| Mary (Miyabi) | `Mary:` | マリー | 4 / 3 |
| Santana | `Santana:` | サンタナ | 3 / 2 |
| Arieta | `Arieta:` | アリエータ | 3 / 7 |
| Bao and Mao | `Bao Mao:`, `Bao:`, `Mao:` | バオ, マオ | 1 / 2, 1 / 6 |
| SHADE | `SHADE:` | シェイド | 9 / 20 |
| Devilotte | `Devilotte:` | デビロット | 7 / 10 |
| Chiyomaru | `Chiyomaru:` | 千代丸 | 0 / 16 |
| Tessan | **none** in the arcade English | 鉄山 | 0 / 8 |
| others | `Gary:`, `Xavier:`, `Customer:`, "Ken" | ケン 4 / 2; Gary and Xavier not found under the spellings tried | — |

Mechs: the Saturn HUD and `MACHINE SELECT` already show Latin names
(`BLODIA`, `REPTOS`, `FORDY`, `GULDIN`, `LIGHTNING`); the VS screen shows them
in katakana (Saturn and arcade Japan) or Latin (arcade US: `BLODIA`,
`R-LIGHTNING`).

Other recurring terms: "Earth Corps" (arcade English, 41 times) stands for
連合軍 (literally "the Allied Forces", 44 + 8 Saturn lines); "Variant Armor"
for ＶＡ.

## Where Names Appear as Art

| Screen | Saturn | Arcade Japan (`cybotsj`) | Arcade US (`cybotsu`) |
| --- | --- | --- | --- |
| Pilot select, under the portrait | katakana (`ジン`) | katakana | Latin (`Jin`) |
| VS screen, pilot names | katakana (`ジン`, `シェイド`) | katakana | Latin (`Jin`, `SHADE`) |
| VS screen, mech names | katakana | katakana | Latin (`BLODIA`, `R-LIGHTNING`) |
| VS screen, chapter caption | Japanese caption | Japanese caption (the same one) | **none** |
| Fight HUD | Latin | Latin | Latin |

On the Saturn the VS-screen name art is VDP1 sprites stored uncompressed in
`SELECT.VAD` (`EXP-0012`). Whether that file or another holds Latin name art
(as both siblings' discs held the other convention) is **UNKNOWN**: the
neighbouring data does not read as a list of names in 64×15 blocks, and
finding the sprite table needs the code that draws the VS screen (`LOC-001`).

Voices: whether any name is spoken was not checked (`LOC-003`).

## What "Two Variants" Can Mean Here

Because the names are the same, a "Saturn names" variant and a "US names"
variant would differ only in the name **art** (katakana or Latin), not in any
name. Options for the user, with their costs:

| Option | What changes | Cost |
| --- | --- | --- |
| Latin name art, one build | Text uses the arcade English names; the pilot select and VS screen show Latin names as the US arcade does | Find or draw Latin name art for 10 pilots and the mechs; one image |
| Keep katakana art, one build | Text in English; name art stays katakana | None for names; mixed scripts on two screens |
| Two builds or an Options toggle (Latin art / katakana art) | As above, selectable | Both art sets, plus a toggle patch (XvSF built one) |

**User decision (2026-11-02):** "I definitely want the toggle and I want it
placed in the options screen. We may need an expanded options screen like I'm
currently working on in the MSHvSF repo." Latin art is the default
(`docs/localization_policy.md`).

A romanization is needed only where the arcade has none: Tessan (and the
console-only story's other names), under the "Recorded new translation"
policy.

## Name-Art Census (`LOC-001`, `EXP-0056`)

Every surface seen, with what the Saturn, the US arcade (`cybotsu`) and the
Japanese arcade (`cybotsj`) show. Saturn evidence: session states 3070
(pilot select) and 6805 (VS screen), each name shown on the real screen by
writing its frame number into the drawn record (no key). Arcade evidence:
MAME 0.289 headless runs. Screenshot hashes: `EXP-0056/census.json`.

### Surfaces

| Surface | Saturn | US arcade | Japanese arcade |
| --- | --- | --- | --- |
| Pilot select, name under the big portrait (cursor's pilot) | katakana art (frames `0x14`-`0x1C`, 9 pilots) | Latin, mixed case: `Jin`, `Mary`, `Santana`, `Gawaine`, `Bao&Mao`, `Arieta` (6 pilots) | katakana |
| VS screen, pilot names (both sides) | katakana art (frames `0x02`-`0x0A`) | Latin, mixed case; the boss `SHADE` in capitals | katakana |
| VS screen, mech names (both sides) | katakana art with a Latin model code (`BX-02`, `RF-009`, ...; frames `0x0C`-`0x1B`) | Latin capitals, no model code (`BLODIA`, `REPTOS`, `FORDY`, `GULDIN`, `R·LIGHTNING`) | katakana with model code |
| VS screen, chapter caption | Japanese box | none | Japanese box |
| `MACHINE SELECT`, `BODY TYPE` | Latin (`BLODIA`, `REPTOS`, `FORDY`, `GULDIN`) | Latin | — |
| Fight HUD | Latin mech names (`BLODIA`, `LIGHTNING`) | Latin | Latin |
| Round end, bonus, continue, game over, initials, options | no name | — | — |
| Versus `VICTORY!` screen | no name art (portrait and quote only) | — | — |
| Versus `RESULT` tally | Latin mech names (`EXP-0031`) | — | — |
| Ending cast roll | Latin names (Japanese names hidden since M7, D-040) | Latin | — |
| Versus mode's select, VS and `SET UP` screens | **UNKNOWN** (not reached; `CYBER.BIN` holds a Latin name list beside `SET UP`, `HANDICAP`, `ROUNDS`) | — | — |
| `RANKING` (attract) | English (`EXP-0001`, `REF-005`); names not checked | — | — |

### Pilots

| Pilot | Saturn select / VS art | US arcade art | Latin in `CYBER.BIN` |
| --- | --- | --- | --- |
| Jin | ジン | `Jin` (select, VS) | `JIN` |
| Santana | サンタナ | `Santana` | `SANTANA` |
| Mary | マリー | `Mary` | `MARY` |
| Arieta | アリエータ | `Arieta` | `ARIETA` |
| Gawaine | ガウェイン | `Gawaine` | `GAWAINE` |
| Bao and Mao | バオ&マオ | `Bao&Mao` | `BAO&MAO` |
| Devilotte | デビロット姫 ("Princess Devilot") | none (not an arcade pilot) | none |
| Chiyomaru | 千代丸 (kanji, as art) | none | `CHIYOMARU` |
| Shade | シェイド | `SHADE` (VS, as the boss) | `SHADE` |
| Tessan | not on the select grid or a VS screen seen | none | none |

The Saturn's grid shows these nine; the select and VS banks hold no tenth
name.

### Mechs (Saturn VS art)

Sixteen names, each katakana with a model code. Their Latin spellings are
the game's own list in `CYBER.BIN` (and the versus `RESULT` tally): BLODIA,
SWORDSMAN, RIOT, REPTOS, LIGHTNING, JACKAL, FORDY, TALANTURA, KILLER BEE,
GULDIN, VICE, CYCLONE, GAITS, HELION, WARLOCK, SUPER-8. The US arcade's VS
art was seen for five (the base bodies and R·LIGHTNING); no route reached a
variant, and Buttons 2-4 at `MACHINE SELECT` pick the same base body. The
VS mech table also has a seventeenth entry, which points at a frame
(`0x1C`) that draws a portrait, not a name; the Latin list's seventeenth
name is ZERO-GOUKI (that the two match is a HYPOTHESIS). The other sixteen
are matched to their Latin names by reading the art.
