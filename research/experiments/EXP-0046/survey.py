"""EXP-0046: what each roster ending shows, from forced runs; numbers only.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0046/survey.py \\
        [--out data/text/ending_surfaces.json]

Reads the forced Saturn runs (``EXP-0042/probe.py`` output: list 0 is
``local/end002/control``, lists 1-5 ``local/end020/listN``) and the headless
MAME runs (``local/end020/mame/route-SET-N``; list 0 is EXP-0040's
``local/end004/mame/route-SET``). For each list it records:

- the posts (``0x06066852``: frame, scene) and the files loaded from
  `END.BIN` to `QSD.PIX`, with frames;
- every box `END.BIN` opens, in order (record table ``0x060817B4``), with
  its open and close frames and the open time (``None`` when no close is
  logged before the next post or the end);
- against ``data/text/ending_posts.json`` (D-036): the boxes that open but no
  post's script lists, and the openings that repeat a box the post lists
  once;
- for every opening, the last screenshot taken while it was open (frame and
  SHA-256), the evidence the agent reviewed;
- the arcade slots read by the story reader (``0x011F6A`` in `cybotsu`,
  ``0x011E7A`` in `cybotsj`) after the ending number is written, in order.

The surface kinds come from the agent's review of every screenshot
(``EXP-0046/README.md``); they are labels, not text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

POSTS = Path("data/text/ending_posts.json")
TABLE = "0x060817B4"
RUNS = {
    0: Path("local/end002/control"),
    **{n: Path(f"local/end020/list{n}") for n in range(1, 6)},
}
ARCADE = {
    (s, n): Path(f"local/end020/mame/route-{s}-{n}")
    for s in ("u", "j")
    for n in range(1, 6)
}
ARCADE |= {(s, 0): Path(f"local/end004/mame/route-{s}") for s in ("u", "j")}
READER = {"u": ("011f6a", 0x0B33AA, "en"), "j": ("011e7a", 0x0A30F6, "jp")}
ENDING_WRITE_FRAME = 9259  # the round end's copy into 0xFFEB2C (EXP-0040)
PILOTS = [
    "Jin",
    "Santana",
    "Mary",
    "Arieta",
    "Gawaine",
    "Bao and Mao",
    "Saturn-only list 6",
    "Saturn-only list 7",
    "Saturn-only list 8",
]
OTHERS = {n: Path(f"local/end020/list{n}") for n in (6, 7, 8)}  # END-022

# The agent's review (EXP-0046/README.md): the kinds of surface each list's
# scenes show before the cast roll. Every Japanese text is one of these, all
# drawn as END.BIN boxes; after KEND.BIN loads, every list shows the same
# cast roll, credits, thank-you screen and QSound notice (D-035).
KINDS = {
    0: ["dialogue box with portrait", "narration", "caption with speaker name"],
    1: ["dialogue box with portrait", "caption with speaker name", "narration"],
    2: ["dialogue box with portrait", "caption with speaker name"],
    3: ["dialogue box with portrait", "caption with speaker name", "narration"],
    4: ["caption with speaker name", "caption without a name", "narration"],
    5: ["dialogue box with portrait", "caption with speaker name"],
}
SHARED = ["cast roll", "staff credits", "thank-you screen", "QSound notice"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def saturn(n: int, run: Path, posted: list[int]) -> dict[str, Any]:
    route = json.loads((run / "route.json").read_text())
    posts = [
        {"frame": p["frame"], "scene": p["scene"]}
        for p in route["posts"]
        if p["routine"] == "0x06066852"
    ]
    files = [
        {"file": str(x["file"]).split(";")[0], "frame": x["frame"]}
        for x in route["loads"]
        if x.get("file") and str(x["file"]).endswith("+0")
    ]
    first = next(f["frame"] for f in files if f["file"] == "END.BIN")
    last = next(
        (f["frame"] for f in files if f["file"] == "QSD.PIX"),
        max(f["frame"] for f in files),
    )
    files = [f for f in files if first <= f["frame"] <= last]
    shots = sorted((int(p.stem[1:]), p) for p in run.glob("f*.png"))
    events = [
        (b["frame"], int(b["word"], 16)) for b in route["boxes"] if b["table"] == TABLE
    ]
    post_frames = [p["frame"] for p in posts]
    openings: list[dict[str, Any]] = []
    for i, (frame, word) in enumerate(events):
        if word & 0x8000:
            continue
        close = next((f for f, w in events[i + 1 :] if w == (word | 0x8000)), None)
        next_post = next((f for f in post_frames if f > frame), None)
        if close is not None and next_post is not None and close > next_post:
            close = None
        stop = close or next_post or frame + 400
        inside = [(f, p) for f, p in shots if frame < f < stop]
        shot = inside[-1] if inside else None
        openings.append(
            {
                "box": word,
                "open": frame,
                "close": close,
                "open_time": close - frame if close is not None else None,
                "shot": (
                    {"frame": shot[0], "sha256": sha256(shot[1])} if shot else None
                ),
            }
        )
    opened = [o["box"] for o in openings]
    return {
        "list": n,
        "pilot": PILOTS[n],
        "run": str(run),
        "posts": posts,
        "files": files,
        "openings": openings,
        "boxes_not_in_posts": sorted(set(opened) - set(posted)),
        "posted_boxes_not_opened": sorted(set(posted) - set(opened)),
        "openings_count": len(opened),
        "posted_openings_count": len(posted),
        "surface_kinds": KINDS.get(n),
        "shared_after_dialogue": SHARED,
    }


def arcade(s: str, n: int, run: Path) -> dict[str, Any]:
    pc, base, table = READER[s]
    rows = [
        line.split()
        for line in (run / f"reads-{table}-ptr.txt").read_text().splitlines()
    ]
    slots: list[dict[str, int]] = []
    for frame, at, address in rows:
        if int(frame) > ENDING_WRITE_FRAME and at == pc:
            slot = (int(address, 16) - base) // 4
            if not slots or slots[-1]["slot"] != slot:
                slots.append({"frame": int(frame), "slot": slot})
    snaps = sorted(run.glob("snap/*.png"))
    return {
        "set": f"cybots{s}",
        "run": str(run),
        "slot_reads": slots,
        "distinct_slots": len({x["slot"] for x in slots}),
        "snapshots": len(snaps),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--others",
        action="store_true",
        help="lists 6-8 (Saturn-only, no arcade), END-022",
    )
    args = parser.parse_args()
    posts = json.loads(POSTS.read_text())
    lists = []
    runs = OTHERS if args.others else RUNS
    for n, run in runs.items():
        posted = [b["box"] for p in posts["lists"][n]["posts"] for b in p["boxes"]]
        entry = saturn(n, run, posted)
        if not args.others:
            entry["arcade"] = [arcade(s, n, ARCADE[(s, n)]) for s in ("u", "j")]
        lists.append(entry)
    result = {
        "sources": {
            "ending_posts": str(POSTS),
            "ending_posts_sha256": sha256(POSTS),
        },
        "lists": lists,
    }
    for e in lists:
        print(
            e["list"],
            e["pilot"],
            "openings",
            e["openings_count"],
            "posted",
            e["posted_openings_count"],
            "not in posts",
            e["boxes_not_in_posts"],
            "arcade slots",
            [a["distinct_slots"] for a in e.get("arcade", [])],
        )
    if args.out:
        args.out.write_text(json.dumps(result, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
