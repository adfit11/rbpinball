"""MPF entrance counting for the original two-switch Volcano trough."""

from mpf.devices.ball_device.entrance_switch_counter import EntranceSwitchCounter


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
