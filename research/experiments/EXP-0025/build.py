"""EXP-0025: build the LAYOUT-001 Phase C image: pair glyphs in the M1 box.

Run from the repository root:

    ./invenv.sh python research/experiments/EXP-0025/build.py FONT_JSON OUT

``FONT_JSON`` is the ignored arcade glyph capture (``capture_font.py``).
From the untouched files in ``local/extracted/saturn_jp/`` (SHA-256 checked
against ``references/saturn_jp/iso_listing.json``):

- ``KANJI.BIN``: each distinct pair of ``ROWS`` is rendered with
  ``tools.font.pairs`` into the glyph slot of a table code that no Japanese
  line uses (the 912-code census, D-023), taken in table order. The table
  itself is not changed.
- ``STG0AS.BIN``: the three rows, as those codes (``0x8140`` for a pair of
  spaces), NUL-terminated and 4-byte aligned, are written from the start of
  Saturn line 752. That is Jin's ending text, dead in this copy (EXP-0024),
  and the script checks that the rows stay inside lines 752-777. Box 2's
  record (``0x0609D184``) gets three entries: rows 1 and 2 continue
  (``0xFFFF``), row 3 ends.

It writes the two files to ``OUT/``, the image with ``tools.disc.patch_image``
to ``OUT/image/``, ``OUT/prediction.json`` (per row, each cell's glyph slot and
the SHA-256 of its 128 bytes) and ``OUT/preview.png`` (the rows drawn as the
Saturn would, on the box grey). ``OUT`` must be under ``build/``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.disc import patch_image
from tools.font import kanji, pairs
from tools.memory.mcs_extract import encode_png

FILES = Path("local/extracted/saturn_jp")
LISTING = Path("references/saturn_jp/iso_listing.json")
SOURCE_DIR = Path("local/disc_images/cyberbots_saturn_jp_2m")
TRACK = "Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin"
MANIFEST = Path("references/saturn_jp/README.md")
BASE = 0x06060000
RECORD = 0x0609D184  # box 2, the M1 box (D-021)
DEAD_FIRST, DEAD_LAST = 752, 777  # Jin's ending lines in this copy (EXP-0024)
SPACE = 0x8140
ROWS = [
    "Pack my box with five dozen jugs",
    "THE QUICK BROWN FOX: 0123456789!",
    'Isn\'t it "odd", Shade? Yes - no.',
]
SATURN_RGB = {
    0: (0x60,) * 3,
    9: (0xF0,) * 3,
    10: (0xD0,) * 3,
    11: (0xA0,) * 3,
    12: (0x70,) * 3,
    13: (0x10,) * 3,
    14: (0x80,) * 3,
}


def checked(name: str) -> bytearray:
    listing = json.loads(LISTING.read_text())
    entry = next(f for f in listing["files"] if f["path"] == f"{name};1")
    data = (FILES / name).read_bytes()
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise SystemExit(f"{name} does not match the listing")
    return bytearray(data)


def main(font_path: Path, out: Path) -> int:
    font = pairs.load_arcade_font(font_path)
    stg, kan = checked("STG0AS.BIN"), checked("KANJI.BIN")
    codes = kanji.read_code_table(bytes(stg))
    census = json.loads(Path("data/text/script_census.json").read_text())
    texts = []
    for f in census["files"]:
        data = (FILES / f["file"]).read_bytes()
        for block in f["blocks"]:
            texts += [data[off : off + n] for off, n, _, _ in block["table"]]
    free = pairs.unused_codes(codes, texts)
    cells = kanji.decode(bytes(kan))
    row_pairs = [pairs.split_pairs(r) for r in ROWS]
    wanted = sorted({p for row in row_pairs for p in row if p != "  "})
    if len(wanted) > len(free):
        raise SystemExit(f"{len(wanted)} pairs, {len(free)} free codes")
    code_of = dict(zip(wanted, free, strict=False))
    for pair, code in code_of.items():
        cells[codes.index(code)] = pairs.render_pair(font, pair)
    kan[:] = kanji.encode(cells)

    lines = census_lines(census)
    start = lines[DEAD_FIRST][0]
    end = lines[DEAD_LAST][0] + lines[DEAD_LAST][1] + 1
    cursor = start
    pointers = []
    prediction = []
    for row in row_pairs:
        data = b"".join(code_of.get(p, SPACE).to_bytes(2, "big") for p in row) + b"\0"
        data += bytes(-len(data) % 4)
        if cursor + len(data) > end:
            raise SystemExit("the rows do not fit in the dead lines")
        stg[cursor : cursor + len(data)] = data
        pointers.append(BASE + cursor)
        prediction.append(
            [
                {
                    "pair": p,
                    "slot": codes.index(code_of[p]),
                    "sha256": hashlib.sha256(
                        cells[codes.index(code_of[p])]
                    ).hexdigest(),
                }
                if p in code_of
                else {"pair": p, "slot": None}
                for p in row
            ]
        )
        cursor += len(data)
    entries = b""
    for n, pointer in enumerate(pointers):
        word = 0xFFFF if n < len(pointers) - 1 else 0
        entries += pointer.to_bytes(4, "big") + word.to_bytes(2, "big") + bytes(2)
    record = RECORD - BASE
    stg[record + 8 : record + 8 + len(entries)] = entries

    out.mkdir(parents=True, exist_ok=False)
    (out / "STG0AS.BIN").write_bytes(stg)
    (out / "KANJI.BIN").write_bytes(kan)
    (out / "prediction.json").write_text(
        json.dumps(
            {
                "rows": prediction,
                "pairs": len(wanted),
                "free_codes": len(free),
                "row_addresses": [f"0x{p:08X}" for p in pointers],
                "dead_room": [f"0x{BASE + start:08X}", f"0x{BASE + end:08X}"],
            },
            indent=1,
        )
        + "\n"
    )
    write_preview(out / "preview.png", font, row_pairs)
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
            "--out-dir",
            str(out / "image"),
        ]
    )


def census_lines(census: dict[str, object]) -> list[tuple[int, int]]:
    stg = next(f for f in census["files"] if f["file"] == "STG0AS.BIN")  # type: ignore[attr-defined]
    return [(off, n) for off, n, _, _ in stg["blocks"][0]["table"]]


def write_preview(
    path: Path, font: dict[str, pairs.Glyph], rows: list[list[str]]
) -> None:
    width, height = 16 + 14 * 16 + 8, 16 * len(rows) + 8
    canvas = [[0] * width for _ in range(height)]
    for r, row in enumerate(rows):
        for c, pair in enumerate(row):
            if pair == "  ":
                continue
            cell = pairs.render_pair(font, pair)
            for y in range(16):
                for x in range(16):
                    v = (cell[y * 8 + x // 2] >> (4 * (1 - x % 2))) & 0xF
                    if v:
                        canvas[4 + 16 * r + y][4 + 14 * c + x] = v
    rgb = bytes(
        b for row in canvas for v in row for b in SATURN_RGB.get(v, (255, 0, 255))
    )
    path.write_bytes(encode_png(width, height, rgb))


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
