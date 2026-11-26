# Proposal

## Why

The song modes use the full-screen HUD over a dimmed video, which doesn't match the agreed Hatch Show Print handbill artwork. The rules are also only shown as a short overlay while the song is already starting.

## What Changes

- While a song mode is picked and playing, the Modern screen shows the "song stage": the JUKE JOINT handbill frame with a 16:9 video window, the mode's device on the left, the mode's instructions on the right and the players along the bottom.
- Each of the ten modes has its own woodcut device panel (stopwatch, ladder, tip jar, spotlight, jukebox, Bouncer, hot plate, microphone, dancers, dial) with its live values on it.
- After the pick, the window shows a handbill with the mode's title, goal and steps while the ball is held. The artist video starts in the window when the ball comes back.
- Score slots without a player show the current player's Ovation, locks and nickel.

## Capabilities

### Modified Capabilities
- `modern-presentation`: song-mode screen layout and the instruction card before the video.

## Impact

- New `slides/modern/song_stage.gd` and `images/modern/stage/` artwork; `modern_hud.gd` hosts the stage and moves the artist video into its window.
- `modern_jukebox` posts `modern_song_intro` (slot, artist, song, title, goal, steps) instead of the teal mode overlay. Each song rule gains a `how` tuple. Scoring and rules are unchanged.
