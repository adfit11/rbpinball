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
