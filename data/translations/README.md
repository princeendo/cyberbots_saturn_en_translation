# Translation Records

Pairing and translation records. Official English is never stored here: it is
read from the arcade ROM at build time (`AGENTS.md` rule 21). New
translations, which are this project's own text, will be recorded with their
translator.

| File | Made by | Holds |
| --- | --- | --- |
| `jin_pairing.json` | `./invenv.sh python research/experiments/EXP-0023/pair_jin.py local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin --out data/translations/jin_pairing.json` (`PAIR-001`, `EXP-0023`) | For each of Jin's 63 story boxes: its scene, box = arcade slot, Saturn line numbers, per-line labels (`exact` or `edited` against the slot's Japanese), the English record's address, line lengths, and the program images' SHA-256. Plus the arcade's Jin scenes as slot lists. |
| `jin_story.json` | `./invenv.sh python -m tools.text.dialogue ... --record data/translations/jin_story.json` (`RE-003`, `EXP-0026`) | For each of Jin's 63 boxes: slot, Saturn lines, the English record's address and SHA-256 (the text is read from the ROM at build time), rows, cells and row addresses; the table codes used, by pair number; the sacrificed Japanese codes; and the sources' hashes. No text. |
| `santana_pairing.json` | `./invenv.sh python research/experiments/EXP-0028/pair_pilot.py local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin --pilot 1 --boxes data/text/santana_boxes.json --out data/translations/santana_pairing.json` (`PAIR-002`, `EXP-0028`) | As `jin_pairing.json`, for Santana's 64 story boxes, plus each slot's English record length and the slots that share a record with a paired box. |
