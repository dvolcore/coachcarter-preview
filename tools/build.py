"""Assemble site/*.html from src/*.html page bodies + shared layout.

Each src page starts with a JSON header comment:
<!--{"title": "...", "desc": "...", "nav": "story", "store": true}-->
Run: python3 tools/build.py
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "site"
SERIES_PRICE = "$19.99"


def academy_cards(catalog, group=None):
    products = {product["id"]: product for product in catalog["products"]}
    collection = catalog["collections"].get(group)
    selected = ([products[key] for key in collection] if collection is not None else
                [product for product in products.values() if product.get("group") == group])
    cards = []
    for product in selected:
        item = {key: escape(product[key]) for key in ("id", "image", "alt", "name", "kind")}
        item["availability"] = escape(product.get("status") or product["price"])
        item["width"] = product.get("image_width", 900)
        item["height"] = product.get("image_height", 1350)
        links = []
        for key in product.get("pieces", []):
            name = escape(products[key]["name"])
            links.append(f'<li><a class="store-text-link" href="academy-product.html?product={escape(key)}">{name}</a></li>')
        item["pieces"] = '<ul class="academy-piece-links">' + "".join(links) + "</ul>" if links else ""
        cards.append('''<article class="academy-product-card">
        <a class="academy-product-link" href="academy-product.html?product={id}">
          <img src="{image}" alt="{alt}" loading="lazy" width="{width}" height="{height}">
          <div class="academy-product-meta">
            <div><h3>{name}</h3><p>{kind}</p></div>
            <div><span>{availability}</span><span class="academy-product-arrow" aria-hidden="true">↗</span></div>
          </div>
        </a>{pieces}
      </article>'''.format(**item))
    return "\n      ".join(cards)


def front_row_views(catalog):
    jacket = next(product for product in catalog["products"] if product["id"] == "front-row-letterman")
    return "\n        ".join(
        f'<a href="academy-product.html?product=front-row-letterman#{escape(view["id"])}">'
        f'<img src="{escape(view["image"])}" alt="" width="{view["width"]}" height="{view["height"]}" loading="lazy">'
        f'<span>{escape(view["label"])}</span></a>'
        for view in jacket["views"]
    )


def series_offer():
    return f'''<section class="series-offer section" id="watch-plans" aria-labelledby="series-offer-title">
  <div class="wrap">
    <div class="series-offer-grid">
      <div class="series-offer-art">
        <img src="assets/img/academy-series-title-card.webp" alt="Coach Carter Academy title over an empty basketball court" width="1280" height="720" loading="lazy">
        <span class="series-preview-tag">Free preview · 60 seconds</span>
      </div>
      <div class="series-offer-copy">
        <span class="eyebrow">Coach Carter Academy · Web series</span>
        <h2 class="h-l mt-s" id="series-offer-title">The preview is free.<br><span class="gold-text">The story is worth it.</span></h2>
        <div class="series-price"><strong>{SERIES_PRICE}</strong><span>Season One<br>One-time purchase · USD</span></div>
        <p class="series-price-note">Planned launch price · Paid access coming soon</p>
        <p class="series-offer-description">Get a first look now. Full episodes will be available through paid season access when the series launches.</p>
        <ul class="series-includes"><li>Full Season One access at launch</li><li>No monthly subscription</li><li>Public viewing is preview only</li></ul>
        <button class="btn btn-gold" data-video="assets/video/academy-preview-60.mp4" data-poster="assets/img/academy-series-title-card.webp">{ICON['play']}<span>Watch the free preview</span></button>
        <p class="series-availability">In development. Final episode lineup and release date will be announced before sales open. No payments are being taken.</p>
      </div>
    </div>
  </div>
</section>'''

NAV = [
    ("story", "story.html", "Story"),
    ("record", "record.html", "Record"),
    ("archive", "archive.html", "Archive"),
    ("keynotes", "keynotes.html", "Keynotes"),
    ("teams", "teams.html", "Teams"),
    ("partners", "partners.html", "Partners"),
    ("store", "store.html", "Store"),
    ("playbook", "playbook.html", "Playbook"),
    ("series", "series.html", "Series"),
    ("investors", "investors.html", "Investors"),
    ("coach", "coach.html", "Coach"),
]

ICON = {
    "arr": '<svg class="arr" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 12h15M13 6l6 6-6 6"/></svg>',
    "bag": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 8h14l-1 12H6L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 8h16M4 16h16"/></svg>',
    "x": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "play": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M7 4.5v15l13-7.5z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" fill="none" stroke="#08090B" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
    "out": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="16" height="16"><path d="M7 17L17 7M9 7h8v8"/></svg>',
    "yt": '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.7 15.1V8.9l5.8 3.1-5.8 3.1z"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M14 8.5V6.8c0-.8.5-1 .9-1h2.4V2.1L14 2c-3.6 0-4.4 2.7-4.4 4.4v2.1H7.3v3.8h2.3V22H14v-9.7h3l.4-3.8H14z"/></svg>',
}


def head(meta):
    title = meta["title"]
    desc = meta.get("desc", "")
    share_image = {
        "series": "assets/img/academy-series-title-card.webp",
        "store": "assets/img/academy-series-title-card.webp",
        "investors": "assets/img/coach_carter_investor_banner.webp",
    }.get(meta.get("nav"), "assets/img/portrait_ken.jpg")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#08090B">
<script>(function(d){{d.classList.add("js");try{{var q=location.search;if(/[?&]review(=|&|$)/.test(q))localStorage.setItem("cc_review","1");if(/[?&]client(=|&|$)/.test(q))localStorage.removeItem("cc_review");if(localStorage.getItem("cc_review"))d.classList.add("review")}}catch(e){{}}}})(document.documentElement)</script>
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://dvolcore.github.io/coachcarter-preview/{share_image}">
<link rel="icon" href="assets/brand/appicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Cinzel:wght@500;700&family=Cormorant+Garamond:ital,wght@1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="stylesheet" href="assets/css/fx.css">
<link rel="stylesheet" href="assets/css/gap1.css">
<link rel="stylesheet" href="assets/css/gap2.css">
<link rel="stylesheet" href="assets/css/gap3.css">
<link rel="stylesheet" href="assets/css/gap4.css">
</head>
<body class="page-{meta.get('nav', 'home')}">
<div class="curtain" aria-hidden="true"><img src="assets/brand/crest_gold.svg" alt=""></div>
<div class="wipe" aria-hidden="true"></div>
<a class="sr" href="#main">Skip to content</a>
"""


