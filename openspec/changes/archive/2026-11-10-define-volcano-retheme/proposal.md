# Proposal

## Why

Retheme Gottlieb's Volcano as one pinball machine with two ways to play. Players can revisit the original game or discover a new ruleset, with the video screen providing a common entry point and presenting each game as it plays.

## What Changes

- Give players a shared attract mode where they can choose and start either game. Return to that attract mode when the game ends.
- Provide a faithful recreation of the original Volcano rules and play behavior for one to four players.
- Provide a second game with its own rules and play experience on the same machine.
- Use a Godot video display in both games in place of traditional player displays, with MPF running the machine and gameplay.

This proposal sets the overall release goal. Detailed Volcano rule mapping, the new game's rules and player count, and the choice of which game to build first belong to follow-up planning.

## Capabilities

### New Capabilities

- `game-selection` lets players choose either game from a shared attract mode and returns them there after play.
- `video-display` presents selection and in-game information on the same screen.
- `classic-volcano` recreates original Volcano gameplay for one to four players.
- `rethemed-game` provides a distinct game and ruleset on the Volcano machine.

### Modified Capabilities

## Impact

The existing MPF machine configuration, gameplay modes, and Godot project provide the starting point. The current attract carousel and score slide provide reusable presentation pieces. The two games will share switch, coil, lamp, and ball-device configuration. Validation will cover virtual play and play on the physical Volcano machine.
