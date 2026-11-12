"""Interlocked MPF subway ejector."""

from mpf.devices.ball_device.pulse_coil_ejector import PulseCoilEjector

from custom_code.subway_recovery import SubwayReleaseInterlock


class InterlockedSubwayEjector(PulseCoilEjector):
    """Route MPF ejects through an arrival-and-clear interlock.

    Startup recovery and MPF eject requests share this interlock.
    """

    __slots__ = ["guard", "_timer", "_reported_fault"]

    def __init__(self, config, ball_device, machine):
        super().__init__(config, ball_device, machine)
        self.guard = SubwayReleaseInterlock()
        self._timer = None
        self._reported_fault = False
        for state in (0, 1):
            machine.switch_controller.add_switch_handler(
                "s_subway_kicker_0", self._observe, state=state)
        machine.events.add_handler("request_to_start_game", self._allow_start)

    def _allow_start(self, **kwargs):
        """Refuse a game while physical recovery or a handoff is unfinished."""
        del kwargs
        self._observe()
        switches = self.machine.switches
        controller = self.machine.switch_controller
        trough = self.machine.ball_devices["bd_trough"]
        kicker = self.machine.ball_devices["bd_classic_subway_kicker"]
        return (self.guard.state == "ready"
                and not controller.is_active(switches["s_subway_lock_10"])
                and not controller.is_active(switches["s_subway_kicker_0"])
                and self.ball_device.balls == 0
                and kicker.balls == 0
                and trough.balls == 3
                and self.machine.ball_controller.num_balls_known == 3)

    def _observe(self):
        now = self.machine.clock.get_time()
        active = self.machine.switch_controller.is_active(self.machine.switches["s_subway_kicker_0"])
        state = self.guard.observe(now, active)
        if state == "failed" and not self._reported_fault:
            self._reported_fault = True
            self.ball_device.log.error("Subway release interlock: %s", self.guard.reason)
            self.machine.events.post("subway_release_interlock_failed", reason=self.guard.reason)
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if state in ("waiting_for_arrival", "waiting_for_clear"):
            self._timer = self.machine.clock.loop.call_later(.05, self._observe)

    async def eject_one_ball(self, is_jammed, eject_try, balls_in_device):
        if self._reserve():
            await super().eject_one_ball(is_jammed, eject_try, balls_in_device)

    def _reserve(self):
        """Reserve the only release before scheduling any coil action."""
        self._observe()
        controller = self.machine.switch_controller
        kicker_switch = self.machine.switches["s_subway_kicker_0"]
        # Require a settled empty kicker even for the first release at boot.
        kicker_ready = controller.is_inactive(kicker_switch, ms=500)
        lock_active = controller.is_active(self.machine.switches["s_subway_lock_10"])
        attract = self.machine.modes.get("attract")
        recovery = getattr(attract, "subway_startup", None)
        waiting = (recovery is not None and recovery.status in ("running", "reconciling")
                   and recovery.awaiting_return)
        outhole_active = controller.is_active(self.machine.switches["s_trough_3_20"])
        if ((not self.machine.game and (not lock_active or waiting or outhole_active))
                or not self.guard.request(self.machine.clock.get_time(), not kicker_ready)):
            self.ball_device.log.warning("Subway release blocked by kicker interlock")
            self.machine.events.post("subway_release_interlock_blocked", state=self.guard.state)
            return False
        self._observe()
        return True

    def request_recovery_release(self):
        """Request one guarded release without relying on MPF's lock count."""
        if not self._reserve():
            return False
        self.machine.clock.loop.create_task(
            super().eject_one_ball(False, 1, 1))
        return True

    def ball_search(self, phase, iteration):
        """Never let ball search bypass the release interlock."""
        del phase, iteration
        return False

    async def reorder_balls(self):
        """A reorder pulse cannot be safely distinguished from a release."""
        self.ball_device.log.warning("Subway reorder blocked by kicker interlock")
