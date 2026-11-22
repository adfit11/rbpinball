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

    def test_songs_are_not_introduced_but_mode_instructions_play(self):
        voices = []
        self.machine.events.add_handler("modern_voice", lambda **kwargs: voices.append(kwargs))
        self.start_slot(1)
        pools = [v["pool"] for v in voices]
        self.assertNotIn("mc_song_intro", pools)
        self.assertIn("mc_mode_hurry_up", pools)

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

    def test_ladder_rung_shows_the_next_value(self):
        rule = self.start_slot(2)
        overlays = []
        self.machine.events.add_handler("modern_overlay", lambda **kwargs: overlays.append(kwargs))
        self.mock_event("modern_song_shot")
        self.hit_location("kitchen")
        self.assertEventCalled("modern_song_shot")
        self.assertIn(("RUNG 1!", "75,000  •  Next 150,000"), [(o["title"], o["subtitle"]) for o in overlays])
        self.assertEqual(rule.status(), "LADDER  RUNG 1 / 4  •  NEXT 150K AT THE KITCHEN")

    def test_full_length_songs_are_capped_at_60_seconds(self):
        from unittest.mock import patch
        with patch("custom_code.modern.catalogue.mp3_length_ms", return_value=180_000):
            self.start_slot(2)
        jukebox = self.machine.modes["modern_jukebox"]
        self.assertLessEqual(jukebox.song_remaining(), S.ROUND_MS)
        self.assertGreater(jukebox.song_remaining(), S.JACKPOT_ROUND_MS)
        self.advance_time_and_run(S.ROUND_MS / 1000 + 1)
        self.assertIsNone(jukebox.song)

    def test_mode_shot_bursts_lamps_one_to_ten(self):
        rule = self.start_slot(5)
        rule.on_crater(1, False)
        self.advance_time_and_run(.3)
        self.assertLightColor("l_xxx_38", "white")
        self.assertLightColor("l_xxx_42", "black")
        self.advance_time_and_run(.3)
        self.assertLightColor("l_xxx_42", "white")
        self.advance_time_and_run(1)
        self.assertLightColor("l_xxx_42", "black")
        self.assertLightColor("l_xxx_33", "white")  # the song count shows again

    def test_build_and_collect_pot(self):
        rule = self.start_slot(3)
        self.mock_event("modern_pot_spin")
        for _ in range(3):
            self.hit_and_release_switch("s_spinner_44")
            self.advance_time_and_run(.05)
        self.assertEqual(rule.pot, S.POT_START * 3 + S.POT_STEP * 3)
        self.assertEventCalledWith("modern_pot_spin", pot=rule.pot, gain=S.POT_START + 2 * S.POT_STEP)
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

    def test_jukebox_jackpot_celebrates_each_hit(self):
        self.start_slot(5)
        self.mock_event("modern_song_jackpot")
        callouts = []
        self.machine.events.add_handler("modern_callout", lambda pool, **kwargs: callouts.append(pool))
        self.shoot_crater(3)
        self.assertEventCalledWith("modern_song_jackpot", crater=3, value=S.JACKPOT_VALUES[2], count=1)
        self.assertIn("mc_song_jackpot", callouts)

    def test_jukebox_jackpot_round_lasts_45_seconds(self):
        self.start_slot(5)
        jukebox = self.machine.modes["modern_jukebox"]
        self.mock_event("modern_song_started")
        self.assertLessEqual(jukebox.song_remaining(), S.JACKPOT_ROUND_MS)
        self.mock_event("modern_song_failed")
        self.advance_time_and_run(S.JACKPOT_ROUND_MS / 1000 - 1)
        self.assertIsNotNone(jukebox.song)
        self.advance_time_and_run(1.5)
        self.assertIsNone(jukebox.song)
        self.assertEventCalled("modern_song_failed")

    def test_jukebox_jackpot_ends_on_the_third_jackpot(self):
        rule = self.start_slot(5)
        for crater in (1, 2, 3):
            rule.on_crater(crater, False)
            self.advance_time_and_run(.1)
        self.assertTrue(rule.completed)
        self.assertIsNone(self.machine.modes["modern_jukebox"].song)
        self.assertIsNone(self.machine.modes["modern_songs"].rule)

    def test_jukebox_jackpot_status_shows_each_crater_value(self):
        rule = self.start_slot(5)
        rule.on_crater(4, False)
        self.assertIn("1: 175K", rule.status())
        self.assertIn("4: 325K", rule.status())

    def test_party_time_doubles_and_pays_last_dance(self):
        self.mock_event("modern_party_time_lights")
        self.mock_event("modern_party_time_lights_stop")
        rule = self.start_slot(6)
        self.assertEventCalled("modern_party_time_lights")
        seen = set()
        for _ in range(70):
            self.advance_time_and_run(.1)
            seen.add(self.machine.lights["l_xxx_47"].get_color().name)
        self.assertGreaterEqual(len(seen), 2)  # the Bar lamp is part of the moving show
        self.assertEqual(self.player.modern_ball_saver_ready, 1)
        start = self.player.score
        self.hit_and_release_switch("s_top_bumpers_35")
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.score - start, 2000)
        self.machine.modes["modern_jukebox"].end_song()
        self.advance_time_and_run(.1)
        self.assertTrue(rule.completed)
        self.assertEqual(self.player.modern_score_factor, 1)
        self.assertEventCalled("modern_party_time_lights_stop")

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

    def test_completing_ladder_ends_the_song(self):
        self.start_slot(2)
        for _ in range(4):
            self.hit_location("kitchen")
        self.assertIsNone(self.machine.modes["modern_jukebox"].song)

    def test_cold_order_fails_and_ends_the_song(self):
        rule = self.start_slot(7)
        self.mock_event("modern_song_failed")
        self.hit_location("kitchen")
        self.assertIsNotNone(rule.destination)
        self.advance_time_and_run(S.ORDER_MS / 1000 + 1)
        self.assertEventCalled("modern_song_failed")
        self.assertIsNone(self.machine.modes["modern_jukebox"].song)

    def test_ball_hold_pauses_the_hurry_up(self):
        rule = self.start_slot(1)
        self.post_event("modern_song_paused", .1)
        value = rule.value()
        self.advance_time_and_run(S.HURRY_MS / 1000 + 2)
        self.assertEqual(rule.value(), value)
        self.assertFalse(rule.completed)
        self.assertIsNotNone(self.machine.modes["modern_songs"].rule)
        self.post_event("modern_song_resumed", .1)
        self.advance_time_and_run(S.HURRY_MS / 1000 + 1)
        self.assertIsNone(self.machine.modes["modern_songs"].rule)

    def test_jukebox_jackpot_flashes_all_craters(self):
        from custom_code.modern.lamps import FLASH, director
        self.start_slot(5)
        for light in S.CRATER_LAMPS:
            self.assertEqual(director(self.machine).state(light), FLASH)

    def test_kitchen_lamp_flashes_as_a_target_but_is_solid_while_extra_ball_is_lit(self):
        from custom_code.modern.lamps import FLASH, SOLID, director
        self.start_slot(2)
        lamps = director(self.machine)
        self.assertEqual(lamps.state(S.EXTRA_BALL_LAMP), FLASH)
        self.post_event("modern_light_extra_ball", .1)
        self.assertEqual(lamps.state(S.EXTRA_BALL_LAMP), SOLID)
        for _ in range(4):
            self.advance_time_and_run(S.FLASH_MS / 1000)
            self.assertTrue(lamps.shown[S.EXTRA_BALL_LAMP])

    def test_next_song_is_not_frozen_by_a_hold_left_from_the_last(self):
        self.start_slot(2)
        self.post_event("modern_song_paused", .1)
        self.machine.modes["modern_jukebox"].end_song(reason="completed")
        self.advance_time_and_run(.1)
        self.start_slot(1)
        self.assertIsNone(self.machine.modes["modern_songs"].paused_at)
        self.advance_time_and_run(S.HURRY_MS / 1000 + 2)
        self.assertIsNone(self.machine.modes["modern_songs"].rule)
