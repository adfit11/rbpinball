# Classic Volcano rules

The Classic rules are adapted from KaydeeOK's `volcano-rb` at revision
`95a2b7917eb93ac70333e326ce09cf74292c4584`. The
[MIT notice](../modes/classic/LICENSE.volcano-rb) accompanies the port.

Classic uses three scheduled balls and the current cabinet's free-play roster.
The donor's three-ball awards are the baseline for basic switches. Classic
starts each ball with one bonus unit and counts each unit at 1,000 points times
the bonus multiplier before the turn advances. The rule port keeps that
countdown in the Classic bonus mode so its delay and player state follow the
current turn.

The port counts subway locks from confirmed MPF ball-device arrivals. The
physical lock count is visible to the next player on an ordinary handoff,
and the subway is released on tilt or game end. Both the shared two-game flow
and the subway sequence can be tested in MPF's Smart Virtual platform.
The [cabinet checklist](classic-cabinet-checklist.md) tracks the corresponding
physical checks.

Gottlieb's [three-ball card index](https://www.pinballrebel.com/pinball/cards/Gottlieb.htm)
identifies A-21125 as the three-ball instruction card. The archived
[Gottlieb release announcement](https://www.worldradiohistory.com/Archive-All-Music/Cash-Box/80s/1981/CB-1981-08-22.pdf#page=31)
describes the freeze, ball-saver, and lit-crater qualification. Basic scoring
values here come from the donor code and spec. The full card's scoring text
remains to be checked.
