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
