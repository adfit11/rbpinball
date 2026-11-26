# Classic Volcano Specification

## Purpose

Recreate Gottlieb Volcano's three-ball Classic game for one to four players, with live scores and feature cues on the cabinet video screen.

## Requirements

### Requirement: Announce and serve Classic
When a Classic session starts, the cabinet SHALL show a Classic started notice on the video screen and serve the first player's ball to the shooter lane.

#### Scenario: Classic begins
- **WHEN** the players confirm a Classic session and the cabinet starts it
- **THEN** the video screen identifies Classic and player one, and the machine serves one ball to the shooter lane

### Requirement: Play a three-ball Classic session
Classic SHALL give the confirmed one to four players three scheduled balls each in player order, plus any extra balls earned under Classic rules. Classic SHALL return to shared attract after the last turn and its bonus complete.

#### Scenario: Four players complete their first scheduled balls
- **WHEN** the four confirmed players drain their first scheduled balls and finish their bonuses
- **THEN** turns have advanced from player one through four and player one receives their second scheduled ball

#### Scenario: A player earns an extra ball
- **WHEN** a player earns an extra ball and drains
- **THEN** that player plays the extra ball before the game advances to the next scheduled turn

#### Scenario: The final turn completes
- **WHEN** the final player's last scheduled or earned ball drains and any bonus has been counted
- **THEN** Classic ends and shared game selection is available again

### Requirement: Award Classic shot scoring and bonus
Classic SHALL apply the original three-ball scoring and bonus rules for the features in this change and credit points to the player who earned them.

#### Scenario: A player hits the two bumper groups
- **WHEN** an active Classic player hits a top bumper and a bottom bumper once each in three-ball play
- **THEN** the player receives 1,000 points for the top hit and 100 for the bottom hit

#### Scenario: A player drains with bonus
- **WHEN** a player drains with earned bonus on an eligible ball
- **THEN** the game counts the bonus with the applicable bonus multiplier before handing off the turn

### Requirement: Advance Classic playfield features
Classic SHALL run drop-target and crater progression, freeze, playfield multipliers, saucer and seismic collection, fire-pit and outlane extra-ball rules, and the return gate and ball saver according to the three-ball rules.

#### Scenario: A Classic multiplier is active
- **WHEN** the player earns a timed playfield multiplier and hits an eligible scoring shot
- **THEN** the game applies the multiplier during its active period and returns to the normal award after it expires

#### Scenario: The player collects seismic bonus
- **WHEN** the player shoots the saucer with seismic collection lit
- **THEN** the game counts the seismic award for that player and releases the held ball when collection finishes

#### Scenario: A lit feature requests a mechanism
- **WHEN** a Classic shot earns a gate, ball saver, or extra-ball opportunity
- **THEN** the game indicates the earned feature and applies its award and mechanism behavior at the qualifying point in play

### Requirement: Start and complete Classic multiball
Classic SHALL distinguish qualifying a lock from capturing a ball and use the subway to stage and release three-ball multiball. Lock and release state SHALL reconcile with the balls actually available.

#### Scenario: The player completes a three-ball lock
- **WHEN** the player qualifies and captures the three required balls
- **THEN** the game serves the required replacement balls during qualification and starts three-ball multiball after the third capture

#### Scenario: A second multiball is earned
- **WHEN** the first multiball ends and the player completes another three-ball lock sequence
- **THEN** the lock sequence starts from its cleared state and three-ball multiball can start again

### Requirement: Present Classic on the video screen
Classic SHALL show scores for all joined players, highlight the active player, show the ball number, and present bonus, multiplier, and lock or multiball cues from the current game state.

#### Scenario: A score and then the active player change
- **WHEN** a Classic player scores and play advances to the next player
- **THEN** the screen retains each player's score and highlights the new active player with the correct ball number

#### Scenario: Feature state changes
- **WHEN** a Classic bonus counts down, a multiplier changes, or a lock is captured
- **THEN** the screen reflects the corresponding game state without changing the award or timing

### Requirement: Isolate Classic sessions
Classic rules, timers, and presentation SHALL run only for Classic and reset at their applicable turn or game boundary.

#### Scenario: The cabinet switches between games
- **WHEN** players finish Classic and select Modern, or finish Modern and select Classic
- **THEN** the new game starts with fresh session state and responds to shared switches using only its own rules and presentation

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

### Requirement: Enter Classic high scores
When a Classic game ends with a score on the Classic Hall of Fame, Classic SHALL let the player enter initials on its own board, kept apart from Modern's. A tap of the right green button SHALL move to the next letter, a 2 s hold SHALL choose it, and the flippers SHALL move left and right.

#### Scenario: Entering Classic initials
- **WHEN** a Classic high score is being entered and the player taps green, then holds green for 2 s
- **THEN** the next letter is highlighted and then chosen, and the finished initials go on the Classic board only
