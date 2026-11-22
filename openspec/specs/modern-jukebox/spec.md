# modern-jukebox Specification

## Purpose
Lets a Modern player earn nickels around the juke joint and spend them at the jukebox to choose artists and play songs. It also tracks song progression across the game.

## Requirements

### Requirement: Direct the nickel hunt to one location
While the player holds no nickel and no song or multiball is running, Modern SHALL light exactly one club location as the next nickel shot, flash its lamp, and name it on screen. After each successful shot that does not complete a nickel, Modern SHALL choose the next location at random, excluding the location just hit.

#### Scenario: A ball starts without a nickel
- **WHEN** a Modern ball starts and the player holds no nickel
- **THEN** one random location flashes and the screen names it as the next shot

#### Scenario: The player hits the directed location
- **WHEN** the player hits the flashing location and the nickel is not yet complete
- **THEN** Modern counts one shot toward the nickel and flashes a different random location

### Requirement: Escalate the nickel cost
The nickels a player earns by location shots SHALL cost 1, 2, 3, 4, and 5 successful shots in turn. After the fifth, the cost SHALL return to 1, and the nickel award points SHALL double each time the cycle restarts.

#### Scenario: The first nickel
- **WHEN** a player who has earned no nickel this game makes one successful location shot
- **THEN** the player is handed a nickel and the next nickel costs 2 shots

#### Scenario: The cycle restarts
- **WHEN** the player earns the nickel that cost 5 shots
- **THEN** the next nickel costs 1 shot and its award points are double the first cycle's

### Requirement: Refuse shots to the wrong location
When the player hits a club location that is not the flashing one, Modern SHALL score its normal points and play a random refusal line in that location's voice. The line SHALL question the player without changing which location is lit. A refusal SHALL name no location other than the one hit and the flashing one; when the voice has no such line, the MC SHALL name the flashing location instead.

#### Scenario: The wrong location is hit
- **WHEN** the Kitchen is flashing and the player hits the Bar
- **THEN** the Bar scores normal points, the Bar's voice plays a random refusal such as "What are you doing here?", and the Kitchen stays lit

#### Scenario: A refusal never points the wrong way
- **WHEN** the Coat Check is flashing and the player hits the Bar
- **THEN** the refusal does not send the player to the Kitchen, the Bandstand, or the Booths

### Requirement: Only the song mode advances during a song
From the moment the selector opens until the song ends, shots SHALL still score their points and end-of-ball bonus counts, but SHALL NOT advance Standing Ovation, the floor nickel, or the nickel hunt. Completing the top bank still lights the lock. A lit extra ball or special SHALL stay lit and be collectable after the song.

#### Scenario: Banks during a song
- **WHEN** both drop banks are completed during a song
- **THEN** they score and reset, but no floor nickel or Standing Ovation is awarded

#### Scenario: A lit extra ball during Ruth Brown's Ladder
- **WHEN** an extra ball is lit and the ball enters the Kitchen during the Ladder
- **THEN** the rung counts and the extra ball stays lit until the song ends

### Requirement: Only the current target is directed
From the moment the selector opens until the song ends, Modern SHALL NOT flash, show, or speak nickel-hunt directions or refusals. Only the song mode's own instructions SHALL direct the player. The nickel hunt SHALL resume when the song ends.

#### Scenario: Picking a song
- **WHEN** the selector is open and the nickel reminder comes due, or the player hits a club location
- **THEN** no location direction or refusal plays

#### Scenario: During Ruth Brown's Ladder
- **WHEN** the Ladder is running and the player hits the Booths
- **THEN** no voice sends the player anywhere but the Kitchen, and the nickel target is shown again after the song ends

### Requirement: A quick return to the Bar or Kitchen counts
An eject from the Bar or the Kitchen SHALL be confirmed by any playfield switch, or after 3 s with none, so that a ball which comes straight back is counted as a new entry.

#### Scenario: Straight back into the Kitchen
- **WHEN** the Kitchen ejects during the Ladder and the ball drops back in 4 s later without touching another switch
- **THEN** the player climbs the next rung

### Requirement: Find a nickel on the floor
Each completed drop bank SHALL stay down and count as half a nickel. When both banks are down, Modern SHALL award a "nickel on the floor" if the player holds no nickel, then reset both banks. The floor nickel SHALL NOT change the location-shot cost.

