# Translation Records

Pairing and translation records. Official English is never stored here: it is
read from the arcade ROM at build time (`AGENTS.md` rule 21). New
translations, which are this project's own text, will be recorded with their
translator.

| File | Made by | Holds |
| --- | --- | --- |
| `jin_pairing.json` | `./invenv.sh python research/experiments/EXP-0023/pair_jin.py local/ref003/cybotsu-maincpu.bin local/ref003/cybotsj-maincpu.bin --out data/translations/jin_pairing.json` (`PAIR-001`, `EXP-0023`) | For each of Jin's 63 story boxes: its scene, box = arcade slot, Saturn line numbers, per-line labels (`exact` or `edited` against the slot's Japanese), the English record's address, line lengths, and the program images' SHA-256. Plus the arcade's Jin scenes as slot lists. |
