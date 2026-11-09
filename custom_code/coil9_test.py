"""Test a physical LISY output with one button-triggered timed pulse."""

from mpf.core.custom_code import CustomCode


class Coil9Test(CustomCode):
    output = 9
    coil_name = "c_test_output9"

    def on_load(self):
        self.fired = False
        self.machine.events.add_handler("init_done", self.wait_to_arm)

    def wait_to_arm(self, **kwargs):
        # Let pending hardware changes drain before accepting a new button press.
        self.delay.add(ms=1000, callback=self.arm)

    def arm(self, **kwargs):
        if self.machine.switches["s_start_47"].state:
            self.delay.add(ms=100, callback=self.arm)
            return
        self.machine.events.add_handler("s_start_47_active", self.fire)
        self.pulse_ms = self.machine.coils[self.coil_name].get_and_verify_pulse_ms(None)
        self.info_log("COIL TEST ARMED: output %s; press Start once for one %s ms pulse.",
                      self.output, self.pulse_ms)

    def fire(self, **kwargs):
        if self.fired:
            return
        self.fired = True
        self.machine.events.remove_handler(self.fire)
        self.info_log("COIL TEST: pulsing output %s once for %s ms.", self.output, self.pulse_ms)
        self.machine.coils[self.coil_name].pulse()
        self.delay.add(ms=1000, callback=self.finish)

    def finish(self):
        self.info_log("COIL TEST COMPLETE: shutting down; report which mechanism moved.")
        self.machine.stop("One-shot coil diagnostic complete")


class Coil115Test(Coil9Test):
    output = 115
    coil_name = "c_test_output115"
