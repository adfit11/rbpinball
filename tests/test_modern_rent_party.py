"""Modern guest list, Gate Crasher locks and Rent Party multiball."""

from custom_code.modern import settings as S
from tests.modern_helpers import ModernTestCase


class TestModernRentParty(ModernTestCase):

    @property
    def party(self):
        return self.machine.modes["modern_rent_party"]

    @property
    def lock(self):
        return self.machine.ball_devices["bd_classic_subway_lock"]

    def fill_guest_list(self):
        for guest in S.GUESTS[:S.GUESTS_TO_FILL]:
            self.party._guest(guest)
        self.advance_time_and_run(.1)
        self.assertEqual(self.player.modern_lock_lit, 1)

    def lock_ball(self, crater=2):
        self.shoot_crater(crater)
        self.hit_and_release_switch("s_subway_lock_10")
        self.advance_time_and_run(5)

    def test_guest_arrives_once(self):
        self.start_modern()
        self.player.modern_nickel = 1
        self.hit_location("bandstand")
        self.assertEqual(self.party.guests(), ["bandstand"])
        self.hit_location("bandstand")
        self.assertEqual(self.party.guests(), ["bandstand"])

    def test_bank_counts_as_guest_and_list_resets_at_drain(self):
        self.start_modern()
        self.post_event_with_params("modern_bank_completed", bank="top_bank")
        self.advance_time_and_run(.1)
        self.assertEqual(self.party.guests(), ["top_bank"])
        self.fill_guest_list()
        self.drain_one_ball()
        self.advance_time_and_run(8)
        self.assertEqual(self.player.modern_guests, 0)
        self.assertEqual(self.player.modern_lock_lit, 0)

    def test_unlit_crater_locks_while_lock_is_lit(self):
        self.start_modern()
        self.fill_guest_list()
        self.mock_event("modern_ball_locked")
        targets = self.machine.modes["modern_targets"]
        switch = targets.CRATER_SWITCHES[0]
        targets.crater_index = 4  # only crater 4 is lit
        self.hit_and_release_switch(switch)
        self.hit_switch_and_run("s_subway_lock_10", 5)
        self.assertEventCalled("modern_ball_locked")
        self.assertEqual(self.lock.balls, 1)
        self.assertEqual(self.player.modern_locked_balls, 1)
        self.assertEqual(self.machine.game.balls_in_play, 1)

    def test_three_locks_start_rent_party_and_jackpots(self):
        self.start_modern()
        self.fill_guest_list()
        for _ in range(2):
            self.lock_ball()
            self.advance_time_and_run(3)
        self.mock_event("modern_rent_party_started")
        self.mock_event("modern_rent_party_build_up")
        self.lock_ball()
        self.advance_time_and_run(5)
        self.assertEventCalled("modern_rent_party_build_up")
        self.assertEventNotCalled("modern_rent_party_started")
        self.assertEqual(self.lock.balls, 3)  # every ball waits in the back room during the build-up
        self.advance_time_and_run(S.RENT_PARTY_BUILD_UP_MS / 1000)
        self.assertEventCalled("modern_rent_party_started")
        self.assertFalse(self._last_event_kwargs["modern_rent_party_started"]["gate_crasher"])
        self.assertEqual(self.machine.game.balls_in_play, 3)
        start = self.player.score
        for _ in range(3):
            self.party._crater(crater=1, lit=True)
        self.assertEqual(self.player.score - start, 250_000 + 300_000 + 350_000)
        self.assertTrue(self.party.super_lit)
        start = self.player.score
        self.party._location("bar")
        self.assertEqual(self.player.score - start, S.SUPER_JACKPOT)

    def test_jukebox_closed_during_rent_party_and_end_lights_extra_ball(self):
        self.start_modern()
        self.party.multiball = True
        self.mock_event("modern_light_extra_ball")
        self.post_event("multiball_modern_rent_party_ended", .1)
        self.assertEventCalled("modern_light_extra_ball")
        self.assertFalse(self.party.multiball)

    def test_gate_crasher_steals_locks(self):
        self.start_modern(players=2)
        self.fill_guest_list()
        self.lock_ball()
        self.advance_time_and_run(3)
        self.lock_ball()
        self.advance_time_and_run(3)
        self.assertEqual(self.lock.balls, 2)
        self.drain_one_ball()
        self.advance_time_and_run(10)
        self.assertEqual(self.machine.game.player.number, 2)
        self.assertEqual(self.player.modern_locked_balls, 2)
        self.fill_guest_list()
        self.mock_event("modern_gate_crasher")
        self.lock_ball()
        self.advance_time_and_run(5 + S.RENT_PARTY_BUILD_UP_MS / 1000)
        self.assertEventCalled("modern_gate_crasher")
        self.assertEqual(self.machine.game.balls_in_play, 3)

    def test_lock_and_nickel_together(self):
        self.start_modern()
        self.fill_guest_list()
        self.give_nickel()
        jukebox = self.machine.modes["modern_jukebox"]
        self.mock_event("modern_nickel_spent")
        self.lock_ball()
        self.assertEqual(self.lock.balls, 1)
        self.assertEqual(self.machine.ball_holds["modern_jukebox"].balls_held, 0)
        self.assertFalse(jukebox.selector_open)
        self.assertEventNotCalled("modern_nickel_spent")
        self.assertEqual(self.player.modern_nickel, 1)

    def test_tilt_during_build_up_releases_the_back_room(self):
        self.start_modern()
        self.fill_guest_list()
        for _ in range(3):
            self.lock_ball()
            self.advance_time_and_run(3)
        self.assertEqual(self.lock.balls, 3)
        for _ in range(S.WARNINGS_TO_TILT + 1):
            self.hit_and_release_switch("s_tilt_46")
            self.advance_time_and_run(1.5)
        self.advance_time_and_run(5)
        self.assertEqual(self.lock.balls, 0)
        for _ in range(3):
            self.drain_one_ball()
            self.advance_time_and_run(4)
        self.advance_time_and_run(10)
        self.assertBallNumber(2)
        self.assertEqual(self.machine.playfield.balls, 1)
