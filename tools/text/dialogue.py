"""Compile pilots' story boxes into pair glyphs; build the image (RE-003, RE-006).

Run from the repository root:

    ./invenv.sh python -m tools.text.dialogue \\
        --pairing data/translations/jin_pairing.json \\
        [--pairing data/translations/santana_pairing.json ...] \\
        --font local/layout001/font/arcade_font.json \\
        --driver local/mame_src/cps2.cpp --rompath local/arcade \\
        --out build/re003/jin [--record-dir data/translations] \\
        [--max-sacrifice 18] [--budget]

The policy and route are in `docs/localization_policy.md`: the official US arcade
English, as paired (D-022, D-027), unchanged, drawn as pair glyphs (D-024).

1. **Pilots.** Each ``--pairing`` file names its box list (``sources``), whose
   ``story_scenes`` are the scenes `STG0AS.BIN` posts for that pilot. Jin's list
   predates the field, so his are 21 and 0-15 (D-021). The pilot's other scenes
   are its ending, posted from `END.BIN`.
2. **English.** Read at build time from the `cybotsu` program, built from the ROM
   zips (`tools.reference.cybots_text`). The English table is at ``0x0B33AA``
   (D-009). The text is never written to the repository (`AGENTS.md` rule 21).
3. **Rows.** Each box's record is re-flowed into rows of at most 32 characters.
   The compiler fails if a box needs more than 3 rows (records hold 3 lines in
   place, D-023) or more than 60 glyph cells (D-020).
4. **Codes.** Each distinct pair (``tools.font.pairs``) across all the pilots,
   in order of first use (pilots in argument order), gets one table code:
   - first, codes no Japanese line uses (D-023), in table order;
   - then new codes in the table's last row, up to one before its end, because
     the lookup scans to a 0 word (``0x0606E9E8``);
   - last, by the user's decision (2026-11-02), the codes of the least-used
     Japanese characters (fewest lines, then table order), never one used by
     a line that stays. With ``--rank staying`` (CAP-001, 2026-11-04) the
     order is fewest lines that stay Japanese and are shown (a scene's box
     or a VS caption), then the same.

   With ``--indent`` (CAP-001) some rows start with a space, half a cell in,
   where that lets rows share pairs (``shift_rows``); the words are unchanged.

   At most ``--max-sacrifice`` codes (default 73, the number approved for
   Jin + Santana) are sacrificed. Beyond that the build stops and prints the budget, for
   the user's decision. ``--budget`` prints the budget and builds nothing.
5. **Text room** in `STG0AS.BIN`: the pilots' own lines and their dead ending
   lines, in line order. A box counts as a user of a line only if some
   pilot's scene shows it (box 63, a duplicate pointer, does not; EXP-0028).
   - **Kept:** a line some other box uses keeps its bytes.
   - **Dead:** an ending line is dead in this copy if every box using it is
     one of the pilots' ending-only boxes (in no other scene). Endings are
     shown from `END.BIN`'s own copy (EXP-0024).

   Rows are NUL-terminated and 4-byte aligned. A pair of spaces is ``0x8140``
   (no glyph).
6. **Records.** Each box's entries are rewritten as (row pointer, ``0xFFFF`` or
   0, 0).
7. **Image.** `KANJI.BIN` and `STG0AS.BIN` go through `tools.disc.patch_image`
   into ``OUT/image``.

8. **Ending** (``--ending PAIRING``, END-010): one ending's dialogue goes into
   `END.BIN` and `SE.DAT`'s font by ``tools.text.ending``, written to
   ``OUT/ending_changes.json`` and ``OUT/ending_prediction.json`` so the story
   outputs stay as they were; ``--ending-record`` writes its provenance.

Also writes ``OUT/prediction.json``: per box, the SHA-256 of each predicted
glyph cell in drawing order, for live checks. ``--record-dir`` writes one
committed provenance record per pilot (``<name>_story.json`` for
``<name>_pairing.json``): per box its slot, the English record's address and
SHA-256, rows, cells and row addresses; the codes it uses; the build's
sacrificed Japanese codes. It holds no text. ``--record`` names the file
for a single pilot.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from tools.disc import patch_image
from tools.font import kanji, pairs
from tools.reference.cybots_text import build_program, decode, long, read_record
from tools.reference.mame_audit import parse_driver

BASE = 0x06060000
RECORDS = 0x060A5684
EN_TABLE = 0x0B33AA
ROW_CHARS = 32
MAX_ROWS = 3
MAX_CELLS = 60
SPACE_CODE = 0x8140
NEW_CODE_FIRST = 0xF040  # user-defined Shift-JIS area: never a table code here
FILES = Path("local/extracted/saturn_jp")
LISTING = Path("references/saturn_jp/iso_listing.json")
SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
CENSUS = Path("data/text/script_census.json")
JIN_STORY = [21, *range(16)]  # D-021; jin_boxes.json predates ``story_scenes``
SCENE_SCRIPTS = 0x060AA840  # 335 scene scripts (D-021)
SCENE_COUNT = 335
PILOT_LISTS = 0x060AAD24
PILOTS = 11
APPROVED_SACRIFICE = 73  # GATE-TRANSLATION, Jin + Santana (2026-11-03)
CAPTIONS = 0x0609CC22  # VS caption boxes, 9 pilots x 10 stages (EXP-0032)
QUOTE_LIST = 9  # the versus win quotes' scene list (D-030)
VICTORY_RECORDS = 0x0607849C  # VICTORY.BIN's box table (D-030)
VICTORY_TABLE_OFFSET = (
    0x1DB94  # VICTORY.BIN's copy of the code table (WRAM-H 0x0607DB94)
)


class BudgetExceeded(SystemExit):
    """The build needs more sacrificed codes than approved."""


@dataclass(frozen=True)
class Box:
    box: int
    slot: int
    lines: tuple[int, ...]
    rows: tuple[str, ...]


def wrap(text: str) -> list[str]:
    """Re-flow an arcade record (``\\n`` line breaks) into rows."""
    flat = " ".join(part.strip() for part in text.split("\n") if part.strip())
    return textwrap.wrap(flat, ROW_CHARS) or [""]


def cells_of(rows: Sequence[str]) -> int:
    return sum(1 for row in rows for p in pairs.split_pairs(row) if p != "  ")


def allocate_codes(
    wanted: Sequence[str],
    unused: Sequence[int],
    new_slots: int,
    rare: Sequence[int],
    max_sacrifice: int | None = None,
) -> tuple[dict[str, int], list[int], list[int]]:
    """(pair -> code, new table codes, sacrificed Japanese codes).

    Raises ``ValueError`` when the codes run out, or when more than
    ``max_sacrifice`` Japanese codes would be needed.
    """
    codes: dict[str, int] = {}
    new: list[int] = []
    sacrificed: list[int] = []
    pool = list(unused)
    for pair in wanted:
        if pool:
            codes[pair] = pool.pop(0)
        elif len(new) < new_slots:
            code = NEW_CODE_FIRST + len(new)
            new.append(code)
            codes[pair] = code
        elif len(sacrificed) < len(rare):
            if max_sacrifice is not None and len(sacrificed) >= max_sacrifice:
                raise ValueError(f"more than {max_sacrifice} sacrificed codes needed")
            code = rare[len(sacrificed)]
            sacrificed.append(code)
            codes[pair] = code
        else:
            raise ValueError(f"no code left for pair {pair!r}")
    return codes, new, sacrificed


def place(rows: Sequence[bytes], room: Sequence[tuple[int, int]]) -> list[int]:
    """First-fit file offsets for each row in the free ranges ``[start, end)``."""
    free = [list(r) for r in room]
    offsets = []
    for data in rows:
        for span in free:
            if span[1] - span[0] >= len(data):
                offsets.append(span[0])
                span[0] += len(data)
                break
        else:
            raise ValueError("the rows do not fit in the text room")
    return offsets


def row_bytes(row: str, codes: dict[str, int]) -> bytes:
    data = b"".join(
        (SPACE_CODE if p == "  " else codes[p]).to_bytes(2, "big")
        for p in pairs.split_pairs(row)
    )
    data += b"\0"
    return data + bytes(-len(data) % 4)


def record_entries(pointers: Sequence[int]) -> bytes:
    out = b""
    for n, pointer in enumerate(pointers):
        word = 0xFFFF if n < len(pointers) - 1 else 0
        out += pointer.to_bytes(4, "big") + word.to_bytes(2, "big") + bytes(2)
    return out


def checked(name: str) -> bytearray:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == f"{name};1")
    data = (FILES / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{name} does not match the listing")
    return bytearray(data)


def line_table() -> list[tuple[int, int]]:
    census = json.loads(CENSUS.read_text())
    stg = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")
    return [(off, n) for off, n, _, _ in stg["blocks"][0]["table"]]


def text_lines() -> list[bytes]:
    census = json.loads(CENSUS.read_text())
    out = []
    for f in census["files"]:
        data = (FILES / f["file"]).read_bytes()
        for block in f["blocks"]:
            out += [data[off : off + n] for off, n, _, _ in block["table"]]
    return out


def codes_in(text: bytes) -> set[int]:
    found, i = set(), 0
    while i < len(text) - 1:
        if text[i] == 0x0A:
            i += 1
            continue
        found.add(int.from_bytes(text[i : i + 2], "big"))
        i += 2
    return found


def wanted_pairs(boxes: Sequence[Box]) -> list[str]:
    """Distinct pairs of all the boxes, in order of first use: one shared pool."""
    return list(
        dict.fromkeys(
            p
            for b in boxes
            for row in b.rows
            for p in pairs.split_pairs(row)
            if p != "  "
        )
    )


def shift_rows(rows: Sequence[str]) -> list[str]:
    """Indent some rows by one space (half a cell) so the rows share pairs.

    CAP-001 (2026-11-04, the user: "Indent + rank (Recommended)"). Greedy
    passes in row order: each row shorter than ``ROW_CHARS`` takes the
    variant (as is, or with a leading space) that adds fewer pairs no other
    row uses; ties keep the row as is. Stops when no row changes. The words
    are unchanged.
    """
    variants = [[r, " " + r if len(r) < ROW_CHARS else r] for r in rows]

    def ps(row: str) -> set[str]:
        return {p for p in pairs.split_pairs(row) if p != "  "}

    choice = [0] * len(rows)
    count: Counter[str] = Counter()
    for v in variants:
        count.update(ps(v[0]))
    while True:
        changed = 0
        for i, v in enumerate(variants):
            count.subtract(ps(v[choice[i]]))
            cost = [sum(1 for p in ps(x) if count[p] <= 0) for x in v]
            new = 0 if cost[0] <= cost[1] else 1
            changed += new != choice[i]
            choice[i] = new
            count.update(ps(v[new]))
        if not changed:
            return [v[c] for v, c in zip(variants, choice, strict=True)]


def rank_codes(
    candidates: Sequence[int],
    table: Sequence[int],
    line_counts: Mapping[int, int],
    staying_counts: Mapping[int, int] | None = None,
) -> list[int]:
    """Sacrifice order: rule ``lines`` (fewest lines, then table order), or,
    with ``staying_counts``, rule ``staying``: fewest lines that stay Japanese
    and are shown, then rule ``lines`` (CAP-001)."""
    if staying_counts is None:
        return sorted(candidates, key=lambda c: (line_counts.get(c, 0), table.index(c)))
    return sorted(
        candidates,
        key=lambda c: (staying_counts.get(c, 0), line_counts.get(c, 0), table.index(c)),
    )


def kept_lines(
    own: Sequence[int], users: dict[int, set[int]], ours: set[int]
) -> list[int]:
    """Own lines that a box outside ``ours`` also uses (they keep their bytes)."""
    return [n for n in own if users.get(n, set()) - ours]


def dead_lines(
    ending_boxes: set[int],
    box_lines: Mapping[int, Sequence[int]],
    users: dict[int, set[int]],
    ours: set[int],
) -> list[int]:
    """Lines used only by ``ending_boxes`` (and ``ours``): dead in this copy."""
    candidates = {n for b in ending_boxes for n in box_lines.get(b, ())}
    return sorted(
        n for n in candidates if not users.get(n, set()) - ending_boxes - ours
    )


def pilot_spec(
    pairing_path: Path,
) -> tuple[dict[str, object], dict[str, object], list[int]]:
    """(pairing, box list, story scenes) for one ``--pairing`` file."""
    pairing = json.loads(pairing_path.read_text())
    sources = pairing["sources"]
    boxes_path = Path(sources.get("boxes") or sources["jin_boxes"])
    box_list = json.loads(boxes_path.read_text())
    story = box_list.get("story_scenes", JIN_STORY)
    return pairing, box_list, list(story)


def roster_inputs(path: Path) -> tuple[list[Path], Path]:
    """The pairing files and the win-quote pairing a roster file names.

    A pilot's pairing is ``data/translations/<name>_pairing.json`` for its box
    list ``data/text/<name>_boxes.json``; the win quotes are the file the
    roster's ``win_quotes`` entry names first (RE-008).
    """
    roster = json.loads(path.read_text())
    pairings = []
    for pilot in roster["pilots"]:
        name = Path(pilot["boxes_file"]).name.removesuffix("_boxes.json")
        pairings.append(Path("data/translations") / f"{name}_pairing.json")
    return pairings, Path(roster["win_quotes"].split()[0])


def build(args: argparse.Namespace) -> int:
    specs = [pilot_spec(p) for p in args.pairing]
    driver = args.driver.read_text(encoding="latin-1")
    romset = parse_driver(driver)["cybotsu"]
    archives = [args.rompath / "cybotsu.zip"]
    if romset.parent:
        archives.append(args.rompath / f"{romset.parent}.zip")
    program = build_program([p for p in archives if p.exists()], romset)
    font = pairs.load_arcade_font(args.font)
    stg, kan = checked("STG0AS.BIN"), checked("KANJI.BIN")

    def u16(a: int) -> int:
        return int.from_bytes(stg[a - BASE : a - BASE + 2], "big")

    def u32(a: int) -> int:
        return int.from_bytes(stg[a - BASE : a - BASE + 4], "big")

    boxes: list[Box] = []
    english_records = {}
    pilot_of_box: dict[int, int] = {}
    for index, (pairing, _, _) in enumerate(specs):
        for p in pairing["pairs"]:  # type: ignore[attr-defined]
            pilot_of_box[p["box"]] = index
    for p in (p for pairing, _, _ in specs for p in pairing["pairs"]):  # type: ignore[attr-defined]
        slot = p["arcade_slot"]
        record = read_record(program, long(program, EN_TABLE + 4 * slot))
        english_records[slot] = record
        rows = wrap(decode(record.codes))
        if len(rows) > MAX_ROWS or cells_of(rows) > MAX_CELLS:
            raise SystemExit(
                f"box {p['box']}: {len(rows)} rows, {cells_of(rows)} cells"
            )
        boxes.append(Box(p["box"], slot, tuple(p["saturn_lines"]), tuple(rows)))
    # Win quotes (VICTORY.BIN, D-030): the boxes the built pilots reach.
    quotes: list[Box] = []
    if args.quotes:
        doc = json.loads(args.quotes.read_text())
        index_of = {int(bl["pilot"]): i for i, (_, bl, _) in enumerate(specs)}  # type: ignore[call-overload]
        for e in doc["entries"]:
            if e["pilot"] in index_of:
                for qb in e["saturn_boxes"]:
                    pilot_of_box.setdefault(qb, index_of[e["pilot"]])
        for q in doc["roster_quote_boxes"]:
            if q["box"] not in pilot_of_box:
                continue  # a pilot outside this build
            slot = q["arcade_slot"]
            record = read_record(program, long(program, EN_TABLE + 4 * slot))
            english_records[slot] = record
            rows = wrap(decode(record.codes))
            if len(rows) > MAX_ROWS or cells_of(rows) > MAX_CELLS:
                raise SystemExit(f"quote box {q['box']}: {len(rows)} rows")
            quotes.append(Box(q["box"], slot, tuple(q["saturn_lines"]), tuple(rows)))
    if args.indent:
        shifted = iter(shift_rows([r for b in boxes + quotes for r in b.rows]))
        boxes, quotes = (
            [
                Box(b.box, b.slot, b.lines, tuple(next(shifted) for _ in b.rows))
                for b in group
            ]
            for group in (boxes, quotes)
        )
        for b in boxes + quotes:
            if cells_of(b.rows) > MAX_CELLS:
                raise SystemExit(f"box {b.box}: {cells_of(b.rows)} cells after indent")

    # Which boxes each scene shows, for every pilot.
    starts = sorted({u32(SCENE_SCRIPTS + 4 * k) for k in range(SCENE_COUNT)})

    def script_boxes(script: int) -> list[int]:
        end = next((s for s in starts if s > script), script + 0x80)
        found: list[int] = []
        for a in range(script, end, 2):
            w = u16(a)
            if w == 0xFFFF or w >= 0xC000:  # commands (EXP-0022's box_list.py)
                continue
            if w & 0x7FFF not in found:
                found.append(w & 0x7FFF)
        return found

    heads = [u32(PILOT_LISTS + 4 * p) for p in range(PILOTS)]
    ordered = sorted(set(heads))
    scene_boxes: dict[tuple[int, int], list[int]] = {}
    for pilot, head in enumerate(heads):
        nxt = [h for h in ordered if h > head]
        count = ((nxt[0] if nxt else PILOT_LISTS) - head) // 4
        for k in range(count):
            scene_boxes[(pilot, k)] = script_boxes(u32(head + 4 * k))
    active = {b for found in scene_boxes.values() for b in found}

    # Lines and their users (boxes some scene shows).
    ours = {b.box for b in boxes}
    lines = line_table()
    address_line = {BASE + off: i for i, (off, _) in enumerate(lines)}
    users: dict[int, set[int]] = {}
    box_lines: dict[int, list[int]] = {}
    for box in range(1074):
        entry = u32(RECORDS + 4 * box) + 8
        while True:
            line = address_line.get(u32(entry))
            if line is not None:
                box_lines.setdefault(box, []).append(line)
                if box in active:
                    users.setdefault(line, set()).add(box)
            if u16(entry + 4) != 0xFFFF:
                break
            entry += 8
    own_lines = sorted({n for b in boxes for n in b.lines})
    kept = kept_lines(own_lines, users, ours)
    ending: set[int] = set()
    for _, box_list, story in specs:
        pilot = int(box_list["pilot"])  # type: ignore[call-overload]
        for (p, k), found in scene_boxes.items():
            if p == pilot and k not in story:
                ending |= set(found)
    elsewhere = {
        b
        for (p, k), found in scene_boxes.items()
        for b in found
        if not any(
            p == int(bl["pilot"]) and k not in st  # type: ignore[call-overload]
            for _, bl, st in specs
        )
    }
    ending_only = ending - elsewhere
    dead = dead_lines(ending_only, box_lines, users, ours)
    free_lines = [n for n in own_lines if n not in kept] + dead
    room: list[list[int]] = []
    for n in sorted(set(free_lines)):
        off, length = lines[n]
        span = [off, off + ((length + 1 + 3) & ~3)]
        if room and room[-1][1] == span[0]:
            room[-1][1] = span[1]
        else:
            room.append(span)

    table = kanji.read_code_table(bytes(stg))
    texts = text_lines()
    kept_codes: set[int] = set()
    for n in kept:
        kept_codes |= codes_in(bytes(stg[lines[n][0] : lines[n][0] + lines[n][1]]))
    unused = pairs.unused_codes(table, texts)
    line_counts: Counter[int] = Counter()
    for text in texts:
        line_counts.update(codes_in(text) & set(table))
    replaced = set(own_lines) - set(kept) | {n for q in quotes for n in q.lines}
    staying_counts: Counter[int] | None = None
    if args.rank == "staying":
        captions = {u16(CAPTIONS + 2 * k) for k in range(PILOTS * 10)} - {0}
        shown = {n for b in active | captions for n in box_lines.get(b, [])}
        staying_counts = Counter()
        for n in shown - replaced:
            off, length = lines[n]
            staying_counts.update(codes_in(bytes(stg[off : off + length])))
    rare = rank_codes(
        [
            c
            for c in table
            if c not in unused and c not in kept_codes and c != SPACE_CODE
        ],
        table,
        line_counts,
        staying_counts,
    )
    wanted = wanted_pairs(boxes + quotes)
    last_row = kanji.TABLE_ROWS - 1
    last_row_used = len(table) - last_row * kanji.TABLE_ROW_CODES
    new_slots = kanji.TABLE_ROW_CODES - last_row_used - 1  # keep a 0 terminator
    needed = max(0, len(wanted) - len(unused) - new_slots)
    # Lines (STG0AS.BIN's numbering; END.BIN and VICTORY.BIN hold copies) that
    # would show a pair glyph: users of a sacrificed code that stay Japanese.
    touched = sorted(
        {
            n
            for n, (off, length) in enumerate(lines)
            if n not in replaced
            and codes_in(bytes(stg[off : off + length])) & set(rare[:needed])
        }
    )
    # VICTORY.BIN shows only list 9 (its one post, D-030): its copies of the
    # quotes' and the stories' own lines are room, less any line another
    # list-9 box shows.
    vic_room: list[list[int]] = []
    if quotes:
        census = json.loads(CENSUS.read_text())
        vic_first = next(f for f in census["files"] if f["file"] == "VICTORY.BIN")
        delta = vic_first["blocks"][0]["table"][0][0] - lines[0][0]
        others = {
            n
            for (p, _), found in scene_boxes.items()
            if p == QUOTE_LIST
            for b in found
            if b not in {q.box for q in quotes}
            for n in box_lines.get(b, [])
        }
        for n in sorted(
            ({n for q in quotes for n in q.lines} | set(own_lines)) - others
        ):
            off, length = lines[n]
            span = [off + delta, off + delta + ((length + 1 + 3) & ~3)]
            if vic_room and vic_room[-1][1] == span[0]:
                vic_room[-1][1] = span[1]
            else:
                vic_room.append(span)
    budget = {
        "pilots": [str(p) for p in args.pairing],
        "quote_boxes": len(quotes),
        "rank": args.rank,
        "indent": args.indent,
        "boxes": len(boxes),
        "pairs": len(wanted),
        "unused_codes": len(unused),
        "new_codes_available": new_slots,
        "sacrifice_needed": needed,
        "sacrifice_approved": args.max_sacrifice,
        "japanese_lines_touched_by_sacrifice": touched,
        "text_bytes": sum(
            len(row_bytes(r, dict.fromkeys(wanted, 1))) for b in boxes for r in b.rows
        ),
        "room_bytes": sum(e - s for s, e in room),
        "quote_text_bytes": sum(
            len(row_bytes(r, dict.fromkeys(wanted, 1))) for b in quotes for r in b.rows
        ),
        "quote_room_bytes": sum(e - s for s, e in vic_room),
        "kept_lines": kept,
        "dead_lines": dead,
    }
    if args.budget:
        print(json.dumps(budget))
        return 0
    if needed > args.max_sacrifice:
        print(json.dumps(budget))
        raise BudgetExceeded(
            f"{needed} sacrificed codes needed, {args.max_sacrifice} approved"
        )
    codes, new, sacrificed = allocate_codes(
        wanted, unused, new_slots, rare, args.max_sacrifice
    )

    changes: list[dict[str, object]] = []
    vic = checked("VICTORY.BIN") if quotes else bytearray()

    # Table: new codes after the last row's codes (and in VICTORY.BIN's copy).
    targets: list[tuple[bytearray, int, str]] = [
        (stg, kanji.TABLE_OFFSET, "STG0AS.BIN")
    ]
    if quotes:
        targets.append((vic, VICTORY_TABLE_OFFSET, "VICTORY.BIN"))
    for target_file, offset, name in targets:
        row_start = offset + last_row * kanji.TABLE_ROW_CODES * 2
        for k, code in enumerate(new):
            at = row_start + 2 * (last_row_used + k)
            target_file[at : at + 2] = code.to_bytes(2, "big")
        if new:
            first = row_start + 2 * last_row_used
            changes.append(
                {
                    "file": name,
                    "start": first,
                    "end": first + 2 * len(new),
                    "what": "table codes",
                }
            )
    table = kanji.read_code_table(bytes(stg))
    cells = kanji.decode(bytes(kan))
    for pair, code in codes.items():
        cells[table.index(code)] = pairs.render_pair(font, pair)
    kan[:] = kanji.encode(cells)
    glyphs_changed = sorted(table.index(c) for c in codes.values())

    # Rows and records: story in STG0AS.BIN, win quotes in VICTORY.BIN.
    prediction = []
    record_out = []
    groups = [(boxes, stg, room, RECORDS, "STG0AS.BIN")]
    if quotes:
        groups.append((quotes, vic, vic_room, VICTORY_RECORDS, "VICTORY.BIN"))
    group_rows: dict[str, list[bytes]] = {}
    for group, data_file, group_room, records, name in groups:
        all_rows = [row_bytes(r, codes) for b in group for r in b.rows]
        group_rows[name] = all_rows
        offsets = iter(place(all_rows, [(r[0], r[1]) for r in group_room]))
        data_rows = iter(all_rows)
        for b in group:
            pointers = []
            for _ in b.rows:
                off, data = next(offsets), next(data_rows)
                data_file[off : off + len(data)] = data
                changes.append(
                    {
                        "file": name,
                        "start": off,
                        "end": off + len(data),
                        "what": f"box {b.box} row",
                    }
                )
                pointers.append(BASE + off)
            rec = int.from_bytes(
                data_file[records - BASE + 4 * b.box : records - BASE + 4 * b.box + 4],
                "big",
            )
            entries = record_entries(pointers)
            data_file[rec - BASE + 8 : rec - BASE + 8 + 24] = entries + bytes(
                24 - len(entries)
            )
            changes.append(
                {
                    "file": name,
                    "start": rec - BASE + 8,
                    "end": rec - BASE + 32,
                    "what": f"box {b.box} record",
                }
            )
            drawn = [
                cells[table.index(codes[p])]
                for r in b.rows
                for p in pairs.split_pairs(r)
                if p != "  "
            ]
            prediction.append(
                {"box": b.box, "cells": [hashlib.sha256(c).hexdigest() for c in drawn]}
            )
            en = english_records[b.slot]
            out_entry: dict[str, object] = {
                "box": b.box,
                "slot": b.slot,
                "saturn_lines": list(b.lines),
                "english_record": f"0x{en.address:06X}",
                "english_sha256": hashlib.sha256(en.codes).hexdigest(),
                "rows": len(b.rows),
                "cells": len(drawn),
                "row_addresses": [f"0x{p:08X}" for p in pointers],
            }
            if name != "STG0AS.BIN":
                out_entry["file"] = name
            record_out.append(out_entry)

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=False)
    (out / "STG0AS.BIN").write_bytes(stg)
    (out / "KANJI.BIN").write_bytes(kan)
    if quotes:
        (out / "VICTORY.BIN").write_bytes(vic)
    (out / "changes.json").write_text(
        json.dumps({"ranges": changes, "kanji_glyphs": glyphs_changed}, indent=1) + "\n"
    )
    (out / "prediction.json").write_text(json.dumps(prediction, indent=1) + "\n")
    summary: dict[str, object] = {
        "boxes": len(boxes),
        "rows": len(group_rows["STG0AS.BIN"]),
        "pairs": len(wanted),
        "unused_codes_used": min(len(wanted), len(unused)),
        "new_codes": len(new),
        "sacrificed": [
            {"code": f"0x{c:04X}", "glyph": table.index(c), "lines": line_counts[c]}
            for c in sacrificed
        ],
        "kept_lines": kept,
        "text_bytes": sum(len(r) for r in group_rows["STG0AS.BIN"]),
        "room_bytes": sum(e - s for s, e in room),
    }
    if quotes:
        summary["quote_boxes"] = len(quotes)
        summary["quote_text_bytes"] = sum(len(r) for r in group_rows["VICTORY.BIN"])
        summary["quote_room_bytes"] = sum(e - s for s, e in vic_room)
    record_paths: list[Path | None] = [None] * len(specs)
    if args.record:
        record_paths[0] = args.record
    if args.record_dir:
        record_paths = [
            args.record_dir / p.name.replace("_pairing", "_story") for p in args.pairing
        ]
    for index, path in enumerate(record_paths):
        if path is None:
            continue
        mine = [r for r in record_out if pilot_of_box[int(str(r["box"]))] == index]
        my_pairs = wanted_pairs(
            [b for b in boxes + quotes if pilot_of_box[b.box] == index]
        )
        my_codes = {p: codes[p] for p in my_pairs} if len(specs) > 1 else codes
        path.write_text(
            json.dumps(
                {
                    "task": args.task,
                    "policy": (
                        "official US arcade English, as paired (D-022), unchanged;"
                        " pair glyphs (D-024)"
                    ),
                    "sources": {
                        "program_sha256": hashlib.sha256(program).hexdigest(),
                        "english_table": f"0x{EN_TABLE:06X}",
                        "pairing": str(args.pairing[index]),
                        "font_capture_sha256": hashlib.sha256(
                            args.font.read_bytes()
                        ).hexdigest(),
                    },
                    "codes": {
                        pair_id: f"0x{code:04X}"
                        for pair_id, code in enumerate(my_codes.values())
                    },
                    "summary": summary,
                    "boxes": mine,
                },
                indent=1,
            )
            + "\n"
        )
    print(json.dumps(summary))
    extra: list[str] = []
    if args.ending:
        from tools.text import ending as ending_text

        built = ending_text.compile_ending(args.ending, program, font, texts, args.task)
        (out / "END.BIN").write_bytes(built.end)
        (out / "SE.DAT").write_bytes(built.se)
        (out / "ending_changes.json").write_text(
            json.dumps({"ranges": built.changes}, indent=1) + "\n"
        )
        (out / "ending_prediction.json").write_text(
            json.dumps(built.prediction, indent=1) + "\n"
        )
        if args.ending_record:
            args.ending_record.write_text(json.dumps(built.record, indent=1) + "\n")
        print(json.dumps(built.record["summary"]))
        for name, data in sorted(built.images.items()):
            (out / name).write_bytes(data)
        for name in ("END.BIN", "SE.DAT", *sorted(built.images)):
            extra += ["--file", f"{name};1", "--data", str(out / name)]
    return patch_image.main(
        [
            "--source-dir",
            str(SOURCE_DIR),
            "--manifest",
            str(MANIFEST),
            "--track",
            TRACK,
            "--file",
            "STG0AS.BIN;1",
            "--data",
            str(out / "STG0AS.BIN"),
            "--file",
            "KANJI.BIN;1",
            "--data",
            str(out / "KANJI.BIN"),
            *(
                ["--file", "VICTORY.BIN;1", "--data", str(out / "VICTORY.BIN")]
                if quotes
                else []
            ),
            *extra,
            "--out-dir",
            str(out / "image"),
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--pairing", type=Path, action="append", default=[])
    parser.add_argument(
        "--roster",
        type=Path,
        help="build every pilot of a roster file (data/text/m5_roster.json)",
    )
    parser.add_argument("--quotes", type=Path, help="win-quote pairing (D-030)")
    parser.add_argument("--ending", type=Path, help="an ending's pairing (END-010)")
    parser.add_argument("--ending-record", type=Path, help="the ending's record")
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--driver", type=Path, required=True)
    parser.add_argument("--rompath", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--record", type=Path, help="record file (one pilot)")
    parser.add_argument("--record-dir", type=Path, help="one record per pilot")
    parser.add_argument("--task", default="RE-003", help="the record's task")
    parser.add_argument("--max-sacrifice", type=int, default=APPROVED_SACRIFICE)
    parser.add_argument("--budget", action="store_true", help="print the budget only")
    parser.add_argument(
        "--rank",
        choices=["lines", "staying"],
        default="lines",
        help="sacrifice order (CAP-001: staying, for the M5 roster)",
    )
    parser.add_argument(
        "--indent",
        action="store_true",
        help="indent rows by half a cell where it saves pairs (CAP-001)",
    )
    args = parser.parse_args(argv)
    if args.roster:
        args.pairing, args.quotes = roster_inputs(args.roster)
    if not args.pairing:
        parser.error("--pairing or --roster is required")
    return build(args)


if __name__ == "__main__":
    raise SystemExit(main())