def header(active):
    links = "".join(
        f'<a href="{href}"{" aria-current=page" if key == active else ""}>{label}</a>' for key, href, label in NAV
    )
    mlinks = "".join(f'<a class="big" href="{href}">{label}</a>' for _, href, label in NAV)
    return f"""<header class="nav">
  <div class="wrap">
    <a class="nav-logo" href="index.html" aria-label="Coach Carter — home">
      <img src="assets/brand/monogram_gold.svg" alt="" width="34" height="34">
      <img class="wm" src="assets/brand/wordmark_gold.svg" alt="The Real Coach Carter" height="22" style="height:30px">
    </a>
    <nav class="nav-links" aria-label="Main">{links}</nav>
    <div class="nav-actions">
      <a class="btn btn-gold btn-sm btn-book" href="keynotes.html#book" data-magnetic>Book Coach Carter</a>
      <button class="icon-btn menu-btn" data-menu aria-label="Menu" aria-expanded="false">{ICON['menu']}</button>
    </div>
  </div>
</header>
<div class="menu" role="dialog" aria-label="Menu">
  <button class="icon-btn close" data-menu aria-label="Close menu">{ICON['x']}</button>
  <a class="big" href="index.html">Home</a>{mlinks}
  <a class="btn btn-gold mt-m" href="keynotes.html#book" style="align-self:flex-start">Book Coach Carter</a>
  <small class="internal">Review mode</small>
</div>
"""


