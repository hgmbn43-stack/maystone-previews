"""Service page copy (10 Nov 2026): a few real paragraphs per service so the service pages aren't thin.

COPY[group][service title] = {
    "intro":    what the job is and why it matters (2-3 sentences, plain English),
    "includes": what a typical job covers (4 bullets),
    "signs":    when people usually need it (3 bullets),
}
Written as general trade knowledge, never claims about one business (no registrations, guarantees or
"24/7"). Previews tag it "Example wording"; the owner checks it before the site goes live.
"""

COPY = {
    "plumbing": {
        "Boiler repairs": {
            "intro": "When the boiler stops, the whole house feels it. A repair starts with finding the real fault, not guessing at parts, so you only pay for what actually fixes it. Most breakdowns come down to pressure, a failed part or a blocked condensate pipe, and many are sorted in one visit.",
            "includes": ["Checking the fault codes, pressure and controls", "Testing the parts most likely to have failed", "A clear price for the repair before any work starts", "Testing the boiler and heating once it's fixed"],
            "signs": ["No heating or hot water, or only one of the two", "Pressure keeps dropping, or the boiler keeps locking out", "New noises: banging, gurgling or whistling"],
        },
        "Boiler installs": {
            "intro": "A new boiler is one of the bigger jobs in a home, so it should be sized to your house and your hot water use, not just the cheapest model going. A modern, efficient boiler can cut your gas bills and end the cycle of call-outs on an old one.",
            "includes": ["A survey of your home, radiators and hot water needs", "Advice on combi, system or regular boilers", "Removing the old boiler and fitting the new one", "Flushing the system, setting up the controls and showing you how it works"],
            "signs": ["Your boiler is over 12–15 years old and breaking down more often", "Parts are getting hard to find or expensive", "Heating bills keep climbing"],
        },
        "Boiler servicing": {
            "intro": "A yearly service keeps your boiler running safely and efficiently, and most manufacturers need one to keep the warranty valid. It's also the best way to catch small problems before they turn into a winter breakdown.",
            "includes": ["Checking the flue, seals and gas pressure", "Cleaning key parts and checking for wear", "Testing the safety devices", "A written record of the service for your warranty"],
            "signs": ["It's been more than a year since the last service", "Your warranty needs a yearly service", "You're a landlord and need the annual gas safety check"],
        },
        "Leaks and burst pipes": {
            "intro": "Water in the wrong place can do a lot of damage quickly. The first job is to stop it and make it safe, then find exactly where it's coming from and fix it properly, so it doesn't come back.",
            "includes": ["Tracing the leak to its source", "Making it safe and stopping the water", "Replacing damaged pipe, joints or fittings", "Checking nearby pipework while we're there"],
            "signs": ["Water through a ceiling or damp patches on walls", "Your water meter moves when nothing's running", "Dripping under sinks, baths or the boiler"],
        },
        "Radiators and heating": {
            "intro": "Cold spots, noisy pipes and radiators that are only warm at the top usually mean the system needs attention. Whether it's a single new radiator or balancing the whole system, the aim is every room warming up evenly.",
            "includes": ["Bleeding, balancing and checking the system", "Fitting new or bigger radiators and valves", "Moving radiators to suit a new layout", "Power flushing to clear sludge where needed"],
            "signs": ["Radiators cold at the bottom or in the middle", "Some rooms never get warm", "Banging or gurgling when the heating comes on"],
        },
        "Bathrooms and taps": {
            "intro": "From a dripping tap to a full new bathroom, good plumbing is what makes the rest of the room work. Small jobs are usually quick, and bigger ones start with a proper look and a clear price.",
            "includes": ["Fixing or replacing taps, toilets and basins", "Fitting showers and mixer valves", "First and second fix plumbing for new bathrooms", "Sealing and testing everything when it's done"],
            "signs": ["A tap that drips or a toilet that keeps running", "Weak or cold showers", "Planning a new bathroom or en-suite"],
        },
    },
    "electrical": {
        "Fault finding": {
            "intro": "Electrical faults can be frustrating to track down, and guessing can make things worse. Fault finding means testing the circuits properly to find the cause, then fixing it safely.",
            "includes": ["Testing circuits to locate the fault", "Checking sockets, switches and fittings", "Repairing or replacing faulty parts", "A safety check before power goes back on"],
            "signs": ["The power keeps tripping", "Sockets or lights that have stopped working", "Flickering lights or buzzing switches"],
        },
        "Fuse board upgrades": {
            "intro": "The fuse board, or consumer unit, protects every circuit in your home. Older boards often don't have the protection modern ones do, and an upgrade is one of the most effective safety improvements you can make.",
            "includes": ["Checking your existing board and circuits", "Fitting a modern consumer unit", "Labelling every circuit clearly", "Testing and certifying the installation"],
            "signs": ["An old board with fuse wire or no RCD protection", "Frequent trips you can't explain", "Planning an extension or rewire"],
        },
        "EICR safety reports": {
            "intro": "An Electrical Installation Condition Report checks the wiring in a property and flags anything that's unsafe. Landlords in England need one at least every five years, and they're useful for buyers and homeowners too.",
            "includes": ["Inspecting the consumer unit, wiring and fittings", "Testing a sample of circuits", "A written report with any issues graded", "A clear price for any repairs needed"],
            "signs": ["You're a landlord and the report is due", "You're buying or selling a home", "The wiring hasn't been checked in years"],
        },
        "Rewires": {
            "intro": "Old wiring can be unsafe and often can't cope with modern appliances. A full or partial rewire is planned around your home, so the disruption is kept to a minimum and you end up with sockets and lights where you actually need them.",
            "includes": ["A survey and plan of the new layout", "New cables, sockets, switches and lighting points", "A new consumer unit where needed", "Testing and certifying the finished work"],
            "signs": ["Old rubber or fabric-covered cables", "Not enough sockets and lots of extension leads", "Renovating or buying an older property"],
        },
        "Lighting and sockets": {
            "intro": "Extra sockets, outdoor lights or new lighting in a kitchen can make a home far easier to live in. Smaller jobs like these are often done in a day.",
            "includes": ["Adding or moving sockets and switches", "Fitting downlights, pendants and outdoor lights", "USB sockets and smart switches", "Testing everything once it's in"],
            "signs": ["Not enough sockets where you need them", "Dark rooms, gardens or driveways", "Updating a kitchen or living room"],
        },
        "EV chargers": {
            "intro": "A home charger is quicker and usually cheaper than public charging. It needs to be fitted on the right circuit, with the right protection, so it's safe and ready for your car.",
            "includes": ["Checking your supply and where the charger will go", "Fitting the charger and its dedicated circuit", "Setting up the charger and app", "Testing and certifying the installation"],
            "signs": ["You've got, or are getting, an electric car", "You're relying on public chargers", "You want a charger ready before you sell"],
        },
    },
    "building": {
        "Extensions": {
            "intro": "An extension can give you the space you need without the cost of moving. Good planning at the start, from the layout to the paperwork, makes the build run more smoothly.",
            "includes": ["Talking through the space and layout you want", "Groundworks, foundations and structure", "Working alongside other trades to a clear plan", "Keeping the site tidy and you up to date"],
            "signs": ["You've outgrown your home but love the area", "You want a bigger kitchen or extra bedroom", "You have plans drawn up and need a builder"],
        },
        "Renovations": {
            "intro": "Renovating a tired home can transform how it works and feels. The key is a clear plan and a sensible order of work, so each job sets up the next one properly.",
            "includes": ["Planning the work and the order it happens in", "Structural work, walls and openings", "Coordinating plastering, electrics and plumbing", "Making good and finishing"],
            "signs": ["You've bought a home that needs updating", "Rooms don't suit the way you live", "Several jobs need doing at once"],
        },
        "Loft conversions": {
            "intro": "A loft is often the easiest place to find a new bedroom or office. The right design depends on your roof, so it starts with a look at what's possible.",
            "includes": ["Checking head height and the roof structure", "Floors, stairs, windows or dormers", "Insulation and fire safety", "Finishing ready for decorating"],
            "signs": ["You need another bedroom or office", "Your loft has good head height", "You want to add space without losing garden"],
        },
        "Brickwork and walls": {
            "intro": "From garden walls to repointing, good brickwork lasts for decades. It should match what's already there and be built on proper foundations.",
            "includes": ["New walls, piers and planters", "Repointing and repairing old brickwork", "Matching bricks and mortar colour", "Clearing up properly afterwards"],
            "signs": ["Crumbling mortar or loose bricks", "A wall that's leaning or cracked", "You want a new garden or boundary wall"],
        },
        "Knock-throughs": {
            "intro": "Opening up two rooms can change how a whole floor feels. Load-bearing walls need the right support, so the work is planned properly before anything comes down.",
            "includes": ["Checking whether the wall is load-bearing", "Temporary support and new steel or lintels", "Removing the wall and making good", "Coordinating any electrics or pipes in the wall"],
            "signs": ["You want an open-plan kitchen and dining room", "Rooms feel dark or closed off", "You're renovating a ground floor"],
        },
        "General building": {
            "intro": "Not every job is a big project. Porches, garden rooms, small repairs and alterations all need doing properly too.",
            "includes": ["Small alterations and repairs", "Porches, outbuildings and garden rooms", "Doorways, windows and openings", "A clear price for the job"],
            "signs": ["A job that's too big for a handyman", "Repairs after damage or a leak", "Small changes to the layout of a room"],
        },
    },
    "plastering": {
        "Skimming": {
            "intro": "A skim coat gives tired or uneven walls and ceilings a smooth, fresh finish ready for decorating. It's one of the quickest ways to make a room look new.",
            "includes": ["Protecting floors and furniture", "Preparing and priming the surface", "Applying a smooth skim finish", "Leaving it clean and ready to paint once dry"],
            "signs": ["Walls with cracks, bumps or old wallpaper damage", "Artex or textured ceilings you want smooth", "Redecorating a room"],
        },
        "Re-plastering": {
            "intro": "When old plaster is blown, cracked or damaged by damp, patching won't last. Re-plastering takes it back and builds up a solid new surface.",
            "includes": ["Removing old or failed plaster", "Treating and preparing the wall", "Bonding or backing coats and a new finish", "Cleaning up and removing waste"],
            "signs": ["Plaster that sounds hollow or comes away", "Walls damaged by damp or leaks", "Renovating an older property"],
        },
        "Rendering": {
            "intro": "Render protects your walls from the weather and can completely change how a house looks from the outside. The right system depends on the wall underneath.",
            "includes": ["Preparing the walls and fixing beads", "Applying the base and top coats", "Smooth, textured or coloured finishes", "Tidying up and clearing the site"],
            "signs": ["Cracked or blown old render", "Pebbledash you want to update", "Walls that need extra protection from the weather"],
        },
        "Plasterboarding": {
            "intro": "Plasterboard is the quick way to form new walls, ceilings and partitions. It's then skimmed to a smooth finish, ready to decorate.",
            "includes": ["Boarding walls, ceilings and stud partitions", "Taping and jointing", "Skimming to a smooth finish", "Working around sockets and pipes"],
            "signs": ["A new partition or room layout", "Ceilings damaged beyond repair", "Extensions and loft conversions"],
        },
        "Ceiling repairs": {
            "intro": "Cracked, sagging or water-damaged ceilings need sorting before they get worse. Most can be repaired or overboarded without the mess of a full replacement.",
            "includes": ["Checking the damage and what's behind it", "Repairing, overboarding or replacing sections", "Skimming to a smooth, even finish", "Protecting the room and clearing up"],
            "signs": ["Cracks across the ceiling", "Stains or sagging after a leak", "Old lath and plaster that's coming loose"],
        },
        "Coving and patching": {
            "intro": "Small repairs and finishing touches make a big difference. Patching holes and cracks, or fitting coving, gets a room ready for decorating.",
            "includes": ["Filling holes and cracks", "Patching after electrical or plumbing work", "Fitting new coving", "Leaving it smooth and ready to paint"],
            "signs": ["Holes left after new wiring or pipes", "Small cracks you want fixing before decorating", "Adding coving to finish a room"],
        },
    },
    "carpentry": {
        "Fitted wardrobes": {
            "intro": "Fitted wardrobes make the most of awkward spaces like alcoves and sloping ceilings. They're built to fit your room exactly, so nothing's wasted.",
            "includes": ["Measuring up and talking through the design", "Building to fit alcoves, eaves and corners", "Shelving, rails and drawers where you want them", "Finishing ready for painting"],
            "signs": ["Not enough storage in bedrooms", "Awkward alcoves or sloping ceilings", "Freestanding wardrobes that don't fit well"],
        },
        "Doors and frames": {
            "intro": "Doors that stick, swing open or look tired let a room down. Hanging new doors properly is a skilled job, and it's quicker than people expect.",
            "includes": ["Hanging new internal doors", "Fitting or repairing frames and linings", "Fitting handles, hinges and locks", "Easing and adjusting sticking doors"],
            "signs": ["Doors that stick, drag or won't close", "Updating the look of a hallway or home", "Damaged frames or architraves"],
        },
        "Staircases": {
            "intro": "A staircase is often the first thing people see. Updating the balustrade or treads can transform a hallway, and repairs make old stairs safe and quiet again.",
            "includes": ["New spindles, handrails and newel posts", "Repairing creaks and loose treads", "Cladding or replacing treads", "Finishing ready for paint or stain"],
            "signs": ["Creaking or loose stairs", "A dated balustrade", "Renovating a hallway"],
        },
        "Flooring and skirting": {
            "intro": "Good flooring needs a level base and neat edges. Fitting skirting and trims properly is what makes the finished floor look right.",
            "includes": ["Preparing and levelling the subfloor", "Fitting wood, laminate or engineered boards", "New skirting boards and trims", "Neat finishes around doors and pipes"],
            "signs": ["Worn, damaged or noisy floors", "Renovating a room", "Skirting that's damaged or dated"],
        },
        "Decking and garden": {
            "intro": "Decking, pergolas and garden structures make outdoor space more usable. They need to be built level and solid, with the right timber, so they last.",
            "includes": ["Decking frames, boards and steps", "Pergolas, gates and garden structures", "Using treated timber and proper fixings", "Clearing up when it's done"],
            "signs": ["An uneven or rotten old deck", "Wanting more usable garden space", "A gate or structure that's falling apart"],
        },
        "Bespoke joinery": {
            "intro": "Some jobs need something made to measure, from shelving and media walls to window seats. Bespoke joinery fits your home exactly.",
            "includes": ["Design and measuring up", "Shelving, cupboards and media walls", "Window seats and built-in storage", "Finishing ready for painting"],
            "signs": ["A space nothing off-the-shelf fits", "Wanting built-in storage", "A feature wall or shelving idea"],
        },
    },
    "decorating": {
        "Interior painting": {
            "intro": "A fresh coat of paint is the quickest way to change how a room feels. Good preparation is what makes the finish look sharp and last.",
            "includes": ["Protecting floors and furniture", "Filling, sanding and preparing surfaces", "Painting walls, ceilings and woodwork", "Leaving the room clean and tidy"],
            "signs": ["Scuffed or tired walls", "Moving in or getting ready to sell", "Changing the colour of a room"],
        },
        "Exterior painting": {
            "intro": "Painting the outside of a home protects it from the weather and gives it instant kerb appeal. It needs the right paints and proper preparation.",
            "includes": ["Washing down and preparing surfaces", "Filling and repairing where needed", "Painting walls, windows, doors and fascias", "Tidying up and clearing away"],
            "signs": ["Peeling or faded paint outside", "Woodwork starting to rot", "Getting a house ready for sale"],
        },
        "Wallpapering": {
            "intro": "Wallpaper can add character that paint can't. Hanging it well, with straight lines and matched patterns, takes patience and care.",
            "includes": ["Stripping old paper and preparing walls", "Lining where needed", "Hanging feature walls or whole rooms", "Matching patterns neatly"],
            "signs": ["Wanting a feature wall", "Old wallpaper that's peeling", "Redecorating a bedroom or hallway"],
        },
        "Woodwork and doors": {
            "intro": "Skirting, doors, frames and spindles take the most knocks. Repainting them makes a whole room look sharper.",
            "includes": ["Sanding and filling woodwork", "Priming bare wood", "Painting doors, frames, skirting and stairs", "A smooth, durable finish"],
            "signs": ["Chipped or yellowed woodwork", "Updating doors to a new colour", "Freshening up a hallway and stairs"],
        },
        "Kitchen cabinet painting": {
            "intro": "Painting kitchen cabinets can give a kitchen a whole new look for far less than replacing it. The finish has to be tough enough for daily use.",
            "includes": ["Cleaning and degreasing doors and frames", "Sanding and priming", "Hard-wearing paint finish", "Refitting doors and handles"],
            "signs": ["Cupboards that work but look dated", "A kitchen refresh on a budget", "Getting ready to sell"],
        },
        "Prep and repairs": {
            "intro": "Most of a great finish is in the preparation. Filling cracks, repairing plaster and sanding properly is what stops problems showing through the paint.",
            "includes": ["Filling cracks and holes", "Small plaster repairs", "Sanding and sealing stains", "Getting surfaces ready to decorate"],
            "signs": ["Cracks that keep reappearing", "Damage after a leak", "Walls that need work before painting"],
        },
    },
    "roofing": {
        "Roof repairs": {
            "intro": "A small roof problem can quickly become a big one once water gets in. Most repairs are quick, and fixing them early saves money later.",
            "includes": ["Inspecting the roof and finding the cause", "Replacing slipped or broken tiles and slates", "Repairing flashing and ridge tiles", "Photos of the problem and the repair"],
            "signs": ["Water coming through a ceiling", "Missing or slipped tiles after wind", "Damp patches in the loft"],
        },
        "New roofs": {
            "intro": "When a roof is past repair, a new one protects the whole house for decades. It's a big job, so it starts with a proper survey and a clear plan.",
            "includes": ["A survey of the roof and timbers", "Stripping the old roof", "New membrane, battens and tiles or slates", "Clearing the site when it's done"],
            "signs": ["Repeated leaks in different places", "Lots of slipped or broken tiles", "A roof that's reached the end of its life"],
        },
        "Flat roofs": {
            "intro": "Flat roofs on extensions, garages and dormers need the right system to stay watertight. Modern materials last much longer than old felt.",
            "includes": ["Checking the deck and drainage", "EPDM rubber, GRP or felt systems", "Neat edges, trims and outlets", "Clearing up properly"],
            "signs": ["Puddles that don't drain away", "Cracked or blistered felt", "Leaks over a garage or extension"],
        },
        "Chimneys": {
            "intro": "Chimneys take the worst of the weather. Loose pots, failing pointing or bad flashing can let water in or become dangerous.",
            "includes": ["Repointing and rebuilding stacks", "Replacing flashing", "Fitting cowls and caps", "Removing chimneys you no longer need"],
            "signs": ["Damp around the chimney breast", "Crumbling brickwork or loose pots", "Leaks where the chimney meets the roof"],
        },
        "Fascias and guttering": {
            "intro": "Gutters and fascias carry water away from your walls. When they leak or overflow, damp and damage soon follow.",
            "includes": ["Replacing fascias, soffits and bargeboards", "New gutters and downpipes", "Clearing and repairing gutters", "Making sure everything drains properly"],
            "signs": ["Overflowing or leaking gutters", "Rotten or flaking fascias", "Damp patches on outside walls"],
        },
        "Roof inspections": {
            "intro": "An inspection tells you what condition your roof is in before a problem turns into a leak. It's useful after storms and before buying a house.",
            "includes": ["Checking tiles, flashing, valleys and gutters", "Looking in the loft for signs of leaks", "Photos of anything that needs attention", "A clear price for any repairs"],
            "signs": ["After a storm or high winds", "Buying or selling a home", "The roof hasn't been checked in years"],
        },
    },
    "kitchens_bathrooms": {
        "Kitchen fitting": {
            "intro": "A new kitchen is one of the biggest upgrades you can make to a home. Fitting it well, level, square and neatly finished, is what makes it look and work right.",
            "includes": ["Removing the old kitchen", "Fitting units, worktops and appliances", "Coordinating plumbing, electrics and tiling", "Finishing touches and a full clean-up"],
            "signs": ["A tired or impractical kitchen", "Renovating or extending", "You've bought a kitchen and need it fitted"],
        },
        "Bathroom fitting": {
            "intro": "A new bathroom has to look good and stay watertight for years. Careful fitting, sealing and tiling makes all the difference.",
            "includes": ["Stripping out the old bathroom", "Fitting the suite, shower and furniture", "Tiling, sealing and finishing", "Testing everything before it's handed over"],
            "signs": ["A dated or leaking bathroom", "Wanting a walk-in shower", "Adding an en-suite"],
        },
        "Wall and floor tiling": {
            "intro": "Good tiling needs straight lines, level surfaces and neat cuts. It's the detail people notice in a kitchen or bathroom.",
            "includes": ["Preparing and levelling surfaces", "Wall, floor and splashback tiling", "Neat cuts around pipes and edges", "Grouting and sealing"],
            "signs": ["Cracked or dated tiles", "A new kitchen or bathroom", "A splashback or feature wall"],
        },
        "Flooring": {
            "intro": "Kitchen and bathroom floors need to handle water and daily wear. The right floor, fitted on a level base, will last for years.",
            "includes": ["Levelling the subfloor", "Tile, vinyl, LVT or laminate", "Neat edges and trims", "Sealing where needed"],
            "signs": ["Worn or lifting flooring", "Renovating a kitchen or bathroom", "Floors that are cold or uneven"],
        },
        "Showers": {
            "intro": "A good shower makes a big difference every day. Whether it's a new electric shower or a full walk-in, it needs to be fitted properly and fully sealed.",
            "includes": ["Fitting electric, mixer or power showers", "Shower trays, enclosures and wet rooms", "Waterproofing and sealing", "Testing flow and temperature"],
            "signs": ["A weak or unreliable shower", "Leaks around the tray", "Wanting a walk-in or wet room"],
        },
        "Design help": {
            "intro": "Not sure what you want yet? Talking through layout, storage and budget at the start helps avoid costly changes later.",
            "includes": ["A visit to measure and talk through ideas", "Advice on layout and storage", "Suggestions to suit your budget", "A clear price for the work"],
            "signs": ["Starting to plan a new kitchen or bathroom", "Unsure what will fit the space", "Wanting to get the layout right first"],
        },
    },
    "gardens": {
        "Patios and paving": {
            "intro": "A patio gives you somewhere to sit, eat and enjoy the garden. Done properly, with a solid base and good drainage, it stays level for years.",
            "includes": ["Digging out and laying a solid sub-base", "Laying slabs, setts or porcelain", "Falls so water drains away", "Pointing, edging and a tidy finish"],
            "signs": ["An uneven or sinking patio", "Wanting more usable outdoor space", "A garden that's hard to get around"],
        },
        "Fencing": {
            "intro": "A good fence gives you privacy and security and keeps pets and children safe. Posts set properly are what stop it leaning in the first windy winter.",
            "includes": ["Removing old fencing", "Setting posts in concrete or spurs", "Panels, closeboard or picket fencing", "Gates and gravel boards"],
            "signs": ["Leaning or broken fence panels", "Rotten posts", "Wanting more privacy"],
        },
        "Turf and lawns": {
            "intro": "A healthy lawn starts with good preparation. New turf laid on well-prepared ground roots quickly and looks good from day one.",
            "includes": ["Clearing and levelling the ground", "Laying new turf", "Lawn repairs and reseeding", "Advice on watering and care"],
            "signs": ["A patchy or worn-out lawn", "A new-build garden", "Ground that needs levelling"],
        },
        "Garden maintenance": {
            "intro": "Regular maintenance keeps a garden looking its best without you giving up your weekends. Visits can be one-off or on a schedule.",
            "includes": ["Mowing, edging and weeding", "Pruning and cutting back", "Leaf clearance", "Taking garden waste away"],
            "signs": ["The garden's got away from you", "Getting a property ready to sell or let", "You'd rather spend weekends enjoying it"],
        },
        "Planting and beds": {
            "intro": "New beds and planting can bring a garden to life. Choosing plants to suit the soil and light means they thrive rather than struggle.",
            "includes": ["Designing and digging new beds", "Raised beds and edging", "Choosing and planting", "Mulching and finishing"],
            "signs": ["Bare or tired borders", "Wanting raised beds", "Planning a garden makeover"],
        },
        "Tree and hedge work": {
            "intro": "Overgrown hedges and trees block light and take over a garden. Cutting them back at the right time keeps them healthy and tidy.",
            "includes": ["Hedge trimming and shaping", "Reducing and cutting back", "Removing small trees and shrubs", "Clearing and taking away the waste"],
            "signs": ["Hedges that are too tall or wide", "Trees blocking light", "Overgrowth you can't manage yourself"],
        },
    },
    "handyman": {
        "Flat-pack assembly": {
            "intro": "Flat-pack furniture can take hours and the instructions don't always help. Having it built properly means it's solid and safe, and fixed to the wall where it needs to be.",
            "includes": ["Assembling wardrobes, beds, desks and units", "Fixing tall furniture to the wall", "Checking everything is level and secure", "Taking the packaging away"],
            "signs": ["Boxes waiting to be built", "Moving into a new home", "Furniture that's wobbly or wasn't built right"],
        },
        "Hanging and fixing": {
            "intro": "Shelves, TVs, mirrors and blinds need fixing into the right wall with the right fixings. Getting it right first time saves holes and hassle.",
            "includes": ["Shelves, mirrors and pictures", "TV wall mounts", "Curtain poles and blinds", "Using the right fixings for the wall"],
            "signs": ["Things waiting to go up", "A TV to mount", "New curtains or blinds"],
        },
        "Small repairs": {
            "intro": "The jobs list that never gets shorter. Small repairs are often quick, and sorting several in one visit saves time.",
            "includes": ["Doors, handles and hinges", "Sealant and grouting", "Minor plaster and woodwork repairs", "Fixing things that have come loose"],
            "signs": ["A list of little jobs", "Getting a home ready to sell or let", "No time to do it yourself"],
        },
        "Painting touch-ups": {
            "intro": "Touch-ups freshen up scuffed walls and woodwork without a full redecoration. Ideal before a viewing or at the end of a tenancy.",
            "includes": ["Filling small holes and cracks", "Touching up walls and woodwork", "Painting single rooms or doors", "Leaving it tidy"],
            "signs": ["Scuffs and marks on walls", "End of a tenancy", "Getting ready for viewings"],
        },
        "Garden jobs": {
            "intro": "Small garden jobs like fence repairs, gutter clearing and jet washing make a big difference to how a home looks.",
            "includes": ["Fence and gate repairs", "Jet washing paths and patios", "Clearing gutters", "Taking away green waste"],
            "signs": ["A broken fence panel or gate", "Green, slippery paths", "Overflowing gutters"],
        },
        "Landlord maintenance": {
            "intro": "Keeping rental properties in good order keeps tenants happy and protects your investment. Repairs between tenants or when issues come up can be booked as needed.",
            "includes": ["Repairs reported by tenants", "End-of-tenancy fixes and touch-ups", "Fitting smoke alarms and small upgrades", "Photos of completed work"],
            "signs": ["A tenant has reported a problem", "A property between tenants", "Several rentals to look after"],
        },
    },
}


