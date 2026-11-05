# EXP-0042: The Lines No Ending Box Shows Are Never Read

Task: END-010
Status: DONE
Confidence: CONFIRMED (Jin's and Santana's endings); SUPPORTED (the other seven endings, by their constant posts, D-036)

## Observation

- Jin's ending English needs 872 row bytes (`EXP-0041`). The lines only
  his ending uses, with the two shared speaker-name lines his translated
  boxes free, hold 828.
- `END.BIN`'s line table (`data/text/script_census.json`) has 1,927
  entries: the 1,851 dialogue lines, then ASCII file names (`KANJI.BIN`,
  `SCR00.PIX`, ...). `EXP-0041`'s 44,124 bytes of "lines no ending box
  shows" counted the file names too.
- Box 938's record points into a 4-byte gap between two lines
  (`0x060759D4`), not to a line start.

## Hypothesis

While `END.BIN` is in memory, no code reads the dialogue lines that no
posted ending box shows, so their bytes are free room for the ending's rows.

## Controlled Change

One test image: `END.BIN`'s 1,591 candidate lines (every line a box record
points to and no posted ending box shows; 18 spans, 43,304 bytes) hold the
marker code `0x82A0` in place of each character, NULs kept. Nothing else
changes (28,360 bytes differ).

## Prediction

- Read breakpoints on the 18 spans (cached and cache-through bus addresses)
  log no hit while `END.BIN` is resident, in Jin's ending and in a second
  ending.
- Every box draws its original cells; box calls are the control's.
- A positive control, one read breakpoint on a line Jin's box 408 shows,
  hits when the box opens.

## Inputs and Provenance

| Input | SHA-256 |
| --- | --- |
| `END.BIN` (untouched) | `a4868d8d…f3fa` |
| Test `END.BIN` | `4e45d87c…2f03` |
| Checkpoint `local/end001/checkpoint/jin_ending_a16503.mcs` | as `EXP-0037` |
| Jin control `local/end002/control` | `EXP-0038` |
| Santana control `local/end003/santana` | `EXP-0039`; fetched back from the homelab archive (`Cyberbots-Saturn-EN`), all 1,146 files matching its manifest |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`room.py`](room.py) | Candidate lines and spans → [`room.json`](room.json) (numbers only); the test image `build/end010/room` |
| [`probe.py`](probe.py) | `EXP-0039`'s `ending_probe.py` (commit `ea2e69c`) with `--read-bp` added |
| [`compare_shots.py`](compare_shots.py) | Screenshots against a control by nearest frame |
| `EXP-0039/check_cells.py`, `EXP-0038/compare_runs.py` | Cells drawn per box; events and cells against a control |

Agent Mednafen 1.32.1 (`2fc3d547…aaf`), silent home, no key pressed, no
cold boot.

## Procedure

```bash
E=research/experiments/EXP-0042
./invenv.sh python $E/room.py --out $E/room.json --image build/end010/room
R=$(./invenv.sh python $E/room.py | tail -1)
CUE="build/end010/room/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
export MEDNAFEN_ALLOWMULTI=1
./invenv.sh python $E/probe.py local/end010/room-jin --cue "$CUE" \
  --frames 13400 --cells-until 7000 --read-bp "$R"
./invenv.sh python $E/probe.py local/end010/room-santana --cue "$CUE" \
  --frames 12000 --cells-until 9000 --onhit 06018E0C:060CFF7E=01 \
  --watch 060CFF7E:1 --read-bp "$R"
./invenv.sh python $E/probe.py local/end010/room-positive --frames 2000 \
  --read-bp 0607017C-06070199,2607017C-26070199
./invenv.sh python research/experiments/EXP-0039/check_cells.py local/end010/room-jin
./invenv.sh python research/experiments/EXP-0039/check_cells.py local/end010/room-santana
./invenv.sh python research/experiments/EXP-0038/compare_runs.py local/end002/control local/end010/room-jin
./invenv.sh python research/experiments/EXP-0038/compare_runs.py local/end003/santana local/end010/room-santana
```

2026-11-05, 14:46-14:56 local, three runs in parallel from saved states.

## Actual Result

| Run | `END.BIN` resident (load → `KEND.BIN` load) | Read hits on the room then | Hits outside that window | Boxes drawing their predicted cells |
| --- | --- | --- | --- | --- |
| Jin, test image | 1169 → 6157 | 0 | 14,499 | 21/21 (control 21/21) |
| Santana (list 1 forced), test image | 1169 → 5365 | 0 | 14,499 | 22/22 (control 22/22) |
| Positive control (box 408's line 752), untouched image | 1169 → (run ends 2000) | 30, at 1635 and on, PCs `0x06062788`/`0x0606278E` (the box's character reader) | 0 | — |

The hits outside the window are of other files at the same addresses:
- **13,383 before frame 1169**, at the checkpoint's first poll, before
  `END.BIN` is loaded: the code that held `0x06060000` then.
- **The rest after `KEND.BIN` loads.** `KEND.BIN` (51,368 bytes) loads at
  `0x06060000` and covers `0x06060000`-`0x0606C8A7`. Every later hit reads
  inside that range:
  - a bulk read by `0x0600F324` at one frame (6464 Jin, 5672 Santana), R4
    from `0x0606AECC` to `0x0606B71A`;
  - single reads at `0x0606C820` by `KEND.BIN` code and the main program.

Against the controls:
- box calls are identical, frame for frame;
- the cell dumps taken at the same frames are equal (13 Jin, 14 Santana);
- the only differing disc read is one frame of timing jitter at 14,159
  against 14,160, in attract mode after the ending.
- The posts differ only by the `r4` field `EXP-0039` added.

Screenshots could not discriminate. Poll frames drift by a frame between
runs, and one frame already changes animated scenes, including before
`END.BIN` loads, where the marker cannot act (nearest-frame comparison: 48
identical and 40 differing for Jin, the differences starting at frame 242).

## Conclusion

Prediction met. While `END.BIN` is in memory, nothing reads the 1,591
dialogue lines that no posted ending box shows (18 spans, 43,304 bytes), in
Jin's or Santana's ending. The read breakpoint is shown to fire on a line
that is read. The lines are free room for ending rows. The other seven
endings post only constant scenes through the same code (D-036), so the same
holds for them as SUPPORTED. `END-010`'s rows use the first span
(`0x0AECC`), which `KEND.BIN` overwrites anyway once the dialogue is over.

## Uncertainty and Alternatives

- DMA reads do not trigger CPU read breakpoints. `END.BIN`'s text is read by
  the CPU (the positive control), and the box cells match.
- Only two of the nine endings were run with the marker.

## Reproduction

Run the procedure: `room.json` reproduces byte for byte, and the test image
and the run results are as above.
