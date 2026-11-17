# Tasks

## 1. Motor output

- [x] 1.1 Replace the `c_skill_motor` coil in `config/config_coils.yaml` with a `skill_motor` digital output on lamp 12 (`type: light`), and verify MPF loads the config in a virtual run.
- [x] 1.2 Change `custom_code/coil_panel.py` and `custom_code/coil_survey.py` to hold `skill_motor` on for a timed test with `diagnostic_game_relay` enabled, and verify `tests/test_coil_panel.py` covers the hold, its automatic stop, and every other output still pulsing.

## 2. Classic skill shot mode

- [x] 2.1 Add a `classic_skill_shot` code mode that starts on `mode_classic_started`, stops on `ball_will_end`, and disables `skill_motor` on stop. Register it in the machine config and verify a test shows it running in Classic and not in Modern.
- [x] 2.2 Start the motor when `bd_trough` ejects a ball to the playfield, and verify tests show it on at ball start, at extra-ball start, and for each lock replacement ball.
- [x] 2.3 Verify tests show the motor stays off for subway multiball release, ball-saver kicks, and Modern ball starts.
- [x] 2.4 Stop the motor on the green button, and verify a test shows one press stops it while the crater and top drop lamps freeze as before.
- [x] 2.5 Stop the motor on the first activation of a non-excluded playfield switch after the serve, excluding trough, outhole, subway lock and kicker, Start, green, tilt, and test switches. Verify tests show a stop on a playfield hit, including during lock replacement when the playfield is already active, and no stop on an excluded switch.
- [x] 2.6 Stop the motor after a 30 s safety timeout and on `tilt` and `slam_tilt`, and verify tests show each stop and that the motor stays off when the next ball's L0 enable fires.

## 3. Existing award regression

- [x] 3.1 Verify tests show the top drop rotation is unchanged, and that a lit drop hit, frozen or not, awards 5,000 points times the playfield multiplier, one bonus multiplier step, and the ball save with lamps 4-6. Verify that a ball passing a down target's gap scores nothing.

## 4. Integration

- [x] 4.1 Run `~/mpf/bin/python -m pytest tests -q` and `openspec validate --all`, and verify both pass.
- [x] 4.2 On the cabinet, verify the motor starts on ball 1 and a lock replacement ball, and stops on green, first playfield contact, timeout, and tilt. Record the timeout value chosen after play: 30 s kept.
