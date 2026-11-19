# Design

## Context

See proposal.md for the motivation. The Modern HUD is one Godot scene, `slides/modern/modern_hud`, laid out at 1280×720 and scaled by `FitToScreen`. It already reacts to `modern_song_started` (carrying `slot`, `artist`, `title` and the song `path`), `modern_song_paused`, `modern_song_resumed` and `modern_song_ended`, and it plays the song MP3 itself.

## Goals / Non-Goals

**Goals:**
- A muted, looped, dimmed video layer behind the HUD for each live song.
- Owner clips can replace placeholders file for file.

**Non-Goals:**
- Syncing the video to the music beat, or showing video audio.
- Video in base play, the selector or Rent Party.

## Decisions

- **Format: Ogg Theora (`.ogv`).** Godot 4's built-in `VideoStreamPlayer` plays only Theora. MP4/WebM would need a GDExtension plugin. The owner converts their clips with one `ffmpeg` command, documented in the cabinet checklist.
- **Path derived in the HUD from the song path.** `sounds/music/jukebox/<folder>/song_<n>.mp3` maps to `videos/modern/jukebox/<folder>/video_<n>.ogv`, so there are no MPF or event changes, and the catalogue stays the only source of titles. The alternative, adding a `video` field to the event, would duplicate the path rule in Python.
- **Layer order:** the background art, then the video (full 1280×720, `modulate` dimmed to about 55%, with a dark gradient under the text panels), then the existing HUD. This is "behind the info". A side-panel layout would shrink the play information on small cabinet screens.
- **Fallback chain is checked with `ResourceLoader.exists`** before playing. A failed load is skipped silently, so the song timer never waits on video.
- **Placeholders:** one generated still for each act type (singer, sax, piano, small band, club), rendered as a 20–30 s looping pan-and-zoom with a warm flicker using `ffmpeg`. Each song uses its artist's act-type clip, with a different crop and seed per song. The output is 960×540 at a low bitrate, keeping the total size to tens of MB.

## Risks / Trade-offs

- Theora decoding at 1280×720 on a small cabinet PC may cost frames. Mitigation: placeholders are 960×540 and are upscaled, and owner clips should stay at 720p or below.
- Total repository size grows with every placeholder. Mitigation: low bitrate, and short loops reused by song.
- Generated performer imagery must stay generic. The prompts exclude real names and likenesses.
