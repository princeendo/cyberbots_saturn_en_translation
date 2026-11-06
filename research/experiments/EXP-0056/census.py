"""EXP-0056: the name-art census's evidence, hashed (numbers and names only).

Run from the repository root after the runs in README.md:

    ./invenv.sh python research/experiments/EXP-0056/census.py \\
        --out research/experiments/EXP-0056/census.json

Collects, with each screenshot's SHA-256:

- Saturn pilot select: frames 0x14-0x1C of the name record ``0x06065192``
  shown from session state 3070 (``local/loc001/sel-name-FF/s0040.png``);
- Saturn VS screen: pilot frames 0x02-0x0A (record ``0x06087E98``) and
  mech frames 0x0C-0x1C (record ``0x06087A3E``) from session state 6805
  (``local/loc001/vs-pilot-FF``, ``vs-mech-FF``);
- arcade (``cybotsu``, ``cybotsj``): the select-cursor snapshots and each
  run's first VS-screen snapshot (``local/loc001/mame/vs_us.json``,
  ``vs_jp.json``).

The readings (what each picture says) are the agent's, entered here from
the screenshots. ``latin_text_name`` is the game's own Latin spelling: the
mech list in `CYBER.BIN` (``BLODIA`` ... ``ZERO-GOUKI``, in this order,
static search), which the versus RESULT tally also shows (`EXP-0031`).
The VS mech table's seventeenth entry points at frame 0x1C, which draws a
portrait, not a name; that it is ZERO-GOUKI (the list's seventeenth name)
is a HYPOTHESIS from list order. The other sixteen are matched by reading
the art.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SELECT_NAMES = {
    0x14: ("Jin", "ジン"),
    0x15: ("Santana", "サンタナ"),
    0x16: ("Mary", "マリー"),
    0x17: ("Arieta", "アリエータ"),
    0x18: ("Gawaine", "ガウェイン"),
    0x19: ("Bao and Mao", "バオ&マオ"),
    0x1A: ("Devilotte", "デビロット姫"),
    0x1B: ("Chiyomaru", "千代丸"),
    0x1C: ("Shade", "シェイド"),
}
VS_MECHS = {
    0x0C: ("BLODIA", "ブロディア", "BX-02"),
    0x0D: ("SWORDSMAN", "B・ソードマン", "BX-04S"),
    0x0E: ("RIOT", "B・ライアット", "BX-07S"),
    0x0F: ("REPTOS", "レプトス", "RF-004"),
    0x10: ("LIGHTNING", "R・ライトニング", "RF-009"),
    0x11: ("JACKAL", "R・ジャッカル", "RF-027"),
    0x12: ("FORDY", "フォーディー", "F7100"),
    0x13: ("TALANTURA", "F・タランテラ", "F7202"),
    0x14: ("KILLER BEE", "F・キラービー", "F7900J"),
    0x15: ("GULDIN", "ガルディン", "GP-N1"),
    0x16: ("VICE", "G・ヴァイス", "GP-V4"),
    0x17: ("CYCLONE", "G・サイクロン", "GP-02"),
    0x18: ("GAITS", "ゲイツ", "P-10033"),
    0x19: ("HELION", "ヘリオン", "UVA-02"),
    0x1A: ("WARLOCK", "ワーロック", "X-0"),
    0x1B: ("SUPER-8", "スーパー8", "S-008"),
    0x1C: ("ZERO-GOUKI (HYPOTHESIS: list order)", "(a portrait, not a name)", None),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    base = Path("local/loc001")
    report: dict[str, Any] = {
        "saturn_select": [
            {
                "frame": f"0x{f:02X}",
                "pilot": name,
                "art": art,
                "shot_sha256": sha(base / f"sel-name-{f:02x}" / "s0040.png"),
            }
            for f, (name, art) in SELECT_NAMES.items()
        ],
        "saturn_vs_pilots": [
            {
                "frame": f"0x{f - 0x12:02X}",
                "pilot": name,
                "art": art,
                "shot_sha256": sha(base / f"vs-pilot-{f - 0x12:02x}" / "s0020.png"),
            }
            for f, (name, art) in SELECT_NAMES.items()
        ],
        "saturn_vs_mechs": [
            {
                "frame": f"0x{f:02X}",
                "latin_text_name": latin,
                "art": art,
                "model_code": code,
                "shot_sha256": sha(base / f"vs-mech-{f:02x}" / "s0020.png"),
            }
            for f, (latin, art, code) in VS_MECHS.items()
        ],
        "arcade": {},
    }
    for game, index in (("cybotsu", "vs_us.json"), ("cybotsj", "vs_jp.json")):
        vs = json.loads((base / "mame" / index).read_text())
        report["arcade"][game] = {
            "select": {
                p.name: sha(p)
                for p in sorted(
                    (base / "mame" / game / "select" / "snap").glob("*.png")
                )
            },
            "vs": {
                run: {
                    "snap": snap,
                    "sha256": sha(base / "mame" / game / run / "snap" / snap),
                }
                for run, snap in sorted(vs.items())
                if snap
            },
        }
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(
        len(report["saturn_select"]),
        len(report["saturn_vs_pilots"]),
        len(report["saturn_vs_mechs"]),
        {g: len(v["vs"]) for g, v in report["arcade"].items()},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
