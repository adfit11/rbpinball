# Classic Volcano Spec Delta

## ADDED Requirements

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
- **THEN** the skill shot motor stays off

### Requirement: Stop the skill shot cam
Classic SHALL stop the skill shot motor at the first of these: the player presses the green button, the served ball hits any playfield switch, the safety timeout elapses, the machine tilts or slam tilts, or the ball ends. Once stopped, the motor SHALL stay off until the next shooter-lane serve.

#### Scenario: The player stops the cam with the green button
- **WHEN** the motor is running and the player presses the green button
- **THEN** the motor stops, the cam holds its aim, and the crater and top drop lamps freeze as they already do

#### Scenario: The player plunges without pressing green
- **WHEN** the motor is running and the served ball hits a playfield switch
- **THEN** the motor stops

#### Scenario: The ball waits in the shooter lane
- **WHEN** the motor has run for the safety timeout without green or playfield contact
- **THEN** the motor stops

#### Scenario: The machine tilts with the motor running
- **WHEN** the machine tilts or slam tilts, or the ball ends, while the motor is running
- **THEN** the motor stops

### Requirement: Keep the top drop skill shot award
Classic SHALL keep the existing top drop rotation, the green freeze shared with the craters, and the lit drop award. A hit on the lit top drop target SHALL award the same points, bonus multiplier advance, and ball save whether or not the player froze the lamps. A ball passing the gap of a down target SHALL score nothing.

#### Scenario: The aimed ball hits the frozen lit target
- **WHEN** the player freezes the top drop lamps with green and the served ball hits the lit top drop target
- **THEN** the player receives 5,000 points times the playfield multiplier, one bonus multiplier step, and an active ball save with its lamps lit

#### Scenario: The ball hits the lit target without a freeze
- **WHEN** the player does not press green and the served ball hits the currently lit top drop target
- **THEN** the player receives the same lit drop award

#### Scenario: The ball passes a down target
- **WHEN** a lock replacement ball travels through the gap of a top drop target that is already down
- **THEN** play continues with no points or award from that gap
