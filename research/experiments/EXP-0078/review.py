"""EXP-0078: the review page for one Saturn-only pilot's drafts (SPECIAL-012).

Run from the repository root (offline):

    ./invenv.sh python research/experiments/EXP-0078/review.py DRAFTS OUT.html

DRAFTS is the pilot's local drafts file (``boxes`` with section, scene or
stage, box, speaker, gloss, english, note; ``names``). The page shows the
new names, then every box in play order with its speaker, the English as
the game wraps it (``tools.text.dialogue.wrap``; captions as one row), the
literal gloss and any note; a box with ``official_slot`` is shown as kept
official English. It holds glosses of the game's Japanese, so it
is written under ``local/`` only and never committed (`SPECIAL-012`).
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.text import dialogue

TITLES = {
    "story": "Story",
    "win_quotes": "Versus win quotes",
    "captions": "VS-screen chapter captions",
    "ending": "Ending",
}
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1f;--muted:#6b6b70;--line:#e3e1dc;--box:#20244a;
--boxfg:#f4f4ff;--note:#8a5a00;--card:#fff}
@media (prefers-color-scheme: dark){:root{--bg:#141416;--fg:#ececf0;--muted:#a0a0a8;
--line:#2c2c31;--box:#2b3170;--boxfg:#f4f4ff;--note:#e3b25a;--card:#1c1c20}}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;
margin:0;padding:24px 16px;max-width:980px;margin-inline:auto}
h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:32px 0 8px}
h3{font-size:15px;color:var(--muted);margin:20px 0 6px;font-weight:600}
p.lead{color:var(--muted);margin:0 0 16px}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--line);
padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}
.row{display:grid;grid-template-columns:64px 130px 1fr 1fr;gap:10px;padding:8px 0;
border-bottom:1px solid var(--line)}
.num{color:var(--muted);font-variant-numeric:tabular-nums}.who{font-weight:600}
.en{background:var(--box);color:var(--boxfg);border-radius:6px;padding:6px 10px;
font-family:ui-monospace,Menlo,monospace;font-size:13px;white-space:pre}
.gl{color:var(--muted)}.note{color:var(--note);font-size:13px;margin-top:4px}
@media (max-width:700px){.row{grid-template-columns:1fr}.en{white-space:pre-wrap}}
"""


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("drafts", type=Path)
    p.add_argument("out", type=Path)
    a = p.parse_args()
    d = json.loads(a.drafts.read_text())
    e = html.escape
    out = [
        "<!doctype html><html lang=en><head><meta charset=utf-8>",
        '<meta name=viewport content="width=device-width,initial-scale=1">',
        f"<title>{e(d['pilot'])} Review</title><style>{CSS}</style></head><body>",
        f"<h1>{e(d['pilot'])}: draft English for review</h1>",
        f"<p class=lead>List {d['list']}, {len(d['boxes'])} boxes. Each row: box "
        "number, speaker (from context), the English as the game wraps it in the "
        "box, and a literal gloss of the Japanese. Notes mark adaptations.</p>",
        "<h2>New names and terms</h2><table><tr><th>English</th><th>Japanese "
        "source</th><th>Why</th></tr>",
    ]
    for n in d["names"]:
        out.append(
            f"<tr><td><b>{e(n['name'])}</b></td><td>{e(n['source'])}</td>"
            f"<td>{e(n['rule'])}</td></tr>"
        )
    out.append("</table>")
    for section, title in TITLES.items():
        boxes = [b for b in d["boxes"] if b["section"] == section]
        out.append(f"<h2>{title} ({len(boxes)})</h2>")
        group = None
        for b in boxes:
            key = b.get("scene", b.get("stage"))
            if section == "story" and key != group:
                out.append(f"<h3>Scene {key}</h3>")
                group = key
            if b.get("official_slot") is not None:
                rows = [f"(official arcade English, slot {b['official_slot']})"]
            elif section == "captions":
                rows = [b["english"]]
            else:
                rows = dialogue.wrap(b["english"])
            who = b.get("speaker") or (
                f"Stage {b['stage'] + 1}" if "stage" in b else ""
            )
            note = f"<div class=note>{e(b['note'])}</div>" if b.get("note") else ""
            out.append(
                f"<div class=row><div class=num>{b['box']}</div>"
                f"<div class=who>{e(who)}</div>"
                f"<div><div class=en>{e(chr(10).join(rows))}</div>{note}</div>"
                f"<div class=gl>{e(b['gloss'])}</div></div>"
            )
    out.append("</body></html>")
    a.out.write_text("\n".join(out))
    print(a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
