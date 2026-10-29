"""Build every lead in leads/*.json into p/<lead-id>-<slug>/ (run by GitHub Actions).

Each JSON file is written by the Google Sheet's script when a rep marks a lead "yes":
{"Lead ID": "L090", "Business": "...", "Trade": "...", "Town": "...", "Phone": "...",
 "Google rating": "4.9", "Google reviews": "93", "Google Maps": "https://..."}

The folder name must match the sheet script's link: slug = lowercase name with runs of
non-letters/digits turned into "-", trimmed of "-", first 40 characters.
"""
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_preview import HERE, build_one  # noqa: E402

ROOT = HERE.parent


def main():
    env = Environment(loader=FileSystemLoader(HERE / "templates"), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    out_root = ROOT / "p"
    out_root.mkdir(exist_ok=True)
    built = 0
    for f in sorted((ROOT / "leads").glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            live = bool(data.get("live"))
            row = {k: str(v) for k, v in data.items() if k != "live"}
        except (ValueError, OSError) as e:
            print(f"skip {f.name}: {e}")
            continue
        result, reason = build_one(env, row, out_root, preview=not live)
        if result:
            built += 1
            print("built", result["Path"])
        else:
            print(f"skip {f.name}: {reason}")
    print(f"built {built}")


if __name__ == "__main__":
    main()
