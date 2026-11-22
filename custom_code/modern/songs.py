"""Song modes: one rule per jukebox slot, run while that slot's song plays."""

import random

from mpf.core.mode import Mode

from custom_code.modern import settings as S
from custom_code.modern.lamps import FLASH, director
from custom_code.modern.scoring import award

LOC = S.LOCATION_NAMES


def drain_value(start, end, total_ms, elapsed_ms):
    return int(max(end, start - (start - end) * min(1.0, elapsed_ms / total_ms)))


class SongRule:
    key = ""
    title = ""
    goal = ""
    ends_on_complete = False
    round_ms = S.ROUND_MS  # the song fades out here if it is longer

    def __init__(self, songs):
        self.songs, self.machine, self.mode = songs, songs.machine, songs
        self.completed = False

    @property
    def lamps(self):
        return director(self.machine)

    def now_ms(self):
        return self.songs.song_ms()

    def pay(self, value, source):
        return award(self.machine, value, source)

    def flash(self, locations):
        self.lamps.clear("song")
        for loc in locations:
            self.lamps.set("song", S.LOCATIONS[loc][1], FLASH)
        self.machine.events.post("modern_song_targets", locations=",".join(locations))

    def shot(self, title=None, subtitle="", pool=None):
        """A mode shot: every playfield lamp bursts bottom to top, the screen flashes, and an optional overlay and callout."""
        self.machine.events.post("modern_song_shot", mode=self.key)
        if title:
            self.machine.events.post("modern_overlay", title=title, subtitle=subtitle, ms=1500, style="gold")
        if pool:
            self.machine.events.post("modern_callout", pool=pool)

    def complete(self):
        if not self.completed:
            self.completed = True
            self.songs.completed(self)

    def status(self):
        return ""

    def start(self): pass
    def stop(self): self.lamps.clear("song")
    def tick(self): pass
    def on_location(self, location): pass
    def on_crater(self, crater, lit): pass
    def on_spin(self): pass
    def on_bumper(self): pass
    def on_hole_held(self, hole): pass
    def on_tap(self): pass
    def on_ball_saved(self): pass
    def on_song_end(self): pass


class HurryUp(SongRule):
    key = "hurry_up"
    title, goal, ends_on_complete = "HURRY-UP", "Shoot the flashing location before it drains!", True

    def start(self):
        self.target = random.choice(LOC)
        self.started = self.now_ms()
        self.flash([self.target])

    def value(self):
        return drain_value(S.HURRY_START, S.HURRY_END, S.HURRY_MS, self.now_ms() - self.started)

    def tick(self):
        if self.now_ms() - self.started >= S.HURRY_MS:
            self.songs.failed(self, end_song=True)

    def on_location(self, location):
        if location == self.target:
            self.pay(self.value(), "hurry_up")
            self.shot()
            self.complete()

    def status(self):
        return f"HURRY-UP  {S.LOCATIONS[self.target][0]}  {self.value():,}"


class Ladder(SongRule):
    key = "ladder"
    title, goal, ends_on_complete = "LADDER", "Climb four rungs at the Kitchen", True

    def start(self):
        self.rung = 0
        self.flash(["kitchen"])

    def next_value(self):
        return S.LADDER_RUNGS[self.rung] if self.rung < len(S.LADDER_RUNGS) else None

    def on_hole_held(self, hole):
        if hole == "kitchen" and self.rung < len(S.LADDER_RUNGS):
            self.machine.modes["modern_holes"].extend("kitchen", S.LADDER_HOLD_MS)
            value = self.next_value()
            self.pay(value, "ladder")
            self.rung += 1
            after = self.next_value()
            self.shot(f"RUNG {self.rung}!", f"{value:,}  •  " + (f"Next {after:,}" if after else "Top of the ladder!"),
                      "mc_song_rung")
            if after is None:
                self.lamps.clear("song")
                self.complete()

    def status(self):
        rungs = len(S.LADDER_RUNGS)
        after = self.next_value()
        where = f"NEXT {after // 1000}K AT THE KITCHEN" if after else "TOP RUNG"
        return f"LADDER  RUNG {self.rung} / {rungs}  •  {where}"