#### Scenario: Both drop banks are completed
- **WHEN** the player completes the second drop bank while holding no nickel
- **THEN** the player is handed a nickel, both banks reset, and the next location nickel still costs what it did before

#### Scenario: Both banks are completed while holding a nickel
- **WHEN** both banks are down and the player already holds a nickel
- **THEN** no nickel is awarded and both banks reset

### Requirement: Hold one nickel at a time
A player SHALL hold at most one nickel. While a nickel is held, Modern SHALL stop directing the nickel hunt and SHALL direct the player to the jukebox until the nickel is spent.

#### Scenario: A nickel is earned
- **WHEN** the player earns a nickel
- **THEN** no location flashes for the nickel hunt, the lit crater lamps prompt the jukebox, and the screen shows the held nickel

### Requirement: Reset nickel progress at drain
At the end of each ball, Modern SHALL discard the player's held nickel, their shot progress toward the next nickel, and any half-nickel held in a down drop bank. The position in the 1-5 cost cycle SHALL carry over to the next ball.

#### Scenario: The ball drains holding a nickel
- **WHEN** a ball ends while the player holds a nickel and has one shot toward the next
- **THEN** the next ball starts with no nickel, no shot progress, and both drop banks up

### Requirement: Spend a nickel at a lit crater
A crater entry SHALL open the jukebox only when the player holds a nickel and the crater was lit in Classic's cascading crater lights, which keep their green freeze. Any other crater entry SHALL score crater points and return the ball to play. Without a nickel, the screen and voice SHALL say the jukebox needs a nickel.

#### Scenario: A lit crater with a nickel
- **WHEN** the player holds a nickel and the ball enters a lit crater
- **THEN** the nickel is spent, the ball is held, and the artist selector opens

#### Scenario: A crater without a nickel
- **WHEN** the player holds no nickel and the ball enters any crater
- **THEN** the crater scores, the ball returns to play, and the screen says the jukebox needs a nickel

#### Scenario: An unlit crater with a nickel
- **WHEN** the player holds a nickel and the ball enters an unlit crater
- **THEN** the crater scores, the nickel is kept, and the ball returns to play

### Requirement: Choose an artist on the jukebox
The selector SHALL show ten artist slots, the tenth being Hit me!. A tap of the right green button SHALL move to the next selectable artist. The *select* action SHALL choose the highlighted artist; it is a 2 s hold of the right green button with an on-screen fill bar, replaceable by another input. If the player does not choose within 10 s, the highlighted artist SHALL be chosen.

#### Scenario: The player scrolls and selects
- **WHEN** the selector is open and the player taps green twice, then holds green for 2 s
- **THEN** the highlight moves two selectable artists, a fill bar shows the hold, and the highlighted artist is chosen

#### Scenario: The player does not choose
- **WHEN** the selector has been open for 10 s with no choice
- **THEN** the highlighted artist is chosen

### Requirement: Play each artist once per round
An artist SHALL be unselectable and greyed out once the player has played them, until all ten artists have been played. Then all ten SHALL become selectable again for a new round. Artist progress SHALL persist for the player for the whole game.

#### Scenario: A played artist is greyed out
- **WHEN** the selector opens after the player has played Artist 3
- **THEN** Artist 3 is greyed out and the highlight skips it

#### Scenario: Every artist has been played
- **WHEN** the selector opens after the player has played all ten artists
- **THEN** all ten artists are selectable again

### Requirement: Start the chosen song on release
Modern SHALL pick one song at random for the chosen artist: one of that artist's three songs for Artists 1-9, or one of the twelve Hit me! songs. The song and its mode SHALL start when the held ball is released back to play.

#### Scenario: An artist is chosen
- **WHEN** the player chooses an artist
- **THEN** the screen names the artist and a random song from that artist's songs, the ball is released, and the song starts as the ball returns to play

### Requirement: Use the jukebox catalogue
The jukebox SHALL list Louis Jordan, Ruth Brown, Big Joe Turner, LaVern Baker, Wynonie Harris, Big Mama Thornton, Etta James, Ray Charles, and Joe Liggins in slots 1-9, each with three songs from the catalogue in design.md, and Hit me! in slot 10. Titles SHALL be kept in one editable catalogue, so a title can change without renaming files.

