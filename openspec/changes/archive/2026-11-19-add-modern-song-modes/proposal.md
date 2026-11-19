# Proposal

## Why

The juke-joint base (`add-modern-juke-joint-base`) plays a song for each nickel, but the songs have no rules yet. Each of the ten artist slots needs a short mode with its own challenge. A successful run of any mode should be worth about the same, so the player's choice of artist is about play style rather than score.

## What Changes

- Add a shared song-mode framework:
  - The song cut is the mode timer, paused while a ball is held.
  - A drain ends the mode, which still counts as played.
  - Modes completed are tracked separately from modes played.
  - Completing a mode pays a 250,000 completion award.
  - While a song plays, the nickel hunt is suspended and the mode owns its shots.
- Add ten artist-neutral modes, each assigned to an artist slot with placeholder names. Slot 10 is Hit me!.
  1. **Hurry-up:** a draining value at one random location.
  2. **Ladder:** four Kitchen rungs.
  3. **Build and collect:** a spinner pot, cashed at the Bar.
  4. **Roving shot:** the lit location moves.
  5. **Jukebox jackpot:** crater jackpots.
  6. **Party time:** double scoring with the Bouncer kept lit.
  7. **Order up:** a Kitchen pickup, then one delivery.
  8. **Request night:** collect all five locations.
  9. **Dance floor:** 5x bumpers.
  10. **Hit me!:** a spin-the-dial location award.
- Balance each mode to about 750,000 mode points for a successful run, plus the completion award, before the song multiplier. All values are tunable.

## Capabilities

### New Capabilities
- `modern-song-modes`: the song-mode framework and the rules and scoring of the ten modes.

### Modified Capabilities
None.

## Impact

- **Depends on:** `add-modern-juke-joint-base`.
- **Adds:** ten MPF code modes, their GMC slides and placeholder music cuts, and MPF tests.
- **Uses:** the base's scoring helper, its lamps, and the *select* and tap actions.
