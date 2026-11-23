"""Piper text-to-speech helper shared by the placeholder generators."""

import os
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import json

PIPER = os.environ.get("PIPER", os.path.expanduser("~/tts/bin/piper"))
VOICES = os.environ.get("PIPER_VOICES", os.path.expanduser("~/tts/voices"))


def speak_wav(text, voice, out_wav):
    """Render text to a WAV with Piper, or a silent placeholder if Piper is unavailable."""
    model = os.path.join(VOICES, voice["model"] + ".onnx")
    if os.path.exists(PIPER) and os.path.exists(model):
        cmd = [PIPER, "--model", model, "--output_file", out_wav,
               "--length-scale", str(voice.get("length_scale", 1.0))]
        if "speaker" in voice:
            cmd += ["--speaker", str(voice["speaker"])]
        subprocess.run(cmd, input=text.encode(), check=True, capture_output=True)
        return
    espeak = shutil.which("espeak-ng") or shutil.which("espeak")
    if espeak:
        subprocess.run([espeak, "-w", out_wav, text], check=True, capture_output=True)
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono",
                    "-t", "1", out_wav], check=True)


ELEVENLABS_URL = "https://api.elevenlabs.io/v1"


def elevenlabs_request(path, body=None):
    """Call the ElevenLabs API with ELEVENLABS_API_KEY; returns raw response bytes."""
    request = urllib.request.Request(ELEVENLABS_URL + path, method="POST" if body is not None else "GET",
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                                              "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500 or attempt == 4:
                raise RuntimeError(f"ElevenLabs {path}: {error.code} {error.read().decode(errors='replace')}")
            time.sleep(2 ** attempt)


def speak_elevenlabs(text, voice, model, out_mp3):
    """Render text with an ElevenLabs voice ({voice_id, settings}) to an MP3."""
    body = {"text": text, "model_id": voice.get("model", model)}
    if "settings" in voice:
        body["voice_settings"] = voice["settings"]
    audio = elevenlabs_request(f"/text-to-speech/{voice['voice_id']}?output_format=mp3_44100_128", body)
    with open(out_mp3, "wb") as handle:
        handle.write(audio)


def to_mp3(in_wav, out_mp3, bitrate="64k", extra=()):
    os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", in_wav, *extra, "-ac", "1",
                    "-codec:a", "libmp3lame", "-b:a", bitrate, out_mp3], check=True)


def temp_wav(suffix=".wav"):
    handle, path = tempfile.mkstemp(suffix=suffix)
    os.close(handle)
    return path
