"""Trough release that re-pulses when a serve leaves both trough switches untouched."""

from mpf.devices.ball_device.pulse_coil_ejector import PulseCoilEjector

TROUGH_SWITCHES = ("s_trough_1_40", "s_trough_2_30")
# A good serve moves switch 40 or 30 within about a second on the cabinet.
SERVE_CHECK_S = 1.5
MAX_PULSES = 3


class RetryingTroughEjector(PulseCoilEjector):
    """Every pulse stays LISY-timed; a missed serve just gets another pulse.

    There is no shooter-lane switch, so MPF alone would count a missed serve as served.
    """

    __slots__ = ["_moved", "_pulses", "_timer"]

    def __init__(self, config, ball_device, machine):
        super().__init__(config, ball_device, machine)
        self._moved = False
        self._pulses = 0
        self._timer = None
        for name in TROUGH_SWITCHES:
            for state in (0, 1):
                machine.switch_controller.add_switch_handler(name, self._switch_moved, state=state)

    def _switch_moved(self):
        self._moved = True

    async def eject_one_ball(self, is_jammed, eject_try, balls_in_device):
        await super().eject_one_ball(is_jammed, eject_try, balls_in_device)
        if self.machine.variables.get_machine_var("lisy_hardware"):
            self._pulses = 1
            self._watch()

    def _watch(self):
        self._moved = False
        if self._timer is not None:
            self._timer.cancel()
        self._timer = self.machine.clock.loop.call_later(SERVE_CHECK_S, self._check)

    def _check(self):
        self._timer = None
        if self._moved:
            return
        if self._pulses >= MAX_PULSES:
            self.ball_device.log.error("Trough serve failed after %s pulses", self._pulses)
            self.machine.events.post("trough_serve_failed", pulses=self._pulses)
            self.machine.events.post("modern_overlay", title="BALL DIDN'T SERVE",
                                     subtitle="Check the trough", ms=4000)
            return
        self._pulses += 1
        self.ball_device.log.warning("Trough serve missed; pulse %s of %s", self._pulses, MAX_PULSES)
        self.machine.events.post("trough_serve_retry", pulse=self._pulses)
        counter = self.ball_device.ball_count_handler.counter
        counter._serve_settles_at = self.machine.clock.get_time() + counter.SERVE_SETTLE_SECONDS
        self.config['eject_coil'].pulse()
        self._watch()
