# Spec Delta

## Purpose

Provide a single video screen for selecting either Volcano game and following play.

## ADDED Requirements

### Requirement: Show the available games
The video screen SHALL show both game choices and indicate which game the player is about to start.

#### Scenario: Player changes the selection
- **WHEN** a player changes the selected game in attract
- **THEN** the screen indicates the newly selected game before the player confirms

### Requirement: Present live gameplay information
The video screen SHALL serve as the player display for both games and present the score and current ball or turn information for the active game.

#### Scenario: Score changes during play
- **WHEN** an active player scores in either game
- **THEN** the video screen updates to reflect the score awarded by that game's rules

#### Scenario: The active ball or player changes
- **WHEN** the game advances to a new ball or player
- **THEN** the video screen identifies the ball or turn now in play
