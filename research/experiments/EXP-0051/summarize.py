"""EXP-0051: summarize the boot cases (numbers only).

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0051/summarize.py \\
        local/boot001/CASE ... [--out research/experiments/EXP-0051/cases.json]

Per case: the fixtures' hashes and cart, the order of the check's routines
with their frames and R4, the warnings shown (R4 of ``0x06036DA8``), the
check's results at the last poll (``0x060DBA94`` internal status,
``0x060DBA98`` cart status, ``0x060DBA9C`` where a save was found,
``0x060DBA9D`` where one fits), the warning captures' hashes, and whether
the game changed its backup memory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases", nargs="+", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report: list[dict[str, Any]] = []
    for case in args.cases:
        route = json.loads((case / "route.json").read_text())
        last = json.loads((case / "poll.jsonl").read_text().splitlines()[-1])
        raw = bytes.fromhex(last["results"])
        entry = {
            "case": case.name,
            "cart": route["cart"],
            "bkr_sha256": route["bkr_sha256"],
            "bcr_sha256": route["bcr_sha256"],
            "first_frame": route["first_frame"],
            "sequence": [
                f"{h['frame']} {h['what']} R4={h['R4']}" for h in route["hits"]
            ],
            "warnings": [
                int(h["R4"], 16) for h in route["hits"] if h["PC"] == "0x06036DA8"
            ],
            "status_internal": int.from_bytes(raw[0:4], "big"),
            "status_cart": int.from_bytes(raw[4:8], "big"),
            "save_found_flags": raw[8],
            "room_flags": raw[9],
            "captures": [
                {
                    **c,
                    "png_sha256": hashlib.sha256(
                        (case / c["png"]).read_bytes()
                    ).hexdigest(),
                }
                for c in route["warning_captures"]
            ],
            "sav_after": route["sav_after"],
        }
        report.append(entry)
        print(
            entry["case"],
            entry["cart"],
            "warnings",
            entry["warnings"],
            "status",
            entry["status_internal"],
            entry["status_cart"],
            "flags",
            entry["save_found_flags"],
            entry["room_flags"],
        )
    if args.out:
        args.out.write_text(json.dumps({"cases": report}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
