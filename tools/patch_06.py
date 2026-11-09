"""Patch 06: real proof (Getty embeds), Playbook + brand architecture, film poster,
timeline additions, client-clean mode (?review shows internal notes)."""
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:80]}"
    p.write_text(s.replace(old, new, 1))


def between(path, start, end, new):
    p = R / path
    s = p.read_text()
    i, j = s.index(start), s.index(end)
    p.write_text(s[:i] + new + s[j:])


def getty(gid, cap=True):
    return f'<figure class="gx" data-reveal><div class="gframe" data-getty="{gid}"></div>{"<figcaption></figcaption>" if cap else ""}</figure>'


# ---------------- build.py: nav, review mode, internal flags ----------------
B = "tools/build.py"
sub(B, '    ("series", "series.html", "Coach Carter II"),\n    ("impact", "impact.html", "Impact"),',
    '    ("playbook", "playbook.html", "Playbook"),\n    ("series", "series.html", "Series"),\n    ("impact", "impact.html", "Impact"),')
sub(B, '<script>document.documentElement.classList.add("js")</script>',
    '<script>(function(d){d.classList.add("js");try{var q=location.search;if(/[?&]review\\b/.test(q))localStorage.setItem("cc_review","1");if(/[?&]client\\b/.test(q))localStorage.removeItem("cc_review");if(localStorage.getItem("cc_review"))d.classList.add("review")}catch(e){}})(document.documentElement)</script>')
sub(B, '<div class="preview-flag">Preview · for approval</div>', '<div class="preview-flag internal">Review mode · internal notes visible</div>')
sub(B, '  <small>Preview build · not public</small>', '  <small class="internal">Review mode</small>')
sub(B, "<h3 class=\"h-m mt-s\">Checkout opens at launch.</h3>\n  <p class=\"body-mute\">This is the approval preview. Your bag is saved on this device. At launch, checkout runs on Shopify / Stripe with signed-copy fulfillment and bulk invoicing for schools and companies.</p>\n  <button class=\"btn btn-gold mt-s\" data-close>Keep browsing</button>",
    "<h3 class=\"h-m mt-s\">The store opens soon.</h3>\n  <p class=\"body-mute\">Your bag is saved. Join the Locker Room list and you'll get first access to the opening drop and signed editions.</p>\n  <form class=\"news\" data-simple=\"You're on the list for the opening drop\" style=\"max-width:none\"><input type=\"email\" required placeholder=\"Your email\" aria-label=\"Email\"><button type=\"submit\">Notify me →</button></form>\n  <p class=\"body-mute internal\" style=\"font-size:13px\">Review note: checkout connects to Shopify / Stripe at launch.</p>\n  <button class=\"btn btn-ghost btn-sm mt-s\" data-close>Keep browsing</button>")

