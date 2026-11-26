"""Cabinet selection before the built-in MPF game starts."""

from mpf.modes.attract.code.attract import Attract

from custom_code.subway_ejector import InterlockedSubwayEjector
from custom_code.subway_startup import SubwayStartupClear


class VolcanoAttract(Attract):
    """Use the cabinet buttons to select a game, then its player count."""

    GREEN_PRESS_MS = 30
    GREEN_RELEASE_MS = 100
    # With no input for this long, attract shows its posters and Hall of Fame until a button is pressed.
    SHOWCASE_IDLE_MS = 30_000

    def mode_start(self, retry_selection=None, **kwargs):
        variables = self.machine.variables
        on_cabinet = bool(variables.get_machine_var("lisy_hardware"))
        self.start_pending = False
        self._cabinet_input_ready_at = 0
        if on_cabinet:
            # LISY can replay queued button transitions as attract starts.
            self._cabinet_input_ready_at = self.machine.clock.get_time() + .25
        variables.set_machine_var("session_game", "")
        variables.set_machine_var("session_players", 0)
        game, count = retry_selection or ("modern", 1)
        variables.set_machine_var("selection_game", game)
        variables.set_machine_var("selection_players", count)
        variables.set_machine_var("selection_stage", "players" if retry_selection else "game")
        variables.set_machine_var("attract_showcase", False)
        self._idle_from_now()
        self.add_mode_event_handler("s_flipper_left_active", self._select_left)
        self.add_mode_event_handler("s_flipper_right_active", self._select_right)
        if on_cabinet:
            green_button = self.machine.switches["s_green_button_right_56"]
            self._green_armed = not self.machine.switch_controller.is_active(green_button)
            self.switch_handlers.append(green_button.add_handler(self._press_green, ms=self.GREEN_PRESS_MS))
            self.switch_handlers.append(green_button.add_handler(self._arm_green, state=0, ms=self.GREEN_RELEASE_MS))
        else:
            self.add_mode_event_handler("s_green_button_right_56_active", self._cycle_selection)
        super().mode_start(**kwargs)
        # LISY keeps L0 from before MPF started. Switch it off so the bumpers, slingshots and flippers
        # are dead while the subway clear drains balls; the game turns it on again.
        relay = self.machine.digital_outputs.get("game_over_relay")
        if relay is not None:
            relay.disable()
        self.subway_startup = None
        subway = self.machine.ball_devices.get("bd_classic_subway_lock")
        if subway is not None and isinstance(subway.ejector, InterlockedSubwayEjector):
            self.subway_startup = SubwayStartupClear(self.machine)
            self.subway_startup.start()

    def mode_stop(self, **kwargs):
        if self.subway_startup is not None:
            self.subway_startup.stop()
        super().mode_stop(**kwargs)

    def _selection_input_ready(self):
        if self.start_pending or self.machine.clock.get_time() < self._cabinet_input_ready_at:
            return False
        # A press during the showcase only brings the selection back.
        return not self._wake()

    def _idle_from_now(self):
        self.delay.reset(ms=self.SHOWCASE_IDLE_MS, name="showcase", callback=self._showcase)

    def _wake(self):
        """Restart the idle clock; return True if this press ended the showcase."""
        self._idle_from_now()
        variables = self.machine.variables
        if not variables.get_machine_var("attract_showcase"):
            return False
        variables.set_machine_var("attract_showcase", False)
        return True

    def _showcase(self):
        if self.start_pending:
            self._idle_from_now()
            return
        variables = self.machine.variables
        variables.set_machine_var("selection_stage", "game")
        variables.set_machine_var("selection_players", 1)
        variables.set_machine_var("attract_showcase", True)

    def _press_green(self):
        if self._green_armed:
            self._green_armed = False
            self._cycle_selection()

    def _arm_green(self):
        self._green_armed = True

    def _cycle_selection(self, **kwargs):
        if not self._selection_input_ready():
            return
        variables = self.machine.variables
        if variables.get_machine_var("selection_stage") == "game":
            game = variables.get_machine_var("selection_game")
            variables.set_machine_var("selection_game", "modern" if game == "classic" else "classic")
        else:
            count = variables.get_machine_var("selection_players")
            variables.set_machine_var("selection_players", 1 if count == 4 else count + 1)

    def _select_left(self, **kwargs):
        self._move_selection("classic", -1)

    def _select_right(self, **kwargs):
        self._move_selection("modern", 1)

    def _move_selection(self, game, player_delta):
        if not self._selection_input_ready():
            return
        variables = self.machine.variables
        if variables.get_machine_var("selection_stage") == "game":
            variables.set_machine_var("selection_game", game)
        else:
            count = variables.get_machine_var("selection_players")
            variables.set_machine_var("selection_players", min(4, max(1, count + player_delta)))

    def start_button_released(self, **kwargs):
        if not self._selection_input_ready():
            return
        variables = self.machine.variables
        if variables.get_machine_var("selection_stage") == "game":
            variables.set_machine_var("selection_players", 1)
            variables.set_machine_var("selection_stage", "players")
            return

        self.start_pending = True
        self._start_when_subway_ready()

    def _start_when_subway_ready(self):
        if not self.active or not self.start_pending:
            return
        if self.subway_startup is not None:
            status = self.subway_startup.status
            if status in ("running", "reconciling"):
                self.machine.events.post("subway_startup_not_ready", status=status,
                                         reason=self.subway_startup.reason)
                self.delay.reset(ms=100, name="wait_for_subway", callback=self._start_when_subway_ready)
                return
            if status != "done":
                self.start_pending = False
                self.machine.events.post("subway_startup_not_ready", status=status,
                                         reason=self.subway_startup.reason)
                return
        super().start_button_released()

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
