# EXP-0063: Where the Katakana Name Art Can Live, and Where It Goes In

Task: OPT-002
Status: DONE
Confidence: CONFIRMED (sizes, disc and directory room, load sites, exact-
size loads, a file read from the Track 01 tail, on Mednafen); SUPPORTED
(versus mode uses the same load sites: static, one reference per name)

## Observation

- D-052: neither `SELECT.VAD` nor `PL3F_0.BIN` has room for both name-art
  sets. The Latin build (D-053) replaces the katakana in four ranges.
- D-017: the game loads files through its own copy of the ISO directory.

## Hypothesis

The katakana can be kept as small extra files on the disc and loaded over
the Latin ranges right after the game loads each file, at one load site per
screen.

## Controlled Change

None to the game for the traces. One test image: the untouched image with a
copy of `M3CB00A.BIN` in Track 01's last 150 sectors, and the game's RAM
directory entry for it pointed there.

## Prediction

The tail sectors are free and readable; the directory and the game's table
have room for a record; each name-art file is loaded at one site; a load
writes exactly the file's size; the game loads the tail copy byte for byte.

## Inputs and Provenance

| Input | Notes |
| --- | --- |
| Untouched image | `local/disc_images/cyberbots_saturn_jp_2m/` |
| `references/saturn_jp/iso_listing.json` | file extents |
| `build/loc005/a/name_art_changes.json` | the Latin ranges |
| Session states | 1646, 2538 (before the pilot select), 3070, 6448 (before the VS screen), 27173 |
| WRAM-H at 27173 | `EXP-0062` dump, for code reading |

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`trace_loads.py`](trace_loads.py) | Requests through `0x06032E38` (none at these screens) |
| [`probe.py`](probe.py) | `loads`, `stack`, `tailimage`, `tail`, `slack` (see its docstring) |
| `tools/sh2/disasm.py` | The select setup, the VS load, the directory structure |
| `tools/disc/patch_image.replace_files` | Writes the tail sectors (EDC/ECC regenerated) |

## Procedure

```bash
P=research/experiments/EXP-0063/probe.py; ST=local/ref005/session/states; E=research/experiments/EXP-0063
./invenv.sh python $P loads local/opt002/p-sel $ST/f00002538.mcs 480   # -> loads_select.json
./invenv.sh python $P loads local/opt002/p-vs $ST/f00006448.mcs 420    # -> loads_vs.json
./invenv.sh python $P stack local/opt002/p-stack $ST/f00002538.mcs 0607CA18-0607CA1B  # -> stg0a_stack.json
./invenv.sh python $P slack local/opt002/p-slack $ST/f00006448.mcs
./invenv.sh python $P tailimage build/opt002/tail/image
./invenv.sh python $P tail local/opt002/t-ctl "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue"
./invenv.sh python $P tail local/opt002/t-tail "build/opt002/tail/image/Cyberbots - Fullmetal Madness (Japan) (2M).cue" --move
```

2026-11-06, 12:30-13:20 local. No key, no cold boot. The test image
(Track 01 `c4dc04ef…1189`) was deleted after the run.

## Actual Result

### Size

The katakana set is the untouched bytes of the four Latin ranges: 30,838
bytes (`SELECT.VAD` `0x17840`-`0x19A00`, 8,640; `STG0A.BIN`
`0x1CA1A`-`0x1CA92`, 120; `PL3F_0.BIN` `0x90`-`0x1FE`, 366, and
`0x42EC`-`0x97BC`, 21,712). As loadable pieces (4-byte aligned): the
select block (8,640 bytes, 5 sectors), `PL3F_0.BIN` `0x90`-`0x97BC` in one
piece (38,700 bytes, 19 sectors; the bytes between the two ranges are the
same in both builds) and the part table `0x1CA18`-`0x1CA94` (124 bytes).

### Room on the disc

- Track 01's files are packed with no gaps; the last (`QSD.PIX`) ends at
  LSN 43,643. **Sectors 43,643-43,792 (150, 307,200 bytes) are valid,
  zero-filled Mode 1 sectors** inside Track 01, before Track 02.
- **Slack** in every file loaded at these screens (`STG0A.BIN` 1,172,
  `ST0A_FNT.BIN` 1,792, `SELECT.VAD` 1,440, `PL14_0.BIN` 0, `PL14_1.BIN`
  912, `STG0AS.BIN` 812, `PL3F_0.BIN` 288, `M3CB00A.BIN` 800, `CYBER.BIN`
  400): 7,616 bytes in all, scattered; too little.
