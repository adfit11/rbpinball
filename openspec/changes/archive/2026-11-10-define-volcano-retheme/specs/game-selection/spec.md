# Spec Delta

## Purpose

Give players a common place to choose which Volcano game to play on the machine.

## ADDED Requirements

### Requirement: Choose a game from shared attract
The machine SHALL present both games in a shared attract mode and let players select and confirm the game they want to start.

#### Scenario: Machine becomes ready to play
- **WHEN** the machine starts and is ready for play
- **THEN** it enters the shared attract mode and makes both game choices available

#### Scenario: Player starts a game
- **WHEN** a player confirms either choice in attract while the machine is ready to start a game
- **THEN** the machine leaves attract and starts the chosen game

### Requirement: Keep the selected game active for the session
The machine SHALL keep the selected ruleset active for the duration of the game.

#### Scenario: Cabinet controls are used during play
- **WHEN** a player uses a cabinet control during an active game
- **THEN** the machine handles the input in the context of that game and keeps the same ruleset active

### Requirement: Return to shared attract after play
The machine SHALL return to the shared attract mode when either game ends.

#### Scenario: Players finish a game
- **WHEN** either game ends
- **THEN** the machine makes both game choices available again through the shared attract mode
