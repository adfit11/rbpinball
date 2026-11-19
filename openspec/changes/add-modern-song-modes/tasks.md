# Tasks

## 1. Framework

- [ ] 1.1 Add `ModernSongMode` with song timing, pause on holds, ending on drain and tilt, the completion award, and the completed and ended events. Verify tests cover each framework scenario in the spec.
- [ ] 1.2 Suspend and resume the nickel hunt around songs. Verify a test shows the progress is kept.
- [ ] 1.3 Map artist slots 1-10 to the modes, with placeholder names and music cuts. Verify a test starts each slot's mode from the jukebox.

## 2. Location modes

- [ ] 2.1 Implement Hurry-up (1) and Order up (7). Verify tests cover collect, bottom out, and delivery.
- [ ] 2.2 Implement Roving shot (4), with the green freeze, and Request night (8). Verify tests cover their scenarios.
- [ ] 2.3 Implement Hit me! (10), with the dial, the green stop, and the auto-stop. Verify tests show green does not freeze the craters.

## 3. Feature modes

- [ ] 3.1 Implement Ladder (2) and Build and collect (3). Verify tests cover the rungs, the holds, the pot reset, and the lost pot.
- [ ] 3.2 Implement Jukebox jackpot (5). Verify tests show the jackpot values, the kick-back, and no lock or selector.
- [ ] 3.3 Implement Party time (6) and Dance floor (9) through scoring factors, the Bouncer re-arm, and their awards. Verify tests cover their scenarios.

## 4. Presentation

- [ ] 4.1 Mock up each mode's overlay and its start, completed, and failed screens as images with transition notes, and get the user's approval. Verify the mockups are delivered.
- [ ] 4.2 Build the approved overlays and result screens with their transitions. Verify each loads in a GMC run and that the HUD stays visible.
- [ ] 4.3 Add each mode's callout pools to the voice script, generate the placeholders, and post the callout events. Verify a test asserts the events for each mode.

## 5. Integration

- [ ] 5.1 Run `~/mpf/bin/python -m pytest tests -q` and `openspec validate --all`, and verify both pass.
- [ ] 5.2 Play each mode on the cabinet and record any tuned values in the settings module.
