"""Set up the confirmed roster before MPF starts the first turn."""

from functools import partial

from mpf.modes.game.code.game import Game


class VolcanoGame(Game):
    """Use MPF's normal player addition for every player selected in attract."""

    def mode_start(self, **kwargs):
        self.roster_queue = None
        super().mode_start(**kwargs)

    async def _start_game(self):
        self.add_mode_event_handler("game_starting", self._start_roster)
        self.add_mode_event_handler("player_added", self._roster_player_added)
        await super()._start_game()

    def _start_roster(self, queue, **kwargs):
        queue.wait()
        self.roster_queue = queue
        self.request_player_add()

    def _roster_player_added(self, **kwargs):
        if self.roster_queue is None:
            return
        if self.num_players < self.max_players:
            self.request_player_add()
        else:
            self._release_roster_queue()

    def _player_add_request_complete(self, ev_result=True, **kwargs):
        if ev_result is False and self.roster_queue is not None:
            variables = self.machine.variables
            selection = (variables.get_machine_var("session_game"), self.max_players)
            self.stop(callback=partial(self.machine.modes["attract"].start, retry_selection=selection))
            return False
        return super()._player_add_request_complete(ev_result, **kwargs)

    def _release_roster_queue(self):
        if self.roster_queue is not None:
            self.roster_queue.clear()
            self.roster_queue = None

    def mode_stop(self, **kwargs):
        self._release_roster_queue()
        super().mode_stop(**kwargs)
