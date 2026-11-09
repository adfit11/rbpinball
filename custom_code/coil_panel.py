"""Local browser controls; all hardware access stays on MPF's event loop."""

import concurrent.futures
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
import time

from mpf.core.custom_code import CustomCode


OUTPUTS = (
    ("c_subway_lock", "Subway release", 400),
    ("c_top_drops", "Top drop reset", 400),
    ("c_subway_kicker", "Subway kicker", 100),
    ("c_right_drops", "Right drop reset", 400),
    ("c_outhole", "Bottom outhole", 100),
    ("c_side_kicker_left", "Left / fire-pit kicker", 100),
    ("c_hole_kicker_top", "Top hole kicker", 100),
    ("c_trough_release", "Trough release", 400),
    ("c_skill_motor", "Motor relay", 1000),
    ("c_Replay_Knock", "Knocker", 100),
)
ALLOWED_HOSTS = {"127.0.0.1:8765", "localhost:8765"}


class CoilPanel(CustomCode):
    def on_load(self):
        self.server = None
        self.ready = False
        self.busy_until = 0
        self.relay_until = 0
        self.history = []
        self.switch_hits = {}
        self.last_hits = {}
        self.virtual = self.machine.default_platform.__class__.__module__.endswith("virtual")
        filename = "coil-panel-results-virtual.json" if self.virtual else "coil-panel-results.json"
        self.results_path = Path(self.machine.machine_path) / "data" / filename
        self.results = {}
        if self.results_path.exists():
            self.results = json.loads(self.results_path.read_text())
        self.machine.events.add_handler("init_done", self.start)
        self.machine.events.add_handler("shutdown", self.close)

    def start(self, **kwargs):
        self.relay_off()
        self.machine.switch_controller.add_monitor(self.switch_change)
        self.ready = True
        self.start_http()
        self.info_log("USB DIAGNOSTIC PANEL: http://127.0.0.1:8765 — outputs idle.")

    def switch_change(self, change):
        if change.state:
            self.switch_hits[change.name] = self.switch_hits.get(change.name, 0) + 1
            self.last_hits[change.name] = time.monotonic()

    def record(self, message):
        self.history.insert(0, {"time": time.strftime("%H:%M:%S"), "message": message})
        del self.history[40:]
        self.info_log("PANEL: %s", message)

    def state(self):
        coils = []
        for name, label, limit in OUTPUTS:
            coil = self.machine.coils[name]
            default = 250 if name == "c_skill_motor" else coil.get_and_verify_pulse_ms(None)
            coils.append({"name": name, "label": label, "output": coil.config["number"],
                          "default_ms": default, "max_ms": limit,
                          "result": self.results.get(name, "untested")})
        return {"ready": self.ready, "virtual": self.virtual,
                "busy": time.monotonic() < self.busy_until,
                "relay_seconds": max(0, round(self.relay_until - time.monotonic(), 1)),
                "coils": coils, "history": self.history,
                "switches": [{"name": switch.name, "number": switch.config["number"],
                              "active": bool(switch.state), "hits": self.switch_hits.get(switch.name, 0),
                              "recent": time.monotonic() - self.last_hits.get(switch.name, float('-inf')) < 2}
                             for switch in self.machine.switches.values()
                             if switch.config["platform"] != "virtual"]}

    def command(self, data):
        if not self.ready:
            raise ValueError("Diagnostic is stopping.")
        action = data.get("action")
        if action == "all_off":
            self.all_off()
        elif action == "relay_off":
            self.relay_off()
            self.record("L0 commanded OFF.")
        elif action == "relay_on":
            self.machine.digital_outputs["diagnostic_game_relay"].enable()
            self.relay_until = time.monotonic() + 10
            self.delay.reset(name="relay_off", ms=10000, callback=self.relay_off)
            self.record("L0 commanded ON for 10 seconds. Observe relay and test local switches.")
        elif action == "pulse":
            name = data.get("name")
            limits = {item[0]: item[2] for item in OUTPUTS}
            duration = data.get("ms")
            if name not in limits or type(duration) is not int or not 1 <= duration <= limits[name]:
                raise ValueError("Choose a listed output and a duration within its diagnostic range.")
            if time.monotonic() < self.busy_until:
                raise ValueError("Wait for the pulse and cooldown to finish.")
            self.machine.coils[name].pulse(pulse_ms=duration)
            self.busy_until = time.monotonic() + duration / 1000 + 2
            self.record(f"Output {self.machine.coils[name].config['number']}: {duration} ms requested; observe mechanism.")
        elif action == "result":
            name, result = data.get("name"), data.get("result")
            if name not in {item[0] for item in OUTPUTS} or result not in {"working", "weak", "no response", "untested"}:
                raise ValueError("Invalid result.")
            self.results[name] = result
            self.results_path.parent.mkdir(exist_ok=True)
            temporary = self.results_path.with_suffix(".tmp")
            temporary.write_text(json.dumps(self.results, indent=2) + "\n")
            temporary.replace(self.results_path)
        elif action == "stop":
            self.all_off()
            self.ready = False
            self.delay.add(ms=200, callback=self.machine.stop, reason="Diagnostic panel closed")
        else:
            raise ValueError("Unknown command.")
        return self.state()

    def relay_off(self):
        self.relay_until = 0
        self.delay.remove("relay_off")
        self.machine.digital_outputs["diagnostic_game_relay"].disable()

    def all_off(self):
        for name, _, _ in OUTPUTS:
            self.machine.coils[name].disable()
        self.relay_off()
        self.busy_until = time.monotonic() + 2
        self.record("All listed coil outputs and L0 commanded OFF.")

    def close(self, **kwargs):
        self.ready = False
        self.machine.switch_controller.remove_monitor(self.switch_change)
        self.all_off()
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def submit(self, callback):
        future = concurrent.futures.Future()

        def run():
            if not future.set_running_or_notify_cancel():
                return
            try:
                future.set_result(callback())
            except Exception as error:
                future.set_exception(error)

        self.machine.clock.loop.call_soon_threadsafe(run)
        try:
            return future.result(timeout=3)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise ValueError("MPF did not respond; check the terminal.") from None

    def start_http(self):
        panel = self
        token = secrets.token_hex(24)
        page = (Path(__file__).parent / "coil_panel.html").read_text().replace("__TOKEN__", token)

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def respond(self, status, payload, content_type="application/json"):
                body = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Frame-Options", "DENY")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                if self.headers.get("Host") not in ALLOWED_HOSTS:
                    return self.respond(403, {"error": "Local access only."})
                if self.path == "/":
                    return self.respond(200, page, "text/html; charset=utf-8")
                if self.path == "/api/state":
                    try:
                        return self.respond(200, panel.submit(panel.state))
                    except ValueError as error:
                        return self.respond(503, {"error": str(error)})
                self.respond(404, {"error": "Not found."})

            def do_POST(self):
                if (self.path != "/api/command" or self.headers.get("Host") not in ALLOWED_HOSTS
                        or self.headers.get("X-Panel-Token") != token
                        or self.headers.get("Origin") not in {None, "http://127.0.0.1:8765", "http://localhost:8765"}):
                    return self.respond(403, {"error": "Local panel access required."})
                try:
                    size = int(self.headers.get("Content-Length", 0))
                    if not 0 < size <= 4096:
                        raise ValueError("Invalid request size.")
                    data = json.loads(self.rfile.read(size))
                    if not isinstance(data, dict):
                        raise ValueError("Expected an object.")
                    self.respond(200, panel.submit(lambda: panel.command(data)))
                except (ValueError, TypeError) as error:
                    self.respond(400, {"error": str(error)})

        self.server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .1}, daemon=True).start()
