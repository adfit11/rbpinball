# Proposal

## Why

Classic currently serves a single scoreless ball per player. Porting the Volcano rules from the local `volcano-rb` project gives Classic a playable ruleset and a basis for checking it against Gottlieb's original game.

## What Changes

- Replace the Classic preview with three scheduled balls per player, scoring, bonus, and earned extra balls. Use the existing attract selector and its confirmed roster of one to four players.
- Port in stages. Start with scoring, end-of-ball bonus, and the Godot scoreboard. Then add the donor's drop and crater progression, multipliers, saucer and seismic collection, fire pit and extra ball, gate and ball saver, and subway multiball.
- Use Godot for the Classic score and ball display and for cues driven by MPF rule state. Keep rule processing and playfield mechanisms in MPF.
- Verify the port in virtual MPF and Godot. Use one cabinet verification task to check every input and output assumed by the port, including the controls for game and player selection.
- Target the three-ball, free-play experience for this change. Five-ball settings, credit and replay accounting, match, and high-score entry are follow-up work.

## Capabilities

### New Capabilities

### Modified Capabilities

- `classic-volcano` moves from the preview in [the selection change](../2026-11-10-add-classic-modern-selection/specs/classic-volcano/spec.md) to a three-ball game with Classic rules and a Godot play display.

## Impact

Affects the Classic MPF modes, rule helpers, Godot presentation, and the device mappings used by Classic. The current selector, player roster, and Modern entry provide the integration boundary.

The selection change is the predecessor for the Classic spec delta. Its virtual implementation is available now. The cabinet visit can verify both changes and provide evidence for each checklist. Publish the selection change's Classic requirements before publishing this delta so the preview requirement can be replaced in order.
