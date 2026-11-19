# Rethemed Game Spec Delta

## ADDED Requirements

### Requirement: Introduce Modern with a rules splash
When a Modern game starts, the screen SHALL show a placeholder splash that introduces the juke joint, the aim of the game, and the basic rules (earn nickels, play songs at the jukebox, fill the guest list) before the first ball is served.

#### Scenario: Modern is started
- **WHEN** players confirm Modern and its roster
- **THEN** the rules splash is shown, and play continues to the first ball

### Requirement: Name the club locations
Modern SHALL treat five shots as club locations, each with a lamp: Bar (saucer, L47), Kitchen (fire pit, L45), Bandstand (spinner, L46), Coat Check (spot target, L43), and Back Door (kicking target, the ball-save inserts below switch 26). Until the Back Door lamp output is identified, Modern SHALL direct the Back Door on screen only.

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

### Requirement: Hold completed drop banks
A completed drop bank SHALL stay down until both banks are down or the ball ends, and then both SHALL reset.

#### Scenario: One bank is completed
- **WHEN** the player completes the top bank and the right bank is still up
- **THEN** the top bank stays down and its bank lamp (L28) lights

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
The end-of-ball bonus SHALL be 100 per bumper hit, 2,500 per club location hit, 1,000 per drop target, and 25,000 per song played this ball. It SHALL be multiplied by Standing Ovation: 1 plus the songs completed this ball plus Drop the Needle steps, capped at 4x. Lamps L30-L32 SHALL show 2x-4x, and Standing Ovation SHALL reset every ball.

#### Scenario: Two songs completed this ball
- **WHEN** a ball ends after the player completed two songs and made no Drop the Needle
- **THEN** the bonus is counted at 3x, and L30 and L31 were lit during the ball

### Requirement: Award Modern extra balls at the Kitchen
The player's third and seventh songs SHALL each light an extra ball at the Kitchen. At most one extra ball SHALL be lit at a time, and a player SHALL earn at most two per game. Entering the Kitchen SHALL collect a lit extra ball and light shoot again (L1). A lit, uncollected extra ball SHALL be lost at drain.

#### Scenario: The third song lights an extra ball
- **WHEN** the player's third song starts and no extra ball is lit
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

## REMOVED Requirements

### Requirement: Preserve current play in Modern
**Reason**: Modern now has its own juke-joint ruleset, replacing the original Volcano bumper, outlane, right-drop, and left-return hurry-up rules.
**Migration**: The behaviour Modern players see is defined by this change's requirements and by `modern-jukebox`. The three-balls-per-player turn order is unchanged.
