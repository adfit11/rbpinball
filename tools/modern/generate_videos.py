"""Generate placeholder performer videos for the Modern song modes.

Each artist folder gets one looping pan-and-zoom video.ogv from a generic act still
(images/modern/video_src), plus a club.ogv fallback. Owner clips named video_<n>.ogv
(video_<nn>.ogv for Hit me!) override per song. Existing files are kept unless --force.
Usage: python3 tools/modern/generate_videos.py [--force] [--seconds 12]
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "images", "modern", "video_src")
OUT = os.path.join(ROOT, "videos", "modern", "jukebox")
ACTS = {
    "01_louis_jordan": "sax", "02_ruth_brown": "singer", "03_big_joe_turner": "singer",
    "04_lavern_baker": "singer", "05_wynonie_harris": "singer", "06_big_mama_thornton": "singer",
    "07_etta_james": "singer", "08_ray_charles": "piano", "09_joe_liggins": "piano", "10_hit_me": "band",
}


def render(still, out, seconds, seed):
    frames = seconds * 25
    drift = f"sin(2*PI*on/{frames}+{seed})"
    vf = (f"scale=1920:-2,zoompan=z='1.10+0.06*{drift}':x='(iw-iw/zoom)/2+iw*0.04*{drift}'"
          f":y='(ih-ih/zoom)/2+ih*0.02*cos(2*PI*on/{frames}+{seed})':d=1:s=960x540:fps=25,"
          f"eq=brightness='0.03*sin(2*PI*t*0.9+{seed})':eval=frame")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", still, "-vf", vf, "-t", str(seconds),
                    "-c:v", "libtheora", "-q:v", "5", "-an", out], check=True)


def main(force=False, seconds=12):
    jobs = [(os.path.join(SRC, f"{act}.png"), os.path.join(OUT, folder, "video.ogv"))
            for folder, act in ACTS.items()]
    jobs.append((os.path.join(SRC, "club.png"), os.path.join(OUT, "club.ogv")))
    made = 0
    for seed, (still, out) in enumerate(jobs):
        if os.path.exists(out) and not force:
            continue
        render(still, out, seconds, seed)
        made += 1
    print(f"generated {made} videos")


if __name__ == "__main__":
    args = sys.argv[1:]
    main("--force" in args, int(args[args.index("--seconds") + 1]) if "--seconds" in args else 12)
