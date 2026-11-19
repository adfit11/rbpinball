# Design

## Context

See proposal.md - Why. Modern currently starts `base` on `ball_starting{machine.session_game == "modern"}`, and `base` starts the `bumpers`, `outlanes`, `right_drops`, and `hurryup` placeholder modes. Classic implements the behaviour Modern needs to reuse in several places:

- **Crater cascade, drop rotation, and green freeze:** `custom_code/classic_targets.py` (`ClassicTargets`).
- **Skill shot motor:** `classic_skill_shot` mode.
- **Saucer and fire pit holds:** `classic_holes` (`bd_classic_saucer`, `bd_classic_firepit`).
- **Ball saver relay:** `classic_gate`, which pulses `c_classic_ball_saver`.
- **Subway:** `bd_classic_subway_lock` and `bd_classic_subway_kicker`, counted by `VolcanoSubwayCounter`. That counter only infers crater arrivals in Classic.

The knocker is `c_Replay_Knock`. The lamp numbers come from the Volcano lamp sheet the user supplied, and they have not been checked at the cabinet. Classic drives L4-L6 for ball save ready, but the sheet lists those lamps as the 2x-4x multipliers. Modern uses the sheet.

## Goals / Non-Goals

**Goals:**
- Build a Modern mode stack that the song-mode and multiball changes can extend without editing the base.
- Reuse Classic's cascade, rotation, freeze, motor, and subway handling rather than copying them, without changing Classic behaviour.
- Keep every tunable value (scores, timings, costs) in one Modern settings place.

**Non-Goals:**
- Song-mode rules, the guest list, and multiball. Those are in the follow-on changes.
- Final art, artist and song names, and final audio.
- Wiring the left green button. Only the *select* indirection is in scope.
- Fixing Classic's lamp mapping.

## Decisions

### Modern mode stack
`modern` replaces `base` as the ball mode for `session_game == "modern"`. It starts these child code modes:
- `modern_targets`: craters, drops, and Drop the Needle.
- `modern_locations`: the five club locations, scoring, and voices.
- `modern_nickels`: the nickel hunt.
- `modern_jukebox`: the selector, rounds, song lights, the multiplier, and the special.
- `modern_holes`: the saucer and fire pit holds, extra balls, and the special collect.
- `modern_bonus`: Standing Ovation and the end-of-ball count.
- `modern_display`: the HUD.

The `bumpers`, `outlanes`, `right_drops`, and `hurryup` placeholder modes and the `base` slide and music are removed. Keeping each feature in its own mode lets the follow-on changes add `modern_song_*` and `modern_multiball` modes that listen to events instead of editing these ones. A single large mode was rejected because the song modes need to take over shots by priority.

### Share Classic mechanics through small extracted helpers
The cascade, rotation, and freeze timing are factored out of `ClassicTargets` into a helper that both Classic and Modern targets use. Classic keeps its scores and lamp choices. The skill-shot motor control is shared the same way. This was chosen over subclassing `ClassicTargets` because Modern's scoring and lamp map differ, and over copying the code because the timings would drift.

### Modern owns its player variables
All Modern state uses `modern_`-prefixed player variables: `modern_nickel`, `modern_nickel_progress`, `modern_nickel_step`, `modern_nickel_cycle`, `modern_artists_played`, `modern_songs_played`, `modern_songs_completed_ball`, `modern_song_multiplier`, `modern_special_awarded`, `modern_extra_balls_earned`, and `modern_ovation`. This keeps Modern state separate from Classic's `classic_` state.

