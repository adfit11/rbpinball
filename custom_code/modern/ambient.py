"""Ambient lamp patterns: a moving background on the lamps no feature is using, at three intensities.

base       a slow single lamp walks from the flippers to whatever is flashing, with the odd twinkle.
guide      artist modes: a two-lamp stream runs to each flashing target in turn, faster as the rule heats up.
wander     Party Time: a few lamps drift around the whole table, because every shot pays.
ripple     Dance Floor: rings spread from the bumpers on each hit; a stream leads to them in between.
multiball  Rent Party: the full-table show.
Lamp requests always win, so flashing targets and steady features read exactly as before.
"""

import math
import random

from custom_code.modern import settings as S

FLIPPERS = (0.47, 0.86)
BUMPERS = (0.38, 0.52)  # between the top and bottom bumpers
RANKS = {"base": 0, "guide": 1, "wander": 1, "ripple": 1, "multiball": 2}


def xy(light):
    return S.LAMP_XY[light]


def path(lamps, start, end, width=0.09):
    """Lamps within width of the line start -> end, ordered from start to end."""
    (x0, y0), (x1, y1) = start, end
    dx, dy = x1 - x0, y1 - y0
    length2 = dx * dx + dy * dy or 1e-9
    hits = []
    for light in lamps:
        x, y = xy(light)
        t = ((x - x0) * dx + (y - y0) * dy) / length2
        if -0.05 <= t <= 0.97 and math.hypot(x - x0 - t * dx, y - y0 - t * dy) <= width:
            hits.append((t, light))
    return [light for _, light in sorted(hits)]


class Pattern:
    step_ms = 100

    def __init__(self, source=None, rng=random):
        self.source, self.rng, self.lit, self.elapsed = source, rng, set(), 0

    def speed(self):
        return max(0.25, getattr(self.source, "ambient_speed", lambda: 1.0)())

    def origin(self):
        return getattr(self.source, "ambient_origin", lambda: FLIPPERS)()

    def advance(self, ms, free, targets):
        """Move on by ms; free is the lamps this layer may light, targets the flashing shots' positions."""
        self.elapsed += ms
        step = self.step_ms / self.speed()
        while self.elapsed >= step:
            self.elapsed -= step
            self.lit = self.step(sorted(free), targets)
        return self.lit & set(free)

    def kick(self):
        pass

    def step(self, free, targets):
        return set()


class Stream(Pattern):
    """A short run of lamps from the origin to each target in turn, then a pause."""
    step_ms, tail, pause, twinkle = 85, 2, 3, 0.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run, self.pos, self.wait, self.turn, self.sparks = [], 0, 0, 0, {}

    def step(self, free, targets):
        lit = set()
        if self.twinkle:
            self.sparks = {l: n - 1 for l, n in self.sparks.items() if n > 1}
            if free and self.rng.random() < self.twinkle:
                self.sparks[self.rng.choice(free)] = 3
            lit |= set(self.sparks)
        if self.wait:
            self.wait -= 1
            return lit
        if not self.run:
            if not targets:
                return lit | self.idle(free)
            self.turn = (self.turn + 1) % len(targets)
            self.run, self.pos = path(free, self.origin(), targets[self.turn]), 0
            if not self.run:
                self.wait = self.pause
                return lit
        lit |= set(self.run[max(0, self.pos - self.tail + 1):self.pos + 1])
        self.pos += 1
        if self.pos >= len(self.run) + self.tail:
            self.run, self.wait = [], self.pause
        return lit

    def idle(self, free):
        return set()


class Base(Stream):
    step_ms, tail, pause, twinkle = 200, 1, 6, 0.08


class Guide(Stream):
    pass


class Wander(Pattern):
    """Three lamps drift to neighbouring lamps all over the table."""
    step_ms, dancers = 220, 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.at = []

    def step(self, free, targets):
        if not free:
            return set()
        self.at = [l for l in self.at if l in free]
        while len(self.at) < min(self.dancers, len(free)):
            self.at.append(self.rng.choice(free))
        moved = []
        for light in self.at:
            near = sorted((l for l in free if l != light and l not in moved),
                          key=lambda l: math.dist(xy(l), xy(light)))[:4]
            moved.append(self.rng.choice(near) if near else light)
        self.at = moved
        return set(moved)


class Ripple(Stream):
    """Each bumper hit sends a ring out from the bumpers; between hits a stream leads back to them."""
    step_ms = 60

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rings = []

    def kick(self):
        self.rings.append(0.0)

    def step(self, free, targets):
        self.rings = [r + 0.035 for r in self.rings if r < 0.5]
        if self.rings:
            return {l for l in free for r in self.rings if abs(math.dist(xy(l), BUMPERS) - r) < 0.03}
        return super().step(free, [BUMPERS])


class Multiball(Pattern):
    """A band rolls up and down the table, alternate lamps trade, a sparkle, lamps 1-10 ping-pong, then flashes."""
    step_ms = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frames, self.index, self.left = [], 0, 0

    def build(self, free):
        lamps = sorted(free, key=lambda l: -xy(l)[1])
        rows, row_y = [], None
        for light in lamps:
            if row_y is None or row_y - xy(light)[1] > 0.035:
                rows.append([])
                row_y = xy(light)[1]
            rows[-1].append(light)
        frames = []
        for i in list(range(len(rows))) + list(range(len(rows) - 2, 0, -1)):
            frames.append((6, {l for r in rows[max(0, i - 1):i + 2] for l in r}))
        for i in range(8):
            frames.append((18, set(lamps[i % 2::2])))
        for _ in range(16):
            frames.append((9, set(self.rng.sample(lamps, max(1, len(lamps) // 3)))))
        song = [l for l in S.SONG_LAMPS if l in free]
        rest = set(lamps) - set(song)
        for i in list(range(len(song))) + list(range(len(song) - 2, 0, -1)):
            frames.append((5, rest | {song[i]}))
        for on in (set(lamps), set(), set(lamps), set()):
            frames.append((14, on))
        return frames

    def step(self, free, targets):
        if not self.frames:
            self.frames = self.build(free)
            self.index, self.left = 0, self.frames[0][0]
        self.left -= 1
        if self.left <= 0:
            self.index = (self.index + 1) % len(self.frames)
            self.left = self.frames[self.index][0]
        return self.frames[self.index][1]


PATTERNS = {"base": Base, "guide": Guide, "wander": Wander, "ripple": Ripple, "multiball": Multiball}
