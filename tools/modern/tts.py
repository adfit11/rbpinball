"""Piper text-to-speech helper shared by the placeholder generators."""

import os
import shutil
import subprocess
import tempfile

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


def to_mp3(in_wav, out_mp3, bitrate="64k", extra=()):
    os.makedirs(os.path.dirname(out_mp3), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", in_wav, *extra, "-ac", "1",
                    "-codec:a", "libmp3lame", "-b:a", bitrate, out_mp3], check=True)


def temp_wav():
    handle, path = tempfile.mkstemp(suffix=".wav")
    os.close(handle)
    return path
