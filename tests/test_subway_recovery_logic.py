"""Safety invariants for the isolated subway recovery logic."""

import unittest

from custom_code.subway_recovery import SubwayRecovery, SubwayReleaseInterlock, SubwayRecoveryRunner


class TestSubwayRecovery(unittest.TestCase):
    def test_kicker_is_cleared_before_releasing_a_locked_ball(self):
        recovery = SubwayRecovery(settle=.1)
        self.assertIsNone(recovery.update(0, True, True))
        self.assertEqual(recovery.update(.11, True, True), "kick")
        self.assertIsNone(recovery.update(.2, True, True))
        self.assertIsNone(recovery.update(.3, True, False))
        self.assertEqual(recovery.update(.41, True, False), "release")
        self.assertIsNone(recovery.update(.5, True, False))
        self.assertIsNone(recovery.update(.6, True, True))
        self.assertEqual(recovery.update(.71, True, True), "kick")

    def test_release_does_not_repeat_on_missing_ball(self):
        recovery = SubwayRecovery(settle=.1, timeout=1)
        recovery.update(0, True, False)
        self.assertEqual(recovery.update(.11, True, False), "release")
        self.assertIsNone(recovery.update(.9, True, False))
        self.assertEqual(recovery.update(1.12, True, False), "failed")
        self.assertIsNone(recovery.update(5, True, False))

    def test_blocked_kicker_stops_without_release(self):
        recovery = SubwayRecovery(settle=.1, timeout=1)
        recovery.update(0, True, True)
        self.assertEqual(recovery.update(.11, True, True), "kick")
        self.assertEqual(recovery.update(1.12, True, True), "failed")
        self.assertIsNone(recovery.update(2, True, True))

    def test_empty_and_three_ball_limit(self):
        empty = SubwayRecovery(settle=.1)
        empty.update(0, False, False)
        self.assertEqual(empty.update(.11, False, False), "done")
        full = SubwayRecovery(settle=.1)
        full.released = 3
        full.update(0, True, False)
        self.assertEqual(full.update(.11, True, False), "failed")

    def test_three_balls_are_released_and_kicked_sequentially(self):
        recovery = SubwayRecovery(settle=.1)
        now = 0.0
        recovery.update(now, True, False)
        for index in range(3):
            now += .11
            self.assertEqual(recovery.update(now, True, False), "release")
            now += .1
            self.assertIsNone(recovery.update(now, True, True))
            now += .11
            self.assertEqual(recovery.update(now, True, True), "kick")
            now += .1
            self.assertIsNone(recovery.update(now, index < 2, False))
        self.assertEqual(recovery.update(now + .11, False, False), "done")

    def test_transient_empty_kicker_does_not_allow_release(self):
        recovery = SubwayRecovery(settle=.1)
        recovery.update(0, True, True)
        recovery.update(.05, True, False)
        recovery.update(.09, True, True)
        self.assertIsNone(recovery.update(.15, True, True))
        self.assertEqual(recovery.update(.2, True, True), "kick")


class TestSubwayReleaseInterlock(unittest.TestCase):
    def test_blocks_occupied_kicker_and_overlapping_requests(self):
        guard = SubwayReleaseInterlock(timeout=1, clear_settle=.25)
        self.assertFalse(guard.request(0, True))
        self.assertTrue(guard.request(.1, False))
        self.assertFalse(guard.request(.2, False))
        self.assertEqual(guard.observe(.3, True), "waiting_for_clear")
        self.assertFalse(guard.request(.4, True))
        self.assertEqual(guard.observe(.5, False), "waiting_for_clear")
        self.assertFalse(guard.request(.6, False))
        self.assertEqual(guard.observe(.8, False), "ready")
        self.assertTrue(guard.request(.9, False))

    def test_kicker_bounce_does_not_rearm_the_release(self):
        guard = SubwayReleaseInterlock(timeout=2, clear_settle=.25)
        self.assertTrue(guard.request(0, False))
        guard.observe(.1, True)
        guard.observe(.2, False)
        guard.observe(.3, True)
        guard.observe(.4, False)
        self.assertEqual(guard.observe(.6, False), "waiting_for_clear")
        self.assertFalse(guard.request(.6, False))
        self.assertEqual(guard.observe(.7, False), "ready")

    def test_timeout_latches_failure_and_rejects_retries(self):
        guard = SubwayReleaseInterlock(timeout=1)
        self.assertTrue(guard.request(0, False))
        self.assertEqual(guard.observe(1, False), "failed")
        self.assertFalse(guard.request(2, False))
        self.assertEqual(guard.observe(3, True), "failed")


class TestSubwayRecoveryRunner(unittest.TestCase):
    def test_three_balls_are_dispatched_only_in_order(self):
        class Owner:
            def __init__(self):
                self.actions = []

            def request_release(self):
                self.actions.append("release")
                return True

            def request_kick(self):
                self.actions.append("kick")
                return True

        owner = Owner()
        runner = SubwayRecoveryRunner(owner, settle=.1)
        runner.update(0, True, True)
        self.assertEqual(runner.update(.11, True, True), "kick")
        runner.update(.2, True, False)
        self.assertEqual(runner.update(.31, True, False), "release")
        runner.update(.4, True, True)
        self.assertEqual(runner.update(.51, True, True), "kick")
        runner.update(.6, True, False)
        self.assertEqual(runner.update(.71, True, False), "release")
        runner.update(.8, False, True)
        self.assertEqual(runner.update(.91, False, True), "kick")
        runner.update(1.0, False, False)
        self.assertEqual(runner.update(1.11, False, False), "done")
        self.assertEqual(owner.actions, ["kick", "release", "kick", "release", "kick"])

    def test_rejected_release_stops_without_kicking(self):
        class Owner:
            def request_release(self):
                return False

            def request_kick(self):
                raise AssertionError("Kicker must not be fired")

        runner = SubwayRecoveryRunner(Owner(), settle=.1)
        runner.update(0, True, False)
        self.assertEqual(runner.update(.11, True, False), "failed")
        self.assertEqual(runner.sequence.reason, "Subway release command was rejected")
        self.assertIsNone(runner.update(5, True, True))

    def test_kicker_that_fails_to_clear_latches_failure(self):
        guard = SubwayReleaseInterlock(timeout=1)
        self.assertTrue(guard.request(0, False))
        self.assertEqual(guard.observe(.2, True), "waiting_for_clear")
        self.assertEqual(guard.observe(1.2, True), "failed")
        self.assertFalse(guard.request(2, False))


if __name__ == "__main__":
    unittest.main()
