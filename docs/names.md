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

Voices: see "Names in Voice" below (`LOC-003`).

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

## Where the Name Art Is Stored (`LOC-002`, `EXP-0057`)

| Surface | Stored in | Format | Latin version on the disc |
| --- | --- | --- | --- |
| Pilot select names (9) | `SELECT.VAD` `0x17840`-`0x19B20` | raw 4 bpp, bank 56 | none (all 149 frames of bank 56 drawn) |
| VS pilot names (9) | `PL3F_0.BIN` `0x4324`-`0x5A..` | compressed type 2, bank 63 | none (all 122 frames of bank 63 drawn) |
| VS mech names (16) | `PL3F_0.BIN` `0x5E58`-`0x97..` | compressed type 2, bank 63 | none |
| Versus mode select, `SET UP`, VS | the same banks | — | none |

Latin names that do exist elsewhere: the cast roll's (`KEND_1.BIN`, its own
small style, D-040; type 2, D-059), `CYBER.BIN`'s plain-text lists (8
pilots, 17 mechs; not seen drawn), bank 56's `BODY TYPE` list of the four
base bodies (D-059), and `FIX.BIN`'s sixteen mech name plates (`EXP-0068`). Bank 63 also holds a Latin banner "G.O.D." (frame `0x0B`)
and a third banner style for story-only characters (frames `0x74`-`0x79`);
where these show is not known.

Room: `SELECT.VAD` can take Latin names of the same size in place, but has
no room to keep the katakana as well (1,440 bytes of slack). `PL3F_0.BIN`'s
name records are 20,804 bytes compressed; Latin art in a literal-only
encoding would need about 7.8 KB more, and the file has 288 bytes of slack.

## Names in Voice (`LOC-003`, `EXP-0058`)

Heard by the user, one clip at a time:

| Moment | Speech | Name heard |
| --- | --- | --- |
| Pilot select, each pick (versus, Jin and Arieta) | none | — |
| VS screen | none | — |
| Round start | none | — |
| Knockout win | "TARGET DESTROYED" | — |
| Story narration (Jin's introduction) | Japanese | "jin", where the text names Jin |
| Versus `VICTORY!` quote | yes | perhaps "Jin" (unsure; the quote's text has no name) |
| Ending dialogue (Santana's) | yes | none |

No announcer calls a name. Names are heard only inside voiced Japanese
lines, in their Japanese readings of the same names, so they cannot
disagree with Latin art; no voice change is planned.

## Latin Name Art, Decided (`LOC-004`, `EXP-0059`)

The user's choices (2026-11-06), from samples drawn into the real screens:
the arcade dialogue letters inside the Saturn's own banners; case as the US
arcade (pilots mixed case, `SHADE` and the mechs in capitals); the mech
model codes kept, placed right after each name; "Devilotte" for her. The
spellings are in `data/translations/name_art.json`:

- Pilots: Jin, Santana, Mary, Arieta, Gawaine, Bao&Mao, Devilotte,
  Chiyomaru, SHADE.
- Mechs: BLODIA, B·SWORDSMAN, B·RIOT, REPTOS, R·LIGHTNING, R·JACKAL, FORDY,
  F·TALANTURA, F·KILLER BEE, GULDIN, G·VICE, G·CYCLONE, GAITS, HELION,
  WARLOCK, SUPER-8 (each with its Saturn model code).

Tessan has no name art; his romanization belongs to `SPECIAL-001`.

## Latin Name Art, Built (`LOC-005`, `EXP-0060`)

`--name-art data/translations/name_art.json` builds the decided names
(D-053): one part per select name in `SELECT.VAD` (with its part table in
`STG0A.BIN`), and type-2 records in `PL3F_0.BIN` for the VS screen (one
per pilot, two per mech: name, then model code). All 34 names were seen on
screen from saved states. The katakana art is replaced, not kept; a
switchable Japanese version (`OPT-001`) needs storage of its own. The
cold-boot play check is `LOC-006`.