def footer(nav=""):
    bgv = "" if nav == "investors" else '<div class="bgv"><video data-auto muted loop playsinline preload="none" poster="assets/video/outro.jpg?v=2" data-src="assets/video/outro.mp4?v=2"></video></div>'
    # investors page is business-only: no video modal, no film player script
    vmodal = "" if nav == "investors" else f"""<div class="modal video" id="video-modal" role="dialog" aria-label="Video"><div class="box"><button class="icon-btn x" data-close aria-label="Close" style="background:rgba(0,0,0,.5)">{ICON['x']}</button><video controls playsinline preload="none"></video></div></div>"""
    filmjs = "" if nav == "investors" else '<script defer src="assets/js/film.js"></script>'
    return f"""
<footer class="footer">
  {bgv}
  <div class="wrap">
    <div class="f-top">
      <div>
        <img src="assets/brand/crest_gold.svg" alt="" width="96" height="96">
        <p class="body-mute mt-s" style="max-width:34ch">The official platform of Coach Ken Carter — educator, author, speaker and the real coach behind the 2005 film.</p>
        <form class="news" data-simple="You're on the list" aria-label="Newsletter">
          <input type="email" required placeholder="Email for the Locker Room letter" aria-label="Email">
          <button type="submit">Join →</button>
        </form>
      </div>
      <div><h6>Explore</h6><ul>
        <li><a href="story.html">The Story</a></li><li><a href="record.html">The Record</a></li>
        <li><a href="series.html">Coach Carter Academy</a></li><li><a href="impact.html">Foundation</a></li></ul></div>
      <div><h6>Work with Coach</h6><ul>
        <li><a href="keynotes.html#book">Book a keynote</a></li><li><a href="partners.html">Brand partnerships</a></li>
        <li><a href="partners.html#builder">Build a package</a></li><li><a href="brand.html">Press &amp; brand kit</a></li></ul></div>
      <div><h6>Store</h6><ul>
        <li><a href="series.html#watch-plans">Web series · {SERIES_PRICE} planned</a></li>
        <li><a href="store.html?cat=books">Books</a></li><li><a href="store.html?cat=apparel">Apparel</a></li>
        <li><a href="store.html?cat=collectibles">Signed collectibles</a></li><li><a href="store.html?cat=film">The film</a></li></ul>
        <div class="socials mt-m">
          <a class="icon-btn" href="https://www.youtube.com/channel/UCkq8ZF3PXaOsHDjgxggkrBg" target="_blank" rel="noopener" aria-label="YouTube">{ICON['yt']}</a>
          <a class="icon-btn" href="https://www.facebook.com/Coachkcarter" target="_blank" rel="noopener" aria-label="Facebook">{ICON['fb']}</a>
        </div></div>
    </div>
    <div class="f-giant"><img src="assets/brand/wordmark_gold.svg" alt="The Real Coach Carter — Winners do one thing. We win." loading="lazy"></div>
    <div class="f-bottom">
      <span>© <span data-curyear>2026</span> Coach Ken Carter. All rights reserved.</span>
      <span>"Coach Carter" (2005) is a Paramount Pictures / MTV Films release. Coach Carter (2005) © Paramount Pictures / MTV Films. Film scenes included for private client review.</span>
    </div>
  </div>
</footer>
<div class="scrim"></div>
{vmodal}
<div class="toast" role="status" aria-live="polite"><img src="assets/brand/monogram_gold.svg" alt="" width="18" height="18" style="filter:brightness(.2)"><span></span></div>
<div class="preview-flag internal">Review mode · internal notes visible</div>
<script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
<script defer src="assets/js/site.js"></script>
{filmjs}
<script defer src="assets/js/store.js"></script>
</body>
</html>
"""


