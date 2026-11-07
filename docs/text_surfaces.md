# Saturn Text Surfaces

Every place the Japanese Saturn Cyberbots shows text, and whether it is
already English (`REF-005`). Built from screenshots the agent reviewed:
the cold boots and attract loop (`EXP-0001`, `EXP-0002`) and one recorded
play session (`EXP-0011`). Sample screenshots are in the ignored
`local/ref005/session/shots/` (named by frame) or `local/emu003/boot1/frames/`;
their SHA-256 is given so a sample can be re-identified.

"Arcade English" says whether the arcade (D-009, D-010) has English for the
surface.

## Seen

| Surface | When shown | Text on the Saturn | Arcade English | Sample (SHA-256) |
| --- | --- | --- | --- | --- |
| BIOS, SEGA licence, Capcom logo | Boot | English | — | `emu003/boot1/frames/010.png` |
| `NOW LOADING` | Between scenes | English | — | many |
| Intro mech schematics | Boot, attract | English part labels | Arcade attract has the same screens | `emu003/boot1/frames/045.png` |
| Title, `PRESS START BUTTON` | Boot, attract | English | — | `emu003/boot1/frames/064.png` (`e9f12474…ee24`) |
| Title menu `ARCADE MODE` / `VERSUS MODE` / `OPTION MODE` | After Start | English | — | `f00002228.png` (`ac13dfe8…aa4f`) |
| `PILOT SELECT` grid (10 portraits) | Mode start | English label; **pilot name as Japanese katakana art** under the portrait | The US arcade shows the name in Latin art (D-013) | `f00003026.png` (`41e1e675…a874`) |
| `MACHINE SELECT`, `BODY TYPE` | After pilot select | English (mech names `BLODIA`, `REPTOS`, `FORDY`, `GULDIN`) | — | `f00003264.png` (`f12cd48e…6eee`) |
| **Story dialogue boxes** | Introduction, before and after each fight | **Japanese**, typed out; Saturn script lines (D-008) | Yes for paired lines (D-011) | intro `f00004959.png` (`fbdcff49…5603`); pre-fight `f00005632.png` (`f4ef1367…a27f`); post-fight `f00013887.png` (`1c56587b…bf91`) |
| **VS screen chapter caption** | Before each fight | **Japanese** box, e.g. Saturn lines 899 and 900 | **No**: the Japanese arcade shows the same caption, the US arcade none (`EXP-0012`); the box is `0x0609CC22`[pilot × 10 + stage] (`STG0AS.BIN`), the arcade's `0x62D9A` table the same: boxes 494-549, and 1045-1071 for pilots 6-8 (`EXP-0032`); the US arcade skips the caption on its region byte, and its English slots 494-551 hold one shared non-caption record: **no official English** (D-060) | `f00006717.png` (`578caa24…565a`), `f00015684.png` (`f9868e50…cd04`) |
| **VS screen names** | Before each fight | **Pilot and mech names as Japanese katakana art** (both sides) | The US arcade shows them in Latin art (D-013) | as above |
| Fight HUD | Fights | English (`BOOST`, `POWER`, mech names, score, timer) | — | `f00008156.png` (`15f29d0a…f689`) |
| Fight banners | Fights | English (`PHASE 1`, `PROCEED`, `GO!`, `FIGHT!`, `N HIT COMBO!`) | — | many |
| Round end | After a KO | English (`TARGET DAMAGED`/`DESTROYED`, `UNIT DAMAGED`, `MISSION TERMINATED`, `1P WIN`/`LOSE`) | — | `f00012822.png` (`84bd973d…b5d6`), `f00023412.png` (`221f7fd7…3645`) |
| Bonus tally | After a win | English (`BONUS`, `ENERGY`, `TIME`, `TOTAL`, `Rank`) | — | `f00012943.png` (`f5e5b747…0057`) |
| Continue | After a loss | English (`CONTINUE?`, countdown) | — | `f00023887.png` (`3dcbfc35…4508`) |
| **Versus win quote** (`VICTORY!`) | After a versus-mode win (`VICTORY.BIN`) | **Japanese**, one dialogue-table line beside the winner's portrait; then an English `RESULT` tally | Yes: the arcade's slot N for Saturn box N (D-029, D-030); the US set shares one English record between most pairs of quotes | `local/win001/versus2/w1793751840-0070.png` (`754723dd…017f`, EXP-0031) |
| Game over, initials | After the countdown | English | — | `f00025276.png` (`88577c3e…9c4e`), `f00025813.png` (`299f26f9…db6c`) |
| `OPTION MODE` | Title menu | English (`DIFFICULTY`, `TIME LIMIT`, `SHORT CUT`, `SOUND`, `SOUND TEST`, `DATA RESET`, `KEY CONFIG`, `3M RAM MODE`, `PRESS START TO EXIT`) | — | `f00027081.png` (`02f4218a…270f`) |
| `RANKING` | Attract | English | — | `emu003/boot1/frames/118.png` |
| Stage backgrounds | Fights, attract | Japanese signage painted into the art of the ruined-city stage (the first attract demo); none seen in the other stages played or demoed (`EXP-0067`) | `cybotsj`: the same signs; **`cybotsu`: the same signs blank** (`EXP-0067`) | `local/ui001/attract/scenes/` (cold boot), `EXP-0067` |

