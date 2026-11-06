# EXP-0056: Census of Every Name-Art Surface

Task: LOC-001
Status: DONE
Confidence: CONFIRMED (the surfaces seen and what each shows on the three releases; the select and VS name records and their frames); UNKNOWN (versus mode's own screens; the US arcade's art for mech variants)

## Observation

- D-013: the names are the same in both regions; the pilot-select and VS
  name art is katakana on the Saturn, Latin on the US arcade.
- The REF-005 session reached the select and VS screens with Jin only, so
  the other pilots' Saturn art had not been seen.

## Hypothesis

The Saturn shows name art only on the pilot select and the VS screen (pilot
and mech names); every other surface is Latin or nameless.

## Controlled Change

None to the disc. On the Saturn, from saved states, one RAM write per run:
the frame number of the record that draws the name, so the real screen
shows another pilot's or mech's name. On the arcade, inputs only.

## Prediction

Name art on the select and VS screens only; the US arcade Latin there.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched image | as `references/saturn_jp/README.md` |
| Session states | `local/ref005/session/states/f00003070.mcs` (select), `f00006805.mcs` (VS) |
| Arcade sets | `cybotsu`, `cybotsj` (`references/arcade/manifest.json`), MAME 0.289 |
| `CYBER.BIN` | as the listing; its Latin name lists (static search) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`trace.py`](trace.py) | Log PC/read/write breakpoints from a state |
| [`poke.py`](poke.py) | Load a state, write RAM, screenshots |
| [`arcade_runs.py`](arcade_runs.py) | MAME timelines: select cursor, picks, body types, Buttons 2-4 |
| [`census.py`](census.py) | → [`census.json`](census.json) (screenshot hashes, the agent's readings) |
| `tools.memory.vdp1_sprites`, `tools.memory.mcs_extract`, `tools.sh2.disasm` | Sprite list, RAM, code |

## Procedure

```bash
T=research/experiments/EXP-0056; ST=local/ref005/session/states
./invenv.sh python $T/trace.py local/loc001/tr-obj --state $ST/f00003070.mcs --pc 060118E4 --frames 1
./invenv.sh python $T/trace.py local/loc001/tr-vs --state $ST/f00006805.mcs --pc 060118E4 --frames 1
for f in 14 15 16 17 18 19 1a 1b 1c; do ./invenv.sh python $T/poke.py local/loc001/sel-name-$f \
  --state $ST/f00003070.mcs --write 06065198=00$f --every-frame --frames 40 --shots 40; done
for f in 02 03 04 05 06 07 08 09 0a; do ./invenv.sh python $T/poke.py local/loc001/vs-pilot-$f \
  --state $ST/f00006805.mcs --write 06087E9E=00$f --every-frame --frames 20 --shots 20; done
for f in 0c 0d 0e 0f 10 11 12 13 14 15 16 17 18 19 1a 1b 1c; do ./invenv.sh python $T/poke.py \
  local/loc001/vs-mech-$f --state $ST/f00006805.mcs --write 06087A44=00$f --every-frame --frames 20 --shots 20; done
./invenv.sh python $T/arcade_runs.py --sets cybotsu,cybotsj
./invenv.sh python $T/census.py --out $T/census.json
```

2026-11-06, 08:40-10:00 local. No key, no cold boot. (`vs_us.json` and
`vs_jp.json`, each run's first VS snapshot, come from a scan for the yellow
"VS" in the screen's centre; the scan is inline in the session log.)

## Actual Result

### How the names are drawn (Saturn)

- Both screens draw through the shared sprite-part routine (`0x060118E4`,
  then `0x060113F0`, D-040's). An actor points at a 16-byte record of a pose
  table; the record's word at +6 is the frame, the byte at +5 the bank. The
  VDP1 command list is built at WRAM-H `0x060E1000` and copied to VDP1.
- **Pilot select** (module `STG0A.BIN`, loaded at `0x06060000`): the name
  record is `0x06065192` (frame `0x14`, Jin); the nine records from it hold
  frames `0x14`-`0x1C`, one per pilot. Writing a frame number shows that
  name under the portrait (frame `0x15` showed サンタナ).
- **VS screen**: a pilot table at `0x06087E72` (word offsets) leads to nine
  name records from `0x06087E98` (frames `0x02`-`0x0A`); a mech table at
  `0x06087A1C` leads to 17 records from `0x06087A3E` (frames `0x0C`-`0x1C`).
- The pilot byte of the fighter record (`0x060D02B2`) is not the select
  cursor (writing it changed nothing); the cursor variable is not found.

### What each release shows

`docs/names.md`, "Name-Art Census": the surface table, the nine pilots and
the sixteen mechs, with the US and Japanese arcade forms. In short:

- Name art only on the pilot select (pilot names) and the VS screen (pilot
  and mech names); everything else seen is Latin or nameless.
- US arcade: pilots in mixed case (`Jin`, `Bao&Mao`), the boss `SHADE` and
  the mechs in capitals, mechs without model codes.
- Saturn-only names: Devilotte (デビロット姫) and Chiyomaru (千代丸) have
  art but no US art; Tessan has none on these screens.
- `CYBER.BIN` holds Latin lists of 17 mechs and 8 pilots (no Devilotte)
  beside the versus `SET UP` labels.

### Not reached

- Versus mode's select, VS and `SET UP` screens (no state; a cold boot with
  key presses would be needed).
- The US arcade's VS art for mech variants: no route met one, and Buttons
  2-4 at `MACHINE SELECT` pick the base body.

## Conclusion

Prediction met for every surface reached. The name art to replace is the
pilot-select names (9) and the VS screen's pilot (9) and mech (16) names.

## Uncertainty and Alternatives

- The versus-mode screens may show more name art (or Latin text from the
  `CYBER.BIN` list); `LOC-002` checks them.
- That the VS table's seventeenth entry is ZERO-GOUKI is a HYPOTHESIS.
- Readings of the art are the agent's (katakana and one kanji name).

## Reproduction

Run the procedure. Expect `census.json`'s hashes.
