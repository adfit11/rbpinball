# Spec Delta

## ADDED Requirements

### Requirement: Song stage layout
While a song mode is picked or playing, the screen SHALL show the handbill song stage: the artist video in a 16:9 window, the mode's device with its live values in the left panel, the mode's title, goal, status and round clock in the right panel, and up to four player scores along the bottom. Score slots without a player SHALL show the current player's status.

#### Scenario: Ladder is playing
- **WHEN** Ruth Brown's Ladder mode is live and the player has climbed two rungs
- **THEN** the left panel shows the ladder with the 75,000 and 150,000 rungs ticked and "RUNG 3 OF 4", and the right panel shows LADDER and the round clock

### Requirement: Instructions before the video
After a song is picked, the video window SHALL show the mode's instructions (artist, song, mode title, goal and steps) while the ball is held. The artist video SHALL start in the window only when the ball returns to play.

#### Scenario: A song is picked
- **WHEN** the player picks Louis Jordan
- **THEN** the window shows the HURRY-UP handbill and its steps, and Louis Jordan's video starts when the ball comes back
