# Cyberbots Arcade (CPS-II): Reference Sets

Translation oracle and reference only (`AGENTS.md` rule 15). Never commit ROM
data or anything decoded from it; commit hashes, set names, offsets and
counts.

## Intake (`REF-001`, 2026-11-02)

The user supplied five MAME-style zips in `~/Downloads/cyberbots/`. They were
copied unchanged (APFS clones) into the ignored `local/arcade/`, together with
`qsound.zip` from the user's MSHvSF download (`~/Downloads/mshvsf/qsound.zip`,
the same file as MSHvSF's `local/arcade_roms/mshvsf/qsound.zip`). MAME needs
it for the shared `dl-1425.bin` QSound program; without it every set fails
verification on that one file.

| File | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `cybots.zip` | 20181433 | `5820114c3824c38feaf04287ab36dbbc941929845a926dcbe82ffb8b0a33587c` |
| `cybotsj.zip` | 627060 | `08fd2473211e5fa9497c65a329b147247c1d0f26ca360bcacbfef1982d1165a5` |
| `cybotsjd.zip` | 322000 | `c32eea487b6dc2c4cac496ff80de3363bd29ce65f475d89dea2ca88e8c006320` |
| `cybotsu.zip` | 627065 | `db4d252b0da88b4648b832912306ac137fa28f246316f74ab9b7b8ab0a612dd6` |
| `cybotsud.zip` | 324683 | `97c4931a7a3d15447e1960d404a893c3fa303f77104a0328ff2bbf4d999e980a` |
| `qsound.zip` | 2676 | `55feb9b70dacb7364f0310ed16cc9281b5b0a31318b9e2e0587ae06d15f95356` |

## Identity Against MAME 0.289

MAME 0.289 from Homebrew (`/opt/homebrew/bin/mame`, `mame -version` prints
`0.289 (unknown)`). Command, per set:
`mame -rompath local/arcade -verifyroms SET`. Every set: `1 romsets found,
1 were OK.` Descriptions are from `mame -listxml`.

| Set | Parent | MAME description | Program ROMs |
| --- | --- | --- | --- |
| `cybots` | — | Cyberbots: Fullmetal Madness (Europe 950424) | `cybe.03`, `cybe.04`; shared graphics, sound and QSound ROMs |
| `cybotsu` | `cybots` | Cyberbots: Fullmetal Madness (USA 950424) | `cybu.03`, `cybu.04`, `cybotsu.key` |
| `cybotsj` | `cybots` | Cyberbots: Fullmetal Madness (Japan 950420) | `cybj.03`, `cybj.04`, `cybotsj.key` |
| `cybotsud` | `cybots` | Cyberbots: Fullmetal Madness (USA 950424 Phoenix Edition) (bootleg) | `cybu_d.03`, `cybu_d.04` (decrypted) |
| `cybotsjd` | `cybots` | Cyberbots: Fullmetal Madness (Japan 950424) (decrypted bootleg) | `cybj_d.03`, `cybj_d.04` (decrypted) |

Notes:

- The two decrypted bootlegs give readable 68000 program images without a
  decryption step. Their relation to the encrypted originals (same code,
  decrypted) is a **HYPOTHESIS** until compared (`REF-003`). Note that
  `cybotsjd` is dated 950424, the Japanese original 950420.
- The supplied `FBNeo 1.0.0.2 ROMs (split).zip` holds only FBNeo DAT files
  (`arcade.dat` lists the same five sets and CRCs as MAME). Zip SHA-256
  `e99f582fc78263663d4ff63e0e0b66ef947167cc0c326ab847ad83cc4904bfc9`. It is
  not copied; MAME is the pinned reference.
- Identity by SHA-1 (`REF-001`, 2026-11-02): `mame -listxml 'cybots*'`
  (MAME 0.289) saved as the ignored `local/logs/ref001-listxml.xml`, SHA-256
  `7a8c40be9058064ccedf2b14652fa2d8be8fa097febf97a976b154fd2b4bc669`;
  `tools/reference/listxml_match.py` matches every member of every zip, none
  unmatched, each zip to the set of its name ([`manifest.json`](manifest.json),
  per-member SHA-1).
- Driver source: `cps2.cpp` copied from MSHvSF's ignored `local/mame_src/`
  into `local/mame_src/` (SHA-256 `a8c09ef83841d75b81a4b2ee8ac029ebf8eecb6a743b016abb33e3d46e861602`,
  MAME commit `f34f02505e32c1993c6a782b6814232cbfc74e36`, as MSHvSF and XvSF
  pinned it); `tools.reference.mame_audit` matches `cybots.zip` 21 of 21. It
  matches by member name within one zip, so clone zips show the parent's
  shared ROMs as "missing"; `-verifyroms` and the SHA-1 match cover those.
- Headless boots (no input), `cybotsu` and `cybotsj`:
  `SNAP_FRAMES="1800 3000" mame SET -rompath local/arcade -autoboot_script
  tools/reference/mame_snap_frames.lua -snapshot_directory local/ref001/snap
  -cfg_directory local/mame_arcade/cfg -nvram_directory local/mame_arcade/nvram
  -skip_gameinfo -nothrottle -video none -sound none`. Both exit 0. Agent
  review: `cybotsu` frame 1800 is the attract fight with `INSERT COIN`,
  frame 3000 a white flash with `INSERT COIN`; `cybotsj` 1800 the attract
  fight, 3000 the intro. PNG SHA-256: `cybotsu_f01800` `ecb879bc…220b`,
  `cybotsu_f03000` `5a77a725…dc52`, `cybotsj_f01800` `668b04d7…8fab`,
  `cybotsj_f03000` `d0d35d7a…e1e4`.

## First Look (2026-11-02, static)

The program image `cybu_d.03` + `cybu_d.04`, concatenated and word-swapped
(CPS-II `ROM_LOAD16_WORD_SWAP`), holds a few ASCII strings: RAM test
messages, a region list (`CYBERBOTS JAPAN`, `USA`, `ASIA`, `HISPANIC`, `EURO`,
`BRAZIL`), `VS DEMO STAGE`, and `WON LOST CONTINUE ENDING`. No English
dialogue is stored as plain ASCII there; finding it is `REF-003`.