class BuildAndCollect(SongRule):
    key = "build_and_collect"
    title, goal = "BUILD AND COLLECT", "Spin the Bandstand to build the pot, collect at the Bar"

    def start(self):
        self.pot, self.per_spin, self.collects = 0, S.POT_START, 0
        self.flash(["bandstand", "bar"])

    def on_spin(self):
        self.pot += self.per_spin
        self.machine.events.post("modern_pot_spin", pot=self.pot, gain=self.per_spin)
        self.per_spin += S.POT_STEP

    def on_location(self, location):
        if location == "bar" and self.pot:
            self.pay(self.pot + S.POT_COLLECT_BONUS, "pot")
            self.shot()
            self.pot, self.per_spin = 0, S.POT_START
            self.collects += 1
            if self.collects >= S.POT_COLLECTS:
                self.complete()

    def status(self):
        return f"POT {self.pot:,}  •  collects {self.collects} / {S.POT_COLLECTS}"


class RovingShot(SongRule):
    key = "roving_shot"
    title, goal, ends_on_complete = "ROVING SHOT", "Chase the moving shot. Tap green once to freeze it", True

    def start(self):
        self.hits, self.frozen_until, self.freeze_used = 0, 0, False
        self.target = random.choice(LOC)
        self.moved = self.now_ms()
        self.mode.machine.modes["modern"].take_green("song")
        self.flash([self.target])

    def tick(self):
        now = self.now_ms()
        if now >= self.frozen_until and now - self.moved >= S.ROVE_MS:
            self.target = random.choice([l for l in LOC if l != self.target])
            self.moved = now
            self.flash([self.target])

    def on_tap(self):
        if not self.freeze_used:
            self.freeze_used = True
            self.frozen_until = self.now_ms() + S.ROVE_FREEZE_MS
            self.moved = self.frozen_until - S.ROVE_MS

    def on_location(self, location):
        if location == self.target and self.hits < S.ROVE_HITS:
            self.pay(S.ROVE_VALUE, "roving")
            self.shot()
            self.hits += 1
            if self.hits >= S.ROVE_HITS:
                self.lamps.clear("song")
                self.complete()

    def stop(self):
        super().stop()
        self.machine.modes["modern"].release_green("song")

    def status(self):
        return f"ROVING SHOT  {S.LOCATIONS[self.target][0]}  •  {self.hits} / {S.ROVE_HITS}"


class JukeboxJackpot(SongRule):
    key = "jukebox_jackpot"
    title, goal, ends_on_complete = "JUKEBOX JACKPOT", "Every crater is a jackpot!", True
    round_ms = S.JACKPOT_ROUND_MS

    def start(self):
        self.jackpots = 0
        for light in S.CRATER_LAMPS:
            self.lamps.set("song", light, FLASH)

    def value(self, crater):
        return S.JACKPOT_VALUES[crater - 1] + S.JACKPOT_STEP * self.jackpots

    def on_crater(self, crater, lit):
        if self.completed:
            return
        value = self.value(crater)
        self.pay(value, "jukebox_jackpot")
        self.jackpots += 1
        self.machine.events.post("modern_song_jackpot", crater=crater, value=value, count=self.jackpots)
        self.shot("JACKPOT!", f"{value:,}  •  Crater {crater}", "mc_song_jackpot")
        if self.jackpots >= S.JACKPOTS_TO_COMPLETE:
            self.complete()

    def status(self):
        values = "  ".join(f"{n}: {self.value(n) // 1000}K" for n in range(1, len(S.JACKPOT_VALUES) + 1))
        return f"JACKPOTS {self.jackpots} / {S.JACKPOTS_TO_COMPLETE}  •  CRATER {values}"


class PartyTime(SongRule):
    key = "party_time"
    title, goal = "PARTY TIME", "Double scoring and the Bouncer is ready. Survive the song!"

    def start(self):
        self.machine.game.player.modern_score_factor = S.PARTY_FACTOR
        self.machine.modes["modern_ball_saver"].ready()
        self.machine.events.post("modern_party_time_lights")

    def on_ball_saved(self):
        self.machine.modes["modern_ball_saver"].ready()

    def on_song_end(self):
        self.pay(S.LAST_DANCE_AWARD, "last_dance")
        self.complete()

    def stop(self):
        super().stop()
        self.machine.events.post("modern_party_time_lights_stop")
        self.machine.game.player.modern_score_factor = 1

    def status(self):
        return "PARTY TIME  ×2 everything  •  Bouncer ready"


