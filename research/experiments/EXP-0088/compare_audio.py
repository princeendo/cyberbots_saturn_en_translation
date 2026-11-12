"""EXP-0088: compare the sound of two Mednafen recordings sample by sample.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0088/compare_audio.py A.mov B.mov

Each ``run.mov`` (``EXP-0067/attract.py``, ``-qtrecord``) is decoded to
16-bit stereo PCM with ffmpeg. Prints the first differing frame, then for
every third second: the left channel's RMS in each, the RMS of A - B, and
the lag (samples, -3000..3000, a 4,800-sample window from 10,000 samples
into the second, every 8th sample) at which B best matches A, with the RMS
left there. Standard library and ffmpeg only.
"""

from __future__ import annotations

import array
import math
import subprocess
import sys

RATE = 48000


def pcm(path: str) -> array.array[int]:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-vn", "-f", "s16le", "-ac", "2", "-"],
        check=True,
        capture_output=True,
    ).stdout
    samples = array.array("h")
    samples.frombytes(raw)
    if sys.byteorder == "big":
        samples.byteswap()
    return samples


def rms(values: list[int] | array.array[int]) -> float:
    return math.sqrt(sum(v * v for v in values) / max(1, len(values)))


def best_lag(a: array.array[int], b: array.array[int], start: int) -> tuple[int, float]:
    window = a[start + 10000 : start + 14800 : 8]
    best = (0, math.inf)
    for lag in range(-3000, 3001):
        other = b[start + 10000 + lag : start + 14800 + lag : 8]
        if len(other) < len(window):
            continue
        err = rms([p - q for p, q in zip(window, other, strict=True)])
        if err < best[1]:
            best = (lag, err)
    return best


def main() -> int:
    a, b = pcm(sys.argv[1]), pcm(sys.argv[2])
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), None)
    print(f"compared {n // 2} frames ({n / 2 / RATE:.1f} s)")
    print("first difference:", "none" if first is None else f"{first / 2 / RATE:.3f} s")
    left_a, left_b = a[0:n:2], b[0:n:2]
    print("sec  rms_a  rms_b  rms_a-b  lag  rms_at_lag")
    for s in range(0, len(left_a) // RATE, 3):
        x = left_a[s * RATE : (s + 1) * RATE]
        y = left_b[s * RATE : (s + 1) * RATE]
        d = rms([p - q for p, q in zip(x, y, strict=True)])
        lag, left = best_lag(left_a, left_b, s * RATE) if d else (0, 0.0)
        print(f"{s:3d} {rms(x):6.0f} {rms(y):6.0f} {d:8.0f} {lag:5d} {left:8.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
