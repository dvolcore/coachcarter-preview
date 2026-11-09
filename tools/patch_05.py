"""Patch 05: independent-review fixes (critical + major + copy)."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new, all_=False):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:80]}"
    p.write_text(s.replace(old, new) if all_ else s.replace(old, new, 1))


# ---------- C2: repair record.html ----------
rec = R / "src/record.html"
lines = rec.read_text().split("\n")
assert lines[133].startswith("</script><div"), lines[133][:40]
s = "\n".join(lines[:133]) + "\n</script>\n"
bd = '<div class="ph" style="--ar:1/1"><em>From Coach\'s archive</em><strong>The Best Damn Sports Show</strong>'
assert bd in s
s = s.replace(bd, '<div class="ph" data-y="FSN" style="--ar:1/1"><em>From Coach\'s archive</em><strong>The Best Damn Sports Show</strong>')
assert s.count('id="tilemap"') == 1 and s.count('class="page-hero"') == 1
rec.write_text(s)

CSS = "site/assets/css/site.css"
FX = "site/assets/css/fx.css"
JS = "site/assets/js/site.js"

# ---------- C1: sticky — body must not become a scroll container ----------
sub(CSS, "  text-rendering: optimizeLegibility;\n  overflow-x: hidden;\n}", "  text-rendering: optimizeLegibility;\n  overflow-x: clip;\n  color-scheme: dark;\n}")

# ---------- C3: only hide system cursor while custom cursor is live ----------
sub(FX, "@media (hover: hover) and (pointer: fine) { body, a, button { cursor: none; }",
    "@media (hover: hover) and (pointer: fine) { body.cur-on, body.cur-on a, body.cur-on button { cursor: none; }")

# ---------- C4: no wipe on same-page links ----------
sub(JS, """    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || reduce || !wipe) return;""",
    """    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || reduce || !wipe) return;
      if (a.pathname === location.pathname) return; // same page (anchor) — let it scroll""")

# ---------- M: modal backdrop click, focus management, inert, Escape on menu ----------
sub(JS, """  const scrim = $(".scrim");
  const openModal = (m) => { m.classList.add("on"); scrim.classList.add("on"); lenis && lenis.stop(); };
  const closeAll = () => {
    $$(".modal.on, .drawer.on").forEach((m) => m.classList.remove("on"));
    scrim && scrim.classList.remove("on");
    $$(".modal video").forEach((v) => v.pause());
    lenis && lenis.start();
  };""", """  const scrim = $(".scrim");
  let lastFocus = null;
  const layers = $$(".modal, .drawer, .menu");
  layers.forEach((l) => { l.inert = true; });
  const focusIn = (el) => { const f = el.querySelector("button, a[href], input, select, textarea, video[controls]"); f && setTimeout(() => f.focus({ preventScroll: true }), 60); };
  const openModal = (m) => {
    lastFocus = document.activeElement; m.inert = false; m.classList.add("on"); scrim.classList.add("on"); lenis && lenis.stop(); focusIn(m);
  };
  const closeAll = () => {
    $$(".modal.on, .drawer.on").forEach((m) => { m.classList.remove("on"); m.inert = true; });
    scrim && scrim.classList.remove("on");
    $$(".modal video").forEach((v) => v.pause());
    lenis && lenis.start();
    if (lastFocus && lastFocus.focus) { lastFocus.focus({ preventScroll: true }); lastFocus = null; }
  };
  $$(".modal").forEach((m) => m.addEventListener("click", (e) => { if (e.target === m) closeAll(); }));
  window.CC_layers = { openModal };""")
sub(JS, """  addEventListener("keydown", (e) => { if (e.key === "Escape") closeAll(); });""",
    """  addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (menu && menu.classList.contains("open")) { setMenu(false); return; }
    closeAll();
  });""")
