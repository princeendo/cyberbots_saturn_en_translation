# EXP-0071: Rendered Samples for the UI Gate (UI-005)

Task: UI-005
Status: DONE
Confidence: CONFIRMED (each sample is what the game drew with the stated RAM
or VRAM change, from saved states); the samples are drafts for a decision,
not builds

## Observation

`UI-005` asks the user, with rendered samples beside both arcades, what the
two remaining Japanese surfaces become: the VS captions (D-060) and the
ruined-city signs (D-061). Neither has official English.

## Hypothesis

Each option can be shown on the Saturn with RAM or VRAM changes alone: an
English caption as pair glyphs in the story font, no caption by making the
reader return, and blank or English signs by editing the NBG2 sign blocks.

## Controlled Change

None to the disc. Per sample, one set of RAM or VRAM writes after loading a
saved state (load and pause in one agent exchange, `EXP-0070`).

## Prediction

The samples draw as intended, with nothing else changed: the caption in the
banner, no banner, blank signs, lettered signs.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Caption state | `local/ref005/session/states/f00006448.mcs` (before a VS screen; untouched image's RAM, so the names are katakana) |
| Sign state | `local/ui002/s2/signs.mcs` and its NBG2 block map (`EXP-0070`) |
| Arcade letters | `local/layout001/font/arcade_font.json` (`LAYOUT-001`), the story's pair-glyph source |
| `FIX.BIN` | small capitals for the facade sign |
| Arcade shots | `EXP-0069` (VS, both sets) and `EXP-0070` (frame 1500, both sets) |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`samples.py`](samples.py) → [`samples.json`](samples.json) | Nine Saturn samples and three offline store renders |
| ffmpeg | Two comparison sheets (local only) |

## Procedure

```bash
./invenv.sh python research/experiments/EXP-0071/samples.py local/ui005/samples   # about 2 min, no key
# sheets: local/ui005/captions_samples.png (both arcades' VS screens, then the Saturn
# samples) and local/ui005/signs_samples.png (both arcades' store front, then the
# Saturn store as now, blank, English), composed with ffmpeg hstack/xstack.
```

2026-11-06, 21:50-22:30 local. No cold boot, no keys.

## Actual Result

- **Captions** (box 496, and box 500 for a longer line): English draft text
  as pair glyphs in 13 cells fits the banner, centred or left-aligned, in
  the Japanese caption's colours. With the reader returning at once, the VS
  screen shows no banner, as the US arcade does.
- **Signs:** blanking the writing colours inside each sign leaves plain
  banners and a plain facade sign (a few pixels of the facade sign's left
  end, in its second palette, are left: a sample limit). Stacked arcade
  capitals (`SALE`, `BAZAAR`) fit the banners; `BARGAIN SALE` in small
  capitals fits the facade sign along its slope.
- Seen while making the samples: a tiny red-marked sign on the stair column
  left of the store (NBG2), too small to read; not in the arcade's region
  difference (`EXP-0070`).
- The sheets went to the user, who decided (verbatim in
  `docs/localization_policy.md`, "UI Text and Art, Decided"): translate the
  54 captions (drafts approved, centred), pilots 6-8 with `SPECIAL-001`, a
  `SIGNS` setting in `EXTRA OPTIONS` (`BLANK` default, `ENGLISH`,
  `JAPANESE`, saved, a tail file), changes under both `NAMES` settings.

## Conclusion

Every option was shown on the Saturn beside both arcades, and the user
chose. The approved data are `data/translations/vs_captions.json` and
`data/translations/signs_switch.json`.

## Uncertainty and Alternatives

- The caption samples used glyph slots and codes freely; whether 54
  captions' pairs fit the font's free codes is measured in `UI-006`.
- The sign samples' blanking and lettering are rough; `UI-006` draws the
  final art and the user reviews it.
