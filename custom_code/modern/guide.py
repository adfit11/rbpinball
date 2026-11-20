"""The player's current task, in plain words, for the HUD task panel."""

from custom_code.modern import settings

WHERE = {
    "bar": "the top saucer",
    "kitchen": "the fire-pit kicker on the left",
    "bandstand": "the spinner",
    "coat_check": "the spot target",
    "back_door": "the kicking target",
}


def place(location):
    name = settings.LOCATIONS[location][0].removeprefix("the ")
    return f"{name.upper()} ({WHERE[location]})"


def current_task(machine):
    """Return (title, detail) for what the player should do next."""
    player = machine.game.player
    modes = machine.modes
    party = modes["modern_rent_party"]
    if party.active and party.multiball:
        return "RENT PARTY!", "Shoot lit craters for jackpots. Three jackpots light the SUPER JACKPOT at the Bar."
    jukebox = modes["modern_jukebox"]
    if jukebox.active and jukebox.selector_open:
        return "PICK A SONG", "Tap green to move to the next artist. Hold green to play it."
    songs = modes["modern_songs"]
    rule = songs.rule if songs.active else None
    if rule:
        return f"SONG MODE: {rule.title}", f"{rule.goal} Finish before the record ends."
    if player.modern_lock_lit:
        return "LOCK IS LIT", "Shoot any crater to lock a ball for Rent Party multiball."
    if player.modern_nickel:
        return "PLAY THE JUKEBOX", "You've got a nickel! Shoot a lit crater to pick a song."
    target = player.modern_nickel_target
    if not target:
        return "GET A NICKEL", "Visit the club staff and ask them for a nickel."
    detail = f"Visit the {place(target)} and ask for one."
    if player.modern_nickel_cost > 1:
        detail += f" Visit {player.modern_nickel_progress + 1} of {player.modern_nickel_cost}."
    return "GET A NICKEL", detail + " Other staff will send you elsewhere."
