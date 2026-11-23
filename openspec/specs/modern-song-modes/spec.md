# modern-song-modes Specification

## Purpose
Gives each Modern jukebox song a short, artist-neutral challenge, with comparable rewards for a successful run.

## Requirements

### Requirement: Time each mode by its song
A song mode SHALL run for its round length: 60 s unless the mode sets a shorter round, or the whole song if the song file is shorter. Full-length song files SHALL NOT lengthen a round. When the round ends before the song, the song SHALL fade out over 2 s instead of stopping abruptly. The timer and the song SHALL pause while the ball is held in the saucer or the fire pit, and resume when the ball is released. Subway trips SHALL NOT pause them.

#### Scenario: The ball is held during a song
- **WHEN** the ball is held for 1 s in the fire pit during a song
- **THEN** the remaining song time is the same when the ball is released

#### Scenario: A full-length song is chosen
- **WHEN** the chosen song file is three minutes long
- **THEN** the mode ends after 60 s and the song fades out

#### Scenario: A 45 s round ends
- **WHEN** Jukebox jackpot has run for 45 s
- **THEN** the mode ends and the song fades out

### Requirement: End the mode on drain
A drain SHALL end the active song mode immediately, and the song SHALL still count as played.

#### Scenario: The ball drains mid-song
- **WHEN** the ball drains during a song mode
- **THEN** the mode ends, the player keeps the points earned, and the song's L33-L42 lamp stays lit

### Requirement: Track completed modes
A mode SHALL count as completed when its goal is met. A completed mode SHALL pay a 250,000 completion award and count toward Standing Ovation for that ball. Played and completed modes SHALL be tracked separately for each player.

#### Scenario: A mode is completed
- **WHEN** the player meets a mode's goal
- **THEN** 250,000 scores, the mode is recorded as completed, and Standing Ovation rises one step

### Requirement: Suspend the nickel hunt during a song
While a song mode runs, Modern SHALL NOT direct the nickel hunt, and location shots SHALL follow the mode's rules. The nickel hunt SHALL resume from the same progress when the song ends.

#### Scenario: A song ends
- **WHEN** a song ends with the player one shot into a 3-shot nickel
- **THEN** the nickel hunt resumes and flashes a location with two shots still needed

### Requirement: Assign the modes to artists
Each artist slot SHALL run one mode:

| Slot | Artist | Mode |
|---|---|---|
| 1 | Louis Jordan | Hurry-up |
| 2 | Ruth Brown | Ladder |
| 3 | Big Joe Turner | Build and collect |
| 4 | LaVern Baker | Roving shot |
| 5 | Wynonie Harris | Jukebox jackpot |
| 6 | Big Mama Thornton | Party time |
| 7 | Etta James | Order up |
| 8 | Ray Charles | Request night |
| 9 | Joe Liggins | Dance floor |
| 10 | Hit me! | Hit me! |

#### Scenario: Ruth Brown is chosen
- **WHEN** the player chooses Ruth Brown
- **THEN** the Ladder mode runs for her song

### Requirement: Mode 1 Hurry-up
One random location SHALL light with a value draining from 1,000,000 to 100,000 over 20 s. Collecting it SHALL pay the current value and complete the mode. Reaching 100,000 uncollected SHALL fail the mode. Either outcome SHALL end the mode immediately. The screen SHALL show a stopwatch ring emptying with the seconds left, the draining value and the target; it SHALL turn from green to red, throb faster through the last 5 s, and burst on a collect or shake on a miss.

#### Scenario: The hurry-up is collected
- **WHEN** the player hits the lit location while it shows 700,000
- **THEN** 700,000 scores, the mode is completed, and the mode ends

#### Scenario: The hurry-up bottoms out
- **WHEN** the value reaches 100,000 without a collect
- **THEN** the mode fails and ends

### Requirement: Mode 2 Ladder
The round SHALL last 60 s. The Kitchen SHALL light for four rungs worth 75,000, 150,000, 225,000, and 300,000. Each Kitchen hit SHALL pay the next rung, hold the ball 2 s, and show the rung climbed with the next rung's value. The goal card SHALL show the rungs climbed as progress dots and the next rung's value. The fourth rung SHALL complete and end the mode. If the song ends first, the player SHALL keep the rungs earned.

#### Scenario: The top rung is reached
- **WHEN** the player makes the fourth Kitchen hit
- **THEN** 300,000 scores, the mode is completed, and the mode ends

#### Scenario: A rung is climbed
- **WHEN** the player makes the second Kitchen hit
- **THEN** 150,000 scores, a "RUNG 2!" screen shows the next rung's value of 225,000, and the MC calls the climb

### Requirement: Mode 3 Build and collect
Each spin SHALL add to a pot. The per-spin amount SHALL start at 5,000 and grow by 1,250 each spin. A Bar hit SHALL pay the pot plus 50,000, then reset the pot and the per-spin amount. Collecting can repeat until the song ends. Three collects SHALL complete the mode. An uncollected pot SHALL be lost. Each spin SHALL show a spinning record on screen with the pot and the amount just added; it SHALL disappear 1.5 s after the last spin.

#### Scenario: The pot is collected
- **WHEN** the player has spun three times and then hits the Bar
- **THEN** the pot of 5,000 + 6,250 + 7,500 plus 50,000 scores, and the next spin adds 5,000

#### Scenario: The song ends with a pot
- **WHEN** the song ends with an uncollected pot
- **THEN** the pot is lost

