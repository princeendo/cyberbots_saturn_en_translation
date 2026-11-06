"""EXP-0062: log every read and write of a RAM range across the session.

Run from the repository root (no key; the silent home):

    ./invenv.sh python research/experiments/EXP-0062/watch.py OUT RANGE \\
        [--states local/ref005/session/states] [--cue CUE] [--out-json PATH]

RANGE is Mednafen breakpoint syntax (``060D9295-060D929F``). One launch:
each session state is loaded in turn and run to the next state's frame
(the last for 300 frames), with read and write breakpoints on RANGE in log
mode. Writes the hit PCs and counts per state to OUT/hits.json (and
``--out-json``).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", type=Path)
    parser.add_argument("range")
    parser.add_argument(
        "--states", type=Path, default=Path("local/ref005/session/states")
    )
    parser.add_argument("--cue", type=Path, default=session.UNTOUCHED)
    parser.add_argument("--out-json", type=Path)
    args = parser.parse_args()
    states = sorted(args.states.glob("f*.mcs"))
    frames = [int(p.stem[1:]) for p in states]
    session.launch(states[0], args.out, args.cue)
    agent = session.agent_of(args.out)
    report: dict[str, object] = {"range": args.range, "states": len(states), "hits": {}}
    total = Counter()
    try:
        for k, state in enumerate(states):
            run = frames[k + 1] - frames[k] if k + 1 < len(states) else 300
            agent.run()
            agent.loadstate(state.resolve())
            agent.pause()
            agent.bpmode("log")
            agent.breakpoints("read", [args.range])
            agent.breakpoints("write", [args.range])
            agent.clear_events()
            agent.frames(run)
            agent.wait_halted(120.0)
            pcs = Counter()
            for e in agent.events():
                f = dict(FIELD.findall(e))
                if "PC" in f:
                    pcs[f["PC"]] += 1
            agent.breakpoints("read", [])
            agent.breakpoints("write", [])
            if pcs:
                report["hits"][state.stem] = dict(pcs)  # type: ignore[index]
                total.update(pcs)
            print(state.stem, run, dict(pcs), flush=True)
    finally:
        session.main.__globals__["os"].kill(
            json.loads((args.out / "run.json").read_text())["pid"], 15
        )
    report["total"] = dict(total)
    text = json.dumps(report, indent=1)
    (args.out / "hits.json").write_text(text + "\n")
    if args.out_json:
        args.out_json.write_text(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
