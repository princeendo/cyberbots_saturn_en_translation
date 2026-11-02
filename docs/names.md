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

Voices: whether any name is spoken was not checked.

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
