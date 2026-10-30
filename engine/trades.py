"""Trade settings for the CALL ME template.

Each trade group sets the colours, wording, services, FAQs, credential
placeholders and gallery captions. `group_for()` maps the Google category in
the lead sheet's Trade column to a group.

Rules for copy here:
- No claims about a specific business (no "24/7", "fixed price", "insured",
  years of experience). Those go in placeholders the client confirms.
- FAQ answers state general facts that are true for any UK trader.
"""
import re

STEPS = [
    ("Call or send a photo", "Tell us what you need. A quick photo of the job helps us price it."),
    ("Get a clear quote", "We explain what needs doing and what it costs before any work starts."),
    ("Job done properly", "The work is finished to a high standard and the area left clean and tidy."),
]

TRADES = {
    "plumbing": {
        "label": "Plumbing & heating",
        "kicker": "Plumber and heating engineer",
        "brand": "#0d3b66",
        "stripe": "#35a7d6",
        "promise": "Boilers, leaks, radiators and bathrooms, sorted by a local engineer.",
        "services_title": "Plumbing and heating",
        "services_intro": "From a dripping tap to a full boiler swap.",
        "services": [
            ("Boiler repairs", "Breakdowns, pressure loss, no heating or hot water."),
            ("Boiler installs", "Combi and system boiler replacements, sized for your home."),
            ("Boiler servicing", "Yearly services to keep your boiler safe and your warranty valid."),
            ("Leaks and burst pipes", "Finding and fixing leaks before they cause damage."),
            ("Radiators and heating", "New radiators, valves, power flushing and cold spots."),
            ("Bathrooms and taps", "Taps, toilets, showers and full bathroom plumbing."),
        ],
        "creds": [
            {"label": "Gas Safe registration number", "hint": "Add your number and we link it to the Gas Safe Register so customers can check it."},
            {"label": "Insurance and guarantees", "hint": "Your public liability cover and any workmanship guarantee."},
        ],
        "gallery": ["Combi boiler install", "New radiator fitted", "New walk-in shower", "Boiler service", "Kitchen tap replaced", "Leak repair"],
        "gallery_intro": "A look at recent installs and repairs.",
        "quote_intro": "Tell us what's wrong or what you're planning. Add a photo of the boiler or the problem and we'll get back to you with a price.",
        "faqs": [
            ("How often should my boiler be serviced?", "Once a year. Most manufacturers need a yearly service to keep the warranty valid, and it catches faults early."),
            ("Do you need to be Gas Safe registered to work on a boiler?", "Yes. By law, anyone working on gas appliances in the UK must be on the Gas Safe Register. You can check any engineer's number on the Gas Safe website."),
            ("Can you do landlord gas safety certificates?", "Landlords need a gas safety check every 12 months by a Gas Safe registered engineer. Ask us when you call and we'll book it in."),
            ("What should I do if I smell gas?", "Call the National Gas Emergency number on 0800 111 999 straight away, open windows and don't use switches or flames."),
        ],
    },
    "electrical": {
        "label": "Electrician",
        "kicker": "Electrician",
        "brand": "#20262e",
        "stripe": "#f2b705",
        "promise": "Rewires, fuse boards, lighting and safety checks by a local electrician.",
        "services_title": "Electrical work",
        "services_intro": "Homes, rentals and small businesses.",
        "services": [
            ("Fault finding", "Tripping switches, dead sockets and power cuts traced and fixed."),
            ("Fuse board upgrades", "Old fuse boxes replaced with modern consumer units."),
            ("EICR safety reports", "Electrical condition reports for landlords and home buyers."),
            ("Rewires", "Full and partial rewires for older properties."),
            ("Lighting and sockets", "New lights, extra sockets, outdoor and garden lighting."),
            ("EV chargers", "Home car charger installs."),
        ],
        "creds": [
            {"label": "NICEIC or NAPIT registration", "hint": "Add your scheme and number so customers know your work is certified."},
            {"label": "Insurance and guarantees", "hint": "Your public liability cover and any workmanship guarantee."},
        ],
        "gallery": ["New consumer unit", "Kitchen lighting", "Garden lighting", "Rewire in progress", "EV charger install", "Extra sockets"],
        "gallery_intro": "Recent installs and upgrades.",
        "quote_intro": "Tell us what you need doing. A photo of your fuse board or the problem helps us quote faster.",
        "faqs": [
            ("What is an EICR?", "An Electrical Installation Condition Report checks the safety of the wiring in a property. Landlords in England need one at least every 5 years."),
            ("Do I need a certificate for new electrical work?", "Most new circuits and fuse board changes are notifiable under Part P of the Building Regulations. A registered electrician can self-certify the work and give you a certificate."),
            ("How do I know if my fuse board needs replacing?", "Signs include old rewireable fuses, no RCD protection, scorch marks or switches that keep tripping. We can check it for you."),
            ("How long does a rewire take?", "A typical three-bed house takes around 5 to 10 days, depending on the size and how much is being done."),
        ],
    },
    "building": {
        "label": "Builder",
        "kicker": "Builder",
        "brand": "#5c2a1e",
        "stripe": "#e0a43a",
        "promise": "Extensions, renovations and building work, managed from start to finish.",
        "services_title": "Building work",
        "services_intro": "Small repairs through to full projects.",
        "services": [
            ("Extensions", "Single and double storey extensions, from plans to finish."),
            ("Renovations", "Whole-house refurbishments and room makeovers."),
            ("Loft conversions", "Turning unused loft space into bedrooms and offices."),
            ("Brickwork and walls", "Garden walls, repointing and structural brickwork."),
            ("Knock-throughs", "Opening up rooms with the right steel and sign-off."),
            ("General building", "Repairs, alterations and smaller jobs."),
        ],
        "creds": [
            {"label": "Trade memberships", "hint": "For example Federation of Master Builders or TrustMark, with your member number."},
            {"label": "Insurance and guarantees", "hint": "Your public liability cover and any insurance-backed guarantee."},
        ],
        "gallery": ["Rear extension", "Open-plan kitchen", "Loft conversion", "Garden wall", "Renovation", "Knock-through"],
        "gallery_intro": "Projects from across the area.",
        "quote_intro": "Tell us about your project: what you want built, rough size and when you'd like to start.",
        "faqs": [
            ("Do I need planning permission for an extension?", "Many single storey extensions fall under permitted development, but it depends on size, location and previous work. We can talk you through it."),
            ("What's the difference between planning permission and building regulations?", "Planning covers how a project looks and affects neighbours. Building regulations cover how it's built safely. Most building work needs building regs sign-off even when planning isn't needed."),
            ("How long does an extension take?", "A typical single storey extension takes around 10 to 14 weeks on site, once plans and approvals are in place."),
            ("Can I cancel after agreeing a quote?", "If you agree a contract at home, by phone or online, you usually have 14 days to cancel under consumer law."),
        ],
    },
    "plastering": {
        "label": "Plastering",
        "kicker": "Plasterer",
        "brand": "#34444f",
        "stripe": "#d9c7a7",
        "promise": "Smooth walls and ceilings, rendering and repairs by a local plasterer.",
        "services_title": "Plastering",
        "services_intro": "Clean, flat finishes ready for decorating.",
        "services": [
            ("Skimming", "Smooth new finish over walls and ceilings."),
            ("Re-plastering", "Hacking off old plaster and starting fresh."),
            ("Rendering", "Sand and cement and modern through-colour renders."),
            ("Plasterboarding", "Boarding, dot and dab and stud walls."),
            ("Ceiling repairs", "Cracks, Artex covering and water damage fixed."),
            ("Coving and patching", "Coving fitted and small areas patched in."),
        ],
        "creds": [
            {"label": "Insurance", "hint": "Your public liability cover."},
            {"label": "Trade memberships and guarantees", "hint": "Any trade body membership and workmanship guarantee."},
        ],
        "gallery": ["Skimmed lounge ceiling", "Re-plastered bedroom", "Rendered house front", "Artex covered", "New stud wall", "Patch repair"],
        "gallery_intro": "Finished walls, ceilings and render.",
        "quote_intro": "Tell us which rooms and roughly how big. A photo of the walls or ceiling helps us price it.",
        "faqs": [
            ("How long before I can paint new plaster?", "Usually 3 to 7 days for a skim, longer for a full re-plaster. It goes from dark to light pink and even in colour when it's dry."),
            ("Can you plaster over Artex?", "Yes. Most Artex can be skimmed over after preparation. Older Artex may need testing for asbestos first."),
            ("Do I need to empty the room?", "It helps to clear as much as you can. Anything left is covered and the floor is protected."),
            ("Skim or re-plaster?", "If the existing plaster is sound, a skim is quicker and cheaper. If it's loose or hollow, it needs re-plastering."),
        ],
    },
    "carpentry": {
        "label": "Carpentry & joinery",
        "kicker": "Carpenter and joiner",
        "brand": "#4a3020",
        "stripe": "#d8954e",
        "promise": "Fitted furniture, doors, stairs and woodwork made and fitted locally.",
        "services_title": "Carpentry and joinery",
        "services_intro": "First fix, second fix and made-to-measure work.",
        "services": [
            ("Fitted wardrobes", "Built-in storage made to fit alcoves and eaves."),
            ("Doors and frames", "Internal doors hung, fire doors and frames."),
            ("Staircases", "Repairs, new balustrades and full replacements."),
            ("Flooring and skirting", "Wood floors, skirting boards and architrave."),
            ("Decking and garden", "Decks, pergolas and garden structures."),
            ("Bespoke joinery", "Shelving, cabinets and one-off pieces."),
        ],
        "creds": [
            {"label": "Insurance", "hint": "Your public liability cover."},
            {"label": "Trade memberships and guarantees", "hint": "Any trade body membership and workmanship guarantee."},
        ],
        "gallery": ["Alcove wardrobes", "New oak staircase", "Internal doors", "Garden decking", "Built-in shelving", "Skirting and architrave"],
        "gallery_intro": "Recent woodwork, made and fitted.",
        "quote_intro": "Tell us what you'd like made or fitted, with rough sizes if you have them. Photos of the space help.",
        "faqs": [
            ("Do you make furniture to measure?", "Yes. Fitted wardrobes and shelving are made to fit the exact space, including awkward alcoves and sloping ceilings."),
            ("Can you supply the materials?", "Materials can be supplied as part of the quote, or fitted using items you've bought yourself."),
            ("What is first fix and second fix?", "First fix is the structural work before plastering, like stud walls and floor joists. Second fix is the finishing work after, like doors, skirting and fitted furniture."),
            ("How long does a fitted wardrobe take?", "Most fitted wardrobes take 2 to 5 days on site, depending on size and finish."),
        ],
    },
    "decorating": {
        "label": "Painting & decorating",
        "kicker": "Painter and decorator",
        "brand": "#163f4f",
        "stripe": "#f0b84f",
        "promise": "Interior and exterior painting, wallpapering and woodwork with a clean finish.",
        "services_title": "Painting and decorating",
        "services_intro": "Single rooms, whole houses and outside work.",
        "services": [
            ("Interior painting", "Walls, ceilings and woodwork in any room."),
            ("Exterior painting", "Render, masonry, fascias, windows and doors."),
            ("Wallpapering", "Feature walls, lining paper and full rooms."),
            ("Woodwork and doors", "Skirting, doors, frames and banisters."),
            ("Kitchen cabinet painting", "Spray or brush finish to refresh units."),
            ("Prep and repairs", "Filling, sanding and making good before painting."),
        ],
        "creds": [
            {"label": "Insurance", "hint": "Your public liability cover."},
            {"label": "Trade memberships and guarantees", "hint": "For example the Painting & Decorating Association, and any guarantee."},
        ],
        "gallery": ["Living room repaint", "Feature wallpaper", "House front", "Painted kitchen units", "Hallway and stairs", "Front door"],
        "gallery_intro": "Rooms and homes recently finished.",
        "quote_intro": "Tell us which rooms or areas need doing. Photos help us give you a price faster.",
        "faqs": [
            ("Do you move furniture?", "Furniture is moved to the middle of the room and covered, and floors are protected with dust sheets."),
            ("Can I supply my own paint?", "Yes. Or paint can be supplied as part of the quote, in the brand and colour you choose."),
            ("When is the best time to paint outside?", "Late spring to early autumn, in dry weather above around 10 degrees, so paint can cure properly."),
            ("How long does a room take?", "An average bedroom takes 1 to 2 days, including preparation and two coats."),
        ],
    },
    "roofing": {
        "label": "Roofing",
        "kicker": "Roofer",
        "brand": "#262f38",
        "stripe": "#c4573a",
        "promise": "Roof repairs, new roofs, flat roofs and guttering by a local roofer.",
        "services_title": "Roofing",
        "services_intro": "Pitched and flat roofs, repairs and full replacements.",
        "services": [
            ("Roof repairs", "Slipped tiles, leaks and storm damage fixed."),
            ("New roofs", "Full strip and re-roof in tile or slate."),
            ("Flat roofs", "EPDM rubber and GRP fibreglass flat roofs."),
            ("Chimneys", "Repointing, flashing and chimney repairs."),
            ("Fascias and guttering", "uPVC fascias, soffits and gutters."),
            ("Roof inspections", "Checks with photos so you can see what's wrong."),
        ],
        "creds": [
            {"label": "Guarantees", "hint": "The guarantee you give on repairs and new roofs."},
            {"label": "Insurance and memberships", "hint": "Your public liability cover and any trade body, for example NFRC."},
        ],
        "gallery": ["New slate roof", "Flat roof in GRP", "Chimney repair", "New fascias and gutters", "Tile repair", "Roof inspection"],
        "gallery_intro": "Roofs recently repaired and replaced.",
        "quote_intro": "Tell us what's wrong or what you need. A photo of the roof or the leak helps us price it.",
        "faqs": [
            ("How long does a new roof last?", "A well-fitted tiled or slate roof can last 50 years or more. Flat roofs in EPDM or GRP typically last 20 to 30 years."),
            ("Is a leak always the roof?", "Not always. Leaks can come from flashing, chimneys, gutters or condensation. An inspection finds the real cause."),
            ("Do I need permission for a new roof?", "Replacing a roof like for like usually doesn't need planning permission, but it does need to meet building regulations."),
            ("Will my home insurance cover storm damage?", "Many policies cover sudden storm damage but not wear and tear. Photos and a written report help with a claim."),
        ],
    },
    "kitchens_bathrooms": {
        "label": "Kitchens, bathrooms & tiling",
        "kicker": "Kitchen, bathroom and tiling specialist",
        "brand": "#1d4b59",
        "stripe": "#8fd0c2",
        "promise": "New kitchens, bathrooms, tiling and floors, designed and fitted locally.",
        "services_title": "Kitchens, bathrooms and floors",
        "services_intro": "Supply and fit, or fit only.",
        "services": [
            ("Kitchen fitting", "Full kitchen installs, worktops and appliances."),
            ("Bathroom fitting", "Bathrooms, en suites and wet rooms."),
            ("Wall and floor tiling", "Ceramic, porcelain and natural stone."),
            ("Flooring", "LVT, laminate and engineered wood."),
            ("Showers", "Walk-in showers, trays and screens."),
            ("Design help", "Layouts and choices planned with you before work starts."),
        ],
        "creds": [
            {"label": "Guarantees", "hint": "Your workmanship guarantee and any insurance-backed cover."},
            {"label": "Gas and electrical work", "hint": "Who does the gas and electrics, and their Gas Safe or Part P registration."},
        ],
        "gallery": ["Shaker kitchen", "Walk-in shower", "Floor tiling", "Family bathroom", "LVT flooring", "Kitchen splashback"],
        "gallery_intro": "Kitchens, bathrooms and floors recently fitted.",
        "quote_intro": "Tell us about the room, what you'd like and rough sizes. Photos of the space help us price it.",
        "faqs": [
            ("How long does a bathroom refit take?", "Most bathrooms take 1 to 2 weeks, depending on tiling and any changes to the layout."),
            ("Can you fit a kitchen I've bought?", "Yes. Fit-only is common, as long as all parts are delivered before the start date."),
            ("Who does the plumbing, gas and electrics?", "Any gas work must be done by a Gas Safe registered engineer and most electrical changes must be certified. We'll tell you who does each part."),
            ("Can I cancel after agreeing a quote?", "If you agree a contract at home, by phone or online, you usually have 14 days to cancel under consumer law."),
        ],
    },
    "gardens": {
        "label": "Landscaping & gardens",
        "kicker": "Landscaper and gardener",
        "brand": "#24502e",
        "stripe": "#b7d464",
        "promise": "Patios, lawns, fencing and garden care from a local landscaper.",
        "services_title": "Gardens and landscaping",
        "services_intro": "New gardens built and existing ones kept tidy.",
        "services": [
            ("Patios and paving", "Porcelain, sandstone and block paving."),
            ("Fencing", "Panel, closeboard and feather-edge fencing and gates."),
            ("Turf and lawns", "New turf, artificial grass and lawn care."),
            ("Garden maintenance", "Regular mowing, hedges, weeding and tidy-ups."),
            ("Planting and beds", "Borders, raised beds and planting schemes."),
            ("Tree and hedge work", "Cutting back, shaping and clearing."),
        ],
        "creds": [
            {"label": "Waste carrier licence", "hint": "Needed if you take garden waste away. Add your CBDU number."},
            {"label": "Insurance and memberships", "hint": "Your public liability cover and any trade body, for example APL or BALI."},
        ],
        "gallery": ["Porcelain patio", "New fence panels", "Fresh turf", "Raised beds", "Hedge cut back", "Garden makeover"],
        "gallery_intro": "Gardens recently built and looked after.",
        "quote_intro": "Tell us about your garden and what you'd like done. Photos and rough sizes help us price it.",
        "faqs": [
            ("Do you take the garden waste away?", "Garden waste can be taken away as part of the job. Anyone carrying waste for you should have a waste carrier licence, which you can check on the Environment Agency register."),
            ("When is the best time to lay turf?", "Autumn and spring are best, when the ground is moist and not frozen."),
            ("Do I need permission to cut down a tree?", "If the tree has a Tree Preservation Order or you're in a conservation area, you need council consent first."),
            ("Can you do regular maintenance visits?", "Yes. Weekly, fortnightly or monthly visits can be arranged through the growing season."),
        ],
    },
    "handyman": {
        "label": "Handyman & property maintenance",
        "kicker": "Handyman",
        "brand": "#2a3640",
        "stripe": "#ff8a2a",
        "promise": "Odd jobs, repairs and maintenance done properly, with no job too small.",
        "services_title": "Jobs we do",
        "services_intro": "The small jobs that never get done.",
        "services": [
            ("Flat-pack assembly", "Furniture built and fixed to the wall safely."),
            ("Hanging and fixing", "Shelves, TVs, mirrors, pictures and curtain poles."),
            ("Small repairs", "Doors, locks, handles, sealant and leaky taps."),
            ("Painting touch-ups", "Single walls, doors and small decorating jobs."),
            ("Garden jobs", "Fence repairs, gutter clearing and tidy-ups."),
            ("Landlord maintenance", "Repairs between tenancies and regular upkeep."),
        ],
        "creds": [
            {"label": "Insurance", "hint": "Your public liability cover."},
            {"label": "DBS check", "hint": "If you have one, add it here. Many customers look for it."},
        ],
        "gallery": ["Shelves fitted", "TV wall mount", "Flat-pack wardrobe", "Door rehung", "Fence repair", "Bathroom resealed"],
        "gallery_intro": "Recent jobs around the area.",
        "quote_intro": "Send us your list of jobs. Photos help us work out how long it'll take.",
        "faqs": [
            ("Do you charge by the hour or by the job?", "Small jobs are often charged by the hour or half day. Bigger jobs get a price for the whole thing."),
            ("Can I give you a list of jobs?", "Yes. A list of small jobs can usually be done in one visit, which saves you money."),
            ("Do you bring your own tools and fixings?", "Yes. Standard fixings are brought along. Any larger materials are discussed with you first."),
            ("Do you work for landlords and letting agents?", "Yes. Regular maintenance and repairs between tenancies can be arranged."),
        ],
    },
    "local": {
        "label": "Local services",
        "kicker": "Local business",
        "brand": "#233646",
        "stripe": "#7fb5d8",
        "promise": "Friendly, reliable service from a local business.",
        "services_title": "What we do",
        "services_intro": "Get in touch to find out more.",
        "services": [
            ("Our main service", "A short line describing your main service."),
            ("Second service", "A short line describing another service."),
            ("Third service", "A short line describing another service."),
        ],
        "creds": [
            {"label": "Qualifications and memberships", "hint": "Any trade body, certification or approval you hold."},
            {"label": "Insurance and guarantees", "hint": "Your cover and any guarantee you offer."},
        ],
        "gallery": ["Recent job", "Recent job", "Recent job", "Recent job"],
        "gallery_intro": "A look at our work.",
        "quote_intro": "Tell us what you need and we'll get back to you.",
        "faqs": [
            ("What areas do you cover?", "We cover the town and the surrounding area. Call to check if you're further out."),
            ("How do I get a price?", "Call us or use the form on this page and we'll get back to you."),
        ],
    },
}

