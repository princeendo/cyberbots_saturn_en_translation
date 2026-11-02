# EXP-0017: M1, the Target Box Changed in Live RAM

Task: RE-001
Status: DONE
Confidence: CONFIRMED

## Observation

The M1 box (Jin's first pre-fight box, Saturn lines 4-5) is drawn from
Shift-JIS text held once in WRAM-H at `0x0606F09C` (line 4) and `0x0606F0B8`
(line 5), inside the resident `STG0AS.BIN`, as one VDP1 sprite per
character, with glyphs rendered as the box types (D-015). `GATE-M0` passed
("GO for M1", 2026-11-02).

## Hypothesis

Replacing line 4's bytes in WRAM-H before the box types changes what the box
shows, and nothing else in the box.

## Controlled Change

One write of 26 bytes to WRAM-H `0x0606F09C` at checkpoint A, while paused,
before the box types. Control: the same run without the write.

## Prediction

With the write, the completed box's first line reads あいうえおかきくけこさしす
and its second line is unchanged; the control shows the original box.

## Inputs and Provenance

- Checkpoint A `local/checkpoints/m1/a-box-open.mcs` (`236c610e…ddfc`,
  `EXP-0015`).
- Original bytes at `0x0606F09C` (26): `8e9f82cd83548343837b815b834f95ba82a98145814581458142`
  (Saturn line 4, census hash `4f587e16e11d3a6c`).
- Written bytes (26): `82a082a282a482a682a882a982ab82ad82af82b182b382b582b7`
  (Shift-JIS of the 13 hiragana あ い う え お か き く け こ さ し す).
- Untouched image (Redump 58190); patched binary `2fc3d547…eaaf`.

## Tools and Environment

[`ram_write.py`](ram_write.py) (agent: load, pause, bus read and write, run,
6 × 50 frames with screenshots); dialogue-strip crop `352x72+0+168` hashed
as raw RGB.

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0017/ram_write.py local/re001/write
./invenv.sh python research/experiments/EXP-0017/ram_write.py local/re001/control --control
```

17:03:52-17:04:11 local, the user present.

## Actual Result

- **Write run:** read-back after the write equals the written bytes; at the
  end of the run (frame 491 of the launch) the 26 bytes still hold the test
  string.
- **Control run:** the 26 bytes are the original before and after.
- **Screens** (agent-reviewed, step 5, about 255 frames after the load):
  the write run's box shows `あいうえおかきくけこさしす` on its first line and
  the original second line (Saturn line 5); the control shows the original
  two lines (`write/step05.png` SHA-256 `2fc819ad…`, `control/step05.png`
  `1fb69fb8…`, in the ignored `local/re001/`). Dialogue-strip hashes per
  step:

| Run | Steps 1-6 |
| --- | --- |
| control | f5e722 22c160 d0e914 ead786 ead786 3a956a |
| write | 1a54b4 59c0c0 74c408 1d501a 1d501a 3a956a |

  The completed control box is `ead786`, as in every earlier replay
  (D-014); the completed write box is `1d501a`; at step 6 both show the same
  next box (Shade's reply, `3a956a`).
- Source manifests identical before and after; both home configs unchanged.
- Every glyph of the test string was drawn: the font has these 13 hiragana.

## Conclusion

**CONFIRMED (M1):** one ordinary pilot's story dialogue box was visibly
modified in live Saturn RAM by writing Shift-JIS to WRAM-H `0x0606F09C`
before the box typed; the control shows the original; the change did not
spill into the next line or the next box.

## Uncertainty and Alternatives

- Only a same-length, all-full-width test string was used. Longer text, half-
  width characters, and Latin letters are later questions (`FONT-002`,
  `LAYOUT-001`).
- The resident copy is `STG0AS.BIN`'s; a disc change for M2 must find which
  file is loaded for this scene (`DISC-001`).

## Reproduction

Run the procedure; expect `1d501a` (write) and `ead786` (control) for the
completed box. Evidence stays in the ignored `local/re001/`.
