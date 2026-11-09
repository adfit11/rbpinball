# Volcano playfield coil survey — 3 November 2026

Hardware: LISY80, firmware 5.26, API 0.09, USB serial at 115200 baud.
Labels below come from this project's configuration; confirm each by observing the machine.

Run `mpf -c diagnostic_coil_survey.yaml -b -t -v` from the project directory.
Each fresh Start press pulses one output. Wait at least two seconds between tests.
Power off before reconnecting wiring. Stop on a locked-on or overheating coil.

| Test | Output | Expected mechanism | Duration | Observed result |
| --- | --- | --- | --- | --- |
| 1 | 1 | Subway ball release | 300 ms | No response observed by user; cause not isolated |
| 2 | 2 | Top drop-target reset | 300 ms | No response observed by user; cause not isolated |
| 3 | 5 | Subway kicker | 40 ms | No response observed by user; cause not isolated |
| 4 | 6 | Right drop-target reset | 300 ms | No response observed by user; cause not isolated |
| 5 | 9 | Bottom outhole | 65 ms | Working — user confirmed during survey |
| 6 | 108 | Left side / fire-pit kicker | 15 ms | No response observed by user; cause not isolated |
| 7 | 116 | Top hole kicker | 55 ms | Working — user confirmed during survey |
| 8 | 115 | Trough release | 270 ms | Working — user confirmed during survey |
| 9 | 112 | Motor relay | 250 ms | No response observed by user; brief identification test only, cause not isolated |

The survey sends no automatic repeat pulses. Outputs 7 (unidentified `c_GGG`,
possibly a coin counter) and 8 (knocker) are excluded from this playfield pass.
Directly controlled bumpers, flippers, and kicking rubbers need separate physical
tests; this survey covers the listed MPF outputs only.

An absent movement does not by itself establish a failed coil: wiring, driver,
power, mechanical binding, and pulse duration remain possible causes.

## Completed survey

- Working: 9 (outhole), 116 (top hole kicker), 115 (trough release at 270 ms).
- No observed response: 1 (subway release), 2 (top drop reset), 5 (subway kicker),
  6 (right drop reset), 108 (left/fire-pit kicker), 112 (motor relay).
- MPF logged all nine output commands. This confirms software requested each
  test, not electrical delivery at the coil. The diagnostic shut down after
  the final test.
- Next: inspect/re-establish connections with power off, then selectively
  retest the non-responsive mechanisms. No failed coil or driver has been
  established by this survey.

## Pop bumpers — separate tests completed

The Volcano technical sheets, PDF page 3, list a dedicated pop-bumper board
for each of the four bumpers. These are not exercised by MPF's coil-output
survey. Verify the fitted machine retains that arrangement. Test each skirt
briefly and record physical kick separately from its MPF scoring input.
PDF page 1 lists the top pair on switch 35 and the bottom pair on switch 13.

| Bumper | Physical kick | MPF input |
| --- | --- | --- |
| Top left | No kick observed by user | No switch 35 transition logged during test |
| Top centre | No kick observed by user | No switch 35 transition logged during test |
| Bottom left | No kick observed by user | No switch 13 transition logged during test |
| Bottom right | No kick observed by user | No switch 13 transition logged during test |

All four skirts were briefly pressed during a switch-only MPF diagnostic;
there was no active game. No physical kicks and no switch 35/13 transitions
were observed. This does not isolate skirt switches, power, enable/relay state,
local boards, wiring, or coils. The switch monitor was stopped after testing.
Verify the fitted wiring and whether game/relay state affects the bumper supply
before interpreting this as four independent failures.

## LISYcontrol research

The user-supplied `lisy_user-manual_v5.27-1.pdf` was inspected at PDF pages
12, 23 and 27. It documents LISYcontrol's browser-based Solenoids pulse page
and network access using the IP shown on the machine displays. The boot table
selects LISYcontrol with S1 switches 6 and 8 ON, all others OFF; serial MPF
mode additionally has switch 4 ON. Record actual existing settings before
changing anything. Disconnect USB as well as machine power when rebooting
because USB can keep the Pi powered (documented in the MPF section).

MPF's LISY documentation states that the game-over relay enables the local
flippers/pop bumpers/slingshots:
https://missionpinball.org/latest/hardware/lisy/flippers_slings_popbumpers/

This project's `l_game_over_relay_00` has a light definition but no configured
enable/disable events. Relay state is a live hypothesis for the bumper results,
not a confirmed cause. Verify the fitted circuit, correct output numbering,
and relay polarity before changing the configuration or concluding hardware
has failed. No relay configuration was changed during this research.
