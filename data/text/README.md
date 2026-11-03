# Text Metadata

Derived factual metadata about the game's text: offsets, lengths, hashes and
counts. Never the text itself (`AGENTS.md` rule 21).

| File | Made by | Holds |
| --- | --- | --- |
| `script_census.json` | `./invenv.sh python -m tools.text.script_census local/extracted/saturn_jp/* --out data/text/script_census.json` (`TXT-001`, `EXP-0007`) | Per file with a Shift-JIS line block: size, SHA-256, block bounds, load base, pointer counts, and a table of lines as `[offset, byte length, SHA-256 prefix, pointer count]`; plus a comparison of the files' line sequences. |
| `arcade_jp_map.json` | `tools/text/arcade_pairing.py` (`REF-006`, `EXP-0010`) | The arcade Japanese character codes (16-bit) and the Shift-JIS character each stands for, learned from the two scripts. A code table, not text. |
| `saturn_arcade_pairing.json` | same | Per Saturn dialogue line (0-1850): `null` or `[arcade slot, line in record, "exact" or "edited", similarity]`; the arcade slot is also the English slot (D-011). Plus counts, unpaired runs and unpaired arcade lines. |
| `jin_boxes.json` | `./invenv.sh python research/experiments/EXP-0022/box_list.py local/extracted/saturn_jp/STG0AS.BIN --out data/text/jin_boxes.json` (`RE-002`, `EXP-0022`) | Jin's 22 scenes (pilot 0, list `0x060AA840`): each scene's script address and its boxes, with each box's record address, header (x, y, attribute) and Saturn line numbers. Scenes 21 and 0-15 are the story; 16-20 are the ending (from `END.BIN`, excluded). |