# Google category -> group. First match wins, so order matters.
CATEGORY_RULES = [
    ("local", r"\bcar\b|auto|vehicle|shipyard|cleaning|washer|dryer"),  # not a CALL ME trade yet
    ("plumbing", r"plumb|heating|gas engineer|boiler"),
    ("electrical", r"electric"),
    ("roofing", r"roof"),
    ("plastering", r"plaster|render|cove and cornice"),
    ("kitchens_bathrooms", r"kitchen|bathroom|tile|tiling|floor"),
    ("decorating", r"paint|decorat"),
    ("carpentry", r"carpent|joiner|wood"),
    ("gardens", r"landscap|garden|tree|fenc|grass|turf"),
    ("handyman", r"handy|property maintenance|building maintenance"),
    ("building", r"build|construct|contractor|restoration|renovat|architect"),
]


def group_for(trade, business=""):
    """Pick a trade group from the Google category, falling back to the business name."""
    for text in (trade or "", business or ""):
        for group, pattern in CATEGORY_RULES:
            if re.search(pattern, text, re.I):
                return group
    return "local"


# Nearby towns for the "Areas we cover" list. Unknown towns just show themselves.
NEARBY = {
    "Worthing": ["Goring-by-Sea", "Durrington", "Findon", "Ferring", "Lancing", "Shoreham-by-Sea"],
    "Brighton": ["Hove", "Portslade", "Rottingdean", "Saltdean", "Woodingdean", "Peacehaven"],
    "Hove": ["Brighton", "Portslade", "Southwick", "Shoreham-by-Sea", "Rottingdean"],
    "Lancing": ["Sompting", "Worthing", "Shoreham-by-Sea", "Steyning", "Findon"],
    "Shoreham-by-Sea": ["Southwick", "Lancing", "Portslade", "Hove", "Steyning"],
    "Littlehampton": ["Rustington", "Angmering", "East Preston", "Arundel", "Bognor Regis"],
    "Bognor Regis": ["Felpham", "Middleton-on-Sea", "Aldwick", "Chichester", "Selsey"],
    "Chichester": ["Bosham", "Selsey", "Bognor Regis", "Emsworth", "Midhurst"],
    "Horsham": ["Southwater", "Broadbridge Heath", "Billingshurst", "Crawley", "Henfield"],
    "Crawley": ["Three Bridges", "Horley", "Pound Hill", "Horsham", "East Grinstead"],
    "Burgess Hill": ["Haywards Heath", "Hassocks", "Hurstpierpoint", "Wivelsfield", "Lewes"],
    "Haywards Heath": ["Lindfield", "Cuckfield", "Burgess Hill", "Hassocks", "Wivelsfield"],
    "Eastbourne": ["Hampden Park", "Polegate", "Pevensey", "Willingdon", "Hailsham"],
    "Lewes": ["Ringmer", "Newhaven", "Seaford", "Kingston", "Peacehaven"],
}


