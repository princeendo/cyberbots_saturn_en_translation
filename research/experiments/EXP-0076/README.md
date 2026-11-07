# EXP-0076: Who the Saturn-Only Pilots Are, How They Are Reached, and What They Show (SPECIAL-010)

Task: SPECIAL-010
Status: DONE
Confidence: CONFIRMED (the select ring and each list's pilot, forced on
screen; list 7's route, forced and repeated; the mech-16 VS name art, forced;
the per-list surface counts, from the game's tables); SUPPORTED (the unlock
rules, by code reading: no unlock was earned in play); HYPOTHESIS (that
`0x060CFF01` counts continues)

## Observation

Lists 6-8 match no arcade pilot (D-026). From Jin, one and two moves left
reach lists 6 and 8 (D-031); list 7 was never reached. The name art has nine
pilots, the last three Devilotte, Chiyomaru and SHADE (`LOC-004`); Tessan
has none. Secondary sources mention an Akuma mech code (`docs/references.md`).

## Hypothesis

Each of lists 6-8 is one select-screen pilot; list 7 is reached by an
unlock, a code or a select position not tried; their text is the story,
win-quote, caption and ending boxes the earlier censuses list.

## Controlled Change

None to the image. From REF-005 saved states in the silent home (no key,
no cold boot), one variable per run:

| Run | State | Change |
| --- | --- | --- |
| `sel` | 3070 (pilot select) | the select byte `0x060D02BE` = 6, 7, 8, 0 |
| `route0`, `route6`-`route8`, `route7b` | 4138 (machine select confirmed, before the story) | player 1's pilot bytes `0x060D02B2` and `0x060D02BE` = 0, 6, 7, 8 |
| `akuma` | 4138 | pilot 0; body `0x060D02BD` = 8, mech `0x060D02C1` = 16 |
| `msel`, `minit04`, `minit08` | 3247 (machine select) | unlock words `0x060D9232`-`3A` = 1; body 4 or 8; `+0x2E0` = 0 to re-run the screen's set-up |

## Prediction

The select ring includes list 7; forcing a pilot at state 4138 posts that
list's opening scene and sets the stage byte to 9 x the list.

## Inputs and Provenance

| Input | SHA-256 |
| --- | --- |
| `local/ref005/session/states/f00003070.mcs` | `b1eed8f2…` |
| `f00003247.mcs` | `9e7c187d…` |
| `f00004138.mcs` | `3eb789da…` |
| `STG0A.BIN`, `STG0AS.BIN`, `CYBER.BIN`, `END.BIN`, `VICTORY.BIN` | untouched, `local/extracted/saturn_jp` |
| `data/text/pilot_census.json`, `reachability.json`, `ending_surfaces_others.json`, `ending_surfaces.json` | earlier records |

## Tools and Environment

| Tool | SHA-256 | Use |
| --- | --- | --- |
| [`route.py`](route.py) | `4e836a0b…` | State 4138, pilot bytes (and `--write`), scene-post log, stage byte, screenshots |
| `research/experiments/EXP-0056/poke.py` | | State, writes, screenshots |
| `research/experiments/EXP-0062/session.py` + `tools.mednafen.agent` | | The `sel` session: writes, write and PC logs |
| [`census.py`](census.py) → `data/text/special_census.json` | `1c42c3e5…` → `2f0b2a0d…` | Per-list surfaces |
| `tools/sh2/disasm.py` | | `STG0A.BIN`, `CYBER.BIN`, `END.BIN` |

Mednafen 1.32.1 with the agent interface (D-007), Python 3.13.

## Procedure

