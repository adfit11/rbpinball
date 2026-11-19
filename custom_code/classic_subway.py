"""Count crater passages that travel to the subway."""

from mpf.core.mode import Mode


class ClassicSubway(Mode):
    """Infer subway arrival after each debounced crater passage."""

    TRAVEL_MS = 2500
    FIRST_BALL_TIMEOUT_MS = 6000
    BOUNCE_SECONDS = .75
    # Ejects shake crater 4, and a contact held closed can blip open.
    QUIET_SECONDS = 1.5
    MIN_OPEN_SECONDS = .05
    EJECTORS = ("bd_trough", "bd_classic_subway_lock", "bd_classic_subway_kicker")
    CRATERS = ("s_ramp_1_34", "s_ramp_2_24", "s_ramp_3_14", "s_ramp_4_4")

    def mode_start(self, **kwargs):
        self._last_hits = {}
        self._opened = {}
        self._quiet_until = -100
        for crater, switch in enumerate(self.CRATERS, 1):
            self.add_mode_event_handler(switch + "_active", self._crater_hit, switch=switch, crater=crater)
            self.add_mode_event_handler(switch + "_inactive", self._crater_open, switch=switch)
        for device in self.EJECTORS:
            self.add_mode_event_handler("balldevice_{}_ejecting_ball".format(device), self._eject)

    def _crater_open(self, switch, **kwargs):
        self._opened[switch] = self.machine.clock.get_time()

    def _eject(self, **kwargs):
        self._quiet_until = self.machine.clock.get_time() + self.QUIET_SECONDS

    def _crater_hit(self, switch, crater, **kwargs):
        now = self.machine.clock.get_time()
        if now < self._quiet_until or now - self._opened.get(switch, -100) < self.MIN_OPEN_SECONDS:
            self.info_log("Ignored %s: eject vibration or brief contact opening", switch)
            return
        if now - self._last_hits.get(switch, -100) < self.BOUNCE_SECONDS:
            return
        self._last_hits[switch] = now
        self._crater_passed(crater)
        self.delay.add(ms=self.TRAVEL_MS, callback=self._arrived, elapsed_ms=self.TRAVEL_MS)

    def _crater_passed(self, crater):
        targets = self.machine.modes["classic_targets"]
        if targets.crater_index and crater >= targets.crater_index:
            self.machine.events.post("classic_lock_qualified")

    def _arrived(self, elapsed_ms):
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        counter = device.ball_count_handler.counter
        if (self.machine.variables.get_machine_var("lisy_hardware") and counter._last_count == 0
                and not self.machine.switch_controller.is_active(self.machine.switches["s_subway_lock_10"])):
            if elapsed_ms >= self.FIRST_BALL_TIMEOUT_MS:
                device.log.error("Crater ball did not reach subway switch 10")
                self.machine.events.post("classic_subway_arrival_unconfirmed")
                return
            self.delay.add(ms=100, callback=self._arrived, elapsed_ms=elapsed_ms + 100)
            return
        counter.crater_ball_arrived()
