from unittest.mock import patch
"""Modern juke joint base rules against the real machine config."""

from custom_code.modern import catalogue, settings
from custom_code.modern.bonus import ovation
from custom_code.modern.callouts import load_script
from custom_code.modern.lamps import FLASH, STEADY, director
from tests.modern_helpers import ModernTestCase

CHILD_MODES = ("modern", "modern_targets", "modern_skill_shot", "modern_nickels", "modern_jukebox",
               "modern_subway", "modern_holes", "modern_ball_saver", "modern_callouts", "modern_display")


class TestModernStack(ModernTestCase):

    def test_modern_modes_run_only_in_modern(self):
        self.start_modern()
        for mode in CHILD_MODES:
            self.assertModeRunning(mode)
        self.assertModeNotRunning("classic")
        for old in ("base", "bumpers", "outlanes", "right_drops", "hurryup"):
            self.assertNotIn(old, self.machine.modes)

    def test_splash_holds_first_ball(self):
        self.mock_event("balldevice_bd_trough_ejecting_ball")
        self.start_modern(skip_splash=False)
        self.assertEventNotCalled("balldevice_bd_trough_ejecting_ball")
        self.advance_time_and_run(settings.SPLASH_MS / 1000 + 1)
        self.assertEventCalled("balldevice_bd_trough_ejecting_ball")

    def test_scores_apply_song_multiplier(self):
        self.start_modern()
        start = self.player.score
        self.hit_and_release_switch("s_top_bumpers_35")
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.score - start, 1000)
        self.player.modern_song_multiplier = 3
        self.player.modern_nickel = 1  # a held nickel pauses the hunt, so no nickel points
        start = self.player.score
        self.hit_and_release_switch("s_spot_target_36")
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.score - start, 30000)

    def test_spinner_bandstand_counts_once_per_burst(self):
        self.start_modern()
        self.mock_event("modern_location_hit")
        self.advance_time_and_run(1.1)
        for _ in range(5):
            self.hit_and_release_switch("s_spinner_44")
            self.advance_time_and_run(.05)
        self.assertEventCalled("modern_location_hit", 1)


class TestModernNickels(ModernTestCase):

    def test_kitchen_is_never_the_target_while_extra_ball_is_lit(self):
        with patch("custom_code.modern.nickels.random.choice", lambda c: "kitchen" if "kitchen" in c else c[0]):
            self.start_modern()
            self.assertEqual(self.player.modern_nickel_target, "kitchen")
            self.machine.modes["modern_holes"]._light_extra_ball()
            self.advance_time_and_run(.1)
            self.assertNotEqual(self.player.modern_nickel_target, "kitchen")
            self.machine.modes["modern_nickels"]._direct()
            self.assertNotEqual(self.player.modern_nickel_target, "kitchen")

    def test_first_nickel_target_flashes_from_ball_start(self):
        with patch("custom_code.modern.nickels.random.choice", lambda c: "bar" if "bar" in c else c[0]):
            self.start_modern()
        light = self.machine.lights["l_xxx_47"]
        seen = set()
        for _ in range(8):
            self.advance_time_and_run(.125)
            seen.add(light.get_color().rgb[0] > 0)
        self.assertEqual(seen, {True, False})

    def test_directed_location_awards_nickel_and_cost_climbs(self):
        self.start_modern()
        nickels = self.machine.modes["modern_nickels"]
        self.assertIn(self.player.modern_nickel_target, settings.LOCATION_NAMES)
        self.assertEqual(nickels.cost(), 1)
        self.mock_event("modern_nickel_awarded")
        self.hit_location(self.player.modern_nickel_target)
        self.assertEventCalled("modern_nickel_awarded")
        self.assertEqual(self.player.modern_nickel, 1)
        self.assertEqual(self.player.modern_nickel_target, "")
        self.assertEqual(nickels.cost(), 2)

    def test_wrong_location_refuses_and_keeps_target(self):
        self.start_modern()
        target = self.player.modern_nickel_target
        wrong = next(l for l in ("coat_check", "back_door", "bandstand") if l != target)
        self.mock_event("modern_nickel_refused")
        self.mock_event("modern_voice")
        self.hit_location(wrong)
        self.assertEventCalled("modern_nickel_refused")
        self.assertEventCalled("modern_voice")
        self.assertEqual(self.player.modern_nickel_target, target)
        self.assertEqual(self.player.modern_nickel, 0)

    def test_cost_cycle_doubles_value(self):
        self.start_modern()
        self.player.modern_nickel_step = 4
        self.player.modern_nickel_progress = 4
        start = self.player.score
        self.hit_location(self.player.modern_nickel_target)
        self.assertEqual(self.player.modern_nickel_step, 0)
        self.assertEqual(self.player.modern_nickel_cycle, 1)
        self.assertGreaterEqual(self.player.score - start, settings.SCORE_NICKEL)
        self.player.modern_nickel = 0
        self.post_event("modern_nickel_spent", .1)
        start = self.player.score
        self.hit_location(self.player.modern_nickel_target)
        self.assertGreaterEqual(self.player.score - start, settings.SCORE_NICKEL * 2)

    def test_floor_nickel_from_both_banks_keeps_cost(self):
        self.start_modern()
        cost = self.machine.modes["modern_nickels"].cost()
        self.mock_event("modern_nickel_awarded")
        for switch in self.machine.modes["modern_targets"].DROP_SWITCHES["top_bank"] + \
                self.machine.modes["modern_targets"].DROP_SWITCHES["right_bank"]:
            self.hit_switch_and_run(switch, .05)
        self.advance_time_and_run(.5)
        self.assertEventCalled("modern_nickel_awarded")
        self.assertEqual(self.player.modern_nickel, 1)
        self.assertEqual(self.machine.modes["modern_nickels"].cost(), cost)

    def test_nickel_resets_at_drain(self):
        self.start_modern()
        self.give_nickel()
        self.player.modern_nickel_progress = 1
        self.drain_one_ball()
        self.advance_time_and_run(8)
        self.assertBallNumber(2)
        self.assertEqual(self.player.modern_nickel, 0)
        self.assertEqual(self.player.modern_nickel_progress, 0)


