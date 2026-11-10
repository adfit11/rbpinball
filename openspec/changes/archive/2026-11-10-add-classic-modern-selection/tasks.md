# Tasks

## 1. Attract and game start

- [x] 1.1 Add the MPF game and player selection stages using the existing flipper and Start switches. Test the initial Modern highlight, both game choices, the first Start advancing without starting a game, and the player count default and bounds using virtual cabinet switch events.
- [x] 1.2 Route the second confirmation through MPF start approval and commit the game and player count once. Verify one game starts on acceptance and a denied request preserves the choices for retry. Verify that a new attract session starts from the default selection.
- [x] 1.3 Initialize the confirmed roster through MPF before the first turn and apply the selected game's ball limit. Test that both games start with the exact confirmed roster at counts one through four, serve the first ball once, and keep the roster fixed when Start is pressed during play.
- [x] 1.4 Build the Godot selection screens and bind them to MPF stage, game, and count. Verify in virtual MPF and Godot that the instructions, initial highlight, and count are visible on entry, update with cabinet inputs, and remain visible during a denied start.

## 2. Classic and Modern gameplay entry points

- [x] 2.1 Restrict the current ball and feature modes to Modern. Verify Modern scoring for bumpers, outlanes, and right drops, and confirm the existing hurry-up, score display, and associated sounds in virtual play.
- [x] 2.2 Add the Classic entry and Godot notices. Test that Classic announces its start, serves one ball per player, and shows the next player on a drain. Verify a solo game returns to attract on its first drain and a four-player game returns after its fourth, with zero scoring and the Modern features inactive.
- [x] 2.3 Document the game ownership convention alongside the running instructions. Verify the documented virtual controls start both games and that a Modern feature's activation path leads only through Modern-owned modes or events.

## 3. Integrated verification

- [x] 3.1 Adapt the existing relay and three-ball tests to the two-step cabinet start and run them. Verify attract lights, tilt, the relay, and the three-ball Modern flow. Play Classic and Modern consecutively in both orders in virtual MPF and Godot to check fresh state, game-specific presentation, and return to attract.
- [ ] 3.2 Verify the flow on the physical Volcano cabinet. Confirm players can follow the on-screen instructions with the flipper and Start buttons, the first ball reaches the shooter lane in each game, and Classic serves the next player's ball after a drain and returns to attract after the final drain.
