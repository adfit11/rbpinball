"""Interlock adapter tests with the hardware pulse mocked."""

import asyncio
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from custom_code.subway_ejector import InterlockedSubwayEjector
from custom_code.subway_kicker_ejector import GuardedSubwayKicker
from custom_code.subway_startup import SubwayStartupClear
from mpf.tests.MpfGameTestCase import MpfGameTestCase
from tests.test_classic_subway import TestClassicSubway


class TestSubwayEjector(IsolatedAsyncioTestCase):
    def setUp(self):
        self.now = 0.0
        self.kicker = False
        self.lock = True
        self.lock_switch = object()
        self.kicker_switch = object()
        switches = SimpleNamespace(
            is_active=lambda switch: (self.kicker if switch is self.kicker_switch
                                      else self.lock if switch is self.lock_switch else False),
            is_inactive=lambda switch, ms: not self.kicker,
            add_switch_handler=Mock())
        clock = SimpleNamespace(get_time=lambda: self.now,
                                loop=SimpleNamespace(call_later=Mock(return_value=Mock())))
        self.machine = SimpleNamespace(switch_controller=switches, clock=clock,
                                       switches={"s_subway_kicker_0": self.kicker_switch,
                                                 "s_subway_lock_10": self.lock_switch,
                                                 "s_trough_3_20": object()},
                                       game=None,
                                       modes={},
                                       events=SimpleNamespace(post=Mock(), add_handler=Mock()))
        self.device = SimpleNamespace(log=SimpleNamespace(error=Mock(), warning=Mock()))

        def initialise(instance, config, ball_device, machine):
            instance.config = config
            instance.ball_device = ball_device
            instance.machine = machine

        with patch("custom_code.subway_ejector.PulseCoilEjector.__init__", initialise):
            self.ejector = InterlockedSubwayEjector({}, self.device, self.machine)

    async def test_only_one_pulse_until_kicker_arrives_and_clears(self):
        pulse = AsyncMock()
        with patch("custom_code.subway_ejector.PulseCoilEjector.eject_one_ball", pulse):
            self.kicker = True
            await self.ejector.eject_one_ball(False, 1, 1)
            pulse.assert_not_awaited()
            self.kicker = False
            await self.ejector.eject_one_ball(False, 1, 1)
            await self.ejector.eject_one_ball(False, 2, 1)
            self.assertEqual(pulse.await_count, 1)
            self.kicker = True
            self.ejector._observe()
            self.kicker = False
            self.now = .1
            self.ejector._observe()
            self.now = .7
            self.ejector._observe()
            await self.ejector.eject_one_ball(False, 1, 1)
            self.assertEqual(pulse.await_count, 2)

    async def test_timeout_and_ball_search_never_pulse(self):
        pulse = AsyncMock()
        with patch("custom_code.subway_ejector.PulseCoilEjector.eject_one_ball", pulse):
            await self.ejector.eject_one_ball(False, 1, 1)
            self.now = 3.1
            self.ejector._observe()
            await self.ejector.eject_one_ball(False, 2, 1)
            self.assertFalse(self.ejector.ball_search(3, 1))
            self.assertEqual(pulse.await_count, 1)
            self.machine.events.post.assert_any_call(
                "subway_release_interlock_failed", reason="Released ball did not reach the kicker")

    async def test_empty_subway_rejects_a_stale_mpf_request(self):
        pulse = AsyncMock()
        self.lock = False
        with patch("custom_code.subway_ejector.PulseCoilEjector.eject_one_ball", pulse):
            await self.ejector.eject_one_ball(False, 1, 1)
            self.assertFalse(self.ejector.request_recovery_release())
            pulse.assert_not_awaited()

    async def test_recovery_and_automatic_release_share_the_reservation(self):
        pulse = AsyncMock()
        self.machine.clock.loop.create_task = asyncio.create_task
        with patch("custom_code.subway_ejector.PulseCoilEjector.eject_one_ball", pulse):
            self.assertTrue(self.ejector.request_recovery_release())
            await self.ejector.eject_one_ball(False, 1, 1)
            await asyncio.sleep(0)
            self.assertEqual(pulse.await_count, 1)
            self.assertFalse(self.ejector.request_recovery_release())


