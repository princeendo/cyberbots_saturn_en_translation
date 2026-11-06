# EXP-0064: Free RAM for the Names Switch's Code

Task: OPT-003
Status: DONE
Confidence: CONFIRMED (two ranges unused once `CYBER.BIN` runs: logs,
canaries, a cold boot, static review); DISPROVEN (the largest zero range is
the VDP1 command list's tail)

## Observation

- `OPT-002` (`EXP-0063`): the switch needs a little code at two load sites
  (option A) or about 31 KB of RAM (option B).
- XvSF lesson 13: zero bytes may be in use (XvSF's first switch build put
  code in the interrupt-handler table and hung the title).

## Hypothesis

Some WRAM-H ranges that are constant in every saved state are never read or
written by the game, by any CPU or DMA, once its program runs.

## Controlled Change

None to the game. Canary fills (`0xA5`) of candidate ranges in saved
states; read/write breakpoints; one cold boot.

## Prediction

At least one range shows no CPU access, no canary change, no access in a
cold boot with `3M RAM MODE` off, and no static path, after `CYBER.BIN` is
loaded.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched image | `local/disc_images/cyberbots_saturn_jp_2m/` |
| Session states | all 166 in `local/ref005/session/states` (4 MB cart, `3M RAM MODE` on) |
| Ending checkpoints | `local/end001/checkpoint/jin_ending_a16503.mcs` (15,500 frames), `local/end002/control/` s07284, s09106, s12488, s13113, `local/end010/timing-pre/` s01800, s05061, `local/end010/cast-pre/s06450.mcs` (1,800 frames each) |
| `CYBER.BIN` | resident at `0x0600D000`-`0x0605DE70` (by matching RAM) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`census.py`](census.py) | Bytes constant across states, one process → [`census.json`](census.json) |
| [`watch2.py`](watch2.py) | Per segment (each state run to the next): canary fill, read/write breakpoints, the address of each hit rebuilt from its instruction and registers, canary bytes changed, screenshot hash |
| [`attribute.py`](attribute.py) | The SH-2 data-access forms: address, size, read/write |
| [`cold_watch.py`](cold_watch.py) | Cold boot with no cart and breakpoints from frame 0; attribution of the log |
| Background workflow | Three independent reviewers (pointers, computed addresses, coverage gaps) and a judge, static only → [`review/`](review/) |

## Procedure

```bash
E=research/experiments/EXP-0064
X="--extra local/end001/checkpoint/jin_ending_a16503.mcs:15500 --extra local/end002/control/s07284.mcs:1800 \
 --extra local/end002/control/s09106.mcs:1800 --extra local/end002/control/s12488.mcs:1800 \
 --extra local/end002/control/s13113.mcs:1800 --extra local/end010/timing-pre/s01800.mcs:1800 \
 --extra local/end010/timing-pre/s05061.mcs:1800 --extra local/end010/cast-pre/s06450.mcs:1800"
./invenv.sh python $E/census.py local/opt003/census --extra <the 8 ending states> --out-json $E/census.json
./invenv.sh python $E/watch2.py local/opt003/w2 --ranges $E/ranges_cold.json $X      # -> watch_candidates.json
./invenv.sh python $E/cold_watch.py launch local/opt003/cold --ranges $E/ranges_cold.json --cart none
#   presses with EXP-0019/drive.py key (start x3, down, a = VERSUS MODE; right x2; a, p2a; a, p2a; a, p2a, a; start)
./invenv.sh python $E/cold_watch.py report local/opt003/cold                         # -> cold_boot.json (attributed)
./invenv.sh python $E/watch2.py local/opt003/w4 --ranges $E/ranges_final.json $X     # -> watch_final.json
./invenv.sh python $E/watch2.py local/opt003/w4-ctl --control --ranges $E/ranges_final.json $X
./invenv.sh python $E/watch2.py local/opt003/w4-ctl2 --control --ranges $E/ranges_final.json $X
```

2026-11-06, 12:40-14:40 local. One cold boot, asked first: "Yes, run it
(Recommended)" (no cart, versus mode, 16 single presses, about 25,700
frames). `ranges_pass1.json` was a first pass whose log is superseded.

## Actual Result

### Candidates (`census.json`)

Over 174 states no byte of WRAM-L is constant in a run of 256 or more;
WRAM-H has 28 such runs. Nineteen candidates were watched: the all-zero
runs of about 1 KB or more above `0x06004000` (not the directory table's
spare entries `0x060DEA10`-`0x060DEF68`, which `OPT-002` may use), and six
zero runs inside `CYBER.BIN`'s own file image.

### What uses them

