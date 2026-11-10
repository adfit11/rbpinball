# Spec Delta

## Purpose

Give Classic its own playable session while the original Volcano rules are developed in later changes.

## ADDED Requirements

### Requirement: Announce and serve Classic
When a Classic session starts, the cabinet SHALL show a Classic started notice on the video screen and serve the first player's ball to the shooter lane.

#### Scenario: Classic begins
- **WHEN** the players confirm a Classic session and the cabinet starts it
- **THEN** the video screen identifies Classic and player one, and the machine serves one ball to the shooter lane

### Requirement: Play one scoreless ball per Classic player
Classic SHALL give each selected player one ball in player order. Playfield hits SHALL award zero points.

#### Scenario: A Classic player hits a scoring switch used by Modern
- **WHEN** a player hits a bumper, outlane, right drop, or left return during Classic
- **THEN** the player's score remains zero and Modern's scoring feedback and hurry-up stay inactive

#### Scenario: Another Classic player is waiting
- **WHEN** the active player's ball drains and another player is waiting for a turn
- **THEN** the screen identifies the next player and the machine serves that player's ball

#### Scenario: The last Classic ball drains
- **WHEN** the last selected player's ball drains, including the first drain in a solo game
- **THEN** Classic ends, the cabinet returns to shared attract, and no further ball is served for that session
