# Arcade Metadata

Derived factual metadata about the arcade (CPS-II) reference sets: addresses,
counts, hashes and code statistics. Never ROM data or decoded text
(`AGENTS.md` rule 21); decoded text goes only to the ignored `local/ref003/`.

| File | Made by | Holds |
| --- | --- | --- |
| `dialogue_tables.json` | `tools/reference/cybots_text.py` (`REF-003`, `EXP-0008`) | For each held set: program-image SHA-256 and its three dialogue tables (address, slots, distinct records, record range, Latin-map coverage, unmapped codes, header patterns, record-content SHA-256). |