# Extra fields used by the redesigned template.
# short: headline word for the trust strip credential; cta_noun: "Need a ___ in Town?";
# ba_text: line beside the before/after slider (only shown when before/after photos exist).
EXTRAS = {
    "plumbing": {"short": "Gas Safe", "cta_noun": "plumber", "ba_text": "An old boiler cupboard, replaced and tidied."},
    "electrical": {"short": "Certified", "cta_noun": "electrician", "ba_text": "An old fuse box, swapped for a modern consumer unit."},
    "building": {"short": "FMB", "cta_noun": "builder", "ba_text": "A tired room turned into open living space."},
    "plastering": {"short": "Insured", "cta_noun": "plasterer", "ba_text": "Cracked old walls, skimmed smooth and ready to paint."},
    "carpentry": {"short": "Insured", "cta_noun": "carpenter", "ba_text": "An empty alcove, turned into fitted storage."},
    "decorating": {"short": "Insured", "cta_noun": "decorator", "ba_text": "A tired room, freshly decorated."},
    "roofing": {"short": "Guaranteed", "cta_noun": "roofer", "ba_text": "A worn roof, stripped and re-laid."},
    "kitchens_bathrooms": {"short": "Guaranteed", "cta_noun": "fitter", "ba_text": "A dated bathroom, fully refitted."},
    "gardens": {"short": "Licensed", "cta_noun": "landscaper", "ba_text": "An overgrown garden, rebuilt with a new patio and lawn."},
    "handyman": {"short": "Insured", "cta_noun": "handyman", "ba_text": "Odd jobs finished properly."},
    "local": {"short": "Approved", "cta_noun": "local expert", "ba_text": "Before and after one of our jobs."},
}
for _g, _x in EXTRAS.items():
    TRADES[_g].update({k: v for k, v in _x.items() if k != "short"})
    TRADES[_g]["creds"] = [dict(c, short=_x["short"]) if i == 0 else c for i, c in enumerate(TRADES[_g]["creds"])]