### Requirement: Mode 4 Roving shot
One location SHALL light and move to a different random location every 6 s. Hitting it SHALL pay 250,000. Three hits SHALL complete and end the mode. A green tap SHALL freeze the roving shot once per mode for 6 s. Unlit locations SHALL score normally.

#### Scenario: The player freezes the roving shot
- **WHEN** the player taps green during Roving shot for the first time
- **THEN** the lit location stops moving

### Requirement: Mode 5 Jukebox jackpot
The round SHALL last 45 s. All four crater lamps SHALL light. Each crater entry SHALL pay a jackpot of 150,000, 200,000, 250,000, or 300,000 for craters 1-4, plus 25,000 per jackpot already collected. The ball SHALL kick straight back without locking or opening the selector. Three jackpots SHALL complete and end the mode. The goal card SHALL show the jackpots collected as progress dots and the current value of each crater.

#### Scenario: The second jackpot
- **WHEN** the player has one jackpot and enters crater 4
- **THEN** 325,000 scores and the ball is kicked back

#### Scenario: The third jackpot
- **WHEN** the player collects a third jackpot
- **THEN** the mode is completed and ends, and the song fades out

### Requirement: Mode 6 Party time
All scoring SHALL be doubled for the song, on top of the song multiplier. Its ambient lamps SHALL wander all over the table, inviting the player to play anywhere. The Bouncer ball saver SHALL stay ready and re-arm after each save. If the ball is still in play when the song ends, the mode SHALL be completed and pay a 600,000 last-dance award.

#### Scenario: The Bouncer saves during Party time
- **WHEN** the ball enters the left outlane and the Bouncer saves it
- **THEN** the Bouncer re-arms and stays ready

#### Scenario: The ball survives the song
- **WHEN** the song ends with the ball in play
- **THEN** 600,000 scores and the mode is completed

### Requirement: Mode 7 Order up
The Kitchen SHALL light first. A Kitchen hit SHALL pay 75,000, hold the ball 1 s, and name one random table among the Bar, Bandstand, Coat Check, and the Booths. The cook SHALL announce where to take the order, and the screen SHALL show it. Its value SHALL drain from 900,000 to 100,000. A delivery SHALL pay the value and complete the mode. A cold order SHALL fail it. Either SHALL end the mode.

#### Scenario: The order is delivered
- **WHEN** the order is for the Coat Check and the player hits it showing 600,000
- **THEN** 600,000 scores, the mode is completed, and the mode ends

### Requirement: Mode 8 Request night
All five locations SHALL light. Each SHALL be collectable once, in any order, and go dark once collected, paying 50,000, 75,000, 100,000, 125,000, and 150,000 in collection order. The fifth SHALL also pay a 250,000 last-request award and complete and end the mode.

#### Scenario: The last request
- **WHEN** four locations have been collected and the player hits the fifth
- **THEN** 150,000 plus 250,000 score, the mode is completed, and the mode ends

### Requirement: Mode 9 Dance floor
Both bumper groups SHALL score 5x their normal value for the song. The screen SHALL show the bumper hits and the points. The 25th bumper hit SHALL pay a 550,000 packed-floor award and complete the mode, which keeps paying until the song ends.

#### Scenario: The floor is packed
- **WHEN** the player makes the 25th bumper hit
- **THEN** 550,000 scores, the mode is completed, and bumpers keep scoring 5x

### Requirement: Mode 10 Hit me!
A dial SHALL cycle through the five locations about four times a second, shown on screen as a wheel of the five locations that turns with the lamps and stops where they stop. A green tap, or 5 s without one, SHALL stop it and flash the location it lands on. Hitting that location SHALL pay 250,000 and restart the dial. Three hits SHALL complete and end the mode. Green SHALL drive only the dial during this mode.

#### Scenario: The dial is stopped
- **WHEN** the dial is spinning and the player taps green
- **THEN** the dial stops on a location, which flashes for 250,000, and the craters do not freeze

### Requirement: Present each song mode
Each song mode SHALL have its own designed display, in front of the artist video and the HUD widgets, showing the artist, the song, the time remaining, the mode's goal and progress, and its live values. Examples are the hurry-up value draining, the ladder rungs, the pot, the roving shot, the jackpot values, the bumper count, the order and table, the open requests, and the dial. Each mode SHALL have animated start, completed, and failed screens.

#### Scenario: The ladder overlay
- **WHEN** Ladder is running and the player has climbed two rungs
- **THEN** the overlay shows four rungs with two climbed, the next rung's value, and the song time remaining

#### Scenario: A mode is completed
- **WHEN** a mode's goal is met
- **THEN** a completed screen animates in with the mode's points and the completion award, then clears back to the HUD

### Requirement: Celebrate each mode shot
Each shot that pays a song mode's goal SHALL light every playfield lamp in rows from the bottom of the table to the top, including lamps 1-10, the song and Standing Ovation multiplier lamps and the lava level lamps, flash them all twice, then return them to their normal state. Lamps L8, L15 and L16 drive coils and SHALL NOT be part of it. It SHALL also play the jackpot sound and flash the screen gold. Mode shots include a jackpot, a rung, a hurry-up collect, a pot collect, a roving-shot hit, an order pickup or delivery, a request, and a Hit me! hit.

#### Scenario: A jackpot is made
- **WHEN** the player collects a Jukebox jackpot
- **THEN** the playfield lamps burst from bottom to top and flash, then return to their normal state

### Requirement: Voice each song mode
Each song mode SHALL have callout pools for its start, its progress hits, completion, failure, and running low on time, spoken in character.

#### Scenario: Order up is delivered
- **WHEN** the order is delivered
- **THEN** a random delivered line plays, such as the cook or the patron thanking the player
