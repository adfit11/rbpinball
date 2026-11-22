"""The ambient lamp layer: base, artist-mode and multiball patterns on lamps no feature is using."""

import random

from custom_code.modern import ambient, settings as S
from custom_code.modern.lamps import FLASH, OFF
from tests.modern_helpers import ModernTestCase


class TestAmbientPatterns:
    def test_path_runs_from_the_flippers_to_the_target(self):
        lamps = list(S.LAMP_XY)
        run = ambient.path(lamps, ambient.FLIPPERS, S.LAMP_XY["l_xxx_47"])
        ys = [S.LAMP_XY[l][1] for l in run]
        assert len(run) >= 4 and ys == sorted(ys, reverse=True)

    def test_guide_streams_toward_the_target_and_speeds_up(self):
        free = [l for l in S.LAMP_XY if l != "l_xxx_47"]
        target = [S.LAMP_XY["l_xxx_47"]]
        lit = [ambient.Guide().advance(10_000, free, target)]
        assert lit[0] and all(l in free for l in lit[0])
        slow, fast = ambient.Guide(), ambient.Guide(source=type("R", (), {"ambient_speed": lambda self: 2.0})())
        steps = []
        for pattern in (slow, fast):
            seen = 0
            for _ in range(20):
                before = pattern.lit
                pattern.advance(50, free, target)
                seen += pattern.lit != before
            steps.append(seen)
        assert steps[1] > steps[0]

    def test_wander_and_multiball_cover_the_table(self):
        free = list(S.LAMP_XY)
        for name, at_least in (("wander", 8), ("multiball", 30)):
            pattern = ambient.PATTERNS[name](rng=random.Random(1))
            seen = set()
            for _ in range(200):
                seen |= pattern.advance(50, free, [])
            assert len(seen) >= at_least, name

    def test_ripple_spreads_from_the_bumpers(self):
        pattern = ambient.Ripple()
        pattern.kick()
        rings = [pattern.advance(60, list(S.LAMP_XY), []) for _ in range(8)]
        assert any(rings) and pattern.rings


class TestAmbientLamps(ModernTestCase):
    ambient = True

    def lit_lamps(self, seconds):
        lamps, seen = self.machine.modes["modern"].lamps, set()
        for _ in range(int(seconds * 10)):
            self.advance_time_and_run(.1)
            seen |= lamps.ambient_lit
        return seen

    def test_base_layer_runs_and_never_touches_location_or_requested_lamps(self):
        self.start_modern()
        lamps = self.machine.modes["modern"].lamps
        seen = self.lit_lamps(6)
        self.assertTrue(seen)
        self.assertFalse(seen & {loc[1] for loc in S.LOCATIONS.values()})
        self.assertNotIn(S.SHOOT_AGAIN_LAMP, seen)
        self.assertEqual(lamps.pattern_key, "base")

    def test_artist_mode_guides_and_multiball_takes_over(self):
        self.start_modern()
        self.player.modern_nickel = 1
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._start_song(jukebox.slots[0][1][0])
        self.advance_time_and_run(.2)
        lamps = self.machine.modes["modern"].lamps
        rule = self.machine.modes["modern_songs"].rule
        self.assertEqual(lamps.state(S.LOCATIONS[rule.target][1]), FLASH)
        self.lit_lamps(1)
        self.assertEqual(lamps.pattern_key, "song")
        self.assertIsInstance(lamps.pattern, ambient.Guide)
        self.assertTrue(all(lamps.state(l) == OFF for l in lamps.ambient_lit))
        lamps.set_ambient("rent_party", "multiball")
        self.lit_lamps(.5)
        self.assertIsInstance(lamps.pattern, ambient.Multiball)
        lamps.clear_ambient("rent_party")
        jukebox.end_song()
        self.lit_lamps(.5)
        self.assertEqual(lamps.pattern_key, "base")
