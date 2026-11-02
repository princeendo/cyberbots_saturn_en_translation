"""Run stock Mednafen and press its hotkeys at fixed times (macOS).

Stock Mednafen takes screenshots and saves or loads states only through
hotkeys, and its debugger only through keys. This tool launches it, and at
each step brings the Mednafen process (by PID) to the front, checks that it is
frontmost, sends the input with System Events, and returns focus to the app
that was frontmost before (`--keep-focus` keeps Mednafen in front for the
whole run instead). If Mednafen is not frontmost nothing is sent and the run
stops, so input never reaches another app. Needs Accessibility permission for
the process that runs osascript.

A step is `SECONDS ACTION` (`--at SECONDS:ACTION`, or one per line in
`--script FILE`, `#` comments allowed). Steps run in the order given, each no
earlier than its time. Actions:

- a named key: `F5` save state, `F7` load state, `F9` screenshot, `F12` exit
  (Mednafen 1.32.1 defaults), `return`, `escape`, `period`, `comma`;
- a chord `option+X` or `shift+X` (X one character or a named key), for
  example `option+a` (frame advance), `option+d` (debugger), `option+3`
  (memory editor), `shift+w` (write breakpoints). Option chords are posted as
  left-Option keyboard events, which the debugger's view switch requires;
- a single character, for example `d`;
- `window=FILE`, a PNG of the Mednafen window alone (macOS `screencapture
  -l`, by window ID; needs Screen Recording permission), including the
  debugger overlay that Mednafen's own screenshots leave out;
- `type=TEXT`, typed one character at a time (`--type-delay`, default 0.05 s).

F12 is sent after the last step.

Copied into the Cyberbots repository from the XvSF repository,
``tools/mednafen/hotkeys.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import signal
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path

from tools.mednafen.cold_boot import MEDNAFEN, QUIET_HOME, sha256

# macOS virtual key codes.
KEY_CODES = {
    "F5": 96,
    "F7": 98,
    "F9": 101,
    "F12": 111,
    "return": 36,
    "escape": 53,
    "period": 47,
    "comma": 43,
}
MODIFIERS = {"option": "option down", "shift": "shift down"}
# US-layout virtual key codes for the characters used in Option chords.
CHAR_KEY_CODES = dict(
    zip(
        "asdfhgzxcvbqweryt123465",
        [*range(10), *range(11, 18), *range(18, 24)],
        strict=True,
    )
)
CHAR_KEY_CODES.update({"9": 25, "7": 26, "8": 28, "0": 29, "o": 31, "u": 32})
CHAR_KEY_CODES.update({"i": 34, "p": 35, "l": 37, "j": 38, "k": 40, "n": 45, "m": 46})
LEFT_OPTION = 58
# kCGEventFlagMaskAlternate | NX_DEVICELALTKEYMASK: Option, marked as the left key.
LEFT_OPTION_FLAGS = 0x80020
TYPE_DELAY = 0.05


def window_id(pid: int) -> int:
    """The CoreGraphics window number of process ``pid``'s main window."""
    return int(
        osascript(
            'ObjC.import("CoreGraphics");'
            "var ws = ObjC.deepUnwrap(ObjC.castRefToObject("
            "$.CGWindowListCopyWindowInfo($.kCGWindowListOptionAll, 0)));"
            f"ws = ws.filter(function(w) {{ return w.kCGWindowOwnerPID == {pid}"
            " && w.kCGWindowLayer == 0; });"
            "ws.sort(function(a, b) { return b.kCGWindowBounds.Width"
            " * b.kCGWindowBounds.Height - a.kCGWindowBounds.Width"
            " * a.kCGWindowBounds.Height; });"
            "ws.length ? ws[0].kCGWindowNumber : -1;",
            "JavaScript",
        )
    )


def capture_window(pid: int, path: Path) -> None:
    """Save only Mednafen's window (by window ID) as a PNG.

    `screencapture -l` captures that window's own pixels, so other apps'
    windows never appear even if they cover it (EXP-0004: a screen-area
    capture picked up another app's window and was deleted).
    """
    number = window_id(pid)
    if number < 0:
        raise RuntimeError(f"no window for pid {pid}")
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["screencapture", "-x", "-o", "-l", str(number), str(path)], check=True
    )


def left_option_jxa(char: str) -> str:
    """JavaScript for Automation posting Left-Option+``char`` as CGEvents.

    Mednafen's debugger view switch (Alt+1/2/3) requires SDL's left-Alt
    modifier. System Events' `using option down` was not recognized as left
    Alt (EXP-0004), so the chord is posted with the left-Option device flag.
    """
    code = CHAR_KEY_CODES[char]
    return (
        "ObjC.import('CoreGraphics');\n"
        "function post(k, down, flags) {"
        " var e = $.CGEventCreateKeyboardEvent(null, k, down);"
        " $.CGEventSetFlags(e, flags); $.CGEventPost($.kCGHIDEventTap, e);"
        " delay(0.03); }\n"
        f"post({LEFT_OPTION}, true, {LEFT_OPTION_FLAGS});\n"
        f"post({code}, true, {LEFT_OPTION_FLAGS});\n"
        f"post({code}, false, {LEFT_OPTION_FLAGS});\n"
        f"post({LEFT_OPTION}, false, 0);\n"
    )


