"""Step through playfield outputs with a fresh Start press per test."""

from mpf.core.custom_code import CustomCode


class CoilSurvey(CustomCode):
    # The motor gets a short identification test, rather than its 5 s game pulse.
    tests = (
        ("c_subway_lock", "Subway ball release", None),
        ("c_top_drops", "Top drop-target reset", None),
        ("c_subway_kicker", "Subway kicker", None),
        ("c_right_drops", "Right drop-target reset", None),
        ("c_outhole", "Bottom outhole", None),
        ("c_side_kicker_left", "Left side / fire-pit kicker", None),
        ("c_hole_kicker_top", "Top hole kicker", None),
        ("c_trough_release", "Trough release", None),
        ("c_skill_motor", "Motor relay", 250),
    )

    def on_load(self):
        self.index = 0
        self.armed = False
        self.machine.events.add_handler("init_done", self.prepare)
        self.machine.events.add_handler("s_start_47_active", self.fire)

    def prepare(self, **kwargs):
        self.delay.add(ms=1500, callback=self.arm)

    def arm(self):
        if self.machine.switches["s_start_47"].state:
            self.delay.add(ms=100, callback=self.arm)
            return
        name, label, override = self.tests[self.index]
        coil = self.machine.coils[name]
        duration = coil.get_and_verify_pulse_ms(override)
        self.armed = True
        self.info_log("SURVEY READY %s/%s: %s, output %s, %s ms. Press Start once.",
                      self.index + 1, len(self.tests), label, coil.config["number"], duration)

    def fire(self, **kwargs):
        if not self.armed:
            return
        self.armed = False
        name, label, override = self.tests[self.index]
        coil = self.machine.coils[name]
        duration = coil.get_and_verify_pulse_ms(override)
        self.info_log("SURVEY FIRED %s/%s: %s, output %s, %s ms. Record physical result.",
                      self.index + 1, len(self.tests), label, coil.config["number"], duration)
        coil.pulse(pulse_ms=duration)
        self.index += 1
        # Finish after the timed pulse, or allow time to observe before the next.
        if self.index == len(self.tests):
            self.delay.add(ms=duration + 1000, callback=self.finish)
        else:
            self.delay.add(ms=duration + 2000, callback=self.arm)

    def finish(self):
        self.info_log("SURVEY COMPLETE: commands sent; physical results require observation.")
        self.machine.stop("Playfield coil survey complete")