class OrderUp(SongRule):
    key = "order_up"
    title, goal, ends_on_complete = "ORDER UP", "Pick up at the Kitchen, deliver before it gets cold", True

    def start(self):
        self.destination, self.started = None, 0
        self.flash(["kitchen"])

    def on_hole_held(self, hole):
        if hole == "kitchen" and self.destination is None and not self.completed:
            self.machine.modes["modern_holes"].extend("kitchen", 1000 + S.HOLE_HOLD_MS)
            self.pay(S.ORDER_PICKUP, "order_pickup")
            self.shot()
            self.destination = random.choice([l for l in LOC if l != "kitchen"])
            self.started = self.now_ms()
            self.machine.events.post("modern_callout", pool="cook_order_up")
            self.flash([self.destination])

    def value(self):
        return drain_value(S.ORDER_START, S.ORDER_END, S.ORDER_MS, self.now_ms() - self.started)

    def tick(self):
        if self.destination and self.now_ms() - self.started >= S.ORDER_MS:
            self.destination = None
            self.songs.failed(self, end_song=True)

    def on_location(self, location):
        if self.destination and location == self.destination:
            self.pay(self.value(), "delivery")
            self.shot()
            self.destination = None
            self.lamps.clear("song")
            self.complete()

    def status(self):
        if self.completed:
            return "ORDER DELIVERED"
        if self.destination:
            return f"DELIVER TO {S.LOCATIONS[self.destination][0]}  {self.value():,}"
        return "ORDER UP  •  pick up at the Kitchen"


class RequestNight(SongRule):
    key = "request_night"
    title, goal, ends_on_complete = "REQUEST NIGHT", "Take a request at every location", True

    def start(self):
        self.remaining = list(LOC)
        self.flash(self.remaining)

    def on_location(self, location):
        if location in self.remaining:
            self.remaining.remove(location)
            self.pay(S.REQUEST_VALUES[len(LOC) - len(self.remaining) - 1], "request")
            self.shot()
            self.flash(self.remaining)
            if not self.remaining:
                self.pay(S.FINAL_REQUEST_AWARD, "final_request")
                self.complete()

    def status(self):
        return f"REQUESTS {len(LOC) - len(self.remaining)} / {len(LOC)}"


class DanceFloor(SongRule):
    key = "dance_floor"
    title, goal = "DANCE FLOOR", "Bumpers score 5×. Pack the floor with 25 hits"

    def start(self):
        self.hits = 0
        self.machine.game.player.modern_bumper_factor = S.DANCE_FACTOR

    def on_bumper(self):
        self.hits += 1
        if self.hits == S.DANCE_HITS:
            self.pay(S.PACKED_FLOOR_AWARD, "packed_floor")
            self.complete()

    def stop(self):
        super().stop()
        self.machine.game.player.modern_bumper_factor = 1

    def status(self):
        return f"DANCERS {self.hits} / {S.DANCE_HITS}"


class HitMe(SongRule):
    key = "hit_me"
    title, goal, ends_on_complete = "HIT ME!", "Tap green to stop the dial, then hit the lit location", True

    def start(self):
        self.hits = 0
        self.mode.machine.modes["modern"].take_green("song")
        self.spin_dial()

    def spin_dial(self):
        self.spinning, self.index, self.target = True, 0, None
        self.spun_at = self.stepped = self.now_ms()

    def tick(self):
        if not self.spinning:
            return
        now = self.now_ms()
        if now - self.stepped >= S.DIAL_STEP_MS:
            self.stepped = now
            self.index = (self.index + 1) % len(LOC)
            self.flash([LOC[self.index]])
        if now - self.spun_at >= S.DIAL_AUTO_STOP_MS:
            self.stop_dial()

    def stop_dial(self):
        self.spinning = False
        self.target = LOC[self.index]
        self.flash([self.target])
        self.machine.events.post("modern_overlay", title="HIT ME!", subtitle=S.LOCATIONS[self.target][0], ms=1200)

    def on_tap(self):
        if self.spinning:
            self.stop_dial()

    def on_location(self, location):
        if self.target and location == self.target:
            self.pay(S.HIT_ME_VALUE, "hit_me")
            self.shot()
            self.hits += 1
            if self.hits >= S.HIT_ME_HITS:
                self.complete()
            else:
                self.spin_dial()

    def stop(self):
        super().stop()
        self.machine.modes["modern"].release_green("song")

    def status(self):
        where = "spinning..." if self.spinning else S.LOCATIONS[self.target][0]
        return f"HIT ME!  {where}  •  {self.hits} / {S.HIT_ME_HITS}"


SLOT_RULES = {1: HurryUp, 2: Ladder, 3: BuildAndCollect, 4: RovingShot, 5: JukeboxJackpot,
              6: PartyTime, 7: OrderUp, 8: RequestNight, 9: DanceFloor, 10: HitMe}
TICK_MS = 100


