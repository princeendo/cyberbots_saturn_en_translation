from tools.text.ending import free_lines, spans


def test_free_lines_own_then_unshown() -> None:
    box_lines = {
        1: [10, 11],  # ours
        2: [11, 12],  # posted, not ours: keeps 11 and 12
        3: [13],  # never posted: unshown room
        4: [14],  # ours, and box 5 (never posted) shares it
        5: [14, 15],
        6: [16],  # ours, shared with box 7 (ours too)
        7: [16],
    }
    own, unshown = free_lines(box_lines, posted={1, 2, 4, 6, 7}, ours={1, 4, 6, 7})
    assert own == [10, 14, 16]
    assert unshown == [13, 15]


def test_spans_merge_adjacent_aligned_lines() -> None:
    lines = [(0, 6), (8, 2), (16, 4)]  # 6+1 -> 8; 2+1 -> 4 (ends at 12)
    assert spans(lines, [0, 1, 2]) == [[0, 12], [16, 24]]
    assert spans(lines, [0, 2]) == [[0, 8], [16, 24]]


def test_erase_qsound_line_only_touches_the_line_region() -> None:
    from tools.text.ending import QSD_BACKGROUND, QSD_WIDTH, erase_qsound_line

    data = bytearray([QSD_BACKGROUND]) * (QSD_WIDTH * 256)
    data[185 * QSD_WIDTH + 120] = 7  # the line
    data[185 * QSD_WIDTH + 86] = 9  # logo edge, outside the columns
    data[179 * QSD_WIDTH + 120] = 5  # the line above, outside the rows
    out, changes = erase_qsound_line(bytes(data))
    assert out[185 * QSD_WIDTH + 120] == QSD_BACKGROUND
    assert out[185 * QSD_WIDTH + 86] == 9
    assert out[179 * QSD_WIDTH + 120] == 5
    assert [c["what"] for c in changes] == ["row 185"]


def test_hide_cast_names_zeroes_each_name_record_once() -> None:
    from tools.text import ending

    kend = bytearray(0xC000)
    kend0 = bytearray(0x200)
    kend1 = bytearray(0x400)
    header = ending.CAST_BANK_HEADER
    frames_at, parts_at = 0x100, 0x10
    kend[header + 4 : header + 8] = (ending.KEND_BASE + frames_at).to_bytes(4, "big")
    kend[header + 8 : header + 12] = (
        0x20000000 | ending.KEND_0_BASE + parts_at
    ).to_bytes(4, "big")
    for n, frame in enumerate(ending.JAPANESE_NAME_FRAMES):
        at = frames_at + 2 * (frame - 1)
        kend[at : at + 2] = n.to_bytes(2, "big")
        part = parts_at + 6 * n
        record_id = 0x10 + (n % 3)  # some frames share a record
        kend0[part + 2 : part + 4] = (0x20 | 2).to_bytes(2, "big")
        kend0[part + 4 : part + 6] = record_id.to_bytes(2, "big")
        kend1[4 * record_id : 4 * record_id + 2] = (0x2A0B).to_bytes(2, "big")
    out, changes = ending.hide_cast_names(bytes(kend), bytes(kend0), bytes(kend1))
    assert [c["start"] for c in changes] == [0x40, 0x44, 0x48]
    assert all(out[a : a + 2] == bytes(2) for a in (0x40, 0x44, 0x48))
