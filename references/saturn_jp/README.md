# Cyberbots Saturn JP: Source Image

This is the modification target. Permitted provenance and factual metadata only;
never commit the image or anything extracted from it.

## Local Source Image (`ENV-006`, 2026-11-02)

The user supplied a Redump-style BIN/CUE set in
`~/Downloads/cyberbots/saturn_cue_bin/` (63 files). They were copied
unchanged, as APFS clones (`cp -c`), into the ignored, previously empty folder
`local/disc_images/cyberbots_saturn_jp_2m/`. Treat these files as immutable;
derived images belong under `build/`.

Release description: `Cyberbots: Fullmetal Madness (Japan) (2M), Sega Saturn
T-1217G V1.002 19970219; Redump-style BIN/CUE supplied by the user 2026-11-02;
release identity as named, not independently verified`.

**Database match (`ENV-007`, 2026-11-02): CONFIRMED.** All 62 tracks and the
CUE sheet equal Redump disc 58190 (<http://redump.org/disc/58190/>:
`Cyberbots - Fullmetal Madness (Japan) (2M)`, T-1217G, version 1.002, build
date 1997-02-19, edition "Original", 62 tracks, write offset 0, mastering
code `T-1217GP-01438 2MB1`) in SHA-1, MD5 and CRC-32 (sizes follow); the CUE
is byte-identical to Redump's. Redump's lists were fetched with `curl` and
compared by script; the page was read in the built-in browser
(`redump_58190.json`). The web-fetch tool had refused the connection earlier
that day; `curl` and the browser did not.

"(2M)" is Redump's name for this pressing: the other entry, disc 3669
(`Cyberbots - Fullmetal Madness (Japan) (1M)`, T-1216G, "Limited Edition",
mastering code `T-1217GP-01438 1M2`, `redump_3669.json`), has the **same
track 01** (SHA-1 `699b6be7…a848`) and different audio tracks (61 of 61
differ; several pregaps are `00:01:74`). The names mark the two masterings,
not a RAM cart. A patch to track 01 therefore applies to both editions.

Hashes were produced with
`./invenv.sh python -m tools.disc.hash_source --json --description "..." local/disc_images/cyberbots_saturn_jp_2m/*`
and agree with an independent `shasum -a 256` of the CUE and track 01.

