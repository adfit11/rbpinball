"""Shared helpers for Modern MPF tests."""

from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class ModernTestCase(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def start_modern(self, players=1, skip_splash=True):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.hit_and_release_switch("s_flipper_right")
        self.hit_and_release_switch("s_start_47")
        for _ in range(players - 1):
            self.hit_and_release_switch("s_flipper_right")
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(.5)
        if skip_splash:
            self.hit_and_release_switch("s_start_47")
            self.advance_time_and_run(2)
            self.hit_and_release_switch("s_10_points_15")
            self.advance_time_and_run(1.5)

    @property
    def player(self):
        return self.machine.game.player

    def light_crater(self, crater):
        targets = self.machine.modes["modern_targets"]
        targets.delay.remove("craters")
        targets.crater_index = crater
        targets._show_lamps()

    def shoot_crater(self, crater):
        self.light_crater(crater)
        switch = self.machine.modes["modern_targets"].CRATER_SWITCHES[crater - 1]
        self.hit_and_release_switch(switch)
        self.advance_time_and_run(.1)

    def give_nickel(self):
        self.post_event("modern_floor_nickel", .1)
        self.assertEqual(self.player.modern_nickel, 1)

    def hit_location(self, location, wait_release=True):
        if location in ("bar", "kitchen"):
            device = self.machine.ball_devices["bd_classic_saucer" if location == "bar" else "bd_classic_firepit"]
            self.machine.default_platform.add_ball_to_device(device)
            self.advance_time_and_run(1.2)  # entrance confirmation, then the hold claims the ball
            for _ in range(150):  # an eject to the playfield confirms after its 10 s timeout
                if not wait_release or (not device.balls and device.state == "idle"):
                    break
                self.advance_time_and_run(.1)
        elif location == "bandstand":
            self.advance_time_and_run(1.1)
            self.hit_and_release_switch("s_spinner_44")
            self.advance_time_and_run(.1)
        elif location == "coat_check":
            self.hit_and_release_switch("s_spot_target_36")
            self.advance_time_and_run(.1)
        elif location == "booths":
            targets = self.machine.modes["modern_targets"]
            self.hit_switch_and_run(targets.DROP_SWITCHES["right_bank"][targets.booth - 1], .1)
