"""EXP-0058: ``EXP-0019/drive.py launch`` with the run recorded (video and sound).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0058/launch_rec.py CUE OUT

The same scratch home and pad keys as ``drive.py launch`` (``local/
mednafen_route``), plus ``-qtrecord OUT/run.mov``. Afterwards drive the run
with ``drive.py key/shot/stop OUT ...`` as usual; the recording closes when
``drive.py stop`` ends Mednafen.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

_spec = importlib.util.spec_from_file_location(
    "exp0019_drive", Path("research/experiments/EXP-0019/drive.py")
)
assert _spec and _spec.loader
drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drive)


def main() -> int:
    cue, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=False)
    home = drive.make_home()
    env = {
        **os.environ,
        "MEDNAFEN_HOME": str(home.resolve()),
        "MEDNAFEN_AGENT_DIR": str((out / "agent").resolve()),
    }
    with (out / "mednafen.log").open("wb") as stream:
        process = subprocess.Popen(
            [str(drive.BINARY), "-qtrecord", str(out / "run.mov"), str(cue)],
            env=env,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    (out / "run.json").write_text(json.dumps({"pid": process.pid, "cue": str(cue)}))
    drive.log(out, {"action": "launch", "pid": process.pid, "frame": drive.frame(out)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
