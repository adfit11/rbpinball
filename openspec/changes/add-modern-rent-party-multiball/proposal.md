# Proposal

## Why

Modern needs a multiball that a player can reasonably reach in a single ball. Its locks are physical balls in the subway, so the next player can steal them. The juke-joint theme frames it as a rent party: the player fills the guest list, then lets the guests in through the lock.

## What Changes

- Add the guest list. Each of the five club locations and each completed drop bank counts as one guest, for seven possible. Five guests fill the list. Progress resets at drain.
- Filling the guest list lights the lock for the current player for the rest of that ball. A lit crater from the cascading crater lights then locks one ball and serves a replacement to the shooter lane. Locking continues until the subway holds three balls.
- Locked balls stay in the subway across turns. The screen always shows the physical lock count, and the next player can steal the locks: their lit lock starts from the count already in the subway. Starting multiball with locks someone else made shows "GATE CRASHER!".
- Add Rent Party, a three-ball multiball:
  - A lit crater pays a jackpot of 250,000 plus 50,000 per jackpot.
  - After three jackpots, the Bar pays a 1,000,000 super jackpot.
  - The jukebox is closed for the whole multiball.
  - Normal play resumes at one ball, and completing the multiball lights an extra ball.
- No automatic ball save for multiball, which follows the base's manual-only rule.

## Capabilities

### New Capabilities
- `modern-multiball`: the guest list, physical locks and stealing, and Rent Party scoring.

### Modified Capabilities
None.

## Impact

- **Depends on:** `add-modern-juke-joint-base`, which provides the crater cascade, Modern subway counting, the jukebox closure, and the extra-ball rules.
- **MPF:** Modern `multiball_locks` and `multiballs` on `bd_classic_subway_lock`. The lock must not be ejected at turn change or game end in Modern, which matches the current Classic-only `eject_all_events`.
- **Display, audio, and tests:** a guest-list and lock HUD, voice lines, and MPF tests.
