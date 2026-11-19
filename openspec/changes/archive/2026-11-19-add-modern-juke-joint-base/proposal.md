# Proposal

## Why

Modern still runs the original Volcano placeholder rules: bumpers, outlanes, right drops, and a left-return hurry-up. It needs its own ruleset. The new theme is a 1940s rhythm-and-blues juke joint, where the player earns nickels around the club and spends them at the jukebox (the craters) to play songs. This change builds the base game that the song modes (`add-modern-song-modes`) and the Rent Party multiball (`add-modern-rent-party-multiball`) build on.

## What Changes

- **BREAKING** Replace Modern's placeholder rules (`base`, `bumpers`, `outlanes`, `right_drops`, `hurryup`) with the juke-joint base game.
- Add five named club locations, each with a lamp and a voice: Bar (saucer, 23), Kitchen (fire pit, 43), Bandstand (spinner, 44), Coat Check (spot target, 36), and Back Door (kicking target, 26).
- Add the nickel hunt. One location at a time flashes as the next shot. A nickel costs 1, then 2, 3, 4, and 5 successful location shots. After that the cost returns to 1 and the points double. Wrong-location hits play a random refusal line. Each completed drop bank counts as half a nickel, and both banks down is a fixed-cost "nickel on the floor".
- Add the jukebox. With a nickel, a lit crater from Classic's cascading crater lights opens the artist selector. The right green button scrolls with a tap and selects with a hold. The song starts when the ball is released. The ten slots are nine named artists (Louis Jordan to Joe Liggins) and Hit me!, which plays from a pool of twelve one-hit wonders. Played artists are greyed out until all ten have been played.
- Add song progression. Lamps L33-L42 count songs played. A song multiplier on L4-L7 rises every five songs. The tenth song lights a special at the Bar that fires the knocker and shows a free-game award.
- Add Drop the Needle: the Classic rotating lit drop, green freeze, skill shot motor, and lit-drop award, now running in Modern.
- Add Modern scoring, a Standing Ovation bonus multiplier (1 + songs completed this ball), extra balls collected at the Kitchen, a one-warning tilt, a manual-only ball saver, a placeholder rules splash, and high-score entry.
- Add one *select* input action, currently a 2 s hold of the right green button, so a wired left green button can replace it later.
- Run song slots without mode rules until `add-modern-song-modes` lands.
- Play songs from MP3 files in the music folder. Generated placeholders keep each song's file name until the user drops in edited recordings; the game is private and the user owns them.
- Add in-character voice callouts mixed over the music. They play at game events and at random as encouragement and era quips, from generated text-to-speech placeholders that supplied recordings replace.
- Add designed screens and animated transitions for every Modern state, mocked up before they are built.

## Capabilities

### New Capabilities
- `modern-jukebox`: nickels, the jukebox selector, artist rounds, song progression, the song multiplier, and the special.

- `modern-presentation`: voice callouts and the rules for screens and transitions across Modern.

### Modified Capabilities
- `rethemed-game`: replaces "preserve current play" with the juke-joint base rules: locations, scoring, drops, Drop the Needle, bonus, extra balls, tilt, ball saver, splash, and high scores.
- `classic-volcano`: the skill shot motor requirement no longer keeps the motor off in Modern, because Modern runs it for Drop the Needle.

## Impact

- **MPF:** Modern modes and custom code, `config/config.yaml` mode registration, and possibly the drop bank reset events in `config/config_drop_targets.yaml`. The Classic subway counter (`custom_code/volcano_subway_counter.py`) must also count crater arrivals in Modern.
- **GMC/Godot:** new Modern slides (splash, base HUD, selector, refusal and award callouts), GMC sound assets, and placeholder voice files.
- **Tests:** new Modern MPF tests. Classic behaviour is unchanged.
- **Hardware:** the Back Door indicator is the ball-save inserts below switch 26, whose lamp output is not yet identified. Until it is, the Back Door is directed on screen only.