# Guide price bands for the "rough price" tool, in the same order as each trade's services.
# (low, high) in pounds, or (low, high, "unit") when the price is per item/hour/room.
# None = no guide price for that service. These are typical UK ranges used as EXAMPLES in
# previews; the client sets their own before the site goes live.
PRICES = {
    "plumbing": [(90, 250), (2000, 4000), (80, 120), (80, 250), (200, 450, "per radiator"), (90, 300)],
    "electrical": [(80, 200), (450, 800), (150, 300), (3500, 8000), (90, 300), (800, 1200)],
    "building": [(30000, 70000), (15000, 50000), (35000, 60000), (500, 3000), (2500, 6000), (200, 1500)],
    "plastering": [(400, 800, "per room"), (800, 1500, "per room"), (3000, 7000), (500, 1200), (150, 500), (100, 400)],
    "carpentry": [(1200, 3500), (120, 250, "per door"), (1000, 4000), (300, 1200), (1500, 5000), (400, 2500)],
    "decorating": [(300, 700, "per room"), (1500, 4000), (250, 600, "per room"), (150, 500), (800, 1800), (100, 400)],
    "roofing": [(150, 600), (6000, 15000), (1500, 4500), (400, 1500), (1500, 4000), (100, 250)],
    "kitchens_bathrooms": [(2500, 6000), (4000, 9000), (400, 1500), (400, 1500), (700, 2000), None],
    "gardens": [(3000, 8000), (1000, 3000), (600, 2500), (25, 40, "an hour"), (300, 1500), (200, 800)],
    "handyman": [(40, 120, "per item"), (50, 150), (50, 150), (150, 400), (80, 250), (30, 45, "an hour")],
    "local": [None, None, None],
}

