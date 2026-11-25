"""Safety check 2 (25 Nov 2026): the shrunk previews look the same as the originals.

Needs the repo served at http://localhost:8765/ with the unshrunk copy in p_orig/ and the shrunk one in p/.
Screenshots N random previews (home page + one inner page, phone size) both ways and compares the pixels.
Nothing outside localhost loads (no Google calls, no view tracking). Animations are frozen. A page passes when
under 0.1% of its pixels differ (a moving ticker can shift a few pixels between any two loads, even of the
same page); a real problem (missing styling, font or photo) changes far more than that. Exits 1 on failure.
Usage: python engine/visual_check.py [N]
"""
import io
import json
import os
import random
import sys

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

FREEZE = ("document.addEventListener('DOMContentLoaded',()=>{const s=document.createElement('style');"
          "s.textContent='*,*::before,*::after{animation:none!important;transition:none!important}';document.head.appendChild(s);});")


def shot(browser, url):
    ctx = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    page = ctx.new_page()
    page.route("**/*", lambda r: r.continue_() if r.request.url.startswith("http://localhost:8765/") else r.abort())
    page.add_init_script(FREEZE)
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.querySelectorAll('img[loading=\"lazy\"]').forEach(i=>{i.loading='eager'})")
    page.evaluate("Promise.race([new Promise(r=>setTimeout(r,6000)),Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})))])")
    page.wait_for_timeout(2000)
    img = Image.open(io.BytesIO(page.screenshot(full_page=True))).convert("RGB")
    ctx.close()
    return img


def share_different(a, b):
    if a.size != b.size:
        return 1.0
    d = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 16 else 0)
    return d.histogram()[255] / (a.size[0] * a.size[1])


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    previews = json.load(open("p/_index.json"))
    pick = random.sample(previews, min(n, len(previews)))
    bad = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for pv in pick:
            subs = [""]
            if os.path.isdir(f"p/{pv}/services"):
                subs.append("services/" + sorted(os.listdir(f"p/{pv}/services"))[0] + "/")
            for sub in subs:
                best = 1.0
                for _ in range(3):
                    best = min(best, share_different(shot(browser, f"http://localhost:8765/p_orig/{pv}/{sub}"),
                                                     shot(browser, f"http://localhost:8765/p/{pv}/{sub}")))
                    if best < 0.001:
                        break
                ok = best < 0.001
                print(("same      " if ok else "DIFFERENT ") + f"{pv}/{sub}  ({best * 100:.3f}% of pixels differ)")
                if not ok:
                    bad.append(f"{pv}/{sub}")
        browser.close()
    if bad:
        print("Visual check failed:", ", ".join(bad))
        sys.exit(1)
    print("Visual check passed")


if __name__ == "__main__":
    main()