## Jin's Ending (`EXP-0037`)

Reached by RAM writes from REF-005 state 4138 (no key pressed); samples
are in the ignored `local/end001/final-c/` (run from the checkpoint,
frames counted from it). Scenes 16-19 are `END.BIN`'s, shown by its copy of
the box routine from its record table `0x060817B4`.

| Surface | When shown | Text on the Saturn | Arcade English | Sample (SHA-256) |
| --- | --- | --- | --- | --- |
| **Ending dialogue boxes** | Scenes 16-17, after the last win | **Japanese**, typed out in a story-style box with portraits (boxes 408-413, 493, 1072) | English boxes, slots 408-413, 493 (no blank box 1072); `EXP-0040` `f09740` | `f02069.png` (`3260eff6…2a17`), `f03109.png` (`0f894470…5b60`) |
| **Ending narration** | Scene 18 | **Japanese**, typed white text on black, no box (boxes 414-415) | English, slots 414-415; `EXP-0040` `f11210` | `f03629.png` (`7242307e…dde8`) |
| **Ending captions with speaker names** | Scene 19 | **Japanese**, typed lines under a picture, each led by the speaker's name (boxes 416-422; names 601, 605) | English, slots 416-422; names `Gawaine:`/`Jin:` are slots 614/610; `EXP-0040` `f12200` | `f04409.png` (`56d90dbb…df73`), `f05189.png` (`3b44d63d…33d4`) |
| **Cast roll** | After scene 19 (`KEND*.BIN`, track 40) | **Japanese** pilot names (katakana; one title in kanji) over yellow Latin names, portraits; `CAST`, `and...`, `AS YOU.` in English | **Latin names only**; no line for the katakana (`cybotsj` shows katakana, as the Saturn); `EXP-0040` `f14340` | `f07276.png` (`b29a715b…9ee7`), `f08056.png` (`deb5723c…060d`) |
| Staff credits | Track 36 | English (`ARCADE STAFF`, `CONSUMER STAFF`) | `STAFF`, the arcade staff only | `f09096.png` (`58c55296…8d23`) |
| `THANK YOU FOR PLAYING!`, `PRODUCED BY CAPCOM` | After the credits | English | — | `f12476.png` (`e6c605e9…1c82`) |
| QSound notice (`QSD.PIX`) | After the credits | English, plus **one Japanese trademark line** (an image) | **None** in the ending; a different, all-English QSound screen in the attract loop | `f13102.png` (`d46c3202…2746`) |
| Game over, initials, ranking | Then the attract loop | English | — | `f13779.png` (`9e00cf92…cf96`), `f14829.png` (`3acbdd4b…864e`) |

Paired with the arcade (`END-005`, `EXP-0041`, D-038): every dialogue,
narration, caption and speaker-name box has official English
(`data/translations/jin_ending_pairing.json`). The cast-roll names and the
QSound line have none; the user chose to hide the names and erase the line.

