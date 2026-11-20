"""Simulator only: the MPF monitor shows lit lamps in bright amber instead of white."""

from mpf.core.custom_code import CustomCode
from mpf.devices.light import Light
from mpf.platforms.virtual import VirtualHardwarePlatform

LIT = (255, 170, 0)


def monitor_color(color):
    """Recolour a lit white lamp amber, keeping its brightness."""
    r, g, b = color
    if r == g == b and r:
        return [round(c * r / 255) for c in LIT]
    return [r, g, b]


class SimMonitorColors(CustomCode):

    def on_load(self):
        if not isinstance(self.machine.default_platform, VirtualHardwarePlatform):
            return
        original = Light.get_monitorable_state
        if getattr(original, "sim_amber", False):
            return

        def get_monitorable_state(light):
            state = original(light)
            color = state.get("color")
            if isinstance(color, (list, tuple)) and len(color) == 3:
                state["color"] = monitor_color(color)
            return state

        get_monitorable_state.sim_amber = True
        Light.get_monitorable_state = get_monitorable_state
