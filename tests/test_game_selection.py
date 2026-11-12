"""Exercise the cabinet selection flow with virtual MPF switches."""

from pathlib import Path
from unittest.mock import patch

from mpf.tests.MpfGameTestCase import MpfGameTestCase


class TestGameSelection(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def assert_selection(self, stage, game, count):
        variables = self.machine.variables
        self.assertEqual(variables.get_machine_var("selection_stage"), stage)
        self.assertEqual(variables.get_machine_var("selection_game"), game)
        self.assertEqual(variables.get_machine_var("selection_players"), count)

    def choose_game_and_count(self, game, count):
        switch = "s_flipper_left" if game == "classic" else "s_flipper_right"
        self.hit_and_release_switch(switch)
        self.hit_and_release_switch("s_start_47")
        for _ in range(count - 1):
            self.hit_and_release_switch("s_flipper_right")

    def test_select_game_and_player_count(self):
        self.assert_selection("game", "modern", 1)
        self.hit_and_release_switch("s_flipper_left")
        self.assert_selection("game", "classic", 1)
        self.hit_and_release_switch("s_flipper_right")
        self.assert_selection("game", "modern", 1)
        self.hit_and_release_switch("s_flipper_left")

        self.mock_event("request_to_start_game")
        self.hit_and_release_switch("s_start_47")
        self.assertEventNotCalled("request_to_start_game")
        self.assertGameIsNotRunning()
        self.assertModeRunning("attract_lights")
        self.assert_selection("players", "classic", 1)

        self.hit_and_release_switch("s_flipper_left")
        self.assert_selection("players", "classic", 1)
        for count in (2, 3, 4, 4):
            self.hit_and_release_switch("s_flipper_right")
            self.assert_selection("players", "classic", count)
        self.hit_and_release_switch("s_flipper_left")
        self.assert_selection("players", "classic", 3)

    def test_right_green_button_cycles_games_and_roster(self):
        green_button = "s_green_button_right_56"
        self.hit_switch_and_run("s_trough_1_40", 1)
        for game in ("classic", "modern", "classic"):
            self.hit_and_release_switch(green_button)
            self.assert_selection("game", game, 1)

        self.hit_and_release_switch("s_start_47")
        self.assert_selection("players", "classic", 1)
        for count in (2, 3, 4, 1, 2):
            self.hit_and_release_switch(green_button)
            self.assert_selection("players", "classic", count)

        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.assertModeRunning("classic")
        self.assertPlayerCount(2)
        self.hit_and_release_switch(green_button)
        self.assertPlayerCount(2)
        self.assertEqual(self.machine.variables.get_machine_var("session_game"), "classic")

    def test_cabinet_selector_ignores_queued_presses_at_attract_start(self):
        self.machine.variables.set_machine_var("lisy_hardware", "LISY80")
        self.stop_mode("attract")
        self.machine.modes["attract"].start()
        self.advance_time_and_run(.05)

        self.hit_and_release_switch("s_green_button_right_56")
        self.hit_and_release_switch("s_start_47")
        self.assert_selection("game", "modern", 1)

        self.advance_time_and_run(.3)
        self.hit_switch_and_run("s_green_button_right_56", .12)
        self.release_switch_and_run("s_green_button_right_56", .12)
        self.hit_and_release_switch("s_start_47")
        self.assert_selection("players", "classic", 1)

    def test_cabinet_green_button_counts_one_press_through_contact_bounce(self):
        self.machine.variables.set_machine_var("lisy_hardware", "LISY80")
        self.stop_mode("attract")
        self.start_mode("attract")
        self.advance_time_and_run(.3)

        green_button = "s_green_button_right_56"
        self.hit_switch_and_run(green_button, .005)
        self.release_switch_and_run(green_button, .078)
        self.hit_switch_and_run(green_button, .046)
        self.release_switch_and_run(green_button, .011)
        self.hit_switch_and_run(green_button, .26)
        self.release_switch_and_run(green_button, .012)
        self.hit_switch_and_run(green_button, .001)
        self.release_switch_and_run(green_button, .12)
        self.assert_selection("game", "classic", 1)

        self.hit_and_release_switch("s_start_47")
        self.hit_switch_and_run(green_button, .012)
        self.release_switch_and_run(green_button, .012)
        self.hit_switch_and_run(green_button, .012)
        self.release_switch_and_run(green_button, .012)
        self.hit_switch_and_run(green_button, .066)
        self.release_switch_and_run(green_button, .012)
        self.hit_switch_and_run(green_button, .034)
        self.release_switch_and_run(green_button, .12)
        self.assert_selection("players", "classic", 2)

        self.hit_switch_and_run(green_button, .15)
        self.release_switch_and_run(green_button, .012)
        self.hit_switch_and_run(green_button, .15)
        self.release_switch_and_run(green_button, .12)
        self.assert_selection("players", "classic", 3)

    def test_denied_start_preserves_selection_and_can_retry(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_and_release_switch("s_flipper_left")
        self.hit_and_release_switch("s_start_47")
        self.hit_and_release_switch("s_flipper_right")
        self.mock_event("game_started")

        denial = self.machine.events.add_handler("request_to_start_game", lambda **kwargs: False)
        self.hit_and_release_switch("s_start_47")
        self.assertGameIsNotRunning()
        self.assert_selection("players", "classic", 2)
        self.assertEqual(self.machine.variables.get_machine_var("session_game"), "")
        self.assertEventNotCalled("game_started")

        self.machine.events.remove_handler_by_key(denial)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.assertGameIsRunning()
        self.assertEventCalled("game_started", 1)
        self.assertEqual(self.machine.variables.get_machine_var("session_game"), "classic")
        self.assertEqual(self.machine.variables.get_machine_var("session_players"), 2)

        self.machine.game.end_game()
        self.advance_time_and_run(1)
        self.assertGameIsNotRunning()
        self.assert_selection("game", "modern", 1)
        self.assertEqual(self.machine.variables.get_machine_var("session_game"), "")

    def test_roster_and_ball_limits(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.mock_event("ball_started")

        for game in ("classic", "modern"):
            for count in range(1, 5):
                with self.subTest(game=game, count=count):
                    self.choose_game_and_count(game, count)
                    previous_starts = self._events.get("ball_started", 0)
                    self.hit_and_release_switch("s_start_47")
                    self.advance_time_and_run(1)
                    self.assertGameIsRunning()
                    self.assertPlayerCount(count)
                    self.assertPlayerNumber(1)
                    self.assertBallNumber(1)
                    self.assertBallsInPlay(1)
                    self.assertEventCalled("ball_started", previous_starts + 1)
                    self.assertEqual(self.machine.game.balls_per_game, 3)

                    self.hit_and_release_switch("s_start_47")
                    self.assertPlayerCount(count)
                    self.release_switch_and_run("s_trough_1_40", 2)
                    self.hit_and_release_switch("s_10_points_15")
                    self.advance_time_and_run(1)
                    self.machine.game.end_game()
                    self.advance_time_and_run(1)
                    self.hit_switch_and_run("s_trough_3_20", 1)
                    self.release_switch_and_run("s_trough_3_20", .1)
                    self.hit_switch_and_run("s_trough_1_40", 1)
                    self.advance_time_and_run(3)
                    self.assertGameIsNotRunning()

    def test_denied_roster_does_not_start_a_partial_game(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 2)
        self.mock_event("game_started")
        self.mock_event("ball_started")

        def allow_first_player(**kwargs):
            return self.machine.game.num_players == 0

        denial = self.machine.events.add_handler("player_add_request", allow_first_player)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.assertGameIsNotRunning()
        self.assertEventNotCalled("game_started")
        self.assertEventNotCalled("ball_started")
        self.assert_selection("players", "classic", 2)

        self.machine.events.remove_handler_by_key(denial)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.assertPlayerCount(2)
        self.assertEventCalled("ball_started", 1)

    def test_classic_three_ball_rotation(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.mock_event("balldevice_bd_trough_ejecting_ball")
        served = 0

        for count in (1, 4):
            with self.subTest(players=count):
                self.choose_game_and_count("classic", count)
                self.hit_and_release_switch("s_start_47")
                self.advance_time_and_run(1)
                self.assertPlayerCount(count)
                for ball in range(1, 4):
                    for player in range(1, count + 1):
                        self.assertModeRunning("classic")
                        self.assertModeNotRunning("base")
                        self.assertPlayerNumber(player)
                        self.assertBallNumber(ball)
                        self.assertBallsInPlay(1)
                        self.release_switch_and_run("s_trough_1_40", 2)
                        self.hit_and_release_switch("s_10_points_15")
                        served += 1
                        self.assertEventCalled("balldevice_bd_trough_ejecting_ball", served)

                        self.hit_switch_and_run("s_trough_3_20", 1)
                        self.release_switch_and_run("s_trough_3_20", .1)
                        final_turn = ball == 3 and player == count
                        self.hit_switch_and_run("s_trough_1_40", 1 if final_turn else .1)
                        if not final_turn:
                            self.release_switch_and_run("s_trough_1_40", .1)
                        self.advance_time_and_run(3)

                self.assertGameIsNotRunning()
                self.assertModeRunning("attract")
                self.assertModeNotRunning("classic")
                self.assertEventCalled("balldevice_bd_trough_ejecting_ball", served)

    def test_classic_scores_and_counts_bonus_for_draining_player(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 2)
        self.hit_and_release_switch("s_start_47")
        self.release_switch_and_run("s_trough_1_40", 2)
        player = self.machine.game.player

        self.hit_and_release_switch("s_top_bumpers_35")
        self.hit_and_release_switch("s_bottom_bumpers_13")
        self.hit_and_release_switch("s_rollunder_25")
        self.assertEqual(player.score, 4100)
        self.assertEqual(player.classic_bonus_units, 2)
        player.classic_bonus_multiplier = 2

        self.hit_switch_and_run("s_trough_3_20", .1)
        self.assertPlayerNumber(1)
        self.advance_time_and_run(1)
        self.assertEqual(player.score, 8100)
        self.assertPlayerNumber(2)
        self.assertEqual(self.machine.game.player.score, 0)
        self.assertEqual(player.classic_counting_bonus, 0)

    def test_classic_target_freeze_progression_and_multiplier(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 1)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1.2)
        self.hit_and_release_switch("s_green_button_right_56")
        self.release_switch_and_run("s_trough_1_40", 2)
        self.assertLightColor("l_xxx_19", "white")
        self.assertLightColor("l_xxx_24", "white")

        player = self.machine.game.player
        self.hit_switch_and_run("s_top_drop_2_12", .1)
        self.assertEqual(player.score, 100)
        self.hit_switch_and_run("s_top_drop_1_2", .1)
        self.assertEqual(player.score, 5100)
        self.assertEqual(player.classic_bonus_multiplier, 2)
        self.advance_time_and_run(1)
        self.assertLightColor("l_xxx_19", "black")

        for switch in ("s_top_drop_3_22", "s_top_drop_4_32", "s_top_drop_5_42"):
            self.hit_switch_and_run(switch, .01)
        coil = self.machine.coils["c_top_drops"]
        with patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            self.advance_time_and_run(.6)
            pulse.assert_called_once()

        self.hit_and_release_switch("s_ramp_4_4")
        self.assertEqual(player.classic_playfield_multiplier, 4)
        self.assertLightColor("l_xxx_32", "white")
        previous = player.score
        self.hit_and_release_switch("s_rollunder_25")
        self.assertEqual(player.score, previous + 12000)
        self.advance_time_and_run(7)
        self.assertEqual(player.classic_playfield_multiplier, 1)
        self.assertLightColor("l_xxx_32", "black")

    def test_classic_seismic_counts_before_releasing_saucer(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 1)
        self.hit_and_release_switch("s_start_47")
        self.release_switch_and_run("s_trough_1_40", 2)
        self.hit_and_release_switch("s_10_points_15")
        player = self.machine.game.player
        player.classic_bonus_units = 19
        player.classic_bonus_multiplier = 2
        self.mock_event("classic_release_saucer")

        self.hit_switch_and_run("s_hole_kicker_top_23", .7)
        self.assertEventNotCalled("classic_release_saucer")
        self.assertEqual(player.classic_counting_bonus, 1)
        self.advance_time_and_run(3)
        self.assertEventCalled("classic_release_saucer", 1)
        self.assertEqual(player.score, 41010)
        self.assertEqual(player.classic_bonus_units, 1)
        self.assertEqual(player.classic_counting_bonus, 0)

    def test_classic_firepit_awards_and_serves_same_player_extra_ball(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 2)
        self.hit_and_release_switch("s_start_47")
        self.release_switch_and_run("s_trough_1_40", 2)
        self.hit_and_release_switch("s_10_points_15")
        player = self.machine.game.player
        for switches in self.machine.modes["classic_targets"].DROP_SWITCHES.values():
            for switch in switches:
                self.hit_switch_and_run(switch, .01)
        self.assertEqual(player.classic_extra_ball_ready, 1)

        self.hit_and_release_switch("s_outlane_right_5")
        self.assertEqual(player.classic_outlane_extra_ready, 1)
        self.hit_and_release_switch("s_rollunder_25")
        self.assertEqual(player.classic_outlane_extra_ready, 0)
        self.hit_switch_and_run("s_side_kicker_left_43", 1.5)
        self.assertEqual(player.extra_balls, 1)
        self.release_switch_and_run("s_side_kicker_left_43", .1)
        self.hit_and_release_switch("s_10_points_15")
        self.mock_event("ball_started")
        self.hit_switch_and_run("s_trough_3_20", 2)
        self.assertEventCalledWith("ball_started", player=1, ball=1, balls_remaining=2, is_extra_ball=True)
        self.assertPlayerNumber(1)

    def test_classic_right_outlane_qualifies_firepit_extra_ball(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 1)
        self.hit_and_release_switch("s_start_47")
        self.release_switch_and_run("s_trough_1_40", 2)
        self.hit_and_release_switch("s_outlane_right_5")
        self.hit_switch_and_run("s_side_kicker_left_43", .7)
        self.assertEqual(self.machine.game.player.extra_balls, 1)
        self.assertEqual(self.machine.game.player.classic_outlane_extra_ready, 0)

    def test_classic_gate_and_ball_saver_clear_on_use_and_tilt(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.choose_game_and_count("classic", 1)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1.2)
        self.hit_and_release_switch("s_green_button_right_56")
        self.release_switch_and_run("s_trough_1_40", 2)
        player = self.machine.game.player
        gate = self.machine.digital_outputs["classic_return_gate"].hw_driver
        saver = self.machine.coils["c_classic_ball_saver"]

        with patch.object(saver, "pulse", wraps=saver.pulse) as pulse:
            self.hit_switch_and_run("s_top_drop_1_2", .1)
            pulse.assert_called_once()
        self.assertEqual(player.classic_ball_save_ready, 1)
        self.hit_and_release_switch("s_outlane_left_6")
        self.assertEqual(player.classic_ball_save_ready, 0)

        for switch in self.machine.modes["classic_targets"].DROP_SWITCHES["top_bank"][1:]:
            self.hit_switch_and_run(switch, .01)
        self.assertEqual(player.classic_gate_ready, 1)
        self.hit_and_release_switch("s_spot_target_36")
        self.assertEqual(gate.current_brightness, 1)
        self.hit_and_release_switch("s_outlane_right_5")
        self.assertEqual(gate.current_brightness, 0)
        self.assertEqual(player.classic_outlane_extra_ready, 0)

        self.post_event("classic_open_gate")
        self.post_event("classic_ball_save_qualified")
        self.hit_switch_and_run("s_tilt_46", .1)
        self.assertEqual(gate.current_brightness, 0)
        self.assertEqual(player.classic_gate_open, 0)
        self.assertEqual(player.classic_ball_save_ready, 0)
