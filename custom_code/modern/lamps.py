"""Layered lamp requests for Modern: flashing directs a shot, steady shows a lit feature."""

import logging

from custom_code.modern import settings

LOG = logging.getLogger("modern.lamps")
WATCHED = {light for (_, light, _) in settings.LOCATIONS.values() if light}
NAMES = {0: "OFF", 1: "STEADY", 2: "FLASH"}

OFF, STEADY, FLASH = 0, 1, 2


class LampDirector:
    """Resolve every Modern lamp request, with flash taking precedence over steady."""

    def __init__(self, mode):
        self.mode = mode
        self.machine = mode.machine
        self.requests = {}
        self.flash_on = True
        self.shown = {}

    def start(self):
        self.mode.delay.reset(ms=settings.FLASH_MS, name="lamp_flash", callback=self._toggle)

    def set(self, key, light, state=STEADY):
        if light is None:
            return
        before = self.state(light)
        if state == OFF:
            self.requests.pop((key, light), None)
        else:
            self.requests[(key, light)] = state
        self._log(light, before, key)
        self.refresh()

    def clear(self, key):
        for request in [r for r in self.requests if r[0] == key]:
            before = self.state(request[1])
            del self.requests[request]
            self._log(request[1], before, key)
        self.refresh()

    def _log(self, light, before, key):
        """Log location-lamp intent changes so a cabinet log shows what each lamp should be doing."""
        after = self.state(light)
        if light in WATCHED and after != before:
            LOG.info("Lamp %s %s -> %s (%s)", light, NAMES[before], NAMES[after], key)

    def state(self, light):
        return max((s for (_, l), s in self.requests.items() if l == light), default=OFF)

    def _toggle(self):
        self.flash_on = not self.flash_on
        self.refresh()
        self.mode.delay.reset(ms=settings.FLASH_MS, name="lamp_flash", callback=self._toggle)

    def refresh(self):
        lights = {l for (_, l) in self.requests} | set(self.shown)
        for light in lights:
            state = self.state(light)
            on = state == STEADY or (state == FLASH and self.flash_on)
            if self.shown.get(light) == on:
                continue
            self.shown[light] = on
            if light in self.machine.lights:
                self.machine.lights[light].color("white" if on else "black",
                                                 priority=self.mode.priority, key="modern_lamps")

    def stop(self):
        self.mode.delay.remove("lamp_flash")
        for light in self.shown:
            if light in self.machine.lights:
                self.machine.lights[light].remove_from_stack_by_key("modern_lamps")
        self.requests.clear()
        self.shown.clear()


class _NullDirector:
    def set(self, *args, **kwargs):
        pass

    def clear(self, *args, **kwargs):
        pass


def director(machine):
    """The running Modern lamp director, or a no-op one between balls."""
    core = machine.modes["modern"]
    return core.lamps if core.active and hasattr(core, "lamps") else _NullDirector()
