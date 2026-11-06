# EXP-0054: The English Boot Warnings, Built and Seen

Task: BOOT-004
Status: DONE
Confidence: CONFIRMED

## Observation

- D-049: each warning is its own `WARNINGn.PIX`, 352 × 224 visible pixels in
  16 program colours; hidden bytes are never shown.
- `BOOT-003`: the approved English and style,
  `data/translations/boot_warnings.json`.

## Hypothesis

A generator that redraws only each file's visible pixels, run inside the M8
build, gives an image whose only change from M8 is the five pictures, and
each warning shows its English exactly as generated.

## Controlled Change

The M8 build command plus `--boot-warnings data/translations/
boot_warnings.json` (one option, one data file), from the untouched source.

## Prediction

- Two builds identical; every M8 output unchanged; every sector that differs
  from M8 inside the five pictures; all sectors valid.
- Under each `EXP-0051` condition the built image shows its English picture,
  pixel for pixel; a normal-save boot is unchanged.

## Inputs and Provenance

| Input | SHA-256 (first 16) | Notes |
| --- | --- | --- |
| Untouched source | `references/saturn_jp/README.md` | `local/disc_images/cyberbots_saturn_jp_2m/` |
| `data/translations/boot_warnings.json` | see `data/regression/boot004_boot_warnings.json` | approved 2026-11-06 |
| `arcade_font.json` | ignored, `local/layout001/font/` | the story's arcade letters |
| M8 image | Track 01 `abb115e40ee0880d` | `build/end023/m8`, the comparison base |
| Fixtures | as `EXP-0051` | `local/boot001/fixtures/` |

## Tools and Environment

| Tool | Use |
| --- | --- |
| `tools/text/boot_warnings.py` (new, with `tests/unit/test_boot_warnings.py`) | Layout, pictures, format checks, change records; reproduces `EXP-0053`'s approved renders exactly |
| `tools/text/dialogue.py --boot-warnings` (new option) | Writes `OUT/WARNINGn.PIX` and `OUT/boot_changes.json` and adds the five files to the image |
| [`check_build.py`](check_build.py) | → [`build.json`](build.json) |
| `EXP-0051/boot_case.py --cue` | The six cold boots |
| [`check_screens.py`](check_screens.py) | → [`screens.json`](screens.json) |

## Procedure

```bash
B="./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent \
  --rank staying --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json \
  --driver local/mame_src/cps2.cpp --rompath local/arcade --endings data/text/m8_endings.json \
  --boot-warnings data/translations/boot_warnings.json"
$B --out build/boot004/a --ending-record-dir local/boot004/rec-a
$B --out build/boot004/b --ending-record-dir local/boot004/rec-b
./invenv.sh python research/experiments/EXP-0054/check_build.py build/boot004/a build/boot004/b \
  --out research/experiments/EXP-0054/build.json
F=local/boot001/fixtures; P=research/experiments/EXP-0051/boot_case.py; O=local/boot004/screens
CUE="build/boot004/a/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python $P $O/control --cue "$CUE" --bkr $F/save.bkr --frames 1800
./invenv.sh python $P $O/damaged --cue "$CUE" --bkr $F/damaged.bkr --frames 1800
./invenv.sh python $P $O/zero --cue "$CUE" --bkr $F/zero.bkr --frames 1800
./invenv.sh python $P $O/cart-zero --cue "$CUE" --bkr $F/save.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python $P $O/both-zero --cue "$CUE" --bkr $F/zero.bkr --bcr $F/cart_zero.bcr --cart backup --frames 1800
./invenv.sh python $P $O/free4 --cue "$CUE" --bkr $F/free4.bkr --frames 1800
./invenv.sh python research/experiments/EXP-0054/check_screens.py --out research/experiments/EXP-0054/screens.json
```

2026-11-06, 10:00-11:00 local. Six cold boots, asked first: "Yes, run all 6
(Recommended)". No key was pressed.

## Actual Result

### Build (`build.json`)

- Two builds: 18 outputs, Track 01 (`ef27ebc6…fe25`) and six ending records
  identical.
- M8 unchanged: the seven M8 replacements, `prediction.json`,
  `changes.json`, `ending_prediction.json`, `ending_changes.json` and
  `ending_timing.json` have `end023`'s hashes; the records equal the
  committed ones.
- Pictures (each passes the format check; every changed byte inside its
  recorded range, rows 0-223, columns 0-351):

  | File | SHA-256 (first 16) | Bytes changed |
  | --- | --- | --- |
  | `WARNING0.PIX` | `66c4d4b2c7868f34` | 11,907 |
  | `WARNING1.PIX` | `538c49028ccc6afa` | 13,611 |
  | `WARNING2.PIX` | `580ef4d18ef75843` | 16,189 |
  | `WARNING3.PIX` | `75c696a64207721f` | 17,267 |
  | `WARNING4.PIX` | `29da7ffce0e94a6c` | 19,544 |

  Original and new bytes: `build/boot004/a/boot_changes.json` (the original
  file's hash and the new one per range; the untouched files are in the
  listing).
- Image: 208 sectors differ from M8, all inside the five pictures; 43,793
  sectors, 0 invalid.

### Screens (`screens.json`)

| Case | Warning | Pixels differing from the built picture | VRAM = built file |
| --- | --- | --- | --- |
| damaged | 0 | 0 | yes |
| zero | 1 | 0 | yes |
| cart-zero | 2 | 0 | yes |
| both-zero | 3 | 0 | yes |
| free4 | 4 | 0 | yes |

- The agent read each screen against the approved text: every line, in
  order, with the yellow title, cyan "Memory Manager" and red "6".
- Normal-save boot: the same routine sequence as the untouched image and
  the same six screenshots. Its polls were labelled one frame later
  (`f00311` against `f00310`, ...), so the check pairs screenshots in poll
  order; a first version paired by label and found no pairs.

## Conclusion

Prediction met. The image is M8 plus five English boot warnings, nothing
else; each shows under its condition exactly as generated.

## Uncertainty and Alternatives

- Buttons on the warning screens are still SUPPORTED only (D-048);
  `BOOT-005`'s play check presses one.
- Both name variants (`LOC-001`, `OPT-001`) are not built yet; the option
  carries over to them.

## Reproduction

Run the procedure (six cold boots: ask the user first). Expect
`build.json` and `screens.json` as committed and
`data/regression/boot004_boot_warnings.json`.
