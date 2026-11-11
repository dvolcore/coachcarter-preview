"""Platform shell v2 — one information architecture applied to every built page.

build.py still assembles head + header + body + footer. `apply()` then rewrites the
result so every page shares the same structure:

  worlds header (5 categories, mega panels)  ->  WORLDS below is the single source
  local nav   (sibling pages of the current world; store = departments)
  chapter rail (in-page sections, ids added automatically)
  next-up band (the logical next page + the other worlds)
  sitemap footer columns
  search index (assets/data/search.json) for the command palette

Nothing in src/*.html has to change for a page to get the shell.
"""
import json
import re
from html import escape, unescape
from pathlib import Path

import motion  # code-authored motion plates (store department title cards)
import motion_pages  # more scenes + the plate that opens each inner page
import private  # Coach's private photo collection (Archive)
import seo  # canonical + social tags, structured data, FAQ hub, sitemap

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"
def _version():
    import hashlib
    h = hashlib.sha1()
    for f in ("assets/css/shell.css", "assets/js/shell.js", "assets/css/motion.css", "assets/js/motion.js"):
        h.update((OUT / f).read_bytes())
    return h.hexdigest()[:8]


V = _version()  # cache-buster: changes whenever shell.css / shell.js change

# --------------------------------------------------------------------------- IA
# (nav key, href, label, one-line description, preview image)
WORLDS = [
    {
        "key": "man", "label": "The Man", "no": "01",
        "title": "The real Coach Carter",
        "blurb": "The lockout, the contract and twenty-seven years of proof. The true story, on the record.",
        "cta": ("story.html", "Start with the story"),
        "image": "assets/video/press.jpg", "video": "assets/video/press.mp4",
        "pages": [
            ("story", "story.html", "The Story", "1999. An undefeated team, a padlocked gym, a signed contract.", "assets/video/court.jpg"),
            ("record", "record.html", "The Record", "Television, stages, honors. The proof, with sources.", "assets/img/own/torch_raised.jpg"),
            ("archive", "archive.html", "The Archive", "His photographs, the 2005 film scene by scene, the original contract.", "assets/img/own/old_team.jpg"),
            ("impact", "impact.html", "The Foundation", "The work in the neighborhood, and the relaunch.", "assets/video/classroom.jpg"),
            ("faq", "faq.html", "Facts & FAQ", "Is it a true story? The contract, the film, the numbers. Sourced.", "assets/img/private/all-stars-24-900.jpg"),
        ],
    },
    {
        "key": "work", "label": "Work with Coach", "no": "02",
        "title": "Put the standard to work",
        "blurb": "Keynotes, a six-week team program and brand partnerships, all built on the same contract.",
        "cta": ("keynotes.html#book", "Check availability"),
        "image": "assets/img/real_gym_discipline.jpg", "video": "",
        "pages": [
            ("keynotes", "keynotes.html", "Keynotes", "Five signature talks. Book a date for your stage.", "assets/img/real_gym_discipline.jpg"),
            ("teams", "teams.html", "Teams & Schools", "The Contract as a six-week team program.", "assets/img/s_team.jpg"),
            ("partners", "partners.html", "Partners", "Brand partnerships and the live package builder.", "assets/img/fieldhouse-premiere-concept.webp"),
            ("playbook", "playbook.html", "The Playbook", "One standard, ten ways in. Every offer in one place.", "assets/img/accountability-kit-concept.webp"),
        ],
    },
    {
        "key": "academy", "label": "Academy", "no": "03",
        "title": "Coach Carter Academy",
        "blurb": "The series. Class is in session. Watch the free preview, see the slate and the look of the show.",
        "cta": ("series.html", "Enter the Academy"),
        "image": "assets/video/drive.jpg", "video": "assets/video/drive.mp4",
        "pages": [
            ("series", "series.html", "The Series", "Coach Carter Academy. Free 60-second preview.", "assets/img/academy-series-title-card.webp"),
            ("series", "series.html#watch-plans", "Season One", "One-time season access, planned at launch.", "assets/img/academy-series-coach.webp"),
            ("gallery", "gallery.html", "The Lookbook", "Dress for the standard. The Academy uniform on campus.", "assets/img/academy/campaign/team-off-the-bus.webp"),
            ("series", "series.html#slate", "The Slate", "The drama, then the documentary on the man.", "assets/img/academy-series-duel.webp"),
        ],
    },
    {
        "key": "store", "label": "Store", "no": "04",
        "title": "The Academy store",
        "blurb": "The uniform, the court gear, the book and the signed editions.",
        "cta": ("store.html", "Shop everything"),
        "image": "assets/img/academy/campaign/team-off-the-bus.webp", "video": "",
        "pages": [
            ("store", "store.html#dept-campus", "Campus Uniform", "Letterman, sport coats, knits, trousers and shoes.", "assets/img/academy/academy-collection-campaign.webp"),
            ("store", "store.html#dept-basketball", "Basketball", "Game and practice jerseys, shorts, warm-ups, court gear.", "assets/img/academy/campaign/game-jersey-official-lineup.webp"),
            ("store", "store.html#dept-books", "Books & Collectibles", "Yes Ma'am, No Sir in every format, and signed editions.", "assets/img/accountability-kit-concept.webp"),
            ("store", "store.html#dept-team", "Team Pack", "The book and the Commitment Card for 25 people.", "assets/img/s_team.jpg"),
        ],
    },
    {
        "key": "company", "label": "Company", "no": "05",
        "title": "The business of the name",
        "blurb": "For investors, press and Coach's own team.",
        "cta": ("investors.html", "Read the investor memo"),
        "image": "assets/img/coach_carter_investor_banner.webp", "video": "",
        "pages": [
            ("investors", "investors.html", "Investors", "The thesis, the model, the gates and the risks.", "assets/img/coach_carter_investor_banner.webp"),
            ("brand", "brand.html", "Press & Brand Kit", "Logos, palette, approved bio and usage rules.", "assets/img/suit_full.jpg"),
            ("coach", "coach.html", "Coach's Briefing", "Private. Everything held back from the public site.", "assets/img/bentley.jpg"),
        ],
    },
]

