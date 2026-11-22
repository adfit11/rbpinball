"""Guest list, physical subway locks (stealable: Gate Crasher), and Rent Party multiball."""

from mpf.core.mode import Mode

from custom_code.modern import settings as S
from custom_code.modern.jukebox import song_mode_running
from custom_code.modern.lamps import FLASH, director
from custom_code.modern.scoring import award

LOCK_DEVICE = "bd_classic_subway_lock"


class ModernRentParty(Mode):
    _owners = None
    _owners_game = None

    @property
    def lock_owners(self):
        """Player numbers, in lock order, of the balls locked during this game."""
        if self._owners_game is not self.machine.game:
            self._owners_game, self._owners = self.machine.game, []
        return self._owners

    def mode_start(self, **kwargs):
        player = self.player
        player.modern_guests = 0
        player.modern_lock_lit = 0
        self.multiball = False
        self.jackpots = 0
        self.super_lit = False
        self.total = 0
        self.building = False
        self.add_mode_event_handler("multiball_lock_modern_subway_lock_full", self._build_up)
        self.add_mode_event_handler("modern_location_hit", self._location)
        self.add_mode_event_handler("modern_bank_completed", self._bank)
        self.add_mode_event_handler("modern_crater_entered", self._crater)
        self.add_mode_event_handler("multiball_lock_modern_subway_lock_locked_ball", self._locked)
        self.add_mode_event_handler("multiball_modern_rent_party_started", self._party_started)
        self.add_mode_event_handler("multiball_modern_rent_party_ended", self._party_ended)
        self.add_mode_event_handler(f"balldevice_{LOCK_DEVICE}_ball_count_changed", self._update_locks)
        self._update_locks()

    @property
    def lamps(self):
        return director(self.machine)

    @property
    def locked_balls(self):
        return self.machine.ball_devices[LOCK_DEVICE].balls

    def _update_locks(self, **kwargs):
        if self.machine.game and self.machine.game.player:
            self.machine.game.player.modern_locked_balls = self.locked_balls

    # Guest list ------------------------------------------------------------
    def guests(self):
        return [g for i, g in enumerate(S.GUESTS) if self.player.modern_guests & (1 << i)]

    def _location(self, location, **kwargs):
        self._guest(location)
        if self.multiball and self.super_lit and location == "bar":
            self.super_lit = False
            self.lamps.clear("rent_party")
            self.total += award(self.machine, S.SUPER_JACKPOT, "super_jackpot")
            self.machine.events.post("modern_super_jackpot")
            self.machine.events.post("modern_overlay", title="SUPER JACKPOT!", subtitle="The rent is paid!",
                                     ms=2500, style="gold")
            self.machine.events.post("modern_callout", pool="mc_super_jackpot")

    def _bank(self, bank, **kwargs):
        self._guest(bank)

    def _guest(self, guest):
        player = self.player
        if guest not in S.GUESTS or player.modern_lock_lit or self.multiball or song_mode_running(self.machine):
            return
        bit = 1 << S.GUESTS.index(guest)
        if player.modern_guests & bit:
            return
        player.modern_guests |= bit
        count = len(self.guests())
        self.machine.events.post("modern_guest_arrived", guest=guest, guest_name=S.GUEST_NAMES[guest], count=count)
        self.machine.events.post("modern_callout", pool="doorman_guest")
        if count >= S.GUESTS_TO_FILL:
            player.modern_lock_lit = 1
            award(self.machine, S.SCORE_LOCK_LIT, "lock_lit")
            self.machine.events.post("modern_lock_lit")
            self.machine.events.post("modern_overlay", title="GUEST LIST FULL", subtitle="LOCK IS LIT. Shoot a lit crater!",
                                     ms=2200)
            self.machine.events.post("modern_callout", pool="mc_lock_lit")

    # Locks -----------------------------------------------------------------
    def qualify_lock(self, lit):
        """Called by the jukebox on any crater entry; returns whether this ball will be locked."""
        if (lit and self.player.modern_lock_lit and not self.multiball
                and self.machine.game.balls_in_play == 1 and self.locked_balls < S.LOCKS_FOR_MULTIBALL):
            self.machine.events.post("modern_lock_qualified")
            return True
        return False

    def _locked(self, total_balls_locked=0, **kwargs):
        self.lock_owners.append(self.player.number)
        self._update_locks()
        # One lock per full guest list: the next lock needs a new list.
        self.player.modern_lock_lit = 0
        self.player.modern_guests = 0
        award(self.machine, S.SCORE_BALL_LOCKED, "ball_locked")
        count = self.locked_balls
        self.machine.events.post("modern_ball_locked", count=count)
        if count < S.LOCKS_FOR_MULTIBALL:
            self.machine.events.post("modern_overlay", title=f"BALL {count} LOCKED",
                                     subtitle=f"{count} in the back room", ms=2000)
            self.machine.events.post("modern_callout", pool="mc_ball_locked")

    # Rent Party --------------------------------------------------------------
    def _build_up(self, **kwargs):
        """The third lock holds every ball while the riser plays; the multiball starts when it peaks."""
        self.building = True
        self.machine.events.post("modern_rent_party_build_up", ms=S.RENT_PARTY_BUILD_UP_MS)
        self.machine.events.post("modern_overlay", title="THE BACK ROOM IS FULL!", subtitle="Get ready for the RENT PARTY…",
                                 ms=S.RENT_PARTY_BUILD_UP_MS, style="gold")
        self.machine.events.post("modern_callout", pool="mc_rent_party_build_up")
        self.delay.reset(ms=S.RENT_PARTY_BUILD_UP_MS, name="build_up",
                         callback=self.machine.events.post, event="modern_rent_party_go")

    def _party_started(self, **kwargs):
        owners = self.lock_owners
        crasher = any(owner != self.player.number for owner in owners)
        self._owners = []
        self.building = False
        self.multiball, self.jackpots, self.super_lit, self.total = True, 0, False, 0
        self.player.modern_lock_lit = 0
        self.player.modern_guests = 0
        if crasher:
            self.machine.events.post("modern_gate_crasher", player=self.player.number)
            self.machine.events.post("modern_overlay", title="GATE CRASHER!",
                                     subtitle=f"Player {self.player.number} crashed the party!", ms=2500, style="red")
            self.machine.events.post("modern_callout", pool="doorman_gate_crasher")
        self.machine.events.post("modern_rent_party_started", gate_crasher=crasher, jackpot=self.jackpot_value())
        self.machine.events.post("modern_overlay", title="RENT PARTY!", subtitle="Every lit crater is a jackpot",
                                 ms=3000, style="gold")
        self.machine.events.post("modern_callout", pool="mc_rent_party")

    def jackpot_value(self):
        return S.JACKPOT_BASE + S.JACKPOT_INCREMENT * self.jackpots

    def _crater(self, crater, lit, **kwargs):
        if not self.multiball or not lit:
            return
        self.total += award(self.machine, self.jackpot_value(), "jackpot")
        self.jackpots += 1
        self.machine.events.post("modern_jackpot", count=self.jackpots, next_value=self.jackpot_value())
        self.machine.events.post("modern_overlay", title="JACKPOT!", subtitle=f"Next {self.jackpot_value():,}", ms=1500,
                                 style="gold")
        self.machine.events.post("modern_callout", pool="mc_jackpot")
        if self.jackpots == S.JACKPOTS_FOR_SUPER:
            self.super_lit = True
            self.lamps.set("rent_party", S.LOCATIONS["bar"][1], FLASH)
            self.machine.events.post("modern_super_jackpot_lit")
            self.machine.events.post("modern_overlay", title="SUPER JACKPOT LIT", subtitle="Shoot the Bar!", ms=2000)

    def _party_ended(self, **kwargs):
        self.multiball, self.super_lit = False, False
        self.lamps.clear("rent_party")
        self._update_locks()
        self.machine.events.post("modern_rent_party_ended", total=self.total, jackpots=self.jackpots)
        self.machine.events.post("modern_overlay", title="RENT PARTY TOTAL", subtitle=f"{self.total:,}", ms=2500)
        self.machine.events.post("modern_light_extra_ball")

    def mode_stop(self, **kwargs):
        self.lamps.clear("rent_party")
        if self.building:  # a tilt cancelled the party; free the back room so the next ball can be served
            self.building = False
            self.lock_owners.clear()
            self.machine.ball_devices[LOCK_DEVICE].eject_all()
