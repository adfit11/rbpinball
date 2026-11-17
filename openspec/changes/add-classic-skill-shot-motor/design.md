# Design

## Context

See proposal.md - Why. Classic already rotates the top drop lamps and freezes them with the craters in `ClassicTargets`. A lit drop hit already posts `classic_ball_save_qualified`, which `classic_gate` turns into the ball-saver relay pulse and lamps 4-6. The trough ejects straight to `playfield` through an unswitched shooter lane, and lock replacements come from the same trough via `multiball_locks.classic_subway_lock.balls_to_replace`.

Cabinet findings from 2026-11-17, made through direct LISY serial commands:

- Holding lamp 12 on while L0 is on runs the motor. Lamp 12 alone, L0 alone, and a 255 ms solenoid pulse on 112 did not.
- No switch in the 89-switch matrix changed while the motor ran, so MPF cannot know the cam position.
- `game_over_relay` (L0) is enabled on `game_started` and `ball_started` and disabled on tilt, slam tilt, and game end.

## Goals / Non-Goals

**Goals:**
- Own the motor in one Classic mode with one start path and one stop path.
- Treat the motor as an on/off output with no position model.

**Non-Goals:**
- Synchronising the lamp rotation with the cam, or changing rotation, freeze timing, or awards.
- Running the motor in Modern, attract, or diagnostics other than the coil panel.

## Decisions

### Drive lamp 12 as a digital output

Replace the `c_skill_motor` coil with a `digital_outputs` entry, `skill_motor`, number 12 with `type: light`, alongside `game_over_relay` and `classic_return_gate`. This uses the LISY lamp on/off command that ran the motor on the cabinet. A pulse coil cannot work, because LISY caps pulse time at 255 ms and its timed pulse did not move the motor. A coil with `allow_enable` would use the solenoid on command on 112, which has not been observed to run the motor.

### A dedicated Classic mode owns the motor

Add `classic_skill_shot` as a code mode that starts with the other Classic modes on `mode_classic_started` and stops on `ball_will_end`. Mode stop always disables the output. Keeping it separate from `ClassicTargets` leaves the existing freeze and award code untouched, and it lets the mode's stop handle ball end.

### Start on each trough eject to the playfield

Start the motor 1 s after `bd_trough` begins ejecting a ball to the playfield while the mode runs, so it does not start together with the release coil. Green, tilt, or ball end during that second cancels the start. Playfield switches are ignored until the motor runs, because the release shakes the spinner contact. This one hook covers scheduled balls, extra balls, and lock replacements, because all of them come from the trough. Multiball release comes from the subway kicker and the ball saver acts at the outlane, so neither goes through this path. Starting on `ball_started` instead would miss lock replacements.

### Stop on first playfield contact after the serve

When the motor starts, arm a one-shot stop on the next activation of any playfield switch. The served ball is the only ball moving, because the locked ball is held in the subway. MPF's `playfield_active` event cannot be used, because the playfield stays active from the previous ball during lock replacements. Exclude switches the served ball cannot reach from the shooter lane or that are not ball contact: the trough and outhole switches, the subway lock and kicker, Start, the green button, tilt, and the test switch. The green button stops the motor through its own handler. It runs alongside `ClassicTargets._freeze`, so one press freezes the lamps and stops the cam.

### Safety timeout, tilt, and ball end

Start a named delay (30 s default) when the motor starts and stop the motor when it expires. Stop on `tilt` and `slam_tilt` through mode handlers. Mode stop on `ball_will_end` covers drains and game end. Disabling L0 on tilt removes motor power anyway, but the lamp 12 state must also clear so the motor does not restart when L0 comes back on at the next ball.

### Diagnostics follow the output change

Update `coil_panel` and `coil_survey` to drive `skill_motor` as a timed hold with `diagnostic_game_relay` on, instead of pulsing `c_skill_motor`. Keep the coil panel's existing behaviour for every other output.

## Risks / Trade-offs

- [The stop switch set is wrong for this playfield, for example the ball touches a switch in the shooter lane, or a switch is missing] → Cover the exclusion list with tests and confirm on the cabinet that a plunged ball stops the motor at first contact.
- [The trough eject event fires before L0 is enabled on ball 1] → L0 has no independent effect on the motor, and lamp 12 stays on until a stop condition. Confirm on the cabinet that the motor starts on the first ball.
- [The cam stops in an awkward position after a timeout] → Accepted: the cam has no home switch, and the player can still play the ball.
- [The motor is not rated for long runs] → The timeout bounds each run. Tune it after cabinet observation.

## Migration Plan

Implement and test in virtual MPF, then apply to the cabinet laptop and verify the start, every stop path, and the lit-drop award with a physical ball. Roll back by reverting the change. The previous coil definition never moved the motor, so no working behaviour is lost.

## Open Questions

- The final safety timeout value. Start at 30 s and adjust after cabinet play.
