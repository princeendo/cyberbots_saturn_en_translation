# EXP-0031: Versus Mode Has a Win-Quote Screen; the Arcade Table Has 624 Slots

Task: WIN-001
Status: DONE
Confidence: CONFIRMED (the loads in each path, the versus `VICTORY!` screen and its line, the arcade table's 624 pointers and the slot-line offset); SUPPORTED (which arcade code reads slots 494-623)

## Observation

`VICTORY.BIN` holds a copy of the dialogue table (D-008) but was never
resident in the 166 REF-005 states (EXP-0018). The REF-005 play session showed
no win quote after a win in arcade mode (`docs/text_surfaces.md`). M5 includes
win quotes only if they are a separate surface.

## Hypothesis

`VICTORY.BIN` drives a screen outside story play, and that screen shows
dialogue-table lines: win quotes.

## Controlled Change

None to the game. CD Play Disc commands and scene posts are logged by
log-mode PC breakpoints; one versus fight's end is forced by holding the
vitality pairs (D-025), with no key presses during the fight.

## Prediction

`VICTORY.BIN` does not load in arcade-mode wins, losses or the attract mode,
and does load after a versus-mode win, before a screen with a dialogue line.

## Inputs and Provenance

- The untouched image (all reads); REF-005 states `f00004138`, `f00012788`,
  `f00023142`, `f00025772`.
- `local/ref003/cybotsj-maincpu.bin` (`2d1e6b25…`) and `cybotsu-maincpu.bin`
  (`18e8827d…`); `data/text/arcade_jp_map.json`.
- WRAM-H of state 12788 by `tools/memory/mcs_extract.py` (validated, D-006).

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`loads.py`](loads.py) | From a state: Play Disc commands (file or audio track) and scene posts, screenshots |
| [`watch.py`](watch.py) | The same, attached to a running cold boot; `--force` holds the vitality pairs; no key presses |
| [`extra_slots.py`](extra_slots.py) | The arcade table's slots 494-623 against Saturn lines; US English per slot |
| `research/experiments/EXP-0019/drive.py` | Cold boot and pad keys; pad 2 added (`KEYS_2`: U, Y, R, X, G, F, V; T is a Mednafen hotkey) |
| `tools/sh2/disasm.py` | The load-script handlers |

Python 3.13.13; Mednafen 1.32.1 with the agent interface (D-007).

## Procedure

```bash
S=local/ref005/session/states; L=research/experiments/EXP-0031/loads.py
./invenv.sh python $L $S/f00004138.mcs local/win001/validate --frames 400
./invenv.sh python $L $S/f00012788.mcs local/win001/win --frames 3000
./invenv.sh python $L $S/f00023142.mcs local/win001/loss --frames 3000
./invenv.sh python $L $S/f00025772.mcs local/win001/attract --frames 12000
ORIG="local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
D="./invenv.sh python research/experiments/EXP-0019/drive.py"; O=local/win001/versus2
$D launch "$ORIG" $O            # wait for frame 3600
$D key $O start 0.5; $D key $O down; $D key $O a        # VERSUS MODE
# pilots, body types, machines: a then p2a, three times; then at SET UP:
$D key $O start 0.3
./invenv.sh python research/experiments/EXP-0031/watch.py $O 150 --force   # twice
./invenv.sh python research/experiments/EXP-0031/watch.py $O 120
$D stop $O
./invenv.sh python research/experiments/EXP-0031/extra_slots.py \
  local/ref003/cybotsj-maincpu.bin local/ref003/cybotsu-maincpu.bin
```

2026-11-03, 14:20-14:50 and 18:19-18:35 local; the user present for the
cold boots. A first versus attempt was stopped at the user's request: its
watcher pressed A every 1.5 s, which kept bringing Mednafen to the front.
`watch.py` now sends no keys.

## Actual Result

### Decoding

From 4138 the log shows Play Disc `1080 58A0` (`STG0AS.BIN`, EXP-0018) and
`KANJI.BIN` at FAD `0x1342`. CR1 without bit `0x80` starts at a track and
index: CD audio (`1000 0C01` is track 12).

### Arcade mode and attract: no `VICTORY.BIN`

