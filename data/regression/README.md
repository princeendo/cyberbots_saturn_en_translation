# Regression References

Hashes that a rebuild must reproduce. Each file names its rebuild command; a
change to the tools that alters a hash needs a new reference and the reason
(`AGENTS.md`).

| File | Build |
| --- | --- |
| `re003_jin.json` | Jin's story in English (`RE-003`, `EXP-0026`): the replacement files' and Track 01's SHA-256, the changed-sector count, the prediction and record hashes, and the checks that passed. Reproduced unchanged by the multi-pilot compiler (`RE-006`, `EXP-0029`). |
| `re007_jin_santana.json` | Jin + Santana in English (`RE-007`, `EXP-0030`): the same fields, both pilots' record hashes, and the checks that passed. From this build on, `data/translations/jin_story.json` is this build's record; `re003_jin.json`'s record hash is the record of a Jin-only build (`--record`). |
| `re008_roster.json` | The M5 roster in English (`RE-008`, `EXP-0036`): story in `STG0AS.BIN`, win quotes in `VICTORY.BIN`; the replacement files', Track 01's, prediction's, changes' and records' SHA-256, and the checks that passed. From this build on, `data/translations/<pilot>_story.json` are this build's records; `re007_jin_santana.json`'s record hashes are those of the Jin + Santana build (`--record-dir` elsewhere). |
| `end010_jin_ending.json` | The M5 roster plus Jin's ending in English (`END-010`, `EXP-0045`): the ending in `END.BIN` and `SE.DAT`'s font, the cast roll's Japanese names hidden (`KEND_1.BIN`), the QSound line erased (`QSD.PIX`); the replacement files', Track 01's, both predictions', both change lists' and the ending record's SHA-256, and the checks that passed. The story files, `prediction.json` and `changes.json` equal `re008_roster.json`'s. |
| `end011_jin_timing.json` | Jin's ending retimed (`END-011`, `EXP-0048`, `--retime`): the same fields as `end010_jin_ending.json` plus `ending_timing.json`'s hash. Only `END.BIN` differs from END-010's build, in its timing words and cues. |
| `end023_roster_endings.json` | The M8 image (`END-023`, `EXP-0050`): the M5 roster plus all six roster endings in English (`--endings data/text/m8_endings.json`): the same fields as `end011_jin_timing.json` and the six ending records' hashes. From this build on, `data/translations/<pilot>_ending.json` are this build's records; `end010_jin_ending.json`'s record hash is that of the Jin-only build. `KANJI.BIN` differs from `re008_roster.json`'s by one glyph (the 153rd story sacrifice). |
