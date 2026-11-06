"""EXP-0061: summarize the two cold boots (``local/loc006/arcade``, ``versus``).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0061/summarize.py \\
        [--out research/experiments/EXP-0061/play.json]

Reads each boot's ``log.jsonl`` (keys, with the frame) and every
``look.py`` report; counts the presses and, per boot, the looks that found
built name art, katakana name art, or none. The names each screen shows
were read by the agent from the screenshots and are listed in
``SEEN`` (this file), keyed by look name.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path("local/loc006")
SEEN = {
    "arcade": {
        "sel-jin": "pilot select: Jin | Arieta",
        "sel-r1": "pilot select: Mary | Arieta",
        "sel-r2": "pilot select: Santana | Arieta",
        "machine5": "MACHINE SELECT (Latin labels, no name art)",
        "vs2-6": "SET UP: Santana | Arieta",
        "vs3-9": "VS: REPTOS RF-004, Santana | BLODIA BX-02, Arieta",
    },
    "versus": {
        "sel0": "pilot select: Jin | Arieta",
        "p1-r4": "pilot select: Gawaine | Arieta",
        "p2-l1": "pilot select: Gawaine | Bao&Mao",
        "mach3": "MACHINE SELECT (Latin labels, no name art)",
        "su-8": "SET UP: Gawaine | Bao&Mao",
        "vs-9": "VS: F·KILLER BEE F7900J, Gawaine | G·CYCLONE GP-02, Bao&Mao",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report: dict[str, Any] = {}
    ok = True
    for boot in ("arcade", "versus"):
        folder = ROOT / boot
        log = [json.loads(line) for line in (folder / "log.jsonl").open()]
        keys = [r for r in log if r["action"] == "key"]
        looks = {}
        for path in sorted(folder.glob("*.json")):
            if path.name in ("run.json",):
                continue
            look = json.loads(path.read_text())
            if "counts" in look:
                looks[look["name"]] = look
        katakana = [
            n
            for n, lk in looks.items()
            if lk["counts"]["katakana-vs"] or lk["counts"]["katakana-select"]
        ]
        built = [
            n
            for n, lk in looks.items()
            if lk["counts"]["built-vs"] or lk["counts"]["built-select"]
        ]
        seen = {
            name: {
                "frame": looks[name]["frame"],
                "screenshot_sha256": looks[name]["screenshot_sha256"],
                "built_parts": looks[name]["counts"]["built-vs"]
                + looks[name]["counts"]["built-select"],
                "read": text,
            }
            for name, text in SEEN[boot].items()
        }
        report[boot] = {
            "launch_frame": log[0]["frame"],
            "presses": len(keys),
            "buttons": [k["button"] for k in keys],
            "looks": len(looks),
            "looks_with_built_art": len(built),
            "looks_with_katakana_art": katakana,
            "screens": seen,
        }
        ok &= not katakana
    report["ok"] = ok
    text = json.dumps(report, indent=1, ensure_ascii=False)
    print(text)
    if args.out:
        args.out.write_text(text + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