```bash
S=local/ref005/session/states
./invenv.sh python research/experiments/EXP-0062/session.py launch $S/f00003070.mcs local/sp010/sel
#   agent: write 0x060D02BE = 6, 7, 8, 0; 30 frames; screenshot each (pilot6-8, pilot0)
#   agent: log writes to 0x060D53C8 (the name actor's record) and PC 0x060621B6 (r6, r13)
./invenv.sh python research/experiments/EXP-0062/session.py stop local/sp010/sel
for p in 0 6 7 8; do
  ./invenv.sh python research/experiments/EXP-0076/route.py local/sp010/route$p $p --frames 1800; done
./invenv.sh python research/experiments/EXP-0076/route.py local/sp010/route7b 7 --frames 1800
./invenv.sh python research/experiments/EXP-0076/route.py local/sp010/akuma 0 --frames 2700 \
  --write 060D02BD=08 --write 060D02C1=10
W="--write 060D9232=0001 --write 060D9234=0001 --write 060D9236=0001 --write 060D9238=0001 --write 060D923A=0001"
./invenv.sh python research/experiments/EXP-0056/poke.py local/sp010/msel --state $S/f00003247.mcs $W --frames 120 --shots 120
for b in 04 08; do ./invenv.sh python research/experiments/EXP-0056/poke.py local/sp010/minit$b \
  --state $S/f00003247.mcs $W --write 060D02BC=00 --write 060D02BD=$b --frames 150 --shots 30,150; done
./invenv.sh python research/experiments/EXP-0076/census.py
./invenv.sh python tools/sh2/disasm.py --base 0x06060000 --start 0x06060780 --end 0x06060F14 local/extracted/saturn_jp/STG0A.BIN
./invenv.sh python tools/sh2/disasm.py --base 0x0600D000 --start 0x06035296 --end 0x06035330 local/extracted/saturn_jp/CYBER.BIN
./invenv.sh python tools/sh2/disasm.py --base 0x06060000 --start 0x060601C8 --end 0x06060230 local/extracted/saturn_jp/END.BIN
```

2026-11-07, local. No cold boot, no keys.

## Actual Result

### The select screen (`STG0A.BIN`)

- **The cursor is the player record's `+0x2E2`** (player 1: `0x060D02BE`):
  `0x060621B6` reads it to pick the name (pose table `0x06064EBC`).
  `EXP-0056` had not found it.
- **Left and Right follow a table of nine (left, right) pairs at
  `0x060643C0`:** one ring, 0 → 2 → 1 → 4 → 5 → 3 → 7 → 8 → 6 → 0 going
  right. The top row holds the six arcade pilots, the bottom row lists 7,
  8, 6. From Jin: list 6 is one move left, list 8 two, **list 7 three left
  (or six right)**. Up and Down jump between rows by fixed rules (from
  0, 1 or 2 Down goes to 7). No pilot is locked.
- **Forced on screen** (`sel`): the byte at 6, 7 and 8 moved the 1P cursor
  and showed each pilot's portrait and name (agent-read): **list 6 Princess
  Devilot** (デビロット姫, with two henchmen; `4c7dc979…`), **list 7
  Chiyomaru** (千代丸, a large man beside him; `11e340bb…`), **list 8
  SHADE** (シェイド; `38df6be8…`).

### Routes (from state 4138)

| Pilot bytes | First posts (frame, list, scene) | Stage byte |
| --- | --- | --- |
| 0 (control) | (614, 0, 21), (1294, 0, 0) | 0 |
| 6 | (520, 6, 18) | 54 |
| 7 | (521, 7, 0); repeat `route7b` (522, 7, 0), all six screenshots identical | 63 |
| 8 | (527, 8, 0) | 72 |

- The control matches D-031 (Jin: 21, then 0). Lists 7 and 8 start at
  scene 0 (no opening scene before it in 1,800 frames).
- **List 7's opening narration** (agent-read, `f00900` `7be89d16…`,
  `f01500` `d5bdc458…`) names the son Chiyomaru and **Tessan** (鉄山),
  his father's former right-hand man and a genius strategist, whom Chiyomaru
  visits. Tessan is a character of Chiyomaru's story, not a pilot.

### Pilot 6-8 restrictions and unlocks (code; SUPPORTED)

- **Fixed mechs.** On confirming a pilot above 5 (`STG0A.BIN`
  `0x06060CB4`, and `CYBER.BIN` `0x060355EC`), unless the long
  `0x060D9288` is set or the word `0x060D9230 + 2 × (pilot − 5)` is
  non-zero, the mech is set from `0x060643D2` (pilots 6, 7, 8 → mechs 12,
  13, 11) and machine select is skipped.
- **Extra bodies.** Machine select's body cursor (`+0x2E1`) goes past the
  four shown bodies only to bodies whose word `0x060D9230 + 2 × (body − 3)`
  is non-zero (`0x06060D80`-`0x06060DF2`); body 4-8 → mech 12, 13, 14, 15,
  16 (`0x06060E4A`).
