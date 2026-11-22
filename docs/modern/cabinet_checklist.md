# Modern mode: cabinet checklist

Everything below was verified only in simulation. Check each item on the real machine with a Modern game. Fixes should be small config edits; the files are named on each line.

## Lamps (`custom_code/modern/settings.py`)
- [ ] Song lights 1-10 are L33-L42, left to right along the bottom inserts.
- [ ] The song multiplier 2x-5x is L4-L7, and Standing Ovation 2x-4x is L30-L32.
- [ ] Crater lamps L27, L26, L25, L24 match craters 1-4, and the lit crater cascades as in Classic.
- [ ] Location lamps flash when the player is directed to them: Bar L47, Kitchen L45, Bandstand L46, Coat Check L43.
- [ ] Booths: with the Booths as the nickel target, check L29 and the lamp by every standing right-bank target flash, and a knocked-down target's lamp goes dark.
- [ ] Shoot Again L1, extra ball L45 and special L44 light as described.
- [ ] Classic note: Classic lights L4-L6 for ball save ready, but the lamp sheet says those are multiplier lamps. Confirm, and fix it separately if wrong.

## Ball handling
- [ ] With a nickel, a lit crater sends the ball into the subway, and it stays held while the jukebox selector is open (hold on `bd_classic_subway_lock`).
- [ ] After a song is picked, the ball returns through the subway kicker and the song clock starts only then.
- [ ] Bar (saucer) and Kitchen (fire pit) holds release after about 1 s, including the Ladder and Order Up holds.
- [ ] Locked balls stay in the subway between players and games. Modern never kicks them out.
- [ ] Rent Party: the third lock releases all three balls and play continues with 3 balls.
- [ ] Gate Crasher: with 2 players, player 1 locks 2 balls and player 2 locks the third. "GATE CRASHER!" shows.

## Switches, coils and motor
- [ ] Right green button: a tap moves the selector, and a 2 s hold selects. Hit me! dial taps work.
- [ ] Drop the Needle: the skill-shot motor (`skill_motor`) and lit drop award work as in Classic.
- [ ] Manual ball saver (`c_classic_ball_saver`) arms and saves as in Classic. Party Time re-arms it.
- [ ] Knocker (`c_Replay_Knock`) fires on the special and on replays.
- [ ] Tilt gives one warning, then tilts and voids the bonus.

## Audio and screens
- [ ] Music volume suits the room, and voice callouts duck the music clearly.
- [ ] Your MP3s go in `sounds/music/jukebox/<nn>_<artist>/song_<n>.mp3` and titles in `catalogue.yaml`. Run `godot --headless --path . --import` once, or open the project in the editor, then check that songs play their full length.
- [ ] Replace the general-play music placeholders `sounds/modern_music/house_band_1.mp3` to `house_band_10.mp3` and the attract-mode placeholders `sounds/modern_music/attract_1.mp3` to `attract_5.mp3` with your own MP3s (same names). Each set plays in random order. The house-band set is the base music for both Classic and Modern: it picks a new track at every new ball, after every Modern artist song, and when a track ends.
- [ ] Replace the between-balls placeholder at `sounds/modern_music/between_balls.mp3` with your own MP3 (same name; it loops after each drain until the next ball starts).
- [ ] Modern screens fill the cabinet monitor, scaled and letterboxed.
- [ ] Artist videos: each artist folder `videos/modern/jukebox/<nn>_<artist>/` holds `clip_01.ogv`, `clip_02.ogv`… (about 20 s each, black and white, no sound, 1280×720). Every song plays random clips one after another, so the footage starts somewhere different each time. A `video_<n>.ogv` for one song, or a single `video.ogv`, still works when there are no clips. Convert with `ffmpeg -ss <start> -t 20 -i clip.mp4 -vf hue=s=0,scale=-2:720 -an -c:v libtheora -q:v 5 clip_01.ogv`, reimport, and check playback on the cabinet PC.
