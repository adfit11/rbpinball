"""Classic's captured-ball awards and release timing."""

from mpf.core.mode import Mode

from custom_code.classic_bonus import count_bonus_unit
from custom_code.classic_targets import ClassicTargets


class ClassicHoles(Mode):
    OUTLANE_CANCEL_SWITCHES = (
        "s_top_bumpers_35", "s_bottom_bumpers_13", "s_trough_3_20", "s_spinner_44",
        "s_hole_kicker_top_23", "s_kicking_target_26", "s_10_points_15", "s_spot_target_36",
        "s_outlane_left_6", "s_return_left_16", "s_rollunder_25",
        *ClassicTargets.CRATER_SWITCHES, *ClassicTargets.DROP_SWITCHES["top_bank"],
        *ClassicTargets.DROP_SWITCHES["right_bank"],
    )

    def mode_start(self, **kwargs):
        self.player.classic_extra_ball_ready = 0
        self.player.classic_outlane_extra_ready = 0
        self.add_mode_event_handler("ball_hold_classic_saucer_held_ball", self._saucer_captured)
        self.add_mode_event_handler("ball_hold_classic_firepit_held_ball", self._firepit_captured)
        self.add_mode_event_handler("s_outlane_right_5_active", self._right_outlane)
        for switch in self.OUTLANE_CANCEL_SWITCHES:
            self.add_mode_event_handler(switch + "_active", self._cancel_outlane_extra)

    def _saucer_captured(self, **kwargs):
        self.player.score += 3000 * self.player.classic_playfield_multiplier
        if self.player.classic_bonus_units == 19:
            self.player.classic_counting_bonus = 1
            self.delay.add(ms=150, callback=self._seismic_tick)
        else:
            self.delay.add(ms=1000, callback=self._release, hole="saucer")

    def _seismic_tick(self):
        if count_bonus_unit(self.player):
            self.delay.add(ms=150, callback=self._seismic_tick)
        else:
            self.player.classic_counting_bonus = 0
            self.player.classic_bonus_units = 1
            self._release("saucer")

    def _firepit_captured(self, **kwargs):
        self.player.score += 5000 * self.player.classic_playfield_multiplier
        if self.player.classic_extra_ball_ready:
            self.player.classic_extra_ball_ready = 0
            self.machine.events.post("classic_award_firepit_extra")
        if self.player.classic_outlane_extra_ready:
            self._cancel_outlane_extra()
            self.machine.events.post("classic_award_outlane_extra")
        self.delay.add(ms=1000, callback=self._release, hole="firepit")

    def _right_outlane(self, **kwargs):
        self.machine.playfield.mark_playfield_active_from_device_action(self.name)
        if self.player.classic_gate_open:
            self.player.score += 1000 * self.player.classic_playfield_multiplier
            self.machine.events.post("classic_close_gate")
        else:
            self.player.score += 5000 * self.player.classic_playfield_multiplier
            self.player.classic_outlane_extra_ready = 1

    def _cancel_outlane_extra(self, **kwargs):
        self.player.classic_outlane_extra_ready = 0

    def _release(self, hole):
        self.machine.events.post(f"classic_release_{hole}")

    def mode_stop(self, **kwargs):
        self.player.classic_counting_bonus = 0
