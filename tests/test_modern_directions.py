"""Modern: spoken and shown directions always match the current target."""

from custom_code.modern import settings as S
from custom_code.modern.callouts import load_script, names_only
from custom_code.modern.guide import current_task
from tests.modern_helpers import ModernTestCase

DIRECTIONS = tuple(f"{staff}_direction" for _, _, staff in S.LOCATIONS.values()) + tuple(
    f"mc_target_{l}" for l in S.LOCATION_NAMES)


class TestModernDirections(ModernTestCase):

    def collect_pools(self):
        pools = []
        self.machine.events.add_handler("modern_voice", lambda pool, **kwargs: pools.append(pool))
        return pools

    def open_selector(self):
        self.give_nickel()
        self.shoot_crater(1)
        self.advance_time_and_run(1)
        self.assertTrue(self.machine.modes["modern_jukebox"].selector_open)

    def assertNoDirections(self, pools):
        self.assertFalse([p for p in pools if p in DIRECTIONS or p.endswith("_refusal")], pools)

    def test_no_nickel_directions_while_picking_a_song(self):
        self.start_modern()
        self.open_selector()
        pools = self.collect_pools()
        self.mock_event("modern_nickel_directed")
        self.hit_location("coat_check")
        self.advance_time_and_run(S.TARGET_REMINDER_MS / 1000 + 1)
        self.assertNoDirections(pools)
        self.assertEventNotCalled("modern_nickel_directed")
        self.assertFalse(self.machine.modes["modern_nickels"].hunting())

    def test_no_nickel_directions_during_a_song_mode(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._start_song(jukebox.slots[1][1][0])
        self.advance_time_and_run(.2)
        pools = self.collect_pools()
        for location in ("coat_check", "bandstand", "booths", "bar"):
            self.hit_location(location)
        self.advance_time_and_run(S.TARGET_REMINDER_MS / 1000 + 1)
        self.assertNoDirections(pools)
        self.mock_event("modern_nickel_directed")
        jukebox.end_song()
        self.advance_time_and_run(.1)
        self.assertEventCalled("modern_nickel_directed")

    def test_task_panel_shows_the_chosen_mode_during_its_intro(self):
        self.start_modern()
        self.open_selector()
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._choose()
        self.advance_time_and_run(.1)
        self.assertIsNotNone(jukebox.chosen)
        self.assertTrue(current_task(self.machine)[0].startswith("SONG MODE"))

    def test_staff_refusals_only_name_the_real_target(self):
        self.start_modern()
        callouts = self.machine.modes["modern_callouts"]
        _, pools = load_script()
        nickels = self.machine.modes["modern_nickels"]
        for target in S.LOCATION_NAMES:
            for location in S.LOCATION_NAMES:
                if location == target:
                    continue
                self.player.modern_nickel_target = target
                voices = []
                handler = self.machine.events.add_handler("modern_voice", lambda **kwargs: voices.append(kwargs))
                for _ in range(10):
                    nickels._callout("refusal", location, allow=(location, target), fallback=f"mc_target_{target}")
                    self.advance_time_and_run(.01)
                self.machine.events.remove_handler_by_key(handler)
                self.assertTrue(voices)
                for voice in voices:
                    self.assertTrue(names_only(voice["text"], (location, target)), (target, location, voice["text"]))
        self.assertIsNotNone(callouts)
        self.assertTrue(pools)

    def test_names_only(self):
        self.assertFalse(names_only("What are you doing here? Kitchen's calling you.", ("bar", "booths")))
        self.assertTrue(names_only("What are you doing here? Kitchen's calling you.", ("bar", "kitchen")))
        self.assertFalse(names_only("You lost? Go see the hostess.", ("bar", "kitchen")))
        self.assertTrue(names_only("Not now, sugar. Try somewhere else.", ("bar",)))

    def test_lock_lit_waits_for_the_song_to_end(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._start_song(jukebox.slots[1][1][0])
        self.advance_time_and_run(.2)
        pools = self.collect_pools()
        party = self.machine.modes["modern_rent_party"]
        for guest in S.GUESTS[:S.GUESTS_TO_FILL]:
            party._guest(guest)
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.modern_lock_lit, 1)
        self.assertNotIn("mc_lock_lit", pools)
        jukebox.end_song()
        self.advance_time_and_run(.1)
        self.assertIn("mc_lock_lit", pools)


class TestKitchenReturns(ModernTestCase):

    def start_ladder(self):
        self.start_modern()
        self.player.modern_nickel = 1
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._start_song(jukebox.slots[1][1][0])
        self.advance_time_and_run(.2)
        return self.machine.modes["modern_songs"].rule

    def kitchen(self):
        device = self.machine.ball_devices["bd_classic_firepit"]
        self.machine.default_platform.add_ball_to_device(device)
        self.advance_time_and_run(1.2 + S.LADDER_HOLD_MS / 1000 + .5)  # held, then kicked out
        self.assertEqual(device.balls, 0)

    def test_every_return_after_a_playfield_switch_climbs_a_rung(self):
        rule = self.start_ladder()
        for rung in range(1, 4):
            self.kitchen()
            self.hit_and_release_switch("s_10_points_15")
            self.advance_time_and_run(.3)
            self.assertEqual(rule.rung, rung)

    def test_a_return_with_no_playfield_switch_still_climbs_a_rung(self):
        rule = self.start_ladder()
        for rung in range(1, 4):
            self.kitchen()
            self.advance_time_and_run(3.5)  # the eject confirms on its timeout
            self.assertEqual(rule.rung, rung)
