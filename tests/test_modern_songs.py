"""Modern song modes: each jukebox slot's rule."""

from custom_code.modern import settings as S
from tests.modern_helpers import ModernTestCase


class TestModernSongs(ModernTestCase):

    def start_slot(self, slot):
        self.start_modern()
        self.player.modern_nickel = 1  # keep the nickel hunt quiet
        jukebox = self.machine.modes["modern_jukebox"]
        jukebox._start_song(jukebox.slots[slot - 1][1][0])
        self.advance_time_and_run(.2)
        return self.machine.modes["modern_songs"].rule

    def test_every_slot_starts_its_rule(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        songs = self.machine.modes["modern_songs"]
        for slot in range(1, 11):
            jukebox._start_song(jukebox.slots[slot - 1][1][0])
            self.advance_time_and_run(.2)
            self.assertIsNotNone(songs.rule, slot)
            jukebox.end_song()
            self.advance_time_and_run(.1)
            self.assertIsNone(songs.rule)

    def test_hurry_up_collect_completes_and_ends(self):
        rule = self.start_slot(1)
        self.mock_event("modern_song_completed")
        self.hit_location(rule.target)
        self.assertEventCalled("modern_song_completed")
        self.assertIsNone(self.machine.modes["modern_jukebox"].song)
        self.assertEqual(self.player.modern_songs_completed_ball, 1)

    def test_hurry_up_bottoms_out(self):
        self.start_slot(1)
        self.mock_event("modern_song_failed")
        self.advance_time_and_run(S.HURRY_MS / 1000 + 1)
        self.assertEventCalled("modern_song_failed")
        self.assertIsNone(self.machine.modes["modern_jukebox"].song)

    def test_ladder_four_rungs(self):
        rule = self.start_slot(2)
        for _ in range(4):
            self.hit_location("kitchen")
        self.assertEqual(rule.rung, 4)
        self.assertTrue(rule.completed)

    def test_build_and_collect_pot(self):
        rule = self.start_slot(3)
        for _ in range(3):
            self.hit_and_release_switch("s_spinner_44")
            self.advance_time_and_run(.05)
        self.assertEqual(rule.pot, S.POT_START * 3 + S.POT_STEP * 3)
        rule.on_location("bar")
        self.assertEqual(rule.pot, 0)
        self.assertEqual(rule.collects, 1)

    def test_roving_shot_moves_and_freezes(self):
        rule = self.start_slot(4)
        first = rule.target
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(S.ROVE_FREEZE_MS / 1000 - .5)
        self.assertEqual(rule.target, first)
        self.advance_time_and_run(1)
        self.assertNotEqual(rule.target, first)
        for _ in range(3):
            rule.on_location(rule.target)
        self.assertTrue(rule.completed)

    def test_jukebox_jackpot_values(self):
        rule = self.start_slot(5)
        start = self.player.score
        self.shoot_crater(2)
        self.assertGreaterEqual(self.player.score - start, S.JACKPOT_VALUES[1])
        self.assertEqual(rule.jackpots, 1)
        self.assertEqual(self.player.modern_nickel, 1)  # no selector during a song

    def test_party_time_doubles_and_pays_last_dance(self):
        rule = self.start_slot(6)
        self.assertEqual(self.player.modern_ball_saver_ready, 1)
        start = self.player.score
        self.hit_and_release_switch("s_top_bumpers_35")
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.score - start, 2000)
        self.machine.modes["modern_jukebox"].end_song()
        self.advance_time_and_run(.1)
        self.assertTrue(rule.completed)
        self.assertEqual(self.player.modern_score_factor, 1)

    def test_order_up_delivery(self):
        rule = self.start_slot(7)
        self.hit_location("kitchen")
        self.assertIsNotNone(rule.destination)
        rule.on_location(rule.destination)
        self.assertTrue(rule.completed)

    def test_request_night_all_five(self):
        rule = self.start_slot(8)
        for loc in S.LOCATION_NAMES:
            rule.on_location(loc)
        self.assertTrue(rule.completed)

    def test_dance_floor_bumpers(self):
        rule = self.start_slot(9)
        start = self.player.score
        self.hit_and_release_switch("s_bottom_bumpers_13")
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.score - start, 5000)
        for _ in range(S.DANCE_HITS - 1):
            rule.on_bumper()
        self.assertTrue(rule.completed)

    def test_hit_me_dial_green_stops_without_freezing(self):
        rule = self.start_slot(10)
        self.mock_event("modern_lamps_frozen")
        self.advance_time_and_run(.6)
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(.1)
        self.assertFalse(rule.spinning)
        self.assertEventNotCalled("modern_lamps_frozen")
        for _ in range(3):
            rule.stop_dial()
            rule.on_location(rule.target)
        self.assertTrue(rule.completed)

    def test_hit_me_auto_stops(self):
        rule = self.start_slot(10)
        self.advance_time_and_run(S.DIAL_AUTO_STOP_MS / 1000 + .3)
        self.assertFalse(rule.spinning)

    def test_drain_ends_song_and_keeps_nickel_progress_rules(self):
        self.start_slot(3)
        self.drain_one_ball()
        self.advance_time_and_run(8)
        self.assertEqual(self.player.modern_song_active, 0)

    def test_each_mode_posts_its_callout_and_has_voice_lines(self):
        from custom_code.modern.songs import SLOT_RULES
        self.start_modern()
        pools = self.machine.modes["modern_callouts"].pools
        jukebox = self.machine.modes["modern_jukebox"]
        self.mock_event("modern_callout")
        for slot, rule in SLOT_RULES.items():
            self.assertIn(f"mc_mode_{rule.key}", pools)
            jukebox._start_song(jukebox.slots[slot - 1][1][0])
            self.advance_time_and_run(.2)
            self.assertEqual(self._last_event_kwargs["modern_callout"]["pool"], f"mc_mode_{rule.key}")
            jukebox.end_song()
            self.advance_time_and_run(.1)
