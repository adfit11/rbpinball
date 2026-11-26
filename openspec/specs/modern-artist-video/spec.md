# modern-artist-video Specification

## Purpose
Shows a performer video for the artist of the song that is playing during a Modern song mode, so each jukebox pick appears on stage.

## Requirements

### Requirement: Play the artist's video during a live song mode
While a Modern song mode is live, the screen SHALL play video of that song's artist, muted and for the whole song, behind the mode information. The HUD, mode banner, song panel, captions and overlays SHALL stay readable on top of it.

#### Scenario: A song mode starts
- **WHEN** the player picks Louis Jordan and his song starts
- **THEN** a Louis Jordan performance video plays behind the score, the mode banner and the NOW PLAYING song panel

#### Scenario: Information stays readable
- **WHEN** an overlay such as JACKPOT or a mode instruction is shown during a song
- **THEN** the overlay appears above the video, and the video is dimmed enough that text keeps its normal contrast

### Requirement: Follow the song's lifecycle
The video SHALL start with the song, pause while the song is paused for a held ball, resume with it, and stop when the song ends for any reason. No artist video SHALL play during base play, the jukebox selector, or Rent Party multiball.

#### Scenario: The ball is held mid-song
- **WHEN** the ball is held in the fire pit during a song
- **THEN** the video pauses on its current frame and resumes when the song resumes

#### Scenario: The song ends
- **WHEN** the song completes, drains or tilts
- **THEN** the video stops and the regular backdrop returns

### Requirement: Use a predictable video file layout
Each artist slot SHALL have a folder that mirrors its song folder, `videos/modern/jukebox/<nn>_<artist>/`. A folder MAY hold numbered clips (`clip_01.ogv`, `clip_02.ogv`, ...), a video for one song named after its song file (`video_<n>.ogv` for `song_<n>.mp3`), and an artist-wide `video.ogv`. The owner SHALL be able to add, remove or replace any of these files, with no configuration change.

#### Scenario: The owner adds a clip
- **WHEN** the owner copies a new `clip_09.ogv` into `videos/modern/jukebox/03_big_joe_turner/`, which holds `clip_01.ogv` to `clip_08.ogv`, and reimports the project
- **THEN** Big Joe Turner's songs include the new clip in their rotation

#### Scenario: The owner replaces one song's video
- **WHEN** the owner copies their own clip to `videos/modern/jukebox/03_big_joe_turner/video_1.ogv` and reimports the project
- **THEN** Big Joe Turner's first song plays that clip, looped, and his other songs keep playing his clips

### Requirement: Play a random sequence of the artist's clips
When a song has no video of its own and its artist has clips, the screen SHALL play one of those clips at random, then another, until the song ends. A clip SHALL NOT play twice in a row while the artist has more than one clip.

#### Scenario: A song with clips
- **WHEN** Etta James's song starts and her folder holds 15 clips
- **THEN** a random clip plays, and each time a clip finishes a different random clip follows

### Requirement: Fall back without blocking the song
For each song the screen SHALL use the first that exists of: the song's `video_<n>.ogv`, the artist's clips, the artist's `video.ogv`, then no video, with the regular backdrop showing. Only the song's own artist footage SHALL play; there is no generic or other artist's video. Video problems SHALL never delay or stop the song or the mode.

#### Scenario: An artist has no videos
- **WHEN** a song starts and its artist folder holds no `video_<n>.ogv`, clips or `video.ogv`
- **THEN** the regular backdrop shows, and the song and mode start on time

### Requirement: Ship a video for every artist slot
A fresh checkout SHALL include either clips or a `video.ogv` for every artist slot, so every song mode shows a video. Clips SHALL be black and white, silent, about 20 s long and 1280×720.

#### Scenario: A fresh checkout
- **WHEN** the project is checked out without owner videos
- **THEN** every song mode shows a video for its artist slot