# "What's gone wrong?" helper (10 Nov 2026) for trades people ring in a hurry. Tap a problem, get the safe
# first steps, answer two quick questions, and it writes the WhatsApp message (or opens the quote form).
# Safety steps are standard UK advice only; nothing here claims anything about the business.
HELP = {
    "plumbing": [
        {"key": "leak", "label": "Something's leaking",
         "now": ["Turn the water off at the stopcock. It's usually under the kitchen sink; turn it clockwise.",
                 "If water is near lights or sockets, switch the electrics off at the fuse box and don't touch anything wet.",
                 "Open the cold taps to drain the pipes and put towels and buckets under the drip."],
         "q": [("Where is it coming from?", ["The ceiling", "A pipe", "Under a sink", "The toilet", "The boiler", "Not sure"]),
               ("Is it stopped?", ["Stopped at the stopcock", "Still leaking", "Can't find the stopcock"])]},
        {"key": "noheat", "label": "No heating or hot water",
         "now": ["Check the boiler display for a fault code and write it down.",
                 "Check the pressure gauge. Most boilers want about 1 to 1.5 bar when cold.",
                 "Check the thermostat and timer are on, and try a reset once. Don't keep resetting it."],
         "q": [("What's not working?", ["No heating", "No hot water", "Neither"]),
               ("What does the boiler show?", ["A fault code", "Low pressure", "Nothing, it's off", "Not sure"])]},
        {"key": "blocked", "label": "Something's blocked",
         "now": ["Stop using the sink, bath or toilet that's blocked so it doesn't overflow.",
                 "Try a plunger, but don't mix drain chemicals.",
                 "If more than one drain is backing up, the blockage may be outside: avoid running water."],
         "q": [("What's blocked?", ["Kitchen sink", "Bath or shower", "Toilet", "Outside drain", "More than one"]),
               ("Is it overflowing?", ["Yes", "No, just slow"])]},
        {"key": "gas", "label": "I can smell gas",
         "now": ["Call the National Gas Emergency number now: 0800 111 999. It's free, any time.",
                 "Open doors and windows. Don't use light switches, flames or anything that could spark.",
                 "Turn off the gas at the meter if you can and leave the property if the smell is strong."],
         "emergency": True, "q": []},
    ],
    "electrical": [
        {"key": "trip", "label": "The power keeps tripping",
         "now": ["Unplug everything on the circuit that's tripping, then try resetting the switch at the fuse box.",
                 "Plug things back in one at a time. If one appliance trips it, leave it unplugged.",
                 "If it trips with nothing plugged in, leave it off and don't keep resetting it."],
         "q": [("What's affected?", ["Sockets", "Lights", "Everything", "One room", "Not sure"]),
               ("Does it trip straight away?", ["Straight away", "After a while", "When it rains"])]},
        {"key": "dead", "label": "Lights or sockets not working",
         "now": ["Check the fuse box for a switch that's dropped down and try switching it back up once.",
                 "Check whether neighbours have power too. If the whole street is off, it's a power cut: call 105.",
                 "Don't open up sockets or fittings yourself."],
         "q": [("What's not working?", ["Some sockets", "Some lights", "A whole room", "The whole house"]),
               ("Has a switch tripped?", ["Yes, it won't stay up", "No", "Not sure"])]},
        {"key": "burning", "label": "Burning smell or sparks",
         "now": ["If there's smoke or fire, get everyone out and call 999.",
                 "If it's safe to, switch the power off at the main switch on the fuse box.",
                 "Don't touch the socket, switch or appliance and don't use it again until it's checked."],
         "emergency": True, "q": []},
    ],
    "roofing": [
        {"key": "leak", "label": "Water coming through the ceiling",
         "now": ["Put buckets and towels under the drip and move anything valuable out of the way.",
                 "If the ceiling is bulging or water is near lights, switch that circuit off and keep clear.",
                 "Don't go up on the roof yourself, especially in wind or rain."],
         "q": [("Where is it?", ["Bedroom ceiling", "Loft", "Around the chimney", "By a window", "Extension or flat roof"]),
               ("How bad is it?", ["A few drips", "Steady drip", "Pouring in"])]},
        {"key": "tiles", "label": "Missing or slipped tiles",
         "now": ["Keep people away from the area below in case more tiles fall.",
                 "Take a photo from the ground if you can do it safely.",
                 "Don't climb up to look. A roofer can check it safely."],
         "q": [("What can you see?", ["Missing tiles", "Slipped tiles", "Ridge tiles loose", "Something else"]),
               ("Is water getting in?", ["Yes", "No", "Not sure"])]},
        {"key": "gutter", "label": "Gutters overflowing",
         "now": ["Check for anything blocking the downpipe at ground level.",
                 "Don't use a ladder in wet or windy weather.",
                 "Take a photo of where it's overflowing."],
         "q": [("Where?", ["Front", "Back", "Side", "All round"]),
               ("Is water getting into the walls?", ["Yes, damp patches", "No", "Not sure"])]},
    ],
}
