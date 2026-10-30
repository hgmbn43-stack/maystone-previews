"""Turn a renovation film (video) into the scroll frames the film template plays.

Usage:
  python3 engine/film_frames.py TALL.mp4 OUT_DIR [--wide WIDE.mp4]

Writes OUT_DIR/m/0001.webp ... (64 frames, 540x960, about 2 MB) from a tall 9:16 film and, with --wide,
OUT_DIR/d/0001.webp ... (64 frames, 1280px wide) from a 16:9 film. Needs ffmpeg.

Library film:   OUT_DIR = engine/films/<group>/<film id>   (then add it to FILMS in trades.py)
Customer film:  OUT_DIR = leads/<lead id>/film             (optional leads/<lead id>/film/film.json with
                "scene", "hook", "hook_sub" or "beats" to change the captions)
"""
import shutil
import subprocess
import sys
from pathlib import Path

FRAMES = 64


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
    print(f"{out}: {len(files)} frames, {size:.1f} MB")


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
    frames(tall, out / "m", "scale=540:960:force_original_aspect_ratio=increase:flags=lanczos,crop=540:960", 44)
    if wide:
        frames(wide, out / "d", "scale=1280:-2:flags=lanczos", 55)


if __name__ == "__main__":
    main()
