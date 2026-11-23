# modern-presentation Specification

## Purpose
Defines how Modern looks and sounds: in-character voice callouts over the music, and the screens and transitions for every Modern feature and mode.

## Requirements

### Requirement: Play voice callouts over the music
Modern SHALL play voice callouts on a voice channel that is mixed over the music. The music SHALL be lowered while a callout plays and restored afterwards. At most one callout SHALL play at a time.

#### Scenario: A callout plays during a song
- **WHEN** a callout is triggered while music is playing
- **THEN** the music is lowered, the callout is heard clearly, and the music returns to its level when the callout ends

### Requirement: Trigger callouts at game events
Modern SHALL play a callout from a matching pool at key game events, such as game start, ball start, a nickel earned, the jukebox opening, a song starting, completing or failing, a lock, Rent Party, a jackpot, Gate Crasher, Drop the Needle, an extra ball, the special, a tilt warning, and the ball's bonus. Within a pool, lines SHALL be chosen at random, without repeating the last line played.

#### Scenario: A nickel is earned
- **WHEN** the player earns a nickel
- **THEN** a random line from the nickel pool plays, and it differs from the last nickel line

### Requirement: Ambient lamp layer
Modern SHALL run a moving background pattern on lamps no feature is using, at three intensities: base, artist mode and multiball. Lamp requests SHALL always win, so flashing targets and lit features read unchanged. Outside multiball it SHALL never light a location, drop, Booths, special or shoot-again lamp.
- Base: one slow lamp walks from the flippers to each flashing target, with an occasional twinkle.
- Artist modes: a quicker two-lamp stream runs to each flashing target in turn, faster as the rule heats up (hurry-up and Order Up drain, more rungs, jackpots or requests). Order Up deliveries run from the Kitchen. Party Time wanders over the whole table; Dance Floor sends a ring out from the bumpers on each hit.
- Multiball: a full-table show (rolling band, trading lamps, sparkle, lamps 1–10 ping-pong, flashes).

#### Scenario: A hurry-up guides the player
- **WHEN** the hurry-up target flashes
- **THEN** a stream of lamps runs from the flippers toward it, and speeds up as the value drains

### Requirement: Celebrate a locked ball
Every ball locked before the third SHALL play an excited MC announcement, the jackpot sound, the lamp burst, a gold screen flash and a "BALL n LOCKED!" card. The third lock SHALL use the Rent Party build-up instead.

#### Scenario: First lock
- **WHEN** a ball locks with none already locked
- **THEN** the MC announces the lock and "BALL 1 LOCKED!" shows

### Requirement: Celebrate a lit ball saver
Whenever the Bouncer ball saver becomes ready, the MC SHALL excitedly announce it after any line already playing, and a "BALL SAVER LIT!" card SHALL show.

#### Scenario: Drop the needle lights the ball saver
- **WHEN** Drop the Needle readies the Bouncer
- **THEN** the MC announces the ball saver is lit and "BALL SAVER LIT!" shows

### Requirement: Celebrate an earned extra ball
Every extra ball earned SHALL play an excited MC announcement, the jackpot sound, the lamp burst, a gold screen flash, and an "EXTRA BALL!" card for 3 s.

#### Scenario: Collecting a lit extra ball
- **WHEN** the ball enters the Kitchen with an extra ball lit
- **THEN** the MC announces the extra ball and the "EXTRA BALL!" card shows

### Requirement: Play random encouragement and quips
During play with no other callout pending, Modern SHALL occasionally play a random encouragement or a witty quip suited to a 1940s rhythm-and-blues juke joint. Each SHALL follow a minimum quiet gap (draft 20 s) and a random chance, and SHALL never interrupt an event callout.

#### Scenario: A quiet stretch of play
- **WHEN** no callout has played for the quiet gap during normal play
- **THEN** Modern may play a random quip from the club regulars' pool

#### Scenario: An event during a quip
- **WHEN** an event callout is triggered while a random quip is queued
- **THEN** the event callout plays and the queued quip is dropped

### Requirement: Keep voices in character
Each speaking character SHALL have a consistent voice. The characters are the five location staff, the jukebox or MC, and the club regulars, with male and female voices mixed. Lines SHALL be written as African American club staff and patrons of the 1940s, using era-appropriate slang. Lines SHALL NOT imitate real performers.

#### Scenario: The Bar speaks twice
- **WHEN** two Bar callouts play in a game
- **THEN** both use the same Bar character voice

### Requirement: Use placeholder voice files until replaced
Until final recordings are supplied, every callout SHALL use a generated text-to-speech placeholder. Each placeholder SHALL use the most in-character voice the available tool can produce, falling back to plain text-to-speech, and its file SHALL be named so a final recording can replace it file for file. Each line's script text SHALL be kept with the audio.

#### Scenario: A final recording is supplied
- **WHEN** a final recording is saved with a placeholder's file name
- **THEN** Modern plays the recording with no rule or config change

### Requirement: Show a real screen for every Modern state
Modern SHALL show a designed screen, not plain debug text, for each state: the rules splash, the base HUD, location directions, refusals, nickel awards, the jukebox selector, song intro, each song mode, mode results, Drop the Needle, extra ball, special, the guest list and locks, Rent Party, jackpots, Gate Crasher, bonus, tilt, high-score entry, and game over.

#### Scenario: A state without its own screen
- **WHEN** any listed Modern state begins
- **THEN** its own screen or overlay is shown in the juke-joint style

### Requirement: Keep the base HUD visible
During play, the base HUD SHALL show the current player's score as the largest item on screen, with the player, ball, and other players' scores beneath it; one goal card that says what to do next; a locks chip with the subway lock count and lock state; and the voice caption. The goal card SHALL show the nickel hunt, the chosen mode's intro, the running mode with its progress dots and time left, Rent Party, or the end-of-ball bonus. The songs played, the song multiplier, Standing Ovation, and the Bouncer ball saver SHALL be shown only by their playfield lamps, not on the HUD. Feature screens SHALL overlay it rather than hide it, except the selector, the splash, and the bonus.

#### Scenario: A mode is running
- **WHEN** a song mode is active
- **THEN** the goal card shows the mode, its progress, and the time left, and the score and lock count remain visible

### Requirement: Transition between screens
Modern SHALL animate changes between screens and overlays, using entrance and exit transitions such as a slide, a fade, or a jukebox flip. Award callouts SHALL appear briefly and then clear without player input.

#### Scenario: A song starts
- **WHEN** an artist is chosen
- **THEN** the selector transitions to a song-intro card, which then transitions to the mode overlay on the HUD
