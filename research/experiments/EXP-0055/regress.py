"""EXP-0055: rebuild earlier regression references and compare their hashes.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0055/regress.py NAME [NAME ...] \\
        [--out research/experiments/EXP-0055/regress.json]

NAME is a file stem in ``data/regression`` (``re003_jin`` ...). Each
reference's ``rebuild`` command is run with its outputs redirected so that
nothing committed is overwritten: ``--out`` to ``build/regress/NAME``, and
``--record``/``--record-dir``/``--ending-record``/``--ending-record-dir`` to
``local/regress/NAME/``. Compared: every ``replacements`` file, Track 01 and
the cue (``output_sha256``), and the ``prediction``, ``changes`` and
``ending_*`` hashes, against the built files. Records are not compared:
several references' record hashes are of builds since superseded (each
reference says which). Numbers only; exits 1 on any mismatch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

FILES = {
    "prediction_sha256": "prediction.json",
    "changes_sha256": "changes.json",
    "ending_prediction_sha256": "ending_prediction.json",
    "ending_changes_sha256": "ending_changes.json",
    "ending_timing_sha256": "ending_timing.json",
}
RECORD_FLAGS = {"--record", "--record-dir", "--ending-record", "--ending-record-dir"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def redirected(command: str, name: str) -> list[str]:
    words = shlex.split(command)
    scratch = Path("local/regress") / name
    scratch.mkdir(parents=True, exist_ok=True)
    out: list[str] = []
    i = 0
    while i < len(words):
        w = words[i]
        if w == "--out":
            out += [w, f"build/regress/{name}"]
            i += 2
        elif w in RECORD_FLAGS:
            target = scratch / Path(words[i + 1]).name
            if w.endswith("-dir"):
                target = scratch / "records"
                target.mkdir(exist_ok=True)
            out += [w, str(target)]
            i += 2
        else:
            out.append(w)
            i += 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("names", nargs="+")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report: dict[str, Any] = {}
    ok = True
    for name in args.names:
        ref = json.loads((Path("data/regression") / f"{name}.json").read_text())
        command = redirected(ref["rebuild"], name)
        log = Path("local/regress") / name / "build.log"
        with log.open("w") as stream:
            code = subprocess.run(
                command, stdout=stream, stderr=subprocess.STDOUT
            ).returncode
        built = Path("build/regress") / name
        result: dict[str, bool] = {}
        for iso, digest in ref["replacements"].items():
            result[iso.split(";")[0]] = sha(built / iso.split(";")[0]) == digest
        for file, digest in ref["output_sha256"].items():
            result[file] = sha(built / "image" / file) == digest
        for key, file in FILES.items():
            if key in ref:
                result[file] = sha(built / file) == ref[key]
        report[name] = {
            "exit": code,
            "matches": result,
            "all": code == 0 and all(result.values()),
        }
        ok &= report[name]["all"]
        print(name, "exit", code, "all match" if report[name]["all"] else result)
    report["ok"] = ok
    if args.out:
        args.out.write_text(json.dumps(report, indent=1) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
