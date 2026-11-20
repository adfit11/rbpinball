"""Simulator only: make the MPF monitor show lamp changes, with lit lamps in bright amber.

MPF 0.80 never notifies the monitor when a light changes (its monitored ``_color``
attribute is never set), so the monitor only ever shows the colours from when it
connected. On a virtual platform this reports every change and recolours lit white
lamps amber; real lamp output is untouched.
"""

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


def _shown_color(light):
    return monitor_color(list(light.get_color().rgb))


class SimMonitorColors(CustomCode):

    def on_load(self):
        if not isinstance(self.machine.default_platform, VirtualHardwarePlatform):
            return
        if getattr(Light, "_sim_monitor", False):
            return
        shown = {}
        original_update = Light._schedule_update

        def get_monitorable_state(light):
            return {"color": _shown_color(light)}

        def _schedule_update(light):
            original_update(light)
            new = _shown_color(light)
            old = shown.get(id(light), [0, 0, 0])
            if new != old:
                shown[id(light)] = new
                light.machine.device_manager.notify_device_changes(light, "color", old, new)

        Light._sim_monitor = True
        Light.get_monitorable_state = get_monitorable_state
        Light._schedule_update = _schedule_update
