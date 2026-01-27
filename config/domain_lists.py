"""
Domain Lists and Content Filtering Data for News Poster Application

This module contains domain lists, blocked sources, and content filtering patterns.
Extracted from settings.py to separate data from configuration logic.
"""

# Paywall Detection
PAYWALL_PHRASES = [
    "subscribe", "subscription", "sign in",
    "premium content", "premium article",
    "paid subscribers only"
]

# Known Paywall Domains - these sites are known to implement paywalls
PAYWALL_DOMAINS = [
    "wsj.com",              # Wall Street Journal
    "nytimes.com",          # New York Times
    "ft.com",               # Financial Times
    "economist.com",        # The Economist
    "bloomberg.com",        # Bloomberg
    "washingtonpost.com",   # Washington Post
    "theatlantic.com",      # The Atlantic
    "newyorker.com",        # The New Yorker
    "medium.com",           # Medium
    "wired.com",            # Wired
    "barrons.com",          # Barron's
    "forbes.com",           # Forbes (sometimes)
    "businessinsider.com",  # Business Insider Prime
    "insider.com",          # Insider
    "buzzfeed.com",         # BuzzFeed (sometimes)
    "understandingwar.org", # Institute for the Study of War
    "federalreserve.gov",   # Federal Reserve
    "whitehouse.gov",       # White House
    "congress.gov",         # Congress
    "justice.gov",          # Department of Justice
    "state.gov",            # Department of State
    "defense.gov",          # Department of Defense
    "cia.gov",              # Central Intelligence Agency
    "nsa.gov",              # National Security Agency
    "fbi.gov",              # Federal Bureau of Investigation
    "dhs.gov",              # Department of Homeland Security
    "dod.gov",              # Department of Defense
    "nasa.gov",             # National Aeronautics and Space Administration
    "treasury.gov",         # Department of the Treasury
    'scmp.com',             # South China Morning Post
    'themoscowtimes.com',   # The Moscow Times
    'freebeacon.com',       # The Washington Free Beacon
    'engadget.com',         # Engadget
    'prnewswire.com',       # PR Newswire
    'vaticannews.va'        # Vatican News
    'churchofjesuschrist.org',  # LDS Church News
    'globenewswire.com'     # GlobeNewswire (last item, no comma needed)
]

# =============================================================================
# Blocked Domains for Article Selection
# =============================================================================

# Domains that should never be selected for posting (religious, government, unreliable)
BLOCKED_DOMAINS = [
    # Government domains (handled by regex, but explicit list for subdomains)
    # Note: .gov and .mil TLDs are filtered by regex pattern in ai_service.py

    # Religious news sites
    "vaticannews.va",
    "churchofjesuschrist.org",
    "christianpost.com",
    "christianitytoday.com",
    "ncregister.com",           # National Catholic Register
    "catholicnews.com",
    "catholicnewsagency.com",
    "ewtn.com",                 # Eternal Word Television Network
    "religionnews.com",
    "christianheadlines.com",
    "crosswalk.com",
    "desiringgod.org",
    "relevantmagazine.com",
    "sojo.net",                 # Sojourners
    "firstthings.com",
    "cruxnow.com",              # Catholic news
    "americamagazine.org",      # Jesuit magazine
    "ncronline.org",            # National Catholic Reporter
    "charismanews.com",
    "onenewsnow.com",           # American Family Association
    "wnd.com",                  # WorldNetDaily
    "lifesitenews.com",
    "theblaze.com",
    "cbn.com",                  # Christian Broadcasting Network
    "jewishpress.com",
    "timesofisrael.com",        # Often religious focus
    "jpost.com",                # Jerusalem Post (mixed, but often religious)
    "aljazeera.com",            # Can have religious bias
    "islamonline.net",
    "muslimmatters.org",

    # Known unreliable/fake news sources
    "infowars.com",
    "naturalnews.com",
    "breitbart.com",
    "dailywire.com",
    "thegatewaypundit.com",
    "zerohedge.com",
    "epochtimes.com",
    "ntd.com",                  # New Tang Dynasty (Epoch Times affiliate)
    "oann.com",                 # One America News Network
    "newsmax.com",
    "rt.com",                   # Russia Today
    "sputniknews.com",
    "globalresearch.ca",
    "beforeitsnews.com",
    "worldtruth.tv",
    "yournewswire.com",
    "neonnettle.com",

    # Clickbait / Low quality
    "buzzfeed.com",
    "dailymail.co.uk",
    "thesun.co.uk",
    "nypost.com",               # Often sensational
    "foxnews.com",              # High bias
    "msnbc.com",                # High bias

    # Press releases / PR sites
    "prnewswire.com",
    "globenewswire.com",
    "businesswire.com",
    "prweb.com",

    # Corporate newsrooms (PR disguised as news)
    "intel.com",
    "lockheedmartin.com",
    "boeing.com",
    "raytheon.com",
    "northropgrumman.com",
    "generaldynamics.com",
    "baesystems.com",
    "apple.com/newsroom",
    "microsoft.com",
    "google.com/press",
    "amazon.com",
    "meta.com",
    "nvidia.com",
    "ibm.com",
    "oracle.com",
    "cisco.com",
    "salesforce.com",
    "tesla.com",
    "spacex.com",
    "ford.com",
    "gm.com",
    "toyota.com",
    "exxonmobil.com",
    "chevron.com",
    "shell.com",
    "bp.com",
    "pfizer.com",
    "johnson.com",
    "merck.com",
    "walmart.com",
    "target.com",
    "costco.com",
    "homedepot.com",
    "lowes.com",

    # Mining / Commodities / Industrial
    "glencore.com",
    "riotinto.com",
    "bhp.com",
    "vale.com",
    "angloamerican.com",
    "freeportmcmoran.com",
    "newmontcorp.com",
    "barrick.com",
    "caterpillar.com",
    "deere.com",
    "3m.com",
    "honeywell.com",
    "ge.com",
    "siemens.com",
]

# PR-style title patterns that indicate corporate statements (case-insensitive)
PR_TITLE_PATTERNS = [
    r"^statement\s+(regarding|on|about)",      # "Statement regarding..."
    r"^announcement\s*:",                       # "Announcement:"
    r"^press\s+release\s*:",                    # "Press Release:"
    r"^media\s+(release|statement)",            # "Media Release"
    r"\bannounces\s+(q[1-4]|quarterly|annual|fiscal)",  # "announces Q1 results"
    r"\breports\s+(q[1-4]|quarterly|annual|fiscal)",    # "reports quarterly earnings"
    r"\b(q[1-4]|quarterly|annual)\s+(results|earnings|revenue)",  # "Q3 results"
    r"investor\s+(update|call|presentation)",   # "Investor Update"
    r"^notice\s+of\s+",                         # "Notice of AGM"
    r"shareholder\s+(meeting|letter|update)",   # "Shareholder Meeting"
]
