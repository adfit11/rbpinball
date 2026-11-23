"""The jukebox: crater entries, the artist selector, rounds, songs and the song multiplier."""

import os
import random

from mpf.core.mode import Mode

from custom_code.modern import catalogue, settings
from custom_code.modern.bonus import ovation
from custom_code.modern.lamps import STEADY, director

TRANSFER_FALLBACK_MS = 15_000


def song_mode_running(machine):
    """From the selector opening until the song ends, only the song mode's rules advance."""
    jukebox = machine.modes["modern_jukebox"]
    return bool(jukebox.active and jukebox.busy)


class ModernJukebox(Mode):

    def mode_start(self, **kwargs):
        self.slots = catalogue.load()
        self.selector_open = False
        self.highlight = 0
        self.chosen = None
        self.ball_waiting = False
        self.song = None
        self.pending_song = None
        self.song_remaining_ms = 0
        self.song_started_at = None
        self.awaiting_kickback = False  # the jukebox has the ball until the subway kicker returns it
        self.clock_waiting = False  # a song is playing but its round clock waits for the ball
        self.pauses = set()
        self.blockers = set()
        self.add_mode_event_handler("modern_tap", self._tap)
        self.add_mode_event_handler("modern_select", self._select)
        self.add_mode_event_handler("ball_hold_modern_jukebox_held_ball", self._ball_held)
        self.add_mode_event_handler("modern_ball_held", self._pause)
        self.add_mode_event_handler("modern_ball_released", self._resume)
        self.add_mode_event_handler("balldevice_bd_classic_subway_kicker_ball_eject_success",
                                    self._start_pending)
        for name in ("player_modern_ovation", "player_modern_songs_completed_ball"):
            self.add_mode_event_handler(name, self._show_ovation)
        self._show()

    # Craters ---------------------------------------------------------------
    @property
    def lamps(self):
        return director(self.machine)

    def crater_entered(self, crater):
        targets = self.machine.modes["modern_targets"]
        lit = targets.crater_entered(crater)
        self.machine.events.post("modern_crater_entered", crater=crater, lit=lit)
        player = self.player
        if self.blockers or self.busy:
            return
        if self.machine.game.balls_in_play > 1:
            return
        rent_party = self.machine.modes["modern_rent_party"]
        if rent_party.active and rent_party.qualify_lock(lit):
            return  # the lock takes the ball; a nickel is kept for the next lit crater
        if not player.modern_nickel or not lit:
            if not player.modern_nickel:
                self.machine.events.post("modern_jukebox_no_nickel")
                self.machine.events.post("modern_callout", pool="mc_needs_nickel")
            return
        self.machine.events.post("modern_jukebox_hold_enable")
        self._open_selector()
        self.machine.events.post("modern_nickel_spent")

    @property
    def busy(self):
        """From the selector opening until the song ends: the song mode owns the directions."""
        return bool(self.selector_open or self.chosen or self.song or self.pending_song)

    # Selector --------------------------------------------------------------
    def played(self, slot_index):
        return bool(self.player.modern_artists_played & (1 << slot_index))

    def _open_selector(self):
        if self.player.modern_artists_played == (1 << len(self.slots)) - 1:
            self.player.modern_artists_played = 0
            self.player.modern_round_songs = 0
            self._show()
        self.selector_open = True
        self.highlight = self._next_selectable(-1)
        self.machine.modes["modern"].take_green("jukebox")
        self.delay.reset(ms=settings.SELECTOR_TIMEOUT_MS, name="selector_timeout", callback=self._choose)
        self.machine.events.post("modern_selector_opened", played=self.player.modern_artists_played,
                                 highlight=self.highlight, timeout_ms=settings.SELECTOR_TIMEOUT_MS,
                                 names="|".join(name for name, _ in self.slots))
        self.machine.events.post("modern_callout", pool="mc_jukebox_open")

    def _next_selectable(self, start):
        for step in range(1, len(self.slots) + 1):
            index = (start + step) % len(self.slots)
            if not self.played(index):
                return index
        return 0

    def _tap(self, owner="", **kwargs):
        if self.selector_open and owner == "jukebox":
            self.highlight = self._next_selectable(self.highlight)
            self.delay.reset(ms=settings.SELECTOR_TIMEOUT_MS, name="selector_timeout", callback=self._choose)
            self.machine.events.post("modern_selector_highlight", highlight=self.highlight,
                                     timeout_ms=settings.SELECTOR_TIMEOUT_MS)

    def _select(self, owner="", **kwargs):
        if self.selector_open and owner == "jukebox":
            self._choose()

    def _choose(self):
        if not self.selector_open:
            return
        self.selector_open = False
        self.delay.remove("selector_timeout")
        self.machine.modes["modern"].release_green("jukebox")
        name, songs = self.slots[self.highlight]
        self.player.modern_artists_played |= 1 << self.highlight
        self.chosen = random.choice(songs)
        self.machine.events.post("modern_artist_chosen", slot=self.highlight + 1, slot_name=name,
                                 artist=self.chosen.artist, title=self.chosen.title)
        from custom_code.modern.songs import SLOT_RULES
        rule = SLOT_RULES[self.highlight + 1]
        self.machine.events.post("modern_overlay", title=rule.title, subtitle=rule.goal,
                                 ms=settings.SONG_READ_MS, style="teal")
        self.delay.reset(ms=settings.SONG_START_MS, name="song_start", callback=self._start_chosen)
        self.delay.reset(ms=settings.SONG_READ_MS, name="read", callback=self._read_done)

    def _ball_held(self, **kwargs):
        self.ball_waiting = True
        self.awaiting_kickback = True

    def _start_chosen(self):
        if not self.chosen:
            return
        song, self.chosen = self.chosen, None
        self._count_song()
        self._start_song(song, counted=True)

    def _read_done(self):
        self.machine.events.post("modern_record_crackle_stop")
        self._release_ball()

    def _release_ball(self):
        self.ball_waiting = False
        self.machine.events.post("modern_jukebox_hold_disable")
        self.machine.events.post("modern_release_jukebox")

    def _start_pending(self, **kwargs):
        """Start the chosen song, or its round clock, once the subway kicker has returned the ball to play."""
        self.awaiting_kickback = False
        if self.clock_waiting:
            self._start_clock()
        if self.pending_song:
            self.delay.remove("transfer")
            song, self.pending_song = self.pending_song, None
            self._start_song(song, counted=True)

    # Songs -----------------------------------------------------------------
    def _count_song(self, step=1):
        """Song progression and multiplier; counted as the ball is released so new scores use it."""
        player = self.player
        before = player.modern_song_multiplier
        player.modern_songs_played += step
        player.modern_round_songs += step
        player.modern_bonus_songs += step
        player.modern_song_multiplier = min(settings.MAX_SONG_MULTIPLIER,
                                            1 + player.modern_songs_played // settings.MULTIPLIER_EVERY)
        if player.modern_song_multiplier > before:
            self.machine.events.post("modern_callout", pool="mc_multiplier", queue=True)
        self._show()

    def _refund(self, song, counted):
        """Give back an artist whose song never started (the ball drained first)."""
        self.player.modern_artists_played &= ~(1 << (song.slot - 1))
        if counted:
            self._count_song(-1)

    def _start_song(self, song, counted=False):
        player = self.player
        if not counted:
            self._count_song()
        player.modern_song_active = 1
        length = catalogue.mp3_length_ms(os.path.join(catalogue.ROOT, song.path), settings.DEFAULT_SONG_MS)
        from custom_code.modern.songs import SLOT_RULES
        round_ms = SLOT_RULES[song.slot].round_ms
        if round_ms:
            length = min(length, round_ms)
        self.song = song
        self.song_remaining_ms = length
        self.pauses.clear()
        self._show()
        self.machine.events.post("modern_song_started", slot=song.slot, artist=song.artist, title=song.title,
                                 path=song.res_path, length_ms=length)
        if self.awaiting_kickback:
            self.clock_waiting = True  # the music plays; the round and the mode wait for the ball
            self.delay.reset(ms=settings.KICKBACK_TIMEOUT_MS, name="kickback", callback=self._start_clock)
        else:
            self._start_clock()

    def _start_clock(self):
        """The round clock and the mode's own counters start together, once the ball is back in play."""
        self.clock_waiting = False
        self.delay.remove("kickback")
        if not self.song:
            return
        self.machine.events.post("modern_song_clock_started", slot=self.song.slot,
                                 length_ms=int(self.song_remaining_ms))
        self._run_song_timer()

    def _run_song_timer(self):
        self.song_started_at = self.machine.clock.get_time()
        self.delay.reset(ms=self.song_remaining_ms, name="song", callback=self.end_song)

    def _pause(self, hole=None, **kwargs):
        if self.clock_waiting:
            return
        if self.song and hole and not self.pauses:
            self.delay.remove("song")
            elapsed = (self.machine.clock.get_time() - self.song_started_at) * 1000
            self.song_remaining_ms = max(0, self.song_remaining_ms - elapsed)
            self.machine.events.post("modern_song_paused")
        if self.song and hole:
            self.pauses.add(hole)

    def _resume(self, hole=None, **kwargs):
        if not self.song or hole not in self.pauses:
            return
        self.pauses.discard(hole)
        if not self.pauses:
            self.machine.events.post("modern_song_resumed", remaining_ms=int(self.song_remaining_ms))
            self._run_song_timer()

    def song_remaining(self):
        if not self.song:
            return 0
        if self.pauses or self.clock_waiting:
            return int(self.song_remaining_ms)
        elapsed = (self.machine.clock.get_time() - self.song_started_at) * 1000
        return int(max(0, self.song_remaining_ms - elapsed))

    def end_song(self, reason="ended"):
        if not self.song:
            return
        song, self.song = self.song, None
        self.delay.remove("song")
        self.clock_waiting = False
        self.delay.remove("kickback")
        self.player.modern_song_active = 0
        self.machine.events.post("modern_song_ended", slot=song.slot, reason=reason)
        if reason not in ("drain", "tilt") and self.player.modern_songs_played in settings.EXTRA_BALL_SONGS:
            self.machine.events.post("modern_light_extra_ball")  # after the round, so it never competes with the mode
        if self.player.modern_songs_played >= settings.SPECIAL_AFTER_SONGS:
            self.machine.events.post("modern_light_special")

    def _show_ovation(self, **kwargs):
        self._show()

    def _show(self):
        lamps = self.lamps
        for index, light in enumerate(settings.SONG_LAMPS):
            lamps.set("songs", light, STEADY if index < self.player.modern_round_songs else 0)
        mult = self.player.modern_song_multiplier
        for index, light in enumerate(settings.MULTIPLIER_LAMPS, 2):
            lamps.set("multiplier", light, STEADY if index == mult else 0)
        level = ovation(self.player)
        for index, light in enumerate(settings.OVATION_LAMPS, 2):
            lamps.set("ovation", light, STEADY if index == level else 0)

    def mode_stop(self, **kwargs):
        if self.selector_open:
            self.selector_open = False
            self.machine.events.post("modern_selector_closed")
        if self.song:
            self.end_song(reason="drain")
        if self.pending_song:
            self._refund(self.pending_song, counted=True)
        if self.chosen:
            self._refund(self.chosen, counted=False)
        self.chosen = self.pending_song = None
        self.player.modern_song_active = 0
        try:
            self.lamps.clear("songs")
            self.lamps.clear("multiplier")
            self.lamps.clear("ovation")
        except KeyError:
            pass
