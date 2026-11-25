"""Safety check 1 (25 Nov 2026): every preview page can find every shared file it needs.

Local:  python engine/check_site.py p                      -> checks the built files on disk
Live:   python engine/check_site.py --live URL [N] [IDS]   -> opens N random previews on the real site
        (plus any preview whose folder starts with one of the comma-separated IDS) and checks every
        shared file they use loads. Live checks never count as a customer view (pages are fetched as
        text; no scripts run).
Exits 1 if anything is missing, so the deploy stops (or GitHub emails the failure).
"""
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urljoin

REF = re.compile(r'''(?:href|src)="([^"#?]*_shared/[^"#?]+)"''')
URL = re.compile(r'''url\(["']?(\.\./f/[^"')]+)''')


def local(root):
    missing, pages, previews = [], 0, 0
    for pv in os.listdir(root):
        pdir = os.path.join(root, pv)
        if pv.startswith("_") or not os.path.isdir(pdir):
            continue
        previews += 1
        if not os.path.exists(os.path.join(pdir, "index.html")):
            missing.append(pv + "/index.html")
        for d, _, fs in os.walk(pdir):
            for f in fs:
                if not f.endswith(".html"):
                    continue
                pages += 1
                s = open(os.path.join(d, f), encoding="utf-8").read()
                for ref in REF.findall(s):
                    if not os.path.exists(os.path.normpath(os.path.join(d, ref))):
                        missing.append(os.path.join(d, f) + " -> " + ref)
    css_dir = os.path.join(root, "_shared", "css")
    for f in os.listdir(css_dir) if os.path.isdir(css_dir) else []:
        for ref in URL.findall(open(os.path.join(css_dir, f), encoding="utf-8").read()):
            if not os.path.exists(os.path.normpath(os.path.join(css_dir, ref))):
                missing.append("_shared/css/" + f + " -> " + ref)
    print(f"check: {previews} previews, {pages} pages, {len(missing)} missing")
    for m in missing[:30]:
        print("MISSING", m)
    return not missing


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "maystone-check"}), timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if i == tries - 1:
                return e.code, ""
        except Exception:
            if i == tries - 1:
                return 0, ""
        time.sleep(10)


def live(site, n, ids):
    site = site.rstrip("/") + "/"
    code, body = get(site + "p/_index.json")
    if code != 200:
        print("live check: could not load the preview list:", code)
        return False
    previews = json.loads(body)
    pick = [p for p in previews if any(p.startswith(i + "-") for i in ids)]
    pick += random.sample([p for p in previews if p not in pick], min(n, len(previews) - len(pick)))
    bad, seen = [], set()
    for pv in pick:
        page = site + "p/" + pv + "/"
        code, html = get(page)
        if code != 200:
            bad.append(f"{code} {page}")
            continue
        for ref in set(REF.findall(html)):
            u = urljoin(page, ref)
            if u in seen:
                continue
            seen.add(u)
            c, css = get(u)
            if c != 200:
                bad.append(f"{c} {u}")
            elif u.endswith(".css"):
                for r in set(URL.findall(css)):
                    v = urljoin(u, r)
                    if v not in seen:
                        seen.add(v)
                        if get(v)[0] != 200:
                            bad.append(f"missing {v}")
    print(f"live check: {len(pick)} previews, {len(seen)} shared files, {len(bad)} problems")
    for b in bad[:30]:
        print("PROBLEM", b)
    return not bad


if __name__ == "__main__":
    if sys.argv[1] == "--live":
        ok = live(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12,
                  [i for i in (sys.argv[4] if len(sys.argv) > 4 else "").split(",") if i])
    else:
        ok = local(sys.argv[1])
    sys.exit(0 if ok else 1)