# store departments (local nav + department directory on the store page)
STORE_DEPTS = [
    ("Campus Uniform", "#dept-campus", "assets/img/academy/academy-collection-campaign.webp",
     [("The full uniform", "#academy-store-title"), ("Sport coats & jackets", "#school-outerwear"), ("Shirts & knits", "#school-layers"), ("Trousers & skirts", "#school-bottoms"),
      ("Shoes & socks", "#school-footwear"), ("Complete looks", "#last-bell")]),
    ("Basketball", "#dept-basketball", "assets/img/academy/campaign/game-jersey-official-lineup.webp",
     [("Game jerseys", "#game-jerseys"), ("Practice jerseys", "#practice-jerseys"), ("Shorts", "#shorts"),
      ("Warm-ups", "#warm-ups"), ("Court gear", "#court-gear"), ("Accessories", "#accessories")]),
    ("Collections", "#dept-collections", "assets/img/academy/campaign/team-off-the-bus.webp",
     [("Signature Collection", "#signature-collection"), ("Combat Editions", "#combat-editions"), ("The Academy lineup", "#lineup"),
      ("First Whistle", "#first-whistle"), ("Last Bell lookbook", "#last-bell-lookbook"),
      ("Front Row Letterman", "academy-product.html?product=front-row-letterman")]),
    ("Watch", "#dept-watch", "assets/img/academy-series-coach.webp",
     [("Season One access", "#watch-plans"), ("About the series", "series.html")]),
    ("Books & Collectibles", "#dept-books", "assets/img/accountability-kit-concept.webp",
     [("Yes Ma'am, No Sir", "#editions"), ("Signed editions", "#preorders")]),
    ("Team Pack", "#dept-team", "assets/img/s_team.jpg",
     [("The book for 25", "#team-pack"), ("The six-week program", "teams.html")]),
]

