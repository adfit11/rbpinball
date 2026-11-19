"""Modern's only ball save: the manually operated Bouncer, readied by Drop the Needle."""

from mpf.core.mode import Mode


class ModernBallSaver(Mode):

    def mode_start(self, **kwargs):
        self.player.modern_ball_saver_ready = 0
        self.add_mode_event_handler("modern_ball_saver_qualified", self.ready)
        self.add_mode_event_handler("s_outlane_left_6_active", self._used)
        for event in ("tilt", "slam_tilt"):
            self.add_mode_event_handler(event, self.clear)

    def ready(self, **kwargs):
        if not self.player.modern_ball_saver_ready:
            self.player.modern_ball_saver_ready = 1
            self.machine.coils["c_classic_ball_saver"].pulse()
            self.machine.events.post("modern_ball_saver_ready")

    def _used(self, **kwargs):
        if self.player.modern_ball_saver_ready:
            self.player.modern_ball_saver_ready = 0
            self.machine.events.post("modern_ball_saved")
            self.machine.events.post("modern_callout", pool="doorman_ball_saved")

    def clear(self, **kwargs):
        self.player.modern_ball_saver_ready = 0

    def mode_stop(self, **kwargs):
        self.player.modern_ball_saver_ready = 0
