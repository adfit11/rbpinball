"""Modern high-score entry: *select* follows Modern's remappable select switch."""

from custom_code.cabinet_high_score import CabinetHighScore
from custom_code.modern import settings


class ModernHighScore(CabinetHighScore):
    TAP_SWITCH = settings.TAP_SWITCH
    SELECT_HOLD_MS = settings.SELECT_HOLD_MS

    def select_switch(self):
        return self.machine.variables.get_machine_var("modern_select_switch") or settings.SELECT_SWITCH
