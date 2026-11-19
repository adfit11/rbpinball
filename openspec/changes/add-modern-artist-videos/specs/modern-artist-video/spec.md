# Spec Delta

## Purpose
Shows a performer video for the artist of the song that is playing during a Modern song mode, so each jukebox pick appears on stage.

## ADDED Requirements

### Requirement: Play the artist's video during a live song mode
While a Modern song mode is live, the screen SHALL play the video for that song's artist, looped and muted, behind the mode information. The HUD, mode banner, song panel, captions and overlays SHALL stay readable on top of it.

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
Each song SHALL have a video file beside a folder per artist that mirrors the song folders: `videos/modern/jukebox/<nn>_<artist>/video_<n>.ogv` for artist songs, and `video_<nn>.ogv` for the 12 Hit me! songs. The owner SHALL be able to replace any video file for file, with no configuration change.

#### Scenario: The owner replaces a video
- **WHEN** the owner copies their own clip over `videos/modern/jukebox/03_big_joe_turner/video_1.ogv` and reimports the project
- **THEN** Big Joe Turner's first song plays the owner's clip

### Requirement: Fall back without blocking the song
If a song's video is missing or cannot play, the screen SHALL use the artist's `video.ogv`, then the generic `videos/modern/jukebox/club.ogv`, then the regular backdrop. Video problems SHALL never delay or stop the song or the mode.

#### Scenario: A video is missing
- **WHEN** a song starts and its `video_<n>.ogv` does not exist
- **THEN** the next available fallback plays, and the song and mode start on time

### Requirement: Provide placeholder videos
Placeholder videos SHALL exist for every catalogue song and for the generic club fallback. Placeholders SHALL show generic, era-appropriate performer scenes for the act type: a singer at a microphone, a saxophone, a piano, or a small band. They SHALL NOT depict, imitate or name any real performer.

#### Scenario: A fresh checkout
- **WHEN** the project is checked out without owner videos
- **THEN** every song mode shows a placeholder performance video