sub(JS, """  const menu = $(".menu");
  $$("[data-menu]").forEach((b) => b.addEventListener("click", () => {
    const open = !menu.classList.contains("open");
    menu.classList.toggle("open", open);
    document.body.classList.toggle("menu-open", open);
    b.setAttribute("aria-expanded", String(open));
    if (lenis) open ? lenis.stop() : lenis.start();
  }));""", """  const menu = $(".menu");
  const menuBtn = $(".menu-btn");
  const setMenu = (open) => {
    if (!menu) return;
    menu.classList.toggle("open", open); menu.inert = !open;
    document.body.classList.toggle("menu-open", open);
    $$("[data-menu]").forEach((x) => x.setAttribute("aria-expanded", String(open)));
    if (lenis) open ? lenis.stop() : lenis.start();
    if (open) { const f = menu.querySelector("a"); f && setTimeout(() => f.focus(), 300); } else if (menuBtn) menuBtn.focus({ preventScroll: true });
  };
  $$("[data-menu]").forEach((b) => b.addEventListener("click", () => setMenu(!menu.classList.contains("open"))));""")

# drawer open from store.js needs inert lifted + focus
sub("site/assets/js/store.js", """    const open = e.target.closest("[data-cart]"); if (open) { $(".drawer").classList.add("on"); $(".scrim").classList.add("on"); }""",
    """    const open = e.target.closest("[data-cart]"); if (open) { const d = $(".drawer"); d.inert = false; d.classList.add("on"); $(".scrim").classList.add("on"); const f = d.querySelector("button"); f && setTimeout(() => f.focus(), 80); }""")

# ---------- M: wizard Enter key advances one step ----------
sub(JS, """    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data""", """    form.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" || e.target.tagName === "TEXTAREA" || e.target.tagName === "BUTTON") return;
      const nx = steps[i] && steps[i].querySelector("[data-next]");
      if (nx) { e.preventDefault(); nx.click(); }
    });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data""")

# ---------- M: performance — mobile hero encode, lazy scrub ----------
sub(JS, """  $$("video[data-auto]").forEach((v) => { v.muted = true; v.playsInline = true; vio.observe(v); });""",
    """  $$("video[data-auto]").forEach((v) => {
    v.muted = true; v.playsInline = true;
    if (v.dataset.mobile && innerWidth < 760) { v.src = v.dataset.mobile; }
    vio.observe(v);
  });""")
sub(JS, """    v.muted = true; v.preload = "auto";
    let target = 0, ready = false;
    v.addEventListener("loadedmetadata", () => { ready = true; });
    v.load();""", """    v.muted = true;
    let target = 0, ready = false;
    v.addEventListener("loadedmetadata", () => { ready = true; });
    new IntersectionObserver(([en], ob) => { if (!en.isIntersecting) return; ob.disconnect(); v.src = v.dataset.src; v.preload = "auto"; v.load(); }, { rootMargin: "150% 0px" }).observe(sec);""")
sub("src/index.html", '<video muted playsinline preload="auto" poster="assets/video/scrub_shot.jpg" src="assets/video/scrub_shot.mp4"></video>',
    '<video muted playsinline preload="none" poster="assets/video/scrub_shot.jpg" data-src="assets/video/scrub_shot.mp4"></video>')
sub("src/index.html", '<video data-auto muted loop playsinline preload="auto" poster="assets/video/hero_reel.jpg" src="assets/video/hero_reel.mp4"></video>',
    '<video data-auto muted loop playsinline preload="metadata" poster="assets/video/hero_reel.jpg" src="assets/video/hero_reel.mp4" data-mobile="assets/video/hero_reel_m.mp4"></video>')

# ---------- M: reduced motion on zoom ----------
sub(JS, """    aim(); addEventListener("resize", aim); document.fonts && document.fonts.ready.then(aim);
    scrollers.push(() => {""", """    aim(); addEventListener("resize", aim); document.fonts && document.fonts.ready.then(aim);
    if (reduce) { mask.style.display = "none"; if (after) after.style.opacity = "1"; return; }
    scrollers.push(() => {""")

# ---------- M: intro must not depend on JS/CDN ----------
sub(CSS, ".curtain.up { clip-path: inset(0 0 100% 0); }",
    ".curtain.up { clip-path: inset(0 0 100% 0); }\n.curtain { animation: curtainSafety .01s linear 3.5s forwards; }\n@keyframes curtainSafety { to { clip-path: inset(0 0 100% 0); visibility: hidden; } }\nhtml:not(.js) .curtain { display: none; }")
