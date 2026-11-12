"""Pure startup subway recovery state machine; no hardware is driven here.

This component is deliberately not connected to MPF until automatic device
ejects and ball accounting have a single coordinated owner.
"""


class SubwayRecovery:
    """Decide one action at a time from stable physical switch observations."""

    def __init__(self, timeout=3.0, settle=1.0, limit=3):
        self.timeout = timeout
        self.settle = settle
        self.limit = limit
        self.state = "settling"
        self.deadline = None
        self.stable_since = None
        self.last_switches = None
        self.released = 0
        self.reason = None

    def _fail(self, reason):
        self.state = "failed"
        self.reason = reason
        return "failed"

    def update(self, now, lock, kicker):
        """Return release, kick, done, failed, or None for one observation."""
        if self.state in ("done", "failed"):
            return None
        switches = (bool(lock), bool(kicker))
        if switches != self.last_switches:
            self.last_switches = switches
            self.stable_since = now

        if self.state == "wait_kicker":
            if kicker:
                self.state = "settling"
                self.stable_since = now
            elif now >= self.deadline:
                return self._fail("Released ball did not reach the kicker")
            return None
        if self.state == "wait_kicker_clear":
            if not kicker:
                self.state = "settling"
                self.stable_since = now
            elif now >= self.deadline:
                return self._fail("Kicker did not clear")
            return None

        if now - self.stable_since < self.settle:
            return None
        if kicker:
            if self.released >= self.limit:
                return self._fail("More than three balls reached the kicker")
            self.released += 1
            self.state = "wait_kicker_clear"
            self.deadline = now + self.timeout
            return "kick"
        if lock:
            if self.released >= self.limit:
                return self._fail("Subway still occupied after three balls")
            self.state = "wait_kicker"
            self.deadline = now + self.timeout
            return "release"
        self.state = "done"
        return "done"


class SubwayReleaseInterlock:
    """Fail-closed permission for a single release into the subway kicker.

    An independent hardware adapter must feed every kicker transition to this
    object and route *all* release requests through it. This class is not yet
    connected to MPF or the cabinet.
    """

    def __init__(self, timeout=3.0, clear_settle=0.5):
        self.timeout = timeout
        self.clear_settle = clear_settle
        self.state = "ready"
        self.deadline = None
        self.clear_since = None
        self.reason = None

    def request(self, now, kicker_active):
        """Grant exactly one pulse only when no handoff is in progress."""
        if self.state != "ready" or kicker_active:
            return False
        self.state = "waiting_for_arrival"
        self.deadline = now + self.timeout
        return True

    def observe(self, now, kicker_active):
        """Require a kicker arrival followed by a clear before rearming."""
        if self.state == "waiting_for_arrival":
            if now >= self.deadline:
                self._fail("Released ball did not reach the kicker")
            elif kicker_active:
                self.state = "waiting_for_clear"
                self.deadline = now + self.timeout
                self.clear_since = None
        elif self.state == "waiting_for_clear":
            if now >= self.deadline:
                self._fail("Kicker did not clear")
            elif kicker_active:
                self.clear_since = None
            elif self.clear_since is None:
                self.clear_since = now
            elif now - self.clear_since >= self.clear_settle:
                self.state = "ready"
                self.deadline = None
        return self.state

    def _fail(self, reason):
        self.state = "failed"
        self.reason = reason
        self.deadline = None


class SubwayRecoveryRunner:
    """Dispatch recovery actions through a single injected hardware owner.

    The owner must implement request_release() and request_kick(), return True
    only when it accepts the command, and enforce the kicker interlock on
    every path to the release coil. A rejected command fails recovery closed.
    This runner is not installed on the machine yet.
    """

    def __init__(self, owner, **options):
        self.owner = owner
        self.sequence = SubwayRecovery(**options)

    def update(self, now, lock, kicker):
        action = self.sequence.update(now, lock, kicker)
        if action == "release" and not self.owner.request_release():
            return self.sequence._fail("Subway release command was rejected")
        if action == "kick" and not self.owner.request_kick():
            return self.sequence._fail("Kicker command was rejected")
        return action