# ---------------- CSS ----------------
CSS = R / "site/assets/css/fx.css"
CSS.write_text(CSS.read_text() + """
/* ---------- client vs review mode ---------- */
.internal { display: none !important; }
.review .internal { display: revert !important; }
.review .internal.preview-flag { display: block !important; }

/* ---------- Getty embeds ---------- */
.gx { margin: 0; break-inside: avoid; }
.gframe { position: relative; width: 100%; border-radius: 14px; overflow: hidden; background: #0d0e11; border: 1px solid var(--line); }
.gframe iframe { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; }
.gframe::before { content: ""; position: absolute; inset: 0; background: linear-gradient(110deg, transparent 30%, rgba(233,207,149,.07) 50%, transparent 70%) 0 0 / 250% 100%; animation: shimmer 1.6s linear infinite; }
.gframe.ready::before { display: none; }
@keyframes shimmer { to { background-position: -250% 0; } }
.gx figcaption { margin-top: 12px; }
.gx figcaption b { display: block; font: 600 19px/1.15 var(--f-head); text-transform: uppercase; letter-spacing: .02em; }
.gx figcaption span { display: block; margin-top: 4px; font: 500 12px/1.4 var(--f-head); letter-spacing: .16em; text-transform: uppercase; color: var(--slate); }
.gwall { columns: 3 300px; column-gap: 20px; }
.gwall .gx { margin-bottom: 26px; }
.ggroup { margin-top: clamp(56px, 7vw, 96px); }
.ggroup:first-of-type { margin-top: 0; }
.ggroup > header { display: flex; align-items: baseline; gap: 18px; justify-content: space-between; border-top: 1px solid var(--line); padding-top: 18px; margin-bottom: 26px; flex-wrap: wrap; }
.ggroup > header h3 { margin: 0; font: 600 clamp(28px, 3vw, 44px)/1 var(--f-head); text-transform: uppercase; }
.ggroup > header span { font: 600 12px/1 var(--f-head); letter-spacing: .28em; text-transform: uppercase; color: var(--gold); }
.credit { font-size: 12.5px; color: var(--mute); }

/* home "In the room" rail */
.room-rail { display: grid; grid-auto-flow: column; grid-auto-columns: clamp(270px, 30vw, 420px); gap: 20px; overflow-x: auto; scroll-snap-type: x mandatory; padding: 4px var(--gutter) 22px; scrollbar-width: thin; scrollbar-color: var(--gold-lo) transparent; }
.room-rail > * { scroll-snap-align: start; }
.room-card { display: flex; flex-direction: column; justify-content: flex-end; min-height: 100%; border-radius: 14px; padding: 26px; background: radial-gradient(120% 90% at 100% 0%, rgba(84,29,48,.8), transparent 60%), var(--carbon-2); border: 1px solid rgba(187,149,88,.35); }
.room-card strong { font: 600 30px/1 var(--f-head); text-transform: uppercase; }
.room-card p { color: var(--slate); margin: 10px 0 0; font-size: 15px; }

/* film one-sheet */
.onesheet { display: grid; grid-template-columns: auto 1fr; gap: clamp(28px, 5vw, 70px); align-items: center; }
.onesheet .frame { width: clamp(180px, 22vw, 253px); padding: 12px; background: #050506; border: 1px solid #2a2a2e; box-shadow: 0 40px 80px -30px #000, inset 0 0 0 1px rgba(233,207,149,.25); transform: rotate(-2deg); }
.onesheet .frame img { width: 100%; height: auto; }
@media (max-width: 640px) { .onesheet { grid-template-columns: 1fr; } }

/* countdowns */
.countdowns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.cd { padding: clamp(24px, 3vw, 40px); border-radius: 22px; border: 1px solid rgba(187,149,88,.35); background: linear-gradient(180deg, rgba(84,29,48,.45), rgba(22,24,29,.9)); }
.cd-n { display: flex; align-items: baseline; gap: 8px 12px; margin: 18px 0 10px; flex-wrap: wrap; }
.cd-n b { font: 700 clamp(48px, 6vw, 88px)/.9 var(--f-head); background: var(--gold-grad); -webkit-background-clip: text; background-clip: text; color: transparent; font-variant-numeric: tabular-nums; }
.cd-n i { font: 600 13px/1 var(--f-head); letter-spacing: .24em; text-transform: uppercase; color: var(--slate); font-style: normal; margin-right: 10px; }
.cd p { margin: 0; color: rgba(245,240,232,.75); }
@media (max-width: 760px) { .countdowns { grid-template-columns: 1fr; } }

/* plays */
.plays { display: grid; gap: 16px; }
.play { position: relative; display: grid; grid-template-columns: 90px 1.3fr 1fr auto; gap: 28px; align-items: center; padding: 30px; border-radius: 20px; background: var(--carbon-2); border: 1px solid var(--line); transition: border-color .4s, transform .6s var(--ease); }
.play:hover { border-color: rgba(187,149,88,.5); transform: translateY(-3px); }
.play.feature { background: linear-gradient(120deg, rgba(84,29,48,.7), var(--carbon-2) 60%); border-color: rgba(187,149,88,.55); }
.p-no { font: 700 64px/.8 var(--f-head); color: transparent; -webkit-text-stroke: 1px rgba(233,207,149,.55); }
.play h3 { margin: 12px 0 8px; font: 600 clamp(28px, 2.6vw, 38px)/1 var(--f-head); text-transform: uppercase; }
.play .p-main p { margin: 0; color: rgba(245,240,232,.75); }
.p-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.p-list li { display: flex; gap: 10px; font-size: 14.5px; color: rgba(245,240,232,.82); }
.p-list li::before { content: ""; flex: 0 0 6px; height: 6px; margin-top: 8px; background: var(--gold); transform: rotate(45deg); }
@media (max-width: 1080px) { .play { grid-template-columns: 70px 1fr; } .play .p-list, .play > .btn { grid-column: 2; } .play > .btn { justify-self: start; } }
@media (max-width: 560px) { .play { grid-template-columns: 1fr; } .play .p-list, .play > .btn { grid-column: 1; } }

/* brand architecture */
.arch { display: grid; gap: 34px; justify-items: center; }
.arch-root { display: grid; justify-items: center; gap: 8px; text-align: center; position: relative; }
.arch-root b { font: 700 clamp(30px, 3vw, 44px)/1 var(--f-brand); letter-spacing: .06em; text-transform: uppercase; color: var(--maroon); }
.arch-root small { font: 600 12px/1 var(--f-head); letter-spacing: .26em; text-transform: uppercase; color: #6b6e75; }
.arch-root::after { content: ""; position: absolute; left: 50%; bottom: -34px; width: 1px; height: 34px; background: rgba(84,29,48,.4); }
.arch-branches { width: 100%; display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: rgba(16,18,22,.12); border: 1px solid rgba(16,18,22,.12); border-radius: 18px; overflow: hidden; }
.arch-branches > div { background: #fff; padding: 24px; display: grid; gap: 6px; }
.arch-branches span { font: 600 11px/1 var(--f-head); letter-spacing: .26em; text-transform: uppercase; color: var(--gold-lo); }
.arch-branches b { font: 600 24px/1.05 var(--f-head); text-transform: uppercase; }
.arch-branches small { color: #5b5f68; font-size: 14px; }
@media (max-width: 900px) { .arch-branches { grid-template-columns: 1fr 1fr; } }
""")

