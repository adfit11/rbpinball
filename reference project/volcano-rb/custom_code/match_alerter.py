from mpf.core.custom_code import CustomCode


class MatchAlerter(CustomCode):

    def on_load(self):
        self._matches = 0
        self.info_log("MatchAlerter custom code started successfully.")
        self.machine.events.add_handler('has_match', self._do_match_alerts)

    def _do_match_alerts(self, **kwargs):
        self._matches = 0
        number = kwargs.get('winner_number')
        player_count = self.machine.game.num_players

        for x in range(player_count):
            if number == kwargs.get('match_number' + str(x)):
                self._matches += 1

        if self._matches > 0:
            self.machine.delay.add(ms=1, callback=self._do_next_alert)
        else:
            self.machine.events.post('match_alerts_done')

    def _do_next_alert(self, **kwargs):
        self.machine.events.post('match_alert')
        self._matches -= 1
        if self._matches > 0:
            self.machine.delay.add(ms=500, callback=self._do_next_alert)
        else:
            self.machine.events.post('match_alerts_done')
