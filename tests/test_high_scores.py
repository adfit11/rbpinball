"""High-score entry for both games, and the idle Hall of Fame showcase in attract."""

from pathlib import Path

from mpf.tests.MpfGameTestCase import MpfGameTestCase

GREEN = "s_green_button_right_56"


class CabinetTestCase(MpfGameTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def play(self, game, score):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_switch_and_run("s_trough_2_30", 1)
        self.hit_and_release_switch("s_flipper_left" if game == "classic" else "s_flipper_right")
        self.hit_and_release_switch("s_start_47")
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        if game == "modern":
            self.hit_and_release_switch("s_start_47")
            self.advance_time_and_run(2)
        self.assertGameIsRunning()
        self.machine.game.player.score = score
        self.machine.game.end_game()
        self.advance_time_and_run(10)
        self.assertModeRunning(game + "_high_score")

    def inputs(self):
        actions = []
        self.machine.events.add_handler("text_input", lambda action, **kwargs: actions.append(action))
        return actions

    def enter(self, initials):
        self.machine.events.post("text_input_high_score_complete", text=initials)
        self.advance_time_and_run(5)


class TestHighScores(CabinetTestCase):
    def test_boards_start_from_their_own_defaults(self):
        variables = self.machine.variables
        self.assertEqual(variables.get_machine_var("classic_score1_label"), "GRAND CHAMPION")
        self.assertEqual(variables.get_machine_var("classic_score1_name"), "ADF")
        self.assertEqual(variables.get_machine_var("modern_score1_label"), "KING OF THE JOINT")
        self.assertEqual(variables.get_machine_var("modern_score4_value"), 5000000)

    def test_classic_green_tap_cycles_and_hold_chooses(self):
        self.play("classic", 999999)
        actions = self.inputs()
        self.hit_and_release_switch(GREEN)
        self.hit_switch_and_run(GREEN, 2.1)
        self.release_switch_and_run(GREEN, .1)
        self.hit_and_release_switch("s_flipper_left")
        self.hit_and_release_switch("s_flipper_right")
        self.assertEqual(actions, ["right", "select", "left", "right"])
        self.enter("ZZZ")
        self.assertModeNotRunning("classic_high_score")
        variables = self.machine.variables
        self.assertEqual(variables.get_machine_var("classic_score1_name"), "ZZZ")
        self.assertGreaterEqual(variables.get_machine_var("classic_score1_value"), 999999)
        self.assertEqual(variables.get_machine_var("classic_score2_name"), "ADF")
        self.assertEqual(variables.get_machine_var("modern_score1_name"), "LJ")
        self.assertModeRunning("attract")

    def test_modern_entry_keeps_its_own_board(self):
        self.play("modern", 12000000)
        actions = self.inputs()
        self.hit_and_release_switch(GREEN)
        self.hit_switch_and_run(GREEN, 2.1)
        self.release_switch_and_run(GREEN, .1)
        self.assertEqual(actions, ["right", "select"])
        self.enter("BB")
        variables = self.machine.variables
        self.assertEqual(variables.get_machine_var("modern_score3_name"), "BB")
        self.assertEqual(variables.get_machine_var("modern_score4_name"), "BJT")
        self.assertEqual(variables.get_machine_var("classic_score1_name"), "ADF")

    def test_modern_remapped_select_switch_chooses(self):
        self.machine.variables.set_machine_var("modern_select_switch", "s_flipper_left")
        self.play("modern", 12000000)
        actions = self.inputs()
        self.hit_switch_and_run(GREEN, 2.1)
        self.release_switch_and_run(GREEN, .1)
        self.assertEqual(actions, ["right"])

    def test_low_score_skips_entry(self):
        self.hit_switch_and_run("s_trough_1_40", 1)
        self.hit_and_release_switch("s_flipper_left")
        self.hit_and_release_switch("s_start_47")
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1)
        self.machine.game.player.score = 10
        self.machine.game.end_game()
        self.advance_time_and_run(1)
        self.assertModeNotRunning("classic_high_score")
        self.assertModeRunning("attract")


class TestAttractShowcase(CabinetTestCase):
    def test_idle_attract_shows_the_boards_and_a_press_returns_to_selection(self):
        variables = self.machine.variables
        self.hit_and_release_switch(GREEN)
        self.assertEqual(variables.get_machine_var("selection_game"), "classic")
        self.advance_time_and_run(29)
        self.assertFalse(variables.get_machine_var("attract_showcase"))
        self.advance_time_and_run(2)
        self.assertTrue(variables.get_machine_var("attract_showcase"))
        self.hit_and_release_switch(GREEN)
        self.assertFalse(variables.get_machine_var("attract_showcase"))
        self.assertEqual(variables.get_machine_var("selection_game"), "classic")
        self.hit_and_release_switch(GREEN)
        self.assertEqual(variables.get_machine_var("selection_game"), "modern")
