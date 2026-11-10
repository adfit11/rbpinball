# Classic cabinet verification

Machine, date, MPF revision, and LISY firmware ________________

Use this sheet for the [Classic port](../openspec/changes/archive/2026-11-10-adopt-classic-volcano-rules/tasks.md) and the [cabinet selection check](../openspec/changes/archive/2026-11-10-add-classic-modern-selection/tasks.md). The [USB diagnostic panel](usb-diagnostic-panel.md) and [previous coil survey](coil-survey.md) provide the starting evidence. Record a result for each switch or output number in grouped rows. Use **confirmed**, **no observed response**, or **unresolved**, with the observed event and motion. A virtual result can be recorded separately.

## Inputs

| Input | Configured switch | Expected MPF observation | Event and result |
| --- | --- | --- | --- |
| Left and right flippers | Virtual `s_flipper_left`, `s_flipper_right` | Check whether each physical press and release produces an observable LISY event. Record the numbers or the absence of an event. | |
| Start | 47 | One press and release per confirmation | |
| Tilt | 46 | Tilt switch transition and tilt event | |
| Trough | 40, 30 | Record arrival and departure sequences for each ball and the full-trough state. Current MPF counting uses 40. | |
| Outhole | 20 | Arrival and release on a drain | |
| Subway entrance, kicker | 10, 0 | One entrance event per captured ball and one kicker arrival per released ball | |
| Top saucer, fire pit | 23, 43 | Capture switch holds while occupied and clears on eject | |
| Green freeze button | 56 | One transition pair per press | |
| Top and bottom bumper groups | 35, 13 | Shared input per pair. Record each bumper's switch transition and physical kick separately. | |
| Top drop bank | 02, 12, 22, 32, 42 | Each target registers down and clears on reset | |
| Right drop bank | 01, 11, 21, 31, 41 | Each target registers down and clears on reset | |
| Craters 1 through 4 | 34, 24, 14, 04 | Each passage registers its crater before the subway entry | |
| Right outlane, left outlane, left return | 05, 06, 16 | Each rollover registers one passage | |
| Standing, rollunder, kicking, spot, spinner | 15, 25, 26, 36, 44 | Each shot reports the mapped switch. Record each wired contact separately where practical. | |

If the physical flippers produce no LISY events, record that and agree on the cabinet controls before assigning switch mappings. Start and the selector each need a complete check in attract with the resulting controls.

## Outputs

| Output | MPF command and expected response | Prior physical evidence | Command observed | Motion and result |
| --- | --- | --- | --- | --- |
| L0 game-over relay | Enable at start and disable on tilt or game over | Physical confirmation pending | | |
| 115 trough release | Configured 270 ms command serves one ball into the shooter lane | Successful serve observed at 270 ms | | |
| 9 outhole | Configured 65 ms command returns the drained ball to the trough | Motion observed | | |
| 2 top drop reset | Reset returns all top targets to the up state | No response observed | | |
| 6 right drop reset | Reset returns all right targets to the up state | No response observed | | |
| 1 subway release | Moves one staged ball to the kicker switch | No response observed | | |
| 5 subway kicker | Returns the staged ball to the playfield and clears the kicker switch | No response observed | | |
| 116 saucer kicker | Ejects the held saucer ball when collection ends | Motion observed | | |
| 108 fire-pit kicker | Returns the held fire-pit ball to the playfield | No response observed | | |
| L14 return gate | Opens on the qualified spot shot and closes on return, drain, or tilt | New to this port | | |
| 113 / L13 ball-saver relay | Arms from a lit drop award. Verify the physical save and latch release separately from the MPF pulse. | New to this port | | |

Check the current configuration before the visit and add a row for each additional output relied on by the installed revision. Record the observed relay behavior as well as any coil pulse.

## Cabinet play-through

- [ ] Select both games and set their rosters with the confirmed cabinet controls. Check the on-screen instructions and that Start serves once after the final confirmation.
- [ ] Check the first ball reaches the shooter lane in each game. In Classic, check a drain, a player handoff, scoreboard retention, bonus, and return to attract.
- [ ] Confirm gate and ball-saver operation and verify that their effects clear when expected.
- [ ] Qualify and confirm three physical subway captures, verify the two replacement serves, and observe all three balls release into play. Confirm the Godot lock and multiball cues and the return to single-ball play.
- [ ] Record outstanding mappings or mechanisms and use the same cabinet results for both OpenSpec changes.

References  
[Volcano technical sheets](https://www.pinballrebel.com/pinball/cards/Tech_Charts/Gottlieb_Volcano_Tech_Sheets.pdf)