Built in English (`END-010`, `EXP-0045`, D-042): the dialogue in `END.BIN`
and `SE.DAT`'s font; the cast roll's Japanese names hidden in every ending
(16 size words in `KEND_1.BIN`, D-040); the QSound line erased (`QSD.PIX`,
D-041).

How each is drawn (`EXP-0038`, D-035):

| Surface | Layer | Pixels from | To change it |
| --- | --- | --- | --- |
| Dialogue, narration, captions | VDP1 glyph cells (the story's path) | `END.BIN`'s lines and code table; glyphs from `SE.DAT`'s copy of `KANJI.BIN` (VDP2 VRAM `0x40000`) | `END.BIN`'s lines, and `SE.DAT`'s font copy as well as `KANJI.BIN` |
| Cast-roll names | VDP1, one sprite per name line | Sprite parts of bank 16 (`KEND.BIN`, `KEND_0.BIN`); images decoded by `0x0601446C` from `KEND_1.BIN` records (D-040) | Hide: a record's size word 0. New images: `KEND_1.BIN`'s pixel format (not decoded yet) |
| Credits, thank-you | VDP2 NBG0 | `FIX.BIN`, ASCII-indexed characters | Already English |
| QSound Japanese line | VDP2 NBG1 bitmap | `QSD.PIX` (raw 512×256, 256 colours) | Edit the bitmap |

## The Other Roster Endings (`END-020`, `EXP-0046`)

Lists 1-5, forced from the END-001 checkpoint on the untouched image
(D-043, `data/text/ending_surfaces.json`). All their Japanese before the
cast roll is `END.BIN` boxes, as in Jin's ending. After the dialogue every
ending shows the same cast roll, credits, thank-you screen and QSound
notice (D-035, D-040, D-041).

| List | Pilot | Scenes posted | Distinct boxes shown | Kinds of box | Pictures from |
| --- | --- | --- | --- | --- | --- |
| 1 | Santana | 16-22 | 18 | dialogue box with portraits, captions with names, narration | `STDEM1.PIR`, `STDEM7.PIR` |
| 2 | Mary | 16 (runs on through the arcade's 17-18) | 15 | dialogue box with portraits, captions with names | `STDEM2.PIR`, `STDEM7.PIR` |
| 3 | Arieta | 16-21, 27, 28 | 23 | dialogue box with portraits, captions with names, narration | `STDEM4.PIR`, `STDEM7.PIR` |
| 4 | Gawaine | 16-19 | 16 | captions with and without a name, narration | none of its own |
| 5 | Bao and Mao | 16, 17, 28, 18, 19, 21, 22 (runs on through the arcade's 20) | 22 | dialogue box with portraits, captions with names | `STDEM5.PIR` |

The arcade (`cybotsu`) shows the same kinds in English, with the Latin-only
cast roll and no QSound notice in the ending.

## Boot-Time Warnings (`BOOT-001`, D-048)

Shown once, before the title, only under the backup-memory condition given.
Each is a whole Japanese picture (`WARNINGn.PIX`) with no official English
known yet (`BOOT-003`). Screenshots: `local/boot001/<case>/w01457.png`.

| Picture | When shown | Text on the Saturn | Arcade English | Sample (SHA-256) |
| --- | --- | --- | --- | --- |
| `WARNING0` | The save fails the game's checksum | **Japanese** picture: the records could not be read | None (`BOOT-003`): a new translation, approved | `damaged/w01457.png` (`1904dbaf…`) |
| `WARNING1` | Internal backup memory unformatted | **Japanese** picture: system RAM not ready | None | `zero/w01457.png` (`3d044f4e…`) |
| `WARNING2` | Save cart unformatted | **Japanese** picture: cartridge RAM not ready | None | `cart-zero/w01457.png` (`177e54ed…`) |
| `WARNING3` | Both unformatted | **Japanese** picture: neither ready | None | `both-zero/w01457.png` (`27518ac1…`) |
| `WARNING4` | No save and too little free space | **Japanese** picture: records cannot be saved | None | `free4/w01457.png` (`3f358756…`) |

## Not Seen Yet

Each needs its own capture before it can be ruled in or out.

| Surface | Why expected | Lead |
| --- | --- | --- |
| Console-only pilots' stories | Four pilots added on consoles | Saturn lines from 1141 on name Chiyomaru and Tessan (D-011) |
| A second route through the same pilot, other pilots' scenes | The arcade script branches by pilot | `RE-002` |

## Summary

So far the Japanese on screen is (1) story dialogue boxes, (2) the VS
screen's chapter caption, (3) pilot and mech names drawn as katakana art
on the pilot select and VS screens, (4) the versus-mode win quote
(D-029), and (5) in Jin's ending, its dialogue, narration and captions,
the cast roll's names and one QSound line (`EXP-0037`). Menus, HUD,
banners, scores, continue, credits,
game over and options are already English.

## Census (`UI-001`, `EXP-0067`)

The current image (`data/regression/opt006_names_switch.json`), outside the
story dialogue and endings. Records: `research/experiments/EXP-0067/`.

| Surface | When shown | Text on the Saturn (current image) | Arcade | Evidence |
| --- | --- | --- | --- | --- |
| Attract loop (boot, CAPCOM logo, intro, blueprint parade, title, demo blueprints, `NOW LOADING`, demo fight, `RANKING`) | No input, about every 5,530-5,860 frames; six demo pairs in rotation | English (part labels, HUD, banners, ranking `CAP`/`COM`/`CP`/`SYS`/`TEM`); Japanese only in the city stage's art (row above) | Both sets English, with a QSound screen; `cybotsu` adds an FBI screen and region warnings | cold boot `attract_loads.json`; long run `attract_long.json`; `arcade_attract.json` |
| `KEY CONFIG` | Options, row 6 | English | — | `screens.json` |
| `SOUND TEST`, `DATA RESET` | Options rows 4, 5 | No screen of their own (code: a sound, or `0x060372A4`); SUPPORTED | — | `EXP-0062` |
| Versus `RESULT` | After a versus match | English | — | `screens.json` |
| `EXTRA OPTIONS`, versus select, `SET UP`, VS | Options; versus mode | English (names per the switch) | — | `EXP-0066` |
| VS chapter captions | Before each arcade-mode fight | Japanese; all 81 forced (boxes 496-549, 1045-1071); five (512, 539, 1052, 1053, 1070) draw one English pair glyph each (the M5 trade-off) | `cybotsj` the same; `cybotsu` none: it skips creating the caption outside Japan (`0x0D43E`), and has no English for it (D-060, `EXP-0069`) | `captions.json` |

Files the outline guessed for attract text (`STDEM*`, `VADEM*`, `STDEMO.*`,
`OPDEMO_0.BIN`) and `CYB_ABS.TXT` do not load in the boot or the attract.


## English Art In The Fonts (`UI-001`, `EXP-0068`)

Every store the UI screens load (`EXP-0067` load log, D-052) and the stores
`UI-001` named. "Colours" are the 4-bit indices used (palettes not read).
Renders are local only (`EXP-0068` `render.py`, `grid.py`). Tile `n` of a
4 bpp store is at byte `32 * n`.

| Store (loaded to) | Format | Range | Contents | Colours |
| --- | --- | --- | --- | --- |
| `FIX.BIN` (VDP2 `0x0`) | 4 bpp 8×8 tiles, ASCII-indexed (D-035; menu print `0x0602A82A`, `EXP-0068`) | 32-127 | The small ASCII font: upper and lower case (`t`-`z` drawn), digits, punctuation; comma and apostrophe are dots | 0-5, F |
| | | 128-511 | Further small Latin glyph sets, half-glyphs and button fragments | all 16 |
| | | 512-639 | Gauge and arrow art, no letters | 0-5, 8, B, D, F |
| | | 640-1023 | A 16×16 Latin font (digits, `A`-`Z`), two styles | 0-5, F |
| | | 1024-1087 | Gauge pieces; the copyright line's letter set; score digits | 0, 1, 3, 4, 9, A, D-F |
| | | 1088-1279 | The fight HUD's `POWER` labels (several palettes) and win marks | all 16 |
| | | 1280-1535 | Sixteen mech name plates (Latin), bright and dim versions | 0, 1, 3, 4, A-C |
| | | 1536-1663 | Large banners: unidentified grey art (1536-1567, 1600-1631; layout not assembled) and the new-challenger banner in two styles | 0, 6-B |
| | | 1664-1791 | Result labels (total, energy, time, bonus) | 0-7, 9-C, F |
| | | 1792-2047 | Digit sets | 0, 1, 3, 4, 6, 7, F |
| | | 2048-4095 | 16×16 Latin fonts in several palettes; small button labels | 0-5, F |
| | | 4096-6143 | Fight HUD parts, with the boost and arm-weapon labels | all 16 |
| | | 6144-9983 | Pilot portrait strips, no text | all 16 |
| `KANJI.BIN` (VDP2 `0x40000`) | D-019 glyphs | 23-58 | Full-width digits (23-32) and capitals `A`-`Z` (33-58); no lower case. The current image adds the English pair glyphs (D-024) | — |
| `SELECT.VAD` (VDP1 `0x20000`), bank 56 | raw 4 bpp parts (D-052) | patterns 395-396, 400, 401-424, 428-429 | The labels pilot select, body type, `1P`/`2P`, machine select (`EXP-0057`) | not read |
| | | pattern 399 (`0x39460`, 48×106, frame `0x35`) | The four base bodies' names, a Latin list in a small plain font, stored mirrored (`EXP-0068`; corrects D-052's "no Latin mech name") | not read |
| `PL3F_0.BIN`, bank 63 | type 2 (D-053) | frame `0x0B` | A Latin "G.O.D." banner; where shown UNKNOWN (`EXP-0057`) | not read |
| `KEND_1.BIN` (WRAM-L `0x00280000`), bank 16 | type 2: all 29 cast-roll records decode byte for byte to the game's shadow (`EXP-0068`) | the 13 records of odd frames `0x1B7`-`0x1C9` (`shadow.json`) | The cast roll's Latin names, 40-120 × 8-16 | colour `0x41E0` (D-040) |
| `CAPCOM.PIX` (VDP2 `0x20000`) | 512-wide 8 bpp bitmap (D-049's format) | 352 × 224 | The Latin company logo | 103 indices |
| `OPS00.PIX`, `OPS10.PIX`, `RANKBG.PIX` | the same | 384 × 224-256 | Backgrounds, no text | 5, 16, 8 indices |
| `QSD.PIX`, `WARNINGn.PIX` | the same (D-041, D-049) | — | English already, or built in English (`END-010`, `BOOT-004`) | — |
| `ST00`-`ST0A_FNT.BIN` (VDP2 `0x19000`) | 4 bpp 8×8 tiles | — | Stage backgrounds; text readable only through the stage maps. The city signs (Japanese) are in `ST00_FNT.BIN` or `ST00_SPR.BIN` (SUPPORTED: the first demo loads them) | — |
| `OPS0_0/1.BIN` (WRAM-L), `ST0n_SPR.BIN` (VDP1 `0x20000`), `PL11_0.BIN` (VDP1 `0x38000`), `PL13_0.BIN` (`0x060A6800`), `M3PL*`, `M3CB*` | UNKNOWN; loaded raw by `0x060385A0`, readers not traced | — | Not decoded; must be decoded before any task draws on them | — |

## VS Captions: Storage and Room (`UI-003`, `EXP-0069`)

| What | Fact |
| --- | --- |
| Drawn by | Reader `0x0606CAE8` (`STG0AS.BIN`), box routine `0x0606E6E0`, typing routine `0x0606E5C0` (D-020) |
| Stored as | One `STG0AS.BIN` line per box, story codes (D-019); records and file offsets of all 83 boxes in `EXP-0069` `captions_table.json`; box 496's line at file `0x1526C` (CONFIRMED by a one-cell RAM change) |
| Room | One row; 13 cells inside the fixed banner from the current start (x 96), or 26 Latin characters with pair glyphs (D-024); extra record entries do not show |
| Arcade English | None: `cybotsu` skips the caption by region (`0x0D43E`) and its drawer reads only the Japanese table; English slots 494-551 point to one non-caption record (both sets) |
| Other creators | Type `0x35` is also created at `0x04BDF6` and `0x04C2C0` (no region test); when they run is UNKNOWN |
