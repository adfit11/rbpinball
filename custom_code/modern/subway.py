"""Modern crater passages, reusing Classic's debounced subway inference."""

from custom_code.classic_subway import ClassicSubway


class ModernSubway(ClassicSubway):
    # A ball resting on switch 10 this long, with no crater passage to explain it, was missed by the craters.
    UNEXPLAINED_MS = 1000

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self._last_passage = -100
        self.switch_handlers.append(self.machine.switch_controller.add_switch_handler(
            "s_subway_lock_10", self._ball_on_switch_10, state=1, ms=self.UNEXPLAINED_MS))

    def _crater_passed(self, crater):
        self._last_passage = self.machine.clock.get_time()
        self.machine.modes["modern_jukebox"].crater_entered(crater)

    def _ball_on_switch_10(self, **kwargs):
        """Backstop: return a ball the craters never reported, as if it came through an unlit crater."""
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        counter = device.ball_count_handler.counter
        if counter._last_count or device.state != "idle":
            return
        if self.machine.clock.get_time() - self._last_passage < self.TRAVEL_MS / 1000:
            return  # that passage's arrival will count it
        device.log.warning("Ball on switch 10 with no crater passage; returning it through the kicker")
        self.machine.events.post("modern_subway_unexplained_ball")
        counter.crater_ball_arrived()
