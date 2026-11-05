"""python3 sheet.py GROUP [kinds...] -> GROUP/sheet.jpg: one column per film, rows = kinds (default after)."""
import sys
from PIL import Image, ImageDraw
from plan import FILMS
group = sys.argv[1]
kinds = sys.argv[2:] or ['after']
W, H = 216, 384
ims = []
cols = len(FILMS[group])
sheet = Image.new('RGB', (cols * (W + 6), len(kinds) * (H + 6) + 22), 'white')
dr = ImageDraw.Draw(sheet)
for c, f in enumerate(FILMS[group]):
    dr.text((c * (W + 6) + 4, 4), f"{c} {f[0]}", fill='black')
    for r, k in enumerate(kinds):
        try:
            im = Image.open(f"{group}/{f[0]}_{k}.png").convert('RGB').resize((W, H))
            sheet.paste(im, (c * (W + 6), 22 + r * (H + 6)))
        except OSError:
            pass
sheet.save(f"{group}/sheet_{'_'.join(kinds)}.jpg", quality=82)
print(f"{group}/sheet_{'_'.join(kinds)}.jpg", sheet.size)
