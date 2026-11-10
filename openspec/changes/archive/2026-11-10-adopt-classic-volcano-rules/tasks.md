# Tasks

## 1. Three-ball Classic in simulation

- [x] 1.1 Set Classic to three scheduled balls per player through the existing selector and MPF game lifecycle. Update the preview tests to verify a solo game, four-player rotation, the confirmed roster, and return to attract after the final scheduled turn.
- [x] 1.2 Port the donor's basic scoring and end-of-ball bonus into Classic-owned modes and record the source revision, MIT notice, and any rule differences resolved against the three-ball reference. Test representative shots and a multiplied bonus, including crediting the correct player before the next turn starts.
- [x] 1.3 Expand the Classic Godot slide to show the start notice, joined players' scores, active player, ball number, and bonus countdown. Verify in virtual MPF and Godot that scores persist across player rotation and the scoreboard follows the current turn through a complete game.

## 2. Playfield features and ball devices in simulation

- [x] 2.1 Port drop-target and crater progression, freeze, and playfield multipliers. Use the shared switch and drop-bank mappings and Classic-owned scoring and shows. Test lit and unlit awards, freeze and resume, target resets, and multiplier expiry in virtual MPF. Verify multiplier feedback in Godot.
- [x] 2.2 Port the saucer and fire-pit captures, seismic collection, and extra-ball rules. Test saucer release after collection, the fire-pit and outlane qualification paths, and the earned extra ball being served to the same player.
- [x] 2.3 Port return-gate and ball-saver behavior. Test qualification, the relay or gate command, and cleanup on the applicable ball or tilt boundary with virtual hardware.
- [x] 2.4 Adapt the subway lock and release rules to the shared three-ball inventory. Test three confirmed captures, replacement serves, release into multiball, return to single-ball play, and a second complete multiball. Cover a player handoff with a partial lock and game end or tilt with balls in the mechanism. Verify the Godot lock and multiball cues follow the actual MPF state.

## 3. Integration and cabinet verification

- [x] 3.1 Run the selection, relay, and Classic rule tests. Play Classic followed by Modern and Modern followed by Classic in virtual MPF and Godot. Verify fresh session state, game-specific scoring and presentation, and a return to attract from both games.
- [x] 3.2 Prepare one cabinet checklist from the final port's switch, coil, and relay references and the existing coil survey. Cross-check the checklist against both the selector and the Classic configuration and record expected behavior and previous observations for each item. This preparation can be completed in simulation.
- [ ] 3.3 Perform the shared cabinet verification when the machine is available. Test every assumed switch, coil, and relay and record switch events, output commands, and observed motion separately. Confirm the flipper inputs for game and player selection, or record their absence and resolve the choice of physical controls before mapping them. Start both games and verify shooter-lane delivery, Classic player and drain transitions, live Godot feedback, and physical three-ball capture and release. Record remaining gaps and use the results for the selection change's cabinet check as well.

## Workflow follow-up

- Sync or archive the selection change's baseline Classic spec before publishing this delta. When publishing the port, update the main capability purpose to describe three-ball Classic gameplay.
