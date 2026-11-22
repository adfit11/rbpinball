# modern-multiball Specification

## Purpose
Defines how a Modern player lights and makes physical subway locks through the guest list, how other players can steal those locks, and how the Rent Party multiball scores.

## Requirements

### Requirement: Fill the guest list
Each club location and each completed drop bank SHALL count once as a guest, making seven possible guests. A guest SHALL count at most once per list, and five guests SHALL fill it. The screen SHALL show the list. A location hit SHALL count toward the guest list and the nickel hunt at the same time.

#### Scenario: A guest arrives
- **WHEN** the player hits the Bandstand for the first time on this list
- **THEN** the Bandstand is ticked on the guest list

#### Scenario: A repeat guest
- **WHEN** the player hits the Bandstand again on the same list
- **THEN** the guest count is unchanged

### Requirement: Reset the guest list at drain
The guest list and its progress SHALL reset at the end of every ball, and a lit lock SHALL go out with it.

#### Scenario: The ball drains with four guests
- **WHEN** the ball ends with four guests on the list
- **THEN** the player's next ball starts with an empty list and no lit lock

### Requirement: Lock balls at a lit crater
Filling the guest list SHALL light the lock for the current player for the rest of the ball. While the lock is lit, entering a crater lit by the cascading crater lights SHALL lock the ball in the subway and serve a replacement to the shooter lane. Locking SHALL continue until the subway holds three balls.

#### Scenario: The first lock
- **WHEN** the lock is lit, the subway is empty, and the ball enters a lit crater
- **THEN** the ball stays in the subway, the lock count shows 1, and a replacement ball is served

#### Scenario: An unlit crater with the lock lit
- **WHEN** the lock is lit and the ball enters an unlit crater
- **THEN** the ball is not locked and returns to play

### Requirement: A lock takes priority over the jukebox
When a crater entry locks a ball while the player holds a nickel, Modern SHALL lock the ball and serve the replacement without opening the selector. The player SHALL keep the nickel for a later lit crater.

#### Scenario: Lock and nickel together
- **WHEN** the lock is lit, the player holds a nickel, and the ball enters a lit crater
- **THEN** the ball is locked, a replacement is served, the selector stays closed, and the player still holds the nickel

### Requirement: Keep locks physical and stealable
Locked balls SHALL stay in the subway across turn changes and SHALL NOT be ejected to return them to their owner. The screen SHALL show the subway's lock count at all times. A player's lock SHALL start counting from the balls already in the subway.

#### Scenario: Another player steals the locks
- **WHEN** player 1 locked two balls and player 2 fills the guest list and enters a lit crater
- **THEN** the third lock starts Rent Party for player 2 and the screen shows "GATE CRASHER!"

#### Scenario: The lock count is always shown
- **WHEN** any Modern player is up and the subway holds two balls
- **THEN** the screen shows two balls locked

### Requirement: Start Rent Party with three balls
The third locked ball SHALL start Rent Party, releasing the subway to put three balls in play. The jukebox SHALL stay closed during Rent Party.

#### Scenario: The third lock
- **WHEN** the subway holds two balls and a third is locked
- **THEN** Rent Party starts with three balls in play

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

### Requirement: Present the guest list and Rent Party
Modern SHALL show the guest list on the HUD with each guest's name and tick, a lock-lit callout, and an animated screen for each lock. It SHALL also show a Rent Party intro, jackpot and super-jackpot screens, a Gate Crasher screen, and a Rent Party total when the multiball ends.

#### Scenario: Rent Party starts
- **WHEN** the third ball is locked
- **THEN** an animated Rent Party intro plays before the balls are released, and the HUD shows the jackpot value

### Requirement: Voice the guest list and Rent Party
The guest list, locks, Rent Party, jackpots, and Gate Crasher SHALL each have in-character callout pools. Gate Crasher lines SHALL taunt the player who stole the locks.

#### Scenario: A guest arrives
- **WHEN** a guest is ticked on the list
- **THEN** a random arrival line for that guest plays
