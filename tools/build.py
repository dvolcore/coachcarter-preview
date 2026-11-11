"""Assemble site/*.html from src/*.html page bodies + shared layout.

Each src page starts with a JSON header comment:
<!--{"title": "...", "desc": "...", "nav": "story", "store": true}-->
Run: python3 tools/build.py
"""
import json
import re
from html import escape
from pathlib import Path

import shell  # platform shell v2: worlds nav, local nav, chapter rail, next-up, search index

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "site"
SERIES_PRICE = "$19.99"


def academy_cards(catalog, group=None, heading="h3"):
    products = {product["id"]: product for product in catalog["products"]}
    collection = catalog["collections"].get(group)
    selected = ([products[key] for key in collection] if collection is not None else
                [product for product in products.values() if product.get("group") == group])
    cards = []
    for product in selected:
        item = {key: escape(product[key]) for key in ("id", "image", "alt", "name", "kind")}
        item["availability"] = escape(product.get("status") or product["price"])
        item["heading"] = heading
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
            <div><{heading}>{name}</{heading}><p>{kind}</p></div>
            <div><span>{availability}</span><span class="academy-product-arrow" aria-hidden="true">↗</span></div>
          </div>
        </a>{pieces}
      </article>'''.format(**item))
    return "\n      ".join(cards)


def jersey_previews(catalog, product_id):
    jersey = next(product for product in catalog["products"] if product["id"] == product_id)
    return "".join(
        f'<img src="{escape(style["image"])}" alt="" loading="lazy" width="{style["image_width"]}" height="{style["image_height"]}">'
        for style in jersey["styles"]
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
    """Private Coach briefing: index of strong bullets, then every section (key points, then the detail folded
    into a closed <details>). Also emits the sticky position bar and its Index sheet. Every word of coach.json
    stays in the DOM; new interface text is marked data-ui."""
    from html import escape as e
    data = json.loads((OUT / "assets/data/coach.json").read_text())
    total = sum(len(p["sections"]) for p in data["parts"])
    idx, body, sheet, n = [], [], [], 0

    def words(x):
        return len(re.findall(r"\w+", str(x)))

    def plural(k, w):
        return f"{k} {w}" + ("" if k == 1 else "s")

    for pi, part in enumerate(data["parts"]):
        sec_html, links, toc = [], [], []
        for s in part["sections"]:
            n += 1
            sid = e(s["id"])
            links.append(f'<li><a href="#c-{sid}"><span class="ch-n">{n:02d}</span><b>{e(s["title"])}</b><span class="ch-k">{e(s["key_points"][0])}</span></a></li>')
            toc.append(f'<li><a href="#c-{sid}"><span>{n:02d}</span>{e(s["title"])}</a></li>')
            kp = "".join(f"<li>{e(k)}</li>" for k in s["key_points"])
            det, wc, ntab = [], 0, 0
            for d in s.get("detail", []):
                h = f'<h4>{e(d["heading"])}</h4>' if d.get("heading") else ""
                wc += words(d.get("heading", ""))
                if "table" in d:
                    t = d["table"]
                    ntab += 1
                    heads = [e(str(c)) for c in t["head"]]
                    th = "".join(f'<th scope="col">{c}</th>' for c in heads)
                    rows = "".join("<tr>" + "".join(
                        f'<td data-label="{heads[i] if i < len(heads) else ""}">{e(str(c))}</td>' for i, c in enumerate(r)) + "</tr>" for r in t["rows"])
                    wc += sum(words(c) for c in t["head"]) + sum(words(c) for r in t["rows"] for c in r)
                    lab = e(d.get("heading") or s["title"]) + " (table)"
                    det.append(f'<div class="ch-block">{h}<div class="ch-table" role="region" aria-label="{lab}"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div></div>')
                elif "items" in d:
                    items = [str(i) for i in d["items"]]
                    wc += sum(words(i) for i in items)
                    if items and all(re.match(r"\d+[.)] ", i) for i in items):
                        lis = "".join(f"<li>{e(re.sub(r'^\d+[.)] ', '', i))}</li>" for i in items)
                        det.append(f'<div class="ch-block">{h}<ol class="ch-list">{lis}</ol></div>')
                    else:
                        det.append(f'<div class="ch-block">{h}<ul class="ch-list">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul></div>")
                elif "note" in d:
                    wc += words(d["note"])
                    det.append(f'<div class="ch-block">{h}<p>{e(d["note"])}</p></div>')
            mins = max(1, -(-wc // 230))
            meta = [f"~{mins} min read", plural(len(det), "block")] + ([plural(ntab, "table")] if ntab else [])
            more = ""
            if det:
                more = f'''<details class="ch-more" id="c-{sid}-full">
    <summary><span class="ch-key-l">In full</span><span class="ch-more-meta" data-ui>{" · ".join(meta)}</span><span class="ch-more-act" data-ui aria-hidden="true"><span class="o">Read in full</span><span class="c">Close</span><i></i></span></summary>
    <div class="ch-detail">{"".join(det)}
    <button class="ch-more-close" type="button" data-ui>Close “{e(s["title"])}” in full</button></div>
  </details>'''
            sec_html.append(f'''<article class="ch-sec" id="c-{sid}" data-n="{n}" data-part="{pi+1}" data-title="{e(s["title"])}">
  <header class="ch-sec-head"><span class="ch-tag">{n:02d} · {e(s.get("chapter",""))}</span><h3 class="h-m">{e(s["title"])}</h3>
  <p class="ch-why"><span>Why it's here, not on the public site:</span> {e(s.get("why_left_out",""))}</p></header>
  <div class="ch-key"><span class="ch-key-l">The key points</span><ul>{kp}</ul></div>
  {more}
