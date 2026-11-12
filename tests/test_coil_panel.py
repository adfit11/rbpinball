"""Exercise real MPF device timing and diagnostic command boundaries virtually."""

from pathlib import Path
import tempfile
from unittest.mock import patch

from mpf.tests.MpfTestCase import MpfTestCase
from custom_code.coil_panel import CoilPanel


class TestCoilPanel(MpfTestCase):
    def get_machine_path(self):
        return str(Path(__file__).resolve().parents[1])

    def get_config_file(self):
        return "diagnostic_panel.yaml"

    def setUp(self):
        self.http_patch = patch.object(CoilPanel, "start_http")
        self.http_patch.start()
        self.addCleanup(self.http_patch.stop)
        super().setUp()
        self.panel = next(code for code in self.machine.custom_code if isinstance(code, CoilPanel))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.panel.results_path = Path(self.temp.name) / "results.json"

    def test_pulse_bounds_and_cooldown(self):
        coil = self.machine.coils["c_trough_release"].hw_driver
        with patch.object(type(coil), "enable", autospec=True) as enable, \
                patch.object(type(coil), "disable", autospec=True) as disable:
            self.panel.command({"action": "pulse", "name": "c_trough_release", "ms": 270})
            self.assertIs(coil, enable.call_args.args[0])
            self.advance_time_and_run(.26)
            disable.assert_not_called()
            self.advance_time_and_run(.02)
            self.assertIs(coil, disable.call_args.args[0])
            with self.assertRaises(ValueError):
                self.panel.command({"action": "pulse", "name": "c_outhole", "ms": 65})
        for name, duration in [("c_outhole", 5000), ("c_GGG", 30), ("c_outhole", True), ("c_outhole", -1)]:
            with self.assertRaises(ValueError):
                self.panel.command({"action": "pulse", "name": name, "ms": duration})

    def test_relay_times_out_and_all_off_cancels_it(self):
        relay = self.machine.digital_outputs["diagnostic_game_relay"]
        with patch.object(type(relay), "enable", autospec=True) as enable, \
                patch.object(type(relay), "disable", autospec=True) as disable:
            self.panel.command({"action": "relay_on"})
            enable.assert_called_once_with(relay)
            self.advance_time_and_run(9.9)
            disable.assert_not_called()
            self.advance_time_and_run(.2)
            disable.assert_called_once_with(relay)
            self.panel.command({"action": "relay_on"})
            self.panel.command({"action": "all_off"})
            self.assertEqual(0, self.panel.relay_until)
            self.assertNotIn("relay_off", self.panel.delay.delays)

    def test_observations_persist_and_switches_are_live(self):
        self.panel.command({"action": "result", "name": "c_outhole", "result": "working"})
        self.assertIn('"working"', self.panel.results_path.read_text())
        self.hit_switch_and_run("s_top_bumpers_35", .01)
        switch = next(s for s in self.panel.state()["switches"] if s["name"] == "s_top_bumpers_35")
        self.assertTrue(switch["active"])
        self.assertEqual(1, switch["hits"])
        self.panel.command({"action": "stop"})
        self.advance_time_and_run(.3)
        self.assertTrue(self.machine.stop_future.done())

    def test_only_mapped_lamps_can_be_toggled(self):
        lamps = self.panel.state()["lamps"]
        self.assertEqual([*range(3, 8), 10, 11, *range(17, 48)],
                         [int(lamp["output"]) for lamp in lamps])
        for name in ("l_diagnostic_08", "l_diagnostic_14", "diagnostic_game_relay"):
            with self.assertRaises(ValueError):
                self.panel.command({"action": "lamp_toggle", "name": name})

        name = "l_diagnostic_10"
        self.panel.command({"action": "lamp_toggle", "name": name})
        self.assertLightChannel(name, 255)
        self.assertLightChannel("l_diagnostic_11", 0)
        self.panel.command({"action": "lamp_toggle", "name": name})
        self.assertLightChannel(name, 0)

    def test_flash_starts_together_and_cancels_on_stop_or_all_off(self):
        for stop_action in ("lamps_flash_stop", "all_off"):
            state = self.panel.command({"action": "lamps_flash_start"})
            self.assertTrue(state["lamps_flashing"])
            self.assertTrue(all(lamp["on"] for lamp in state["lamps"]))
            for name in self.panel.lamps:
                self.assertLightChannel(name, 255)
            with self.assertRaises(ValueError):
                self.panel.command({"action": "lamp_toggle", "name": "l_diagnostic_03"})
            self.advance_time_and_run(.51)
            for name in self.panel.lamps:
                self.assertLightChannel(name, 0)
            self.advance_time_and_run(.5)
            for name in self.panel.lamps:
                self.assertLightChannel(name, 255)

            state = self.panel.command({"action": stop_action})
            self.assertFalse(state["lamps_flashing"])
            self.advance_time_and_run(1.1)
            for name in self.panel.lamps:
                self.assertLightChannel(name, 0)
