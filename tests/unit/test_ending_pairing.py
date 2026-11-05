import pytest

from tools.text.ending_pairing import align, surface_of


def test_align_pairs_numbers_and_names_and_leaves_extras() -> None:
    boxes = [408, 605, 416, 603, 435]
    slots = [408, 614, 416, 435]
    assert align(boxes, slots) == [
        (408, 408),
        (605, 614),
        (416, 416),
        (603, None),  # a Saturn name the arcade does not open here
        (435, 435),
    ]


def test_align_keeps_an_arcade_only_slot() -> None:
    assert align([408, 410], [408, 409, 410]) == [(408, 408), (None, 409), (410, 410)]


@pytest.mark.parametrize(
    ("header", "kind"),
    [
        ("0000008c00ac000e", "dialogue box"),
        ("000000500050000e", "narration"),
        ("000000700050000e", "narration"),
        ("0030008800ac000e", "caption"),
        ("0000002800ac000e", "speaker name"),
        ("0000004c00ac000e", "speaker name"),
    ],
)
def test_surface_of_header(header: str, kind: str) -> None:
    assert surface_of(bytes.fromhex(header)) == kind


def test_surface_of_unknown_header() -> None:
    with pytest.raises(ValueError):
        surface_of(bytes.fromhex("0001000000000000"))
