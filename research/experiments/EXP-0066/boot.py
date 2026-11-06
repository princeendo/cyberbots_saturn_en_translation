"""EXP-0066: cold boots of the names-switch build, with a kept save.

Run from the repository root (cold boots with presses: ask the user first):

    ./invenv.sh python research/experiments/EXP-0066/boot.py launch OUT CUE [--bkr FILE]
    ./invenv.sh python research/experiments/EXP-0066/boot.py keep OUT DESTDIR

``launch`` is ``EXP-0019/drive.py launch`` (the pad-key home
``local/mednafen_route``, the patched build, no state) with FILE copied in as
the internal backup memory first (FILE keeps its name: Mednafen names it by
the disc's identity, so a built image's file differs from the original's).
``keep`` copies that home's backup memory files (written by Mednafen when it
quits) into DESTDIR. Presses and screenshots use
``drive.py key`` and ``drive.py shot``; the stop is ``drive.py stop``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
_spec = importlib.util.spec_from_file_location(
    "drive", Path("research/experiments/EXP-0019/drive.py")
)
assert _spec and _spec.loader
drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drive)


def launch(out: Path, cue: Path, bkr: Path | None) -> None:
    out.mkdir(parents=True, exist_ok=False)
    home = drive.make_home()
    if bkr:
        (home / "sav").mkdir(exist_ok=True)
        shutil.copyfile(bkr, home / "sav" / bkr.name)
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as stream:
        process = subprocess.Popen(
            [str(drive.BINARY), str(cue)],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(json.dumps({"pid": process.pid, "cue": str(cue)}))
    drive.log(
        out,
        {
            "action": "launch",
            "pid": process.pid,
            "frame": drive.frame(out),
            "bkr": str(bkr),
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["launch", "keep"])
    parser.add_argument("out", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("--bkr", type=Path)
    a = parser.parse_args()
    if a.command == "launch":
        launch(a.out, a.target, a.bkr)
    else:
        a.target.mkdir(parents=True, exist_ok=True)
        for src in sorted((drive.HOME / "sav").glob("*.bkr")):
            shutil.copyfile(src, a.target / src.name)
            print(src, "->", a.target / src.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
