"""Exercise the game-over relay against the real MPF machine config."""
from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class TestGameRelay(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return 'config.yaml'

    def setUp(self):
        self.machine_config_patches['virtual_platform_start_active_switches'] = []
        super().setUp()

    def test_game_and_tilt(self):
        relay = self.machine.digital_outputs['game_over_relay'].hw_driver
        self.assertEqual(relay.current_brightness, 0)
        self.assertModeRunning('attract_lights')
        self.advance_time_and_run(.4)
        self.assertLightColor('l_xxx_24', 'on')

        self.hit_switch_and_run('s_trough_1_40', 1)
        self.hit_and_release_switch('s_start_47')
        self.start_game(start_switch='s_start_47')
        self.assertModeNotRunning('attract_lights')
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
        self.hit_and_release_switch('s_start_47')
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

    def test_trough_counts_each_arrival_once(self):
        trough = self.machine.ball_devices['bd_trough']
        entrance = 's_trough_1_40'
        self.assertEqual(trough.balls, 0)

        self.hit_switch_and_run(entrance, .012)
        self.release_switch_and_run(entrance, .024)
        self.hit_switch_and_run(entrance, .104)
        self.release_switch_and_run(entrance, .012)
        self.hit_switch_and_run(entrance, .012)
        self.release_switch_and_run(entrance, 1)
        self.assertEqual(trough.balls, 1)

        self.hit_switch_and_run(entrance, .001)
        self.release_switch_and_run(entrance, .024)
        self.hit_switch_and_run(entrance, .013)
        self.release_switch_and_run(entrance, 1)
        self.assertEqual(trough.balls, 2)

        self.hit_switch_and_run(entrance, .011)
        self.release_switch_and_run(entrance, .001)
        self.hit_switch_and_run(entrance, .011)
        self.release_switch_and_run(entrance, .013)
        self.hit_switch_and_run(entrance, .4)
        self.assertEqual(trough.balls, 2)
        self.advance_time_and_run(.6)
        self.assertEqual(trough.balls, 3)

    def test_cabinet_trough_does_not_count_serve_as_a_drain(self):
        self.machine.variables.set_machine_var('lisy_hardware', 'LISY80')
        entrance = 's_trough_1_40'
        self.hit_switch_and_run(entrance, 1)
        self.hit_and_release_switch('s_start_47')
        self.mock_event('ball_drain')
        self.mock_event('balldevice_bd_trough_ejecting_ball')
        self.hit_and_release_switch('s_start_47')
        self.advance_time_and_run(.04)

        self.release_switch_and_run(entrance, .012)
        self.hit_switch_and_run(entrance, 1)
        self.release_switch_and_run(entrance, .08)
        self.hit_switch_and_run(entrance, .6)
        self.release_switch_and_run(entrance, .6)
        self.assertEventNotCalled('ball_drain')
        self.assertEventCalled('balldevice_bd_trough_ejecting_ball', 1)
        self.assertBallNumber(1)
        self.assertEqual(self.machine.ball_devices['bd_trough'].balls, 2)

        self.hit_and_release_switch('s_return_left_16')
        self.mock_event('balldevice_bd_outhole_ball_eject_success')
        self.hit_switch_and_run('s_trough_3_20', 1)
        self.release_switch_and_run('s_trough_3_20', .1)
        self.hit_switch_and_run(entrance, 1)
        self.assertEventCalled('balldevice_bd_outhole_ball_eject_success', 1)
        self.assertBallNumber(2)

