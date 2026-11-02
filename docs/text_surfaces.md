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
| `PILOT SELECT` grid (10 portraits) | Mode start | English label; **pilot name as Japanese katakana art** under the portrait | Arcade has its own select (not compared) | `f00003026.png` (`41e1e675…a874`) |
| `MACHINE SELECT`, `BODY TYPE` | After pilot select | English (mech names `BLODIA`, `REPTOS`, `FORDY`, `GULDIN`) | — | `f00003264.png` (`f12cd48e…6eee`) |
| **Story dialogue boxes** | Introduction, before and after each fight | **Japanese**, typed out; Saturn script lines (D-008) | Yes for paired lines (D-011) | intro `f00004959.png` (`fbdcff49…5603`); pre-fight `f00005632.png` (`f4ef1367…a27f`); post-fight `f00013887.png` (`1c56587b…bf91`) |
| **VS screen chapter caption** | Before each fight | **Japanese** box, e.g. Saturn lines 899 and 900 | **No**: lines 899-952 have no arcade counterpart (D-011) | `f00006717.png` (`578caa24…565a`), `f00015684.png` (`f9868e50…cd04`) |
| **VS screen names** | Before each fight | **Pilot and mech names as Japanese katakana art** (both sides) | Arcade VS screen not compared | as above |
| Fight HUD | Fights | English (`BOOST`, `POWER`, mech names, score, timer) | — | `f00008156.png` (`15f29d0a…f689`) |
| Fight banners | Fights | English (`PHASE 1`, `PROCEED`, `GO!`, `FIGHT!`, `N HIT COMBO!`) | — | many |
| Round end | After a KO | English (`TARGET DAMAGED`/`DESTROYED`, `UNIT DAMAGED`, `MISSION TERMINATED`, `1P WIN`/`LOSE`) | — | `f00012822.png` (`84bd973d…b5d6`), `f00023412.png` (`221f7fd7…3645`) |
| Bonus tally | After a win | English (`BONUS`, `ENERGY`, `TIME`, `TOTAL`, `Rank`) | — | `f00012943.png` (`f5e5b747…0057`) |
| Continue | After a loss | English (`CONTINUE?`, countdown) | — | `f00023887.png` (`3dcbfc35…4508`) |
| Game over, initials | After the countdown | English | — | `f00025276.png` (`88577c3e…9c4e`), `f00025813.png` (`299f26f9…db6c`) |
| `OPTION MODE` | Title menu | English (`DIFFICULTY`, `TIME LIMIT`, `SHORT CUT`, `SOUND`, `SOUND TEST`, `DATA RESET`, `KEY CONFIG`, `3M RAM MODE`, `PRESS START TO EXIT`) | — | `f00027081.png` (`02f4218a…270f`) |
| `RANKING` | Attract | English | — | `emu003/boot1/frames/118.png` |
| Stage backgrounds | Fights, attract | Japanese signage painted into the art | Same art in the arcade | many |

## Not Seen Yet

Each needs its own capture before it can be ruled in or out.

| Surface | Why expected | Lead |
| --- | --- | --- |
| Endings | Every pilot has one | `END.BIN`; audio tracks 42-62 (D-002) |
| Console-only pilots' stories | Four pilots added on consoles | Saturn lines from 1141 on name Chiyomaru and Tessan (D-011) |
| Versus mode screens | Title menu item | — |
| `KEY CONFIG`, `SOUND TEST`, `DATA RESET` sub-screens | Option rows | — |
| Boot, cart and save warnings | `WARNING0`-`4.PIX` on the disc | `UI-004` |
| Attract or opening text not in the first two minutes | `OPDEMO*`, `STDEM*`, `VADEM*` files | `UI-002` |
| A second route through the same pilot, other pilots' scenes | The arcade script branches by pilot | `RE-002` |

## Summary

So far the Japanese on screen is (1) story dialogue boxes, (2) the VS
screen's chapter caption, and (3) pilot and mech names drawn as katakana art
on the pilot select and VS screens. Menus, HUD, banners, scores, continue,
game over and options are already English.
