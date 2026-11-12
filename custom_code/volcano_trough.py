"""MPF entrance counting for the original two-switch Volcano trough."""

from mpf.devices.ball_device.entrance_switch_counter import EntranceSwitchCounter
from mpf.devices.ball_device.physical_ball_counter import BallLostActivity


class VolcanoTroughCounter(EntranceSwitchCounter):
    """Ignore switch 40 activity caused by serving a ball on the cabinet."""

    SERVE_SETTLE_SECONDS = 1.5

    def __init__(self, ball_device, config):
        self._serve_settles_at = 0
        self._ignored_serve_closure = False
        super().__init__(ball_device, config)

    async def wait_for_ball_to_leave(self):
        ball_left = await super().wait_for_ball_to_leave()
        if self.machine.variables.get_machine_var("lisy_hardware"):
            self._serve_settles_at = self.machine.clock.get_time() + self.SERVE_SETTLE_SECONDS
        return ball_left

    def _is_serve_activity(self):
        return (self.machine.clock.get_time() < self._serve_settles_at
                and not self.ball_device.incoming_balls_handler.get_num_incoming_balls())

    def _entrance_switch_handler(self, switch_name):
        self._ignored_serve_closure = self._is_serve_activity()
        if not self._ignored_serve_closure:
            super()._entrance_switch_handler(switch_name)

    def _entrance_switch_full_handler(self):
        if not self._ignored_serve_closure and not self._is_serve_activity():
            super()._entrance_switch_full_handler()

    def reconcile_empty_at_start(self):
        """Correct a stale full count only with stable empty-trough evidence."""
        if self.machine.game:
            return False
        switches = self.machine.switches
        controller = self.machine.switch_controller
        if not controller.is_active(switches["s_trough_3_20"], ms=500):
            return False
        if not all(controller.is_inactive(switches[name], ms=1000)
                   for name in ("s_trough_1_40", "s_trough_2_30")):
            return False
        if self._last_count != 3:
            return False
        self._last_count = 0
        for _ in range(3):
            self.record_activity(BallLostActivity())
        self.mark_count_as_stable_and_trigger_activity()
        self.machine.events.post("trough_startup_empty_reconciled")
        return True