# ---------------- JS: Getty loader + countdowns ----------------
JS = R / "site/assets/js/site.js"
s = JS.read_text()
anchor = '  /* ---------------- year in footer ---------------- */'
assert anchor in s
s = s.replace(anchor, r'''  /* ---------------- Getty editorial embeds (official embed player, lazy) ---------------- */
  const gSlots = $$("[data-getty]");
  if (gSlots.length) {
    const base = document.querySelector('script[src*="site.js"]').src.replace(/assets\/js\/site\.js.*$/, "");
    fetch(base + "assets/data/getty.json").then((r) => r.json()).then((list) => {
      const byId = Object.fromEntries(list.map((g) => [g.id, g]));
      const gio = new IntersectionObserver((ents) => ents.forEach((en) => {
        if (!en.isIntersecting) return; gio.unobserve(en.target);
        const el = en.target; const g = byId[el.dataset.getty]; if (!g) return;
        const f = document.createElement("iframe");
        f.src = `https://embed.gettyimages.com/embed/${g.id}?et=${encodeURIComponent(g.et)}&tld=com&sig=${encodeURIComponent(g.sig)}&caption=false&ver=1`;
        f.title = `${g.title} — Getty Images`; f.loading = "lazy"; f.scrolling = "no"; f.setAttribute("frameborder", "0");
        f.addEventListener("load", () => el.classList.add("ready"));
        el.appendChild(f);
      }), { rootMargin: "400px 0px" });
      gSlots.forEach((el) => {
        const g = byId[el.dataset.getty]; if (!g) { el.closest(".gx") && el.closest(".gx").remove(); return; }
        el.style.aspectRatio = `${g.w} / ${g.h + 34}`;
        const cap = el.parentElement.querySelector("figcaption");
        if (cap && !cap.textContent.trim()) cap.innerHTML = `<b>${g.title}</b><span>${g.where}</span>`;
        gio.observe(el);
      });
    }).catch(() => {});
  }

  /* ---------------- countdowns ---------------- */
  $$("[data-countdown]").forEach((el) => {
    const t = new Date(el.dataset.countdown).getTime();
    const tick = () => {
      const d = Math.max(0, t - Date.now());
      const v = { d: Math.floor(d / 864e5), h: Math.floor(d / 36e5) % 24, m: Math.floor(d / 6e4) % 60 };
      $$("[data-u]", el).forEach((b) => { b.textContent = String(v[b.dataset.u]).padStart(b.dataset.u === "d" ? 1 : 2, "0"); });
    };
    tick(); setInterval(tick, 30000);
  });

''' + anchor)
JS.write_text(s)