#### Scenario: The selector lists the artists
- **WHEN** the selector opens
- **THEN** it shows Louis Jordan through Joe Liggins in slots 1-9 and Hit me! in slot 10

#### Scenario: A title is changed
- **WHEN** the user edits a song title in the catalogue
- **THEN** the screen shows the new title and the same file plays

### Requirement: Use the Hit me! songs
The Hit me! pool SHALL be:
- "Rocket 88", Jackie Brenston & His Delta Cats (1951)
- "Sixty Minute Man", Billy Ward and His Dominoes (1951)
- "Chicken Shack Boogie", Amos Milburn (1948)
- "Ain't Got No Home", Clarence "Frogman" Henry
- "Stagger Lee", Lloyd Price
- "Hey Hey Baby", Helen Humes
- "Snatch and Grab It", Julia Lee
- "Maybe", The Chantels
- "Mr. Lee", The Bobbettes
- "I Wanna Know", The Du Droppers
- "Do Unto Others", Pee Wee Crayton
- "Rock the Joint", Jimmy Preston

#### Scenario: Hit me! is chosen
- **WHEN** the player chooses Hit me!
- **THEN** the screen names one song at random from this pool, with its artist

### Requirement: Play user-supplied song files
Each song SHALL play from a numbered MP3 in its slot's folder: `sounds/music/jukebox/<nn>_<artist>/song_<n>.mp3` (for example `03_big_joe_turner/song_2.mp3`) and `sounds/music/jukebox/10_hit_me/song_<nn>.mp3` in catalogue order. Until the user supplies a file, Modern SHALL use a generated placeholder at that path. The placeholder SHALL be of the expected length and SHALL NOT contain the original recording. The game is private and non-commercial, and the user owns the recordings.

#### Scenario: A song file is replaced
- **WHEN** the user saves an edited MP3 as `03_big_joe_turner/song_2.mp3`
- **THEN** Honey Hush plays the user's recording, with no config change

#### Scenario: A song is shorter or longer than the placeholder
- **WHEN** a supplied song file has a different length from its placeholder
- **THEN** the song-mode timer uses the supplied file's length

### Requirement: Close the jukebox during multiball
Modern SHALL NOT open the selector while more than one ball is in play. A held nickel SHALL be kept until play returns to one ball.

#### Scenario: A lit crater during multiball
- **WHEN** two or more balls are in play and the player holding a nickel enters a lit crater
- **THEN** the selector does not open and the nickel is kept

### Requirement: Count songs on the playfield
Each song played SHALL light the next lamp of L33-L42 in order. The lamps SHALL persist for the player for the whole game. When a new round of ten artists starts, the lamps SHALL clear and count that round's songs.

#### Scenario: The player's third song starts
- **WHEN** the player's third song starts
- **THEN** lamps L33-L35 are lit for that player

### Requirement: Raise the song multiplier every five songs
The song multiplier SHALL be 2x after five songs, 3x after ten, and 4x after fifteen songs played, and SHALL apply to all Modern scoring for that player for the rest of the game. The playfield's 2x-4x lamps (L30-L32) SHALL show the current multiplier by lighting the lamp for that level only; the back-box screen SHALL NOT show it.

#### Scenario: The fifth song starts
- **WHEN** the player's fifth song starts
- **THEN** the song multiplier becomes 2x, lamp L30 lights, and later scores are doubled

### Requirement: Award the special after ten songs
When the player's tenth song ends, Modern SHALL light the special at the Bar, flashing lamp L44. Collecting it SHALL fire the knocker, show an on-screen free-game award, and score the special points. The special SHALL be awarded at most once per player per game.

#### Scenario: The player collects the special
- **WHEN** the special is lit and the ball enters the Bar
- **THEN** the knocker fires, the screen shows the free-game award, the special points score, and L44 goes out

### Requirement: Voice the club locations
Each club location SHALL have its own voice, with male and female voices mixed. Each location SHALL have a pool of at least three refusal lines and its own direction and nickel lines. Until final recordings are supplied, Modern SHALL use placeholder text-to-speech files with the same names and triggers.

#### Scenario: A placeholder voice plays
- **WHEN** a refusal is triggered at the Coat Check before final audio is supplied
- **THEN** a placeholder text-to-speech refusal plays in the Coat Check voice