| Range | Bytes | Finding |
| --- | --- | --- |
| `0x060085A8`, `0x06009098`, `0x0600CBE0`-`0x0600CFE8` | 1,732 / 1,488 / 1,032 | Task stacks (the task switcher `0x0600D020` saves registers; its stack pointer at `0x0600CFE8`) |
| `0x06009C54`, `0x0600ACBC` | 3,996 / 6,876 | Rare writes by `0x06000926` and `rte` at `0x0600094A`: an interrupt stack |
| `0x060DC258` | 1,031 | A CD load buffer at boot |
| `0x060DA3D8`, `0x060CEC40`, `0x060CF738` | 2,956 / 1,904 / 952 | `CYBER.BIN`'s BSS (`0x060CC000`-`0x060DF8A8`, cleared by its start-up code `0x0600D3E6`): no access after the clear in the logs, but program variables; not used |
| `0x060CB7CC`, `0x060CB3B8` | 2,100 / 996 | Just above the load areas of `STDEMO.MAP` (to `0x060CB134`) and `PL13_0.BIN` (to `0x060CB038`); cleared by the boot program; not reviewed; not used |
| `0x060E32E4`-`0x060E8000` | 19,740 | **The tail of the VDP1 command list** (review): commands are appended at `0x060CE668` from `0x060E1000` with no bound and copied to VDP1 by SCU DMA each frame (`0x0600FF7C`); the game's own high-water mark (`0x06047D30` = `0x2300` at state 27173) ends exactly at `0x060E3300`, so the census edge is the busiest frame seen, and that frame's DMA read A's first 28 bytes. **DISPROVEN** as free |
| `0x0604E2E8` and four other `CYBER.BIN` runs | 112-264 | Zero runs in `CYBER.BIN`; not reviewed statically; not proposed |
| **`0x060DF8A8`-`0x060E0EA4`** | **5,628** | **Unused**, below |
| **`0x06055424`-`0x06055824`** | **1,024** | **Unused**, below (trimmed from `0x06055830`: the last 12 bytes are record 0 of a box table at `0x06055824`, pointed to from `0x06057044`; its readers skip index 0) |

### The two ranges

- **`0x060DF8A8`-`0x060E0EA4`** (5,628 bytes): it starts at `CYBER.BIN`'s
  linker end (its start-up code clears BSS up to `0x060DF8A8` and copies 0
  bytes there; nothing else names the address) and ends under the stale
  stack of the boot program `0.BIN` (loaded at `0x060A0000`, stack from
  `0x060E1144`). No CPU access, no canary change in 174 segments
  (`watch_final.json`, `watch_candidates.json`); none in the cold boot; no
  literal, load destination, DMA set-up or loader range reaches it (review).
  Code placed there must be copied in by the game's program at run time.
- **`0x06055424`-`0x06055824`** (1,024 bytes): zero bytes in `CYBER.BIN`'s
  file (offsets `0x48424`-`0x48824`), so anything placed there in the file
  is loaded with the program at boot. Written only in the three segments
  before `CYBER.BIN` is loaded (states 384-747: the boot program uses that
  memory; `CYBER.BIN` is in RAM from state 928, 159 of 162 sectors equal,
  the rest its live data) and never after, in any segment or the cold boot.
  The damage table below it (`0x06054424`, 4 KB) is indexed without a
  bound, but no attack value on the disc reaches its rows 128-159 (review).

### Other observations

- The cold boot (no cart, `3M RAM MODE` off; `cold_boot.json`): after boot
  only stack and BSS accesses, none to the two ranges.
- **Screenshots do not separate the runs:** two identical control passes
  differ in 64 of 174 end-of-segment screenshots, the canary pass in 57 and
  59; screenshot timing is not repeatable here, so that check is
  uninformative (`watch_final_control*.json`).
- Breakpoint logs see the master SH-2 only; the canary covers writes by DMA
  and the slave SH-2; reads by DMA (as in the command list) need the static
  review.
- Only one Mednafen can run per home (the lock): passes run in sequence.

## Conclusion

Prediction met for two ranges: **1,024 bytes inside `CYBER.BIN`
(`0x06055424`-`0x06055824`) for code loaded at boot, and 5,628 bytes of
RAM (`0x060DF8A8`-`0x060E0EA4`)**. The biggest zero range is the command
list's tail and must not be used. About 31 KB of free RAM (option B of
`OPT-002`) does not exist among the proven ranges.

## Uncertainty and Alternatives

- One arcade route, ending checkpoints and one versus fight were run; other
  pilots' stages and boss fights were reviewed statically only.
- The slave SH-2's reads are covered by static review only.

## Reproduction

Run the procedure. Expect the committed JSON files (screenshot hashes vary).
