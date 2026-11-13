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
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from trades import BRAND, FILM_TIMING, FILMS, NEARBY, POSTCODES, PRICES, SCENES, STEPS, TRADES, group_for

HERE = Path(__file__).resolve().parent
try:
    CONFIG = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    CONFIG = {}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SCHEMA_TYPE = {
    "plumbing": "Plumber", "electrical": "Electrician", "roofing": "RoofingContractor",
    "building": "GeneralContractor", "decorating": "HousePainter", "local": "LocalBusiness",
    "cafe": "CafeOrCoffeeShop",
}

DEMOS = [
    {"Lead ID": "DEMO1", "Business": "Harbour Heating & Plumbing", "Trade": "Plumber", "Town": "Worthing",
     "Phone": "07700 900417", "Google rating": "4.9", "Google reviews": "38", "Google Maps": "https://www.google.com/maps"},
    {"Lead ID": "DEMO2", "Business": "Downland Roofing", "Trade": "Roofing contractor", "Town": "Lancing", "Look": "brand",
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


def film_library(group):
    """Films for a trade group that have their frames in place, in library order."""
    out = []
    for f in FILMS.get(group, []):
        folder = HERE / "films" / group / f["id"]
        tall = sorted((folder / "m").glob("*.webp")) if (folder / "m").is_dir() else []
        if tall:
            out.append(dict(f, folder=folder, frames=len(tall), wide=(folder / "d" / "0001.webp").exists()))
    return out


def area_of(town):
    """A town plus its neighbours: two leads in the same area never share a film."""
    town = (town or "").strip()
    near = set(NEARBY.get(town, [])) | {t for t, n in NEARBY.items() if town in n}
    return ({town} | near) if town else set()


def lead_order(lead_id):
    m = re.match(r"([A-Za-z]*)(\d*)", lead_id or "")
    return (m.group(1), int(m.group(2) or 0), lead_id or "")


def assign_films(rows):
    """Pick a library film for every lead. Leads are taken in ID order, so a lead keeps its film when
    later leads arrive. A film already used in the lead's area is only reused when the library runs out.
    Films whose kind of job matches the business name come first (e.g. "heating" -> boiler films).
    films/pins.json can fix a lead to a film: {"L002": "bathroom-01"}."""
    try:
        pins = json.loads((HERE / "films" / "pins.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pins = {}
    used, out = {}, {}
    for row in sorted(rows, key=lambda r: lead_order(r.get("Lead ID"))):
        lead_id = (row.get("Lead ID") or "").strip()
        name = tidy_name(row.get("Business"))
        group = group_for(row.get("Trade"), name)
        library = film_library(group)
        if not lead_id or not library:
            continue
        town = (row.get("Town") or "").strip()
        taken = set()
        for t in area_of(town):
            taken |= used.get(t, set())
        words = f"{name} {row.get('Trade') or ''}".lower()
        ids = [f["id"] for f in library]
        if pins.get(lead_id) in ids:
            choice = pins[lead_id]
        else:
            def rank(f):
                scene = SCENES.get(f.get("scene"), {})
                liked = any(w in words for w in scene.get("prefer", []))
                return (f["id"] in taken, not liked, hashlib.sha1(f"{lead_id}/{f['id']}".encode()).hexdigest())
            choice = sorted(library, key=rank)[0]["id"]
        out[lead_id] = choice
        used.setdefault(town, set()).add(choice)
    return out


def film_context(film, base, label):
    """Everything the template needs about one film: frames, colours, captions and timing."""
    scene = SCENES.get(film.get("scene"), SCENES["bathroom"])
    beats = [{"eyebrow": e, "line": l, "from": a, "to": z}
             for (e, l), (a, z) in zip(film.get("beats") or scene["beats"], FILM_TIMING["beats"])]
    ctx = {k: v for k, v in film.items() if k not in ("folder",)}
    ctx.update(base=base, label=label, beats=beats, end_from=FILM_TIMING["end_from"], hook_to=FILM_TIMING["hook_to"],
               hook=film.get("hook") or scene["hook"], hook_sub=film.get("hook_sub") or scene["hook_sub"],
               quote_words=film.get("quote_words") or scene["quote_words"])
    return ctx


BADGES = [("Checkatrade", r"checka ?trade"), ("TrustMark", r"trust ?mark"), ("Gas Safe registered", r"gas ?safe"),
          ("NICEIC", r"niceic"), ("NAPIT", r"napit"), ("Federation of Master Builders", r"\bfmb\b|master builders"),
          ("Which? Trusted Trader", r"which\??\s*trusted"), ("TrustATrader", r"trust ?a ?trader"),
          ("Guild of Master Craftsmen", r"guild of master"), ("Painting & Decorating Association", r"\bpda\b|painting (and|&) decorating assoc"),
          ("CHAS", r"\bchas\b"), ("Constructionline", r"constructionline"), ("Competent Roofer", r"competent roofer"),
          ("OFTEC", r"\boftec\b"), ("HETAS", r"\bhetas\b")]
from service_copy import COPY, HELP  # noqa: E402

NOUN = {"kitchens_bathrooms": "Kitchen & bathroom fitter", "handyman": "Handyman", "local": "Local business"}


def _join(items):
    items = [i for i in items if i]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


def write_subpages(env, out_dir, home_html, group, t, biz, areas, svc_pages, area_pages, preview, canonical, badges, address):
    """Service, area and contact pages. They reuse the home page's styles so the whole site matches."""
    m = re.search(r"<style>(.*?)</style>", home_html, re.S)
    css = m.group(1) if m else ""
    noun = NOUN.get(group) or (t.get("cta_noun") or t["label"]).capitalize()
    btype = SCHEMA_TYPE.get(group, "HomeAndConstructionBusiness")
    provider = {"@type": btype, "name": biz["name"], "telephone": biz["tel"], "areaServed": areas[:5],
                "address": {"@type": "PostalAddress", "addressLocality": biz["town"], "addressCountry": "GB"}}
    if address:
        provider["address"]["streetAddress"] = address
    town, name, phone = biz["town"], biz["name"], biz["phone"]
    others = [a for a in areas[1:4]]
    rating_line = (f"Customers rate us {biz['rating_str']} out of 5 from {biz['reviews']} Google review{'s' if biz['reviews'] != 1 else ''}."
                   if biz.get("show_rating") else "")
    contact_line = (f"Call {phone}{', or send a photo of the job on WhatsApp,' if biz.get('whatsapp') else ''} "
                    "and we'll talk it through and give you a clear price before any work starts.")
    faqs = list(t.get("faqs") or [])
    pages = []
    for i, sp in enumerate(svc_pages):
        sv = sp["sv"]
        copy = (COPY.get(group) or {}).get(sv["title"]) or {}
        guide = {"low": sv["low"], "high": sv["high"], "unit": sv.get("unit", "")} if sv.get("low") is not None else None
        pages.append(dict(kind="service", path=sp["path"], job=sv["title"],
            title=f"{sv['title']} in {town} | {name}",
            description=f"{sv['title']} in {town} and nearby from {name}. {sv['blurb']} Call {phone}.",
            crumbs=["Services", sv["title"]], kicker=t["label"], h1=f"{sv['title']} in {town}", lede=sv["blurb"],
            includes=copy.get("includes") or [], signs=copy.get("signs") or [],
            paras=[p for p in [
                copy.get("intro", ""),
                f"{name} is a local {(t.get('cta_noun') or 'business')} based in {town}" + (f", covering {_join(others)} and the villages around them." if others else "."),
                f"Need help with {sv['title'][0].lower() + sv['title'][1:]}? {contact_line}",
                rating_line] if p],
            guide=guide, faqs=[faqs[(i + k) % len(faqs)] for k in range(min(2, len(faqs)))] if faqs else [],
            schema={"@context": "https://schema.org", "@type": "Service", "serviceType": sv["title"], "areaServed": areas[:5], "provider": provider}))
    for ap in area_pages:
        a = ap["name"]
        svc_names = [s["name"][0].lower() + s["name"][1:] for s in svc_pages[:3]]
        home = a == town
        pages.append(dict(kind="area", path=ap["path"], job="",
            title=f"{noun} in {a} | {name}",
            description=f"{name}: {t['label'].lower()} in {a}. {('Based in ' + town) if home else ('Local to ' + a + ', based in ' + town)}. Call {phone}.",
            crumbs=["Areas", a], kicker="Areas we cover", h1=f"{noun} in {a}",
            lede=(f"Based in {town}, {name} works across {town} and the surrounding area." if home
                  else f"{name} covers {a} from our base in {town}, close by."),
            paras=[p for p in [
                f"From {_join(svc_names)} to smaller jobs, we're a local {(t.get('cta_noun') or 'business')} who know {a}." if svc_names else "",
                contact_line, rating_line] if p],
            postcodes=POSTCODES.get(a) or [], guide=None, faqs=faqs[-2:] if not home else faqs[:2],
            schema=dict(provider, **{"@context": "https://schema.org", "areaServed": a})))
    pages.append(dict(kind="contact", path="contact/", job="",
        title=f"Contact {name} | {t['label']} in {town}",
        description=f"Get in touch with {name}, {t['label'].lower()} in {town}. Call {phone}.",
        crumbs=["Contact"], kicker="Contact", h1="Get in touch.", lede=f"{contact_line}",
        paras=[], guide=None, faqs=[],
        schema={"@context": "https://schema.org", "@type": "ContactPage", "about": provider}))
    tpl = env.get_template("subpage.html")
    for pg in pages:
        depth = pg["path"].strip("/").count("/") + 1
        root = "../" * depth
        page_css = css.replace('url("assets/', f'url("{root}assets/')
        pg["schema"] = json.dumps(pg["schema"]).replace("</", "<\\/")
        out = tpl.render(page=pg, root=root, css=page_css, biz=biz, t=t, areas=areas[:5], svc_pages=svc_pages,
                         area_pages=area_pages, preview=preview, canonical=canonical, badges=badges, address=address,
                         year=date.today().year)
        dest = out_dir / pg["path"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
    if canonical:   # live sites: a sitemap for Google
        urls = [""] + [pg["path"] for pg in pages]
        (out_dir / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{canonical}{u}</loc></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
        (out_dir / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {canonical}sitemap.xml\n", encoding="utf-8")


def build_one(env, row, out_root, preview=True, details=None, lead_dir=None, domain="", film_id=None):
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
    # Scroll film (signature hero). A customer's own film (made from their real before and after photos,
    # in leads/<ID>/film/) comes first; otherwise the library film picked by assign_films. Previews share the
    # library frames in engine/films/; a live site gets its own copy so it can move to the customer's domain.
    film = None
    own_film = lead_dir / "film" if lead_dir else None
    library = film_library(group)
    if own_film and (own_film / "m" / "0001.webp").exists():
        shutil.copytree(own_film, out_dir / "film", dirs_exist_ok=True)
        try:
            meta = json.loads((own_film / "film.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = {}
        base_film = dict(library[0] if library else {}, **meta)
        base_film.update(frames=len(list((own_film / "m").glob("*.webp"))), wide=(own_film / "d" / "0001.webp").exists())
        base_film.setdefault("alt", "One of our real jobs, from before to finished")
        film = film_context(base_film, "film/", "Made from our real job photos")
    elif library:
        chosen = next((f for f in library if f["id"] == film_id), library[0])
        if preview:
            base = os.path.relpath(chosen["folder"], out_dir).replace(os.sep, "/") + "/"
        else:
            shutil.copytree(chosen["folder"], out_dir / "film", dirs_exist_ok=True)
            base = "film/"
        film = film_context(chosen, base, "Example film" if preview else "Illustration")
    # BRAND look (13 Nov 2026): premium photo first screen instead of the film, when the lead asks for it.
    brand = None
    if film and str(row.get("Look") or "").strip().lower() == "brand" and group in BRAND:
        bd = dict(BRAND[group])
        hero_src = HERE / "heroes" / (bd["hero"] + "-wide.webp")
        if preview:
            rel = os.path.relpath(HERE / "heroes", out_dir).replace(os.sep, "/") + "/"
        else:
            (out_dir / "hero").mkdir(parents=True, exist_ok=True)
            for size in ("wide", "tall"):
                shutil.copy(HERE / "heroes" / f"{bd['hero']}-{size}.webp", out_dir / "hero" / f"{bd['hero'].split('/')[-1]}-{size}.webp")
            rel, bd["hero"] = "hero/", bd["hero"].split("/")[-1]
        if hero_src.exists():
            bd.update(wide=f"{rel}{bd['hero']}-wide.webp", tall=f"{rel}{bd['hero']}-tall.webp",
                      sub=bd["sub"].format(town=biz["town"]), label="Example photo" if preview else "")
            brand = bd
    # Extra pages (10 Nov 2026): one per service, one per town covered (home town + up to 4 nearby), and Contact.
    # Film pages only; a cafe stays one page (menu, hours and map are all on it).
    multi = bool(film) and not t.get("venue")
    svc_pages = [{"name": sv["title"], "path": f"services/{slugify(sv['title'])}/", "sv": sv} for sv in services] if multi else []
    area_pages = [{"name": a, "path": f"areas/{slugify(a)}/"} for a in areas[:5]] if multi else []
    # Badges: named in the details form's "Registrations and memberships" box (or a badges list). Only ones they say they have.
    reg_text = " ".join([str(x) for x in (details.get("creds_list") or [])[:1]] + [str(v) for v in (details.get("creds") or {}).values()])
    badges = [str(b).strip() for b in (details.get("badges") or []) if str(b).strip()]
    for label, pat in BADGES:
        if re.search(pat, reg_text, re.I) and label not in badges:
            badges.append(label)
    address = str(details.get("address") or "").strip()
    pcs = sorted(POSTCODES.get(town) or [], key=lambda c: (re.sub(r"\d", "", c), int(re.sub(r"\D", "", c) or 0)))
    same_area = len({re.sub(r"\d", "", c) for c in pcs}) == 1
    pc_label = f"{pcs[0]}–{pcs[-1]}" if len(pcs) > 1 and same_area else (pcs[0] if pcs else "")
    html = env.get_template("film.html" if film else "call_me.html").render(
        film=film, pc_label=pc_label,
        biz=biz, t=t, gallery=gallery, img=img, areas=areas, preview=preview, year=date.today().year,
        lead_id=lead_id, pay={"once": CONFIG.get("pay_once", ""), "monthly": CONFIG.get("pay_monthly", "")},
        track=CONFIG.get("track", ""), places_key=CONFIG.get("places_key", "") if preview else "", place_id=place_id, own=own, canonical=f"https://{domain}/" if domain else "", legal={"company": str(details.get("company") or "").strip()},
        svc_pages=svc_pages, area_pages=area_pages, badges=badges, address=address, brand=brand,
        help=(HELP.get(group) or []) if film and not t.get("venue") else [],
        hide_photos=[int(x) for x in re.findall(r"\d+", str(row.get("Hide photos") or ""))],
        schema_json=json.dumps(schema).replace("</", "<\\/"),
        price_json=json.dumps(price_json).replace("</", "<\\/"),
        coverage_json=json.dumps(coverage).replace("</", "<\\/"),
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")
    if multi:
        write_subpages(env, out_dir, html, group=group, t=t, biz=biz, areas=areas, svc_pages=svc_pages, area_pages=area_pages,
                       preview=preview, canonical=f"https://{domain}/" if domain else "", badges=badges, address=address)
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
    films = assign_films(rows)
    for row in rows:
        result, reason = build_one(env, row, out_root, preview, film_id=films.get((row.get("Lead ID") or "").strip()))
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
