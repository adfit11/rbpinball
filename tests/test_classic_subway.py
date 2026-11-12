"""Verify Classic subway accounting with MPF's smart virtual devices."""

from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class TestClassicSubway(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def start_classic(self, players):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.hit_and_release_switch("s_flipper_left")
        self.hit_and_release_switch("s_start_47")
        for _ in range(players - 1):
            self.hit_and_release_switch("s_flipper_right")
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.hit_and_release_switch("s_10_points_15")

    def capture(self):
        # Shoot the lit crater before the ball reaches the lock entrance.
        targets = self.machine.modes["classic_targets"]
        if targets.crater_index == 0:
            self.advance_time_and_run(.3)
        switch = targets.CRATER_SWITCHES[targets.crater_index - 1]
        self.assertNotEqual(targets.crater_index, 0)
        self.hit_and_release_switch(switch)
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(3.2)

    def test_lock_entrance_repeat_does_not_release_locked_ball(self):
        self.start_classic(1)
        targets = self.machine.modes["classic_targets"]
        targets.crater_index = 4
        self.hit_and_release_switch("s_ramp_4_4")
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(.54)
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(3)
        self.assertEqual(self.machine.ball_devices["bd_classic_subway_lock"].balls, 1)
        self.assertEqual(self.machine.game.player.classic_locks, 1)

    def test_second_lit_crater_locks_while_first_ball_holds_switch_10(self):
        self.start_classic(1)
        targets = self.machine.modes["classic_targets"]
        targets.crater_index = 4
        self.hit_and_release_switch("s_ramp_4_4")
        self.hit_switch_and_run("s_subway_lock_10", 3)
        self.assertEqual(self.machine.game.player.classic_locks, 1)
        targets.crater_index = 3
        self.hit_and_release_switch("s_ramp_3_14")
        self.advance_time_and_run(4)
        self.assertEqual(self.machine.game.player.classic_locks, 2)
        self.assertBallsInPlay(1)

    def test_unlit_crater_releases_one_ball_and_keeps_existing_lock_count(self):
        self.start_classic(1)
        self.capture()
        self.mock_event("multiball_lock_classic_subway_lock_locked_ball")
        self.mock_event("balldevice_bd_classic_subway_lock_ball_eject_success")
        targets = self.machine.modes["classic_targets"]
        targets.crater_index = 4
        self.hit_and_release_switch("s_ramp_1_34")
        self.advance_time_and_run(8)
        self.assertEventNotCalled("multiball_lock_classic_subway_lock_locked_ball")
        self.assertEventCalled("balldevice_bd_classic_subway_lock_ball_eject_success", 1)
        self.assertEqual(self.machine.ball_devices["bd_classic_subway_lock"].balls, 1)
        self.assertEqual(self.machine.game.player.classic_locks, 1)
        self.assertBallsInPlay(1)

    def test_three_lit_passages_start_multiball_with_switch_10_held(self):
        self.start_classic(1)
        self.mock_event("multiball_classic_subway_started")
        targets = self.machine.modes["classic_targets"]
        for crater, switch in ((4, "s_ramp_4_4"), (3, "s_ramp_3_14"), (2, "s_ramp_2_24")):
            targets.crater_index = crater
            self.hit_and_release_switch(switch)
            if crater == 4:
                self.hit_switch_and_run("s_subway_lock_10", .1)
            self.advance_time_and_run(3.2)
        self.advance_time_and_run(10)
        self.assertEventCalled("multiball_classic_subway_started", 1)
        self.assertBallsInPlay(3)

    def test_crater_contact_bounce_counts_one_passage(self):
        self.start_classic(1)
        targets = self.machine.modes["classic_targets"]
        targets.crater_index = 4
        for _ in range(4):
            self.hit_and_release_switch("s_ramp_4_4")
            self.advance_time_and_run(.05)
        self.advance_time_and_run(4)
        self.assertEqual(self.machine.game.player.classic_locks, 1)
        self.assertEqual(self.machine.ball_devices["bd_classic_subway_lock"].balls, 1)

    def test_cabinet_first_ball_requires_subway_switch(self):
        self.start_classic(1)
        self.machine.variables.set_machine_var("lisy_hardware", "LISY80")
        self.mock_event("classic_subway_arrival_unconfirmed")
        self.machine.modes["classic_targets"].crater_index = 4
        self.hit_and_release_switch("s_ramp_4_4")
        self.advance_time_and_run(7)
        self.assertEventCalled("classic_subway_arrival_unconfirmed", 1)
        self.assertEqual(self.machine.game.player.classic_locks, 0)

    def test_crater_lights_accumulate_and_any_lit_crater_qualifies(self):
        self.start_classic(1)
        targets = self.machine.modes["classic_targets"]
        subway = self.machine.modes["classic_subway"]
        self.mock_event("classic_lock_qualified")
        calls = 0

        for index, lit in ((4, {4}), (3, {3, 4}), (2, {2, 3, 4}),
                           (1, {1, 2, 3, 4}), (0, set()), (4, {4})):
            targets.crater_index = index
            targets._show_lamps()
            for crater in range(1, 5):
                self.assertLightColor(f"l_xxx_{28 - crater}",
                                      "white" if crater in lit else "black")
                subway._last_hits.clear()
                subway._crater_hit(subway.CRATERS[crater - 1], crater)
                self.advance_time_and_run(.001)
                calls += crater in lit
                self.assertEventCalled("classic_lock_qualified", calls)

        targets.crater_index = 4
        for expected in (3, 2, 1, 0, 4):
            targets._advance_craters()
            self.assertEqual(targets.crater_index, expected)

    def test_freeze_holds_the_full_crater_pattern(self):
        self.start_classic(1)
        targets = self.machine.modes["classic_targets"]
        targets.crater_index = 2
        targets._show_lamps()
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(1)
        for crater in range(1, 5):
            self.assertLightColor(f"l_xxx_{28 - crater}",
                                  "white" if crater >= 2 else "black")
        self.advance_time_and_run(1.1)
        self.assertEqual(targets.crater_index, 1)

    def test_two_multiballs_on_same_ball(self):
        self.start_classic(1)
        self.mock_event("multiball_classic_subway_started")
        lock = self.machine.ball_devices["bd_classic_subway_lock"]

        for starts in (1, 2):
            for count in (1, 2):
                self.capture()
                self.assertEqual(lock.available_balls, count)
                self.assertEqual(self.machine.game.player.classic_locks, count)
                self.assertBallsInPlay(1)
            self.capture()
            self.advance_time_and_run(10)
            self.assertEventCalled("multiball_classic_subway_started", starts)
            self.assertEqual(lock.balls, 0)
            self.assertBallsInPlay(3)
            self.assertEqual(self.machine.playfield.balls, 3)
            self.assertEqual(self.machine.game.player.classic_multiball, 1)

            for remaining in (2, 1):
                self.drain_one_ball()
                self.advance_time_and_run(2)
                self.assertBallsInPlay(remaining)
            self.assertEqual(self.machine.game.player.classic_multiball, 0)

    def test_partial_physical_lock_is_visible_to_next_player_and_empties_on_tilt(self):
        self.start_classic(2)
        self.capture()
        self.drain_one_ball()
        self.advance_time_and_run(10)
        self.assertPlayerNumber(2)
        self.assertEqual(self.machine.game.player.classic_locks, 1)
        self.hit_and_release_switch("s_10_points_15")
        self.hit_switch_and_run("s_tilt_46", 4)
        self.assertEqual(self.machine.ball_devices["bd_classic_subway_lock"].balls, 0)
        self.assertEqual(self.machine.game.player.classic_locks, 0)
        self.assertEqual(self.machine.playfield.balls, 2)
        self.drain_one_ball()
        self.advance_time_and_run(2)
        self.drain_one_ball()
        self.advance_time_and_run(6)
        self.assertPlayerNumber(1)
        self.assertBallNumber(2)
        self.assertEqual(self.machine.game.player.classic_locks, 0)