class TestModernJukebox(ModernTestCase):

    def test_unlit_crater_without_nickel_kicks_back(self):
        self.start_modern()
        self.mock_event("modern_jukebox_no_nickel")
        self.mock_event("modern_selector_opened")
        self.shoot_crater(2)
        self.assertEventCalled("modern_jukebox_no_nickel")
        self.assertEventNotCalled("modern_selector_opened")

    def test_lit_crater_with_nickel_opens_selector_and_auto_picks(self):
        self.start_modern()
        self.give_nickel()
        self.mock_event("modern_selector_opened")
        self.mock_event("modern_song_started")
        self.shoot_crater(3)
        self.assertEventCalled("modern_selector_opened")
        self.assertEqual(self.player.modern_nickel, 0)
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(4)
        self.assertEqual(self.machine.ball_holds["modern_jukebox"].balls_held, 1)
        self.assertEventNotCalled("modern_song_started")
        self.advance_time_and_run(settings.SELECTOR_TIMEOUT_MS / 1000)
        self.assertEventCalled("modern_song_started")
        self.assertEqual(self.machine.ball_holds["modern_jukebox"].balls_held, 0)
        self.assertEqual(self.player.modern_songs_played, 1)
        self.assertEqual(self.player.modern_artists_played, 1)
        self.assertTrue(self.machine.modes["modern_jukebox"].song)

    def test_song_waits_for_the_subway_kicker(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        self.mock_event("modern_song_started")
        jukebox.chosen = jukebox.slots[0][1][0]
        jukebox._release_ball()
        self.advance_time_and_run(3)
        self.assertEventNotCalled("modern_song_started")
        self.assertIsNone(jukebox.song)
        jukebox._start_pending()  # balldevice_bd_classic_subway_kicker_ball_eject_success
        self.advance_time_and_run(.1)
        self.assertEventCalled("modern_song_started")
        self.assertIsNotNone(jukebox.song)
        self.assertIsNone(jukebox.pending_song)

    def test_multiplier_applies_while_ball_returns_and_drain_refunds_artist(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        self.player.modern_songs_played = settings.MULTIPLIER_EVERY - 1
        jukebox.selector_open, jukebox.highlight = True, 3
        jukebox._choose()
        jukebox._release_ball()
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.modern_song_multiplier, 2)
        self.assertTrue(jukebox.played(3))
        self.drain_one_ball()
        self.advance_time_and_run(8)
        self.assertFalse(jukebox.played(3))
        self.assertEqual(self.player.modern_songs_played, settings.MULTIPLIER_EVERY - 1)
        self.assertEqual(self.player.modern_song_multiplier, 1)

    def test_tap_moves_and_hold_selects(self):
        self.start_modern()
        self.give_nickel()
        self.player.modern_artists_played = 0b10  # slot 2 already played
        self.shoot_crater(4)
        jukebox = self.machine.modes["modern_jukebox"]
        self.assertEqual(jukebox.highlight, 0)
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(.1)
        self.assertEqual(jukebox.highlight, 2)
        self.mock_event("modern_artist_chosen")
        self.hit_switch_and_run("s_green_button_right_56", 2.2)
        self.release_switch_and_run("s_green_button_right_56", .1)
        self.assertEventCalled("modern_artist_chosen")
        self.assertEqual(self._last_event_kwargs["modern_artist_chosen"]["slot"], 3)

    def test_green_tap_freezes_cascade_when_unowned(self):
        self.start_modern()
        self.mock_event("modern_lamps_frozen")
        self.hit_and_release_switch("s_green_button_right_56")
        self.advance_time_and_run(.1)
        self.assertEventCalled("modern_lamps_frozen")

    def test_select_switch_is_remappable(self):
        self.machine.variables.set_machine_var("modern_select_switch", "s_flipper_left")
        self.start_modern()
        self.mock_event("modern_select")
        self.hit_and_release_switch("s_flipper_left")
        self.advance_time_and_run(.1)
        self.assertEventCalled("modern_select")

    def test_round_resets_after_all_ten(self):
        self.start_modern()
        self.give_nickel()
        self.player.modern_artists_played = (1 << 10) - 1
        self.player.modern_round_songs = 10
        self.shoot_crater(1)
        self.assertEqual(self.player.modern_artists_played, 0)
        self.assertEqual(self.player.modern_round_songs, 0)

    def test_song_progression_multiplier_extra_ball_and_special(self):
        self.start_modern()
        jukebox = self.machine.modes["modern_jukebox"]
        song = jukebox.slots[0][1][0]
        self.mock_event("modern_light_special")
        for count in range(1, 11):
            jukebox._start_song(song)
            jukebox.end_song()
            if count == 3:
                self.advance_time_and_run(.1)
                self.assertEqual(self.player.modern_extra_ball_lit, 1)
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.modern_song_multiplier, 3)
        self.assertEventCalled("modern_light_special")
        self.assertEqual(self.player.modern_special_state, 1)
        self.mock_event("modern_special_awarded")
        self.hit_location("bar")
        self.assertEventCalled("modern_special_awarded")
        self.assertEqual(self.player.modern_special_state, 2)

    def test_catalogue_files_exist_and_lengths_are_read(self):
        for _, songs in catalogue.load():
            for song in songs:
                path = catalogue.os.path.join(catalogue.ROOT, song.path)
                self.assertTrue(catalogue.os.path.exists(path), path)
                self.assertGreater(catalogue.mp3_length_ms(path, 0), 10000)


