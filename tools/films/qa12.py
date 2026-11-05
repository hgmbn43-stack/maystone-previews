"""python3 qa12.py GROUP PART -> GROUP/qa_PART.jpg: 5 films per sheet (PART 0 = films 1-5, 1 = 6-10),
12 frames each between 12% and 92% of the film, to spot ghost hands, people and glitches."""
import subprocess, sys, os, io
from PIL import Image, ImageDraw
from plan import FILMS
group, part = sys.argv[1], int(sys.argv[2])
ids = [f[0] for f in FILMS[group]][part * 5:part * 5 + 5]
W, H, N = 150, 267, 12
sheet = Image.new('RGB', (N * (W + 3) + 110, len(ids) * (H + 3)), 'white')
dr = ImageDraw.Draw(sheet)
for r, fid in enumerate(ids):
    v = f"{group}/{fid}_video.mp4"
    dr.text((2, r * (H + 3) + 4), fid, fill='black')
    if not os.path.exists(v):
        continue
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v], capture_output=True, text=True).stdout)
    for c in range(N):
        t = dur * (0.12 + 0.8 * c / (N - 1))
        png = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', v, '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        im = Image.open(io.BytesIO(png)).convert('RGB').resize((W, H))
        sheet.paste(im, (110 + c * (W + 3), r * (H + 3)))
out = f"{group}/qa_{part}.jpg"
sheet.save(out, quality=78)
print(out, sheet.size)
