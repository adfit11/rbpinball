"""Render every line in sounds/modern_voice/script.yaml to a placeholder MP3.

Usage: ~/tts/bin/python tools/modern/generate_voices.py [--force]
Existing files are kept unless --force is given, so recorded replacements survive.
"""

import os
import sys

from ruamel.yaml import YAML

sys.path.insert(0, os.path.dirname(__file__))
import tts  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def main(force=False):
    with open(os.path.join(ROOT, "sounds", "modern_voice", "script.yaml"), encoding="utf-8") as handle:
        script = YAML(typ="safe").load(handle)
    made = 0
    for character, info in script["characters"].items():
        for pool, lines in info["pools"].items():
            for number, text in enumerate(lines, 1):
                out = os.path.join(ROOT, "sounds", "modern_voice", character, f"{character}_{pool}_{number:02d}.mp3")
                if os.path.exists(out) and not force:
                    continue
                wav = tts.temp_wav()
                tts.speak_wav(text, info["voice"], wav)
                # A little room tone keeps the lines from sounding like a clean studio.
                tts.to_mp3(wav, out, "64k", ["-af", "highpass=f=120,lowpass=f=7000,aecho=0.8:0.5:40:0.15"])
                os.remove(wav)
                made += 1
    print(f"generated {made} voice files")


if __name__ == "__main__":
    main("--force" in sys.argv)
