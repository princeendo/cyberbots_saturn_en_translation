"""EXP-0064: prove RAM ranges unused: CPU logs, canaries, and the screen.

Run from the repository root (no key; the silent home):

    ./invenv.sh python research/experiments/EXP-0064/watch2.py OUT \\
        --ranges FILE [--control] [--states DIR] [--extra STATE:FRAMES ...] \\
        [--only NAME,NAME]

FILE is JSON: a list of [start, end) hex strings. One Mednafen process (the
patched build, D-007) on the untouched image. For each state (every state in
``--states``, default ``local/ref005/session/states``, each run to the next
state's frame, the last 300 frames; then each ``--extra`` state for its
FRAMES):

- unless ``--control``: every range is filled with the canary ``0xA5`` and
  log-mode read and write breakpoints are set on all ranges;
- the state runs; then the hit PCs (master SH-2 accesses), the number of
  bytes of each range that are no longer ``0xA5`` (any writer: CPU, DMA, the
  other SH-2) and the SHA-256 of a screenshot are recorded.

A control run (``--control``: no canary, no breakpoints) gives the
screenshots to compare: a range that is read by anything that matters would
change what is drawn. Writes ``OUT/watch.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "session", Path("research/experiments/EXP-0062/session.py")
)
assert _spec and _spec.loader
session = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(session)
FIELD = re.compile(r"(\w+)=([0-9A-Fa-f]+)")
_aspec = importlib.util.spec_from_file_location(
    "attribute", Path("research/experiments/EXP-0064/attribute.py")
)
assert _aspec and _aspec.loader
attribute = importlib.util.module_from_spec(_aspec)
_aspec.loader.exec_module(attribute)
CANARY = 0xA5


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("--ranges", type=Path, required=True)
    parser.add_argument("--control", action="store_true")
    parser.add_argument(
        "--states", type=Path, default=Path("local/ref005/session/states")
    )
    parser.add_argument("--extra", action="append", default=[])
    parser.add_argument("--only", help="comma-separated state file names to run")
    args = parser.parse_args()
    ranges = [(int(a, 16), int(b, 16)) for a, b in json.loads(args.ranges.read_text())]
    states = sorted(args.states.glob("*.mcs"))
    frames = [int(p.stem[1:]) for p in states]
    plan = [
        (s, frames[k + 1] - frames[k] if k + 1 < len(states) else 300)
        for k, s in enumerate(states)
    ]
    for item in args.extra:
        path, count = item.rsplit(":", 1)
        plan.append((Path(path), int(count)))
    if args.only:
        keep = set(args.only.split(","))
        plan = [(s, n) for s, n in plan if s.name in keep]
    session.launch(plan[0][0], args.out, session.UNTOUCHED)
    agent = session.agent_of(args.out)
    spec = [f"{a:08X}-{b - 1:08X}" for a, b in ranges]
    rows = []
    total: Counter[str] = Counter()
    try:
        for state, run in plan:
            agent.run()
            agent.loadstate(state.resolve())
            agent.pause()
            if not args.control:
                for a, b in ranges:
                    agent.bus_write(a, bytes([CANARY]) * (b - a))
                agent.bpmode("log")
                agent.breakpoints("read", spec)
                agent.breakpoints("write", spec)
                agent.clear_events()
            agent.frames(run)
            agent.wait_halted(max(300.0, run / 10))
            pcs: Counter[str] = Counter()
            changed = []
            by_range: dict[str, Counter[str]] = {}
            ops: dict[str, int | None] = {}
            if not args.control:
                for e in agent.events():
                    f = dict(FIELD.findall(e))
                    if "PC" not in f:
                        continue
                    pc = f["PC"]
                    pcs[pc] += 1
                    if pc not in ops:
                        address = int(pc, 16)
                        try:
                            ops[pc] = int.from_bytes(agent.bus_read(address, 2), "big")
                        except Exception:
                            ops[pc] = None
                    op = ops[pc]
                    regs = {k: int(v, 16) for k, v in f.items() if k[0] in "RG"}
                    hit = attribute.access(op, regs) if op is not None else None
                    k = attribute.in_ranges(hit[0], hit[1], ranges) if hit else None
                    key = str(k) if k is not None else "?"
                    tag = f"{pc}:{hit[2]}" if hit else pc
                    by_range.setdefault(key, Counter())[tag] += 1
                agent.breakpoints("read", [])
                agent.breakpoints("write", [])
                for a, b in ranges:
                    data = agent.bus_read(a, b - a)
                    changed.append(sum(1 for x in data if x != CANARY))
            shot = (args.out / "shot.png").resolve()
            agent.screenshot(shot)
            digest = hashlib.sha256(shot.read_bytes()).hexdigest()
            shot.unlink()
            rows.append(
                {
                    "state": str(state),
                    "frames": run,
                    "pcs": dict(pcs),
                    "changed": changed,
                    "by_range": {k: dict(v) for k, v in by_range.items()},
                    "screen": digest,
                }
            )
            total.update(pcs)
            partial = {"ranges": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in ranges]}
            partial["rows"] = rows  # type: ignore[assignment]
            (args.out / "partial.json").write_text(json.dumps(partial) + "\n")
            print(
                state.name,
                run,
                {k: sum(v.values()) for k, v in by_range.items()},
                {i: c for i, c in enumerate(changed) if c},
                flush=True,
            )
    finally:
        os.kill(json.loads((args.out / "run.json").read_text())["pid"], 15)
    report = {
        "control": args.control,
        "ranges": [[f"0x{a:08X}", f"0x{b:08X}"] for a, b in ranges],
        "rows": rows,
        "total_pcs": dict(total),
        "changed_total": [
            sum(r["changed"][i] for r in rows if r["changed"])
            for i in range(len(ranges))
        ]
        if not args.control
        else [],
    }
    (args.out / "watch.json").write_text(json.dumps(report, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
