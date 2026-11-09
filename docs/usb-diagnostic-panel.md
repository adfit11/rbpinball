# USB diagnostic panel

Stop any running game/diagnostic first. Keep the machine in LISY serial slave
mode; this tool does not need LISYcontrol, a DIP change, or Godot.

From this project directory:

```sh
/Users/adrian/mpf/bin/mpf -c diagnostic_panel.yaml -b -t
```

Open <http://127.0.0.1:8765> on this computer. MPF exclusively owns the existing
USB serial connection. This panel is available only over loopback.

For a hardware-free preview, add `-x`; the page labels virtual hardware and
keeps its observations in a separate file.

## Relay check first

The Volcano technical sheets identify the game-over Q relay as lamp L0
(PDF pages 2–3). Installed MPF's LISY platform passes the light number through
unchanged. The diagnostic defines L0 as a digital output, not a coil pulse.

The generic MPF example uses output 1, which does not match the Volcano chart;
this diagnostic uses 0 and leaves normal game configuration unchanged until
the fitted relay and its effect have been physically confirmed.

Click **Command L0 on · 10 seconds**, observe the relay, and briefly test a
bumper skirt, flipper button, or slingshot switch. L0 switches off automatically
after ten seconds; **L0 off** turns it off early. The display describes the
commanded state, not a sensed relay position. No individual pop-bumper or
slingshot firing is possible through stock LISY wiring.

Power off before reconnecting any wiring. Stop if a coil stays energized or
gets hot. The normal game-over relay's load and contacts must match the stock
arrangement before interpreting the test.

## Output tests and observations

- Each **Pulse once** button sends a single command using the displayed time.
- The server enforces a cooldown and per-output diagnostic duration bounds.
  Those bounds are not manufacturer-approved coil ratings.
- Pulses above LISY's native 255 ms limit use MPF's timed enable/disable path.
- The motor defaults to a short 250 ms response test rather than its configured
  five-second game duration.
- **All outputs off** disables the listed coils and L0 while MPF is responsive.
  This is a software control, not a replacement for removing machine power.
- Choose **Working**, **Weak**, or **No response** to save a physical observation
  in `data/coil-panel-results.json`. Simulation uses a separate virtual file.
- Switch badges show MPF state. Bumper inputs are shared by pairs: 35 top,
  13 bottom. No scoring input alone does not isolate the local trigger circuit.
- **Stop diagnostic** turns outputs off and exits MPF. Ctrl+C also stops it.

The panel intentionally excludes unidentified output 7. The previous survey
remains in [coil-survey.md](coil-survey.md); new panel observations start untested.

## Validation

`/Users/adrian/mpf/bin/python -m unittest discover -s tests -p test_coil_panel.py`
checks MPF's real timing path for a 270 ms pulse, duration rejection, cooldown,
relay timeout/off, result persistence, live switch data, and shutdown using
virtual hardware. Browser controls were exercised against virtual hardware.
Requests without the per-session panel token are rejected.

Sources:
- Volcano technical sheets, inspected PDF pages 1–3.
- <https://missionpinball.org/latest/hardware/lisy/lights/>
- <https://missionpinball.org/latest/hardware/lisy/flippers_slings_popbumpers/>
- Installed MPF 0.80.0.dev7 `platforms/lisy/lisy.py` and `devices/digital_output.py`.