class ModernSongs(Mode):

    def mode_start(self, **kwargs):
        self.rule = None
        self.add_mode_event_handler("modern_song_started", self._song_started)
        self.add_mode_event_handler("modern_song_ended", self._song_ended)
        self.add_mode_event_handler("modern_location_hit", self._forward, method="on_location", arg="location")
        self.add_mode_event_handler("modern_crater_entered", self._crater)
        self.add_mode_event_handler("modern_spin", self._forward, method="on_spin")
        self.add_mode_event_handler("modern_bumper_hit", self._forward, method="on_bumper")
        self.add_mode_event_handler("modern_hole_held", self._forward, method="on_hole_held", arg="hole")
        self.add_mode_event_handler("modern_tap", self._tap)
        self.add_mode_event_handler("modern_ball_saved", self._forward, method="on_ball_saved")
        self.add_mode_event_handler("tilt", self._tilt)
        self.add_mode_event_handler("modern_song_paused", self._paused)
        self.add_mode_event_handler("modern_song_resumed", self._resumed)
        self.paused_total, self.paused_at = 0, None

    def _wall_ms(self):
        return self.machine.clock.get_time() * 1000

    def song_ms(self):
        """Song-clock time: wall time minus time the ball spent held, so challenges pause with the song."""
        held = self.paused_total + (self._wall_ms() - self.paused_at if self.paused_at is not None else 0)
        return self._wall_ms() - held

    def _paused(self, **kwargs):
        if self.paused_at is None:
            self.paused_at = self._wall_ms()

    def _resumed(self, **kwargs):
        if self.paused_at is not None:
            self.paused_total += self._wall_ms() - self.paused_at
            self.paused_at = None

    def _song_started(self, slot, **kwargs):
        self.paused_total, self.paused_at = 0, None  # a hold left over from the previous song
        self.rule = SLOT_RULES[slot](self)
        self.rule.start()
        self.machine.events.post("modern_song_mode_started", slot=slot, title=self.rule.title, goal=self.rule.goal)
        self.machine.events.post("modern_callout", pool=f"mc_mode_{self.rule.key}", queue=True)
        self._tick()

    def _tick(self):
        if not self.rule:
            return
        if self.paused_at is None:
            self.rule.tick()
        if self.rule:
            self.machine.events.post("modern_mode_status", text=self.rule.status())
            self.delay.reset(ms=TICK_MS, name="tick", callback=self._tick)

    def _forward(self, method, arg=None, **kwargs):
        if self.rule:
            getattr(self.rule, method)(*([kwargs[arg]] if arg else []))

    def _crater(self, crater, lit, **kwargs):
        if self.rule:
            self.rule.on_crater(crater, lit)

    def _tap(self, owner="", **kwargs):
        if self.rule and owner == "song":
            self.rule.on_tap()

    def completed(self, rule):
        player = self.machine.game.player
        player.modern_songs_completed_ball += 1
        points = award(self.machine, S.SONG_COMPLETION_AWARD, "song_complete")
        self.machine.events.post("modern_song_completed", title=rule.title, points=points)
        self.machine.events.post("modern_overlay", title="SONG COMPLETE!", subtitle=f"{rule.title}  +{points:,}",
                                 ms=2000)
        self.machine.events.post("modern_callout", pool="mc_song_complete")
        if rule.ends_on_complete:
            self.machine.modes["modern_jukebox"].end_song(reason="completed")

    def failed(self, rule, end_song=False):
        self.machine.events.post("modern_song_failed", title=rule.title)
        self.machine.events.post("modern_overlay", title="THE RECORD SKIPPED", subtitle=rule.title, ms=1800)
        self.machine.events.post("modern_callout", pool="mc_song_failed")
        if end_song:
            self.machine.modes["modern_jukebox"].end_song(reason="failed")

    def _song_ended(self, reason="ended", **kwargs):
        rule, self.rule = self.rule, None
        self.delay.remove("tick")
        if rule is None:
            return
        if reason == "ended":
            rule.on_song_end()
            if not rule.completed:
                self.machine.events.post("modern_song_failed", title=rule.title)
                self.machine.events.post("modern_overlay", title="SONG OVER", subtitle=rule.title, ms=1500)
        rule.stop()
        self.machine.events.post("modern_mode_status", text="")

    def _tilt(self, **kwargs):
        self.machine.modes["modern_jukebox"].end_song(reason="tilt")

    def mode_stop(self, **kwargs):
        if self.rule:
            self.rule.stop()
            self.rule = None
