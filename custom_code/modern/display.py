"""Game-long Modern presentation: the rules splash and the HUD slide."""

from mpf.core.mode import Mode

from custom_code.modern import settings


class ModernDisplay(Mode):

    def mode_start(self, **kwargs):
        self.splash_queue = None
        self.add_mode_event_handler("ball_starting", self._ball_starting, priority=10000)
        self.add_mode_event_handler("s_start_47_active", self._end_splash)
        self.splash_shown = False
        self._green_at = None
        self.add_mode_event_handler(settings.TAP_SWITCH + "_active", self._green_down)
        self.add_mode_event_handler(settings.TAP_SWITCH + "_inactive", self._green_up)

    def _ball_starting(self, queue=None, **kwargs):
        if self.splash_shown or queue is None:
            self.machine.events.post("modern_callout", pool="mc_ball_start")
            return
        self.splash_shown = True
        # The HUD slide is created as the game starts and subscribes to voice lines over BCP a moment later.
        self.delay.add(ms=settings.GAME_START_CALLOUT_MS, name="welcome",
                       callback=self.machine.events.post, event="modern_callout", pool="mc_game_start")
        queue.wait()
        self.splash_queue = queue
        self.machine.events.post("modern_splash_show")

    def _end_splash(self, **kwargs):
        if self.splash_queue is None:
            return
        queue, self.splash_queue = self.splash_queue, None
        self.machine.events.post("modern_splash_hide")
        queue.clear()

    # High-score entry runs after the ball modes stop, so the select action lives here too.
    def _entering_initials(self):
        return "modern_high_score" in self.machine.modes and self.machine.modes["modern_high_score"].active

    def _green_down(self, **kwargs):
        if self._entering_initials():
            self._green_at = self.machine.clock.get_time()
            self.delay.reset(ms=settings.SELECT_HOLD_MS, name="hs_select", callback=self._hs_select)

    def _hs_select(self):
        self._green_at = None
        self.machine.events.post("modern_hs_select")

    def _green_up(self, **kwargs):
        self.delay.remove("hs_select")
        if self._green_at is not None and self._entering_initials():
            self.machine.events.post("modern_hs_tap")
        self._green_at = None

    def mode_stop(self, **kwargs):
        self._end_splash()
