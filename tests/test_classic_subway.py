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
        switch = targets.CRATER_SWITCHES[targets.crater_index - 1]
        self.assertNotEqual(targets.crater_index, 0)
        self.hit_and_release_switch(switch)
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(.8)

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
