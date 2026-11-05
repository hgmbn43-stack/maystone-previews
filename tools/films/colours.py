"""Pick each film's colours from its stills.
accent      = the strongest colour in the part of the picture the work changed (falls back to the whole picture),
              set to a mid lightness so dark text on it passes 4.5:1
accent_ink  = darker version for small text on the light ground (>= 4.5:1)
accent_dark = lighter version for dark mode text on #15191d (>= 4.5:1)
ground      = very light page background tinted towards the picture's overall colour
python3 colours.py GROUP [GROUP...]  -> prints JSON and writes colours.json"""
import json, sys
import numpy as np
from PIL import Image
from plan import FILMS

def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055) * 255

M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
WHITE = np.array([0.95047, 1.0, 1.08883])

def rgb_to_lab(rgb):
    xyz = srgb_to_lin(rgb) @ M.T / WHITE
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)

def lab_to_rgb(lab):
    L, a, b = lab
    fy = (L + 16) / 116; fx = fy + a / 500; fz = fy - b / 200
    f = np.array([fx, fy, fz])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * WHITE
    lin = np.linalg.solve(M, xyz)
    return lin

def to_hex(L, C, h):
    """Lab colour from lightness, chroma, hue; chroma is reduced until it fits in sRGB."""
    for c in np.linspace(C, 0, 60):
        lin = lab_to_rgb((L, c * np.cos(h), c * np.sin(h)))
        if (lin >= -1e-4).all() and (lin <= 1 + 1e-4).all():
            rgb = lin_to_srgb(lin)
            return '#%02x%02x%02x' % tuple(int(round(v)) for v in rgb)
    return '#808080'

def lum(hexc):
    rgb = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], float)
    return float(srgb_to_lin(rgb) @ np.array([0.2126, 0.7152, 0.0722]))

def contrast(x, y):
    a, b = sorted([lum(x), lum(y)], reverse=True)
    return (a + 0.05) / (b + 0.05)

def kmeans(X, w, k=5, it=25):
    rng = np.random.default_rng(1)
    C = X[rng.choice(len(X), k, replace=False)]
    for _ in range(it):
        lab = ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
        for j in range(k):
            m = lab == j
            if m.any():
                C[j] = (X[m] * w[m, None]).sum(0) / w[m].sum()
    return C, lab

OVERRIDE = {
    "lounge-01": "#4f6b55", "hallway-04": "#8a9c84", "cabinets-05": "#8c9c80", "panelling-08": "#3d5a80",
    "kitchen-01": "#3c5a7d", "floor-tiles-04": "#4f7fb0", "utility-09": "#7f9a83", "alcove-01": "#3f5f86",
    "understairs-09": "#86a08c",
}

def pick(group, fid):
    a = np.asarray(Image.open(f"{group}/{fid}_after.png").convert('RGB').resize((120, 214)), float)
    b = np.asarray(Image.open(f"{group}/{fid}_before.png").convert('RGB').resize((120, 214)), float)
    la, lb = rgb_to_lab(a), rgb_to_lab(b)
    diff = np.sqrt(((la - lb) ** 2).sum(-1))
    Lc, ac, bc = la[..., 0], la[..., 1], la[..., 2]
    chroma = np.hypot(ac, bc)
    hue = np.degrees(np.arctan2(bc, ac)) % 360
    rows = np.arange(214)[:, None] * np.ones((1, 120))
    sky = (hue > 200) & (hue < 290) & (rows < 214 * 0.4)
    upper = rows < 214 * 0.68          # leave out the floor / lawn / drive at the bottom where captions sit
    foliage = (hue > 95) & (hue < 160) & (group != 'gardens')
    ok = (chroma >= 12) & (Lc > 22) & (Lc < 88) & ~sky & upper
    changed = ok & (diff > 22)
    sel = changed if changed.sum() > 0.015 * diff.size else ok & ~foliage
    if sel.sum() < 0.01 * diff.size:
        sel = ok
    if sel.sum() < 50:
        sel = (Lc > 20) & (Lc < 90)
    X = np.stack([ac[sel], bc[sel], Lc[sel] * 0.3], -1)
    w = chroma[sel] + 1
    C, lab = kmeans(X, w)
    best, score = None, -1
    for j in range(len(C)):
        n = (lab == j).sum()
        if n == 0:
            continue
        c = np.hypot(C[j, 0], C[j, 1])
        s = c * np.sqrt(n)
        if s > score:
            best, score = C[j], s
    h = np.arctan2(best[1], best[0])
    Cc = float(np.clip(np.hypot(best[0], best[1]) * 1.1, 22, 50))
    if fid in OVERRIDE:   # hand-picked source colour (e.g. the painted walls or units the film is about)
        rgb = np.array([int(OVERRIDE[fid][i:i + 2], 16) for i in (1, 3, 5)], float)
        _, oa, ob = rgb_to_lab(rgb)
        h, Cc = np.arctan2(ob, oa), float(np.clip(np.hypot(oa, ob) * 1.1, 22, 50))
    # ground: picture's average tint, very light
    ma, mb = float(np.median(ac)), float(np.median(bc))
    gh, gc = np.arctan2(mb, ma), float(min(4.5, np.hypot(ma, mb) * 0.35))
    ground = to_hex(94.2, gc, gh)
    for L in range(62, 50, -1):
        accent = to_hex(L, Cc, h)
        if contrast(accent, '#16110a') >= 5.0:
            break
    for L in range(42, 20, -1):
        ink = to_hex(L, Cc * 0.85, h)
        if contrast(ink, ground) >= 4.8:
            break
    for L in range(72, 90):
        dark = to_hex(L, Cc * 0.8, h)
        if contrast(dark, '#15191d') >= 6:
            break
    return {"accent": accent, "accent_ink": ink, "accent_dark": dark, "ground": ground,
            "checks": [round(contrast(accent, '#16110a'), 2), round(contrast(ink, ground), 2), round(contrast(dark, '#15191d'), 2)]}

if __name__ == '__main__':
    try:
        out = json.load(open('colours.json'))
    except OSError:
        out = {}
    for g in sys.argv[1:]:
        for f in FILMS[g]:
            out.setdefault(g, {})[f[0]] = pick(g, f[0])
            print(g, f[0], out[g][f[0]])
    json.dump(out, open('colours.json', 'w'), indent=1)
