# Design

## Context

See proposal.md - Why. Classic locks with `multiball_locks.classic_subway_lock` (`physical_only`, three balls, two replacements) on `bd_classic_subway_lock`. It releases through `bd_classic_subway_kicker`. `bd_classic_subway_lock` ejects all its balls on tilt and game end only in Classic sessions, so Modern locks stay put. The base change extends crater-arrival counting to Modern.

## Goals / Non-Goals

**Goals:**
- A lock count that is the physical subway count, shared by all players.
- A guest list kept per player and reset each ball.

**Non-Goals:**
- Virtual locks or relocking.
- Automatic ball save.

## Decisions

### A dedicated `modern_multiball` mode
It starts with the Modern ball modes and owns:
- the guest list, counted from Modern location and bank-complete events;
- the lit-lock flag;
- a `multiball_locks` device with `locked_ball_counting_strategy: physical_only`, enabled when the guest list is full;
- a three-ball `multiballs` entry started when the lock is full.

The physical-only strategy gives stealing for free: the device counts the balls in the subway, not per-player locks. A per-player virtual lock was rejected, because the user wants stealing and no eject at turn change.

### Lit-crater gating
The lock device is only enabled while the lock is lit. A crater entry is accepted as a lock only if `modern_targets` reports the crater as lit. Otherwise the entry goes down the kick-back path. This matches Classic's qualification.

### Gate Crasher detection
Record the player number that made each lock (`modern_lock_owners`, a machine variable). When Rent Party starts and any lock belongs to another player, post `modern_gate_crasher` for the slide and voice line.

### Jackpots and ending
During the multiball the craters stay in the cascade, and a lit crater pays the jackpot. The Bar flashes for the super jackpot after three jackpots. When `balls_in_play` drops to 1, the multiball ends, the jukebox reopens, and the extra-ball light is requested through the base's limits.

### Lock and nickel on one entry
A lit crater with the lock lit and a nickel held locks the ball first, then opens the selector. The song start is deferred until the replacement ball is plunged (first playfield switch).

## Risks / Trade-offs

- **The subway count drifts with crater-4 chatter.** Mitigation: the base change's debounced counting, plus tests with prior locks.
- **A lock left at game end carries into the next game.** This is accepted for Modern, because the next game can steal it. Classic recovery is unaffected.

## Migration Plan

Land after the base change. Test in virtual MPF, then on the cabinet with multiple players. Roll back by reverting.
