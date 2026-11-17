"""Classic's skill shot cam, which sweeps while a served ball waits in the shooter lane."""

from mpf.core.mode import Mode


class ClassicSkillShot(Mode):
    START_DELAY_MS = 1000
    TIMEOUT_MS = 30000
    # Inputs that are not ball contact, or that the served ball cannot reach from the lane.
    IGNORED_SWITCHES = {
        "s_flipper_left", "s_flipper_right", "s_green_button_right_56", "s_test_switch_7",
        "s_start_47", "s_tilt_46", "s_trough_1_40", "s_trough_2_30", "s_trough_3_20",
        "s_subway_kicker_0", "s_subway_one_3", "s_subway_lock_10",
    }

    def mode_start(self, **kwargs):
        self.motor = self.machine.digital_outputs["skill_motor"]
        self.running = False
        self.motor_on = False
        self.add_mode_event_handler("balldevice_bd_trough_ejecting_ball", self._serve)
        for event in ("s_green_button_right_56_active", "tilt", "slam_tilt"):
            self.add_mode_event_handler(event, self._stop)
        for switch in self.machine.switches.values():
            if switch.name not in self.IGNORED_SWITCHES:
                self.add_mode_event_handler(switch.name + "_active", self._playfield_hit)

    def _serve(self, target, **kwargs):
        if target is not self.machine.playfield:
            return
        self.running = True
        self.delay.reset(ms=self.START_DELAY_MS, name="start", callback=self._start_motor)

    def _start_motor(self):
        self.motor_on = True
        self.motor.enable()
        self.delay.reset(ms=self.TIMEOUT_MS, name="timeout", callback=self._stop)

    def _playfield_hit(self, **kwargs):
        # The trough release shakes the spinner, so contacts only count once the motor runs.
        if self.motor_on:
            self._stop()

    def _stop(self, **kwargs):
        if self.running:
            self.running = False
            self.motor_on = False
            self.delay.remove("start")
            self.delay.remove("timeout")
            self.motor.disable()

    def mode_stop(self, **kwargs):
        self.running = False
        self.motor_on = False
        self.motor.disable()
