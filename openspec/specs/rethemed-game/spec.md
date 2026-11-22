# Rethemed Game Specification

## Purpose

Run the current Volcano gameplay as Modern and give it a boundary for future rules and presentation.

## Requirements

### Requirement: Keep Modern features within Modern sessions
Modern's scoring rules and feature presentation SHALL be active only in Modern sessions, including when the same cabinet switches are used by Classic.

#### Scenario: A game follows a game of the other type
- **WHEN** players start Classic after Modern or Modern after Classic
- **THEN** the new session starts with fresh state and only its own rules and presentation respond to playfield hits

### Requirement: Introduce Modern with a rules splash
When a Modern game starts, the screen SHALL show a placeholder splash that introduces the juke joint, the aim of the game, and the basic rules (earn nickels, play songs at the jukebox, fill the guest list) before the first ball is served.

#### Scenario: Modern is started
- **WHEN** players confirm Modern and its roster
- **THEN** the rules splash is shown, and play continues to the first ball

### Requirement: Name the club locations
Modern SHALL treat five shots as club locations, each with a lamp: Bar (saucer, L47), Kitchen (fire pit, L45), Bandstand (spinner, L46), Coat Check (spot target, L43), and the Booths (the whole right drop bank, L29 plus the drop lamp L19–L23 of every target still standing). Any right-bank target hit SHALL visit the Booths. A location SHALL refuse a wrong-location visit at most once every 3 s. The kicking target (switch 26) SHALL score as a plain switch.

#### Scenario: A location is named on screen
- **WHEN** any Modern feature directs the player to a location
- **THEN** the screen uses the location's club name and the location's lamp is driven

### Requirement: Flash lamps to direct shots
Modern SHALL flash a shot's lamp whenever it directs the player to make that shot, and SHALL light a lamp steadily when a feature is lit or held there. When a lamp is both directing a shot and showing a held feature, the flash SHALL take precedence.

#### Scenario: The Kitchen is directed while an extra ball is lit
- **WHEN** the extra ball is lit at the Kitchen and the nickel hunt also directs the Kitchen
- **THEN** L45 flashes

### Requirement: Score Modern base play
Before the song multiplier, Modern SHALL score these values (all tunable): 1,000 for bumpers, the 10-point standups, the rollunder, the left return, and the outlanes; 500 per spin; 5,000 per drop target; 25,000 per completed drop bank; 10,000 per club location hit; 25,000 per nickel handed over; and 10,000 per crater entry, or 25,000 for a lit crater.

#### Scenario: A drop target is hit
- **WHEN** the player hits an unlit drop target with a 1x song multiplier
- **THEN** 5,000 points are scored

#### Scenario: Scoring with a song multiplier
- **WHEN** the player hits a bumper with a 3x song multiplier
- **THEN** 3,000 points are scored

### Requirement: Run Classic's crater cascade in Modern
Modern SHALL light the craters with Classic's cascading crater lights on L24-L27. Green SHALL freeze the cascade as it does in Classic, except while the jukebox selector or a song mode uses green.

#### Scenario: The player freezes the craters
- **WHEN** no selector or mode uses green and the player taps green
- **THEN** the crater lamps freeze as they do in Classic

### Requirement: Reset completed drop banks and reward the right bank
A completed drop bank SHALL score 25,000 and pop back up at once; its bank lamp (L28 or L29) SHALL stay lit until both banks have been completed, which drops a nickel on the floor. Completing the right bank SHALL also add one Standing Ovation step for the ball, show "EVERY BOOTH IS FULL!" with the new multiplier, and play a hostess line. The drop lamps SHALL cascade only until the ball is in play; then they light only as part of the Booths, when something directs a shot there.

#### Scenario: The right bank is completed
- **WHEN** the player knocks down all five right-bank targets
- **THEN** Standing Ovation rises one step, the screen shows "EVERY BOOTH IS FULL!", and the bank resets

### Requirement: Drop the Needle
Modern SHALL run Classic's skill shot motor for each shooter-lane serve. It SHALL rotate the lit drop on L19-L23 and freeze it with green, the same as Classic. A lit drop hit SHALL score 50,000, add one Standing Ovation step for the ball, and ready the ball saver. The screen SHALL call it "Drop the Needle".

#### Scenario: The player drops the needle
- **WHEN** the player stops the cam with green and the plunged ball hits the lit top drop
- **THEN** 50,000 scores, the screen shows "Drop the Needle", Standing Ovation rises one step, and the ball saver is ready

### Requirement: Use only the manual ball saver
Modern SHALL NOT re-serve a drained ball automatically. Its only ball save SHALL be the Classic manually operated ball saver. Drop the Needle readies it, its relay is pulsed, and its inserts light steadily while it is ready. It SHALL clear when used, on tilt, and at ball end.

#### Scenario: A ball drains with no saver ready
- **WHEN** the ball drains down the centre with the ball saver not ready
- **THEN** the ball ends

### Requirement: Multiply the bonus by Standing Ovation
The end-of-ball bonus SHALL be 100 per bumper hit, 2,500 per club location hit, 1,000 per drop target, and 25,000 per song played this ball. It SHALL be multiplied by Standing Ovation: 1 plus the songs completed this ball plus Drop the Needle steps, capped at 5x. The playfield's 2x-5x lamps (L4-L7) SHALL show the current level by lighting the lamp for that level only, the back-box screen SHALL NOT show it, and Standing Ovation SHALL reset every ball.

#### Scenario: Two songs completed this ball
- **WHEN** a ball ends after the player completed two songs and made no Drop the Needle
- **THEN** the bonus is counted at 3x, and lamp L5 (3x) is lit when the ball ends

### Requirement: Award Modern extra balls at the Kitchen
The player's third and seventh songs SHALL each light an extra ball at the Kitchen when the song ends, so no song mode starts with an extra ball lit. A song cut short by a drain or tilt SHALL NOT light one. At most one extra ball SHALL be lit at a time, and a player SHALL earn at most two per game. Entering the Kitchen SHALL collect a lit extra ball and light shoot again (L3). A lit, uncollected extra ball SHALL be lost at drain.

#### Scenario: The third song lights an extra ball
- **WHEN** the player's third song ends and no extra ball is lit
- **THEN** L45 lights for the extra ball, and entering the Kitchen awards it

#### Scenario: The extra-ball limit is reached
- **WHEN** a player who has earned two extra balls this game reaches their seventh song
- **THEN** no extra ball is lit

### Requirement: Tilt Modern after one warning
Modern SHALL give one tilt warning. The next tilt-bob activation in the same ball SHALL tilt the ball, ending any song and multiball, clearing the ball saver, and voiding that ball's bonus.

#### Scenario: The second tilt-bob activation
- **WHEN** the player has received a warning and the tilt bob activates again in the same ball
- **THEN** the ball tilts and no bonus is counted

### Requirement: Enter Modern high scores
When a Modern game ends with a high score, Modern SHALL let the player enter initials. A green tap SHALL cycle the letter, and the *select* action SHALL confirm it.

#### Scenario: Entering initials
- **WHEN** a high score is being entered and the player taps green three times, then performs *select*
- **THEN** the current letter advances three places and is confirmed

### Requirement: Map select to one replaceable input
Modern SHALL treat *select* as one input action, used by the jukebox, the high-score entry, and any other choice. It SHALL currently be a 2 s hold of the right green button, and it SHALL be possible to remap it to a different switch, such as a wired left green button, without changing the features that use it.

#### Scenario: Select is remapped
- **WHEN** *select* is mapped to another switch
- **THEN** the jukebox and high-score entry confirm with that switch, and a right green hold no longer selects
