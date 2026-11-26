"""High-score entry for either game, with the right green button as the letter selector."""

from mpf.modes.high_score.code.high_score import HighScore


class CabinetHighScore(HighScore):
    """Keep each game's board apart and enter initials with the cabinet buttons.

    The board is saved to the ``mpf: paths: <mode name>`` file and published as the machine vars
    ``<game>_<category><position>_label/_name/_value`` (``classic_score1_name``) for the attract Hall of Fame.
    A green tap moves to the next letter and a green hold chooses it; the flippers move left and right.
    """

    TAP_SWITCH = "s_green_button_right_56"
    SELECT_HOLD_MS = 2000
    GREEN_PRESS_MS = 30
    GREEN_RELEASE_MS = 100

    def mode_init(self):
        self.board = self.name.removesuffix("_high_score")
        self.data_manager = self.machine.create_data_manager(self.name)
        self.high_scores = self.data_manager.get_data()
        self.high_score_config = self.machine.config_validator.validate_config(
            config_spec='high_score', source=self.config.get('high_score', {}), section_name='high_score')
        if self.high_scores and not self._validate_data(self.high_scores):
            self.log.warning("High score data failed validation. Resetting to defaults.")
            self.high_scores = None
        if not self.high_scores:
            self._load_defaults()
        self._create_machine_vars()
        self.pending_award = None
        for event in self.high_score_config['reset_high_scores_events']:
            self.machine.events.add_handler(event, self._reset)

    def _create_machine_vars(self):
        variables = self.machine.variables
        for category, labels in self.high_score_config['categories'].items():
            for position, (label, entry) in enumerate(zip(labels, self.high_scores.get(category, [])), 1):
                base = "{}_{}{}_".format(self.board, category, position)
                variables.set_machine_var(base + "label", label)
                variables.set_machine_var(base + "name", entry[0])
                variables.set_machine_var(base + "value", entry[1])

    def select_switch(self):
        return self.TAP_SWITCH

    def mode_start(self, **kwargs):
        super().mode_start(**kwargs)
        self._green_at = None
        if self.machine.variables.get_machine_var("lisy_hardware"):
            # The cabinet's green button bounces; count a press once it has settled.
            green = self.machine.switches[self.TAP_SWITCH]
            self.switch_handlers.append(green.add_handler(self._green_down, ms=self.GREEN_PRESS_MS))
            self.switch_handlers.append(green.add_handler(self._green_up, state=0, ms=self.GREEN_RELEASE_MS))
        else:
            self.add_mode_event_handler(self.TAP_SWITCH + "_active", self._green_down)
            self.add_mode_event_handler(self.TAP_SWITCH + "_inactive", self._green_up)
        if self.select_switch() != self.TAP_SWITCH:
            self.add_mode_event_handler(self.select_switch() + "_active", self._choose)
        self.add_mode_event_handler("s_flipper_left_active", self._move, action="left")
        self.add_mode_event_handler("s_flipper_right_active", self._move, action="right")

    def _move(self, action, **kwargs):
        self.machine.events.post("text_input", action=action)

    def _choose(self, **kwargs):
        self.machine.events.post("text_input", action="select")

    def _green_down(self, **kwargs):
        if self.select_switch() != self.TAP_SWITCH:
            self._move("right")
            return
        self._green_at = self.machine.clock.get_time()
        self.delay.reset(ms=self.SELECT_HOLD_MS, name="hold_select", callback=self._held)

    def _held(self):
        self._green_at = None
        self._choose()

    def _green_up(self, **kwargs):
        self.delay.remove("hold_select")
        if self._green_at is not None:
            self._green_at = None
            self._move("right")