# Postcode districts for the "Do you cover me?" checker (Sussex towns in NEARBY).
POSTCODES = {
    "Worthing": ["BN11", "BN12", "BN13", "BN14"], "Goring-by-Sea": ["BN12"], "Durrington": ["BN13"],
    "Findon": ["BN14"], "Ferring": ["BN12"], "Lancing": ["BN15"], "Sompting": ["BN15"],
    "Shoreham-by-Sea": ["BN43"], "Southwick": ["BN42"], "Portslade": ["BN41"], "Steyning": ["BN44"],
    "Brighton": ["BN1", "BN2"], "Hove": ["BN3"], "Rottingdean": ["BN2"], "Saltdean": ["BN2"],
    "Woodingdean": ["BN2"], "Peacehaven": ["BN10"], "Newhaven": ["BN9"], "Seaford": ["BN25"],
    "Lewes": ["BN7", "BN8"], "Ringmer": ["BN8"], "Kingston": ["BN7"],
    "Littlehampton": ["BN17"], "Rustington": ["BN16"], "Angmering": ["BN16"], "East Preston": ["BN16"],
    "Arundel": ["BN18"], "Bognor Regis": ["PO21", "PO22"], "Felpham": ["PO22"], "Middleton-on-Sea": ["PO22"],
    "Aldwick": ["PO21"], "Chichester": ["PO19"], "Selsey": ["PO20"], "Bosham": ["PO18"], "Emsworth": ["PO10"],
    "Midhurst": ["GU29"], "Horsham": ["RH12", "RH13"], "Southwater": ["RH13"], "Broadbridge Heath": ["RH12"],
    "Billingshurst": ["RH14"], "Henfield": ["BN5"], "Crawley": ["RH10", "RH11"], "Three Bridges": ["RH10"],
    "Pound Hill": ["RH10"], "Horley": ["RH6"], "East Grinstead": ["RH19"], "Burgess Hill": ["RH15"],
    "Hassocks": ["BN6"], "Hurstpierpoint": ["BN6"], "Wivelsfield": ["RH17"], "Haywards Heath": ["RH16"],
    "Lindfield": ["RH16"], "Cuckfield": ["RH17"], "Eastbourne": ["BN20", "BN21", "BN22", "BN23"],
    "Hampden Park": ["BN22"], "Polegate": ["BN26"], "Pevensey": ["BN24"], "Willingdon": ["BN20"], "Hailsham": ["BN27"],
}