for sel_old, sel_new in [
    ("[data-reveal] { opacity: 0;", ".js [data-reveal] { opacity: 0;"),
    (".reveal-mask { clip-path: inset(0 100% 0 0); }", ".js .reveal-mask { clip-path: inset(0 100% 0 0); }"),
    (".fade-up { opacity: 0; transform: translateY(26px); }", ".js .fade-up { opacity: 0; transform: translateY(26px); }"),
    (".split-line > span { display: block; transform: translateY(105%);", ".split-line > span { display: block; }\n.js .split-line > span { transform: translateY(105%);"),
]:
    sub(CSS, sel_old, sel_new)
sub(FX, "[data-words] .w > span { display: inline-block; transform:", "[data-words] .w > span { display: inline-block; }\n.js [data-words] .w > span { transform:")
sub("tools/build.py", '<meta name="theme-color" content="#08090B">', '<meta name="theme-color" content="#08090B">\n<script>document.documentElement.classList.add("js")</script>')
sub("tools/build.py", '<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>\n<script src="assets/js/site.js"></script>\n<script src="assets/js/store.js"></script>',
    '<script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>\n<script defer src="assets/js/site.js"></script>\n<script defer src="assets/js/store.js"></script>')

# ---------- M: contrast ----------
sub(CSS, "  --mute: #6E727B;", "  --mute: #8F939C;")
sub(FX, ".light .secnum { color: #9a9ca2; }", ".light .secnum { color: #66696F; }")
sub(CSS, ".sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }",
    ".sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }\n.sr:focus { position: fixed; top: 12px; left: 12px; z-index: 400; width: auto; height: auto; clip: auto; padding: 12px 18px; background: var(--chalk); color: var(--ink); border-radius: 999px; font-weight: 600; }")
sub(CSS, ".light { background: var(--chalk); color: var(--carbon); }", ".light { background: var(--chalk); color: var(--carbon); color-scheme: light; }")

# ---------- M: store mobile + series mobile ----------
sub(FX, "/* sent state */", """@media (max-width: 760px) {
  .team-books .book3d:not(.mid) { display: none; }
  .page-series .hero-media video, .page-series .hero-media img { object-fit: contain; background: #000; }
  .page-series .hero-media { background: #000; }
  .hero-kicker .eyebrow { letter-spacing: .2em; font-size: 11px; }
  .hero-kicker .eyebrow::before, .hero-kicker .eyebrow::after { width: 18px; }
}
/* sent state */""")
sub("src/store.html", '<div class="book-stage" style="gap:0;display:flex;justify-content:center">', '<div class="book-stage team-books" style="gap:0;display:flex;justify-content:center;min-width:0">')
sub("src/store.html", '<div class="book3d" style="--w:230px;z-index:2">', '<div class="book3d mid" style="--w:230px;z-index:2">')

# ---------- store: ?cat chip, film card w/o studio branding, copy ----------
SJ = "site/assets/js/store.js"
sub(SJ, """    draw(new URLSearchParams(location.search).get("cat") || "all");""",
    """    const start = new URLSearchParams(location.search).get("cat") || "all";
    $$(".filters .chip").forEach((x) => x.classList.toggle("on", x.dataset.cat === start));
    draw(start);""")
sub(SJ, """      <div class="ct-top">Paramount Pictures · 2005</div>
      <div><div class="ct-title" style="font-size:30px">COACH<br>CARTER</div><div class="ct-sub" style="font-size:13px">The film inspired by his true story</div></div>
      <div class="ct-author" style="font-size:11px">Blu-ray · DVD · Digital</div>""",
    """      <div class="ct-top">The 2005 film</div>
      <div><div class="ct-title" style="font-size:22px;letter-spacing:.08em">INSPIRED BY<br>HIS TRUE STORY</div></div>
      <div class="ct-author" style="font-size:11px">Blu-ray · DVD · Digital</div>""")
