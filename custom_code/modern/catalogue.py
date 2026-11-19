"""Load the jukebox catalogue and measure song files."""

import os
from dataclasses import dataclass

from ruamel.yaml import YAML

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JUKEBOX_DIR = os.path.join("sounds", "music", "jukebox")


@dataclass
class Song:
    slot: int
    artist: str
    title: str
    path: str  # project-relative

    @property
    def res_path(self):
        return "res://" + self.path.replace(os.sep, "/")

    @property
    def intro_path(self):
        """MC announcement spoken as the song starts; sits beside the song file."""
        folder, name = os.path.split(self.path)
        return os.path.join(folder, name.replace("song_", "intro_", 1))

    @property
    def intro_text(self):
        return f"Here's {self.artist} with {self.title}!"


def load(root=ROOT):
    with open(os.path.join(root, JUKEBOX_DIR, "catalogue.yaml"), encoding="utf-8") as handle:
        data = YAML(typ="safe").load(handle)
    slots = []
    for slot, artist in enumerate(data["artists"], 1):
        songs = [Song(slot, artist["name"], title, os.path.join(JUKEBOX_DIR, artist["folder"], f"song_{n}.mp3"))
                 for n, title in enumerate(artist["songs"], 1)]
        slots.append((artist["name"], songs))
    hit_me = data["hit_me"]
    songs = [Song(len(slots) + 1, song["artist"], song["title"],
                  os.path.join(JUKEBOX_DIR, hit_me["folder"], f"song_{n:02d}.mp3"))
             for n, song in enumerate(hit_me["songs"], 1)]
    slots.append((hit_me["name"], songs))
    return slots


_BITRATES = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
             2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
_RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}


def mp3_length_ms(path, default_ms):
    """Sum MPEG layer III frame durations; fall back to default_ms if unreadable."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError:
        return default_ms
    pos = 0
    if data[:3] == b"ID3" and len(data) > 10:
        pos = 10 + ((data[6] & 0x7f) << 21 | (data[7] & 0x7f) << 14 | (data[8] & 0x7f) << 7 | (data[9] & 0x7f))
    seconds = 0.0
    while pos + 4 <= len(data):
        b1, b2, b3 = data[pos + 1], data[pos + 2], data[pos + 3]
        if data[pos] != 0xFF or (b1 & 0xE0) != 0xE0:
            pos += 1
            continue
        version = (b1 >> 3) & 3
        bitrate_index, rate_index = b2 >> 4, (b2 >> 2) & 3
        if version == 1 or (b1 >> 1) & 3 != 1 or bitrate_index in (0, 15) or rate_index == 3:
            pos += 1
            continue
        rate = _RATES[version][rate_index]
        bitrate = _BITRATES[1 if version == 3 else 2][bitrate_index] * 1000
        samples = 1152 if version == 3 else 576
        length = samples // 8 * bitrate // rate + ((b2 >> 1) & 1)
        if length <= 0:
            break
        seconds += samples / rate
        pos += length
    return int(seconds * 1000) if seconds > 1 else default_ms