# motion plates: (dept index, key, scene, title lines, blurb, regex of the section it opens, top-level?)
PLATES = [
    (0, "campus", "seal", ["Campus", "Uniform"], "Letterman, sport coats, knits, pleats and penny loafers. Dressed for the front row.",
     r'<section\b[^>]*\bclass="academy-collection"', True),
    (1, "basketball", "court", ["Basketball"], "Game and practice jerseys, shorts, warm-ups and court gear. Run the play.",
     r'<section\b[^>]*\bid="uniforms"', False),
    (2, "collections", "strip", ["The", "Collections"], "Signature, Combat Editions, First Whistle and the lookbooks. The contact sheet.",
     r'<section\b[^>]*\bid="signature-collection"', False),
    (3, "watch", "leader", ["Watch", "Season One"], "The series. A free sixty-second preview now, the full season at launch.",
     r'<section\b[^>]*\bid="watch-plans"', True),
    (4, "books", "contract", ["Books &", "Collectibles"], "Yes Ma\'am, No Sir in every format, and the signed editions in development.",
     r'<section\b[^>]*\bid="editions"', True),
    (5, "team", "cards", ["Team", "Pack"], "The book and the Commitment Card for twenty-five people. Everybody signs.",
     r'<section\b[^>]*\bid="team-pack"', True),
]

# reading order for the "next up" band
JOURNEY = ["home", "story", "record", "archive", "impact", "keynotes", "teams", "partners", "playbook",
           "series", "gallery", "store", "investors", "brand", "coach"]

HOME = ("home", "index.html", "Home", "The platform, start to finish.", "assets/video/hero_reel.jpg")

ICON = {
    "chev": '<svg viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg>',
    "arr": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    "search": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 8h16M4 16h16"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true" class="lk"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
}


def page_index():
    """nav key -> (world, page tuple). First entry per key wins (the page itself, not an anchor)."""
    idx = {}
    for w in WORLDS:
        for p in w["pages"]:
            if "#" in p[1] and w["key"] != "store":
                continue
            idx.setdefault(p[0], (w, p))
    return idx


PAGES = page_index()
# the store is one page with departments: as a destination it is "The Store", not its first department
PAGES["store"] = (PAGES["store"][0], ("store", "store.html", "The Store",
                                      "The uniform, the court gear, the book and the signed editions.",
                                      "assets/img/academy/campaign/team-off-the-bus.webp"))


def world_of(nav):
    hit = PAGES.get(nav)
    return hit[0] if hit else None


# ------------------------------------------------------------------------ header
def header(active):
    cur = world_of(active)
    btns, megas, mobile = [], [], []
    for w in WORLDS:
        is_cur = cur is not None and cur["key"] == w["key"]
        btns.append(
            f'<button class="world-btn{" cur" if is_cur else ""}" type="button" data-world="{w["key"]}" '
            f'aria-expanded="false" aria-controls="mega-{w["key"]}">{escape(w["label"])}{ICON["chev"]}</button>'
        )
        links = []
        for i, (key, href, label, desc, img) in enumerate(w["pages"]):
            here = ' aria-current="page"' if key == active and "#" not in href else ""
            lock = ICON["lock"] if key == "coach" else ""
            links.append(
                f'<a class="mega-link" href="{href}" data-pv="{img}" style="--i:{i}"{here}>'
                f'<span class="ml-n">{i + 1:02d}</span><span class="ml-t">{escape(label)}{lock}</span>'
                f'<span class="ml-d">{escape(desc)}</span>{ICON["arr"]}</a>'
            )
        megas.append(f'''<div class="mega" id="mega-{w["key"]}" data-mega="{w["key"]}" role="region" aria-label="{escape(w["label"])}">
    <div class="mega-in">
      <div class="mega-intro">
        <span class="mega-no">{w["no"]} <i></i> {escape(w["label"])}</span>
        <p class="mega-title">{escape(w["title"])}</p>
        <p class="mega-blurb">{escape(w["blurb"])}</p>
        <a class="mega-cta" href="{w["cta"][0]}">{escape(w["cta"][1])}{ICON["arr"]}</a>
      </div>
      <div class="mega-links">{"".join(links)}</div>
      <figure class="mega-pv" aria-hidden="true"><img src="{w["pages"][0][4]}" alt="" loading="lazy" decoding="async"><img alt="" decoding="async"><figcaption>{escape(w["pages"][0][2])}</figcaption></figure>
    </div>
  </div>''')
        mlinks = "".join(
            f'<a href="{href}"{" aria-current=page" if key == active and "#" not in href else ""}>{escape(label)}</a>'
            for key, href, label, _, _ in w["pages"]
        )
        mobile.append(f'<div class="m-world" style="--i:{len(mobile)}"><span class="m-no">{w["no"]}</span><h3>{escape(w["label"])}</h3><div class="m-links">{mlinks}</div></div>')

    return f'''<div class="progress" aria-hidden="true"><i></i></div>
<header class="nav nav2">
  <div class="wrap">
    <a class="nav-logo" href="index.html" aria-label="Coach Carter — home">
      <img src="assets/brand/monogram_gold.svg" alt="" width="34" height="34">
      <img class="wm" src="assets/brand/wordmark_gold.svg" alt="The Real Coach Carter" height="22" style="height:30px">
    </a>
    <nav class="worlds" aria-label="Main">{"".join(btns)}</nav>
    <div class="nav-actions">
      <button class="icon-btn pal-btn" type="button" data-palette aria-label="Search the platform" title="Search  ( / )">{ICON["search"]}</button>
      <a class="btn btn-gold btn-sm btn-book" href="keynotes.html#book" data-magnetic>Book Coach Carter</a>
      <button class="icon-btn menu-btn" data-menu aria-label="Menu" aria-expanded="false">{ICON["menu"]}</button>
    </div>
  </div>
  <div class="megas">{"".join(megas)}</div>
</header>
<div class="mega-scrim" aria-hidden="true"></div>
<div class="menu menu2" role="dialog" aria-label="Menu">
  <button class="icon-btn close" data-menu aria-label="Close menu">{ICON["x"]}</button>
  <div class="m-scroll">
    <a class="m-home" href="index.html">Home</a>
    {"".join(mobile)}
    <div class="m-foot">
      <a class="btn btn-gold" href="keynotes.html#book">Book Coach Carter</a>
      <button class="btn btn-ghost" type="button" data-palette>{ICON["search"]}<span>Search</span></button>
    </div>
    <small class="internal">Review mode</small>
  </div>
</div>
'''


