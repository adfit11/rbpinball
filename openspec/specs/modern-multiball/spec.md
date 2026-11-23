# modern-multiball Specification

## Purpose
Defines how a Modern player lights and makes physical subway locks by completing the top drop bank, how other players can steal those locks, and how the Rent Party multiball scores.

## Requirements

### Requirement: Light the lock at the top bank
Completing the top drop bank SHALL light the lock for the current player. Location visits and the right bank SHALL NOT light it. Completing the top bank SHALL light the lock at any time, including during a song or Rent Party, because the ball falls into that bank during those modes; a ball SHALL NOT lock until the song or Rent Party ends. It SHALL NOT light the lock while the subway already holds three balls. The HUD SHALL show "LOCK: TOP BANK" until the lock is lit, then "LOCK IS LIT".

#### Scenario: The top bank lights the lock
- **WHEN** the player completes the top drop bank in base play
- **THEN** the lock is lit, the "THE BACK ROOM IS OPEN" overlay shows, and the MC calls it

#### Scenario: The top bank during a song
- **WHEN** the player completes the top drop bank during a song
- **THEN** the lock is lit, and the next lit crater after the song ends locks the ball

#### Scenario: The right bank does not light the lock
- **WHEN** the player completes the right drop bank
- **THEN** the lock stays unlit

### Requirement: The lit lock goes out at drain
A lit lock SHALL go out at the end of every ball.

#### Scenario: The ball drains with the lock lit
- **WHEN** the ball ends with the lock lit
- **THEN** the player's next ball starts with no lit lock

### Requirement: Lock balls at a lit crater
A lit lock SHALL stay lit until one ball is locked or the ball ends. While the lock is lit, entering a crater lit by the cascading crater lights SHALL lock the ball in the subway and serve a replacement to the shooter lane. Each lock SHALL put the lock out, so every lock needs the top bank completed again. An unlit crater SHALL NOT lock.

#### Scenario: The first lock
- **WHEN** the lock is lit, the subway is empty, and the ball enters a lit crater
- **THEN** the ball stays in the subway, the lock count shows 1, a replacement ball is served, and the lock goes out

#### Scenario: An unlit crater with the lock lit
- **WHEN** the lock is lit and the ball enters an unlit crater
- **THEN** the ball is not locked and returns to play

#### Scenario: A crater entry the switches missed
- **WHEN** a ball rests on subway switch 10 for 1 s, the subway count is empty, and no crater passage in the last 2.5 s explains it
- **THEN** Modern treats it as an unlit crater entry: the ball is not locked and returns to play through the kicker

### Requirement: A lock takes priority over the jukebox
When a crater entry locks a ball while the player holds a nickel, Modern SHALL lock the ball and serve the replacement without opening the selector. The player SHALL keep the nickel for a later lit crater.

#### Scenario: Lock and nickel together
- **WHEN** the lock is lit, the player holds a nickel, and the ball enters a lit crater
- **THEN** the ball is locked, a replacement is served, the selector stays closed, and the player still holds the nickel

#### Scenario: The nickel after a lock
- **WHEN** the player locked a ball holding a nickel and the replacement ball enters a lit crater
- **THEN** the selector opens, because the lock is no longer lit

### Requirement: Keep locks physical and stealable
Locked balls SHALL stay in the subway across turn changes and SHALL NOT be ejected to return them to their owner. The screen SHALL show the subway's lock count at all times. A player's lock SHALL start counting from the balls already in the subway.

#### Scenario: Another player steals the locks
- **WHEN** player 1 locked two balls and player 2 completes the top bank and enters a lit crater
- **THEN** the third lock starts Rent Party for player 2 and the screen shows "GATE CRASHER!"

#### Scenario: The lock count is always shown
- **WHEN** any Modern player is up and the subway holds two balls
- **THEN** the screen shows two balls locked

### Requirement: Start Rent Party with three balls
The third locked ball SHALL start an 8 s build-up: every ball stays in the subway while a rising effect plays and the MC announces the Rent Party over it. When the build-up ends, Rent Party SHALL start, releasing the subway to put three balls in play, and the Rent Party music SHALL loop until the multiball ends. The jukebox SHALL stay closed during Rent Party.

#### Scenario: The third lock
- **WHEN** the subway holds two balls and a third is locked
- **THEN** the build-up plays for 8 s with all three balls held, then Rent Party starts with three balls in play and its music

### Requirement: Pay Rent Party jackpots
During Rent Party, entering a lit crater SHALL pay a jackpot of 250,000 plus 50,000 for each jackpot already paid. After three jackpots, the Bar SHALL light for a 1,000,000 super jackpot. Values are before the song multiplier.

#### Scenario: The third jackpot
- **WHEN** two jackpots have been paid and the ball enters a lit crater
- **THEN** 350,000 scores and the Bar flashes for the super jackpot

### Requirement: End Rent Party at one ball
Rent Party SHALL end when one ball remains in play, after which normal play resumes and the jukebox reopens. Ending a Rent Party SHALL light an extra ball at the Kitchen, subject to the base extra-ball limits.

#### Scenario: Multiball drains to one ball
- **WHEN** two of the three balls drain
- **THEN** Rent Party ends, the jukebox reopens, and an extra ball is lit at the Kitchen

### Requirement: Present the lock and Rent Party
Modern SHALL show the lock state on the HUD, a lock-lit callout, and an animated screen for each lock. It SHALL also show a Rent Party intro, jackpot and super-jackpot screens, a Gate Crasher screen, and a Rent Party total when the multiball ends.

#### Scenario: Rent Party starts
- **WHEN** the third ball is locked
- **THEN** an animated Rent Party intro plays before the balls are released, and the HUD shows the jackpot value

### Requirement: Voice the locks and Rent Party
The lit lock, locks, Rent Party, jackpots, and Gate Crasher SHALL each have in-character callout pools. Gate Crasher lines SHALL taunt the player who stole the locks.

#### Scenario: The lock lights
- **WHEN** the top bank lights the lock
- **THEN** a random lock-lit line plays
