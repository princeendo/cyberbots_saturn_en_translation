# EXP-0002: Cartridge Controls for Boot and Attract

Task: EMU-004
Status: DONE
Confidence: CONFIRMED (boot and attract only)

## Observation

With `ss.cart auto`, Mednafen gives the game the 1 MiB extended-RAM cart
(D-001), as its database lists `T-1217G` as `CART_EXTRAM_1M` with no
"Game requirement" note (`docs/mednafen.md`). Both sibling games needed the
4 MiB cart and stopped on a warning without it. The header's peripheral field
reads `JW`.

## Hypothesis

The cartridge changes nothing the game shows in a no-input boot and attract
run: with no cart, a save cart, or either extended-RAM cart, it reaches the
title and attract mode without a warning. Prediction for the control:
`extram1` gives frames byte-identical to D-001.

## Controlled Change

One variable per run: the cart type, passed as `-ss.cart VALUE` on the
command line (`cold_boot.py --setting ss.cart=VALUE`). Everything else as in
`EXP-0001`: untouched image, silent home, empty `sav/`, 120 s, no input. The
user was present ("Yes, run EMU-004", 2026-11-02). After each run,
`tools.mednafen.home` restored the configuration, because Mednafen saves the
setting on exit.

Mednafen 1.32.1's `ss.cart` values (`Documentation/ss.html`): `auto`, `none`,
`backup` (Backup Memory, 512 KiB), `extram1`, `extram4`, `cs1ram16`. `backup`
was added to the agreed three because a save cart is a common real-hardware
setup.

## Prediction

- `extram1`: 119 of 119 frames equal to D-001 (`EXP-0001` boot 1).
- `none`, `backup`, `extram4`: **UNKNOWN**; either the same sequence, a
  warning screen as in the sibling games, or some other difference.

## Inputs and Provenance

As `EXP-0001`: source `local/disc_images/cyberbots_saturn_jp_2m/` (63
components), BIOS `sega_101.bin` (`dcfef4b9…deac`), stock binary
`077ac658…669f`, home `local/mednafen_quiet/` (config `ef897288…5019`).

## Tools and Environment

macOS 26.7.2, Darwin 25.6.0 arm64; ffmpeg 9.0.1; `tools/mednafen/cold_boot.py`
and `tools/mednafen/home.py` (both re-validated on Cyberbots, `EXP-0001`,
`EMU-002`).

## Procedure

```bash
D=local/disc_images/cyberbots_saturn_jp_2m
CUE="$D/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python -m tools.disc.hash_source --json $D/* > local/emu004/source-before.json
for c in extram1 none backup extram4; do
  rm -f local/mednafen_quiet/sav/*
  ./invenv.sh python -m tools.mednafen.cold_boot "$CUE" local/emu004/$c \
    --seconds 120 --setting ss.cart=$c
  ./invenv.sh python -m tools.mednafen.home
  shasum -a 256 local/mednafen_quiet/mednafen.cfg
done
./invenv.sh python -m tools.disc.hash_source --json $D/* > local/emu004/source-after.json
cmp local/emu004/source-before.json local/emu004/source-after.json
```

Frames were compared with `EXP-0001` boot 1 by the SHA-256 in each
`run.json`; each differing frame was also looked up among all D-001 frames to
tell a time shift from new content.

## Actual Result

| Cart | Start (UTC) | Exit | Log line | Log SHA-256 | Frames equal to D-001 |
| --- | --- | ---: | --- | --- | ---: |
| `extram1` | 2026-11-02 20:04:32 | 0 | `Cart: 1MiB Extended RAM` | `0b540762…a5b0` | 119 of 119 |
| `none` | 2026-11-02 20:06:47 | 0 | `Cart: None` | `975f6ffd…8f34` | 97 of 119 |
| `backup` | 2026-11-02 20:09:02 | 0 | `Cart: Backup Memory` | `c74a0d7c…8b61` | 78 of 119 |
| `extram4` | 2026-11-02 20:11:17 | 0 | `Cart: 4MiB Extended RAM` | `437afa93…589b` | 119 of 119 |

- Each log differs from D-001's only in the `Cart:` line (and the output file
  name).
- **`extram1` and `extram4`:** every frame equals D-001.
- **`none`:** frames 001-087 equal D-001, including the title (058, 064).
  From 088 the attract fight starts about one second earlier (088 is its
  fade-in, 089 `PHASE 1`, against D-001's 089 black and 090 `PHASE 1`); the
  later `NOW LOADING` and `RANKING` frames shift likewise.
- **`backup`:** the same sequence with small shifts: frame 028 is still
  `NOW LOADING` (D-001: the intro has begun), 061 already shows
  `PRESS START BUTTON` (D-001: from 062), 071 equals D-001's 046; the title
  frames 058 and 064 equal D-001. From 088 the attract fight is shifted as
  with `none`.
- No run shows a warning, error or Japanese text. The agent reviewed the
  contact sheets of `none` and `backup` (every second).
- Every run restored the quiet config to `ef897288…5019`; the 63 source
  components are unchanged (`cmp` of the manifests).

## Conclusion

**CONFIRMED for boot and attract:** the game needs no cartridge to reach the
title and play its attract loop; no cart and a save cart give the same screens
with timing shifts of about one second, and the 1 MiB and 4 MiB extended-RAM
carts give byte-identical frames. `ss.cart auto` (1 MiB) stays the project
setting: it equals D-001's evidence and Mednafen's database entry.

## Uncertainty and Alternatives

- Only a no-input boot and attract were tested. A cart check could still come
  at Start, at a mode select, or when a fight or story scene loads; with no
  cart, loading may be slower or some data may be loaded differently in play.
  Re-check if a play session with another cart ever matters (for example a
  real-hardware report).
- The earlier attract fight with no cart, and the later intro with a save
  cart, suggest the game uses the cart for something during loading (a cache
  in extended RAM, or a save-memory check), but nothing here shows what.
- `backup` and `none` were run once each; their shifts were not checked for
  repeatability.
- What the header's `W` peripheral code means is not established by this.

## Reproduction

Run the procedure above from the repository root, with the user present.
Evidence stays in the ignored `local/emu004/` (`<cart>/run.json`,
`mednafen.log`, `frames/`, `sheet-*.png`; source manifests).
