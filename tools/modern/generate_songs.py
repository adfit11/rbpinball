"""Generate a placeholder MP3 for every jukebox catalogue entry.

Each placeholder is a synthesized boogie-woogie loop with the title spoken over it.
No original recordings are used. Existing files are kept unless --force is given,
so the owner's own MP3s are never overwritten.
Usage: ~/tts/bin/python tools/modern/generate_songs.py [--force] [--intros] [--seconds 60]
--intros regenerates only the MC song announcements, e.g. after editing catalogue titles.
"""

import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import tts  # noqa: E402
from custom_code.modern import catalogue  # noqa: E402

RATE = 22050
MC = {"model": "en_US-john-medium", "length_scale": 1.0}
BASS = [0, 4, 7, 9, 10, 9, 7, 4]
BARS = [0, 0, 0, 0, 5, 5, 0, 0, 7, 5, 0, 7]


def tone(freq, seconds, shape="saw"):
    t = np.arange(int(RATE * seconds)) / RATE
    if shape == "saw":
        wave_ = 2 * (t * freq % 1) - 1
    else:
        wave_ = np.sin(2 * np.pi * freq * t)
    env = np.minimum(1, np.exp(-t * 6) * 1.5)
    return wave_ * env


def backing(seconds, key, tempo, seed):
    rng = np.random.default_rng(seed)
    eighth = 60 / tempo / 2
    out = np.zeros(int(RATE * seconds) + RATE)
    pos, step = 0, 0
    while pos < seconds:
        bar = BARS[(step // 8) % 12]
        note = key * 2 ** ((bar + BASS[step % 8]) / 12)
        length = eighth * (1.33 if step % 2 == 0 else 0.67)  # shuffle feel
        start = int(pos * RATE)
        bass = tone(note, length, "saw") * 0.25
        out[start:start + len(bass)] += bass
        if step % 2 == 0:
            chord = sum(tone(note * 2 * 2 ** (i / 12), length * 0.6, "sine") for i in (4, 7, 10)) * 0.08
            out[start:start + len(chord)] += chord
        hat = rng.normal(0, 1, int(RATE * 0.03)) * np.exp(-np.arange(int(RATE * 0.03)) / 80) * 0.08
        out[start:start + len(hat)] += hat
        pos += length
        step += 1
    return out[:int(RATE * seconds)]


def read_wav(path):
    with wave.open(path) as handle:
        data = np.frombuffer(handle.readframes(handle.getnframes()), dtype=np.int16) / 32768
        rate = handle.getframerate()
    if rate != RATE:
        data = np.interp(np.arange(0, len(data), rate / RATE), np.arange(len(data)), data)
    return data


def write_wav(path, data):
    data = np.clip(data, -1, 1)
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(RATE)
        handle.writeframes((data * 32767).astype(np.int16).tobytes())


def make_intros(force=False):
    """MC "Here's <artist> with <title>!" announcements; rerun with --intros after editing catalogue titles."""
    made = 0
    for _, songs in catalogue.load():
        for song in songs:
            out = os.path.join(catalogue.ROOT, song.intro_path)
            if os.path.exists(out) and not force:
                continue
            wav = tts.temp_wav()
            tts.speak_wav(song.intro_text, MC, wav)
            tts.to_mp3(wav, out, "64k")
            os.remove(wav)
            made += 1
    print(f"generated {made} song intros")


def main(force=False, seconds=60):
    made = 0
    for slot, (name, songs) in enumerate(catalogue.load(), 1):
        for number, song in enumerate(songs, 1):
            out = os.path.join(catalogue.ROOT, song.path)
            if os.path.exists(out) and not force:
                continue
            music = backing(seconds, 98 + slot * 7 % 40, 150 + slot * 9 + number * 4, slot * 100 + number)
            spoken = tts.temp_wav()
            tts.speak_wav(f"{song.title}, by {song.artist}. Placeholder track.", MC, spoken)
            voice = read_wav(spoken)
            os.remove(spoken)
            for at in range(0, seconds - 5, 20):
                start = int((at + 0.5) * RATE)
                end = min(len(music), start + len(voice))
                music[start:end] = music[start:end] * 0.4 + voice[:end - start] * 0.9
            fade = int(RATE * 2)
            music[-fade:] *= np.linspace(1, 0, fade)
            wav = tts.temp_wav()
            write_wav(wav, music * 0.8)
            tts.to_mp3(wav, out, "48k")
            os.remove(wav)
            made += 1
    print(f"generated {made} song files")
    make_intros(force)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--intros" in args:
        make_intros(force=True)
        sys.exit()
    main("--force" in args, int(args[args.index("--seconds") + 1]) if "--seconds" in args else 60)
