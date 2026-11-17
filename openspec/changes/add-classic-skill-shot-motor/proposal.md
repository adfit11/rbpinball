# Proposal

## Why

Classic serves each ball through an unswitched shooter lane, but its skill shot cam never moves. The cam needs the motor running while a served ball waits in the lane. The green button should stop the cam so the player can aim at the frozen lit top drop target. The cabinet check on 2026-11-17 showed the motor runs only while lamp output 12 and the game-over relay (L0) are both held on. The configured 5,000 ms pulse on coil 112 is capped at 255 ms by LISY and did not move the motor.

## What Changes

- Run the skill shot motor 1 s after Classic serves a ball to the shooter lane. This covers each ball start, including extra balls, and each lock replacement ball.
- Stop the motor when the green button is pressed, on the first playfield switch hit after that serve, at a safety timeout, on tilt or slam tilt, or at ball end, whichever comes first.
- Drive the motor as a held output on lamp 12, the same way the game-over relay and return gate are driven. Replace the `c_skill_motor` pulse coil and update the diagnostic coil panel and survey to match.
- Keep the existing top drop rotation, the green freeze shared with the craters, and the lit drop award unchanged. A lit top drop hit still scores 5,000 points times the playfield multiplier, adds one bonus multiplier, and readies the ball save, whether or not the player froze the lamps. A ball passing through the gap left by a down target scores nothing.
- Leave multiball release and ball save kicks without the motor, because neither goes through the shooter lane.

## Capabilities

### New Capabilities

### Modified Capabilities

- `classic-volcano`: adds a requirement that Classic runs the skill shot motor for each shooter-lane serve and stops it on green, first playfield contact, timeout, tilt, or ball end.

## Impact

Affects the Classic MPF modes and custom code, `config/config_coils.yaml`, the diagnostic coil panel and survey, and the MPF tests. Modern, attract, and the existing drop, crater, and ball-save rules keep their behavior. The cabinet must confirm the motor run and stop and the timeout length.