# ---------------- HOME: in the room rail + kicker ----------------
IX = "src/index.html"
sub(IX, '<span class="eyebrow center">Educator · Author · Speaker · Coach</span>', '<span class="eyebrow center">The real Coach Carter · Accountability, on the record</span>')
rail = "".join(getty(g) for g in ["51962763", "110239085", "51962765", "51962463", "117809386", "490354626", "1561588922", "51962473"])
sub(IX, "<!-- PINNED STORY -->", f'''<!-- IN THE ROOM -->
<section class="section carbon" style="padding-bottom:clamp(60px,8vw,110px)">
  <span class="secnum">02 — In the room</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Hollywood · Television · Hall of Famers · Arenas</span><h2 class="h-l mt-s">The company<br>he keeps.</h2></div>
      <a class="btn btn-ghost" href="record.html#room">See the full record {{{{arr}}}}</a></div>
  </div>
  <div class="room-rail">{rail}<a class="room-card" href="record.html#room"><span class="eyebrow">And more</span><strong>Courtside with Prince. Olympic torch. Dr. Phil.</strong><p>The full record of a life in the room — premieres, stages, studios and sidelines.</p></a></div>
  <div class="wrap"><p class="credit">Editorial photos via Getty Images embed.</p></div>
</section>

<!-- PINNED STORY -->''')
for a, b in [("01 — The Man", "01 — The Man"), ("02 — The Code", "03 — The Code"), ("03 — Why Coach Carter", "04 — Why Coach Carter"),
             ("04 — The Book", "05 — The Book"), ("05 — Now in development", "06 — Now in development"), ("06 — Sign it", "07 — Sign it")]:
    if a != b:
        sub(IX, a, b)

# ---------------- RECORD: real wall ----------------
RC = "src/record.html"
groups = [
    ("Hollywood premiere", "Grauman's Chinese Theatre · January 13, 2005", ["51962763", "51962765", "51962845", "51962893", "51962885"]),
    ("Dr. Phil", "With Samuel L. Jackson · January 2005", ["110239085", "110239084"]),
    ("Hall of Famers", "Premiere celebration · The Highland", ["51962463", "51962473"]),
    ("Palm Springs International Film Festival", "Opening-night film · January 2005", ["117809386", "117809466", "118037718", "117806665"]),
    ("On the courts", "Celebrity &amp; benefit games", ["115144906", "104862816"]),
    ("On stage", "Life Is Beautiful Festival · Las Vegas · 2015", ["490354626", "490356552"]),
    ("SlamBall", "Head coach, the Rumble · Las Vegas · 2023", ["1561588922", "1556033357"]),
]
wall = ""
for title, sub_, ids in groups:
    wall += f'<div class="ggroup"><header><h3>{title}</h3><span>{sub_}</span></header><div class="gwall">' + "".join(getty(i) for i in ids) + "</div></div>\n"