class TestSubwayEjectorMpf(MpfGameTestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.machine_config_patches["ball_devices"] = {
            "bd_classic_subway_lock": {
                "ejector": {"class": "custom_code.subway_ejector.InterlockedSubwayEjector"}
            },
            "bd_classic_subway_kicker": {
                "ejector": {"class": "custom_code.subway_kicker_ejector.GuardedSubwayKicker"}
            },
        }

    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_mpf_loads_the_interlocked_ejector(self):
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        self.assertIsInstance(device.ejector, InterlockedSubwayEjector)
        self.assertFalse(device.ejector.ball_search(3, 1))
        self.assertIsInstance(self.machine.ball_devices["bd_classic_subway_kicker"].ejector,
                              GuardedSubwayKicker)

    def test_attract_waits_for_startup_clear_before_requesting_game(self):
        attract = self.machine.modes["attract"]
        self.assertIsNotNone(attract.subway_startup)
        self.assertEqual(attract.subway_startup.status, "running")
        self.hit_and_release_switch("s_start_47")
        self.mock_event("request_to_start_game")
        self.hit_and_release_switch("s_start_47")
        self.assertEventNotCalled("request_to_start_game")
        self.advance_time_and_run(1.2)
        self.assertEqual(attract.subway_startup.status, "done")
        self.assertEventCalled("request_to_start_game", 1)

    def test_virtual_mpf_blocks_occupied_kicker_and_repeat(self):
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        ejector = device.ejector
        coil = self.machine.coils["c_subway_lock"]

        def request():
            self.machine.clock.loop.create_task(ejector.eject_one_ball(False, 1, 1))
            self.advance_time_and_run(.01)

        lock = self.machine.switches["s_subway_lock_10"]
        controller = self.machine.switch_controller
        original = type(controller).is_active
        def is_active(switch, *args, **kwargs):
            return True if switch is lock else original(controller, switch, *args, **kwargs)

        with patch.object(type(controller), "is_active", side_effect=is_active), \
                patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            self.hit_switch_and_run("s_subway_kicker_0", .01)
            request()
            pulse.assert_not_called()
            self.release_switch_and_run("s_subway_kicker_0", .6)
            request()
            self.assertEqual(pulse.call_count, 1)
            request()
            self.assertEqual(pulse.call_count, 1)
            self.hit_switch_and_run("s_subway_kicker_0", .01)
            self.release_switch_and_run("s_subway_kicker_0", .6)
            self.post_event("balldevice_bd_outhole_ball_eject_success")
            request()
            self.assertEqual(pulse.call_count, 2)

    def test_start_is_blocked_with_a_ball_or_pending_handoff(self):
        ejector = self.machine.ball_devices["bd_classic_subway_lock"].ejector
        self.assertTrue(ejector._allow_start())
        controller = self.machine.switch_controller
        lock = self.machine.switches["s_subway_lock_10"]
        kicker = self.machine.switches["s_subway_kicker_0"]
        with patch.object(type(controller), "is_active", side_effect=lambda switch: switch is lock):
            self.assertFalse(ejector._allow_start())
        with patch.object(type(controller), "is_active", side_effect=lambda switch: switch is kicker):
            self.assertFalse(ejector._allow_start())
        self.assertTrue(ejector._allow_start())
        self.assertTrue(ejector.guard.request(self.machine.clock.get_time(), False))
        self.assertFalse(ejector._allow_start())

    def test_start_is_blocked_when_ball_counts_are_inconsistent(self):
        lock_device = self.machine.ball_devices["bd_classic_subway_lock"]
        ejector = lock_device.ejector
        self.assertTrue(ejector._allow_start())
        self.machine.ball_controller.num_balls_known = 2
        self.assertFalse(ejector._allow_start())

    def test_phantom_ball_is_cleared_only_when_three_balls_are_home(self):
        startup = SubwayStartupClear(self.machine)
        self.advance_time_and_run(1.2)
        self.machine.ball_controller.num_balls_known = 4
        self.machine.playfield.balls = 1
        self.machine.playfield.available_balls = 1
        startup._reconcile_home_counts()
        self.assertEqual(self.machine.ball_controller.num_balls_known, 3)
        self.assertEqual(self.machine.playfield.balls, 0)
        self.assertEqual(self.machine.playfield.available_balls, 0)

    def test_phantom_ball_is_not_cleared_when_trough_not_full(self):
        startup = SubwayStartupClear(self.machine)
        self.machine.ball_controller.num_balls_known = 4
        self.machine.playfield.balls = 1
        self.release_switch_and_run("s_trough_1_40", 1.2)
        startup._reconcile_home_counts()
        self.assertEqual(self.machine.ball_controller.num_balls_known, 4)
        self.assertEqual(self.machine.playfield.balls, 1)

    def test_unexpected_lock_ball_cannot_fire_into_occupied_kicker(self):
        coil = self.machine.coils["c_subway_lock"]
        with patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            self.hit_switch_and_run("s_subway_kicker_0", .01)
            self.hit_and_release_switch("s_subway_lock_10")
            self.advance_time_and_run(.2)
            pulse.assert_not_called()

    def test_pregame_lock_switch_bounce_does_not_queue_phantom_ejects(self):
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        before = device.balls
        coil = self.machine.coils["c_subway_lock"]
        with patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            for _ in range(4):
                self.hit_switch_and_run("s_subway_lock_10", .03)
                self.release_switch_and_run("s_subway_lock_10", .03)
            self.advance_time_and_run(2.5)
            self.assertEqual(device.balls, before)
            pulse.assert_not_called()

    def test_kicker_reservation_prevents_automatic_and_recovery_double_kicks(self):
        kicker = self.machine.ball_devices["bd_classic_subway_kicker"].ejector
        coil = self.machine.coils["c_subway_kicker"]
        with patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            self.assertFalse(kicker.request_recovery_kick())
            self.hit_switch_and_run("s_subway_kicker_0", .01)
            self.assertTrue(kicker.request_recovery_kick())
            self.assertFalse(kicker.request_recovery_kick())
            self.machine.clock.loop.create_task(kicker.eject_one_ball(False, 1, 1))
            self.advance_time_and_run(.02)
            self.assertEqual(pulse.call_count, 1)
            self.assertFalse(kicker.ball_search(3, 1))

    def test_startup_runner_clears_one_ball_through_guarded_ejectors(self):
        controller = self.machine.switch_controller
        lock = self.machine.switches["s_subway_lock_10"]
        kicker = self.machine.switches["s_subway_kicker_0"]
        original = type(controller).is_active
        state = {"lock": True, "kicker": False}

        def is_active(switch, *args, **kwargs):
            if switch is lock:
                return state["lock"]
            if switch is kicker:
                return state["kicker"]
            return original(controller, switch, *args, **kwargs)

        release_coil = self.machine.coils["c_subway_lock"]
        kicker_coil = self.machine.coils["c_subway_kicker"]
        startup = SubwayStartupClear(self.machine)
        with patch.object(type(controller), "is_active", side_effect=is_active), \
                patch.object(release_coil, "pulse", wraps=release_coil.pulse) as release, \
                patch.object(kicker_coil, "pulse", wraps=kicker_coil.pulse) as kick:
            self.assertTrue(startup.start())
            self.advance_time_and_run(1.2)
            self.assertEqual(release.call_count, 1)
            self.assertEqual(kick.call_count, 0)
            state["kicker"] = True
            self.advance_time_and_run(1.2)
            self.assertEqual(release.call_count, 1)
            self.assertEqual(kick.call_count, 1)
            state["lock"] = False
            state["kicker"] = False
            self.post_event("balldevice_bd_outhole_ball_eject_success")
            self.advance_time_and_run(1.2)
            self.assertEqual(startup.status, "done")

    def test_startup_runner_handles_three_queued_balls_in_order(self):
        controller = self.machine.switch_controller
        lock = self.machine.switches["s_subway_lock_10"]
        kicker = self.machine.switches["s_subway_kicker_0"]
        original = type(controller).is_active
        state = {"lock": True, "kicker": False}

        def is_active(switch, *args, **kwargs):
            if switch is lock:
                return state["lock"]
            if switch is kicker:
                return state["kicker"]
            return original(controller, switch, *args, **kwargs)

        release_coil = self.machine.coils["c_subway_lock"]
        kicker_coil = self.machine.coils["c_subway_kicker"]
        startup = SubwayStartupClear(self.machine)
        with patch.object(type(controller), "is_active", side_effect=is_active), \
                patch.object(release_coil, "pulse", wraps=release_coil.pulse) as release, \
                patch.object(kicker_coil, "pulse", wraps=kicker_coil.pulse) as kick:
            self.assertTrue(startup.start())
            for count in range(1, 4):
                self.advance_time_and_run(1.2)
                self.assertEqual(release.call_count, count)
                self.assertEqual(kick.call_count, count - 1)
                state["kicker"] = True
                self.advance_time_and_run(1.2)
                self.assertEqual(kick.call_count, count)
                state["kicker"] = False
                state["lock"] = count < 3
                self.advance_time_and_run(5)
                self.assertEqual(release.call_count, count)
                self.post_event("balldevice_bd_outhole_ball_eject_success")
            self.advance_time_and_run(1.2)
            self.assertEqual(startup.status, "done")
            self.assertEqual(release.call_count, 3)
            self.assertEqual(kick.call_count, 3)

    def test_startup_stops_when_release_does_not_reach_kicker(self):
        controller = self.machine.switch_controller
        lock = self.machine.switches["s_subway_lock_10"]
        kicker = self.machine.switches["s_subway_kicker_0"]
        original = type(controller).is_active

        def is_active(switch, *args, **kwargs):
            if switch is lock:
                return True
            if switch is kicker:
                return False
            return original(controller, switch, *args, **kwargs)

        startup = SubwayStartupClear(self.machine)
        coil = self.machine.coils["c_subway_lock"]
        with patch.object(type(controller), "is_active", side_effect=is_active), \
                patch.object(coil, "pulse", wraps=coil.pulse) as release:
            startup.start()
            self.advance_time_and_run(5)
            self.assertEqual(startup.status, "failed")
            self.assertEqual(release.call_count, 1)
            self.assertEqual(startup.reason, "Released ball did not reach the kicker")

    def test_startup_stops_if_ball_never_reaches_trough(self):
        controller = self.machine.switch_controller
        lock = self.machine.switches["s_subway_lock_10"]
        kicker = self.machine.switches["s_subway_kicker_0"]
        original = type(controller).is_active
        state = {"kicker": False}

        def is_active(switch, *args, **kwargs):
            if switch is lock:
                return True
            if switch is kicker:
                return state["kicker"]
            return original(controller, switch, *args, **kwargs)

        startup = SubwayStartupClear(self.machine)
        coil = self.machine.coils["c_subway_lock"]
        with patch.object(type(controller), "is_active", side_effect=is_active), \
                patch.object(coil, "pulse", wraps=coil.pulse) as release:
            startup.start()
            self.advance_time_and_run(1.2)
            self.assertEqual(release.call_count, 1)
            state["kicker"] = True
            self.advance_time_and_run(1.2)
            state["kicker"] = False
            self.advance_time_and_run(61)
            self.assertEqual(release.call_count, 1)
            self.assertEqual(startup.status, "failed")
            self.assertIn("did not return", startup.reason)

    def test_empty_trough_reconciles_stale_full_count_and_accepts_drain(self):
        trough = self.machine.ball_devices["bd_trough"]
        outhole_coil = self.machine.coils["c_outhole"]
        self.assertEqual(trough.balls, 3)
        self.release_switch_and_run("s_trough_1_40", .01)
        self.release_switch_and_run("s_trough_2_30", 1.1)
        startup = SubwayStartupClear(self.machine)
        with patch.object(outhole_coil, "pulse", wraps=outhole_coil.pulse) as pulse:
            self.hit_switch_and_run("s_trough_3_20", .6)
            startup.start()
            self.advance_time_and_run(8)
            pulse.assert_called_once()
            self.assertLess(trough.balls, 3)
            self.assertNotEqual(startup.status, "done")

    def test_trough_reconciliation_requires_both_trough_switches_open(self):
        trough = self.machine.ball_devices["bd_trough"]
        self.release_switch_and_run("s_trough_1_40", 1.1)
        self.hit_switch_and_run("s_trough_3_20", .6)
        self.assertFalse(trough.ball_count_handler.counter.reconcile_empty_at_start())
        self.assertEqual(trough.balls, 3)


class TestSubwayBootClosed(MpfGameTestCase):
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.machine_config_patches["virtual_platform_start_active_switches"] = [
            "s_trough_1_40", "s_trough_2_30", "s_subway_lock_10"]
        self.machine_config_patches["ball_devices"] = {
            "bd_classic_subway_lock": {
                "ejector": {"class": "custom_code.subway_ejector.InterlockedSubwayEjector"},
                "counter": {"class": "custom_code.volcano_subway_counter.VolcanoSubwayCounter"}
            },
            "bd_classic_subway_kicker": {
                "ejector": {"class": "custom_code.subway_kicker_ejector.GuardedSubwayKicker"}
            },
        }

    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "config.yaml"

    def get_platform(self):
        return "smart_virtual"

    def test_a_closed_lock_switch_at_boot_does_not_permit_start(self):
        device = self.machine.ball_devices["bd_classic_subway_lock"]
        ejector = device.ejector
        self.assertFalse(ejector._allow_start())
        self.assertEqual(device.ball_count_handler.counter.count_balls_sync(), 1)

    def test_boot_counter_refuses_reconciliation_while_occupied(self):
        counter = self.machine.ball_devices["bd_classic_subway_lock"].ball_count_handler.counter
        with self.assertRaisesRegex(RuntimeError, "occupied"):
            counter.reconcile_empty_after_recovery()

    def test_unresolved_missing_ball_does_not_start_a_game(self):
        startup = self.machine.modes["attract"].subway_startup
        self.advance_time_and_run(5)
        self.assertNotEqual(startup.status, "done")
        self.assertFalse(self.machine.ball_devices["bd_classic_subway_lock"].ejector._allow_start())

    def test_boot_with_occupied_lock_releases_at_most_one_before_kicker_arrival(self):
        release = self.machine.ball_devices["bd_classic_subway_lock"].ejector
        coil = self.machine.coils["c_subway_lock"]
        with patch.object(coil, "pulse", wraps=coil.pulse) as pulse:
            self.advance_time_and_run(4.5)
            self.assertLessEqual(pulse.call_count, 1)
            self.assertNotEqual(self.machine.modes["attract"].subway_startup.status, "done")
            self.assertFalse(release._allow_start())


class TestClassicSubwayGuarded(TestClassicSubway):
    """Run existing Classic scenarios with the proposed hardware owners."""

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        self.machine_config_patches["ball_devices"] = {
            "bd_classic_subway_lock": {
                "ejector": {"class": "custom_code.subway_ejector.InterlockedSubwayEjector"},
                "counter": {"class": "custom_code.volcano_subway_counter.VolcanoSubwayCounter"},
            },
            "bd_classic_subway_kicker": {
                "ejector": {"class": "custom_code.subway_kicker_ejector.GuardedSubwayKicker"},
            },
        }