def localnav(active):
    if active == "home":
        return ""
    w = world_of(active)
    if w is None:
        return ""
    if active == "store":
        # each department owns several sections that are not contiguous on the page; the spy needs all of them
        def ids(href, subs):
            return " ".join(dict.fromkeys(h[1:] for h in [href] + [u for _, u in subs] if h.startswith("#")))
        links = "".join(f'<a href="{href}" data-spy="{ids(href, subs)}">{escape(label)}</a>' for label, href, _, subs in STORE_DEPTS)
        links += '<a class="ln-out" href="gallery.html">Lookbook</a>'
        return (f'<nav class="localnav" aria-label="Store departments"><div class="wrap">'
                f'<a class="ln-world" href="store.html"><span>{w["no"]}</span>Store</a>'
                f'<div class="ln-links">{links}</div></div></nav>\n')
    seen, links = set(), []
    for key, href, label, _, _ in w["pages"]:
        if "#" in href or href in seen:
            continue
        seen.add(href)
        links.append(f'<a href="{href}"{" aria-current=page" if key == active else ""}>{escape(label)}</a>')
    return (f'<nav class="localnav" aria-label="{escape(w["label"])}"><div class="wrap">'
            f'<a class="ln-world" href="{w["pages"][0][1]}"><span>{w["no"]}</span>{escape(w["label"])}</a>'
            f'<div class="ln-links">{"".join(links)}</div></div></nav>\n')


# ---------------------------------------------------------------- chapter rail
SEC_RE = re.compile(r"<section\b([^>]*)>", re.I)
SKIP_ARIA = {"from the film"}


def _text(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html))).strip()


def _short(label, n=30):
    label = label.rstrip(".")
    if len(label) <= n:
        return label
    cut = label[:n].rsplit(" ", 1)[0]
    return cut.rstrip(" ,.—-") + "…"


def _slug(label):
    s = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return s[:40].strip("-") or "section"


