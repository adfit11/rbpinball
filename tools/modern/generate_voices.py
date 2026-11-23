"""Render every line in sounds/modern_voice/script.yaml to a placeholder MP3.

Usage: ~/tts/bin/python tools/modern/generate_voices.py [--force] [--only CHARACTER[,CHARACTER...]]
Existing files are kept unless --force is given, so recorded replacements survive.
Characters with an `elevenlabs` voice render through ElevenLabs when ELEVENLABS_API_KEY is set; others use Piper.
"""

import os
import sys

from ruamel.yaml import YAML

sys.path.insert(0, os.path.dirname(__file__))
import tts  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def render(text, info, model, out, number):
    if "elevenlabs" in info and os.environ.get("ELEVENLABS_API_KEY"):
        voices = info["elevenlabs"] if isinstance(info["elevenlabs"], list) else [info["elevenlabs"]]
        raw = tts.temp_wav(".mp3")
        tts.speak_elevenlabs(text, voices[(number - 1) % len(voices)], model, raw)
        tts.to_mp3(raw, out, "96k", ["-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100"])
        os.remove(raw)
        return
    wav = tts.temp_wav()
    tts.speak_wav(text, info["voice"], wav)
    # A little room tone keeps the lines from sounding like a clean studio.
    tts.to_mp3(wav, out, "64k", ["-af", "highpass=f=120,lowpass=f=7000,aecho=0.8:0.5:40:0.15"])
    os.remove(wav)


def main(force=False, only=None):
    with open(os.path.join(ROOT, "sounds", "modern_voice", "script.yaml"), encoding="utf-8") as handle:
        script = YAML(typ="safe").load(handle)
    model = script.get("elevenlabs_model", "eleven_v4")
    made = 0
    for character, info in script["characters"].items():
        if only and character not in only:
            continue
        for pool, lines in info["pools"].items():
            for number, text in enumerate(lines, 1):
                out = os.path.join(ROOT, "sounds", "modern_voice", character, f"{character}_{pool}_{number:02d}.mp3")
                if os.path.exists(out) and not force:
                    continue
                render(text, info, model, out, number)
                made += 1
    print(f"generated {made} voice files")


if __name__ == "__main__":
    args = sys.argv[1:]
    chosen = args[args.index("--only") + 1].split(",") if "--only" in args else None
    main("--force" in args, chosen)