sub(SJ, 'kind: "Hardcover · Business Plus / Hachette, 2012", price: 27, badge: "Bestseller"', 'kind: "Hardcover · Business Plus / Hachette, 2012", price: 27, badge: "Hardcover"')
sub(SJ, 'kind: "Hardcover, signed & numbered by Coach"', 'kind: "Hardcover, signed by Coach"')
sub(SJ, 'kind: "The Paramount film · Blu-ray / DVD / Digital"', 'kind: "The 2005 film · Blu-ray / DVD / Digital"')
sub(SJ, 'kind: "Museum print · signed · 18×24"', 'kind: "Archival print · signed · 18×24"')
# richer cart thumbnails
sub(SJ, """<div class="li-thumb">${p.cat === "books" ? `<img src="assets/brand/appicon.svg" alt="">` : `<img src="assets/brand/monogram_gold.svg" alt="" style="width:70%;height:auto">`}</div>""",
    """<div class="li-thumb">${p.art()}</div>""")
sub(CSS, ".line-item .li-thumb img { width: 100%; height: 100%; object-fit: cover; }",
    ".line-item .li-thumb img { width: 100%; height: 100%; object-fit: cover; }\n.line-item .li-thumb .book3d { --w: 40px !important; --d: 6px; transform: rotateY(-20deg); }\n.line-item .li-thumb .book3d .cover > * { display: none; }\n.line-item .li-thumb .tee svg { width: 100%; }\n.line-item .li-thumb .cover.c2 { width: 46px !important; }")
sub("src/store.html", "<p class=\"body-mute\">Every signed item is hand-signed and numbered, with a certificate.</p>", "<p class=\"body-mute\">Signed editions are signed by Coach Ken Carter himself.</p>")

# ---------- copy accuracy ----------
IX = "src/index.html"
sub(IX, "will never go out of style.”", "will never ever go out of style.”")
sub(IX, "Two decades of keynotes across the country, a bestselling book, and a new series", "Two decades of keynotes across the country, a book from Hachette, and a new series")
sub(IX, "A number-one film, twenty years of cable and streaming replays, and a name that still means “the coach who put school first.”",
    "A number-one film that keeps finding new audiences, and a name that still means “the coach who put school first.”")
sub(IX, "Partners borrow a track record that is documented in the New York Times, not a slogan written for the campaign.",
    "Partners borrow a track record documented by the New York Times and the Los Angeles Times — not a slogan written for the campaign.")
sub(IX, "It is the leadership trait every company says it wants and few can teach. Coach Carter is the most recognisable face of it in American culture.",
    "It is the leadership trait every company says it wants and few can teach. When people tell the story of accountability, they tell his.")
sub(IX, "Parents saw it in theatres.", "Parents saw it in theaters.")
sub(IX, "<p>The New York Times, the Los Angeles Times, NPR, CNN, Today and Good Morning America came to Richmond. Some called it a stunt. The governor called him a hero.</p>",
    "<p>NPR, CNN, the New York Times and the Los Angeles Times carried the story nationwide. Some called it a stunt. Governor Gray Davis called him a hero.</p>")
sub(IX, "Every one of those fifteen players went on to higher education.", "Two years later, the Los Angeles Times reported, all fifteen who had fallen short were in higher education.")
sub(IX, '<div class="l">Benched players who went<br>on to higher education</div>', '<div class="l">Who missed the contract, then<br>went to college · LA Times 2001</div>')
sub(IX, "<span class=\"hint\">Sign here ✍</span>", "<span class=\"hint\">Sign here</span>")
sub(IX, "Universities, Fortune-500 summits", "Universities, business summits") if "Fortune-500" in (R / IX).read_text() else None

ST = "src/story.html"
sub(ST, "<span class=\"hint\">Sign here ✍</span>", "<span class=\"hint\">Sign here</span>")
sub(ST, "Universities, Fortune-500 summits, school districts", "Universities, business summits, school districts")
sub(ST, "NPR, CNN, the New York Times and the Los Angeles Times cover it; Today and Good Morning America follow.",
    "NPR, CNN, the New York Times and the Los Angeles Times cover it.")
sub(ST, "California's governor called him a hero.", "Governor Gray Davis called him a hero.")

RC = "src/record.html"
sub(RC, "keynotes in 20+ states", "keynotes in 19 states")
sub(RC, "Every line below is documented.", "Linked to the outlets that ran it. Items still coming from Coach's archive are marked.")
sub(RC, '<div class="r"><span class="yr">1999</span><span class="show">Today · Good Morning America</span><span class="what">Network morning-show appearances as the story went national.</span>',
    '<div class="r"><span class="yr">1999</span><span class="show">Today · Good Morning America</span><span class="what">Network morning-show appearances as the story went national, as reported by the East Bay Express. <em style="color:var(--gold)">Clips from Coach\'s archive — to be added.</em></span>')
