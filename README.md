# Cyberbots: Fullmetal Madness (Saturn): English Translation

This repository will build an English patch for the Japanese Sega Saturn
release of **Cyberbots: Fullmetal Madness** (Capcom, 1997, T-1217G). Wherever
an official English text exists, the patch is meant to use it: the arcade
release's English. Where none exists, it will use a new translation, marked as
such. The full policy, as the user decided it, is in
[docs/localization_policy.md](docs/localization_policy.md).

The repository holds the tools, the translation data, and the expected hashes.
It holds no game data. How the work is done is recorded in
[TASKS.md](TASKS.md), [research_log.md](research_log.md), and
`research/experiments/`.

It follows the method of two sibling projects that shipped Saturn English
patches: Marvel Super Heroes vs. Street Fighter and X-Men vs. Street Fighter.
See [docs/playbook_from_mshvsf.md](docs/playbook_from_mshvsf.md) and
[docs/lessons_from_xvsf.md](docs/lessons_from_xvsf.md).

## Download

Nothing is released yet (`REL-001`). Work in progress is tracked in "Current
State" in [TASKS.md](TASKS.md).

## What's Changed

In the current development build (not released):

- **Story dialogue** of the six arcade pilots (Jin, Santana, Mary, Arieta,
  Gawaine, Bao and Mao) and their **versus win quotes**: the official US
  arcade English (M5).
- **Endings** of those six pilots: the official US arcade English, with
  the cast roll's Japanese names hidden and the QSound notice's Japanese
  line removed (M8).
- **Boot warnings** (damaged save, unformatted memory, no room to save): a
  new translation, approved by the user, in the arcade's letters
  (`UI-004`).
- **Pilot and mech names** on the pilot-select, `SET UP` and VS screens:
  Latin art in the arcade's letters, spelled as the US arcade (Devilotte
  for the Saturn-only princess), with each mech's model code after its name
  (`LOC-001`). A switch back to the katakana is planned (`OPT-001`).

**Still Japanese:**

- The Saturn-only pilots' stories, win quotes and endings (lists 6-8; no
  official English, `SPECIAL-001`).
- The VS screen's chapter captions (no official English shown by the US
  arcade).
- Six story-only name banners in the VS bank, in katakana or kanji, whose
  screen is not known (`LOC-006`; listed in the coverage register).
- Surfaces not yet surveyed: attract and opening text (`UI-002`), option
  sub-screens and other UI text (`UI-003`), rare or region-gated text
  (`TXT-002`). The register is
  [docs/coverage_exceptions.md](docs/coverage_exceptions.md).

## Patch Files

Not yet (`REL-001`). Releases will be xdelta and Sega Saturn Patcher (`.ssp`)
patches for track 01 of the image named in
[references/saturn_jp/README.md](references/saturn_jp/README.md), published as
GitHub Release assets only.

### Applying a Patch

Not yet (`REL-001`). The tools, the steps and the patched-track hashes will be
listed here with the first release.

## Build the Patch

There is no patch yet (`REL-001`). The current development image is built
from the untouched source, with the game data under the ignored paths below.

### Files You Need

None of these are in the repository. They go at these paths (all ignored by
git):

| File | Where it goes | What it is |
| --- | --- | --- |
| `Cyberbots - Fullmetal Madness (Japan) (2M).cue` and its 62 track `.bin` files | `local/disc_images/cyberbots_saturn_jp_2m/` | The untouched Japanese Saturn BIN/CUE (never modified). Every file must match the SHA-256 values in [references/saturn_jp/README.md](references/saturn_jp/README.md); track 01 is `758fa795…dbd1` (103,001,136 bytes). |
| `cybots.zip`, `cybotsj.zip`, `cybotsjd.zip`, `cybotsu.zip`, `cybotsud.zip`, `qsound.zip` | `local/arcade/` | MAME arcade sets. Identities in [references/arcade/README.md](references/arcade/README.md). |
| `cps2.cpp` | `local/mame_src/` | MAME's CPS-II driver source at commit `f34f02505e32c1993c6a782b6814232cbfc74e36` (SHA-256 `a8c09ef8…1602`); see [references/arcade/README.md](references/arcade/README.md). |
| `arcade_font.json` | `local/layout001/font/` | The arcade glyph capture, made with MAME by the procedure in [EXP-0025](research/experiments/EXP-0025/README.md). |
| The 264 files of track 01 | `local/extracted/saturn_jp/` | Extracted from the untouched track 01 by the second command in "Set Up". Their SHA-256 values are in [references/saturn_jp/iso_listing.json](references/saturn_jp/iso_listing.json). |

### Set Up

Python 3.12+ and [uv](https://docs.astral.sh/uv/). No runtime dependencies.

```bash
./setup_venv.sh
```

Extract the files of track 01 (the track is only read):

```bash
./invenv.sh python -m tools.disc.iso9660 "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin" --extract local/extracted/saturn_jp/
```

### Build the Release Patches

Not yet (`REL-001`). The current development image is built with:

```bash
./invenv.sh python -m tools.text.dialogue --roster data/text/m5_roster.json --indent --rank staying --max-sacrifice 160 --task END-023 --font local/layout001/font/arcade_font.json --driver local/mame_src/cps2.cpp --rompath local/arcade --out build/loc005/a --endings data/text/m8_endings.json --ending-record-dir local/loc005/rec-a --boot-warnings data/translations/boot_warnings.json --name-art data/translations/name_art.json
```

Its expected hashes are in
[data/regression/loc005_name_art.json](data/regression/loc005_name_art.json).

### Build Options

Not yet (`REL-001`). The options and the release images that use them will be
listed here.

## Development

### Further Files for Research

Not yet listed in full. The Saturn BIOS and Mednafen are described in
[docs/mednafen.md](docs/mednafen.md) and
[vendor/mednafen/README.md](vendor/mednafen/README.md).

### Python Tooling

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
- [docs/localization_policy.md](docs/localization_policy.md): the user's
  translation, naming, scope and release decisions.
- [docs/research_protocol.md](docs/research_protocol.md) and
  [research/experiments/README.md](research/experiments/README.md): how an
  experiment is run and recorded.
- [references/](references/): hashes and identity of the source image and the
  reference releases.