# Light-and-airy palettes (v4). brand = main colour for text accents and buttons,
# stripe = accent for lines, underlines and highlights, soft = very light section tint.
PALETTES = {
    "plumbing": {"brand": "#12406b", "stripe": "#3ea6d4", "soft": "#eef6fb"},
    "electrical": {"brand": "#1c2433", "stripe": "#f0b21c", "soft": "#fbf6e8"},
    "building": {"brand": "#6a3622", "stripe": "#d8964a", "soft": "#fbf3ec"},
    "plastering": {"brand": "#37464f", "stripe": "#c6a47a", "soft": "#f6f2ec"},
    "carpentry": {"brand": "#4d3322", "stripe": "#c88748", "soft": "#f9f2ea"},
    "decorating": {"brand": "#1d4d59", "stripe": "#e6a443", "soft": "#eef6f5"},
    "roofing": {"brand": "#2b3540", "stripe": "#c75d3c", "soft": "#f6f1ee"},
    "kitchens_bathrooms": {"brand": "#1d5660", "stripe": "#6cc3b0", "soft": "#edf7f5"},
    "gardens": {"brand": "#2a5733", "stripe": "#8fbf4f", "soft": "#f0f6ea"},
    "handyman": {"brand": "#253341", "stripe": "#ee8436", "soft": "#fcf2ea"},
    "local": {"brand": "#22384b", "stripe": "#62a5d4", "soft": "#eef4f9"},
}
for _g, _p in PALETTES.items():
    TRADES[_g].update(_p)