- **Full alternate files** (`SELECT.VAD` 186 sectors, `PL3F_0.BIN` 163) do
  not fit in the 150-sector tail.

### Directory

- The root directory (LSN 20-27, 16,384 bytes) has room: its last sector
  holds 11 records, ending with `WARNING4.PIX`, and 1,532 free bytes.
- The game copies it at start-up into a table described at `0x060DCB5C`:
  type 1, **maximum 0x180 (384) entries**, table `0x060DCB68` (`.`, `..`,
  then 325 files; 24 bytes each: FAD, size, flags, name). 327 are used, 57
  spare.
- Files are found **by name**: a binary search compares names
  (`0x0603B564`, from `0x060410EA`), and a file's request number is its
  table index (`VICTORY.BIN` 320 = `0x140`). A new name that sorts after
  `WARNING4.PIX` keeps every existing number.

### Load sites (`loads_select.json`, `loads_vs.json`, `stg0a_stack.json`)

- **Loader** `0x060385A0`(r4 name, r5 destination, r6 maximum): opens by
  name (`0x06038E40`) and polls `0x06038E9C` until done.
- **Pilot select** (`0x06038C8C`, in `CYBER.BIN`, called from
  `0x06017662`): `0x060388FA`(10) loads the overlay `STG0A.BIN` to
  `0x06060000` (seen by a write watch on its part table, frame 27 of state
  2538, return chain `0x06038C9E` ← `0x06017662`); then `ST0A_FNT.BIN`;
  **`SELECT.VAD` → VDP1 VRAM `0x20000` (`0x25C20000`, at `0x06038CD6`)**;
  then `PL14_0/1.BIN`.
- **VS screen** (`STG0AS.BIN` overlay code): `0x06038E40`(`PL3F_0.BIN`,
  `0x20200000`, `0x80000`) at `0x060605B6`, then a wait loop to
  `0x060605C2`.
- **Every reference:** the strings `SELECT.VAD` and `STG0A.BIN` occur once
  on the disc (`CYBER.BIN`), `PL3F_` once (`STG0AS.BIN` `0xEA64`, one
  pointer), so versus mode and `SET UP` use these same sites (SUPPORTED;
  no versus state was traced).
- **Exact size:** `0xAA` written over the 288 bytes after `PL3F_0.BIN`'s
  end in RAM survived its load (304 of 304), so a load writes only the
  file's bytes.

### A file in the tail (`tail_load.json`)

With `M3CB00A.BIN` copied to LSN 43,643 and its RAM directory entry's FAD
changed to 43,793, the VS screen's load of it gave RAM equal to the file
(37 of 37 sectors by frame 441; the control's own load at the usual place
reached 36 of 37 by then) and the same screenshot as the control.

## Conclusion

Prediction met. The katakana can be kept in new small files in Track 01's
tail and loaded over the Latin ranges at two sites (after `0x06038CD6` for
the select art and part table, after `0x060605C2` for the VS records). The
options for `OPT-004`:

| Option | Disc | RAM | Code | Risk |
| --- | --- | --- | --- | --- |
| **A. Small files in the tail, loaded per screen** (recommended) | 2-3 new files, 24-25 of the 150 tail sectors; 2-3 directory records | none extra | two hooks (load if the setting is set), about 40 bytes each, in space `OPT-003` proves | Directory editing is new tool work; one extra load (5 or 19 sectors) in katakana mode; real hardware untested |
| B. One file loaded once into RAM, copied per screen | as A | about 31 KB of proven free RAM | a boot load and two copies | needs a large free RAM range (`OPT-003`) |
| C. Longer Track 01 with full alternate files | Track 01 grows by more than 200 sectors | none | a name swap at each site | every audio track moves (cue, TOC, the ISO's CD-DA entries); the patch is no longer Track 01 only |
| D. Existing slack | 7,616 bytes | — | — | does not fit |

## Uncertainty and Alternatives

- Real hardware reading the tail sectors was not tested (Mednafen only).
- Versus mode's loads were not traced (static evidence only).
- Whether the game modifies the loaded name ranges before the switch's load
  would land was not checked (the hook runs right after each load).

## Reproduction

Run the procedure. Expect the committed JSON files.
