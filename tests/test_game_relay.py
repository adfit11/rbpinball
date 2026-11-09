"""Exercise the game-over relay against the real MPF machine config."""
from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class TestGameRelay(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return 'config.yaml'

    def test_game_and_tilt(self):
        relay = self.machine.digital_outputs['game_over_relay'].hw_driver
        self.assertEqual(relay.current_brightness, 0)

        self.hit_switch_and_run('s_trough_1_40', 1)
        self.start_game(start_switch='s_start_47')
        self.advance_time_and_run(2)
        self.assertEqual(relay.current_brightness, 1)
        self.post_event('ball_will_end', 0.1)
        self.assertEqual(relay.current_brightness, 1)
        self.hit_switch_and_run('s_tilt_46', 0.1)
        self.assertEqual(relay.current_brightness, 0)
        self.release_switch_and_run('s_tilt_46', 0.1)
        self.post_event('ball_started', 0.1)
        self.assertEqual(relay.current_brightness, 1)
        self.post_event('game_will_end', 0.1)
        self.assertEqual(relay.current_brightness, 0)

    def test_three_ball_game(self):
        relay = self.machine.digital_outputs['game_over_relay'].hw_driver
        self.hit_switch_and_run('s_trough_1_40', 1)
        self.hit_switch_and_run('s_trough_2_30', 1)
        self.assertEqual(self.machine.ball_devices['bd_trough'].balls, 3)
        self.start_game(start_switch='s_start_47')
        for ball in range(1, 4):
            self.release_switch_and_run('s_trough_1_40', 2)
            self.hit_and_release_switch('s_return_left_16')
            self.advance_time_and_run(1)
            self.assertBallNumber(ball)
            self.assertEqual(relay.current_brightness, 1)
            self.hit_switch_and_run('s_trough_3_20', 1)
            self.release_switch_and_run('s_trough_3_20', .1)
            self.hit_switch_and_run('s_trough_1_40', 1 if ball == 3 else .1)
            if ball != 3:
                self.release_switch_and_run('s_trough_1_40', .1)
            self.advance_time_and_run(3)
        self.assertGameIsNotRunning()
        self.assertEqual(relay.current_brightness, 0)