# Scroll films (signature hero). Each trade has a library of short renovation films that play frame by
# frame as the visitor scrolls. Each lead gets a film nobody else in their area has (build_preview.assign_films).
# Frames: films/<group>/<film id>/m/0001.webp ... (tall, 540x960) and optionally d/ (wide, 1280px).
# Films without a wide set show the tall film in a framed panel on computers.
# Made with Higgsfield: an "after" still, a matching "before" still (same camera), then Seedance 2.0 Mini
# with start and end frames, 4 s, 720p, 9:16, no audio (about 7 credits a film in all; MiniMax H3 failed
# most runs on 2026-10-30, Flux 3 Video works but costs 30+). pins.json fixes a lead to a film.
#
# SCENES: captions and review keywords per kind of job. prefer = words in a business's name or trade
# that make this kind of film the first choice for them.
SCENES = {
    "bathroom": {
        "hook": "Seen better days?", "hook_sub": "Scroll to watch this one get sorted.",
        "beats": [("Step 1 · Strip out", "Back to bare walls. Pipework done properly."),
                  ("Step 2 · Fit", "Tiled, plumbed in, tested.")],
        "quote_words": ["bathroom", "en-suite", "ensuite", "shower room", "renovat", "refit", "tiling"],
        "prefer": ["bathroom"],
    },
    "wetroom": {
        "hook": "Time for a proper shower?", "hook_sub": "Scroll to watch this one get built.",
        "beats": [("Step 1 · Strip out", "Old suite out. Floor levelled and tanked."),
                  ("Step 2 · Fit", "Walk-in shower tiled, plumbed and tested.")],
        "quote_words": ["wet room", "wetroom", "walk-in", "shower", "bathroom", "tiling"],
        "prefer": ["bathroom", "wet room", "shower"],
    },
    "shower": {
        "hook": "Shower seen better days?", "hook_sub": "Scroll to watch it get replaced.",
        "beats": [("Step 1 · Out", "Old cubicle out. Leaks found and fixed."),
                  ("Step 2 · In", "New shower tiled, sealed and tested.")],
        "quote_words": ["shower", "bathroom", "leak", "tiling"],
        "prefer": ["bathroom", "shower"],
    },
    "boiler": {
        "hook": "Boiler on its last legs?", "hook_sub": "Scroll to watch it get swapped.",
        "beats": [("Step 1 · Out", "Old boiler and pipework removed safely."),
                  ("Step 2 · In", "New combi fitted, flushed and tested.")],
        "quote_words": ["boiler", "combi", "heating", "gas"],
        "prefer": ["heating", "boiler", "gas"],
    },
    "heating": {
        "hook": "Cold rooms?", "hook_sub": "Scroll to warm this one up.",
        "beats": [("Step 1 · Off", "Old radiators off. System drained."),
                  ("Step 2 · On", "New radiators fitted, flushed and balanced.")],
        "quote_words": ["radiator", "heating", "warm", "power flush", "powerflush"],
        "prefer": ["heating"],
    },
    "hotwater": {
        "hook": "Running out of hot water?", "hook_sub": "Scroll to watch it get sorted.",
        "beats": [("Step 1 · Out", "Old tank and cylinder out."),
                  ("Step 2 · In", "New cylinder fitted and tested.")],
        "quote_words": ["hot water", "cylinder", "tank", "immersion", "boiler"],
        "prefer": ["heating"],
    },
    "sink": {
        "hook": "Drip, drip, drip?", "hook_sub": "Scroll to watch it get fixed.",
        "beats": [("Step 1 · Find it", "Leak traced. Old pipework out."),
                  ("Step 2 · Fix it", "New sink, tap and pipework fitted.")],
        "quote_words": ["leak", "sink", "tap", "kitchen", "pipe", "blocked"],
        "prefer": ["leak", "drain"],
    },
}
# When each caption shows, as a share of the scroll through the film.
FILM_TIMING = {"hook_to": .14, "beats": [(.2, .42), (.5, .74)], "end_from": .84}

