"""Clean look (25 Nov 2026): makes previews look less like stock.

The big UK trade sites (Pimlico, Aspect, iHeat, Heat in London) never show stock photos of tradesmen at work.
They show their own van or engineer, the result (a warm home, a finished room) or plain icons. So, with
copy.look = "clean":
  1. their own photo goes at the top (copy.photos.wide/tall), set per lead;
  2. service rows show a simple line icon instead of a stock photo (their own tile photos are kept);
  3. any stock photo left (top, About, quote band) gets one colour grade in the site's palette, so they look
     like one shoot instead of six photographers.
"""
import re

from trades import CLEAN

_S = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>'
ICONS = {
    "flame": '<path d="M12 3c1 3.5 5 5.5 5 10a5 5 0 0 1-10 0c0-2.4 1.2-3.8 2.3-5 .3 1.6 1.2 2.6 2.2 2.6C11.3 8.3 11 5.6 12 3z"/>',
    "drop": '<path d="M12 3.5c3 4 6 7.2 6 10.5a6 6 0 0 1-12 0c0-3.3 3-6.5 6-10.5z"/><path d="M9.5 14.5a2.6 2.6 0 0 0 2.5 2.5"/>',
    "radiator": '<rect x="3" y="6" width="18" height="11" rx="1.5"/><path d="M7 6v11M11 6v11M15 6v11M19 6v11M5 17v2M19 17v2"/>',
    "bath": '<path d="M3 12h18v2a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5v-2zM6 12V5.5A1.5 1.5 0 0 1 7.5 4c.8 0 1.5.7 1.5 1.5M7 19l-1 2M17 19l1 2"/>',
    "shower": '<path d="M5 21V8a4 4 0 0 1 4-4h1a4 4 0 0 1 4 4"/><path d="M11 9h6"/><path d="M12 13v1M14 12.5v1M16 13v1M13 16v1M15 16v1"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0 5 5L21 13l-8 8-3-3 6.3-6.3-1.6-1.6L8 16.4 5.6 14l6.3-6.3a4 4 0 0 0 2.8-1.4z"/><path d="M3 21l2.5-2.5"/>',
    "bolt": '<path d="M13 2 4.5 13.5H12l-1 8.5 8.5-11.5H12z"/>',
    "plug": '<path d="M9 3v5M15 3v5M6 8h12v3a6 6 0 0 1-12 0V8zM12 17v4"/>',
    "bulb": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    "shield": '<path d="M12 3 4.5 6v5.5c0 4.5 3.2 8.2 7.5 9.5 4.3-1.3 7.5-5 7.5-9.5V6L12 3z"/><path d="m9 12 2 2 4-4"/>',
    "car": '<path d="M5 16V11l2-5h10l2 5v5M3 16h18v2H3zM7 11h10"/><circle cx="7.5" cy="18.5" r="1.5"/><circle cx="16.5" cy="18.5" r="1.5"/>',
    "roof": '<path d="M2.5 12 12 4l9.5 8"/><path d="M5 10v10h14V10"/><path d="M15 6V3.5h2.5v4.6"/>',
    "house": '<path d="M3 11 12 4l9 7"/><path d="M5 9.5V20h14V9.5"/><path d="M10 20v-5h4v5"/>',
    "gutter": '<path d="M3 7h18v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/><path d="M17 11v9M15 20h4"/>',
    "brick": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 9.7h18M3 14.3h18M9 5v4.7M15 5v4.7M6 9.7v4.6M12 9.7v4.6M18 9.7v4.6M9 14.3V19M15 14.3V19"/>',
    "brush": '<path d="M4 4h12v5H4zM16 6.5h3v5h-7v3"/><rect x="10.5" y="14.5" width="3" height="6.5" rx="1"/>',
    "roller": '<rect x="3" y="4" width="14" height="5" rx="1"/><path d="M17 6.5h3v5h-8v3"/><rect x="10.5" y="14.5" width="3" height="6.5" rx="1"/>',
    "leaf": '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-4 6-7 10-9"/>',
    "sprout": '<path d="M12 21v-9M12 12c0-4-3-6-7-6 0 4 3 6 7 6zM12 14c0-4 3-6.5 7-6.5 0 4-3 6.5-7 6.5zM8 21h8"/>',
    "tree": '<path d="M12 21v-6M12 3l6 8h-3l4 4H5l4-4H6z"/>',
    "fence": '<path d="M4 8l1.5-3L7 8v12H4zM10.5 8 12 5l1.5 3v12h-3zM17 8l1.5-3L20 8v12h-3zM7 11h3.5M13.5 11H17M7 16h3.5M13.5 16H17"/>',
    "paving": '<path d="M3 20 7 4h10l4 16z"/><path d="M5 12h14M12 4v16M8.5 12 7.5 20M15.5 12l1 8"/>',
    "kitchen": '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 10h18M12 10v10M9 7h1M14 7h1M9.5 14v2M14.5 14v2"/>',
    "tiles": '<rect x="3.5" y="3.5" width="7.5" height="7.5"/><rect x="13" y="3.5" width="7.5" height="7.5"/><rect x="3.5" y="13" width="7.5" height="7.5"/><rect x="13" y="13" width="7.5" height="7.5"/>',
    "floor": '<path d="M3 17 9 7h12l-6 10zM6 12h12M9 7l-3 10M15 7l-3 10"/>',
    "door": '<path d="M6 21V3h12v18M3 21h18"/><circle cx="15" cy="12" r=".8"/>',
    "stairs": '<path d="M3 20h5v-4h4v-4h4V8h5"/>',
    "wardrobe": '<rect x="4" y="3" width="16" height="17" rx="1"/><path d="M12 3v17M10 11h.5M13.5 11h.5M6 20v1.5M18 20v1.5"/>',
    "saw": '<path d="M3 15 15 3l3 3L6 18z"/><path d="M7 11l1 1M10 8l1 1M13 5l1 1M18 6l3 3-2 2-3-3"/>',
    "hammer": '<path d="M14 4h5l1 4-3 1-1-2h-3"/><path d="M14 4 11.5 6.5 13 8l1.5-1.5M12.5 7.5 4 16l3 3 8.5-8.5"/>',
    "box": '<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5z"/><path d="M3 7.5 12 12l9-4.5M12 12v9"/>',
    "drill": '<path d="M4 7h11v5H4zM15 8.5h5M8 12l-1.5 8h4L12 12"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.4-4.4"/>',
    "check": '<path d="M4 12.5 9.5 18 20 6"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
    "sparkle": '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"/>',
}
# Every rule that matches a service is a candidate, in order; each row takes the first icon not already used,
# so three boiler services get a flame, a spanner and a shield rather than three flames.
RULES = [
    (r"radiator|underfloor", "radiator"), (r"tiling", "tiles"), (r"fuse|consumer|board", "bolt"), (r"chimney", "brick"), (r"flat roof", "house"), (r"\bev\b|charger", "car"), (r"loft", "stairs"), (r"knock", "door"),
    (r"exterior", "house"), (r"wallpaper", "tiles"), (r"woodwork", "door"), (r"plant|bed|flower", "sprout"), (r"rewir|wiring", "plug"),
    (r"repair|fault|breakdown", "wrench"), (r"servic|maint", "check"),
    (r"install|replace", "box"), (r"boiler|heating|gas|cylinder|heat pump", "flame"),
    (r"shower", "shower"), (r"bath|tap|toilet|sink|basin|wet ?room", "bath"),
    (r"leak|burst|pipe|drain|water|softener|blockage", "drop"),
    (r"\bev\b|charger|car", "car"), (r"fuse|consumer|board|rewire|wiring", "bolt"), (r"socket|plug", "plug"),
    (r"light", "bulb"), (r"eicr|safety|inspect|certif|test|survey|report", "shield"), (r"electr", "bolt"),
    (r"gutter|fascia|soffit", "gutter"), (r"chimney|roof|slate|flat roof|lead", "roof"),
    (r"brick|wall|point|block|knock", "brick"), (r"extension|loft|conversion|build|renovat|refurb", "house"),
    (r"wallpaper|paint|decor", "roller"), (r"woodwork|varnish|stain", "brush"),
    (r"kitchen|cabinet", "kitchen"), (r"tiling|tile", "tiles"), (r"floor|skirting|laminate|carpet", "floor"),
    (r"door|frame|window", "door"), (r"stair", "stairs"), (r"wardrobe|cupboard|storage|shelv", "wardrobe"),
    (r"deck|joinery|bespoke|carpent", "saw"), (r"patio|paving|driveway|path", "paving"), (r"fenc|gate", "fence"),
    (r"tree|hedge", "tree"), (r"turf|lawn|plant|bed|garden|landscap", "leaf"),
    (r"flat[- ]?pack|assembl", "box"), (r"hang|fix|mount|shelf|tv", "drill"), (r"clean", "sparkle"),
    (r"landlord|letting|propert", "key"), (r"odd job|small job|general", "hammer"),
    (r"design|plan|quote", "search"), (r"emergency|24", "clock"),
]
SPARE = ["hammer", "wrench", "check", "shield", "clock", "search", "sparkle", "key"]


