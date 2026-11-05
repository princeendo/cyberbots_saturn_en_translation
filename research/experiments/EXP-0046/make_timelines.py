"""EXP-0046: MAME timelines that play an arcade ending for lists 1-5.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/make_timelines.py OUTDIR

For each set (``u``, ``j``) and list 1-5, writes ``OUTDIR/route-SET-LIST.txt``
from ``EXP-0040/timelines/route-SET.txt`` (Jin's route: coin, start, two
buttons; the round-end breakpoint ``0xDAE4`` that ends the game in a win).
Two changes: every output path points to ``local/end020/mame/route-SET-LIST/``,
and one more breakpoint line sets the ending number ``0xFFEB2C`` (D-037) to
the list right after the game copies the winner's pilot byte into it
(``move.b ($370,A6),($6b2c,A5)`` at ``0xDBB6`` and ``0xDC0C`` in both sets;
the breakpoints are on the next instructions, ``0xDBBC`` and ``0xDC12``).
"""

from __future__ import annotations

import sys
from pathlib import Path

SOURCE = Path("research/experiments/EXP-0040/timelines")
AFTER_COPY = ("dbbc", "dc12")


def main(out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    for s in ("u", "j"):
        base = (SOURCE / f"route-{s}.txt").read_text().splitlines()
        for n in range(1, 6):
            name = f"route-{s}-{n}"
            lines = []
            for line in base:
                line = line.replace(
                    f"local/end004/mame/route-{s}/", f"local/end020/mame/{name}/"
                )
                if line.startswith("#"):
                    line = (
                        f"# END-020 (EXP-0046): {s}, list {n}'s ending; from EXP-0040's"
                        f" route-{s}.txt with the ending number set to {n}. " + line[2:]
                    )
                lines.append(line)
                if line.startswith("2 debug bpset dae4"):
                    for at in AFTER_COPY:
                        lines.append(f"2 debug bpset {at},1,{{b@ffeb2c={n};g}}")
            (out / f"{name}.txt").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
