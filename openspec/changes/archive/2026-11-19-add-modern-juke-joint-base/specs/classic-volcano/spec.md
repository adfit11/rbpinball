# Classic Volcano Spec Delta

## MODIFIED Requirements

### Requirement: Sweep the skill shot cam for each shooter-lane serve
Classic SHALL run the skill shot motor starting 1 s after it serves a ball to the shooter lane, at each ball start and for each lock replacement ball. Classic SHALL NOT run the motor for balls that enter play without passing through the shooter lane.

#### Scenario: A Classic ball starts
- **WHEN** Classic serves a player's scheduled or extra ball to the shooter lane
- **THEN** the skill shot motor starts 1 s after the release and the cam sweeps while the ball waits in the lane

#### Scenario: A lock replacement ball is served
- **WHEN** a ball is captured during lock qualification and Classic serves a replacement ball to the shooter lane
- **THEN** the skill shot motor runs for the replacement ball

#### Scenario: A ball enters play without the shooter lane
- **WHEN** multiball releases balls from the subway or the ball saver kicks a ball back into play
- **THEN** the skill shot motor stays off

#### Scenario: Modern is selected
- **WHEN** a Modern game serves a ball to the shooter lane
- **THEN** the skill shot motor runs for Drop the Needle under the same start and stop rules
