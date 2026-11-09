"""Assemble site/*.html from src/*.html page bodies + shared layout.

Each src page starts with a JSON header comment:
<!--{"title": "...", "desc": "...", "nav": "story", "store": true}-->
Run: python3 tools/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "site"

NAV = [
    ("story", "story.html", "Story"),
    ("record", "record.html", "Record"),
    ("archive", "archive.html", "Archive"),
    ("keynotes", "keynotes.html", "Keynotes"),
    ("partners", "partners.html", "Partners"),
    ("store", "store.html", "Store"),
    ("playbook", "playbook.html", "Playbook"),
    ("series", "series.html", "Series"),
    ("investors", "investors.html", "Investors"),
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
<meta property="og:image" content="assets/img/keyart_cc2.jpg">
<link rel="icon" href="assets/brand/appicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Cinzel:wght@500;700&family=Cormorant+Garamond:ital,wght@1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
<link rel="stylesheet" href="assets/css/fx.css">
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
      <button class="icon-btn cart" data-cart aria-label="Open bag">{ICON['bag']}<span class="cart-count">0</span></button>
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


def footer():
    return f"""
<footer class="footer">
  <div class="bgv"><video data-auto muted loop playsinline preload="none" poster="assets/video/outro.jpg" data-src="assets/video/outro.mp4"></video></div>
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
        <li><a href="series.html">Coach Carter II</a></li><li><a href="impact.html">Foundation</a></li></ul></div>
      <div><h6>Work with Coach</h6><ul>
        <li><a href="keynotes.html#book">Book a keynote</a></li><li><a href="partners.html">Brand partnerships</a></li>
        <li><a href="partners.html#builder">Build a package</a></li><li><a href="brand.html">Press &amp; brand kit</a></li></ul></div>
      <div><h6>Store</h6><ul>
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
      <span>"Coach Carter" (2005) is a Paramount Pictures / MTV Films release. No film footage is used on this site.</span>
    </div>
  </div>
</footer>
<div class="scrim"></div>
<aside class="drawer" aria-label="Shopping bag">
  <header><h4>Your bag</h4><button class="icon-btn" data-close aria-label="Close">{ICON['x']}</button></header>
  <div class="items"></div>
  <footer><div class="total"><span>Subtotal</span><b>$0</b></div>
    <button class="btn btn-gold" style="width:100%;justify-content:center" data-checkout>Checkout {ICON['arr']}</button>
    <p class="body-mute" style="font-size:13px;margin:12px 0 0;text-align:center">Free shipping over $100 · Bulk orders for schools</p></footer>
</aside>
<div class="modal video" id="video-modal" role="dialog" aria-label="Video"><div class="box"><button class="icon-btn x" data-close aria-label="Close" style="background:rgba(0,0,0,.5)">{ICON['x']}</button><video controls playsinline preload="none"></video></div></div>
<div class="modal" id="checkout-modal" role="dialog" aria-label="Checkout"><div class="box">
  <img src="assets/brand/crest_gold.svg" alt="" width="84" height="84">
  <h3 class="h-m mt-s">The store opens soon.</h3>
  <p class="body-mute">Your bag is saved. Join the Locker Room list and you'll get first access to the opening drop and signed editions.</p>
  <form class="news" data-simple="You're on the list for the opening drop" style="max-width:none"><input type="email" required placeholder="Your email" aria-label="Email"><button type="submit">Notify me →</button></form>
  <p class="body-mute internal" style="font-size:13px">Review note: checkout connects to Shopify / Stripe at launch.</p>
  <button class="btn btn-ghost btn-sm mt-s" data-close>Keep browsing</button></div></div>
<div class="toast" role="status" aria-live="polite"><img src="assets/brand/monogram_gold.svg" alt="" width="18" height="18" style="filter:brightness(.2)"><span></span></div>
<div class="preview-flag internal">Review mode · internal notes visible</div>
<script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
<script defer src="assets/js/site.js"></script>
<script defer src="assets/js/store.js"></script>
</body>
</html>
"""


def build():
    pages = sorted(SRC.glob("*.html"))
    for p in pages:
        raw = p.read_text()
        m = re.match(r"<!--(\{.*?\})-->\s*", raw, re.S)
        meta = json.loads(m.group(1))
        body = raw[m.end():]
        for k, v in ICON.items():
            body = body.replace("{{" + k + "}}", v)
        html = head(meta) + header(meta.get("nav", "home")) + '<main id="main">\n' + body + "\n</main>" + footer()
        (OUT / p.name).write_text(html)
        print("built", p.name, len(html))


if __name__ == "__main__":
    build()
