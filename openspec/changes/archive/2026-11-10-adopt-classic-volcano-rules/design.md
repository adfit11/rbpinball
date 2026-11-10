# Design

## Context

`rbpinball` already selects Classic or Modern in attract, commits the roster before the first turn, and routes play through a shared MPF game. Classic uses `modes/classic/config/classic.yaml` and `slides/classic.tscn` for the one-ball preview. Modern's ball entry is gated on the committed game. The shared trough uses an entrance switch and serves through an unswitched shooter lane.

The sibling `volcano-rb` repository has MPF rules and a separate segment-display layer. Its logs show scoring and lock qualification in virtual play. Full multiball release and original-game fidelity still need verification. Its working tree has local subway changes, and its documented coil and switch mappings contain cabinet-specific assumptions.

## Goals / Non-Goals

- Use the existing MPF lifecycle, Godot connection, and shared cabinet definitions.
- Keep ported rules and presentation under Classic ownership, with tests through the normal game selector.
- Carry the three-ball rules and their physical mechanisms through verification in stages. Operator menus and credit accounting are separate from the gameplay port.

## Decisions

### Pin the source and verify the rules

Use donor commit `95a2b7917eb93ac70333e326ce09cf74292c4584` as the reproducible code baseline and retain KaydeeOK's MIT notice for reused material. Treat local donor changes as evidence to review, especially the entrance-switch subway model and lock-counting change. Use Gottlieb's three-ball instruction card A-21125 and technical sheets as the rules and wiring references. Compare the donor behavior to the card where it is documented and record any differences and their resolution. Use the donor's three-ball settings consistently in score conditions and in the Classic session ball limit. Start with its normal and liberal playfield settings for the free-play port. [Instruction card index](https://www.pinballrebel.com/pinball/cards/Gottlieb.htm) · [Volcano technical sheets](https://www.pinballrebel.com/pinball/cards/Tech_Charts/Gottlieb_Volcano_Tech_Sheets.pdf)

### Port from the Classic entry and reuse the machine layer

Use the committed `session_game` to activate Classic. Keep the existing Start approval and roster initialization, with MPF managing player turns and extra balls. Adapt the donor base, bumpers, spinner, drops, craters, saucer, fire pit, lanes, ball saver, bonus, and multiball under Classic-owned modes. Track their event dependencies when renaming modes and devices, including generated shot, timer, and drop-bank events. Keep bonus and seismic work tied to the owning player and clear callbacks at the appropriate lifecycle boundary. Let the MPF bonus queue finish before the next turn.

Use the existing switch, lamp, drop-bank, and coil definitions for shared hardware. Map donor references to those names and use Classic-scoped events for gameplay actions, including target resets and gates. Add the required ball devices against the existing shared hardware definitions. Preserve passive ball tracking and recovery across games. Keep the existing trough, shooter-lane, tilt, and game-over relay paths. The donor's virtual centre-trough and shooter-lane switches and its 30 ms trough-release setting are tied to a different ball-device configuration. The existing cabinet survey records a successful trough release at 270 ms.

Model lock qualification separately from the physical captures and release sequence. Account for all three balls through replacement serves, multiball start, drains, and return to the trough. Explicitly clear or reconcile the lock state after release and on game end or tilt as appropriate. The donor state machine omits `3_locked` from its reset transition, and changing MPF's lock-counting strategy changes the relationship between a player's progress and the balls in the mechanism. Cover repeated multiball, player handoff with a partial lock, and switching to Modern after Classic.

### Render game state in Godot

Extend the existing Classic scene with one score per joined player, active-player emphasis, and ball number. Initialize it from MPF's current state and update it on score and turn changes. Feed Classic bonus, multiplier, and lock cues through existing MPF variables or events and the Godot slide integration. The donor's segment display mode is a reference for information and timing. It stays outside the port, along with the donor's attract and monitor connection setup. Retain the Classic start notice.

### Record evidence in one cabinet visit

Prepare one checklist from the final port's references. Start from the existing coil survey and list each assumed switch, coil, and relay with its configured number, expected response, actual response, and verification status. Record switch press and release or ball passage separately from coil commands and mechanism movement.

- Cover the selector flippers and Start, tilt, trough and drain, subway entry and exit, saucer, fire pit, the green freeze button, and every scoring switch referenced by Classic.
- Cover the game-over relay, trough release, outhole, both drop resets, subway release and kicker, saucer, fire pit, return gate, and ball-saver relay, plus any other outputs introduced by the port.
- Recheck the unresolved results from the earlier survey where the port relies on those mechanisms. Verify both game starts, shooter-lane delivery, turn and drain handling, the Godot display, and actual three-ball capture and release.
- The flippers are virtual in both checkouts. Keep the virtual mapping until a cabinet input is confirmed. If the flippers produce no LISY events, record that result and confirm the physical controls to use before assigning a mapping. This visit can supply the hardware evidence for both the selection change and the port.

## Risks / Trade-offs

- Virtual ball tracking can pass while a cabinet mechanism fails to move. Require physical observations for cabinet acceptance, especially for subway outputs 1 and 5 and the fire pit at 108, which had no observed response in the prior survey.
- The donor has global rule hooks and machine-level state. Keep the imported hooks and delayed callbacks in Classic's lifecycle and test both game orders.
- Some rules interact with physical devices, including the ball-saver relay and return gate. Verify their trigger and release behavior against the cabinet and technical sheets before considering those features ready for physical play.

## Migration Plan

Bring up a complete virtual game with basic scoring, bonus, and the scoreboard. Add the remaining feature groups in virtual MPF with regression tests. Use the cabinet checklist to validate the mappings and physical play when the machine is available. Record unresolved inputs and outputs explicitly so virtual completion and cabinet readiness can be reviewed separately. Sync or archive the selection change's baseline Classic spec before publishing this delta.