def applescript_for(action: str, type_delay: float = TYPE_DELAY) -> str:
    """The System Events command for one action; ValueError if malformed."""
    if action in KEY_CODES:
        return f"key code {KEY_CODES[action]}"
    if action.startswith("type="):
        text = action[5:].replace("\\", "\\\\").replace('"', '\\"')
        # Paced, one character at a time.
        return (
            f'repeat with c in characters of "{text}"\n'
            f"keystroke c\ndelay {type_delay}\nend repeat"
        )
    modifier, plus, char = action.rpartition("+")
    if plus and modifier in MODIFIERS and char in KEY_CODES:
        return f"key code {KEY_CODES[char]} using {{{MODIFIERS[modifier]}}}"
    if plus and modifier == "option" and char in CHAR_KEY_CODES:
        return left_option_jxa(char)
    if plus and modifier in MODIFIERS and len(char) == 1:
        return f'keystroke "{char}" using {{{MODIFIERS[modifier]}}}'
    if not plus and len(action) == 1 and action not in '"\\':
        return f'keystroke "{action}"'
    raise ValueError(f"unknown action {action!r}")


def osascript(script: str, language: str = "AppleScript") -> str:
    result = subprocess.run(
        ["osascript", "-l", language, "-e", script], capture_output=True, text=True
    )
    if result.returncode:
        raise RuntimeError(f"osascript failed: {result.stderr.strip()}")
    return result.stdout.strip()


def frontmost_pid() -> int:
    return int(
        osascript(
            'tell application "System Events" to get unix id of first process '
            "whose frontmost is true"
        )
    )


def activate(pid: int) -> None:
    osascript(
        'tell application "System Events" to set frontmost of first process '
        f"whose unix id is {pid} to true"
    )


def press(
    pid: int, action: str, type_delay: float = TYPE_DELAY, restore: bool = True
) -> None:
    """Send ``action`` to process ``pid``; restore the previous front app."""
    if action.startswith("window="):
        capture_window(pid, Path(action[7:]))
        return
    command = applescript_for(action, type_delay)
    previous = frontmost_pid()
    for _attempt in range(3):
        if previous == pid:
            break
        activate(pid)
        time.sleep(0.3)
        if frontmost_pid() == pid:
            break
    else:
        raise RuntimeError(f"Mednafen (pid {pid}) is not frontmost; {action} not sent")
    if command.startswith("ObjC.import"):
        osascript(command, "JavaScript")
    else:
        osascript(f'tell application "System Events"\n{command}\nend tell')
    if restore and previous != pid:
        activate(previous)


def parse_step(text: str, separator: str = ":") -> tuple[float, str]:
    seconds, _, action = text.strip().partition(separator)
    try:
        if not action.startswith("window="):
            applescript_for(action)
        return float(seconds), action
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def read_script(path: Path) -> list[tuple[float, str]]:
    return [
        parse_step(line, " ")
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def run(
    image: Path,
    log: Path,
    steps: Sequence[tuple[float, str]],
    home: Path,
    mednafen: Path,
    type_delay: float = TYPE_DELAY,
    keep_focus: bool = False,
) -> dict[str, object]:
    """Run Mednafen and the steps. ``keep_focus`` leaves Mednafen frontmost
    from the first step to the exit instead of returning focus after each."""
    env = {**os.environ, "MEDNAFEN_HOME": str(home.resolve())}
    command = [str(mednafen), str(image)]
    pressed = []
    with log.open("wb") as handle:
        process = subprocess.Popen(
            command, env=env, stdout=handle, stderr=subprocess.STDOUT
        )
        started = time.time()
        previous: int | None = None
        try:
            for at, action in steps:
                time.sleep(max(0.0, started + at - time.time()))
                if previous is None:
                    previous = frontmost_pid()
                press(process.pid, action, type_delay, restore=not keep_focus)
                pressed.append({"at": round(time.time() - started, 2), "key": action})
            press(process.pid, "F12")
            pressed.append({"at": round(time.time() - started, 2), "key": "F12"})
            code = process.wait(timeout=30)
        except BaseException:
            process.send_signal(signal.SIGTERM)
            process.wait(timeout=30)
            raise
        finally:
            if keep_focus and previous is not None and previous != process.pid:
                with contextlib.suppress(RuntimeError):
                    activate(previous)
    return {
        "command": command,
        "home": str(home),
        "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
        "keep_focus": keep_focus,
        "pressed": pressed,
        "exit_code": code,
        "log_sha256": sha256(log),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("log", type=Path, help="new log file; run.json beside it")
    parser.add_argument(
        "--at", dest="steps", action="append", type=parse_step, default=[]
    )
    parser.add_argument("--script", type=Path, help="file of SECONDS ACTION lines")
    parser.add_argument("--home", type=Path, default=QUIET_HOME)
    parser.add_argument("--mednafen", type=Path, default=MEDNAFEN)
    parser.add_argument("--type-delay", type=float, default=TYPE_DELAY)
    parser.add_argument(
        "--keep-focus",
        action="store_true",
        help="keep Mednafen frontmost from the first step to the exit",
    )
    args = parser.parse_args(argv)
    if args.log.exists():
        parser.error(f"{args.log} exists")
    args.log.parent.mkdir(parents=True, exist_ok=True)
    steps = [*(read_script(args.script) if args.script else []), *args.steps]
    record = run(
        args.image,
        args.log,
        steps,
        args.home,
        args.mednafen,
        args.type_delay,
        args.keep_focus,
    )
    args.log.with_suffix(".json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
