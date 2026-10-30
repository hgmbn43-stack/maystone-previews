"""Maystone preview builder: turn lead rows into personalised preview websites.

Usage:
  python3 build_preview.py LEADS.csv OUT_DIR [--ids L001,L007] [--live]
  python3 build_preview.py --demo OUT_DIR

LEADS.csv is the Leads tab exported as CSV (columns: Lead ID, Business, Trade,
Town, Phone, Google rating, Google reviews, Google Maps). With --ids only those
leads are built; otherwise every row with a phone number is.

Each lead gets OUT_DIR/<lead-id>-<name>/index.html plus any library photos in
img/. A manifest.csv lists what was built, so the sheet's Preview link column
can be filled in once the pages are hosted.

--live drops the preview ribbon and noindex tag (for a signed-up client).
Photos: put example images in images/<group>/ (e.g. images/plumbing/1.jpg).
They show tagged "Example photo"; with none, tiles show "Your photo here".
"""
import csv
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from trades import NEARBY, POSTCODES, PRICES, STEPS, TRADES, group_for

HERE = Path(__file__).resolve().parent
try:
    CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    CONFIG = {}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SCHEMA_TYPE = {
    "plumbing": "Plumber", "electrical": "Electrician", "roofing": "RoofingContractor",
    "building": "GeneralContractor", "decorating": "HousePainter", "local": "LocalBusiness",
}

DEMOS = [
    {"Lead ID": "DEMO1", "Business": "Harbour Heating & Plumbing", "Trade": "Plumber", "Town": "Worthing",
     "Phone": "07700 900417", "Google rating": "4.9", "Google reviews": "38", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO2", "Business": "Downland Roofing", "Trade": "Roofing contractor", "Town": "Lancing",
     "Phone": "01903 960123", "Google rating": "4.6", "Google reviews": "12", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO3", "Business": "Fairlight Decorating", "Trade": "Painter", "Town": "Brighton",
     "Phone": "07700 900862", "Google rating": "", "Google reviews": "0", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO4", "Business": "Saltmarsh Gardens Ltd", "Trade": "Landscaper", "Town": "Littlehampton",
     "Phone": "07700 900235", "Google rating": "5", "Google reviews": "21", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO5", "Business": "Brightwire Electrical", "Trade": "Electrician", "Town": "Hove",
     "Phone": "07700 900590", "Google rating": "5", "Google reviews": "7", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO6", "Business": "Flintstone Plastering", "Trade": "Plasterer", "Town": "Shoreham-by-Sea",
     "Phone": "07700 900318", "Google rating": "4.8", "Google reviews": "16", "Google Maps": "https://www.google.com/maps"},
]


def tidy_name(name):
    """Fix ALL CAPS or all-lowercase names; leave mixed case alone."""
    name = re.sub(r"\s+", " ", (name or "")).strip().rstrip(",")
    letters = re.sub(r"[^A-Za-z]", "", name)
    if letters and (letters.isupper() or letters.islower()) and len(letters) > 3:
        name = name.title()
        name = re.sub(r"\bLtd\b\.?", "Ltd", name)
    return name


def initials(name):
    words = [w for w in re.findall(r"[A-Za-z0-9]+", name) if w.lower() not in ("and", "the", "ltd", "limited", "of", "co")]
    return "".join(w[0] for w in words[:2]).upper() or name[:1].upper()


def tel_link(phone):
    digits = re.sub(r"\D", "", phone or "")
    return "+44" + digits[1:] if digits.startswith("0") else digits


def whatsapp_link(phone):
    digits = re.sub(r"\D", "", phone or "")
    return f"https://wa.me/44{digits[1:]}" if digits.startswith("07") and len(digits) == 11 else ""


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


def library_images(group):
    folder = HERE / "images" / group
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXT)


