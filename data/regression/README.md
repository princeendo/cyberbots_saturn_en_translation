# Regression References

Hashes that a rebuild must reproduce. Each file names its rebuild command; a
change to the tools that alters a hash needs a new reference and the reason
(`AGENTS.md`).

| File | Build |
| --- | --- |
| `re003_jin.json` | Jin's story in English (`RE-003`, `EXP-0026`): the replacement files' and Track 01's SHA-256, the changed-sector count, the prediction and record hashes, and the checks that passed. Reproduced unchanged by the multi-pilot compiler (`RE-006`, `EXP-0029`). |
| `re007_jin_santana.json` | Jin + Santana in English (`RE-007`, `EXP-0030`): the same fields, both pilots' record hashes, and the checks that passed. From this build on, `data/translations/jin_story.json` is this build's record; `re003_jin.json`'s record hash is the record of a Jin-only build (`--record`). |
| `re008_roster.json` | The M5 roster in English (`RE-008`, `EXP-0036`): story in `STG0AS.BIN`, win quotes in `VICTORY.BIN`; the replacement files', Track 01's, prediction's, changes' and records' SHA-256, and the checks that passed. From this build on, `data/translations/<pilot>_story.json` are this build's records; `re007_jin_santana.json`'s record hashes are those of the Jin + Santana build (`--record-dir` elsewhere). |