### Song multiplier as a score multiplier
Modern scoring goes through one helper that applies `modern_song_multiplier`. Song modes later add their own factors (Party time's 2x) through the same helper. Using MPF `variable_player` scores directly was rejected, because they would skip the multiplier.

### Subway handling for the jukebox
Crater entries are inferred the same way as in Classic: a debounced crater switch followed by travel to the subway, with the crater-4 chatter filter. `VolcanoSubwayCounter.crater_ball_arrived` is extended to Modern sessions. A jukebox entry holds the ball in the subway lock while the selector is open, then kicks it out. The song starts when that eject is confirmed. Other entries kick straight back. The lock device is never ejected for the jukebox, so balls already locked by the multiball change stay put.

### Selector and select action
`modern_jukebox` owns a `select` abstraction. It posts `modern_select` after a 2 s hold of the configured select switch, and `modern_select_progress` events while the hold builds, which drive the fill bar. Taps post `modern_tap`. The switch is a machine setting, so a wired left green button can be mapped in later. While the selector or a mode owns green, the crater freeze is suppressed.

### Lamps
Modern uses `light_player` and `show_player` with a shared flash show. Song lights are L33-L42, the multiplier is L4-L7, Standing Ovation is L30-L32, shoot again is L1, the extra ball is L45, the special is L44, and the locations are L47, L45, L46, L43, and the Back Door insert. The Back Door insert is defined as a named light with a placeholder number that tests ignore. Until it is mapped, the Back Door is directed on screen only.

### Tilt, high score, and splash
- **Tilt:** Modern sets one warning through the MPF `tilt` settings for Modern sessions only. The game mode switches the warning count by session, so Classic is unchanged.
- **High scores:** use MPF `high_score` with a Modern-only category list. Its GMC entry slide is driven by `modern_tap` and `modern_select`.
- **Splash:** a GMC slide shown on `game_started` for Modern, which holds the first ball serve for a few seconds.

### Callout director
A `modern_callouts` mode owns every voice line:
- **Event pools:** pools keyed by game event, with no repeat of the last line.
- **Random quips:** a random-quip timer with a quiet gap and a chance roll.
- **Priority queue:** event callouts drop queued quips.
- **Playback:** lines play on the GMC `voice` bus (sequential), and music ducking is configured on the `music` bus.

Features post semantic events (for example `modern_callout{pool=nickel}`) rather than naming sound files, so the line content can change without code changes.

### Placeholder voices
Each line has a script entry (character, pool, text, and file name) in one YAML or CSV script file. A generation script renders every entry to `sounds/voice/<character>/<pool>_<nn>.ogg`.
- **Engine:** an offline neural text-to-speech engine with selectable US English speakers, such as Piper or Coqui XTTS. Each character is given the most fitting male or female speaker, with a slower, warmer delivery.
- **Fallback:** if no suitable engine is available on the build machine, use plain system text-to-speech.
- **Replacing lines:** final recordings replace the files with the same names.
- **Real performers:** no voice cloning or impersonation of real performers.

### Screens and transitions
Each Modern state in `modern-presentation` gets a GMC slide or a HUD overlay scene in a shared juke-joint theme: palette, fonts, a jukebox frame, and neon accents. Overlays are child scenes of the base HUD, so the score and lock count stay visible. Transitions use GMC slide transitions and Godot tweens. Before the scenes are built, each screen is mocked up as an image (layout, content, and transition notes) for the user to approve. Plain text screens are used only if mockups cannot be produced.

### Jukebox catalogue
The suggested song titles below are kept in one catalogue data file. Files live at `sounds/music/jukebox/<nn>_<artist>/song_<n>.mp3`.

| Slot | Artist | Song 1 | Song 2 | Song 3 |
|---|---|---|---|---|
| 1 | Louis Jordan | Caldonia | Choo Choo Ch'Boogie | Saturday Night Fish Fry |
| 2 | Ruth Brown | (Mama) He Treats Your Daughter Mean | Teardrops from My Eyes | 5-10-15 Hours |
| 3 | Big Joe Turner | Shake, Rattle and Roll | Honey Hush | Flip, Flop and Fly |
| 4 | LaVern Baker | Tweedlee Dee | Jim Dandy | Bop-Ting-a-Ling |
| 5 | Wynonie Harris | Good Rockin' Tonight | All She Wants to Do Is Rock | Bloodshot Eyes |
| 6 | Big Mama Thornton | Hound Dog | They Call Me Big Mama | I Smell a Rat |
| 7 | Etta James | Roll with Me, Henry | Good Rockin' Daddy | Tough Lover |
| 8 | Ray Charles | I Got a Woman | Mess Around | What'd I Say |
| 9 | Joe Liggins | The Honeydripper | Pink Champagne | I've Got a Right to Cry |

## Risks / Trade-offs

- **The lamp sheet does not match the cabinet.** Mitigation: the lamp numbers are confined to Modern config, so they are a one-line fix each.
- **Classic's L4-L6 ball-save lamps also drive the Modern multiplier lamps.** Mitigation: Modern never uses Classic's gate mode. Fixing Classic is a separate change.
- **Crater entries are misread while locked balls sit in the subway.** Mitigation: reuse Classic's debounced inference and cover it with tests that include a non-empty lock.
- **Holding the jukebox ball at the kicker fails on the cabinet.** Mitigation: fall back to holding the ball in the lock device only when no balls are locked, and check on the cabinet.
- **The score scale is a first draft.** Mitigation: every value lives in one settings file, for tuning at the cabinet.

## Migration Plan

Implement and test in virtual MPF, then apply to the cabinet laptop for play testing. Rollback is reverting the change, which restores the placeholder Modern modes.

## Open Questions

- The Back Door lamp output number, once found on the cabinet.
- The final special points (draft 1,000,000) and the jukebox auto-pick time (draft 10 s).
