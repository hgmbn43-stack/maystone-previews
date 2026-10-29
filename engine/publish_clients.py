"""Publish every paid customer that has a domain to its own GitHub Pages site (run by GitHub Actions).

For each leads/<ID>.json with "live": true and a "domain", the built site in p/<ID>-<slug>/ is
copied into its own repo <owner>/site-<id> with a CNAME file, and GitHub Pages is switched on
with that custom domain. Unchanged sites are left alone.

Needs env CLIENT_TOKEN: a GitHub token that can create repos and manage Pages for the owner
(fine-grained: All repositories, Administration + Contents + Pages read/write).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_preview import slugify, tidy_name  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("CLIENT_TOKEN", "")
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", "hgmbn43-stack")
DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))+$")


def api(method, path, body=None):
    req = urllib.request.Request(
        "https://api.github.com/" + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except ValueError:
            return e.code, {"message": raw.decode(errors="replace")}


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, stdout=subprocess.DEVNULL)


def publish(lead_id, domain, site_dir):
    repo = f"site-{lead_id.lower()}"
    code, _ = api("GET", f"repos/{OWNER}/{repo}")
    if code == 404:
        code, body = api("POST", "user/repos", {"name": repo, "auto_init": True, "private": False,
                                                 "description": f"Website for {domain} (built by Maystone)"})
        if code != 201:
            raise RuntimeError(f"create repo {repo}: {code} {body.get('message')}")
    remote = f"https://x-access-token:{TOKEN}@github.com/{OWNER}/{repo}.git"
    with tempfile.TemporaryDirectory() as tmp:
        git("clone", "-q", "--depth", "1", remote, tmp, cwd=ROOT)
        for item in Path(tmp).iterdir():
            if item.name != ".git":
                shutil.rmtree(item) if item.is_dir() else item.unlink()
        shutil.copytree(site_dir, tmp, dirs_exist_ok=True)
        (Path(tmp) / "CNAME").write_text(domain + "\n")
        (Path(tmp) / ".nojekyll").write_text("")
        robots = Path(tmp) / "robots.txt"
        robots.write_text(f"User-agent: *\nAllow: /\nSitemap: https://{domain}/sitemap.xml\n")
        (Path(tmp) / "sitemap.xml").write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"<url><loc>https://{domain}/</loc></url></urlset>\n")
        git("add", "-A", cwd=tmp)
        changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=tmp).returncode != 0
        if changed:
            git("-c", "user.name=Maystone", "-c", "user.email=hello@maystone.uk", "commit", "-qm", "Update site", cwd=tmp)
            git("push", "-q", "origin", "HEAD", cwd=tmp)
    code, pages = api("GET", f"repos/{OWNER}/{repo}/pages")
    if code == 404:
        branch = api("GET", f"repos/{OWNER}/{repo}")[1].get("default_branch", "main")
        code, body = api("POST", f"repos/{OWNER}/{repo}/pages", {"source": {"branch": branch, "path": "/"}})
        if code not in (201, 409):
            raise RuntimeError(f"enable pages {repo}: {code} {body.get('message')}")
        pages = {}
    if pages.get("cname") != domain:
        api("PUT", f"repos/{OWNER}/{repo}/pages", {"cname": domain})
    elif not pages.get("https_enforced") and (pages.get("https_certificate") or {}).get("state") == "approved":
        api("PUT", f"repos/{OWNER}/{repo}/pages", {"cname": domain, "https_enforced": True})
    return "updated" if changed else "unchanged"


def main():
    if not TOKEN:
        print("CLIENT_TOKEN not set: skipping own-domain sites")
        return
    for f in sorted((ROOT / "leads").glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        domain = str(data.get("domain") or "").strip().lower()
        if not (data.get("live") and domain):
            continue
        if not DOMAIN_RE.match(domain):
            print(f"{f.stem}: bad domain {domain!r}")
            continue
        site = ROOT / "p" / f"{f.stem}-{slugify(tidy_name(data.get('Business')))}"
        if not (site / "index.html").exists():
            print(f"{f.stem}: site not built")
            continue
        try:
            print(f"{f.stem} -> {domain}: {publish(f.stem, domain, site)}")
        except Exception as e:  # keep going for the others
            print(f"{f.stem} -> {domain}: FAILED {e}")


if __name__ == "__main__":
    main()