| Filename | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 01).bin` | 103001136 | `758fa7956aa6139460c391ec5225e69cc9cde13dfe2281e8c544e594d201dbd1` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 02).bin` | 5315520 | `fb6f2702f7e02c541ab0e305a3c8881eecdfc1efe1bd1743ce599b42ca157b00` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 03).bin` | 6435072 | `fb14d5c26cc919baa6bca0734ede7fdb61209ddc5fd6b9f73dd6746360141291` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 04).bin` | 4412352 | `f157c6ddd66f0d8ac4ee57158a5440b6aa0831045a95136848cec4e65667491e` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 05).bin` | 4398240 | `97ead1ee3e124bae37235416fbed8c2a971d469ac5a18bffdc66c39f9d5f1018` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 06).bin` | 4424112 | `02d9bf49e8266a8919b257658485b575c3d4343d90521bbc9619eeec19e51c7b` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 07).bin` | 3342192 | `875eaf2d8b4b08f5a69861a2efaf9512b1fff1742d654ef69adbae40a22abc4c` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 08).bin` | 3535056 | `73d32ce3ab297e2d56b3657df9d2cfbdce94000f41dfd304208dcf9b0dab214f` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 09).bin` | 3525648 | `ae9bca51cca39e34e237fc5a888bc30e29b66fbbc0af67f867487c8433200781` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 10).bin` | 3539760 | `8a377688df3e279823b9caf28bbae6d1d51213b127d3294b1434338f402b2564` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 11).bin` | 1058400 | `77f9cf01bda7993a4777062f2faf88680671fcbbc80ab5ff7d972f7e8e685145` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 12).bin` | 1133664 | `ffb3f7f216ddce3c449f9a5f967cd8e42de7b5cf192606a7213b1d1fe212e68a` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 13).bin` | 1208928 | `d4a7d66f8da6f0d88509af54ad6d2d0748ee9ad326be89036c739282e4374829` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 14).bin` | 1058400 | `3a7984fd00ccbdde7e10d446c07157c23827915e1c31a00d7d46d775402d4275` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 15).bin` | 6178704 | `5b3eb2c9506615c935242aaab5b09a57874579cbbce046a55f8a7b2fe5379af2` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 16).bin` | 1058400 | `c82f303fd11c52b5675f6d601aa2f1f61eb3e3f8500872253cdc6b6bc8235fef` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 17).bin` | 1058400 | `85a574df1a706418c434b074b8c97b7ff093e89270c93799de4456eee62cfaf4` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 18).bin` | 18305616 | `f428142f4924fca6a8aee20c366c9738af705d01f3798e89e382ead98bb9711a` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 19).bin` | 18874800 | `d2b3c996abfab54736f71448d3dd3dc27ed4f843018bd6efaba7744c823a9a5b` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 20).bin` | 18874800 | `fc91db2148458252412aeb626442814ad5659020c1b0dc3d1a65a0bef9beb86f` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 21).bin` | 18863040 | `e57a402c2d6aae3ed16eb0899493c8f1ba27387806d595ee13f5cc8891a5b1de` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 22).bin` | 18877152 | `adc38c8558165a9238d157ecbdb30a2ae62f38ac2b83d898b258f905f4bc226b` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 23).bin` | 18877152 | `ed1f5a888a65d0d7ea15a01384cc92c8066e39fdd298bf9934768f306b4bca9f` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 24).bin` | 18877152 | `4322a795af1693075ba2a389ea2ede6f624260d2c6cc895054c373adfd1e9e0a` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 25).bin` | 18874800 | `e74a09dbeed2f9b5b38518a412f511acd0178a73f05d25ff8e558b7b13abd665` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 26).bin` | 18877152 | `cc134af6224469e5bf72fa588ce198ea83deb6e90bd33f5f11e6ef755abdfc0e` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 27).bin` | 18877152 | `cccdee8e2e873dabdd793b6952c3b11b07b019881861e74beed52001652eccac` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 28).bin` | 18877152 | `5c4b92bf006262d7709b30c1a4f3250e08b5159491b6003fb9e58737a1f2d72c` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 29).bin` | 12999504 | `512f93968dabc868f026e793318e12874a5da9d8a5f6ab62b748bb37b99a4a44` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 30).bin` | 13709808 | `b5026594b55cdada90da0906094fd18336bb79a79617592ff574e417842bd317` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 31).bin` | 9974832 | `a9ff20f28a0be4998fe15adf3cc0b74266240070dd78ebc59ebd6c51df485140` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 32).bin` | 9290400 | `5c4e7b42606bb270cc924a2e6bfe4ac8d69ee756f69c829e18ebbe2d7357c6ca` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 33).bin` | 9814896 | `91dfc0be00a8868997f17f08db33de0ecd16143e4e4b08b627e0dfd2979747b3` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 34).bin` | 1707552 | `4fe6f56ff10603266509ae73b3201a2b3b22b622819aea9902606abe71a4a4ec` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 35).bin` | 1721664 | `d24499524063e467d2fef7b7de1ea2fe25d62154a92572d8ca5ef121bbc8ea9c` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 36).bin` | 12639648 | `34c73ed69d2ffe627e803fd4f95e16452d816e0f12928257e2434f5acde1a382` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 37).bin` | 4412352 | `de4df00663e75d84a523e2d847aa8bc1961765ac66262fc928282a78bd8b68c3` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 38).bin` | 2455488 | `5d0b00159d4af3b417c6f943d2ad61bc42b3ed0f0325a9a677fca2bc52a15e04` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 39).bin` | 4360608 | `02f934022332ca89a8754184698583c734201094ead99f8c3ed339f7aeaec9c4` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 40).bin` | 6642048 | `cad9ff0236c5b96e157be6caf1056c952e489ee3995ef325a5a0b9c1e522086a` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 41).bin` | 8716512 | `7fe0ac60560571a01efbda084e7cfaa69dff57023e6f31659aa06ff53f836814` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 42).bin` | 4513488 | `7fb9c56d6c22a18e748b7c11f7b2aa5a17896a6846c76db18763004ab22e8828` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 43).bin` | 1742832 | `363a0744d5bb870832abbe06578ef459acf4495377927fb4cd2c01b91720ecd2` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 44).bin` | 7422912 | `47e3c5282e7faa436e7e6c49bfe2e479e4b69aa843f25c6b08a50ddec8cf574f` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 45).bin` | 4833360 | `30b810c8f120e061bc8f5c53d1537c1b5431dabeea7a10346095292b8c760c6f` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 46).bin` | 1832208 | `62fed78d2e4985bc49f601a80f4021c8dc70c2c3c448182f1017d38894a30bdb` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 47).bin` | 5355504 | `1d80a3ade0de3370820c8d066b0e8390112a4c4dd0372f26b95e408eea956f4e` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 48).bin` | 1881600 | `083c2ec4755a7d7bfdf328248e88fa702ed4ec6edac3c7a0926ce83a2fe06dc3` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 49).bin` | 8309616 | `796f0f19b4596953570280d5a783628dd16b297f3efbff969a2703c4d3b365dc` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 50).bin` | 6291600 | `9eb85709901746cf109005e1a1ae398ff8e4b02e8f17215b1c03fa5d66f403f6` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 51).bin` | 7808640 | `6a4819477f958f064e529b898d8213e19bf8d96bbad868b46db5e47cc43e5d6b` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 52).bin` | 4628736 | `a59f7f97229b4c91e4f8d084c4798d4a32f66474f7c38e6c435710d864b4a721` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 53).bin` | 2213232 | `0a8fee62a2a17c87e8213c1870cb26839ea7879a3893a575090d7e97a00ff1b9` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 54).bin` | 5663616 | `78274d197e006f0126479ca2bdb38a49b3baa3e62879e46a47c4e2fa00916548` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 55).bin` | 8827056 | `e62187c8c26703202fe254825ad1d1069263bdfcd058c3ca975c1871350f23a4` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 56).bin` | 8660064 | `5058162653c70aeb0723124819b90da063d74ea795d13c8dc334158adc3c54dc` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 57).bin` | 7030128 | `4a1ffc8f4eb8bce95c4848da271b859640a74bd8eaacabc41ec526e540c34444` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 58).bin` | 10322928 | `657d6446b1a45ebb1cb4fbfde8180f135122294b0154998d963e53106d7adab4` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 59).bin` | 9908976 | `f086c070dbeed12194d58b925c06369f269684611e9a35f1308f93551dba2138` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 60).bin` | 6162240 | `7da6e2134e257619ac87723975f3d6200dee6d3ca024ffe00e5071d7b1dfbf56` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 61).bin` | 9789024 | `a65e91593b39136209570157a21dac4230b79bbcb381124c33abe790a7fd0be9` |
| `Cyberbots - Fullmetal Madness (Japan) (2M) (Track 62).bin` | 7620480 | `24a19305f1f8ad1895ddb49f4e2d962453a3f39736205bb06e898b804e012ca9` |
| `Cyberbots - Fullmetal Madness (Japan) (2M).cue` | 8499 | `9f1248adc58b225fa55aa2960df36113212ff200c26917a8c40f22f2cb9c5f14` |

## Observations (2026-11-02, static, no emulator)

- **Layout.** 63 files: one `.cue`, Track 01 `MODE1/2352` (43,793 sectors, FAD
  150-43,942), and Tracks 02-62 `AUDIO`, each with a 2-second `INDEX 00`
  pregap. `CATALOG 0000000000000`.
- **System area (track 01, sector 0).** `SEGA SEGASATURN`, maker
  `SEGA TP T-12`, product `T-1217G`, version `V1.002`, date `19970219`,
  `CD-1/1`, area `J`, peripherals `JW`, title `CYBER BOTS`. These first 512
  user-data bytes are what RetroAchievements hashes; a release patch must keep
  them (`docs/lessons_from_xvsf.md`, lesson 3).
- **ISO 9660.** `tools.disc.iso9660 --check`: 0 bad sync, 0 non-Mode-1 and 0
  address mismatches. Volume ID `CYBER_BOTS`; root at LSN 20, 16,384 bytes;
  325 files, no subdirectories. The primary volume descriptor's volume space
  size is 251,277 blocks, which spans the audio tracks, not only track 01.
- **Files** (`iso_listing.json`: name, LSN, size and SHA-256 of each readable
  file). 264 files (89,118,286 bytes) lie in track 01 and were extracted to
  the ignored `local/extracted/saturn_jp/`. 61 entries start past track 01's
  end and are unreadable from it: `01`-`32` and `45`-`52`, and 21 named ones
  (`ARI_END1`, `BAO_END`, `DE_END1`, `GA_END1`, `JIN_END1`, `MA_END1`,
  `SAN_END1`, `SYE_END1`, `TI_END1`, and their numbered siblings). For `01`,
  LSN 43,943 and 2,110 sectors equal track 02's start after its pregap and its
  length less the pregap. **Confirmed** (`EXP-0001`, D-002): each of the 61
  entries starts at one audio track's first sector, per Mednafen's table of
  contents; the 21 named ones are tracks 42-62. Their content is not yet
  known.
- **Text.** First-look results are in `research_log.md` (SESSION-0001).
