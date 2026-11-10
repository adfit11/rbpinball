# Classic cabinet verification

Machine, date, MPF revision, and LISY firmware ________________

Use this sheet for the [Classic port](../openspec/changes/archive/2026-11-10-adopt-classic-volcano-rules/tasks.md) and the [cabinet selection check](../openspec/changes/archive/2026-11-10-add-classic-modern-selection/tasks.md). The [USB diagnostic panel](usb-diagnostic-panel.md) and [previous coil survey](coil-survey.md) provide the starting evidence. Record a result for each switch or output number in grouped rows. Use **confirmed**, **no observed response**, or **unresolved**, with the observed event and motion. A virtual result can be recorded separately.

## Inputs

| Input | Configured switch | Expected MPF observation | Event and result |
| --- | --- | --- | --- |
| Left and right flippers | Virtual `s_flipper_left`, `s_flipper_right` | Check whether each physical press and release produces an observable LISY event. Record the numbers or the absence of an event. | No observed response from either button in the switch-only test, with the game-over relay not commanded. |
| Start | 47 | One press and release per confirmation | Confirmed in the switch-only test. Switch 47 reported one active and one inactive transition. |
| Tilt | 46 | Tilt switch transition and tilt event | |
| Trough | 40, 30 | Record arrival and departure sequences for each ball and the full-trough state. Current MPF counting uses 40. | Manual refill confirmed that 40 opens after each of the first two balls and stays closed on the third. Each of the first two arrivals generated multiple closures. Switch 30 closed on the first arrival and stayed closed through refill. See the timings below. |
| Outhole | 20 | Arrival and release on a drain | Confirmed active after several transitions when a ball was placed in the outhole. Cleared 69 ms after a single 65 ms coil pulse. |
| Subway entrance, kicker | 10, 0 | One entrance event per captured ball and one kicker arrival per released ball | |
| Top saucer, fire pit | 23, 43 | Capture switch holds while occupied and clears on eject | |
| Right green button | 56 | One selection change per press in attract. Triggers Freeze during Classic play. | Confirmed switch 56. The selector requires a 30 ms closure and a 100 ms release to handle the repeated transitions seen on the cabinet. |
| Left green button | Unmapped | Check for an observable LISY event on press and release. | No observed response on two isolated presses in the switch-only test. |
| Top and bottom bumper groups | 35, 13 | Shared input per pair. Record each bumper's switch transition and physical kick separately. | |
| Top drop bank | 02, 12, 22, 32, 42 | Each target registers down and clears on reset | |
| Right drop bank | 01, 11, 21, 31, 41 | Each target registers down and clears on reset | |
| Craters 1 through 4 | 34, 24, 14, 04 | Each passage registers its crater before the subway entry | |
| Right outlane, left outlane, left return | 05, 06, 16 | Each rollover registers one passage | |
| Standing, rollunder, kicking, spot, spinner | 15, 25, 26, 36, 44 | Each shot reports the mapped switch. Record each wired contact separately where practical. | |

On 10 November 2026, the switch-only diagnostic ran on LISY80 firmware 5.26 (API 0.09), MPF 0.80.0.dev7, checkout `09efbbc`.

- During manual removal, both 30 and 40 were active at three balls. Switch 40 toggled several times and settled inactive at two balls. Switch 30 opened during the last two removals and was inactive with the trough empty. The log does not identify which removal opened 30.
- During manual refill, switch 40 reported three closures within 152 ms for the first ball and two closures within 89 ms for the second. It stayed active after the third ball, consistent with the configured 500 ms full-trough threshold.
- With 65 ms outhole pulses, switch 40 closed once on the first ball and twice within 25 ms on the second. On the third ball, 40 first closed 227 ms after the command, opened twice, and stayed closed from 263 ms onward. Switch 20 cleared on each pulse.
- With the trough full, a single 270 ms release served exactly one ball into the shooter lane. Switches 40 and 30 both toggled during the serve. By about 950 ms after the command, 40 had settled inactive and 30 active, matching the two-ball state.
- The shared trough uses a 200 ms ignore window for repeated closures. A live start also showed switch 40 re-closing during a serve and causing a false drain. The cabinet counter now ignores switch 40 closures for 1.5 seconds after a serve unless MPF expects a ball from the outhole. Virtual regression tests replay the measured arrival and serve behavior.
- The corrected cabinet run confirmed right green selected Classic and increased the roster to two. Start advanced both stages, Godot showed Classic, and exactly one ball reached the shooter lane. MPF kept the first turn active and counted two balls remaining in the trough.

The selector uses the confirmed right green button and Start. The two-player Classic start is confirmed. Repeat the cabinet check for Modern and verify turn changes after a real drain.

## Outputs

| Output | MPF command and expected response | Prior physical evidence | Command observed | Motion and result |
| --- | --- | --- | --- | --- |
| L0 game-over relay | Enable at start and disable on tilt or game over | Physical confirmation pending | | |
| 115 trough release | Configured 270 ms command serves one ball into the shooter lane | Successful serve observed at 270 ms | One 270 ms diagnostic pulse | Confirmed. Exactly one ball reached the shooter lane. |
| 9 outhole | Configured 65 ms command returns the drained ball to the trough | Motion observed | One 65 ms pulse per diagnostic return | Confirmed. Switch 20 cleared and 40 reported the ball entering the trough. |
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