| Path | Loads and screens |
| --- | --- |
| Win (12788, 3,000 frames) | Bonus tally; `STG0AS.BIN`, demo files, `KANJI.BIN`; scenes 1 and 2 posted (post-fight and next pre-fight dialogue); VS screen; next stage |
| Loss (23142, 3,000) | `CONTI_0.BIN`; continue countdown; game over; `OPDEMO.BIN` |
| Attract (25772, 12,000) | Intro, ranking, Capcom logo, title, demo fights on stages 00 and 01, twice |

### The load script

In the game's file table (`0x060DCB98`, 24-byte entries), `VICTORY.BIN` is
entry 318, request `0x140` (`STG0AS.BIN` is `0x124`, EXP-0018). A load
script of (handler, argument) pairs (`0x0604C1A0` on; `0x0602B394` and
siblings load a file through `0x0602B1E0`) has a sequence at `0x0604C320`:
`VICTORY.BIN`, `VRAM00.DAT`, `VADEMC`-`VADEME.MAC`. Nothing holds that
address as a pointer.

### Versus mode (cold boot)

- Pad 2 joins with its own keys. Jin (pad 1) against Arieta (pad 2), Blodia
  against Blodia, stage `STG07.BIN`. Versus mode also loads `STG0AS.BIN`.
- The fight ended at time-out with player 1 ahead (`TARGET DESTROYED`, `TIME
  OVER`). Then: **`VICTORY.BIN`** (frame 21415), `AC0.LF`, `PL3E_0.BIN`,
  **`KANJI.BIN`**, audio track 14.
- **Screen** (agent-reviewed): `VICTORY!`, the winner's portrait (Jin) and
  mech, and a one-line Japanese box: Saturn line 959 (the same bytes in all
  three files' tables). Then a `RESULT` tally in English.

### The arcade's table runs to 624 slots

- The Japanese dialogue table at `0x0A30F6` has **624** pointers, not 494:
  `find_tables` stops at 494, and pointers 494-623 (from `0x0A38AE`) point
  to records after slot 493's. The US table at `0x0B33AA` has 624 too, and
  every slot 494-623 has an English record.
- Line 959's text is in `cybotsj` at `0x0AB004`, in slot **558**'s record.
  The US slot 558 is a Jin line of different wording (not quoted here).
- `extra_slots.py`: of 138 record lines in slots 494-623, **79** equal a
  Saturn line exactly, 43 hold codes the map does not know, 16 differ. Each
  match is **slot k = Saturn line k + 405**: slots 494-600 against lines
  899-1005.
- So the Saturn range 899-1850, counted as having no arcade counterpart
  (D-011), starts with lines that do: the VS captions (lines 899 and 900,
  EXP-0012) and the versus win quotes. Which lines are which is open.

The source is unchanged.

## Conclusion

**CONFIRMED:** Cyberbots has a separate win-quote surface. A versus-mode win
loads `VICTORY.BIN` and shows a `VICTORY!` screen with the winner's portrait
and one dialogue-table line. Arcade-mode wins, losses and the attract mode
never load it. The arcade dialogue table has 624 slots; slots 494-623 follow
the Saturn lines from 899 at a fixed offset, and the US set has English in
all of them.

Asked (2026-11-03): "Versus mode has a separate win-quote screen
(VICTORY.BIN: the winner's portrait and a one-line Japanese quote, e.g.
Saturn line 959). The arcade tables hold them in slots 494-623 (slot k =
Saturn line k+405), with US English in all 130 slots. Should versus win
quotes join M5?" The user's answer, verbatim: "Add to M5 (Recommended)".

## Uncertainty and Alternatives

- Which arcade code reads slots 494-623, and how a quote is chosen (winner,
  loser, random), is not traced; the US slot 558 differs in wording from the
  Japanese, so pairing may be by game logic, not by meaning (MSHvSF's lesson).
- Whether a challenger's fight in arcade mode also shows the screen was not
  tried.
- The split of lines 899-1028 into captions and quotes, and slots 601-623,
  are not measured.

## Reproduction

Run the procedure. Expect no `VICTORY.BIN` in the three state runs, the
`VICTORY!` screen with line 959 after the forced versus win, and the
extra-slot counts above.
