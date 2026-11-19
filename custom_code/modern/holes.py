"""The Bar (saucer) and Kitchen (fire pit): holds, extra balls and the special."""

from mpf.core.mode import Mode

from custom_code.modern import settings
from custom_code.modern.lamps import FLASH, STEADY, director
from custom_code.modern.scoring import award

HOLES = {"bar": "ball_hold_modern_saucer_held_ball", "kitchen": "ball_hold_modern_firepit_held_ball"}


class ModernHoles(Mode):

    def mode_start(self, **kwargs):
        self.hold_ms = {}
        for hole, event in HOLES.items():
            self.add_mode_event_handler(event, self._captured, hole=hole)
        self.add_mode_event_handler("modern_light_extra_ball", self._light_extra_ball)
        self.add_mode_event_handler("modern_light_special", self._light_special)
        self._show()

    @property
    def lamps(self):
        return director(self.machine)

    def extend(self, hole, ms):
        """Hold the captured ball longer; call from a modern_hole_held handler."""
        self.hold_ms[hole] = max(self.hold_ms.get(hole, 0), ms)

    def _captured(self, hole, **kwargs):
        self.hold_ms[hole] = settings.HOLE_HOLD_MS
        self.machine.events.post("modern_ball_held", hole=hole)
        self.machine.modes["modern"].location_hit(hole)
        if hole == "kitchen" and self.player.modern_extra_ball_lit:
            self.player.modern_extra_ball_lit = 0
            self.player.modern_extra_balls_earned += 1
            self.machine.events.post("modern_award_extra_ball")
            self.machine.events.post("modern_callout", pool="cook_extra_ball")
        if hole == "bar" and self.player.modern_special_state == 1:
            self.player.modern_special_state = 2
            self.machine.coils["c_Replay_Knock"].pulse()
            points = award(self.machine, settings.SCORE_SPECIAL, "special")
            self.machine.events.post("modern_special_awarded", points=points)
            self.machine.events.post("modern_callout", pool="bartender_special")
        self.machine.events.post("modern_hole_held", hole=hole)
        self._show()
        self.delay.reset(ms=self.hold_ms[hole], name=hole, callback=self._release, hole=hole)

    def _release(self, hole):
        self.machine.events.post("modern_ball_released", hole=hole)
        self.machine.events.post(f"modern_release_{hole}")

    def _light_extra_ball(self, **kwargs):
        player = self.player
        if player.modern_extra_ball_lit or player.modern_extra_balls_earned >= settings.MAX_EXTRA_BALLS:
            return
        player.modern_extra_ball_lit = 1
        self.machine.events.post("modern_extra_ball_lit")
        self.machine.events.post("modern_callout", pool="mc_extra_ball_lit")
        self._show()

    def _light_special(self, **kwargs):
        if self.player.modern_special_state == 0:
            self.player.modern_special_state = 1
            self.machine.events.post("modern_special_lit")
            self.machine.events.post("modern_callout", pool="mc_special_lit")
        self._show()

    def _show(self):
        lamps = self.lamps
        lamps.set("extra_ball", settings.EXTRA_BALL_LAMP, STEADY if self.player.modern_extra_ball_lit else 0)
        special = self.player.modern_special_state == 1
        lamps.set("special", settings.SPECIAL_LAMP, FLASH if special else 0)
        lamps.set("special", settings.LOCATIONS["bar"][1], FLASH if special else 0)

    def mode_stop(self, **kwargs):
        self.player.modern_extra_ball_lit = 0
        try:
            self.lamps.clear("extra_ball")
            self.lamps.clear("special")
        except KeyError:
            pass
