"""Count Classic's end-of-ball bonus while MPF waits to end the turn."""

from mpf.core.mode import Mode


def count_bonus_unit(player):
    """Credit one unit and return the units still to count."""
    player.classic_bonus_units -= 1
    player.score += 1000 * player.classic_bonus_multiplier
    return player.classic_bonus_units


class ClassicBonus(Mode):
    """Award each bonus unit to the player whose ball just drained."""

    def mode_start(self, **kwargs):
        if self.machine.game.tilted or not self.player.classic_bonus_units:
            self.player.classic_bonus_units = 0
            self.stop()
            return

        self.player.classic_counting_bonus = 1
        self.delay.add(ms=150, callback=self._count_unit)

    def _count_unit(self):
        if count_bonus_unit(self.player):
            self.delay.add(ms=150, callback=self._count_unit)
        else:
            self.stop()

    def mode_stop(self, **kwargs):
        self.player.classic_counting_bonus = 0
