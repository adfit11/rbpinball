### Start Up Routine

**initiate the environment**
source mpf/bin/activate

**navigate to the folder**
cd dropbox/dev/rbpinball



### Running the game

**to run MPF in virtual mode (no connection to actual machine)**
mpf -xtb
then start Godot and play the base-slide

**keys to emulate some switches (in virtual mode)**
enter = start
comma = flipper_left
period = flipper_right
1 = return_left
8 = top_bumpers
9 = bottom_bumpers
q = right_drop_1

**to run MPF against the actual machine, plugged in via USB**
mpf -t
then start Godot and play the base-slide



### **Diagnostic test for coils**

**navigate to this folder and start mpf diagnostics (in terminal)**
cd /Users/adrian/Library/CloudStorage/Dropbox/Dev/rbpinball
/Users/adrian/mpf/bin/mpf -c diagnostic_panel.yaml -b -t

**then hit this page**
http://127.0.0.1:8765/