new_room = f'''<!-- IN THE ROOM -->
<section class="section carbon" id="room">
  <span class="secnum">02 — In the room</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Red carpets · Studios · Sidelines</span><h2 class="h-l mt-s">The company<br>he keeps.</h2></div>
      <a class="btn btn-ghost" href="https://www.gettyimages.com/search/2/image?phrase=coach%20ken%20carter" target="_blank" rel="noopener">All 140 photos at Getty {{{{out}}}}</a></div>
    <div class="ggroup"><header><h3>From Coach's own collection</h3><span>Coachcarter.com archive</span></header>
      <div class="gwall">
        <figure class="gx" data-reveal><div class="media-frame"><img src="assets/img/real_onset_slj.jpg" alt="Coach Ken Carter with Samuel L. Jackson on the set of Coach Carter" loading="lazy"></div><figcaption><b>On set with Samuel L. Jackson</b><span>Coach Carter · 2004</span></figcaption></figure>
        <figure class="gx" data-reveal><div class="media-frame"><img src="assets/img/real_gym_discipline.jpg" alt="Coach Carter leading a packed school assembly" loading="lazy"></div><figcaption><b>Holding the standard</b><span>School assembly</span></figcaption></figure>
        <figure class="gx" data-reveal><div class="room-card" style="min-height:260px"><span class="eyebrow">Courtside</span><strong>Front row with Prince</strong><p>From Coach's personal collection.</p></div><figcaption class="internal"><b>Photo needed</b><span>Ask Coach for the original</span></figcaption></figure>
        <figure class="gx" data-reveal><div class="room-card" style="min-height:260px"><span class="eyebrow">2002 · Salt Lake City Winter Games</span><strong>Olympic torchbearer</strong><p>He carried the flame for Richmond and the Bay Area — the moment he calls the greatest of his life.</p></div><figcaption class="internal"><b>Photo needed</b><span>Torch-run photo from Coach</span></figcaption></figure>
      </div>
    </div>
    {wall}
    <div class="ggroup"><header><h3>Back home</h3><span>Richmond High School · December 2024</span></header>
      <div class="room-card" style="min-height:0"><strong>Back on the Richmond bench.</strong><p>More than twenty years after the lockout, Coach returned to lead Richmond High. Photos of his first game back are in the Getty archive.</p><p><a class="link-u" href="https://www.gettyimages.com/search/2/image?phrase=richmond%20high%20school%20coach%20ken%20carter" target="_blank" rel="noopener">View the December 2024 photos ↗</a></p></div>
    </div>
    <p class="credit mt-m">Editorial photographs embedded from Getty Images; © their photographers. Collection photos © Coach Ken Carter.</p>
    <p class="body-mute mt-s internal" style="font-size:14px">Review note: Getty embeds are free for editorial display; any ad or paid campaign use needs a Getty licence and the celebrity's consent. Prince, Olympic torch, Today/GMA and Best Damn Sports Show photos/clips must come from Coach.</p>
  </div>
</section>

'''
between(RC, "<!-- IN THE ROOM -->", "<!-- MAP -->", new_room)
sub(RC, '<span class="what">Fox Sports Net studio appearance. <em style="color:var(--gold)">Archive pending — clip and date from Coach.</em></span>',
    '<span class="what">Fox Sports Net studio appearance. <em class="internal" style="color:var(--gold)">Archive pending — clip and date from Coach.</em></span>')
sub(RC, '<em style="color:var(--gold)">Clips from Coach\'s archive — to be added.</em>', '<em class="internal" style="color:var(--gold)">Clips from Coach\'s archive — to be added.</em>')
sub(RC, 'Items still coming from Coach\'s archive are marked.', 'Photographs courtesy of Getty Images and Coach\'s own collection.')
sub(RC, '<span data-count="100">0</span>+</div><div class="l">Editorial photos in the<br>Getty Images archive', '<span data-count="140">0</span></div><div class="l">Editorial photos in the<br>Getty Images archive')
sub(RC, '<div class="r"><span class="yr">2005</span><span class="show">Dr. Phil</span><span class="what">The “Coach Carter” episode, alongside Samuel L. Jackson, on putting education first.</span><span class="go">{{out}}</span></div>',
    '<a href="https://www.gettyimages.com/detail/110239085" target="_blank" rel="noopener"><span class="yr">2005</span><span class="show">Dr. Phil</span><span class="what">On the show with Samuel L. Jackson, January 2005 — putting education first.</span><span class="go">{{out}}</span></a>')

# ---------------- STORY: timeline additions + film one-sheet ----------------
ST = "src/story.html"
sub(ST, '<div class="tl-item" data-reveal><div class="y">1959</div><div><h4>Born. Raised in Richmond.</h4>', '<div class="tl-item" data-reveal><div class="y">1959</div><div><h4>Born February 13. Raised in Richmond.</h4>')
sub(ST, '<p>Carries the Olympic flame for Richmond and the Bay Area on the road to the Salt Lake City Winter Games.</p></div></div>',
    '<p>Carries the Olympic flame for Richmond and the Bay Area on the road to the Salt Lake City Winter Games — the moment he has called the greatest of his life. The same year he becomes head coach of the Los Angeles Rumble in SlamBall.</p></div></div>')
