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
| **VS screen chapter caption** | Before each fight | **Japanese** box, e.g. Saturn lines 899 and 900 | **No**: the Japanese arcade shows the same caption, the US arcade none (`EXP-0012`); the box is `0x0609CC22`[pilot × 10 + stage] (`STG0AS.BIN`), the arcade's `0x62D9A` table the same: boxes 494-549, and 1045-1071 for pilots 6-8 (`EXP-0032`); the US set has English records for these slots but the US arcade shows none | `f00006717.png` (`578caa24…565a`), `f00015684.png` (`f9868e50…cd04`) |
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
| Stage backgrounds | Fights, attract | Japanese signage painted into the art | Same art in the arcade | many |

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

How each is drawn (`EXP-0038`, D-035):

| Surface | Layer | Pixels from | To change it |
| --- | --- | --- | --- |
| Dialogue, narration, captions | VDP1 glyph cells (the story's path) | `END.BIN`'s lines and code table; glyphs from `SE.DAT`'s copy of `KANJI.BIN` (VDP2 VRAM `0x40000`) | `END.BIN`'s lines, and `SE.DAT`'s font copy as well as `KANJI.BIN` |
| Cast-roll names | VDP1, one sprite per name line | Images decoded by `0x0601446C` from `KEND_1.BIN` | New images in `KEND_1.BIN`'s format (not decoded yet) |
| Credits, thank-you | VDP2 NBG0 | `FIX.BIN`, ASCII-indexed characters | Already English |
| QSound Japanese line | VDP2 NBG1 bitmap | `QSD.PIX` (raw 512×256, 256 colours) | Edit the bitmap |

## Not Seen Yet

Each needs its own capture before it can be ruled in or out.

| Surface | Why expected | Lead |
| --- | --- | --- |
| Other pilots' endings | Every pilot has one, selected by the winner's pilot byte; Santana's was forced and shown (D-036). Jin's scene 20 is never posted | `data/text/ending_posts.json`; `END-020` |
| Console-only pilots' stories | Four pilots added on consoles | Saturn lines from 1141 on name Chiyomaru and Tessan (D-011) |
| `KEY CONFIG`, `SOUND TEST`, `DATA RESET` sub-screens | Option rows | — |
| Boot, cart and save warnings | `WARNING0`-`4.PIX` on the disc | `UI-004` |
| Attract or opening text not in the first two minutes | `OPDEMO*`, `STDEM*`, `VADEM*` files | `UI-002` |
| A second route through the same pilot, other pilots' scenes | The arcade script branches by pilot | `RE-002` |

## Summary

So far the Japanese on screen is (1) story dialogue boxes, (2) the VS
screen's chapter caption, (3) pilot and mech names drawn as katakana art
on the pilot select and VS screens, (4) the versus-mode win quote
(D-029), and (5) in Jin's ending, its dialogue, narration and captions,
the cast roll's names and one QSound line (`EXP-0037`). Menus, HUD,
banners, scores, continue, credits,
game over and options are already English.