def coach_sections():
    """Private Coach briefing: index of strong bullets, then every section (key points, then detail)."""
    from html import escape as e
    data = json.loads((OUT / "assets/data/coach.json").read_text())
    idx, body, n = [], [], 0
    for pi, part in enumerate(data["parts"]):
        sec_html, links = [], []
        for s in part["sections"]:
            n += 1
            links.append(f'<li><a href="#c-{e(s["id"])}"><span class="ch-n">{n:02d}</span><b>{e(s["title"])}</b><span class="ch-k">{e(s["key_points"][0])}</span></a></li>')
            kp = "".join(f"<li>{e(k)}</li>" for k in s["key_points"])
            det = []
            for d in s.get("detail", []):
                h = f'<h4>{e(d["heading"])}</h4>' if d.get("heading") else ""
                if "table" in d:
                    t = d["table"]
                    th = "".join(f"<th>{e(str(c))}</th>" for c in t["head"])
                    rows = "".join("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in r) + "</tr>" for r in t["rows"])
                    det.append(f'<div class="ch-block">{h}<div class="ch-table"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div></div>')
                elif "items" in d:
                    items = [str(i) for i in d["items"]]
                    if items and all(re.match(r"\d+[.)] ", i) for i in items):
                        lis = "".join(f"<li>{e(re.sub(r'^\d+[.)] ', '', i))}</li>" for i in items)
                        det.append(f'<div class="ch-block">{h}<ol class="ch-list">{lis}</ol></div>')
                    else:
                        det.append(f'<div class="ch-block">{h}<ul class="ch-list">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul></div>")
                elif "note" in d:
                    det.append(f'<div class="ch-block">{h}<p>{e(d["note"])}</p></div>')
            sec_html.append(f'''<article class="ch-sec" id="c-{e(s["id"])}">
  <header class="ch-sec-head"><span class="ch-tag">{n:02d} · {e(s.get("chapter",""))}</span><h3 class="h-m">{e(s["title"])}</h3>
  <p class="ch-why"><span>Why it's here, not on the public site:</span> {e(s.get("why_left_out",""))}</p></header>
  <div class="ch-key"><span class="ch-key-l">The key points</span><ul>{kp}</ul></div>
  <div class="ch-detail"><span class="ch-key-l">In full</span>{"".join(det)}</div>
</article>''')
        idx.append(f'<div class="ch-idx-part"><h3><span>Part {pi+1}</span> {e(part["title"])}</h3><ul>{"".join(links)}</ul></div>')
        body.append(f'''<section class="section ch-part" id="part-{pi+1}"><div class="wrap">
  <div class="ch-part-head"><span class="eyebrow">Part {pi+1}</span><h2 class="h-l">{e(part["title"])}</h2><p class="lede">{e(part["sub"])}</p></div>
  {"".join(sec_html)}
</div></section>''')
    return {"index": "".join(idx), "body": "".join(body), "count": str(n)}


def build():
    pages = sorted(SRC.glob("*.html"))
    for p in pages:
        raw = p.read_text()
        m = re.match(r"<!--(\{.*?\})-->\s*", raw, re.S)
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        body = body.replace("{{series_offer}}", series_offer()).replace("{{series_price}}", SERIES_PRICE)
        if "{{coach_index}}" in body:
            c = coach_sections()
            body = body.replace("{{coach_index}}", c["index"]).replace("{{coach_body}}", c["body"]).replace("{{coach_count}}", c["count"])
        if "{{academy_cards}}" in body:
            catalog = json.loads((OUT / "assets/data/academy-products.json").read_text())
            body = (body.replace("{{academy_cards}}", academy_cards(catalog))
                    .replace("{{last_bell_cards}}", academy_cards(catalog, "last-bell"))
                    .replace("{{court_gear_cards}}", academy_cards(catalog, "court-gear"))
                    .replace("{{front_row_views}}", front_row_views(catalog)))
        for k, v in ICON.items():
            body = body.replace("{{" + k + "}}", v)
        html = head(meta) + header(meta.get("nav", "home")) + '<main id="main">\n' + body + "\n</main>" + footer(meta.get("nav", "home"))
        (OUT / p.name).write_text(html)
        print("built", p.name, len(html))


if __name__ == "__main__":
    build()
