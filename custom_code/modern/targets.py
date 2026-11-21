"""Modern craters, drop banks and Drop the Needle.

The crater cascade timings mirror Classic's ClassicTargets, but live here so Modern can be
removed without touching Classic. The drop lamps cascade all ball, and each lamp
also stays lit while its right-bank target is down.
"""

from mpf.core.mode import Mode

from custom_code.classic_targets import ClassicTargets
from custom_code.modern import settings
from custom_code.modern.holes import plain_virtual
from custom_code.modern.lamps import STEADY, director
from custom_code.modern.scoring import award

SCAN_MS = 200
RESUME_MS = 1000
FREEZE_MS = 2000
SKILL_IGNORED = {
    "s_flipper_left", "s_flipper_right", "s_green_button_right_56", "s_test_switch_7", "s_start_47",
    "s_tilt_46", "s_trough_1_40", "s_trough_2_30", "s_trough_3_20", "s_subway_kicker_0",
    "s_subway_one_3", "s_subway_lock_10", "s_spinner_44",
}


class ModernTargets(Mode):
    DROP_SWITCHES = ClassicTargets.DROP_SWITCHES
    CRATER_SWITCHES = ClassicTargets.CRATER_SWITCHES

    def mode_start(self, **kwargs):
        self.drop_index = 1
        self.crater_index = 4
        self.ball_active = False
        self.can_freeze = True
        self.frozen = False
        self.down_banks = set()
        self.down_targets = set()
        self.skill_window = False
        for bank, switches in self.DROP_SWITCHES.items():
            for target, switch in enumerate(switches, 1):
                self.add_mode_event_handler(switch + "_active", self._drop_hit, bank=bank, target=target)
            self.add_mode_event_handler(f"drop_target_bank_{bank}_down", self._bank_down, bank=bank)
            self.add_mode_event_handler(f"drop_target_bank_{bank}_up", self._bank_up, bank=bank)
        self.add_mode_event_handler("modern_freeze", self._freeze)
        self.add_mode_event_handler("balldevice_bd_trough_ejecting_ball", self._serve)
        for switch in self.machine.switches.values():
            if switch.name not in SKILL_IGNORED and not switch.name.startswith(("s_top_drop", "s_right_drop")):
                self.add_mode_event_handler(switch.name + "_active", self._playfield_hit)
        self._clear_simulated_drops()
        self._schedule("drops", SCAN_MS, self._advance_drops)
        self._schedule("craters", SCAN_MS, self._advance_craters)
        self._show_lamps()

    @property
    def lamps(self):
        return director(self.machine)

    def crater_lit(self, crater):
        return bool(self.crater_index) and crater >= self.crater_index

    def _schedule(self, name, delay, callback):
        self.delay.reset(ms=delay, name=name, callback=callback)

    def _advance_drops(self):
        self.drop_index = self.drop_index % 5 + 1
        self._show_lamps()
        self._schedule("drops", SCAN_MS, self._advance_drops)

    def _advance_craters(self):
        self.crater_index = (self.crater_index - 1) % 5
        self._show_lamps()
        self._schedule("craters", SCAN_MS, self._advance_craters)

    def _serve(self, target=None, **kwargs):
        if target is self.machine.playfield:
            self.skill_window = True
            self.machine.events.post("modern_skill_shot_ready")
            self.machine.events.post("modern_callout", pool="mc_skill_shot")

    def _playfield_hit(self, **kwargs):
        self.skill_window = False
        if not self.ball_active:
            self.ball_active = True
            self.machine.events.post("modern_ball_in_play")
            self._schedule("drops", RESUME_MS, self._advance_drops)
            self._schedule("craters", RESUME_MS, self._advance_craters)
        self.can_freeze = True

    def _freeze(self, **kwargs):
        if not self.can_freeze:
            return
        self.can_freeze = False
        self.delay.remove("drops")
        self.delay.remove("craters")
        self.machine.events.post("modern_lamps_frozen")
        if self.ball_active:
            self._schedule("drops", FREEZE_MS, self._advance_drops)
            self._schedule("craters", FREEZE_MS, self._advance_craters)

    def crater_entered(self, crater):
        """Score a crater; return whether it was lit."""
        lit = self.crater_lit(crater)
        award(self.machine, settings.SCORE_CRATER_LIT if lit else settings.SCORE_CRATER, "crater")
        self._schedule("craters", RESUME_MS, self._advance_craters)
        self._playfield_hit()
        return lit

    def _drop_hit(self, bank, target, **kwargs):
        lit = target == self.drop_index
        self.down_targets.add((bank, target))
        self.player.modern_bonus_drops += 1
        award(self.machine, settings.SCORE_DROP, "drop")
        if lit and self.skill_window:
            self.skill_window = False
            award(self.machine, settings.SCORE_DROP_THE_NEEDLE, "drop_the_needle")
            self.player.modern_ovation = min(settings.MAX_OVATION - 1, self.player.modern_ovation + 1)
            self.machine.events.post("modern_drop_the_needle")
            self.machine.events.post("modern_ball_saver_qualified")
        self.skill_window = False
        self._playfield_hit()
        if lit:
            self._schedule("drops", RESUME_MS, self._advance_drops)
        self._show_lamps()
        self.machine.events.post("modern_drop_hit", bank=bank, lit=lit)

    def _bank_down(self, bank, **kwargs):
        if bank in self.down_banks:
            return
        self.down_banks.add(bank)
        award(self.machine, settings.SCORE_BANK, "bank")
        self.machine.events.post("modern_bank_completed", bank=bank)
        # The completed bank pops straight back up; its bank lamp stays lit until both are completed.
        self.delay.reset(ms=500, name=f"reset_{bank}", callback=self._reset_bank, bank=bank)
        if len(self.down_banks) == 2:
            self.machine.events.post("modern_floor_nickel")
            self.down_banks.clear()
        self._show_lamps()

    def _bank_up(self, bank, **kwargs):
        self.down_targets = {(b, t) for b, t in self.down_targets if b != bank}
        self._show_lamps()

    def _reset_bank(self, bank):
        self.machine.drop_target_banks[bank].reset()
        self._clear_simulated_drops(bank)

    def _clear_simulated_drops(self, bank=None):
        """mpf -x: the reset coil can't raise simulated targets, so release their switches."""
        if not plain_virtual(self.machine):
            return
        for name, switches in self.DROP_SWITCHES.items():
            if bank and name != bank:
                continue
            for switch in switches:
                if self.machine.switches[switch].state:
                    self.machine.default_platform.virtual_set_switch(switch, 0)

    def _show_lamps(self):
        if not hasattr(self, "drop_index"):
            return
        lamps = self.lamps
        for index, light in enumerate(settings.DROP_LAMPS, 1):
            lit = index == self.drop_index or ("right_bank", index) in self.down_targets
            lamps.set("drops", light, STEADY if lit else 0)
        for crater, light in enumerate(settings.CRATER_LAMPS, 1):
            lamps.set("craters", light, STEADY if self.crater_lit(crater) else 0)
        for bank, light in settings.BANK_LAMPS.items():
            lamps.set("banks", light, STEADY if bank in self.down_banks else 0)

    def mode_stop(self, **kwargs):
        try:
            lamps = self.lamps
        except KeyError:
            return
        for key in ("drops", "craters", "banks"):
            lamps.clear(key)
