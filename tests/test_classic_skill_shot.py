"""Verify Classic's skill shot motor with MPF's smart virtual devices."""

from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class TestClassicSkillShot(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def start_game(self, game="classic"):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.hit_and_release_switch("s_flipper_left" if game == "classic" else "s_flipper_right")
        self.hit_and_release_switch("s_start_47")
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.assertEqual(self.machine.variables.get_machine_var("session_game"), game)

    def motor_on(self):
        return self.machine.digital_outputs["skill_motor"].hw_driver.current_brightness == 1

    def capture(self):
        targets = self.machine.modes["classic_targets"]
        if targets.crater_index == 0:
            self.advance_time_and_run(.3)
        self.hit_and_release_switch(targets.CRATER_SWITCHES[targets.crater_index - 1])
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(3.2)

    def test_serve_runs_motor_until_first_playfield_hit(self):
        self.start_game()
        self.assertModeRunning("classic_skill_shot")
        self.assertTrue(self.motor_on())
        for switch in ("s_start_47", "s_flipper_left", "s_test_switch_7"):
            self.hit_and_release_switch(switch)
            self.advance_time_and_run(.1)
            self.assertTrue(self.motor_on())
        self.hit_and_release_switch("s_10_points_15")
        self.advance_time_and_run(.1)
        self.assertFalse(self.motor_on())

    def serve(self):
        self.machine.modes["classic_skill_shot"]._serve(target=self.machine.playfield)

    def test_motor_starts_one_second_after_serve(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        self.serve()
        self.advance_time_and_run(.9)
        self.assertFalse(self.motor_on())
        self.advance_time_and_run(.2)
        self.assertTrue(self.motor_on())

    def test_release_vibration_does_not_cancel_motor_start(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        self.serve()
        self.hit_and_release_switch("s_spinner_44")
        self.advance_time_and_run(1.1)
        self.assertTrue(self.motor_on())
        self.hit_and_release_switch("s_spinner_44")
        self.advance_time_and_run(.1)
        self.assertFalse(self.motor_on())

    def test_green_before_motor_starts_cancels_it(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        self.serve()
        self.advance_time_and_run(.5)
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(2)
        self.assertFalse(self.motor_on())

    def test_green_stops_motor_and_freezes_lamps(self):
        self.start_game()
        targets = self.machine.modes["classic_targets"]
        self.hit_and_release_switch("s_green_button_right_56")
        frozen = targets.drop_index, targets.crater_index
        self.advance_time_and_run(1)
        self.assertFalse(self.motor_on())
        self.assertEqual(frozen, (targets.drop_index, targets.crater_index))

    def test_timeout_stops_motor(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        self.serve()
        self.advance_time_and_run(30.9)
        self.assertTrue(self.motor_on())
        self.advance_time_and_run(.2)
        self.assertFalse(self.motor_on())

    def test_tilt_stops_motor_and_next_relay_enable_leaves_it_off(self):
        self.start_game()
        self.hit_switch_and_run("s_tilt_46", .1)
        self.assertFalse(self.motor_on())
        self.release_switch_and_run("s_tilt_46", .1)
        self.post_event("ball_started", .1)
        self.assertEqual(self.machine.digital_outputs["game_over_relay"].hw_driver.current_brightness, 1)
        self.assertFalse(self.motor_on())

    def test_ball_end_stops_motor_and_next_ball_runs_it(self):
        self.start_game()
        self.assertTrue(self.motor_on())
        self.drain_one_ball()
        self.advance_time_and_run(.8)
        self.assertBallNumber(2)
        self.assertFalse(self.motor_on())
        self.advance_time_and_run(2)
        self.assertTrue(self.motor_on())

    def test_lock_replacements_run_motor_and_multiball_release_does_not(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        for _ in range(2):
            self.capture()
            self.advance_time_and_run(1)
            self.assertTrue(self.motor_on())
            self.hit_and_release_switch("s_rollunder_25")
            self.advance_time_and_run(.1)
            self.assertFalse(self.motor_on())
        self.mock_event("multiball_classic_subway_started")
        self.capture()
        self.advance_time_and_run(10)
        self.assertEventCalled("multiball_classic_subway_started", 1)
        self.assertBallsInPlay(3)
        self.assertFalse(self.motor_on())

    def test_ball_saver_kick_leaves_motor_off(self):
        self.start_game()
        self.hit_and_release_switch("s_10_points_15")
        self.post_event("classic_ball_save_qualified", .1)
        self.hit_and_release_switch("s_outlane_left_6")
        self.advance_time_and_run(2)
        self.assertEqual(self.machine.game.player.classic_ball_save_ready, 0)
        self.assertFalse(self.motor_on())

    def test_modern_ball_start_leaves_motor_off(self):
        self.start_game("modern")
        self.assertModeNotRunning("classic_skill_shot")
        self.assertFalse(self.motor_on())

    def test_top_drop_rotation_is_unchanged(self):
        self.start_game()
        targets = self.machine.modes["classic_targets"]
        seen = []
        for _ in range(6):
            seen.append(targets.drop_index)
            self.advance_time_and_run(.2)
        self.assertEqual([(seen[0] + step - 1) % 5 + 1 for step in range(6)], seen)

    def assert_lit_drop_award(self, freeze):
        self.start_game()
        targets = self.machine.modes["classic_targets"]
        if freeze:
            self.hit_and_release_switch("s_green_button_right_56")
            self.advance_time_and_run(1)
        player = self.machine.game.player
        self.hit_switch_and_run(targets.DROP_SWITCHES["top_bank"][targets.drop_index - 1], .1)
        self.assertFalse(self.motor_on())
        self.assertEqual(player.score, 5000)
        self.assertEqual(player.classic_bonus_multiplier, 2)
        self.assertEqual(player.classic_ball_save_ready, 1)
        for lamp in ("l_xxx_04", "l_xxx_05", "l_xxx_06"):
            self.assertLightColor(lamp, "white")

    def test_frozen_lit_drop_awards_ball_save(self):
        self.assert_lit_drop_award(freeze=True)

    def test_unfrozen_lit_drop_awards_ball_save(self):
        self.assert_lit_drop_award(freeze=False)

    def test_gap_of_down_target_scores_nothing(self):
        self.start_game()
        targets = self.machine.modes["classic_targets"]
        self.hit_switch_and_run("s_top_drop_2_12", .1)
        self.drain_one_ball()
        self.advance_time_and_run(3)
        player = self.machine.game.player
        score = player.score
        targets.drop_index = 1
        self.hit_and_release_switch("s_green_button_right_56")
        targets.drop_index = 2
        targets._show_lamps()
        self.advance_time_and_run(1)
        self.assertEqual(player.score, score)
        self.assertEqual(player.classic_ball_save_ready, 0)
