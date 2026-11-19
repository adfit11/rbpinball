"""Voice callouts over the music: event pools, no repeats, and occasional quips."""

import os
import random

from ruamel.yaml import YAML
from mpf.core.mode import Mode

from custom_code.modern import settings
from custom_code.modern.catalogue import ROOT

SCRIPT = os.path.join("sounds", "modern_voice", "script.yaml")


def load_script(root=ROOT):
    with open(os.path.join(root, SCRIPT), encoding="utf-8") as handle:
        data = YAML(typ="safe").load(handle)
    pools = {}
    for character, info in data["characters"].items():
        for pool, lines in info["pools"].items():
            for number, text in enumerate(lines, 1):
                name = f"{character}_{pool}_{number:02d}"
                path = f"sounds/modern_voice/{character}/{name}.mp3"
                pools.setdefault(f"{character}_{pool}", []).append(
                    {"character": character, "speaker": info["name"], "text": text, "path": path})
    return data, pools


class ModernCallouts(Mode):
    """Game-long mode; features post modern_callout{pool=...}."""

    def mode_start(self, **kwargs):
        _, self.pools = load_script()
        self.last = {}
        self.last_spoken = self.machine.clock.get_time()
        self.add_mode_event_handler("modern_callout", self._callout)
        self.delay.reset(ms=settings.QUIP_CHECK_MS, name="quip", callback=self._quip)

    def _callout(self, pool=None, queue=False, **kwargs):
        lines = self.pools.get(pool)
        if not lines:
            self.debug_log("No voice pool %s", pool)
            return
        choices = [l for l in lines if l is not self.last.get(pool)] or lines
        line = random.choice(choices)
        self.last[pool] = line
        self.last_spoken = self.machine.clock.get_time()
        self.machine.events.post("modern_voice", pool=pool, file="res://" + line["path"],
                                 speaker=line["speaker"], text=line["text"], queue=queue)

    def _quip(self):
        self.delay.reset(ms=settings.QUIP_CHECK_MS, name="quip", callback=self._quip)
        game = self.machine.game
        if not game or not game.player or game.player.modern_counting_bonus:
            return
        quiet = (self.machine.clock.get_time() - self.last_spoken) * 1000
        if quiet >= settings.QUIP_GAP_MS and random.random() < settings.QUIP_CHANCE:
            pool = random.choice([p for p in self.pools if p.startswith("regulars_")] or [None])
            if pool:
                self._callout(pool)
