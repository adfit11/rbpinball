from mpf.core.custom_code import CustomCode


class BonusCounter(CustomCode):

    def on_load(self):
        self._delay = 150
        self._countdowntype = 1
        self.info_log("BonusCountdown custom code started successfully.")
        self.machine.events.add_handler('bonus_start', self._start_bonus_countdown)
        self.machine.events.add_handler('collect_seismic', self._start_seismic_countdown)
        self.machine.events.add_handler('bonus_countdown_decrement', self._decrement_bonus, 1)
        self.machine.events.add_handler('seismic_countdown_decrement', self._decrement_bonus, 1)
        self.machine.events.add_handler('flipper_cancel', self._speed_up_bonus)
        self.machine.events.add_handler('ball_ended', self._reset_state)

    def _reset_state(self, **kwargs):
        self._delay = 150
        self._countdowntype = 1

    def _start_bonus_countdown(self, **kwargs):
        del kwargs
        if self.machine.game.player.bonus_val > 0:
            self.machine.game.player.bonus_val -= 1
            if self._countdowntype == 1:
                self.machine.events.post('bonus_countdown_decrement')
            else:
                self.machine.events.post('seismic_countdown_decrement')
        else:
            self.machine.events.post('finish_up_bonus')

    def _start_seismic_countdown(self, **kwargs):
        del kwargs
        self._countdowntype = 2
        self._start_bonus_countdown()

    def _decrement_bonus(self, **kwargs):
        self.machine.delay.add(ms=self._delay, callback=self._do_decrement)
        self.machine.delay.add(ms=self._delay, callback=self._do_decrement_audio)

    def _do_decrement_audio(self, **kwargs):
        self.machine.events.post('bonus_countdown_decrement_audio')

    def _speed_up_bonus(self, **kwargs):
        self._delay = 10

    def _do_decrement(self):
        if self.machine.game.player.bonus_val > 0:
            self.machine.game.player.bonus_val -= 1
            if self._countdowntype == 1:
                self.machine.events.post('bonus_countdown_decrement')
            else:
                self.machine.events.post('seismic_countdown_decrement')
        else:
            if self._countdowntype == 1:
                self.machine.events.post('finish_up_bonus')
            else:
                self.machine.events.post('finish_up_seismic')
