"""Modern's ball mode: base scoring, club locations, the select action and the lamps."""

from mpf.core.mode import Mode

from custom_code.modern import guide, settings
from custom_code.modern.lamps import LampDirector, STEADY
from custom_code.modern.scoring import award

BASE_SWITCHES = {
    "s_top_bumpers_35": "bumper", "s_bottom_bumpers_13": "bumper", "s_10_points_15": "standup",
    "s_rollunder_25": "rollunder", "s_return_left_16": "left_return",
    "s_outlane_left_6": "outlane", "s_outlane_right_5": "outlane", "s_kicking_target_26": "standup",
}
TASK_EVENTS = (
    "modern_nickel_directed", "modern_nickel_awarded", "modern_nickel_spent", "modern_selector_opened",
    "modern_selector_closed", "modern_artist_chosen", "modern_song_started", "modern_song_clock_started", "modern_song_ended", "modern_lock_lit", "modern_ball_locked",
    "multiball_modern_rent_party_started", "multiball_modern_rent_party_ended",
)
LOCATION_SWITCHES = {"s_spot_target_36": "coat_check"}

BALL_VARS = (
    "modern_nickel", "modern_nickel_progress", "modern_ovation", "modern_songs_completed_ball",
    "modern_bonus_bumpers", "modern_bonus_locations", "modern_bonus_drops", "modern_bonus_songs",
    "modern_ball_saver_ready", "modern_song_active", "modern_extra_ball_lit", "modern_counting_bonus",
)


class ModernCore(Mode):
    """Owns Modern's shared services; feature modes ask it for lamps and green ownership."""

    def mode_will_start(self, **kwargs):
        # Child modes start inside mode_modern_started, before mode_start runs, and set lamps at once.
        self.lamps = LampDirector(self)
        self.lamps.start()

    def mode_start(self, **kwargs):
        player = self.player
        for name in BALL_VARS:
            setattr(player, name, 0)
        player.modern_score_factor = 1
        player.modern_bumper_factor = 1
        if not player.modern_song_multiplier:
            player.modern_song_multiplier = 1
        self.green_owner = None
        self._green_down_at = None
        self._last_spin = -100
        self._set_tilt_warnings(settings.WARNINGS_TO_TILT)

        for switch, kind in BASE_SWITCHES.items():
            self.add_mode_event_handler(switch + "_active", self._base_hit, kind=kind)
        for switch, location in LOCATION_SWITCHES.items():
            self.add_mode_event_handler(switch + "_active", self._location_switch, location=location)
        self.add_mode_event_handler("s_spinner_44_active", self._spin)
        self.add_mode_event_handler(settings.TAP_SWITCH + "_active", self._green_down)
        self.add_mode_event_handler(settings.TAP_SWITCH + "_inactive", self._green_up)
        select_switch = self.select_switch()
        if select_switch != settings.TAP_SWITCH:
            self.add_mode_event_handler(select_switch + "_active", self._select_pressed)
        self.add_mode_event_handler("player_extra_balls", self._shoot_again_lamp)
        self._task = None
        for event in TASK_EVENTS:
            self.add_mode_event_handler(event, self._task_changed)
        self._task_changed()
        self._shoot_again_lamp()

    # Shared services -------------------------------------------------------
    def select_switch(self):
        return self.machine.variables.get_machine_var("modern_select_switch") or settings.SELECT_SWITCH

    def take_green(self, owner):
        self.green_owner = owner

    def release_green(self, owner):
        if self.green_owner == owner:
            self.green_owner = None

    def location_hit(self, location):
        """Score a club location and announce it to the feature modes."""
        self.player.modern_bonus_locations += 1
        award(self.machine, settings.SCORE_LOCATION, location)
        self.machine.events.post("modern_location_hit", location=location)

    def _task_changed(self, **kwargs):
        self.delay.reset(ms=50, name="task", callback=self._post_task)

    def _post_task(self):
        if not self.active or not self.machine.game:
            return
        task = guide.current_task(self.machine)
        if task != self._task:
            self._task = task
            self.machine.events.post("modern_task", title=task[0], detail=task[1])

    # Handlers --------------------------------------------------------------
    def _base_hit(self, kind, **kwargs):
        factor = 1
        if kind == "bumper":
            self.player.modern_bonus_bumpers += 1
            factor = max(1, self.player.modern_bumper_factor)
        award(self.machine, settings.SCORE_SWITCH, kind, factor)
        self.machine.events.post("modern_" + kind + "_hit")

    def _location_switch(self, location, **kwargs):
        self.location_hit(location)

    def _spin(self, **kwargs):
        now = self.machine.clock.get_time()
        award(self.machine, settings.SCORE_SPIN, "spinner")
        self.machine.events.post("modern_spin")
        if now - self._last_spin >= settings.BANDSTAND_QUIET_MS / 1000:
            self.location_hit("bandstand")
        self._last_spin = now

    def _green_down(self, **kwargs):
        self._green_down_at = self.machine.clock.get_time()
        if self.select_switch() == settings.TAP_SWITCH:
            self.delay.reset(ms=settings.SELECT_PROGRESS_MS, name="select_progress", callback=self._progress)

    def _progress(self):
        if self._green_down_at is None:
            return
        held = (self.machine.clock.get_time() - self._green_down_at) * 1000
        if held >= settings.SELECT_HOLD_MS:
            self._green_down_at = None
            self.machine.events.post("modern_select_progress", progress=1.0)
            self.machine.events.post("modern_select", owner=self.green_owner or "")
            return
        self.machine.events.post("modern_select_progress", progress=round(held / settings.SELECT_HOLD_MS, 2))
        self.delay.reset(ms=settings.SELECT_PROGRESS_MS, name="select_progress", callback=self._progress)

    def _green_up(self, **kwargs):
        self.delay.remove("select_progress")
        if self._green_down_at is None:
            return
        self._green_down_at = None
        self.machine.events.post("modern_select_progress", progress=0.0)
        self.machine.events.post("modern_tap", owner=self.green_owner or "")
        if self.green_owner is None:
            self.machine.events.post("modern_freeze")

    def _select_pressed(self, **kwargs):
        self.machine.events.post("modern_select", owner=self.green_owner or "")

    def _shoot_again_lamp(self, **kwargs):
        self.lamps.set("shoot_again", settings.SHOOT_AGAIN_LAMP,
                       STEADY if self.player.extra_balls > 0 else 0)

    def _set_tilt_warnings(self, count):
        """Route the tilt-tagged bob to warnings for Modern; Classic keeps its immediate tilt."""
        try:
            tilt = self.machine.modes["tilt"]
        except KeyError:
            return
        if getattr(tilt, "_warnings_to_tilt", None) is None:
            return
        restore = hasattr(self, "_saved_tilt")
        if not restore:
            self._saved_tilt = tilt._warnings_to_tilt
        tilt._warnings_to_tilt = count
        controller = self.machine.switch_controller
        for switch in self.machine.switches.items_tagged(tilt.tilt_config["tilt_switch_tag"]):
            old, new = (tilt._tilt_warning_switch_handler, tilt.tilt) if restore else \
                (tilt.tilt, tilt._tilt_warning_switch_handler)
            controller.remove_switch_handler(switch_name=switch.name, callback=old)
            controller.add_switch_handler_obj(switch=switch, callback=new)
        if restore:
            del self._saved_tilt

    def mode_stop(self, **kwargs):
        if hasattr(self, "_saved_tilt"):
            self._set_tilt_warnings(self._saved_tilt)
            self.machine.events.post("modern_tilt_restored")
        self.lamps.stop()
