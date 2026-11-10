### Start Up Routine

**initiate the environment**
source mpf/bin/activate

**navigate to the folder**
cd dropbox/dev/rbpinball



### Running the game

Open the project in Godot and press **F5** to run the main scene. Then start MPF from the project directory.

For virtual hardware, run `mpf -xt`. On the attract screen, **comma** selects Classic and **period** selects Modern. **Enter** opens player selection. Use **comma** for fewer players and **period** for more, then press **Enter** again to start.

In virtual play, **1** hits the left return, **8** and **9** hit the bumpers, **R** and **L** hit the outlanes, and **Q** hits a right drop target.

For the USB cabinet, run `mpf -t` after starting Godot. The flipper inputs are currently virtual and still need their LISY switch numbers confirmed on the cabinet.

### Adding rules to a game

MPF's shared selector commits the game and roster before play. `modes/base/config/base.yaml` is the Modern entry point and starts the current scoring and feature modes. `modes/classic/config/classic.yaml` is the Classic entry point.

For a new rule, use a game-owned MPF mode with a `modern_` or `classic_` name. Start it from that game's entry point or one of its own feature events. Use the shared physical switch and ball-device names for input, and keep feature-specific scoring, timers, slides, and sounds with the owning game. Test the feature in its game and hit the same switches in the other game to check that it stays inactive.

### **Diagnostic test for coils**

**navigate to this folder and start mpf diagnostics (in terminal)**
cd /Users/adrian/Library/CloudStorage/Dropbox/Dev/rbpinball
/Users/adrian/mpf/bin/mpf -c diagnostic_panel.yaml -b -t

**then hit this page**
http://127.0.0.1:8765/
