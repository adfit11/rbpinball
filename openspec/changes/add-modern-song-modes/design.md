# Design

## Context

See proposal.md - Why. `add-modern-juke-joint-base` adds the pieces this change builds on:
- `modern_jukebox` posts a song-start event with the artist slot and song, and counts songs played.
- `modern_locations`, `modern_targets`, and `modern_holes` post Modern shot events.
- Scoring goes through one Modern helper that applies the song multiplier.
- The *select* and tap actions, and suppression of the crater freeze, are available to modes.

## Goals / Non-Goals

**Goals:**
- One framework that owns song timing, pause, drain, completion, and the nickel-hunt suspension, so each mode only implements its challenge.
- All mode values live in the Modern settings module.

**Non-Goals:**
- Final artist and song choices, and final music. Placeholder cuts are used.
- Running songs during multiball, which the base already blocks.

## Decisions

### A base song-mode class
A `ModernSongMode` base class (MPF code mode) starts on the song-start event for its slot and does the following:
- runs the song timer, pausing it on ball-hold events and on subway holds;
- stops on the song end, a drain, or tilt;
- posts `modern_song_completed` once, and pays the completion award;
- posts `modern_song_ended` with the outcome.

`modern_bonus` increments Standing Ovation on `modern_song_completed`, and `modern_nickels` suspends and resumes on song start and end. Each of the ten modes subclasses it with its own shot handlers. A data-driven YAML-only approach was rejected because several modes need timers and random choices.

### Modes take over shots by priority
Song modes run at a priority above `modern_locations`. They block the location's nickel and refusal handling while active, but the location's base score still applies unless the mode replaces it. Party time doubles scores through a factor the scoring helper reads. Dance floor sets a bumper factor of 5.

### Holds and releases
The Ladder and Order up holds use `modern_holes` hold-and-release events with a 1 s delay. Jukebox jackpot kicks the subway straight back through the base's non-jukebox path, so it never locks or opens the selector.

### Green ownership
Roving shot and Hit me! claim green through the base's ownership mechanism, so taps drive the mode instead of freezing the craters.

## Risks / Trade-offs

- **Build and collect and Dance floor values depend on shot rate.** Mitigation: the values are tuned at the cabinet in the settings module.
- **Pausing the song cut needs GMC music control.** Mitigation: the mode posts pause and resume events, and if GMC pause is unreliable, the timer pauses while the music keeps playing.

## Migration Plan

Land after the base change. Test in virtual MPF, then play on the cabinet. Roll back by reverting. Song slots then return to the base's placeholder cut.

## Open Questions

- The final song cut lengths per song (the draft assumes about 60 s).
