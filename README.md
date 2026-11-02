# Cyberbots: Fullmetal Madness (Saturn): English Translation

This repository will build an English patch for the Japanese Sega Saturn
release of **Cyberbots: Fullmetal Madness** (Capcom, 1997, T-1217G). Wherever
an official English text exists, the patch is meant to use it: the arcade
release's English. Where none exists, it will use a new translation, marked as
such. The translation policy is not settled yet (`DOC-002` in
[TASKS.md](TASKS.md)).

The repository holds the tools, the translation data, and the expected hashes.
It holds no game data. How the work is done is recorded in
[TASKS.md](TASKS.md), [research_log.md](research_log.md), and
`research/experiments/`.

It follows the method of two sibling projects that shipped Saturn English
patches: Marvel Super Heroes vs. Street Fighter and X-Men vs. Street Fighter.
See [docs/playbook_from_mshvsf.md](docs/playbook_from_mshvsf.md) and
[docs/lessons_from_xvsf.md](docs/lessons_from_xvsf.md).

## Download

Nothing is released yet. The project is at milestone M0 (environment); see
"Current State" in [TASKS.md](TASKS.md).

## What's Changed

Nothing yet.

## Patch Files

Not yet. Releases will be xdelta and Sega Saturn Patcher (`.ssp`) patches for
track 01 of the image named in
[references/saturn_jp/README.md](references/saturn_jp/README.md), published as
GitHub Release assets only.

## Build the Patch

Not yet.

## Development

### Python Tooling

Python 3.12+ and [uv](https://docs.astral.sh/uv/). No runtime dependencies.

```bash
./setup_venv.sh
```

```bash
./invenv.sh pytest -q
```

```bash
./invenv.sh ruff check .
```

```bash
./invenv.sh ruff format --check .
```

```bash
./invenv.sh mypy
```

Run every tool through `./invenv.sh python -m tools.<area>.<tool>`. Tools
copied from the sibling projects carry a provenance note and are not evidence
for Cyberbots until a task re-validates them (`AGENTS.md` rule 26).

### Local Data

Game data stays under ignored paths:

| Path | Holds |
| --- | --- |
| `local/disc_images/cyberbots_saturn_jp_2m/` | The untouched Saturn BIN/CUE (never modified) |
| `local/extracted/saturn_jp/` | Files extracted from track 01 |
| `local/arcade/` | MAME arcade sets |
| `local/logs/` | Tool output |
| `build/` | Derived images and patches |
| `vendor/mednafen/src*`, `build*` | Mednafen source and builds |

### Project Guides

- [AGENTS.md](AGENTS.md): the rules every session follows.
- [TASKS.md](TASKS.md): the dependency-controlled plan and current state.
- [research_log.md](research_log.md): chronological record, failures
  included.
- [docs/discoveries.md](docs/discoveries.md): confirmed findings only.
- [docs/known_unknowns.md](docs/known_unknowns.md): open questions and the
  experiment that would answer each.
- [docs/research_protocol.md](docs/research_protocol.md) and
  [research/experiments/README.md](research/experiments/README.md): how an
  experiment is run and recorded.
- [references/](references/): hashes and identity of the source image and the
  reference releases.