</article>''')
        cnt = len(part["sections"])
        idx.append(f'<div class="ch-idx-part"><h3><span>Part {pi+1}</span> {e(part["title"])}</h3><ul>{"".join(links)}</ul></div>')
        sheet.append(f'<li class="ch-sheet-part"><a class="ch-sheet-ph" href="#part-{pi+1}"><span>Part {pi+1}</span>{e(part["title"])}</a><ol>{"".join(toc)}</ol></li>')
        body.append(f'''<section class="section ch-part" id="part-{pi+1}" data-title="{e(part["title"])}"><div class="wrap">
  <div class="ch-part-head"><span class="ch-part-n" aria-hidden="true" data-ui>{pi+1:02d}</span><div class="ch-part-copy"><span class="eyebrow">Part {pi+1}</span><h2 class="h-l">{e(part["title"])}</h2><p class="lede">{e(part["sub"])}</p>
  <p class="ch-part-count" data-ui>{plural(cnt, "section")} in this part</p><ol class="ch-part-toc" data-ui aria-label="Sections in part {pi+1}">{"".join(toc)}</ol></div></div>
  {"".join(sec_html)}
</div></section>''')
    bar = f'''<nav class="ch-bar" aria-label="Briefing position" data-ui>
  <div class="ch-bar-in">
    <p class="ch-bar-where"><span class="ch-bar-part">Index</span><span class="ch-bar-n"><b>00</b>/{total:02d}</span><span class="ch-bar-t">What this covers</span></p>
    <button class="ch-bar-btn ch-bar-all" type="button" aria-pressed="false"><span class="o">Expand all</span><span class="c">Collapse all</span></button>
    <button class="ch-bar-btn ch-bar-idx" type="button" aria-haspopup="dialog" aria-controls="ch-sheet" aria-expanded="false"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 4h12M2 8h12M2 12h8"/></svg>Index</button>
  </div>
  <i class="ch-bar-line" aria-hidden="true"><i></i></i>
</nav>
<dialog class="ch-sheet" id="ch-sheet" aria-labelledby="ch-sheet-t" data-ui data-lenis-prevent>
  <div class="ch-sheet-head"><p class="ch-sheet-t" id="ch-sheet-t">Briefing index <span>{total} sections · {len(data["parts"])} parts</span></p><button class="ch-sheet-x" type="button" aria-label="Close index"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 3.5l9 9M12.5 3.5l-9 9"/></svg></button></div>
  <ol class="ch-sheet-parts">{"".join(sheet)}</ol>
  <a class="ch-sheet-top" href="#covers">Back to the key-points index</a>
</dialog>'''
    return {"index": "".join(idx), "body": "".join(body), "count": str(n), "bar": bar}


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
            body = body.replace("{{coach_index}}", c["index"]).replace("{{coach_body}}", c["body"]).replace("{{coach_count}}", c["count"]).replace("{{coach_bar}}", c["bar"])
        if "_cards}}" in body:
            catalog = json.loads((OUT / "assets/data/academy-products.json").read_text())
            body = (body.replace("{{academy_cards}}", academy_cards(catalog))
                    .replace("{{school_outerwear_cards}}", academy_cards(catalog, "school-outerwear", "h4"))
                    .replace("{{school_layers_cards}}", academy_cards(catalog, "school-layers", "h4"))
                    .replace("{{school_bottoms_cards}}", academy_cards(catalog, "school-bottoms", "h4"))
                    .replace("{{school_footwear_cards}}", academy_cards(catalog, "school-footwear", "h4"))
                    .replace("{{last_bell_cards}}", academy_cards(catalog, "last-bell"))
                    .replace("{{game_jersey_previews}}", jersey_previews(catalog, "official-game-jerseys"))
                    .replace("{{practice_jersey_previews}}", jersey_previews(catalog, "official-practice-jerseys"))
                    .replace("{{shorts_cards}}", academy_cards(catalog, "shorts", "h4"))
                    .replace("{{court_gear_cards}}", academy_cards(catalog, "court-gear", "h4"))
                    .replace("{{warm_ups_cards}}", academy_cards(catalog, "warm-ups", "h4"))
                    .replace("{{accessories_cards}}", academy_cards(catalog, "accessories", "h4")))
        for k, v in ICON.items():
            body = body.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{[a-z_]*cards\}\}", body)
        if left:
            raise SystemExit(f"{p.name}: unfilled product grids {left}")
        html = head(meta) + header(meta.get("nav", "home")) + '<main id="main">\n' + body + "\n</main>" + footer(meta.get("nav", "home"))
        html = shell.apply(html, meta, p.name, SERIES_PRICE)
        (OUT / p.name).write_text(html)
        print("built", p.name, len(html))
    shell.write_index()
    shell.seo.write_site_files([(p.name, "home" if p.name == "index.html" else p.stem) for p in pages])
    shell.apply_product()
    cache_bust()


def cache_bust():
    """Tag every unversioned local CSS/JS link with a short hash of the file,
    so returning visitors never get new pages with old styles."""
    import hashlib
    pat = re.compile(r'((?:href|src)="assets/(?:css|js)/[\w.-]+\.(?:css|js))"')
    memo = {}

    def ver(m):
        rel = m.group(1).split('"', 1)[1]
        if rel not in memo:
            f = OUT / rel
            memo[rel] = hashlib.sha1(f.read_bytes()).hexdigest()[:8] if f.exists() else None
        return f'{m.group(1)}?v={memo[rel]}"' if memo[rel] else m.group(0)

    for f in OUT.glob("*.html"):
        html = f.read_text()
        new = pat.sub(ver, html)
        if new != html:
            f.write_text(new)


if __name__ == "__main__":
    build()
