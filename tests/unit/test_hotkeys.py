"""Copied into the Cyberbots repository from the XvSF repository,
``tests/unit/test_hotkeys.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from tools.mednafen.hotkeys import (
    LEFT_OPTION_FLAGS,
    applescript_for,
    parse_step,
    read_script,
)


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        ("F9", "key code 101"),
        ("return", "key code 36"),
        ("period", "key code 47"),
        ("shift+w", 'keystroke "w" using {shift down}'),
        ("shift+F9", "key code 101 using {shift down}"),
        ("d", 'keystroke "d"'),
        (
            "type=00000000 000FFFFF local/x.bin",
            'repeat with c in characters of "00000000 000FFFFF local/x.bin"\n'
            "keystroke c\ndelay 0.05\nend repeat",
        ),
        (
            'type=a"b\\c',
            'repeat with c in characters of "a\\"b\\\\c"\n'
            "keystroke c\ndelay 0.05\nend repeat",
        ),
    ],
)
def test_applescript_for(action: str, expected: str) -> None:
    assert applescript_for(action) == expected


@pytest.mark.parametrize("action", ["", "ctrl+a", "option+ab", '"', "F13", "dd"])
def test_applescript_for_rejects(action: str) -> None:
    with pytest.raises(ValueError, match="unknown action"):
        applescript_for(action)


def test_parse_step_and_script_keep_order(tmp_path: Path) -> None:
    assert parse_step("70:option+a") == (70.0, "option+a")
    with pytest.raises(argparse.ArgumentTypeError):
        parse_step("70:nope")
    script = tmp_path / "steps.txt"
    script.write_text("# freeze\n70 option+a\n\n70 type=0 1 a b.bin\n69 F9\n")
    assert read_script(script) == [
        (70.0, "option+a"),
        (70.0, "type=0 1 a b.bin"),
        (69.0, "F9"),
    ]


def test_option_chord_posts_left_option_events() -> None:
    script = applescript_for("option+3")
    assert script.startswith("ObjC.import('CoreGraphics')")
    assert f"post(58, true, {LEFT_OPTION_FLAGS});" in script
    assert f"post(20, true, {LEFT_OPTION_FLAGS});" in script
    assert f"post(20, false, {LEFT_OPTION_FLAGS});" in script
    assert script.rstrip().endswith("post(58, false, 0);")


def test_window_step_is_accepted_without_applescript() -> None:
    assert parse_step("80:window=local/x/a.png") == (80.0, "window=local/x/a.png")
    with pytest.raises(ValueError, match="unknown action"):
        applescript_for("window=local/x/a.png")
