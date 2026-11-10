"""Cabinet selection before the built-in MPF game starts."""

from mpf.modes.attract.code.attract import Attract


class VolcanoAttract(Attract):
    """Use the cabinet buttons to select a game, then its player count."""

    def mode_start(self, retry_selection=None, **kwargs):
        variables = self.machine.variables
        self.start_pending = False
        variables.set_machine_var("session_game", "")
        variables.set_machine_var("session_players", 0)
        game, count = retry_selection or ("modern", 1)
        variables.set_machine_var("selection_game", game)
        variables.set_machine_var("selection_players", count)
        variables.set_machine_var("selection_stage", "players" if retry_selection else "game")
        self.add_mode_event_handler("s_flipper_left_active", self._select_left)
        self.add_mode_event_handler("s_flipper_right_active", self._select_right)
        super().mode_start(**kwargs)

    def _select_left(self, **kwargs):
        self._move_selection("classic", -1)

    def _select_right(self, **kwargs):
        self._move_selection("modern", 1)

    def _move_selection(self, game, player_delta):
        if self.start_pending:
            return
        variables = self.machine.variables
        if variables.get_machine_var("selection_stage") == "game":
            variables.set_machine_var("selection_game", game)
        else:
            count = variables.get_machine_var("selection_players")
            variables.set_machine_var("selection_players", min(4, max(1, count + player_delta)))

    def start_button_released(self, **kwargs):
        if self.start_pending:
            return
        variables = self.machine.variables
        if variables.get_machine_var("selection_stage") == "game":
            variables.set_machine_var("selection_players", 1)
            variables.set_machine_var("selection_stage", "players")
            return

        self.start_pending = True
        super().start_button_released(**kwargs)

    def result_of_start_request(self, ev_result=True):
        if not self.active:
            return
        if ev_result is False:
            self.start_pending = False
        else:
            variables = self.machine.variables
            variables.set_machine_var("session_game", variables.get_machine_var("selection_game"))
            variables.set_machine_var("session_players", variables.get_machine_var("selection_players"))
        super().result_of_start_request(ev_result)
