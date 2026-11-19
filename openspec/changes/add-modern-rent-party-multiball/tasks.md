# Tasks

## 1. Guest list

- [ ] 1.1 Add `modern_multiball` with the per-player guest list (five locations and two banks, five to fill, reset at drain) and its HUD. Verify tests cover each guest-list scenario.

## 2. Locks

- [ ] 2.1 Add the physical-only lock, enabled only while the lock is lit and gated to lit craters, with a replacement served. Verify tests cover the lit-crater lock, the unlit-crater pass, and the count starting from balls already in the subway.
- [ ] 2.2 Show the lock count at all times and detect Gate Crasher. Verify a two-player test steals the locks and posts `modern_gate_crasher`.
- [ ] 2.3 Handle a lock and a nickel on the same entry. Verify a test shows the lock, then the selector, then the song starting on the plunge.

## 3. Rent Party

- [ ] 3.1 Start the three-ball multiball on the third lock and keep the jukebox closed. Verify a test shows three balls in play.
- [ ] 3.2 Add the jackpots and the Bar super jackpot. Verify tests cover the values and the super jackpot lighting.
- [ ] 3.3 End at one ball, reopen the jukebox, and light an extra ball within the limits. Verify tests cover each.

## 4. Presentation

- [ ] 4.1 Mock up the guest-list HUD, lock, Rent Party intro, jackpot, super jackpot, Gate Crasher, and total screens, and get the user's approval. Verify the mockups are delivered.
- [ ] 4.2 Build the approved screens with their transitions, and add the guest-list, lock, Rent Party, and Gate Crasher callout pools with generated placeholders. Verify the screens load in GMC and a test asserts the callout events.

## 5. Integration

- [ ] 5.1 Run `~/mpf/bin/python -m pytest tests -q` and `openspec validate --all`, and verify both pass.
- [ ] 5.2 On the cabinet, check locks, stealing between two players, and the multiball release.
