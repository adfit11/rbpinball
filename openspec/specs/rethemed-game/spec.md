# Rethemed Game Specification

## Purpose

Run the current Volcano gameplay as Modern and give it a boundary for future rules and presentation.

## Requirements

### Requirement: Preserve current play in Modern
Modern SHALL run the current gameplay for the confirmed roster, including three balls per player, existing scoring, feature progression, sounds, and gameplay display.

#### Scenario: Modern players take their turns
- **WHEN** a Modern session starts with the confirmed roster and players play through their turns
- **THEN** the machine follows the existing ball and turn order and shows the active player, score, and ball as it does today

#### Scenario: Modern scoring switches are hit
- **WHEN** the active Modern player hits a bumper, outlane, or right drop
- **THEN** the game awards the existing 1,000, 100, or 5,000 points respectively and plays the associated sound

#### Scenario: Modern player triggers the left-return feature
- **WHEN** the active Modern player hits the left return under the current hurry-up rules
- **THEN** the existing hurry-up sequence runs, including its timer, score opportunity, display, and sound

### Requirement: Keep Modern features within Modern sessions
Modern's scoring rules and feature presentation SHALL be active only in Modern sessions, including when the same cabinet switches are used by Classic.

#### Scenario: A game follows a game of the other type
- **WHEN** players start Classic after Modern or Modern after Classic
- **THEN** the new session starts with fresh state and only its own rules and presentation respond to playfield hits
