"""Conservative pre-game occupancy counter for Volcano's subway."""

from mpf.devices.ball_device.entrance_switch_counter import EntranceSwitchCounter
from mpf.devices.ball_device.physical_ball_counter import BallLostActivity, BallEntranceActivity


class VolcanoSubwayCounter(EntranceSwitchCounter):
    """Treat switch 10 as evidence of at least one ball, not a full queue.

    Classic gameplay counts debounced crater passages after a travel delay;
    switch 10 alone cannot distinguish multiple queued balls.
    """

    def __init__(self, ball_device, config):
        super().__init__(ball_device, config)
        if any(self.machine.switch_controller.is_active(s) for s in self.config["entrance_switch"]):
            self._last_count = 1
            self._count_stable.set()

    def count_balls_sync(self):
        if not self._count_stable.is_set():
            raise ValueError("Subway count is not stable")
        return self._last_count

    def _entrance_switch_handler(self, switch_name):
        if not self.machine.game or self.machine.variables.get_machine_var("session_game") == "classic":
            # During recovery switch 10 is an occupancy sensor. Contact
            # bounce and balls advancing over it must not enqueue MPF ejects.
            return
        super()._entrance_switch_handler(switch_name)

    def crater_ball_arrived(self):
        """Record one inferred crater passage after its travel delay."""
        if not self.machine.game or self.machine.variables.get_machine_var("session_game") != "classic":
            return
        if self._last_count >= self.capacity:
            self.ball_device.log.warning("Ignored crater arrival: subway counter is full")
            return
        self._last_count += 1
        self.record_activity(BallEntranceActivity())
        self.mark_count_as_stable_and_trigger_activity()

    def _entrance_switch_full_handler(self):
        if self.machine.game:
            super()._entrance_switch_full_handler()

    def reconcile_empty_after_recovery(self):
        """Report observed empty subway through MPF's counter activity stream."""
        if self.machine.game:
            raise RuntimeError("Cannot reconcile subway while a game is active")
        if any(self.machine.switch_controller.is_active(s) for s in self.config["entrance_switch"]):
            raise RuntimeError("Cannot reconcile an occupied subway")
        old_count = self._last_count
        self._last_count = 0
        for _ in range(old_count):
            self.record_activity(BallLostActivity())
        self.mark_count_as_stable_and_trigger_activity()
