# EXP-0043: The QSound Notice's Japanese Line, Erased on Disc

Task: END-010
Status: DONE
Confidence: CONFIRMED

## Observation

- The QSound notice is `QSD.PIX`, a 512 × 256 bitmap of 256-colour pixels
  loaded raw at VDP2 VRAM `0x20000`; screen (x, y) is bitmap (x − 16,
  y + 8) (D-035).
- `EXP-0038` zeroed rows 180-189 at x 84-300 in VRAM, and the Japanese line
  disappeared. But index 0 is transparent in this bitmap: the zoomed shot
  shows the layer behind through the gap. It also cut the logo's 5-pixel
  edge (x 84-88) and left the line's descender in row 190.
- In the file, the notice's background is index 255. Rows 191-194, x 84-300,
  are all 255. Rows 180-190, x 89-300, hold nothing but the Japanese line
  (drawn as text from the file, agent-reviewed).
- The user's decision for this line (`END-005`): "Erase the line
  (Recommended)".

## Hypothesis

Setting rows 180-190, x 89-300 of `QSD.PIX` to index 255 on disc removes
only the Japanese line, with no gap and no other change on screen.

## Controlled Change

`QSD.PIX` with `tools.text.ending.erase_qsound_line` applied: 798 bytes
changed, all in rows 180-190, x 99-285, all now 255. The rest of the image
is untouched (`build/end010/qsd`).

## Prediction

From a state before `QSD.PIX` loads, the notice differs from the control
only at screen x 115-301, y 172-182 (the line). The English lines and the
logo are unchanged, and the background where the line was matches its
surroundings.

## Inputs and Provenance

| Input | SHA-256 |
| --- | --- |
| `QSD.PIX` (untouched) | `ff061ebd…d488` |
| Erased `QSD.PIX` | `e37dc053…a42f` |
| State `local/end002/control/s12488.mcs` (`EXP-0038`, before `QSD.PIX` loads at 12904) | as `EXP-0038` |

## Tools and Environment

[`qsound.py`](qsound.py) (the change, its checks and the test image; →
[`qsound.json`](qsound.json), numbers only) and `EXP-0038/vram_probe.py`
(screenshots after N frames). Agent Mednafen 1.32.1, silent home, no key,
no cold boot.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0043/qsound.py \
  --image build/end010/qsd --out research/experiments/EXP-0043/qsound.json
V=research/experiments/EXP-0038/vram_probe.py; S=local/end002/control/s12488.mcs
./invenv.sh python $V $S local/end010/qsd-control --shots 640,700,800
./invenv.sh python $V $S local/end010/qsd-test --shots 640,700,800 \
  --cue "build/end010/qsd/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
```

2026-11-05, 15:05 local.

## Actual Result

- **Static** (`qsound.json`): 798 bytes changed, rows 180-190, x 99-285,
  all inside the region; no non-background pixel is left in it. Kept nearby:
  - the logo's edge at x 84-88 (125 pixels);
  - the English line above (618 pixels in rows 170-178), and its comma's
    tail in row 179 (1 pixel);
  - 4 pixels in rows 191-199.
- **On screen, +640 frames** (the notice):
  - test `9d0ec074…` against control `d46c3202…`, which is `EXP-0038`'s
    QSound control shot;
  - 798 pixels differ, all in x 115-301, y 172-182;
  - agent-reviewed: the Japanese line is gone, the area is the same black
    as around it, and the five English lines and the logo are intact.
- **+700 and +800 frames:** both runs are identical, after the notice
  (`36583d94…`, `2dd70d50…`).

## Conclusion

Prediction met. Writing index 255 over rows 180-190, x 89-300 of `QSD.PIX`
removes the Japanese trademark line and nothing else. `END-010`'s build
uses this function.

## Uncertainty and Alternatives

None for this surface. The English lines already state the trademark.

## Reproduction

Run the procedure. Expect `qsound.json` byte for byte, and the shot hashes
above.