class TestModernBallFeatures(ModernTestCase):

    def test_drop_the_needle_scores_and_readies_saver(self):
        self.start_modern(skip_splash=False)
        self.hit_and_release_switch("s_start_47")
        self.advance_time_and_run(1.5)
        targets = self.machine.modes["modern_targets"]
        self.assertTrue(targets.skill_window)
        switch = targets.DROP_SWITCHES["top_bank"][targets.drop_index - 1]
        start = self.player.score
        self.mock_event("modern_drop_the_needle")
        self.hit_switch_and_run(switch, .1)
        self.assertEventCalled("modern_drop_the_needle")
        self.assertEqual(self.player.score - start, settings.SCORE_DROP + settings.SCORE_DROP_THE_NEEDLE)
        self.assertEqual(self.player.modern_ovation, 1)
        self.assertEqual(self.player.modern_ball_saver_ready, 1)
        self.mock_event("modern_ball_saved")
        self.hit_and_release_switch("s_outlane_left_6")
        self.advance_time_and_run(.1)
        self.assertEventCalled("modern_ball_saved")
        self.assertEqual(self.player.modern_ball_saver_ready, 0)

    def test_standing_ovation_caps_and_bonus_pays(self):
        self.start_modern()
        self.player.modern_songs_completed_ball = 5
        self.assertEqual(ovation(self.player), settings.MAX_OVATION)
        self.player.modern_songs_completed_ball = 1
        self.player.modern_bonus_bumpers = 10
        self.mock_event("modern_bonus_total")
        self.drain_one_ball()
        self.advance_time_and_run(8)
        self.assertEventCalled("modern_bonus_total")
        kwargs = self._last_event_kwargs["modern_bonus_total"]
        self.assertEqual(kwargs["ovation"], 2)
        self.assertEqual(kwargs["points"], kwargs["subtotal"] * 2)

    def test_extra_ball_collected_at_kitchen(self):
        self.start_modern()
        self.post_event("modern_light_extra_ball", .1)
        self.assertEqual(self.player.modern_extra_ball_lit, 1)
        self.hit_location("kitchen")
        self.assertEqual(self.player.extra_balls, 1)
        self.assertEqual(self.player.modern_extra_balls_earned, 1)

    def test_bar_and_kitchen_speak_when_the_nickel_hunt_is_quiet(self):
        self.start_modern()
        self.give_nickel()
        self.mock_event("modern_voice")
        for hole, staff in (("bar", "bartender"), ("kitchen", "cook")):
            self.hit_location(hole)
            self.assertEqual(self._last_event_kwargs["modern_voice"]["pool"], f"{staff}_held")

    def test_holes_leave_the_nickel_hunt_line_alone(self):
        self.start_modern()
        pools = []
        self.machine.events.add_handler("modern_voice", lambda pool, **kwargs: pools.append(pool))
        hole = "kitchen" if self.player.modern_nickel_target == "bar" else "bar"
        self.hit_location(hole)
        staff = "bartender" if hole == "bar" else "cook"
        self.assertIn(f"{staff}_refusal", pools)
        self.assertNotIn(f"{staff}_held", pools)

    def test_task_panel_guides_the_nickel_hunt_and_jukebox(self):
        self.mock_event("modern_task")
        self.start_modern()
        task = self._last_event_kwargs["modern_task"]
        self.assertEqual(task["title"], "GET A NICKEL")
        name = settings.LOCATIONS[self.player.modern_nickel_target][0].removeprefix("the ")
        self.assertIn(f"Visit the {name.upper()} (", task["detail"])
        self.give_nickel()
        self.advance_time_and_run(.1)
        self.assertEqual(self._last_event_kwargs["modern_task"]["title"], "PLAY THE JUKEBOX")

    def test_plain_virtual_kicker_clears_the_hole_switch(self):
        self.start_modern()
        platform = self.machine.default_platform
        with patch("custom_code.modern.holes.plain_virtual", return_value=True), \
                patch.object(platform, "virtual_remove_ball_from_device") as remove:
            self.hit_location("bar", wait_release=False)
            self.advance_time_and_run(2)
        remove.assert_any_call(ball_device="bd_classic_saucer")

    def test_drop_lamps_keep_cascading_and_dropped_targets_stay_lit(self):
        self.start_modern()
        targets = self.machine.modes["modern_targets"]
        lamps = director(self.machine)
        self.hit_switch_and_run("s_right_drop_2_11", .5)
        seen = set()
        for _ in range(20):
            self.advance_time_and_run(.25)
            seen.add(targets.drop_index)
            self.assertEqual(lamps.state("l_xxx_20"), STEADY)
        self.assertGreater(len(seen), 2)

    def test_lit_craters_stay_steady_while_holding_a_nickel(self):
        self.start_modern()
        self.give_nickel()
        lamps = director(self.machine)
        for _ in range(20):
            self.advance_time_and_run(.1)
            self.assertNotIn(FLASH, [lamps.state(l) for l in settings.CRATER_LAMPS])

    def test_simulator_monitor_shows_lit_lamps_amber(self):
        light = self.machine.lights["l_xxx_33"]
        light.color("white", priority=1000, key="test")
        self.advance_time_and_run(.1)
        self.assertEqual(light.get_monitorable_state()["color"], [255, 170, 0])
        light.remove_from_stack_by_key("test")
        light.color("black", priority=1000, key="test")
        self.advance_time_and_run(.1)
        self.assertEqual(light.get_monitorable_state()["color"], [0, 0, 0])

    def test_simulator_monitor_is_told_about_lamp_changes(self):
        light = self.machine.lights["l_xxx_46"]
        manager = type(self.machine.device_manager)
        with patch.object(manager, "notify_device_changes", autospec=True) as notify:
            light.color("white", priority=1000, key="test")
            self.advance_time_and_run(.1)
        self.assertIn((light, "color", [0, 0, 0], [255, 170, 0]), [c.args[1:] for c in notify.call_args_list])

    def test_one_warning_tilt_in_modern(self):
        self.start_modern()
        self.mock_event("tilt")
        self.hit_and_release_switch("s_tilt_46")
        self.advance_time_and_run(2)
        self.assertEventNotCalled("tilt")
        self.hit_and_release_switch("s_tilt_46")
        self.advance_time_and_run(.5)
        self.assertEventCalled("tilt")

    def test_callouts_never_repeat_last_line(self):
        self.start_modern()
        callouts = self.machine.modes["modern_callouts"]
        seen = []
        self.machine.events.add_handler("modern_voice", lambda **kwargs: seen.append(kwargs["text"]))
        for _ in range(10):
            self.post_event("modern_callout", .01)  # missing pool is ignored
            callouts._callout("mc_jukebox_open")
            self.advance_time_and_run(.01)
        self.assertTrue(all(a != b for a, b in zip(seen, seen[1:])))

    def test_every_voice_line_has_a_file(self):
        _, pools = load_script()
        for lines in pools.values():
            for line in lines:
                self.assertTrue(catalogue.os.path.exists(catalogue.os.path.join(catalogue.ROOT, line["path"])),
                                line["path"])
