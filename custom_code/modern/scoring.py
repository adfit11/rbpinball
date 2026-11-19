"""Score Modern points through the song multiplier and any mode factor."""


def multiplier(player):
    return max(1, player.modern_song_multiplier) * max(1, player.modern_score_factor)


def award(machine, value, source="", factor=1):
    """Add value x song multiplier x mode factor to the current player."""
    player = machine.game.player
    points = int(value * factor * multiplier(player))
    player.score += points
    machine.events.post("modern_scored", points=points, source=source)
    return points
