"""End-of-ball bonus multiplied by Standing Ovation."""

from mpf.core.mode import Mode

from custom_code.modern import settings

STEP_MS = 600


def bonus_lines(player):
    return [
        ("Dancers", player.modern_bonus_bumpers, settings.BONUS_BUMPER),
        ("Club visits", player.modern_bonus_locations, settings.BONUS_LOCATION),
        ("Drop targets", player.modern_bonus_drops, settings.BONUS_DROP),
        ("Songs played", player.modern_bonus_songs, settings.BONUS_SONG),
    ]


def ovation(player):
    return min(settings.MAX_OVATION, 1 + player.modern_ovation + player.modern_songs_completed_ball)


class ModernBonus(Mode):

    def mode_start(self, **kwargs):
        if self.machine.game.tilted:
            self.machine.events.post("modern_bonus_void")
            self.stop()
            return
        self.player.modern_counting_bonus = 1
        self.lines = bonus_lines(self.player)
        self.total = 0
        self.index = 0
        self.delay.add(ms=STEP_MS, callback=self._step)

    def _step(self):
        if self.index < len(self.lines):
            label, count, value = self.lines[self.index]
            self.total += count * value
            self.machine.events.post("modern_bonus_line", label=label, count=count, value=value,
                                     subtotal=self.total)
            self.index += 1
            self.delay.add(ms=STEP_MS, callback=self._step)
            return
        times = ovation(self.player)
        points = self.total * times
        self.player.score += points
        self.machine.events.post("modern_bonus_total", subtotal=self.total, ovation=times, points=points)
        self.machine.events.post("modern_callout", pool="mc_bonus")
        self.delay.add(ms=STEP_MS * 3, callback=self.stop)

    def mode_stop(self, **kwargs):
        self.player.modern_counting_bonus = 0
