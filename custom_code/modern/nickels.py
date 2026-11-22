"""The nickel hunt: directed club locations, escalating costs and the floor nickel."""

import random

from mpf.core.mode import Mode

from custom_code.modern import settings
from custom_code.modern.jukebox import song_mode_running
from custom_code.modern.lamps import FLASH, director
from custom_code.modern.scoring import award


class ModernNickels(Mode):

    def mode_start(self, **kwargs):
        self.suspended = 0
        self.last_location = ""
        self.player.modern_nickel_cost = self.cost()
        self.add_mode_event_handler("modern_location_hit", self._location_hit)
        self.add_mode_event_handler("modern_floor_nickel", self._floor_nickel)
        self.add_mode_event_handler("modern_nickel_spent", self._spent)
        self.add_mode_event_handler("modern_extra_ball_lit", self._extra_ball_lit)
        for event in ("modern_song_started", "multiball_modern_rent_party_started"):
            self.add_mode_event_handler(event, self._suspend)
        for event in ("modern_song_ended", "modern_rent_party_ended"):
            self.add_mode_event_handler(event, self._resume)
        # The skill shot comes first: the nickel hunt starts on the ball's first playfield switch.
        self.player.modern_nickel_target = ""
        self.add_mode_event_handler("modern_ball_in_play", self._ball_in_play)
        self._show()

    def _ball_in_play(self, **kwargs):
        if not self.player.modern_nickel_target:
            self._direct()

    @property
    def lamps(self):
        return director(self.machine)

    def cost(self):
        return settings.NICKEL_COSTS[self.player.modern_nickel_step % len(settings.NICKEL_COSTS)]

    def hunting(self):
        return not self.suspended and not song_mode_running(self.machine) and not self.player.modern_nickel

    def _suspend(self, **kwargs):
        self.suspended += 1
        self._show()

    def _resume(self, **kwargs):
        self.suspended = max(0, self.suspended - 1)
        self._show()

    def _direct(self, exclude=""):
        if self.player.modern_nickel:
            self.player.modern_nickel_target = ""
        else:
            # The Kitchen shares L45 with Extra Ball, so it is never the target while extra ball is lit.
            blocked = {exclude, "kitchen" if self.player.modern_extra_ball_lit else ""}
            choices = [l for l in settings.LOCATION_NAMES if l not in blocked]
            self.player.modern_nickel_target = random.choice(choices)
            if self.hunting():
                self._announce_target()
        self._show()

    def _announce_target(self):
        """The target's staff call the player over, or the MC points the way."""
        target = self.player.modern_nickel_target
        staff = settings.LOCATIONS[target][2]
        pool = random.choice([f"{staff}_direction", f"mc_target_{target}"])
        self.machine.events.post("modern_callout", pool=pool)

    def _remind(self):
        if self.hunting() and self.player.modern_nickel_target:
            self._announce_target()
        self.delay.reset(ms=settings.TARGET_REMINDER_MS, name="remind", callback=self._remind)

    def _extra_ball_lit(self, **kwargs):
        if self.player.modern_nickel_target == "kitchen":
            self._direct(exclude="kitchen")

    def _show(self):
        self.lamps.clear("nickel")
        target = self.player.modern_nickel_target
        if self.hunting() and target:
            self.delay.reset(ms=settings.TARGET_REMINDER_MS, name="remind", callback=self._remind)
            self.lamps.set("nickel", settings.LOCATIONS[target][1], FLASH)
            self.machine.events.post("modern_nickel_directed", location=target,
                                     location_name=settings.LOCATIONS[target][0],
                                     progress=self.player.modern_nickel_progress, cost=self.cost())

    def _callout(self, pool, location, **kwargs):
        self.machine.events.post("modern_callout", pool=f"{settings.LOCATIONS[location][2]}_{pool}", **kwargs)

    def _location_hit(self, location, **kwargs):
        # No target until the ball's first playfield switch; a plunge through the spinner comes first.
        if not self.hunting() or not self.player.modern_nickel_target:
            return
        if location != self.player.modern_nickel_target:
            if self.delay.check(f"refused_{location}"):
                return
            self.delay.add(ms=settings.REFUSAL_GAP_MS, name=f"refused_{location}", callback=lambda: None)
            # Staff may only name the real target; otherwise the MC points the way.
            self._callout("refusal", location, allow=(location, self.player.modern_nickel_target),
                          fallback=f"mc_target_{self.player.modern_nickel_target}")
            self.machine.events.post("modern_nickel_refused", location=location,
                                     location_name=settings.LOCATIONS[location][0],
                                     target=settings.LOCATIONS[self.player.modern_nickel_target][0])
            return
        self.player.modern_nickel_progress += 1
        if self.player.modern_nickel_progress < self.cost():
            self._direct(exclude=location)
            return
        value = settings.SCORE_NICKEL * 2 ** self.player.modern_nickel_cycle
        self.player.modern_nickel_progress = 0
        self.player.modern_nickel_step += 1
        if self.player.modern_nickel_step >= len(settings.NICKEL_COSTS):
            self.player.modern_nickel_step = 0
            self.player.modern_nickel_cycle += 1
        self.player.modern_nickel_cost = self.cost()
        self._give_nickel(value, location)

    def _floor_nickel(self, **kwargs):
        if self.player.modern_nickel:
            return
        self._give_nickel(settings.SCORE_NICKEL, "floor")

    def _give_nickel(self, value, source):
        self.player.modern_nickel = 1
        points = award(self.machine, value, "nickel")
        if source in settings.LOCATIONS:
            self._callout("nickel", source)
        else:
            self.machine.events.post("modern_callout", pool="mc_floor_nickel")
        self.machine.events.post("modern_nickel_awarded", source=source, points=points)
        self._direct()

    def _spent(self, **kwargs):
        self.player.modern_nickel = 0
        self._direct(exclude=self.last_location)

    def mode_stop(self, **kwargs):
        self.player.modern_nickel = 0
        self.player.modern_nickel_progress = 0
        self.player.modern_nickel_target = ""
        try:
            self.lamps.clear("nickel")
        except KeyError:
            pass
