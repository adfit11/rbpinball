# Proposal

## Why

Song modes currently show text and lamps over a static club backdrop. A video of the artist performing while their song plays puts the jukebox pick on stage and makes each mode feel live.

## What Changes

- While a song mode is live, the Modern screen plays a video of that song's artist performing. It runs muted behind the mode information: dimmed and full screen, under the HUD, mode banner, song panel and overlays.
- Videos come from a folder per artist that mirrors the song folders. The owner can drop in their own clips file for file, with no config change.
- The video starts with the song, pauses when the song pauses for a held ball, and stops when the song ends, drains or tilts. Rent Party, the selector and base play show no artist video.
- Placeholder videos are generated for every song: animated, era-styled performer scenes. They don't depict or impersonate the real artists, and the owner replaces them later.
- A missing or unplayable video never blocks the song. The screen falls back to the artist's video, then a generic club video, then the current backdrop.

## Capabilities

### New Capabilities
- `modern-artist-video`: on-screen performer video for each live Modern song mode, its file layout, fallbacks and placeholders.

### Modified Capabilities
None. The HUD layering is covered by the new capability.

## Impact

- `slides/modern/modern_hud.*`: a video layer behind the existing HUD.
- New `videos/modern/jukebox/<nn>_<artist>/` assets and a generator in `tools/modern/`.
- The song-start event already carries the slot and file path. The video path is derived from the same catalogue entry, so the game rules don't change.
- Repository size grows with the placeholder clips, kept small at a low bitrate.
