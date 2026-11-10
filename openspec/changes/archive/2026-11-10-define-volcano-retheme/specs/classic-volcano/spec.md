# Spec Delta

## Purpose

Recreate the rules and play behavior of Gottlieb's original Volcano on the rethemed machine.

## ADDED Requirements

### Requirement: Reproduce original Volcano gameplay
The classic game SHALL reproduce original Volcano scoring, feature progression, ball and turn handling, and end-of-game behavior for the agreed reference machine and settings.

#### Scenario: A player completes a documented Volcano sequence
- **WHEN** a player completes a shot or feature sequence documented for the reference game
- **THEN** the classic game awards the corresponding points and advances the feature and ball state as the reference game does

### Requirement: Support one to four classic players
The classic game SHALL support one to four players in a session and track each player's score and turn independently.

#### Scenario: One player plays a classic game
- **WHEN** one player starts a classic game and plays through its allotted turns
- **THEN** the machine completes the game using the original single-player rules

#### Scenario: Four players join a classic game
- **WHEN** four players join within the allowed entry period and take their turns
- **THEN** the machine rotates through all four according to the original rules and credits each player's points to that player's score
