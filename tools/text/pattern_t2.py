"""Type-2 compressed sprite patterns of the sprite-part routine (`LOC-005`).

The VS screen's name art (D-052) is stored as type-2 records in
`PL3F_0.BIN`. Read from the decoder at ``0x0601446C`` (``EXP-0060``):

- record: word 0 = type (bits 12-15, 2 here) | width / 8 (bits 8-11) |
  height (bits 0-7); word 1 = byte offset, from the end of word 1, to the
  literal stream (a multiple of 4); the control bytes start right after
  word 1;
- output: width * height / 2 bytes (4 bpp), written as 32-bit longs; the
  row length in bytes ``R = width / 2``;
- each control byte ``n`` is one operation on the output position:

  ===========  =================================================================
  0-15         copy ``n + 1`` longs from the literal stream
  16-191       copy the literal ``4 * (n - 15)`` bytes before the literal
               pointer (one long; the pointer does not move)
  192-207      write ``n - 191`` longs, each the previous halfword repeated
  208-223      copy ``n - 207`` longs from ``R`` bytes back (the row above)
  224-239      copy ``n - 223`` longs from ``R + 4`` bytes back
  240-255      copy ``n - 239`` longs from ``R - 4`` bytes back
  ===========  =================================================================

  until the output is full.
"""

from __future__ import annotations

from collections.abc import Sequence

TYPE = 2


class FormatError(ValueError):
    pass


def header(width: int, height: int) -> int:
    if width % 8 or not 8 <= width <= 120 or not 1 <= height <= 255:
        raise FormatError(f"size {width} x {height}")
    return (TYPE << 12) | ((width // 8) << 8) | height


def size_of(record: bytes) -> tuple[int, int]:
    word0 = int.from_bytes(record[0:2], "big")
    if word0 >> 12 != TYPE:
        raise FormatError(f"type {word0 >> 12}")
    return ((word0 >> 8) & 15) * 8, word0 & 0xFF


def decode(record: bytes) -> bytes:
    """The pixels (width * height / 2 bytes) of one type-2 record."""
    width, height = size_of(record)
    row = width // 2
    total = row * height
    literal = 4 + int.from_bytes(record[2:4], "big")
    control = 4
    out = bytearray()

    def take(position: int) -> bytes:
        if position < 0 or position + 4 > len(out):
            raise FormatError(f"reference to {position}")
        return bytes(out[position : position + 4])

    while len(out) < total:
        n = record[control]
        control += 1
        if n <= 15:
            out += record[literal : literal + 4 * (n + 1)]
            literal += 4 * (n + 1)
        elif n <= 191:
            back = literal - 4 * (n - 15)
            out += record[back : back + 4]
        elif n <= 207:
            half = bytes(out[-2:])
            out += half * 2 * (n - 191)
        else:
            group, count = divmod(n - 208, 16)
            distance = (row, row + 4, row - 4)[group]
            for _ in range(count + 1):
                out += take(len(out) - distance)
    if len(out) != total:
        raise FormatError(f"{len(out)} bytes for {total}")
    return bytes(out)


def encode(pixels: bytes, width: int, height: int) -> bytes:
    """A valid type-2 record for these pixels (greedy, not optimal)."""
    row = width // 2
    if len(pixels) != row * height or len(pixels) % 4:
        raise FormatError("pixel size")
    longs = [pixels[i : i + 4] for i in range(0, len(pixels), 4)]
    controls: list[int] = []
    literals: list[bytes] = []
    pending: list[bytes] = []

    def flush() -> None:
        while pending:
            chunk = pending[:16]
            del pending[:16]
            controls.append(len(chunk) - 1)
            literals.extend(chunk)

    i = 0
    while i < len(longs):
        here = 4 * i
        best_n, best_op = 0, -1
        for group, distance in enumerate((row, row + 4, row - 4)):
            if distance < 4:
                continue
            n = 0
            while (
                n < 16
                and i + n < len(longs)
                and here - distance >= 0
                and pixels[here + 4 * n - distance : here + 4 * n - distance + 4]
                == longs[i + n]
            ):
                n += 1
            if n > best_n:
                best_n, best_op = n, 208 + 16 * group + n - 1
        if here >= 2:
            half = pixels[here - 2 : here]
            n = 0
            while n < 16 and i + n < len(longs) and longs[i + n] == half * 2:
                n += 1
            if n > best_n:
                best_n, best_op = n, 191 + n
        if best_n >= 1:
            flush()
            controls.append(best_op)
            i += best_n
            continue
        recent = literals[-176:]
        if not pending and longs[i] in recent:
            k = len(recent) - max(j for j, v in enumerate(recent) if v == longs[i])
            controls.append(15 + k)
            i += 1
            continue
        pending.append(longs[i])
        i += 1
        if len(pending) == 16:
            flush()
    flush()
    body = bytes(controls)
    body += b"\0" * (-len(body) % 4)
    record = header(width, height).to_bytes(2, "big") + len(body).to_bytes(2, "big")
    record += body + b"".join(literals)
    if decode(record) != pixels:
        raise FormatError("round trip failed")
    return record


def records_of(blob: bytes, offsets: Sequence[int]) -> dict[int, bytes]:
    """Each type-2 record of ``blob`` at ``offsets``, cut to the next offset."""
    ordered = sorted(set(offsets))
    out = {}
    for k, offset in enumerate(ordered):
        end = ordered[k + 1] if k + 1 < len(ordered) else len(blob)
        out[offset] = blob[offset:end]
    return out
