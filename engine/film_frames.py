"""Turn a renovation film (video) into the scroll frames the film template plays.

Usage:
  python3 engine/film_frames.py TALL.mp4 OUT_DIR [--wide WIDE.mp4]

Writes OUT_DIR/m/0001.webp ... (64 frames, 540x960, about 2 MB) from a tall 9:16 film and, with --wide,
OUT_DIR/d/0001.webp ... (64 frames, 1280px wide) from a 16:9 film. Needs ffmpeg.
Busy scenes (foliage, gravel, brick) compress badly, so the tall set steps the quality down, then the size
(480x854), until it fits the phone budget (TALL_BUDGET_MB).

Library film:   OUT_DIR = engine/films/<group>/<film id>   (then add it to FILMS in trades.py)
Customer film:  OUT_DIR = leads/<lead id>/film             (optional leads/<lead id>/film/film.json with
                "scene", "hook", "hook_sub" or "beats" to change the captions)
"""
import shutil
import subprocess
import sys
from pathlib import Path

FRAMES = 64
TALL_BUDGET_MB = 2.4
# (quality, width, height) tried in order until the tall set fits the budget
TALL_STEPS = [(44, 540, 960), (32, 540, 960), (24, 540, 960), (24, 480, 854)]


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         check=True, capture_output=True, text=True).stdout.strip()
    return float(out)


def frames(video, out, scale, quality):
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    fps = (FRAMES + 0.5) / duration(video)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={fps},{scale}", "-frames:v", str(FRAMES),
                    "-c:v", "libwebp", "-quality", str(quality), "-compression_level", "6", str(out / "%04d.webp")], check=True)
    files = sorted(out.glob("*.webp"))
    size = sum(f.stat().st_size for f in files) / 1e6
    print(f"{out}: {len(files)} frames, {size:.1f} MB (quality {quality})")
    return size


def tall_frames(video, out):
    for q, w, h in TALL_STEPS:
        size = frames(video, out, f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}", q)
        if size <= TALL_BUDGET_MB:
            break


def main():
    args = sys.argv[1:]
    wide = None
    if "--wide" in args:
        i = args.index("--wide")
        wide = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    tall, out = Path(args[0]), Path(args[1])
    tall_frames(tall, out / "m")
    if wide:
        frames(wide, out / "d", "scale=1280:-2:flags=lanczos", 55)


if __name__ == "__main__":
    main()
