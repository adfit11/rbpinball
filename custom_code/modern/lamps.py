"""Layered lamp requests for Modern: flashing directs a shot, steady shows a lit feature.

SOLID is steady that also beats flash, for a feature whose lamp must never be read as a shot target.
A virtual lamp (the Booths) is an alias the targets mode points at a group of real lamps.
"""

import logging

from custom_code.modern import settings
from custom_code.modern.ambient import PATTERNS, RANKS

LOG = logging.getLogger("modern.lamps")
WATCHED = {light for (_, light, _) in settings.LOCATIONS.values() if light}
NAMES = {0: "OFF", 1: "STEADY", 2: "FLASH", 3: "SOLID"}

OFF, STEADY, FLASH, SOLID = 0, 1, 2, 3


class LampDirector:
    """Resolve every Modern lamp request: solid beats flash, which beats steady."""

    def __init__(self, mode):
        self.mode = mode
        self.machine = mode.machine
        self.requests = {}
        self.flash_on = True
        self.shown = {}
        self.aliases = {settings.BOOTHS_LAMP: ()}
        self.ambients = {"base": ("base", None)}  # key -> (pattern name, rule it reads speed/origin from)
        self.pattern, self.pattern_key = None, None
        self.ambient_lit = set()

    def alias(self, name, lights):
        """Point a virtual lamp's requests at a group of real lamps (or none)."""
        self.aliases[name] = tuple(lights)
        self.refresh()

    def _real(self, light):
        return self.aliases.get(light, (light,))

    def start(self):
        self.mode.delay.reset(ms=settings.FLASH_MS, name="lamp_flash", callback=self._toggle)
        if settings.AMBIENT_ENABLED:
            self.mode.delay.reset(ms=settings.AMBIENT_MS, name="lamp_ambient", callback=self._ambient)

    # Ambient layer --------------------------------------------------------
    def set_ambient(self, key, name, source=None):
        """Run an ambient pattern; the most intense one requested plays (base < artist mode < multiball)."""
        self.ambients[key] = (name, source)

    def clear_ambient(self, key):
        self.ambients.pop(key, None)

    def ambient_kick(self):
        if self.pattern:
            self.pattern.kick()

    def ambient_free(self, name):
        """Lamps the ambient layer may light: unrequested, and never a location, special, multiplier or shoot-again lamp."""
        busy = {settings.SHOOT_AGAIN_LAMP}
        if name != "multiball":
            busy |= set(settings.MULTIPLIER_LAMPS) | set(settings.OVATION_LAMPS)
            busy |= WATCHED | set(settings.DROP_LAMPS) | {settings.BANK_LAMPS["right_bank"], settings.SPECIAL_LAMP}
        return [l for l in settings.LAMP_XY if l not in busy and self.state(l) == OFF]

    def ambient_targets(self):
        """Where each flashing request is, so a stream can lead the player to it."""
        spots = []
        for (_, light), state in sorted(self.requests.items()):
            real = [l for l in self._real(light) if l in settings.LAMP_XY]
            if state == FLASH and real:
                spot = tuple(sum(settings.LAMP_XY[l][i] for l in real) / len(real) for i in (0, 1))
                if spot not in spots:
                    spots.append(spot)
        return spots

    def _ambient(self):
        self.mode.delay.reset(ms=settings.AMBIENT_MS, name="lamp_ambient", callback=self._ambient)
        key = max(self.ambients, key=lambda k: RANKS[self.ambients[k][0]])
        name, source = self.ambients[key]
        if key != self.pattern_key or not isinstance(self.pattern, PATTERNS[name]):
            self.pattern, self.pattern_key = PATTERNS[name](source), key
        lit = self.pattern.advance(settings.AMBIENT_MS, self.ambient_free(name), self.ambient_targets())
        if lit != self.ambient_lit:
            self.ambient_lit = lit
            self.refresh()

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
        return max((s for (_, l), s in self.requests.items() if l == light or light in self._real(l)), default=OFF)

    def _toggle(self):
        self.flash_on = not self.flash_on
        self.refresh()
        self.mode.delay.reset(ms=settings.FLASH_MS, name="lamp_flash", callback=self._toggle)

    def refresh(self):
        lights = {real for (_, l) in self.requests for real in self._real(l)} | set(self.shown) | self.ambient_lit
        for light in lights:
            state = self.state(light)
            on = state in (STEADY, SOLID) or (state == FLASH and self.flash_on) or (state == OFF and light in self.ambient_lit)
            if self.shown.get(light) == on:
                continue
            self.shown[light] = on
            if light in self.machine.lights:
                self.machine.lights[light].color("white" if on else "black",
                                                 priority=self.mode.priority, key="modern_lamps")

    def stop(self):
        self.mode.delay.remove("lamp_flash")
        self.mode.delay.remove("lamp_ambient")
        self.ambient_lit = set()
        for light in self.shown:
            if light in self.machine.lights:
                self.machine.lights[light].remove_from_stack_by_key("modern_lamps")
        self.requests.clear()
        self.shown.clear()


class _NullDirector:
    def set(self, *args, **kwargs):
        pass

    def alias(self, *args, **kwargs):
        pass

    def clear(self, *args, **kwargs):
        pass

    def set_ambient(self, *args, **kwargs):
        pass

    def clear_ambient(self, *args, **kwargs):
        pass

    def ambient_kick(self):
        pass


def director(machine):
    """The running Modern lamp director, or a no-op one between balls."""
    core = machine.modes["modern"]
    return core.lamps if core.active and hasattr(core, "lamps") else _NullDirector()
