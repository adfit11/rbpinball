"""Classic's rotating targets, crater awards and timed lava multipliers."""

from mpf.core.mode import Mode


class ClassicTargets(Mode):
    DROP_SWITCHES = {
        "top_bank": ("s_top_drop_1_2", "s_top_drop_2_12", "s_top_drop_3_22",
                     "s_top_drop_4_32", "s_top_drop_5_42"),
        "right_bank": ("s_right_drop_1_1", "s_right_drop_2_11", "s_right_drop_3_21",
                       "s_right_drop_4_31", "s_right_drop_5_41"),
    }
    CRATER_SWITCHES = ("s_ramp_1_34", "s_ramp_2_24", "s_ramp_3_14", "s_ramp_4_4")
    SCORING_EVENTS = (
        "classic_top_bumper_hit", "classic_bottom_bumper_hit", "classic_standing_hit",
        "classic_rollunder_hit", "classic_kicking_target_hit", "classic_left_return_hit",
        "classic_left_outlane_hit", "classic_spot_hit", "s_outlane_right_5_active",
        "ball_hold_classic_saucer_held_ball", "ball_hold_classic_firepit_held_ball",
    )
    LAMPS = (*range(19, 33), 46)

    def mode_start(self, **kwargs):
        self.drop_index = 1
        self.crater_index = 4
        self.ball_active = False
        self.can_freeze = True
        self.completed_banks = set()
        self.player.classic_spinner_value = 100
        self.player.classic_ball_save_ready = 0

        for bank, switches in self.DROP_SWITCHES.items():
            for target, switch in enumerate(switches, 1):
                self.add_mode_event_handler(switch + "_active", self._drop_hit, bank=bank, target=target)
            self.add_mode_event_handler(f"drop_target_bank_{bank}_down", self._bank_down, bank=bank)
        for crater, switch in enumerate(self.CRATER_SWITCHES, 1):
            self.add_mode_event_handler(switch + "_active", self._crater_hit, crater=crater)
        self.add_mode_event_handler("s_green_button_right_56_active", self._freeze)
        self.add_mode_event_handler("playfield_active", self._playfield_active)
        for event in self.SCORING_EVENTS:
            self.add_mode_event_handler(event, self._playfield_active)
        self.add_mode_event_handler("s_spinner_44_active", self._spinner_hit)
        self._show_lamps()
        self._schedule_scan("drops", 200, self._advance_drops)
        self._schedule_scan("craters", 200, self._advance_craters)

    def _schedule_scan(self, name, delay, callback):
        self.delay.reset(ms=delay, name=name, callback=callback)

    def _advance_drops(self):
        self.drop_index = self.drop_index % 5 + 1
        self._show_lamps()
        self._schedule_scan("drops", 200, self._advance_drops)

    def _advance_craters(self):
        self.crater_index = (self.crater_index - 1) % 5
        self._show_lamps()
        self._schedule_scan("craters", 200, self._advance_craters)

    def _playfield_active(self, **kwargs):
        if not self.ball_active:
            self.ball_active = True
            self._schedule_scan("drops", 1000, self._advance_drops)
            self._schedule_scan("craters", 1000, self._advance_craters)
        self.can_freeze = True

    def _freeze(self, **kwargs):
        if not self.can_freeze:
            return
        self.can_freeze = False
        self.delay.remove("drops")
        self.delay.remove("craters")
        if self.ball_active:
            self._schedule_scan("drops", 2000, self._advance_drops)
            self._schedule_scan("craters", 2000, self._advance_craters)

    def _drop_hit(self, bank, target, **kwargs):
        lit = target == self.drop_index
        value = 5000 if lit else (1000 if bank in self.completed_banks else 100)
        self._score(value)
        if lit:
            self.player.classic_bonus_multiplier = min(5, self.player.classic_bonus_multiplier + 1)
            self.machine.events.post("classic_ball_save_qualified")
            self._schedule_scan("drops", 1000, self._advance_drops)

    def _bank_down(self, bank, **kwargs):
        self.completed_banks.add(bank)
        other_bank = self.player.classic_completed_bank
        if other_bank and other_bank != bank:
            self.player.classic_completed_bank = ""
            self.player.classic_extra_ball_ready = 1
        else:
            self.player.classic_completed_bank = bank
        self.delay.reset(ms=500, name=bank, callback=self.machine.drop_target_banks[bank].reset)
        self._show_lamps()

    def _crater_hit(self, crater, **kwargs):
        self._score(1000 * crater * crater)
        self.player.classic_bonus_units = min(19, self.player.classic_bonus_units + crater)
        if crater == self.crater_index:
            self.machine.events.post("classic_lock_qualified")
        self._schedule_scan("craters", 1000, self._advance_craters)
        if crater > 1:
            self.player.classic_playfield_multiplier = crater
            self.delay.reset(ms={2: 28000, 3: 11000, 4: 7000}[crater],
                             name="multiplier", callback=self._clear_multiplier)
        if crater >= 3:
            self.player.classic_spinner_value = 1000
        self._show_lamps()

    def _clear_multiplier(self):
        self.player.classic_playfield_multiplier = 1
        self._show_lamps()

    def _spinner_hit(self, **kwargs):
        self._score(self.player.classic_spinner_value)

    def _score(self, value):
        self.machine.playfield.mark_playfield_active_from_device_action(self.name)
        self.player.score += value * self.player.classic_playfield_multiplier
        self._playfield_active()

    def _show_lamps(self):
        lit = {18 + self.drop_index}
        if self.crater_index:
            lit.add(28 - self.crater_index)
        if "top_bank" in self.completed_banks:
            lit.add(28)
        if "right_bank" in self.completed_banks:
            lit.add(29)
        if self.player.classic_playfield_multiplier > 1:
            lit.add(28 + self.player.classic_playfield_multiplier)
        if self.player.classic_spinner_value == 1000:
            lit.add(46)
        for number in self.LAMPS:
            self.machine.lights[f"l_xxx_{number}"].color(
                "white" if number in lit else "black", priority=self.priority, key=self.name
            )

    def mode_stop(self, **kwargs):
        for number in self.LAMPS:
            self.machine.lights[f"l_xxx_{number}"].remove_from_stack_by_key(self.name)