def icons_for(titles):
    used, out = set(), []
    for title in titles:
        t = (title or "").lower()
        cands = [name for pat, name in RULES if re.search(pat, t)] + SPARE
        pick = next((c for c in cands if c not in used), cands[0])
        used.add(pick)
        out.append(_S.format(ICONS[pick]))
    return out


def icon_for(title):
    return icons_for([title])[0]


def _u(pid, w, h=None):
    return f"https://images.unsplash.com/{pid}?w={w}" + (f"&h={h}" if h else "") + "&q=78&auto=format&fit=crop"


def apply(brand, services, copy, preview, group=None):
    """Turn the clean look on for one lead's brand dict. services: list of dicts with "title"."""
    if not brand or copy.get("look") != "clean":
        return
    brand["clean"] = True
    set_by_hand = (copy.get("photos") or {})
    if copy.get("hero") == "type":   # no photo up top at all: their name, big, in their colours
        brand["type_hero"], brand["label"] = True, ""
    if group in CLEAN:
        hero, about = CLEAN[group]
        if not set_by_hand.get("wide"):
            brand["wide"], brand["tall"] = _u(hero, 1920), _u(hero, 900, 1600)
        if not set_by_hand.get("about") and not brand.get("about_own"):
            brand["about_img"] = _u(about, 900, 1125)
    own_tiles = all(str(x).startswith("img/fb/") for x in (brand.get("tiles") or [])) and brand.get("tiles")
    if not own_tiles:
        brand["icons"] = icons_for([sv.get("title") if isinstance(sv, dict) else sv[0] for sv in services])
    brand["hero_stock"] = bool(brand.get("label"))
    brand["about_stock"] = not brand.get("about_own") and not str(brand.get("about_img") or "").startswith("img/fb/")
