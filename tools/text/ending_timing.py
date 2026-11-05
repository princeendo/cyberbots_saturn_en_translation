"""Retime an ending's English boxes so each holds its finished line (END-011).

The user's choice (2026-11-05): "Faster typing + move cues (Recommended)".

How ending boxes are timed (EXP-0048, D-045):

- Script word ``0xE2nn`` before a box sets its typing interval to ``nn``
  frames per glyph (``E206`` in the Japanese; ``E203`` types twice as fast).
- Script word ``0xEAnn`` after a box waits until the scene timer reaches cue
  ``nn``; the box then closes. Each list's cues are 16-bit frames in a table
  that `END.BIN`'s pointer table ``0x060879A0`` gives. Moving one cue moves
  only that close and the next box's open.

The rule:

1. Every English box that is not a speaker name and closes on a cue types
   at ``TYPING_FRAMES`` per glyph (its ``E2nn`` word becomes ``E203``);
   other English boxes follow step 3.
2. A run is a sequence of boxes, each closing on a cue and the next opening
   right after it (within ``GAP`` frames, from the forced run's frames in
   ``data/text/ending_surfaces.json``). In a run, the first open and the
   last cue stay where they are, so nothing outside the run moves, and no
   scene change or track moves.
3. A box that ends on a wait: the script waits for its typing, then the
   wait. Its interval and wait are chosen so typing + wait equals the
   Japanese box's (``interval_and_wait``). A box the scene's end follows
   directly gets the interval closest to the Japanese typing time
   (``segment_interval``). So the scene changes, and the music that starts
   with them, stay where they were.
4. In a run, each English box gets its typing time
   (``START_FRAMES`` + ``TYPING_FRAMES`` x glyph cells) plus an equal share
   of the run's spare time; any other box keeps its window. The build stops
   if a share is below ``MIN_HOLD``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

BASE = 0x06060000
CUE_POINTERS = 0x060879A0
SCENE_LISTS = 0x06086E54
TYPING_FRAMES = 3
TYPING_WORD = 0xE200 | TYPING_FRAMES
START_FRAMES = 6
MAX_INTERVAL = 16  # the slowest typing used to keep a scene's end in place
MIN_HOLD = 42  # frames, 0.7 s: the share the user was shown (END-011)
GAP = 4
NAMES = range(601, 615)


@dataclass
class Retimed:
    changes: list[dict[str, object]] = field(default_factory=list)
    boxes: list[dict[str, Any]] = field(default_factory=list)
    waits: list[dict[str, Any]] = field(default_factory=list)


def _u16(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - BASE : a - BASE + 2], "big")


def _u32(data: bytes, a: int) -> int:
    return int.from_bytes(data[a - BASE : a - BASE + 4], "big")


def walk(
    end: bytes, list_no: int, first_scene: int, want: Sequence[int]
) -> list[tuple[int, str, int]]:
    """(address, kind, value) tokens of the list's script.

    The walk ends at the first timing word (cue, wait or segment) after the
    last opening of ``want``, so the last box's ending is included.
    """
    a = _u32(end, _u32(end, SCENE_LISTS + 4 * list_no) + 4 * first_scene)
    tokens: list[tuple[int, str, int]] = []
    matched = 0
    while matched < len(want) or tokens[-1][1] not in ("cue", "wait", "segment"):
        if len(tokens) > 5000:
            raise ValueError(f"list {list_no}: script walk did not meet the openings")
        w = _u16(end, a)
        if w < 0x8000:
            tokens.append((a, "open", w))
            if w == want[matched]:
                matched += 1
        elif w == 0xFFFF:
            pass
        elif w < 0xC000:
            tokens.append((a, "close", w & 0x7FFF))
        elif w & 0xFF00 == 0xEA00:
            tokens.append((a, "cue", w & 0xFF))
        elif w & 0xFF00 == 0xE300:
            tokens.append((a, "wait", w & 0xFF))
        elif w == 0xE000:
            tokens.append((a, "segment", 0))
        a += 2
    while _u16(end, a) & 0xFF00 == 0xE300:  # waits that follow directly
        tokens.append((a, "wait", _u16(end, a) & 0xFF))
        a += 2
    return tokens


def endings(
    tokens: Sequence[tuple[int, str, int]],
) -> list[tuple[int, int, str, int, list[tuple[int, int]]]]:
    """Per non-name opening: (open address, box, ending kind, value, waits).

    For a box that ends on a wait, ``waits`` is that wait and the waits that
    follow it directly, as (address, frames); ``value`` is their sum.
    """
    out: list[tuple[int, int, str, int, list[tuple[int, int]]]] = []
    for k, (address, kind, value) in enumerate(tokens):
        if kind != "open" or value in NAMES:
            continue
        m = next(
            (
                j
                for j in range(k + 1, len(tokens))
                if tokens[j][1] in ("cue", "wait", "segment")
                or (tokens[j][1] == "close" and tokens[j][2] == value)
            ),
            None,
        )
        if m is None:
            out.append((address, value, "none", 0, []))
            continue
        ta, tk, tv = tokens[m]
        waits: list[tuple[int, int]] = []
        if tk == "wait":
            waits.append((ta, tv))
            j = m + 1
            while (
                j < len(tokens)
                and tokens[j][1] == "wait"
                and tokens[j][0] == waits[-1][0] + 2
            ):
                waits.append((tokens[j][0], tokens[j][2]))
                j += 1
        out.append((address, value, tk, sum(w for _, w in waits) or tv, waits))
    return out


def segment_interval(
    japanese: int, english: int, original: int, slowest: int | None = None
) -> int:
    """Typing interval for a box the scene's end follows directly (step 3).

    The next scene is posted when the typing ends, so the interval whose
    English typing time is closest to the Japanese one (the faster of two
    equally close) keeps the scene change where it was.
    """
    target = japanese * original
    return min(
        range(1, (slowest or max(original, TYPING_FRAMES)) + 1),
        key=lambda i: (abs(english * i - target), i),
    )


def interval_and_wait(
    waits: Sequence[int],
    japanese: int,
    english: int,
    original: int,
    slowest: int | None = None,
) -> tuple[int, list[int]]:
    """Typing interval and waits for a box that ends on waits (rule step 3).

    The script waits for the typing, then each wait, so the time to the next
    event is typing + the waits. Keep it equal to the Japanese (``japanese``
    glyphs at ``original`` frames each): the fastest interval from
    ``TYPING_FRAMES`` up whose remainder fits in the waits (a byte each),
    spread evenly. If none fits, the closest one (the caller reports it).
    """
    target = sum(waits) + japanese * original
    room = 0xFF * len(waits)
    best: tuple[int, int, int] | None = None
    for interval in range(TYPING_FRAMES, (slowest or max(original, TYPING_FRAMES)) + 1):
        rest = target - english * interval
        clipped = min(max(rest, 0), room)
        if best is None or abs(rest - clipped) < abs(best[2]):
            best = (interval, clipped, rest - clipped)
        if rest == clipped:
            break
    assert best is not None
    interval, rest, _ = best
    k = len(waits)
    return interval, [rest // k + (1 if i < rest % k else 0) for i in range(k)]


def shares(
    windows: Sequence[int], typing: Sequence[int | None]
) -> tuple[list[int], int]:
    """New windows for one run, and the hold each English box gets.

    ``typing[i]`` is ``None`` for a box that stays as it is. The total is
    kept, so the run's last cue does not move; the remainder of the equal
    split goes to the last English box.
    """
    english = [i for i, t in enumerate(typing) if t is not None]
    if not english:
        return list(windows), 0
    spare = sum(windows[i] for i in english) - sum(t for t in typing if t is not None)
    hold = spare // len(english)
    new = list(windows)
    for i in english:
        new[i] = int(typing[i] or 0) + hold
    new[english[-1]] += spare - hold * len(english)
    return new, hold


def retime(
    end: bytearray,
    list_no: int,
    surfaces: Mapping[str, Any],
    cells: Mapping[int, int],
    japanese_cells: Mapping[int, int],
    min_hold: int = MIN_HOLD,
) -> Retimed:
    """Apply the rule to ``end`` for one list.

    ``cells`` maps each English box to its glyph cells; ``japanese_cells``
    each box to its Japanese glyphs (from the untouched `END.BIN`).
    """
    openings = [o for o in surfaces["openings"]]
    first_scene = surfaces["posts"][0]["scene"]
    tokens = walk(bytes(end), list_no, first_scene, [o["box"] for o in openings])
    ends = endings(tokens)
    non_names = [o for o in openings if o["box"] not in NAMES]
    if len(ends) < len(non_names):
        raise ValueError(
            f"list {list_no}: {len(ends)} script boxes, {len(non_names)} seen"
        )
    out = Retimed()

    # 1. Typing speed, and the waits after boxes that end on one.
    def put(at: int, word: int, what: str) -> None:
        if _u16(bytes(end), at) != word:
            end[at - BASE : at - BASE + 2] = word.to_bytes(2, "big")
            out.changes.append(
                {
                    "file": "END.BIN",
                    "start": at - BASE,
                    "end": at - BASE + 2,
                    "what": what,
                }
            )

    delta: dict[int, int] = {}  # Japanese minus English frames, per opening
    typing_at: dict[int, int] = {}
    wait_index: list[int] = []  # the opening index of each out.waits entry
    absorbed: set[int] = set()
    for index, (address, box, kind, value, waits) in enumerate(ends[: len(non_names)]):
        if box not in cells:
            continue
        at = next(
            (
                address - 2 * k
                for k in range(1, 4)
                if _u16(bytes(end), address - 2 * k) & 0xFF00 == 0xE200
            ),
            0,
        )
        if not at:
            raise ValueError(f"list {list_no}: no typing word before box {box}")
        word = _u16(bytes(end), at)
        typing_at[index] = at
        original = word & 0xFF
        interval = TYPING_FRAMES
        if kind == "wait":
            interval, new_waits = interval_and_wait(
                [w for _, w in waits], japanese_cells[box], cells[box], original
            )
            for (wait_at, _), w in zip(waits, new_waits, strict=True):
                put(wait_at, 0xE300 | w, f"box {box} wait")
            out.waits.append(
                {
                    "box": box,
                    "interval": [original, interval],
                    "wait": [[w for _, w in waits], new_waits],
                    "japanese_frames": japanese_cells[box] * original + value,
                    "english_frames": cells[box] * interval + sum(new_waits),
                }
            )
            delta[index] = (
                out.waits[-1]["japanese_frames"] - out.waits[-1]["english_frames"]
            )
            wait_index.append(index)
        elif kind == "segment":
            interval = segment_interval(japanese_cells[box], cells[box], original)
            out.waits.append(
                {
                    "box": box,
                    "interval": [original, interval],
                    "wait": None,
                    "japanese_frames": japanese_cells[box] * original,
                    "english_frames": cells[box] * interval,
                }
            )
            delta[index] = (
                out.waits[-1]["japanese_frames"] - out.waits[-1]["english_frames"]
            )
            wait_index.append(index)
        put(at, 0xE200 | interval, f"box {box} typing")
    # 2. Runs of cued boxes, and their new cues. A box joins the run before
    # it when no wait or scene end lies between that run's cue and its open.
    open_index = [
        k for k, tok in enumerate(tokens) if tok[1] == "open" and tok[2] not in NAMES
    ]
    clean: set[int] = set()
    for i in range(1, min(len(open_index), len(non_names))):
        between = tokens[open_index[i - 1] + 1 : open_index[i]]
        if not any(kind in ("wait", "segment") for _, kind, _ in between):
            clean.add(i)
    pointer = _u32(bytes(end), CUE_POINTERS + 4 * list_no)
    rows = [(o, e[:4]) for o, e in zip(non_names, ends, strict=False)]
    run: list[tuple[dict[str, Any], int]] = []
    runs: list[tuple[list[tuple[dict[str, Any], int]], int]] = []  # (run, next)
    for index, (o, (_, box, kind, value)) in enumerate(rows):
        if box != o["box"]:
            raise ValueError(f"list {list_no}: script box {box}, seen {o['box']}")
        cued = kind == "cue" and o["close"] is not None
        joins = bool(run) and index in clean
        if cued and joins:
            run.append((o, value))
        else:
            if run:
                runs.append((run, index))
            run = [(o, value)] if cued else []
    if run:
        runs.append((run, len(rows)))
    for run, following in runs:
        windows = [o["close"] - o["open"] for o, _ in run]
        # A box that ends on waits right after the run and cannot match the
        # Japanese time by itself: its difference goes to the run's last cue,
        # so the scene still ends where it did (rule step 3).
        extra = 0
        if following < len(rows):
            nxt = rows[following][0]
            if nxt["open"] - (run[-1][0]["close"] or 0) <= GAP:
                extra = delta.get(following, 0)
        typing = [
            START_FRAMES + TYPING_FRAMES * cells[o["box"]]
            if o["box"] in cells
            else None
            for o, _ in run
        ]
        english = [i for i, x in enumerate(typing) if x is not None]
        target = list(windows)
        if english:
            target[english[-1]] += extra
        new, hold = shares(target, typing)
        if any(t is not None for t in typing) and hold < min_hold:
            raise ValueError(
                f"list {list_no}: run of boxes {[o['box'] for o, _ in run]} "
                f"holds {hold} frames, below {min_hold}"
            )
        shift = 0
        for (o, cue), w, w2, t in zip(run, windows, new, typing, strict=True):
            shift += w2 - w
            at = pointer + 2 * cue
            old = _u16(bytes(end), at)
            if shift:
                end[at - BASE : at - BASE + 2] = (old + shift).to_bytes(2, "big")
                out.changes.append(
                    {
                        "file": "END.BIN",
                        "start": at - BASE,
                        "end": at - BASE + 2,
                        "what": f"cue {cue}",
                    }
                )
            out.boxes.append(
                {
                    "box": o["box"],
                    "cue": cue,
                    "cue_frames": [old, old + shift],
                    "window": [w, w2],
                    "typing": t,
                    "hold": None if t is None else w2 - t,
                }
            )
        if shift != (extra if english else 0):
            raise ValueError(f"list {list_no}: run's last cue moved by {shift}")
        if shift:
            out.boxes[-1]["absorbs"] = shift
            absorbed.add(following)
    # 3. A difference no run absorbed: slower typing, up to MAX_INTERVAL.
    for index, entry in zip(wait_index, out.waits, strict=True):
        if index in absorbed or not delta.get(index):
            continue
        _, box, kind, _, waits = ends[index]
        original = entry["interval"][0]
        if kind == "wait":
            interval, new_waits = interval_and_wait(
                [v for _, v in waits],
                japanese_cells[box],
                cells[box],
                original,
                MAX_INTERVAL,
            )
            for (wait_at, _), v in zip(waits, new_waits, strict=True):
                put(wait_at, 0xE300 | v, f"box {box} wait")
            entry["wait"][1] = new_waits
            entry["english_frames"] = cells[box] * interval + sum(new_waits)
        else:
            interval = segment_interval(
                japanese_cells[box], cells[box], original, MAX_INTERVAL
            )
            entry["english_frames"] = cells[box] * interval
        put(typing_at[index], 0xE200 | interval, f"box {box} typing")
        entry["interval"][1] = interval
        entry["slowed"] = True
    return out
