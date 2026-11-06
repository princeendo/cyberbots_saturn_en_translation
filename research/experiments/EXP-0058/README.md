# EXP-0058: Are Any Names Spoken?

Task: LOC-003
Status: DONE
Confidence: CONFIRMED (the user's hearing of each clip)

## Observation

Whether any name is spoken had never been checked (`docs/names.md`). The
names are the same in Japan and the US (D-013), so a spoken name cannot
disagree with Latin art; this is a completeness check.

## Hypothesis

No pilot or mech name is called at the select, VS, round start or win;
names may be heard in voiced story lines.

## Controlled Change

None. Clips recorded with sound from saved states (and one cold boot for
the pilot pick), each heard by the user, one at a time.

## Prediction

No name called by an announcer; possibly names inside voiced dialogue.

## Inputs and Provenance

| Clip | Source | Moment | SHA-256 (first 8; all in `clips.json`) |
| --- | --- | --- | --- |
| 1 | session state 6626, 5 s | VS screen, Jin against Shade | `06c25d18…` |
| 2 | state 7339, last 4.5 s of 600 frames | first round's start ("GO!") | `ed4500f8…` |
| 3 | state 12611, 10 s | Jin's knockout win and bonus |`036b9586…` |
| 4 / 4b | state 4851, 10 s / seconds 4-8 | Jin's story introduction (narration) |`c440a00f…` |
| 5 | `local/win002/saturn/post.mcs` (EXP-0032), 6 s | versus VICTORY (Jin over Arieta) and RESULT |`c06cbfad…` |
| 6 | END-001 checkpoint, Santana's ending forced (`--onhit 06018E0C:060CFF7E=01`), last 12 s of 2,400 frames | Santana and Arieta talking |`fe6aaf7f…` |
| 7 | cold boot, versus select, 10 s | player 1 picks Jin, player 2 picks Arieta |`4ebcffd7…` |

Clip hashes are in `research/experiments/EXP-0058/clips.json`; the clips
are game audio and stay in the ignored `local/loc003/listen/`.

## Tools and Environment

| Tool | Use |
| --- | --- |
| [`record.py`](record.py) | Patched build with `-qtrecord` from a state (optional writes and on-hit writes); the silent home's volume does not reach the recording |
| [`launch_rec.py`](launch_rec.py) | `drive.py launch` with `-qtrecord`, for the cold boot |
| `EXP-0019/drive.py` | Single pad presses, checked by screenshot |
| ffmpeg | Clip cutting |

## Procedure

```bash
R=research/experiments/EXP-0058/record.py; ST=local/ref005/session/states
./invenv.sh python $R local/loc003/vs1 --state $ST/f00006626.mcs --frames 600
./invenv.sh python $R local/loc003/start --state $ST/f00007339.mcs --frames 600
./invenv.sh python $R local/loc003/win --state $ST/f00012611.mcs --frames 600
./invenv.sh python $R local/loc003/story --state $ST/f00004851.mcs --frames 600
./invenv.sh python $R local/loc003/victory --state local/win002/saturn/post.mcs --frames 360
./invenv.sh python $R local/loc003/santana --state local/end001/checkpoint/jin_ending_a16503.mcs \
  --frames 2400 --onhit 06018E0C:060CFF7E=01
./invenv.sh python research/experiments/EXP-0058/launch_rec.py "local/disc_images/cyberbots_saturn_jp_2m/Cyberbots - Fullmetal Madness (Japan) (2M).cue" local/loc003/select
# drive.py key: Start (title), Down, A (VERSUS MODE), A (P1 Jin), p2a (P2 Arieta); drive.py stop
# clips cut with ffmpeg as listed above (clip 7: 106.5-116.5 s, the picks at frames 6422 and 6695)
```

2026-11-06, 10:10-10:30 local. The cold boot was the user's choice:
"Run one more cold boot" (to cover the pilot pick); 5 single presses.

## Actual Result

The user's answers, verbatim:

| Clip | Answer |
| --- | --- |
| 1, VS screen | "No speech" |
| 2, round start | "No speech" |
| 3, win | "It says "TARGET DESTROYED" but no other speech is there" |
| 4, story narration | "Japanese language is spoken, no idea what it's saying" |
| 4b, the line naming Jin | "Yes, "jin" is said" |
| 5, versus VICTORY | "I hear speech. MAYBE it says "Jin" at the very start of the phrase?" (the quote's text has no name) |
| 6, Santana's ending | "Speech, no name" |
| 7, pilot picks | "No speech" |

## Conclusion

No announcer calls a pilot or mech name (select, VS, round start, win).
The story is voiced in Japanese, and a name is heard where the text has
one ("jin"); victory quotes and the endings are voiced too. Since the names
are the same in both regions, no spoken name conflicts with Latin art, and
no change is needed.

## Uncertainty and Alternatives

- Clip 5's possible "Jin" is unconfirmed; its text has no name.
- Only some pilots' story, victory and ending lines were heard; others may
  speak names in the same way (Japanese readings of the same names).

## Reproduction

Run the procedure; the user listens to each clip.
