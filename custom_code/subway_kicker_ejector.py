"""Single-owner kicker for startup recovery and MPF ejects."""

from mpf.devices.ball_device.pulse_coil_ejector import PulseCoilEjector


class GuardedSubwayKicker(PulseCoilEjector):
    """Pulse only with a ball present and no kick already in progress.

    Startup recovery and MPF eject requests share this guard.
    """

    __slots__ = ["state", "deadline", "clear_since", "_timer"]
    TIMEOUT = 3.0
    CLEAR_SETTLE = .5

    def __init__(self, config, ball_device, machine):
        super().__init__(config, ball_device, machine)
        self.state = "ready"
        self.deadline = None
        self.clear_since = None
        self._timer = None
        for state in (0, 1):
            machine.switch_controller.add_switch_handler("s_subway_kicker_0", self._observe, state=state)

    def _active(self):
        return self.machine.switch_controller.is_active(self.machine.switches["s_subway_kicker_0"])

    def _observe(self):
        now = self.machine.clock.get_time()
        if self.state == "waiting_for_clear":
            if now >= self.deadline:
                self.state = "failed"
                self.ball_device.log.error("Subway kicker failed to clear")
                self.machine.events.post("subway_kicker_interlock_failed")
            elif self._active():
                self.clear_since = None
            elif self.clear_since is None:
                self.clear_since = now
            elif now - self.clear_since >= self.CLEAR_SETTLE:
                self.state = "ready"
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self.state == "waiting_for_clear":
            self._timer = self.machine.clock.loop.call_later(.05, self._observe)

    def _reserve(self):
        self._observe()
        if self.state != "ready" or not self._active():
            self.machine.events.post("subway_kicker_interlock_blocked", state=self.state)
            return False
        self.state = "waiting_for_clear"
        self.deadline = self.machine.clock.get_time() + self.TIMEOUT
        self.clear_since = None
        self._observe()
        return True

    async def eject_one_ball(self, is_jammed, eject_try, balls_in_device):
        if self._reserve():
            await super().eject_one_ball(is_jammed, eject_try, balls_in_device)

    def request_recovery_kick(self):
        """Reserve before yielding so MPF cannot schedule a second kick."""
        if not self._reserve():
            return False
        self.machine.clock.loop.create_task(super().eject_one_ball(False, 1, 1))
        return True

    def ball_search(self, phase, iteration):
        del phase, iteration
        return False

    async def reorder_balls(self):
        self.ball_device.log.warning("Subway kicker reorder blocked")
