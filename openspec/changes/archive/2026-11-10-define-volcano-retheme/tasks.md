# Tasks

## 1. Shared machine and display

- [ ] 1.1 Scope MPF gameplay mode startup and teardown to the selected game while keeping the shared ball devices, tilt, and game-over relay lifecycle. Verify in virtual MPF that the selected modes start, stop at game end, and leave the machine ready for another game. Run the existing relay and tilt checks.
- [ ] 1.2 Wire cabinet navigation and confirmation through the shared attract mode. Verify in virtual MPF that one confirmation starts one session, attract lights stop during play, and the selector is available again at game over.
- [ ] 1.3 Connect the Godot attract and gameplay displays to MPF. Verify in virtual play that the highlighted choice, game in progress, score, and ball or turn on screen follow MPF state.

## 2. Playable games

Either game can be developed first. Bring up the shared flow with that game before integrating the second.

- [ ] 2.1 Define the classic game's rule-level acceptance scenarios in a follow-up OpenSpec change. Record the original Volcano reference and operator settings, and map scoring, feature sequences, player entry, turns, and ball handling to that reference.
- [ ] 2.2 Deliver classic Volcano against the follow-up spec. Verify its reference scenarios and play complete one- and four-player sessions with independent scores and the expected turn order.
- [ ] 2.3 Define the new game's rule-level acceptance scenarios in a follow-up OpenSpec change. Record its objectives, scoring, progression, player count, and game-end conditions.
- [ ] 2.4 Deliver the new game against the follow-up spec. Verify its feature and progression scenarios and play a complete session through game over.

## 3. Cabinet integration

- [ ] 3.1 Play the two games consecutively in both orders in virtual MPF and Godot. Verify correct rule selection, fresh session state, live video updates, and return to shared attract after each game.
- [ ] 3.2 Repeat the two-game flow on the physical Volcano cabinet. Verify cabinet controls, the video screen, ball handling, tilt, and the game-over relay through the transitions.
