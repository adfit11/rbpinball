"""Game-long Modern presentation: the rules splash and the HUD slide."""

from mpf.core.mode import Mode

from custom_code.modern import settings


class ModernDisplay(Mode):

    def mode_start(self, **kwargs):
        self.splash_queue = None
        self.add_mode_event_handler("ball_starting", self._ball_starting, priority=10000)
        self.add_mode_event_handler("s_start_47_active", self._end_splash)
        self.splash_shown = False

    def _ball_starting(self, queue=None, **kwargs):
        if self.splash_shown or queue is None:
            return
        self.splash_shown = True
        queue.wait()
        self.splash_queue = queue
        self.machine.events.post("modern_splash_show")
        self.delay.reset(ms=settings.SPLASH_MS, name="splash", callback=self._end_splash)

    def _end_splash(self, **kwargs):
        if self.splash_queue is None:
            return
        self.delay.remove("splash")
        queue, self.splash_queue = self.splash_queue, None
        self.machine.events.post("modern_splash_hide")
        queue.clear()

    def mode_stop(self, **kwargs):
        self._end_splash()