# accent = colour picked from the film (buttons, rails); accent_ink = darker version for small text on the
# light ground; accent_dark = lighter version for dark mode; ground = page background matching the film.
FILMS = {
    "plumbing": [
        {"id": "bathroom-01", "scene": "bathroom", "accent": "#b0853a", "accent_ink": "#7a5a22", "accent_dark": "#d9ad62", "ground": "#f1ece4",
         "alt": "A tired 1990s bathroom being stripped back to bare walls and rebuilt into a modern bathroom"},
        {"id": "bathroom-02", "scene": "bathroom", "accent": "#7495ab", "accent_ink": "#3f5b6e", "accent_dark": "#9fbdd1", "ground": "#eef0f1",
         "alt": "A dated family bathroom being stripped out and refitted with a new bath, shower and grey tiles"},
        {"id": "wetroom-03", "scene": "wetroom", "accent": "#b08a3e", "accent_ink": "#76591f", "accent_dark": "#d8b15f", "ground": "#eef1ec",
         "alt": "A small old bathroom being turned into a green-tiled walk-in wet room"},
        {"id": "cottage-04", "scene": "bathroom", "accent": "#7d9a7e", "accent_ink": "#4d6a4f", "accent_dark": "#a9c6aa", "ground": "#f1efe8",
         "alt": "An old cottage bathroom being rebuilt with a roll-top bath and sage green panelling"},
        {"id": "ensuite-05", "scene": "bathroom", "accent": "#b67f4f", "accent_ink": "#7a4f2a", "accent_dark": "#d49a66", "ground": "#efeeec",
         "alt": "A tired loft en-suite being refitted with a black-framed walk-in shower"},
        {"id": "boiler-06", "scene": "boiler", "accent": "#b8693a", "accent_ink": "#8a4a24", "accent_dark": "#e09868", "ground": "#f2eeea",
         "alt": "An old floor-standing boiler and tangled pipes being replaced with a neat new combi boiler"},
        {"id": "radiators-07", "scene": "heating", "accent": "#c2783f", "accent_ink": "#8d5226", "accent_dark": "#e4a06a", "ground": "#f3eee8",
         "alt": "A cold, damp living room getting new column radiators and warming up"},
        {"id": "cylinder-08", "scene": "hotwater", "accent": "#b8693a", "accent_ink": "#8a4a24", "accent_dark": "#e09868", "ground": "#f1efec",
         "alt": "An old leaking hot water tank being replaced with a new cylinder in a tidy airing cupboard"},
        {"id": "sink-09", "scene": "sink", "accent": "#a98a45", "accent_ink": "#715a22", "accent_dark": "#d6b466", "ground": "#eff1ec",
         "alt": "A leaking old kitchen sink being replaced with a new Belfast sink, tap and pipework"},
        {"id": "shower-10", "scene": "shower", "accent": "#c97d6d", "accent_ink": "#93503f", "accent_dark": "#eaa596", "ground": "#f6efec",
         "alt": "A mouldy old shower cubicle being replaced with a new walk-in shower"},
    ],
}
