"""Modern craters, drop banks and Drop the Needle.

The cascade timings mirror Classic's ClassicTargets, but live here so Modern can be
removed without touching Classic.
"""

from mpf.core.mode import Mode

from custom_code.classic_targets import ClassicTargets
from custom_code.modern import settings
from custom_code.modern.lamps import FLASH, STEADY, director
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
        self.skill_window = False
        self.crater_prompt = False
        for bank, switches in self.DROP_SWITCHES.items():
            for target, switch in enumerate(switches, 1):
                self.add_mode_event_handler(switch + "_active", self._drop_hit, bank=bank, target=target)
            self.add_mode_event_handler(f"drop_target_bank_{bank}_down", self._bank_down, bank=bank)
        self.add_mode_event_handler("modern_freeze", self._freeze)
        self.add_mode_event_handler("balldevice_bd_trough_ejecting_ball", self._serve)
        for switch in self.machine.switches.values():
            if switch.name not in SKILL_IGNORED and not switch.name.startswith(("s_top_drop", "s_right_drop")):
                self.add_mode_event_handler(switch.name + "_active", self._playfield_hit)
        self._schedule("drops", SCAN_MS, self._advance_drops)
        self._schedule("craters", SCAN_MS, self._advance_craters)
        self._show_lamps()

    @property
    def lamps(self):
        return director(self.machine)

    def crater_lit(self, crater):
        return bool(self.crater_index) and crater >= self.crater_index

    def set_crater_prompt(self, prompt):
        """Flash the lit craters while the player is directed to the jukebox or lock."""
        self.crater_prompt = prompt
        if self.active:
            self._show_lamps()

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

    def _playfield_hit(self, **kwargs):
        self.skill_window = False
        if not self.ball_active:
            self.ball_active = True
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
        self.machine.events.post("modern_drop_hit", bank=bank, lit=lit)

    def _bank_down(self, bank, **kwargs):
        if bank in self.down_banks:
            return
        self.down_banks.add(bank)
        award(self.machine, settings.SCORE_BANK, "bank")
        self.machine.events.post("modern_bank_completed", bank=bank)
        if len(self.down_banks) == 2:
            self.machine.events.post("modern_floor_nickel")
            self.down_banks.clear()
            self.delay.reset(ms=500, name="reset_banks", callback=self._reset_banks)
        self._show_lamps()

    def _reset_banks(self):
        for bank in self.DROP_SWITCHES:
            self.machine.drop_target_banks[bank].reset()

    def _show_lamps(self):
        if not hasattr(self, "drop_index"):
            return
        lamps = self.lamps
        for index, light in enumerate(settings.DROP_LAMPS, 1):
            lamps.set("drops", light, STEADY if index == self.drop_index else 0)
        for crater, light in enumerate(settings.CRATER_LAMPS, 1):
            state = 0
            if self.crater_lit(crater):
                state = FLASH if self.crater_prompt else STEADY
            lamps.set("craters", light, state)
        for bank, light in settings.BANK_LAMPS.items():
            lamps.set("banks", light, STEADY if bank in self.down_banks else 0)

    def mode_stop(self, **kwargs):
        try:
            lamps = self.lamps
        except KeyError:
            return
        for key in ("drops", "craters", "banks"):
            lamps.clear(key)
