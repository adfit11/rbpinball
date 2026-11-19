# Tasks

## 1. Placeholder videos

- [ ] 1.1 Generate act-type stills (singer, saxophone, piano, small band, club) in the Modern art style, generic and with no real likeness
- [ ] 1.2 Add `tools/modern/generate_videos.py`: build `video_<n>.ogv` / `video_<nn>.ogv` for every catalogue song, plus the artist `video.ogv` and `club.ogv` fallbacks, as looping pan-and-zoom Theora at 960×540; never overwrite existing files without `--force`
- [ ] 1.3 Generate and import all placeholder videos

## 2. HUD video layer

- [ ] 2.1 Add a dimmed, muted, looping `VideoStreamPlayer` layer behind the HUD widgets in `modern_hud`
- [ ] 2.2 Derive the video path from the song path and apply the fallback chain (song, artist, club, none)
- [ ] 2.3 Start on `modern_song_started`, pause and resume with the song, and stop on `modern_song_ended`, so nothing shows outside songs
- [ ] 2.4 Make sure overlays, captions and the song panel stay readable over the video

## 3. Verification

- [ ] 3.1 Extend the headless slide check to load every video and confirm the fallback path rule
- [ ] 3.2 Run the MPF test suite and confirm no game-rule changes
- [ ] 3.3 Record a short GMC capture of a song mode with its video, the pause during a hold, and the end of the song
- [ ] 3.4 Add the owner's video replacement step (`ffmpeg -i clip.mp4 -c:v libtheora -q:v 6 -an video_1.ogv`) to `docs/modern/cabinet_checklist.md`