def chapters(body):
    """Give every labelled <section> an id and return (body, [(id, label)])."""
    used = set(re.findall(r'(?<![-\w])id="([^"]+)"', body))
    out, items, pos = [], [], 0
    matches = list(SEC_RE.finditer(body))
    for i, m in enumerate(matches):
        attrs = m.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        chunk = body[m.end():end]
        label = None
        dm = re.search(r'data-rail="([^"]*)"', attrs)
        if dm:
            label = unescape(dm.group(1))
        else:
            h = re.search(r"<h2\b[^>]*>(.*?)</h2>", chunk, re.S)
            if h and _text(h.group(1)):
                label = _text(h.group(1))
            else:
                am = re.search(r'aria-label="([^"]+)"', attrs)
                if am and unescape(am.group(1)).lower() not in SKIP_ARIA and "film-band" not in attrs:
                    label = unescape(am.group(1))
        if not label or re.search(r'class="[^"]*\b(uniform-group|hero)\b', attrs):
            continue
        idm = re.search(r'(?<![-\w])id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
        else:
            base = sid = _slug(label)
            n = 2
            while sid in used:
                sid = f"{base}-{n}"
                n += 1
            used.add(sid)
            out.append(body[pos:m.start()])
            out.append(f'<section id="{sid}"{attrs}>')
            pos = m.end()
        items.append((sid, label))
    out.append(body[pos:])
    return "".join(out), items


def rail(items):
    if len(items) < 3:
        return ""
    links = "".join(f'<a href="#{sid}"><span>{escape(_short(label))}</span></a>' for sid, label in items[:16])
    return f'<nav class="rail" aria-label="On this page">{links}</nav>\n'


# -------------------------------------------------------------------- next up
def nextup(active):
    order = [k for k in JOURNEY]
    i = order.index(active) if active in order else 0
    nxt = order[(i + 1) % len(order)]
    if active in ("coach", "store"):   # the public journey ends at the store; Company pages are reached on purpose, not by "next"
        nxt = "home"
    w, p = (None, HOME) if nxt == "home" else PAGES[nxt]
    kicker = f'Next <i></i> {escape(w["label"])}' if w else "Back to the start"
    cur = world_of(active)
    others = []
    for ow in WORLDS:
        if ow["key"] == "company" or (cur is not None and ow["key"] == cur["key"]) or (w is not None and ow["key"] == w["key"]):
            continue
        href = ow["pages"][0][1].split("#")[0] if ow["key"] != "store" else "store.html"
        others.append(f'<a class="nu-world" href="{href}"><span>{ow["no"]}</span><b>{escape(ow["label"])}</b><em>{escape(ow["title"])}</em>{ICON["arr"]}</a>')
    return f'''<section class="nextup" aria-label="Continue">
  <a class="nu-main" href="{p[1]}">
    <span class="nu-bg"><img src="{p[4]}" alt="" loading="lazy" decoding="async"></span>
    <span class="wrap nu-in">
      <span class="nu-kicker">{kicker}</span>
      <span class="nu-title"><span>{escape(p[2])}</span></span>
      <span class="nu-desc">{escape(p[3])}</span>
      <span class="nu-go" aria-hidden="true">{ICON["arr"]}</span>
    </span>
  </a>
  <div class="wrap nu-worlds">{"".join(others)}</div>
</section>
'''


# --------------------------------------------------------------------- footer
def footer_cols(series_price):
    cols = []
    for w in WORLDS:
        seen, lis = set(), []
        for key, href, label, _, _ in w["pages"]:
            if href in seen:
                continue
            seen.add(href)
            lis.append(f'<li><a href="{href}">{escape(label)}</a></li>')
        if w["key"] == "work":
            lis.append('<li><a href="partners.html#builder">Build a package</a></li>')
        if w["key"] == "store":
            lis.append(f'<li><a href="series.html#watch-plans">Season One · {series_price} planned</a></li>')
        cols.append(f'<div><h6><span>{w["no"]}</span>{escape(w["label"])}</h6><ul>{"".join(lis)}</ul></div>')
    return "".join(cols)


# --------------------------------------------------------- store departments
def store_directory():
    tiles = []
    for i, (label, href, img, subs) in enumerate(STORE_DEPTS):
        sl = "".join(f'<li><a href="{h}">{escape(t)}</a></li>' for t, h in subs)
        tiles.append(f'''<article class="dept" style="--i:{i}">
      <a class="dept-top" href="{href}"><span class="dept-img"><img src="{img}" alt="" loading="lazy" decoding="async"></span>
        <span class="dept-no">{i + 1:02d}</span><h3>{escape(label)}</h3></a>
      <ul>{sl}</ul>
    </article>''')
    return f'''<section class="store-depts" id="departments" aria-labelledby="departments-title" data-rail="Departments">
  <div class="store-shell">
    <header class="depts-head"><p class="store-label">Shop by department</p><h2 id="departments-title">Six departments. One standard.</h2></header>
    <div class="depts">{"".join(tiles)}</div>
  </div>
</section>
'''


# ------------------------------------------------------------------- home hub
def hub():
    panels = []
    for i, w in enumerate(x for x in WORLDS if x["key"] != "company"):
        seen, links = set(), []
        for _, href, label, _, _ in w["pages"]:
            if href in seen:
                continue
            seen.add(href)
            links.append(f'<li><a href="{href}">{escape(label)}</a></li>')
        video = (f'<video muted loop playsinline preload="none" data-src="{w["video"]}"></video>' if w["video"] else "")
        panels.append(f'''<article class="hub-panel{" on" if i == 0 else ""}" style="--i:{i}" aria-labelledby="hub-{w["key"]}">
      <div class="hp-media"><img src="{w["image"]}" alt="" loading="lazy" decoding="async">{video}</div>
      <span class="hp-no">{w["no"]}</span>
      <div class="hp-copy">
        <h3 class="hp-title" id="hub-{w["key"]}">{escape(w["label"])}</h3>
        <div class="hp-body"><div>
          <p>{escape(w["blurb"])}</p>
          <ul class="hp-links">{"".join(links)}</ul>
          <a class="btn btn-gold btn-sm" href="{w["cta"][0]}">{escape(w["cta"][1])}{ICON["arr"]}</a>
        </div></div>
      </div>
    </article>''')
    company = next(x for x in WORLDS if x["key"] == "company")
    clinks = "".join(f'<a href="{href}">{escape(label)}{ICON["lock"] if key == "coach" else ""}</a>' for key, href, label, _, _ in company["pages"])
    return f'''<section class="hub" id="platform" aria-labelledby="hub-title" data-rail="The platform">
  <div class="wrap hub-head">
    <div><span class="eyebrow">The platform</span><h2 class="h-l mt-s" id="hub-title">One standard.<br><span class="gold-text">Four ways in.</span></h2></div>
    <p class="lede">The man, the work, the series and the store. Everything Coach Carter has built, and everything he is building next, starts here.</p>
  </div>
  <div class="hub-panels">
    {"".join(panels)}
  </div>
  <div class="wrap"><div class="hub-company"><span>Company</span>{clinks}<a class="sp" href="impact.html">The Foundation</a><button type="button" data-palette>{ICON["search"]}Search everything</button></div></div>
</section>
'''


# --------------------------------------------------------------- search index
_index = []


def _add(kind, title, sub, url, img=""):
    _index.append({"k": kind, "t": title, "s": sub, "u": url, "i": img})


def index_page(meta, name, items):
    nav = "home" if name == "index.html" else name[:-5]
    w = world_of(nav)
    label = PAGES[nav][1][2] if nav in PAGES else "Home"
    world = w["label"] if w else "Home"
    img = PAGES[nav][1][4] if nav in PAGES else HOME[4]
    _add("Page", label, f'{world} · {meta.get("desc", "")}'[:120], name, img)
    if nav == "coach":
        return
    for sid, text in items:
        _add("Section", text.rstrip("."), f"{world} · {label}", f"{name}#{sid}")


def write_index():
    try:
        cat = json.loads((OUT / "assets/data/academy-products.json").read_text())
        for p in cat["products"]:
            _add("Product", p["name"], " · ".join(x for x in ("Store", p.get("kind", "")) if x),f'academy-product.html?product={p["id"]}', p.get("image", ""))
    except Exception as e:  # catalog is owned by another workstream; the palette still works without it
        print("search index: products skipped:", e)
    try:
        film = json.loads((OUT / "assets/data/film.json").read_text())
        for c in film.get("clips", []):
            if c.get("scene"):
                _add("Scene", c["scene"], "The 2005 film · Archive", "archive.html#the-2005-film")
    except Exception as e:
        print("search index: scenes skipped:", e)
    for t, s, u in [
        ("Book Coach Carter", "Keynotes · Check availability", "keynotes.html#book"),
        ("Watch the free preview", "Coach Carter Academy · 60 seconds", "series.html#watch-plans"),
        ("Build a partnership package", "Partners · Live builder", "partners.html#builder"),
        ("Bring The Contract to your team", "Teams & Schools · Inquiry", "teams.html#inquire"),
        ("Sign the contract", "Home · Join the Locker Room list", "index.html#contract"),
    ]:
        _add("Action", t, s, u)
    (OUT / "assets/data/search.json").write_text(json.dumps(_index, ensure_ascii=False, separators=(",", ":")))
    print("search index", len(_index), "entries")
    _index.clear()


# ---------------------------------------------------------------------- apply
# The cross-page view transition is opted into from here, not from shell.css: automated browsers
# (navigator.webdriver) skip it because Playwright's headless shell never paints the incoming page.
HEAD_BOOT = ('<script>try{if(sessionStorage.getItem("cc_seen"))document.documentElement.classList.add("seen");'
             'sessionStorage.setItem("cc_seen","1")}catch(e){}'
             'if(!navigator.webdriver&&!matchMedia("(prefers-reduced-motion: reduce)").matches){'
             'var vt=document.createElement("style");vt.textContent="@view-transition{navigation:auto}";document.head.appendChild(vt)}</script>\n'
             '<script type="speculationrules">{"prefetch":[{"where":{"and":[{"href_matches":"/*"},'
             '{"not":{"selector_matches":"[target=_blank],[download]"}}]},"eagerness":"moderate"}]}</script>\n')

HEADER_RE = re.compile(r'<header class="nav">.*?<small class="internal">Review mode</small>\s*</div>\s*', re.S)
FOOT_COLS_RE = re.compile(r'(<div class="f-top">\s*<div>.*?</form>\s*</div>)(.*?)(\s*</div>\s*<div class="f-giant">)', re.S)
SOCIAL_RE = re.compile(r'<div class="socials mt-m">.*?</div>', re.S)
STORE_NAV_RE = re.compile(r'<nav class="store-nav".*?</nav>\s*', re.S)


def apply(html, meta, name, series_price="$19.99"):
    meta_nav = meta.get("nav", "home")           # drives body class + page CSS (gallery.html uses "store")
    nav = "home" if name == "index.html" else name[:-5]   # the shell goes by the page itself

    # 1. header -> worlds header + local nav
    if not HEADER_RE.search(html):
        raise SystemExit(f"{name}: shell could not find the header block")
    html = HEADER_RE.sub(lambda _: header(nav) + localnav(nav), html, count=1)

    # 2. the old full-screen wipe delayed every click by 620 ms; view transitions replace it
    html = html.replace('<div class="wipe" aria-hidden="true"></div>\n', "")

    # 3. store: the 11-link strip becomes the departments local nav + a department directory
    if nav == "store":
        html = STORE_NAV_RE.sub("", html, count=1)
        m = re.search(r'</section>', html[html.index('class="store-campaign"'):])
        at = html.index('class="store-campaign"') + m.end()
        html = html[:at] + "\n" + store_directory() + html[at:]
    if nav == "archive":   # the private collection opens the archive, ahead of the public record
        m = re.search(r'<section\b[^>]*\bid="headliners-sec"', html)
        if not m:
            raise SystemExit(f"{name}: no place for the private collection")
        html = html[:m.start()] + private.collection() + html[m.start():]

    if "{{faq}}" in html:
        html = html.replace("{{faq}}", seo.faq_html(), 1)

    if "{{hub}}" in html:
        html = html.replace("{{hub}}", hub(), 1)

    # 4. chapters: ids + rail + search entries
    a, b = html.index('<main id="main">'), html.index("</main>")
    body, items = chapters(html[a:b])
    html = html[:a] + body + html[b:]
    index_page(meta, name, items)

    # plates are added after the chapter pass so their headings never label a neighbouring section
    if nav == "store":
        for di, key, scene, lines, blurb, target, top in PLATES:
            label, _, _, subs = STORE_DEPTS[di]
            m = re.search(target, html)
            if not m:
                raise SystemExit(f"{name}: no section for the {label} plate ({target})")
            card = motion.plate(key, scene, f"{di + 1:02d}", lines, blurb, subs, label)
            if top:
                card = f'<div class="plate-wrap">{card}</div>'
            html = html[:m.start()] + card + "\n" + html[m.start():]

    # every inner page opens with its own plate: a title card that is also the chapter index
    if nav in motion_pages.PAGE_PLATES:
        scene, kicker, lines, blurb, links, target = motion_pages.PAGE_PLATES[nav]
        m = re.search(target, html)
        if not m:
            raise SystemExit(f"{name}: no section for the page plate ({target})")
        label = PAGES[nav][1][2]
        card = motion.plate(nav, scene, "", lines, blurb, links, label, kicker=kicker, pid="chapters")
        html = html[:m.start()] + f'<div class="plate-wrap plate-wrap--page">{card}</div>\n' + html[m.start():]

    # 5. rail + next-up band before the footer
    if html.count("\n</main>") != 1:
        raise SystemExit(f"{name}: shell expected exactly one </main> on its own line")
    html = html.replace("\n</main>", "\n" + nextup(nav) + "</main>\n" + rail(items), 1)

    # 6. footer sitemap = the same worlds
    m = FOOT_COLS_RE.search(html)
    if not m:
        raise SystemExit(f"{name}: shell could not find the footer columns")
    soc = SOCIAL_RE.search(m.group(2))
    social = soc.group(0).replace("socials mt-m", "socials") if soc else ""
    html = html[:m.start()] + m.group(1).replace("</form>", "</form>\n        " + social) + footer_cols(series_price) + m.group(3) + html[m.end():]

    # 7. assets
    html = html.replace("</head>", f'<link rel="stylesheet" href="assets/css/shell.css?v={V}">\n{HEAD_BOOT}</head>', 1)
    html = html.replace("</body>", f'<script defer src="assets/js/shell.js?v={V}"></script>\n</body>', 1)
    share = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    html = seo.apply(html, meta, name, nav, PAGES[nav][1][2] if nav in PAGES else "Home", world_of(nav), share.group(1) if share else seo.IMG)
    if "data-plate" in html:
        html = html.replace("</head>", f'<link rel="stylesheet" href="assets/css/motion.css?v={V}">\n</head>', 1)
        html = html.replace("</body>", f'<script defer src="assets/js/motion.js?v={V}"></script>\n</body>', 1)
    html = html.replace(f'<body class="page-{meta_nav}">', f'<body class="page-{meta_nav} world-{(world_of(nav) or {"key": "home"})["key"]}">', 1)
    return html

# ------------------------------------------------- hand-built product page
# site/academy-product.html is written by hand (another workstream owns its body). It gets the
# same header, departments bar and search through three marked blocks that are replaced on
# every build, so the rest of the file is never touched.
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Cinzel:wght@500;700'
         '&family=Cormorant+Garamond:ital,wght@1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')