sub(ST, '<div class="tl-item" data-reveal><div class="y">Today</div>',
    '''<div class="tl-item" data-reveal><div class="y">2023</div><div><h4>Back to SlamBall</h4><p>Head coach of the Rumble as SlamBall returns in Las Vegas.</p></div></div>
      <div class="tl-item" data-reveal><div class="y">2024</div><div><h4>Home to Richmond</h4><p>More than twenty years after the lockout, Coach returns to lead Richmond High School's basketball program.</p></div></div>
      <div class="tl-item" data-reveal><div class="y">Today</div>''')
sub(ST, "<!-- QUOTE -->", '''<!-- THE FILM -->
<section class="section carbon">
  <div class="wrap onesheet">
    <div class="frame" data-reveal="scale"><img src="assets/img/film_poster_2005.jpg" alt="Theatrical poster for the 2005 film Coach Carter" loading="lazy" width="253" height="394"></div>
    <div>
      <span class="eyebrow">The film · January 14, 2005</span>
      <h2 class="h-l mt-s">His story.<br><span class="gold-text">America's #1 film.</span></h2>
      <p class="lede mt-m">Paramount Pictures and MTV Films brought the lockout to theaters with Samuel L. Jackson as Coach Carter. It opened at number one with $24.2 million, earned $76.7 million worldwide, and opened the Palm Springs International Film Festival. Coach and his son Damien served as executive consultants.</p>
      <div class="flex mt-m"><a class="btn btn-ghost" href="record.html#room">Premiere night photos {{arr}}</a><a class="btn btn-ghost" href="store.html?cat=film">Own the film</a></div>
      <p class="credit mt-s">Poster © Paramount Pictures.</p>
    </div>
  </div>
</section>

<!-- QUOTE -->''')

# ---------------- copy from brand review ----------------
sub("src/keynotes.html", '<h1 class="h-xl"><span class="split-line"><span>The talk that</span></span><span class="split-line"><span class="gold-text">changes the room.</span></span></h1>',
    '<h1 class="h-xl"><span class="split-line"><span>Your team is 13–0.</span></span><span class="split-line"><span class="gold-text">Is it keeping its contract?</span></span></h1>')
sub("src/keynotes.html", "<p class=\"lede\">No slides about synergy. A coach who padlocked a 13–0 team's gym, telling your people exactly what accountability costs — and what it pays.</p>",
    "<p class=\"lede\">The coach who padlocked an undefeated team's gym tells your people what accountability costs, what it pays — and hands your managers a contract they can run on Monday.</p>")
sub("src/partners.html", '<h1 class="h-xl"><span class="split-line"><span>Accountability</span></span><span class="split-line"><span class="gold-text">is a brand.</span></span></h1>',
    '<h1 class="h-xl"><span class="split-line"><span>Your brand,</span></span><span class="split-line"><span class="gold-text">held to his standard.</span></span></h1>')
sub("src/partners.html", '<h2 class="h-l mt-s">Let\'s talk<br><span class="gold-text">about winning.</span></h2>', '<h2 class="h-l mt-s">Tell us the standard<br><span class="gold-text">you want to be known for.</span></h2>')

# ---------------- other internal notes ----------------
sub("src/impact.html", '<p class="body-mute" style="font-size:13px;margin:0">Preview — no payment is taken. Giving opens at launch.</p>', '<p class="body-mute internal" style="font-size:13px;margin:0">Review note: no payment is taken; giving opens at launch.</p>')
sub("src/brand.html", '<p class="cap">Series portrait · official press headshot from Coach to replace before launch</p>', '<p class="cap internal">Review note: series portrait — replace with Coach\'s official press headshot before launch</p>')
sub("site/assets/js/site.js", "<p class=\"body-mute\">Preview build — inquiries are saved on this device only. At launch this routes straight to Coach Carter's booking desk.</p>",
    "<p class=\"body-mute\">Coach Carter's team will be in touch within two business days.</p><p class=\"body-mute internal\" style=\"font-size:13px\">Review note: preview saves inquiries on this device only; connect to the booking inbox before launch.</p>")
print("patch_06 ok")
