# Tasks

## 1. Modern mode stack and settings

- [x] 1.1 Replace `base`, `bumpers`, `outlanes`, `right_drops`, and `hurryup` with a `modern` ball mode that starts empty child modes. Register them in `config/config.yaml` and verify a test shows they run only in Modern sessions and the old placeholder scoring is gone.
- [x] 1.2 Add a Modern settings module holding every tunable value from the specs, and a scoring helper that applies `modern_song_multiplier`. Verify unit tests cover the multiplier.
- [x] 1.3 Add the Modern rules splash slide on Modern game start. Verify a test shows the first ball is served after the splash.

## 2. Shared Classic mechanics

- [x] 2.1 Extract the crater cascade, drop rotation, and green freeze timing from `ClassicTargets` into a shared helper. Verify the existing Classic tests pass unchanged.
  - Deviation: to keep Modern removable, `ModernTargets` reuses Classic's switch tables and mirrors its timings instead of changing `ClassicTargets`. Classic only gained a `_crater_passed` hook in `ClassicSubway` and Modern support in `VolcanoSubwayCounter`.
- [x] 2.2 Let the skill shot motor run for Modern shooter-lane serves using the shared control. Verify tests show the motor runs on Modern serves and replacement balls, and the Classic skill shot tests still pass.
- [x] 2.3 Extend `VolcanoSubwayCounter` crater-arrival counting to Modern sessions. Verify tests show Modern crater entries are counted with the crater-4 chatter filter, including with balls already locked.

## 3. Targets, locations, and scoring

- [x] 3.1 Implement `modern_targets`: crater lamps L24-L27, crater scoring, drop scoring, banks held down until both are down or the ball ends (L28 and L29), and Drop the Needle (50,000, one Standing Ovation step, ball saver ready). Verify tests cover each scenario in the rethemed-game spec delta.
- [x] 3.2 Implement `modern_locations` for the five club locations: names, lamps, the 10,000 hit score, flash-versus-steady lamp precedence, and the remaining base scores. Verify tests cover scoring with a 1x and a 3x multiplier.
- [x] 3.3 Implement the manual-only ball saver: readied by Drop the Needle, pulsing `c_classic_ball_saver`, and clearing on use, tilt, and ball end. Verify tests show no automatic re-serve.

## 4. Nickels

- [x] 4.1 Implement `modern_nickels`: a single random flashing location excluding the last one hit, the 1-5 cost cycle with doubled points per cycle, one nickel held at a time, and a reset at drain. Verify tests cover each nickel scenario in the modern-jukebox spec.
- [x] 4.2 Add the floor nickel from both banks down and the refusal behaviour at the wrong location. Verify tests show the cost is unchanged after a floor nickel and that refusals keep the lit location.
- [x] 4.3 Add the location lines (direction, at least three refusals, and nickel) to the voice script and post their callout events. Verify a test asserts the events are posted.

## 5. Jukebox and song progression

- [x] 5.1 Implement the *select* action (2 s hold with progress events, taps, and a configurable switch) and suppress the crater freeze while it is in use. Verify tests cover tap, hold, remapping, and freeze suppression.
- [x] 5.2 Implement the jukebox entry: a lit crater with a nickel holds the ball at the kicker and opens the selector, and the other cases kick the ball back with their message. Verify tests cover each crater scenario.
- [x] 5.3 Implement the selector slide and logic: ten slots with Hit me! tenth, played artists greyed out, the round reset, the 10 s auto-pick, a random placeholder song, and the song starting when the ball is released. Verify tests cover each scenario.
- [x] 5.4 Add the jukebox catalogue (artists, song titles, and the Hit me! pool) as one data file mapped to `sounds/music/jukebox/<nn>_<artist>/song_<n>.mp3`. Generate a placeholder MP3 for every song file name, with a spoken title over a short backing loop of the expected length, and no original recording. Re-import Godot assets so replaced files load. Verify every catalogue entry has a file that GMC loads, and that the mode timer reads the actual file length.
- [x] 5.5 Implement song lights L33-L42, the song multiplier on L4-L7, the special at the Bar (L44, knocker, free-game slide), and closing the jukebox during multiball. Song slots play a placeholder cut with no mode rule. Verify tests cover each scenario.

## 6. Bonus, extra balls, tilt, and high scores

- [x] 6.1 Implement Standing Ovation (L30-L32, capped at 4x) and the end-of-ball bonus count with its slide. Verify tests cover the multiplier, and the bonus being voided on tilt.
- [x] 6.2 Implement extra balls from songs 3 and 7, collected at the Kitchen, with one lit at a time, two per game, and lost at drain. Verify tests cover each scenario.
- [x] 6.3 Configure Modern's one-warning tilt and keep Classic's count unchanged. Verify tests for both games.
- [x] 6.4 Add Modern high-score entry using green taps and *select*. Verify a test enters initials.

## 7. Presentation

- [x] 7.1 Add `modern_callouts` with event pools, no repeat of the last line, random quips with the quiet gap, the event-over-quip priority, and music ducking. Verify tests cover each callout scenario in the modern-presentation spec.
- [x] 7.2 Write the voice script for all characters and pools in 1940s juke-joint character, and a generation script that renders in-character text-to-speech placeholders, falling back to plain text-to-speech. Verify every scripted line has a generated file that GMC loads.
- [x] 7.3 Mock up each base screen as an image (splash, HUD, direction and refusal callouts, nickel, selector, song intro, mode result, Drop the Needle, extra ball, special, bonus, tilt, high score, game over) with transition notes, and get the user's approval. Verify the mockups are delivered.
  - The user delegated mockup approval; mockups are in `docs/modern/mockups/` and were self-approved.
- [x] 7.4 Build the approved screens as GMC slides and HUD overlays with their transitions. Verify each loads in a GMC run, and that the HUD stays visible under overlays.

## 8. Integration

- [x] 8.1 Run `~/mpf/bin/python -m pytest tests -q` and `openspec validate --all`, and verify both pass.
- [ ] 8.2 On the cabinet, play Modern and check the lamps against the sheet, the jukebox hold and release, Drop the Needle, and the special knocker. Record any lamp fixes.
