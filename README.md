### Running the game

Open the project in Godot and press **F5** to run the main scene. Then open Terminal and go to the project folder.

```sh
cd "/Users/adrian/Library/CloudStorage/Dropbox/Dev/rbpinball"
```

#### USB cabinet

```sh
/Users/adrian/mpf/bin/mpf -t
```

Wait for MPF to report a connection to LISY and make sure all three balls are in the trough. Use the right green button to switch games, then press Start to continue. Use the same green button to cycle from one to four players and back to one. Press Start again to begin.

#### Keyboard simulation

```sh
/Users/adrian/mpf/bin/mpf -xt
```

The `-x` flag forces virtual hardware and disables cabinet input. Godot shows the attract screen in both launch modes. On the keyboard, **comma** selects Classic and **period** selects Modern. **Enter** opens player selection. Use **comma** for fewer players and **period** for more, then press **Enter** again to start.

In virtual play, **1** hits the left return, **8** and **9** hit the bumpers, **R** and **L** hit the outlanes, and **Q** hits a right drop target.

### Adding rules to a game

MPF's shared selector commits the game and roster before play. `modes/base/config/base.yaml` is the Modern entry point and starts the current scoring and feature modes. `modes/classic/config/classic.yaml` is the Classic entry point.

For a new rule, use a game-owned MPF mode with a `modern_` or `classic_` name. Start it from that game's entry point or one of its own feature events. Use the shared physical switch and ball-device names for input, and keep feature-specific scoring, timers, slides, and sounds with the owning game. Test the feature in its game and hit the same switches in the other game to check that it stays inactive.

### **Diagnostic test for coils**

**navigate to this folder and start mpf diagnostics (in terminal)**
cd /Users/adrian/Library/CloudStorage/Dropbox/Dev/rbpinball
/Users/adrian/mpf/bin/mpf -c diagnostic_panel.yaml -b -t

**then hit this page**
http://127.0.0.1:8765/

### Modern: the Juke Joint

Modern is a 1940s rhythm and blues club. Hit the club staff (Bar, Kitchen, Bandstand, Coat Check, Booths) where the flashing lamp or screen directs you to earn a nickel, then shoot a lit crater to play the jukebox. Each artist runs a song mode; completed songs raise Standing Ovation, and every five songs raise the song multiplier.

Everything Modern lives in `modes/modern_*`, `custom_code/modern/`, `slides/modern/`, `sounds/modern_*`, `sounds/music/jukebox/`, `images/modern/`, `fonts/modern/` and `tools/modern/`, so it can be removed without touching Classic. Tunable values are in `custom_code/modern/settings.py`.

**Your own songs:** drop MP3s over the placeholders using the same names, for example `sounds/music/jukebox/03_big_joe_turner/song_1.mp3`, or `sounds/music/jukebox/10_hit_me/song_01.mp3` to `song_12.mp3`. Edit titles in `sounds/music/jukebox/catalogue.yaml`. Song length is read from each file. Open the project in Godot once (or run `godot --headless --path . --import`) so it picks up new files.

**Voice lines:** the script is `sounds/modern_voice/script.yaml`. Replace any file in `sounds/modern_voice/<character>/` with a recording of the same name. Lines render with the ElevenLabs voices whose IDs are in the script (designed from `tools/modern/elevenlabs_voice_prompts.md`) when `ELEVENLABS_API_KEY` is set, otherwise with Piper (`python3 -m venv ~/tts && ~/tts/bin/pip install piper-tts ruamel.yaml numpy`, voices in `~/tts/voices`). Run `~/tts/bin/python tools/modern/generate_voices.py` (`--only mc,cook` for some characters); `tools/modern/generate_songs.py` makes song placeholders. Both keep existing files unless given `--force`.

**Select action:** holding the right green button for 2 s is *select* (jukebox and initials). To move it to a wired left green button, set the machine variable `modern_select_switch` to that switch name.
