# Game Selection Specification

## Purpose

Let players use the Volcano cabinet and video screen to choose a game and set its roster before the first ball is served.

## Requirements

### Requirement: Choose a game on the attract screen
The attract screen SHALL display Classic and Modern together and highlight the selected game. It SHALL explain that the left flipper selects Classic, the right flipper selects Modern, and Start continues to player selection.

#### Scenario: Cabinet enters attract
- **WHEN** the cabinet enters the shared attract screen at boot or after a game
- **THEN** it shows both choices and highlights Modern by default

#### Scenario: Player chooses a game
- **WHEN** the player presses the left or right flipper on the game selection screen
- **THEN** the highlight moves to Classic or Modern respectively and stays there until another selection is made

#### Scenario: Player confirms the game choice
- **WHEN** the player presses Start on the game selection screen
- **THEN** the cabinet opens player selection for the highlighted game and waits in attract for the second confirmation before requesting a start

### Requirement: Choose the player count before play
For either game, the player selection screen SHALL show the chosen game and current count, default to one player, and allow one to four players. It SHALL explain that the left flipper decreases the count, the right flipper increases it, and Start begins the game.

#### Scenario: Player selection opens
- **WHEN** the player confirms either game choice
- **THEN** the player selection screen displays that game and a count of one, regardless of the previous game's roster

#### Scenario: Players adjust the count
- **WHEN** the left or right flipper is pressed on the player selection screen
- **THEN** the count decreases or increases by one respectively within the one-to-four range and the screen updates

### Requirement: Start with the confirmed game and roster
The cabinet SHALL start one session of the confirmed game with exactly the confirmed number of players when Start is pressed on the player selection screen and the start is approved. The confirmed game and roster SHALL remain fixed for that session.

#### Scenario: Four players confirm a game
- **WHEN** Start is pressed with four players selected and the start is approved
- **THEN** the cabinet leaves attract, establishes players one through four before the first turn, and serves one ball for player one

#### Scenario: Start is denied
- **WHEN** the cabinet cannot start the requested game
- **THEN** it keeps the chosen game and player count visible on the player selection screen and allows a new confirmation once the machine is ready

#### Scenario: Players use the cabinet buttons during play
- **WHEN** a player uses a flipper or presses Start after the session begins
- **THEN** the cabinet continues the selected game with the confirmed roster

### Requirement: Return to game selection after play
The cabinet SHALL return to the shared game selection screen when Classic or Modern ends.

#### Scenario: A session ends
- **WHEN** the selected game ends
- **THEN** the cabinet clears its session selection and presents Classic and Modern again with the game selection instructions