def build_one(env, row, out_root, preview=True, details=None, lead_dir=None, domain=""):
    """details: what the customer sent through the details form (business, phone, creds, company).
    lead_dir: folder with the customer's own photos: hero.*, side.*, logo.*, 1.*, 2.* ..."""
    details = details or {}
    slug_name = tidy_name(row.get("Business"))  # the link never changes, even if they rename
    name = tidy_name(details.get("business") or row.get("Business"))
    if not name or name.lower() in ("none", "null"):
        return None, "no business name"
    phone = (details.get("phone") or row.get("Phone") or "").strip()
    if not phone:
        return None, "no phone"
    group = group_for(row.get("Trade"), name)
    t = dict(TRADES[group], steps=STEPS)
    cred_values = details.get("creds") or {}          # by label, or
    cred_list = details.get("creds_list") or []        # by position: [registration, insurance/guarantee]
    t["creds"] = [dict(c, value=str(cred_values.get(c["label"]) or (cred_list[i] if i < len(cred_list) else "") or "").strip())
                  for i, c in enumerate(t["creds"])]
    town = (row.get("Town") or "").strip() or "your area"

    try:
        rating = float(row.get("Google rating") or "")
    except ValueError:
        rating = None
    try:
        reviews = int(float(row.get("Google reviews") or 0))
    except ValueError:
        reviews = 0
    if rating is None:
        reviews = 0

    lead_id = (row.get("Lead ID") or "lead").strip()
    out_dir = out_root / f"{lead_id}-{slugify(slug_name)}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "assets").mkdir(exist_ok=True)
    shutil.copyfile(HERE / "assets" / "archivo.woff2", out_dir / "assets" / "archivo.woff2")

    # Photo library: images/<group>/ holds hero.*, side.*, before.*, after.* and
    # gallery photos named 1.*, 2.* ... Any slot without a file shows a placeholder.
    own_files = sorted(p for p in lead_dir.iterdir() if p.suffix.lower() in IMAGE_EXT) if lead_dir and lead_dir.is_dir() else []
    own = any(p.stem.lower() != "logo" for p in own_files)
    # Library (example) photos only on previews; a live site shows the customer's own photos or none.
    files = own_files if own else (library_images(group) if preview else [])
    by_stem = {p.stem.lower(): p for p in files}
    img_dir = out_dir / "img"

    def place(src_path, name):
        img_dir.mkdir(exist_ok=True)
        dest = img_dir / f"{name}{src_path.suffix.lower()}"
        shutil.copyfile(src_path, dest)
        return f"img/{dest.name}"

    img = {slot: place(by_stem[slot], slot) for slot in ("hero", "side", "before", "after") if slot in by_stem}
    numbered = sorted((p for p in files if p.stem.isdigit()), key=lambda p: int(p.stem))
    gallery = []
    if own:
        # customer's own photos: first ones double as hero/side if they didn't pick them
        if "hero" not in img and numbered:
            img["hero"] = place(numbered[0], "hero")
        if "side" not in img and len(numbered) > 1:
            img["side"] = place(numbered[1], "side")
        captions = details.get("captions") or {}
        for i, p in enumerate(numbered[:9]):
            gallery.append({"caption": str(captions.get(p.stem, "")), "src": place(p, f"g{i + 1}")})
    else:
        for i, caption in enumerate(t["gallery"]):
            src = place(numbered[i], f"g{i + 1}") if i < len(numbered) else ""
            gallery.append({"caption": caption, "src": src})
    logo = next((p for p in own_files if p.stem.lower() == "logo"), None)

    biz = {
        "name": name, "initials": initials(name), "town": town, "town_longest": max(len(w) for w in re.split(r"[-\s]", town)), "phone": phone, "tel": tel_link(phone),
        "whatsapp": whatsapp_link(phone), "reviews": reviews,
        "rating_str": f"{rating:.1f}" if rating is not None else "",
        "rating_pct": round(rating / 5 * 100) if rating is not None else 0,
        "maps": (row.get("Google Maps") or "").strip() or "https://www.google.com/maps",
        "is_ltd": bool(re.search(r"\b(ltd|limited)\b", name, re.I)),
        "logo": place(logo, "logo") if logo else "",
    }
    areas = [town] + [a for a in NEARBY.get(town, []) if a != town]
    # Rating rules: show it from 4.0 up; only animate (count up) a strong rating.
    biz["show_rating"] = bool(reviews) and rating is not None and rating >= 4.0
    biz["animate_rating"] = biz["show_rating"] and rating >= 4.5
    biz["pc_example"] = (POSTCODES.get(town) or [town])[0]

    # Services with guide prices for the "rough price" tool. Guide prices are example
    # ranges, so they only appear on previews, never on a customer's live site.
    services = []
    for (title, blurb), band in zip(t["services"], PRICES.get(group, [])):
        item = {"title": title, "blurb": blurb, "low": None, "high": None, "unit": ""}
        if band and preview:
            item.update(low=band[0], high=band[1], unit=band[2] if len(band) > 2 else "")
        services.append(item)
    t["services_full"] = services
    price_json = [x for x in services if x["low"] is not None]
    coverage = [{"name": a, "pc": POSTCODES.get(a, [])} for a in areas]
    schema = {
        "@context": "https://schema.org", "@type": SCHEMA_TYPE.get(group, "HomeAndConstructionBusiness"),
        "name": name, "telephone": biz["tel"], "areaServed": areas,
        "address": {"@type": "PostalAddress", "addressLocality": town, "addressCountry": "GB"},
    }
    # Google place ID from the Maps link: previews load the listing's own photos and reviews live.
    m = re.search(r"place_id[:=]([A-Za-z0-9_-]{10,})", row.get("Google Maps") or "")
    place_id = m.group(1) if m else ""
    html = env.get_template("call_me.html").render(
        biz=biz, t=t, gallery=gallery, img=img, areas=areas, preview=preview, year=date.today().year,
        lead_id=lead_id, pay={"once": CONFIG.get("pay_once", ""), "monthly": CONFIG.get("pay_monthly", "")},
        track=CONFIG.get("track", ""), places_key=CONFIG.get("places_key", "") if preview else "", place_id=place_id, own=own, canonical=f"https://{domain}/" if domain else "", legal={"company": str(details.get("company") or "").strip()},
        schema_json=json.dumps(schema).replace("</", "<\\/"),
        price_json=json.dumps(price_json).replace("</", "<\\/"),
        coverage_json=json.dumps(coverage).replace("</", "<\\/"),
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    return {"Lead ID": lead_id, "Business": name, "Group": group, "Path": str(out_dir / "index.html")}, None


def main():
    args = sys.argv[1:]
    preview = "--live" not in args
    args = [a for a in args if a != "--live"]
    ids = None
    if "--ids" in args:
        i = args.index("--ids")
        ids = {x.strip() for x in args[i + 1].split(",")}
        del args[i:i + 2]

    if args and args[0] == "--demo":
        rows, out_root = DEMOS, Path(args[1])
    elif len(args) == 2:
        with open(args[0], encoding="utf-8-sig") as f:
            rows = [r for r in csv.DictReader(f) if (r.get("Lead ID") or "").strip()]
        out_root = Path(args[1])
    else:
        sys.exit(__doc__)
    if ids:
        rows = [r for r in rows if r.get("Lead ID", "").strip() in ids]

    env = Environment(loader=FileSystemLoader(HERE / "templates"), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)
    out_root.mkdir(parents=True, exist_ok=True)
    built, skipped = [], []
    for row in rows:
        result, reason = build_one(env, row, out_root, preview)
        if result:
            built.append(result)
        else:
            skipped.append(f"{row.get('Lead ID')}: {reason}")

    with open(out_root / "manifest.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Lead ID", "Business", "Group", "Path"])
        w.writeheader()
        w.writerows(built)
    print(f"built {len(built)} previews in {out_root}")
    if skipped:
        print("skipped:", "; ".join(skipped))


if __name__ == "__main__":
    main()
