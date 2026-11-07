# Making a Release

Adapted from XvSF's `release/RELEASING.md` (itself from MSHvSF's, commit
`7d4c587`) for Cyberbots (`REL-003`). The examples use `0.1.0`.

The agent does steps 1-6. You do steps 7-9 on github.com, because `gh` on
this machine is signed in as the work account, which this project never uses.

## Before You Start

- [ ] Every open task in `TASKS.md` is done, or you have deferred it.
- [ ] The release image has been played (Mednafen, or real hardware).
- [ ] `git status` is clean, on `main`, and up to date with `origin/main`.
- [ ] `git config user.email` prints
      `13876322+princeendo@users.noreply.github.com`.
- [ ] The local files the top-level `README.md` lists are in place, and
      `xdelta3 -V` reports 3.2.2.

## 1. Rebuild and Check

```bash
./invenv.sh python research/experiments/EXP-0055/regress.py re003_jin re007_jin_santana \
  re008_roster end010_jin_ending end011_jin_timing end023_roster_endings boot004_boot_warnings \
  loc005_name_art opt006_names_switch ui007_ui_text special018_saturn_only
```

Every reference must match. The release image lands in
`build/regress/special018_saturn_only/image/`.

## 2. The Patch and Its Record

The command is in [`README.md`](README.md), "Rebuild the Patch", step 2.
Run it twice (two `--out-dir`s) and compare the patches with `cmp`. The
`--record` file in `release/` is committed; the zip and docs are checked
against it.

## 3. The Zip, Twice, and the Check

```bash
V="English translation (all pilots, endings, UI; NAMES and SIGNS settings)"
./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0 --kinds xdelta \
  --patches build/release --variant cyberbots_en patch "$V"
./invenv.sh python -m tools.release.make_zips 0.1.0 build/release/v0.1.0-again --kinds xdelta \
  --patches build/release --variant cyberbots_en patch "$V"
shasum -a 256 build/release/v0.1.0/*.zip build/release/v0.1.0-again/*.zip
./invenv.sh python -m tools.release.check_zips 0.1.0 build/release/v0.1.0 local/rel/v0.1.0-check \
  --kinds xdelta --expect f6789cae74814ab82d8060db3b50a99906b668bacfe950d1e0850ac4d01d25e0
```

Both builds must hash the same, and the patch from the unpacked zip must
give the reference track 01. There is no `.ssp` (`REL-002`: the image adds
files to track 01).

## 4. The Notes

`release/notes_v0.1.0.md`: what changed, the zip with its size and SHA-256,
how to apply, known limits.

## 5. Records

- `TASKS.md`: the `REL-` task with the zip hash.
- `research_log.md`: the session.

Stage only the files above: never the zip, the patch or images (`AGENTS.md`
rule 21).

## 6. Commit, Tag, Push

```bash
git -c user.name=Colin -c user.email=13876322+princeendo@users.noreply.github.com commit ...
git tag -a v0.1.0 -m "Cyberbots: Fullmetal Madness (Saturn) English 0.1.0"
git push origin main v0.1.0
```

## 7-9. Publish (You, on github.com)

| Do this | What you should see |
| --- | --- |
| Open the repository's Releases page, "Draft a new release", choose the tag `v0.1.0`. | The tag is listed. |
| Title "0.1.0", paste `release/notes_v0.1.0.md` as the description. | The notes render. |
| Drag in `build/release/v0.1.0/cyberbots_saturn_en_0.1.0_xdelta.zip`, then publish. | The file listed under the description. |

Afterwards the agent checks the asset's size and `sha256:` digest through
the public API against the zip built in step 3, and links the release from
the top-level README.