- **The words come from five saved bytes** `0x060D9306`-`0x060D930A`
  (`CYBER.BIN` `0x060352A4`; save offset +138, EXP-0062), so one byte
  unlocks both a pilot's free choice and a body: `9306` pilot 6 / body 4,
  `9307` pilot 7 / body 5, `9308` pilot 8 / body 6, `9309` body 7,
  `930A` body 8.
- **Set by `END.BIN` (`0x060601C8`) at the end of an ending**, with the
  difficulty `0x060D9290` above 2 (EXP-0062): finishing with pilot 6, 7
  or 8 sets that pilot's byte; all three set → `9309`; `0x060CFF01` = 0 →
  `930A`. `0x060CFF01` is the winner's record `+0x2F0`, copied at the last
  fight's round end (`CYBER.BIN` `0x06018E00`, with the pilot byte, D-036);
  that it counts continues is a HYPOTHESIS. So the "Akuma mech code" is an
  unlock earned in play, not a typed code.

### What the unlocks show

- **Mech 16** (`akuma`): the story scene showed an orange Akuma-like mech
  (`f02400` `4df8cd9f…`); the VS screen drew its name as three blue kanji
  with the model code `G-18EX` (agent-read; the kanji are small, probably
  豪鬼號; `f02700` `a1d77da5…`). The other VS names on that screen were
  the usual art. This name art is not in `LOC-004`'s sixteen mechs.
- **Machine select** with the unlock words set and body 4 or 8 forced
  (`minit04` `ac266f71…`, `minit08` `8dccf470…`): the body's mech is drawn
  and an empty fifth label box appears under the four labels. Whether a
  real unlocked screen draws a label there is not known from these states.
- Win quotes, story and endings are chosen by pilot (D-030, D-031, D-036),
  so a mech adds no dialogue.

### Surfaces (`data/text/special_census.json`)

| List | Pilot | Story boxes / lines / characters | Win quotes | VS captions | Ending boxes / lines / characters |
| --- | --- | --- | --- | --- | --- |
| 6 | Devilotte | 119 / 244 / 3,002 | 7 / 9 / 123 | 9 / 9 / 84 | 15 / 28 / 336 |
| 7 | Chiyomaru | 103 / 198 / 2,350 | 8 / 11 / 136 | 9 / 9 / 78 | 27 / 51 / 586 |
| 8 | SHADE | 117 / 196 / 2,190 | 7 / 12 / 123 | 9 / 9 / 69 | 17 / 35 / 414 |
| Distinct | | 339 / 636 / 7,538 | 22 / 32 / 382 | 27 / 27 / 231 | 59 / 114 / 1,336 |

- Every story box is in `TXT-010`'s "posted" class; quotes and captions in
  their own classes. No box is shared with the roster's story; one line is
  (661, list 6). In the endings, list 7 opens the blank box 1072 and list 8
  the speaker names 601 and 605 (English since M8, D-047).
- The endings draw with `KANJI.BIN` (D-047) and end in the shared cast
  roll, staff credits and thank-you screen (`END-022`). Each loads its own
  pictures (`STDEM6`/`7`/`8.PIR`). Whether they have voices was not
  examined (audio, not text).

## Conclusion

The three Saturn-only pilots are Devilotte (list 6), Chiyomaru (list 7,
with Tessan in his story) and SHADE (list 8). All three are on the select
ring from the start; list 7 is three moves left of Jin, and its route was
forced. Unlocks earned by finishing endings at difficulty 3 or higher give
those pilots a free mech choice and add five bodies, the last an Akuma mech
with Japanese name art. Their text is 339 story boxes, 22 win quotes, 27
captions and three endings (59 boxes): about 9,500 Japanese characters, all
on paths a player can reach.

## Uncertainty and Alternatives

- The unlock rules are code reading; no unlock was earned in play, and the
  meaning of `0x060CFF01` is not tested.
- The fifth machine-select label (bodies 4-8) needs a real unlocked screen:
  a save with the unlock bytes and a cold boot, asked first.
- The mech-16 kanji are read from a small image.
- The 2P side, versus mode and continue screens with these pilots were not
  forced; by the code they choose text by pilot as the 1P story does.
