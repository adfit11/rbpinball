# Design

## Context

The attract carousel currently rotates through title, credits, last scores, and the MPF logo. Its timer and cabinet flippers change the displayed page. MPF's built-in attract code also watches Start and requests a game when the button is released. The ball-scoped `base` mode starts unconditionally on `ball_starting` and is the entry point for the current gameplay and Godot score display.

The cabinet already has left and right flipper switches and a Start switch. The trough releases to the playfield through the mechanical shooter lane, which has no switch of its own.

## Goals / Non-Goals

- Keep the cabinet flow and the committed game and roster in MPF. Render those decisions in Godot using the existing integration.
- Give each game an entry point that owns its rules and presentation. Share machine wiring, the trough and drain, tilt, and the game-over relay.
- Keep this slice focused on starting games and proving isolation. Original Volcano rules, new Modern features, and presentation redesign beyond the selector and Classic notices belong to later changes.

## Decisions

### Give Start one owner in each attract stage

Keep MPF's attract lifecycle and its normal `request_to_start_game` approval. Use a small project-owned attract controller to make the existing Start release path stage-aware. The first release opens player selection. The second captures the displayed game and count and requests a start. While approval is pending, accept one confirmation and hold the confirmed values steady. On denial, keep the player selection screen and allow a retry. On approval, commit the session before the game reads its settings. Cabinet Start stops driving the selector once play begins and does not add players to the confirmed roster.

Use a stable game screen with Modern highlighted on entry and a count screen initialized to one. Each flipper press has a stage-specific effect. The game choice stays visible on the count screen. Remove timed navigation from this flow so the choice on screen is the choice Start confirms.

### Initialize one MPF game with the full roster

Use the built-in MPF game and turn lifecycle for both games. Set the ball limit from the committed game before MPF evaluates `balls_per_game`. Classic uses one ball per player and Modern uses its current three. During the queued game-start phase, use the normal MPF player-add path and hold the first turn until all confirmed players have finished joining. Make the confirmed count the session limit and remove automatic Start-to-join input. Ensure a rejected start or an incomplete roster cannot serve a ball for a partial session.

Both games use the existing ball-start request through the trough. Classic announces the session and shows the active player. MPF advances turns on drains and returns to attract after the last turn. Keep the existing lifecycle resets of the drop banks as shared hardware preparation. The right bank's reset on completing a bank remains a Modern feature.

### Make each game own its entry point and features

Make the current `base` config the Modern ball entry and start it only for a committed Modern game. Keep the existing feature behavior and Godot bindings. Modern's entry owns the activation of bumpers, outlanes, right drops, and hurry-up. Classic has a separate entry and its own slide for the start and turn notices. It uses the same ball devices and physical switches.

For a future Modern feature, put its rules in a Modern-owned MPF mode with a `modern_` name and activate it from the Modern entry or a Modern feature event. Put any feature-specific Godot slide or audio under the same game's ownership. A new Modern rule should need only its own config, a Modern activation point, and its tests. Classic follows the equivalent convention for its own rules. Existing shared switch and device names remain the source of cabinet input. Check that mode handlers, timers, and media are cleaned up at their ball or game boundary.

### Render the selector and Classic notice from MPF state

Use project-owned Godot scenes and the existing MPF-Godot connection. Expose the stage, selected game, and count from MPF as display state that Godot can read when a slide opens and update while it is visible. This keeps the first frame and input-driven changes in sync. Keep the current Modern score, ball, player, and feature slides driven by the existing bindings.

## Risks / Trade-offs

- The built-in attract Start handler can bypass the new flow if left active alongside the selector. Verify the first press never starts a game and the second starts exactly one. Cover a denied request and a successful retry.
- Player addition is asynchronous. Wait for the entire roster before the first turn and cover the four-player case for each game.
- The trough has no shooter-lane switch to confirm arrival. Verify the normal eject path in virtual MPF and verify physical arrival in the lane on the cabinet.
- Shared inputs can accidentally launch an old feature if its start event stays global. Exercise Modern scoring and hurry-up, then hit the same switches during Classic and check the score and presentation.

## Migration Plan

Validate the selector and game lifecycle with virtual MPF and Godot, then use the same switch mappings and game flow on the cabinet. This is the implementation slice for selection and startup from `define-volcano-retheme`. Use the resulting specs as the baseline when the wider plan is next revised.
