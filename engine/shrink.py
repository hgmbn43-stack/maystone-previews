"""Shrink the built previews so far more fit under GitHub Pages' 1 GB cap (25 Nov 2026).

Run after build_all.py and publish_clients.py (customers' own-domain sites are copied out before this).
Pages look exactly the same; only where files are stored changes:
  1. Fonts and photos that every preview carried its own copy of are stored once in p/_shared/f/<hash>.<ext>.
  2. Each page's inline styling is moved into p/_shared/css/<hash>.css files. The part every preview shares is
     stored once; the few lines that differ per preview (colours, film) go in their own small file.
  3. Files in assets/ or img/ that no page refers to (library photos the template doesn't use) are dropped.
     Every other file (e.g. a preview's own film/ frames, loaded by script) is left exactly where it is.
Files are named by their content, so a shared file is never edited: a change makes a new file.
Writes p/_index.json (every preview folder) for the live checks.

Usage: python engine/shrink.py [p]
"""
import collections
import hashlib
import json
import os
import posixpath
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "p"
SH = os.path.join(ROOT, "_shared")
REF = re.compile(r'''(?<=["'(])((?:\.\./)*(?:assets|img)/[^"')?#\s]+)''')
STYLE = re.compile(r"<style([^>]*)>(.*?)</style>", re.S)
URL = re.compile(r'''url\((["']?)([^"')]+)\1\)''')


def h(b):
    return hashlib.sha1(b).hexdigest()[:12]


def rules(css):
    """Split CSS into top-level rules, keeping every character (comments, strings, nested @media)."""
    out, i, n, depth, start, q = [], 0, len(css), 0, 0, None
    while i < n:
        c = css[i]
        if q:
            if c == "\\":
                i += 2
                continue
            if c == q:
                q = None
        elif css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = j + 2 if j >= 0 else n
            continue
        elif c in "\"'":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                out.append(css[start:i + 1])
                start = i + 1
        elif c == ";" and depth == 0:
            out.append(css[start:i + 1])
            start = i + 1
        i += 1
    if css[start:]:
        out.append(css[start:])
    return out


def write_shared(name, data):
    dst = os.path.join(ROOT, name)
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)


def main():
    os.makedirs(os.path.join(SH, "f"), exist_ok=True)
    os.makedirs(os.path.join(SH, "css"), exist_ok=True)
    css_text, css_pv, pages_with_css, previews = {}, collections.defaultdict(set), [], []
    moved = dropped = 0
    for pv in sorted(os.listdir(ROOT)):
        pdir = os.path.join(ROOT, pv)
        if pv.startswith("_") or not os.path.isdir(pdir):
            continue
        previews.append(pv)
        pages, files, used = [], {}, set()
        for d, _, fs in os.walk(pdir):
            for f in fs:
                full = os.path.join(d, f)
                if f.endswith(".html"):
                    pages.append(full)
                else:
                    rel = posixpath.relpath(full, pdir).replace(os.sep, "/")
                    if rel.startswith(("assets/", "img/")):   # anything else (e.g. a preview's own film/ frames) is left exactly where it is
                        files[rel] = full

        def shared(rel):
            with open(files[rel], "rb") as fh:
                data = fh.read()
            name = "_shared/f/" + h(data) + os.path.splitext(rel)[1].lower()
            write_shared(name, data)
            used.add(rel)
            return name

        for page in pages:
            with open(page, encoding="utf-8") as fh:
                s = fh.read()
            pd = posixpath.normpath(posixpath.relpath(os.path.dirname(page), pdir).replace(os.sep, "/"))
            page_dir = posixpath.normpath(posixpath.join(pv, pd))      # relative to ROOT

            def target(ref):
                return posixpath.normpath(posixpath.join(pd, ref))

            def css_out(m):
                attrs, css = m.group(1), m.group(2)
                if re.search(r"\bmedia\s*=", attrs):
                    return m.group(0)                                    # leave unusual blocks inline
                css = REF.sub(lambda mm: posixpath.relpath(shared(target(mm.group(1))), "_shared/css")
                              if target(mm.group(1)) in files else mm.group(1), css)

                def any_url(mm):
                    u = mm.group(2)
                    if re.match(r"(?:[a-z]+:|/|#|\.\./f/)", u):
                        return mm.group(0)
                    return "url(" + mm.group(1) + posixpath.relpath(posixpath.normpath(posixpath.join(page_dir, u)), "_shared/css") + mm.group(1) + ")"
                css = URL.sub(any_url, css)
                k = h(css.encode("utf-8"))
                css_text[k] = css
                css_pv[k].add(pv)
                return "<!--MS-CSS:%s-->" % k

            s = STYLE.sub(css_out, s)

            # A CSS variable holding a photo in a style="" attribute (e.g. --qb-img: url('img/fb/x.jpg')) is read by the
            # shared stylesheet, and browsers resolve it from there, so point it at the photo from _shared/css/.
            def var_url(mm):
                ref = mm.group(3)
                if not re.match(r"(?:\.\./)*(?:assets|img)/", ref) or target(ref) not in files:
                    return mm.group(0)
                return mm.group(1) + mm.group(2) + posixpath.relpath(shared(target(ref)), "_shared/css") + mm.group(2) + ")"
            s = re.sub(r'''(--[\w-]+\s*:\s*url\()(['"]?)([^'")]+)\2\)''', var_url, s)
            s = REF.sub(lambda mm: posixpath.relpath(shared(target(mm.group(1))), page_dir)
                        if target(mm.group(1)) in files else mm.group(1), s)
            with open(page, "w", encoding="utf-8") as fh:
                fh.write(s)
            if "<!--MS-CSS:" in s:
                pages_with_css.append(page)
        for rel, full in files.items():
            os.remove(full)
            moved += rel in used
            dropped += rel not in used
        for d, _, _ in sorted(os.walk(pdir), reverse=True):
            if not os.listdir(d):
                os.rmdir(d)

    # Styling: rules used by 2+ previews are shared; consecutive runs keep their order (so the cascade is unchanged).
    seen = collections.defaultdict(set)
    for k, css in css_text.items():
        for r in rules(css):
            seen[r.strip()].update(css_pv[k])
    chunks = {}
    for k, css in css_text.items():
        assert "".join(rules(css)) == css
        runs = []
        for r in rules(css):
            common = len(seen[r.strip()]) >= 2
            if runs and (runs[-1][0] == common or not r.strip()):
                runs[-1][1] += r
            else:
                runs.append([common, r])
        names = []
        for _, txt in runs:
            b = txt.encode("utf-8")
            name = "_shared/css/" + h(b) + ".css"
            write_shared(name, b)
            names.append(name)
        chunks[k] = names
    for page in pages_with_css:
        with open(page, encoding="utf-8") as fh:
            s = fh.read()
        pr = posixpath.relpath(os.path.dirname(page), ROOT).replace(os.sep, "/")
        s = re.sub(r"<!--MS-CSS:(\w+)-->", lambda m: "".join(
            '<link rel="stylesheet" href="%s">' % posixpath.relpath(x, pr) for x in chunks[m.group(1)]), s)
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(s)
    with open(os.path.join(ROOT, "_index.json"), "w") as fh:
        json.dump(previews, fh)
    print(f"shrink: {len(previews)} previews, {moved} files shared, {dropped} unused files dropped, "
          f"{len(os.listdir(os.path.join(SH, 'css')))} style files, {len(os.listdir(os.path.join(SH, 'f')))} shared files")


if __name__ == "__main__":
    main()
