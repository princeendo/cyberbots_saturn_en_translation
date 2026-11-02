"""Pin the project-local Mednafen homes' settings (`EMU-002`).

`local/mednafen/` is the interactive home; `local/mednafen_quiet/` is the silent
home for unattended runs (no sound, no wait for vertical sync), sharing the
interactive home's firmware. Both configurations start as the file Mednafen
generates on its first run; this tool only rewrites existing `key value` lines.

Mednafen saves command-line settings into the configuration on exit, so rerun
this tool after any run that passed settings on the command line.

`--bindings-from CFG` copies the port 1 gamepad bindings from another
Mednafen configuration (for example MSHvSF's) into both homes. Bindings are
not pinned, so later runs of this tool leave them alone.

`apply_settings` and the quiet-home layout are adapted from MSHvSF
`tools/mednafen/replay_state.py` `quiet_home()` at commit `69c666c`. The
settings are parameters, not MSHvSF facts; each value is recorded in
`docs/mednafen.md`.

Copied into the Cyberbots repository from the XvSF repository,
``tools/mednafen/home.py``
at commit ``a1c82ba`` (``ENV-003``). Notes above about MSHvSF or XvSF are
their history; for Cyberbots they are at most a HYPOTHESIS until
re-validated.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from pathlib import Path

HOME = Path("local/mednafen")
QUIET_HOME = Path("local/mednafen_quiet")

PROJECT_SETTINGS = {
    "filesys.path_firmware": "firmware",
    "filesys.path_sav": "sav",
    "filesys.path_savbackup": "b",
    "filesys.path_state": "mcs",
    "filesys.path_snap": "snaps",
    "filesys.path_movie": "mcm",
    "filesys.path_pgconfig": "pgconfig",
    "filesys.path_cheat": "cheats",
    "filesys.fname_state": "%f.%M%X",
    "filesys.fname_snap": "%f-%p.%x",
    "autosave": "0",
    "debugger.autostepmode": "0",
    "ss.bios_jp": "sega_101.bin",
    "ss.bios_na_eu": "mpr-17933.bin",
    "ss.bios_sanity": "1",
    "ss.cart": "auto",
    "ss.region_autodetect": "1",
}

PAD_PREFIX = "ss.input.port1.gamepad."

QUIET_SETTINGS = {
    "sound.volume": "0",
    "video.glvsync": "0",
    "video.blit_timesync": "0",
}


def apply_settings(config: Path, settings: Mapping[str, str]) -> list[str]:
    """Rewrite each setting's existing line; return the keys that changed.

    Raises KeyError if a key has no line, so a typo never passes silently.
    """
    # Split on newlines only: values may hold bytes that ``splitlines`` treats
    # as line breaks in latin-1 (0x85, 0x1C-0x1E).
    lines = config.read_bytes().split(b"\n")
    found: set[str] = set()
    changed: list[str] = []
    for index, line in enumerate(lines):
        key = line.split(b" ", 1)[0].decode("latin-1")
        if key in settings:
            found.add(key)
            new = f"{key} {settings[key]}".encode()
            if line != new:
                changed.append(key)
                lines[index] = new
    if missing := sorted(set(settings) - found):
        raise KeyError(f"settings not in {config}: {', '.join(missing)}")
    config.write_bytes(b"\n".join(lines))
    return changed


def configure(home: Path = HOME, quiet: Path = QUIET_HOME) -> dict[str, list[str]]:
    """Pin both homes; create the quiet home from the interactive one if missing."""
    changed = {str(home): apply_settings(home / "mednafen.cfg", PROJECT_SETTINGS)}
    quiet_config = quiet / "mednafen.cfg"
    if not quiet_config.exists():
        quiet.mkdir(parents=True, exist_ok=True)
        quiet_config.write_bytes((home / "mednafen.cfg").read_bytes())
    changed[str(quiet)] = apply_settings(
        quiet_config, {**PROJECT_SETTINGS, **QUIET_SETTINGS}
    )
    firmware = quiet / "firmware"
    if not firmware.exists():
        firmware.symlink_to(Path("..") / home.name / "firmware")
    return changed


def read_settings(config: Path, prefix: str) -> dict[str, str]:
    """Return every `key value` line of ``config`` whose key starts with ``prefix``."""
    settings = {}
    for line in config.read_bytes().split(b"\n"):
        key, _, value = line.decode("latin-1").partition(" ")
        if key.startswith(prefix):
            settings[key] = value
    return settings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=HOME)
    parser.add_argument("--quiet-home", type=Path, default=QUIET_HOME)
    parser.add_argument(
        "--bindings-from",
        type=Path,
        help=f"copy every {PAD_PREFIX}* line from this mednafen.cfg to both homes",
    )
    args = parser.parse_args(argv)
    changed = configure(args.home, args.quiet_home)
    if args.bindings_from:
        bindings = read_settings(args.bindings_from, PAD_PREFIX)
        if not bindings:
            parser.error(f"no {PAD_PREFIX}* lines in {args.bindings_from}")
        for home in (args.home, args.quiet_home):
            changed[str(home)] += apply_settings(home / "mednafen.cfg", bindings)
    for path, keys in changed.items():
        print(f"{path}: {', '.join(keys) if keys else 'no change'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
