# Design

## Context

MPF already defines the machine hardware in `config/` and starts gameplay features from the ball-scoped `base` mode. The current attract mode pairs an MPF carousel with a Godot slide and an attract light show. The Godot base slide displays score, ball, and player information. The existing relay test covers the game and tilt lifecycle in MPF's virtual environment. These are starting points for the retheme. The original rules still need to be mapped and verified.

## Goals / Non-Goals

- Keep one machine configuration and lifecycle for both games, including the existing ball devices, tilt, and game-over relay behavior.
- Keep each game's rules and session state scoped to that game so either can evolve independently.
- Define the shared lifecycle and display responsibilities here. Leave feature-by-feature rule mapping and screen artwork to each game's design.

## Decisions

- **Use a game selection for the whole session.** MPF owns the selected game and activates the corresponding gameplay modes through the game and ball lifecycle. The two player-facing games can each use several MPF modes. Clear game-specific state at game end so the next choice starts a fresh session.
- **Build on the existing attract and cabinet inputs.** Reuse the attract carousel integration and light-show lifecycle where they fit. Use the existing flipper switches for navigation and Start for confirmation as the initial control mapping. MPF handles Start in the current context so confirming a choice starts a single game and later Start presses can join players when the active rules allow it.
- **Keep gameplay state in MPF and presentation in Godot.** Godot renders the shared selector and each game's play display using selection, score, ball, and player information supplied through the existing MPF-Godot integration. Game transitions drive the display so that it follows the game actually in progress.

## Risks / Trade-offs

- The existing ball-start path launches the same feature modes for every game. Scope those feature launches to the selected game and verify consecutive sessions in both orders.
- Start serves different purposes in attract and gameplay. Verify that a single confirmation starts exactly one game with one initial player, and that subsequent join inputs obey the active game's rules.
- The current gameplay code is a partial starting point for classic mode. Establish the original rules and operator settings from a documented reference before treating scoring, ball handling, or turn transitions as faithful.

## Migration Plan

Bring up the shared selection and display flow with the first playable game in virtual MPF and Godot, then verify it on the cabinet. Keep the shared flow reusable for the second game and verify the two-choice flow once both games are playable. Use the existing relay and tilt checks during integration.

## Open Questions

- Which game should be the first playable milestone?
- Which original machine and operator settings should define classic fidelity?
- What are the new game's objectives, progression, and supported player count?
