# Text Metadata

Derived factual metadata about the game's text: offsets, lengths, hashes and
counts. Never the text itself (`AGENTS.md` rule 21).

| File | Made by | Holds |
| --- | --- | --- |
| `script_census.json` | `./invenv.sh python -m tools.text.script_census local/extracted/saturn_jp/* --out data/text/script_census.json` (`TXT-001`, `EXP-0007`) | Per file with a Shift-JIS line block: size, SHA-256, block bounds, load base, pointer counts, and a table of lines as `[offset, byte length, SHA-256 prefix, pointer count]`; plus a comparison of the files' line sequences. |
