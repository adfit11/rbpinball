"""Startup clearing adapter for the cabinet subway."""

from custom_code.subway_recovery import SubwayRecoveryRunner


class SubwayStartupClear:
    """Poll the two physical switches and dispatch through guarded ejectors.

    Completion requires the subway to be clear and MPF to agree that all
    three balls are home.
    """

    INTERVAL = .05
    RETURN_TIMEOUT = 60.0

    def __init__(self, machine):
        self.machine = machine
        self.runner = None
        self._timer = None
        self.status = "idle"
        self.reason = None
        self._reconciled = False
        self.awaiting_return = False
        self._return_deadline = None
        self._return_handler = None

    def start(self):
        if self.status in ("running", "reconciling"):
            return False
        release = self.machine.ball_devices["bd_classic_subway_lock"].ejector
        kicker = self.machine.ball_devices["bd_classic_subway_kicker"].ejector
        if not hasattr(release, "request_recovery_release") or not hasattr(kicker, "request_recovery_kick"):
            self.status = "failed"
            self.reason = "Guarded subway ejectors are not installed"
            return False
        self.runner = SubwayRecoveryRunner(self)
        self._reconciled = False
        self.awaiting_return = False
        self._return_deadline = None
        self._return_handler = self.machine.events.add_handler(
            "balldevice_bd_outhole_ball_eject_success", self._ball_returned)
        self.status = "running"
        self._tick()
        return True

    def request_release(self):
        ejector = self.machine.ball_devices["bd_classic_subway_lock"].ejector
        if ejector.guard.state == "waiting_for_arrival":
            # MPF already released this ball; track the existing handoff.
            self._wait_for_return()
            return True
        accepted = ejector.request_recovery_release()
        if accepted:
            self._wait_for_return()
        return accepted

    def _wait_for_return(self):
        if not self.awaiting_return:
            self.awaiting_return = True
            self._return_deadline = self.machine.clock.get_time() + self.RETURN_TIMEOUT

    def _ball_returned(self, **kwargs):
        del kwargs
        if self.awaiting_return:
            self.awaiting_return = False
            self._return_deadline = None
            self.machine.events.post("subway_startup_ball_home")

    def _finish(self, status, reason=None):
        self.status = status
        self.reason = reason
        if self._return_handler is not None:
            self.machine.events.remove_handler_by_key(self._return_handler)
            self._return_handler = None
        self.machine.events.post("subway_startup_clear_" + status, reason=reason)

    def request_kick(self):
        kicker = self.machine.ball_devices["bd_classic_subway_kicker"].ejector
        if kicker.state == "waiting_for_clear":
            # MPF has already reserved and fired this kicker, so do not add
            # a second pulse. The runner still waits for the switch to clear.
            return True
        return kicker.request_recovery_kick()

    def _reconcile_home_counts(self):
        """Discard phantom playfield balls only when all three are home."""
        if self.machine.game:
            return
        trough = self.machine.ball_devices["bd_trough"]
        controller = self.machine.switch_controller
        if (trough.balls != 3 or trough.available_balls != 3
                or not controller.is_active(self.machine.switches["s_trough_1_40"], ms=1000)):
            return
        for device in self.machine.ball_devices.values():
            if device.is_playfield() or device is trough:
                continue
            if device.balls or device.state != "idle":
                return
        ball_controller = self.machine.ball_controller
        if not ball_controller._captured_balls.empty():
            return
        playfield = self.machine.playfield
        if (ball_controller.num_balls_known != 3 or playfield.balls != 0
                or playfield.available_balls != 0):
            old_known = ball_controller.num_balls_known
            old_playfield = playfield.balls
            ball_controller.num_balls_known = 3
            playfield.balls = 0
            playfield.available_balls = 0
            self.machine.events.post("subway_startup_home_counts_reconciled",
                                     old_known=old_known, old_playfield=old_playfield)

    def _tick(self):
        if self.status not in ("running", "reconciling"):
            return
        switches = self.machine.switches
        controller = self.machine.switch_controller
        trough_counter = self.machine.ball_devices["bd_trough"].ball_count_handler.counter
        if hasattr(trough_counter, "reconcile_empty_at_start"):
            trough_counter.reconcile_empty_at_start()
        lock = controller.is_active(switches["s_subway_lock_10"])
        kicker = controller.is_active(switches["s_subway_kicker_0"])
        release = self.machine.ball_devices["bd_classic_subway_lock"].ejector
        outhole = controller.is_active(switches["s_trough_3_20"])
        if kicker or outhole or release.guard.state == "waiting_for_arrival":
            self._wait_for_return()
        if self.awaiting_return and self.machine.clock.get_time() >= self._return_deadline:
            self._finish("failed", "Ball did not return to the trough within 60 seconds")
            return
        if self.status == "reconciling":
            if lock or kicker:
                self._finish("failed", "A subway switch became active while reconciling")
                return
            counter = self.machine.ball_devices["bd_classic_subway_lock"].ball_count_handler.counter
            if not self._reconciled and hasattr(counter, "reconcile_empty_after_recovery"):
                counter.reconcile_empty_after_recovery()
                self._reconciled = True
            self._reconcile_home_counts()
            kicker_ejector = self.machine.ball_devices["bd_classic_subway_kicker"].ejector
            if release._allow_start() and kicker_ejector.state == "ready":
                if not self.awaiting_return:
                    self._finish("done")
                    return
            self._timer = self.machine.clock.loop.call_later(self.INTERVAL, self._tick)
            return
        if (self.runner.sequence.state == "settling" and not kicker
                and (self.awaiting_return or release.guard.state == "waiting_for_clear")):
            # Do not begin a new release until the previous handoff is fully
            # clear, even if switch 10 already shows another waiting ball.
            self._timer = self.machine.clock.loop.call_later(self.INTERVAL, self._tick)
            return
        action = self.runner.update(self.machine.clock.get_time(), lock, kicker)
        if action == "failed":
            self._finish("failed", self.runner.sequence.reason)
            return
        if action == "done":
            self.status = "reconciling"
            self.machine.events.post("subway_startup_cleared_waiting_for_balls")
        self._timer = self.machine.clock.loop.call_later(self.INTERVAL, self._tick)

    def stop(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self.status in ("running", "reconciling"):
            self.status = "stopped"
        if self._return_handler is not None:
            self.machine.events.remove_handler_by_key(self._return_handler)
            self._return_handler = None