def _marked(html, tag, block, before):
    start, end = f"<!--shell:{tag}-->", f"<!--/shell:{tag}-->"
    full = f"{start}{block}{end}\n"
    if start in html:
        a, b = html.index(start), html.index(end) + len(end)
        return html[:a] + full.rstrip("\n") + html[b:]
    if before not in html:
        raise SystemExit(f"academy-product.html: shell could not find {before!r}")
    return html.replace(before, full + before, 1)


def apply_product():
    path = OUT / "academy-product.html"
    html = path.read_text()
    bar = localnav("store").replace('href="#dept-', 'href="store.html#dept-')
    bar = re.sub(r' data-spy="[^"]*"', "", bar)
    top = (header("store").replace('<header class="nav nav2">', '<header class="nav nav2 solid" data-standalone>')
           + bar)
    html = _marked(html, "css", f'{FONTS}<link rel="stylesheet" href="assets/css/shell.css?v={V}">{HEAD_BOOT.strip()}', "</head>")
    html = _marked(html, "js", f'<script defer src="assets/js/shell.js?v={V}"></script>', "</body>")
    m = re.search(r"<body[^>]*>\n?", html)
    if "<!--shell:top-->" in html:
        html = _marked(html, "top", f'<div class="shell-top">{top}</div>', "")
    else:
        html = html[:m.end()] + f'<!--shell:top--><div class="shell-top">{top}</div><!--/shell:top-->\n' + html[m.end():]
    path.write_text(html)
    print("shelled academy-product.html", len(html))
