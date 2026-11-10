# Proposal

## Why

Volcano needs a cabinet-driven way to start either game with the intended group of players. The first playable slice establishes that shared flow and gives Classic and Modern separate places for their rules, so future features can be developed one game at a time.

## What Changes

- Show Classic and Modern together on the Godot attract screen, with a visible highlight and instructions for the cabinet flipper buttons and Start.
- Use a second screen to choose one to four players for either game. Start the count at one and display the chosen game, count, and instructions before the final confirmation.
- Start a single MPF game with the confirmed game and roster. Return to the shared attract screen after either game ends.
- Start Classic with a visible notification and one ball per player, with no scoring. Serve the next player's ball after each drain until the last player finishes.
- Run the gameplay already in the repo as Modern, including its scoring, features, sounds, and gameplay display.
- Establish separate entry modes and feature ownership so a new rule can be added to one game independently.

This is the first playable slice of [the Volcano retheme plan](../2026-11-10-define-volcano-retheme/proposal.md). Full original-rule fidelity and new Modern rules belong to later changes.

## Capabilities

### New Capabilities

- `game-selection` covers the shared attract screens, game and player selection, and starting the confirmed session.
- `classic-volcano` covers the initial one-ball-per-player Classic game and its on-screen start and turn notices.
- `rethemed-game` covers running the current rules as Modern and isolating those rules to Modern sessions.

### Modified Capabilities

## Impact

Affects the MPF attract and game startup paths, the current ball-scoped gameplay modes, the Godot attract and Classic slides, and cabinet input and game lifecycle tests. Both games use the current machine configuration and MPF ball handling. The selector replaces the current timer-driven attract pages as the cabinet's idle screen.