sub(RC, '<span class="what">Fox Sports Net studio appearance. <em style="color:var(--gold)">Clip and date from Coach\'s archive — to be added.</em></span>',
    '<span class="what">Fox Sports Net studio appearance. <em style="color:var(--gold)">Archive pending — clip and date from Coach.</em></span>')
sub(RC, '<span data-count="20">0</span></div><div class="l">States — plus<br>Canada', '<span data-count="19">0</span></div><div class="l">States — plus<br>Canada')
sub(RC, '<span data-count="5">0</span></div><div class="l">Statewide &amp; national<br>honors', '<span data-count="6">0</span></div><div class="l">Honors &amp;<br>distinctions')
sub(RC, '<span data-count="140">0</span></div><div class="l">Editorial photos in the<br>Getty Images archive', '<span data-count="100">0</span>+</div><div class="l">Editorial photos in the<br>Getty Images archive')
sub(RC, "Universities, Fortune-500 summits, trade conventions, school districts, churches and youth organisations.", "Universities, business summits, trade conventions, school districts, churches and youth organizations.")
sub(RC, "Recognised for excellence in secondary education.", "Recognized for excellence in secondary education.")
sub(RC, "if (lit[s]) { d.dataset.tip = lit[s]; d.dataset.lit = \"1\"; }", "if (lit[s]) { d.dataset.tip = lit[s]; d.dataset.lit = \"1\"; d.tabIndex = 0; d.setAttribute(\"aria-label\", s + \": \" + lit[s]); }")
sub(FX, "/* sent state */", ".tilemap .t[data-tip]:focus::after { content: attr(data-tip); position: absolute; bottom: 115%; left: 50%; transform: translateX(-50%); white-space: nowrap; background: var(--chalk); color: var(--ink); padding: 8px 10px; border-radius: 8px; font: 500 12px/1.2 var(--f-body); z-index: 5; }\n/* sent state */")

PT = "src/partners.html"
sub(PT, '<span class="tag">Most requested</span>', '<span class="tag">Signature</span>')
sub(PT, '<span data-count="20">0</span></div><div class="l">States reached on<br>the keynote circuit', '<span data-count="19">0</span></div><div class="l">States reached on<br>the keynote circuit')

BR = "src/brand.html"
sub(BR, "Every one of the fifteen players he benched went on to higher education.",
    "Two years later, the Los Angeles Times reported that all fifteen players who had fallen short of the contract were in higher education.")
sub(BR, "Headlines · the scoreboard voice. Stand-in for DIN Condensed.", "Headlines · the scoreboard voice.")
sub(BR, '<div class="portrait mt-m" style="max-width:340px"><img class="p" src="assets/img/portrait_sheet.jpg" alt="Coach Ken Carter headshot" loading="lazy"></div>',
    '<div class="portrait mt-m" style="max-width:340px"><img class="p" src="assets/img/portrait_sheet.jpg" alt="Coach Ken Carter — Coach Carter II series portrait" loading="lazy"></div><p class="cap">Series portrait · official press headshot from Coach to replace before launch</p>')
sub("src/impact.html", "so the next fifteen players don't need a padlock to find their way.", "so the next generation doesn't need a padlock to find its way.")
sub("src/impact.html", "because fifteen of fifteen is the target, not the exception.", "because every player in college is the target, not the exception.")
sub(IX, 'alt="Coach Ken Carter in a navy pinstripe suit and gold tie"', 'alt="Coach Ken Carter in a navy pinstripe suit and gold tie — Coach Carter II series portrait"')
sub("src/keynotes.html", 'alt="Coach Carter at a press-conference podium"', 'alt="Coach Carter at a press-conference podium — scene from Coach Carter II"')
sub("tools/build.py", "Free shipping on orders over $100 · Bulk orders for schools", "Free shipping over $100 · Bulk orders for schools")
sub("tools/build.py", "At launch, checkout runs on Shopify / Stripe with signed-copy fulfilment", "At launch, checkout runs on Shopify / Stripe with signed-copy fulfillment")
print("patch_05 ok")
