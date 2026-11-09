"""Patch 07: wire Coach's own videos (torch, Dr. Phil, speaker reel) into Record/Keynotes/Home,
generic click-to-load YouTube facade, archive links, modal close-button fix."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:80]}"
    p.write_text(s.replace(old, new, 1))


def facade(vid, title, ratio="16/9"):
    return (f'<div class="cinema yt" data-reveal="scale" style="aspect-ratio:{ratio};background:#000">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="{title}" loading="lazy" style="opacity:.75">'
            f'<div class="over"><button class="play-btn" data-yt="{vid}" data-cursor="Play" aria-label="Play: {title}">{{{{play}}}}</button></div></div>')


# generic YouTube facade in site.js
sub("site/assets/js/site.js", '  /* ---------------- countdowns ---------------- */', '''  /* ---------------- YouTube click-to-load ---------------- */
  document.addEventListener("click", (e) => {
    const b = e.target.closest(".cinema [data-yt]"); if (!b) return;
    const box = b.closest(".cinema");
    box.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.yt}?autoplay=1&rel=0" title="Coach Ken Carter video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe>`;
  });

  /* ---------------- countdowns ---------------- */''')
# remove the record page's own (duplicate) yt handler
rec = R / "src/record.html"
s = rec.read_text()
i = s.index('  document.querySelectorAll("[data-yt]")')
j = s.index("}));", i) + len("}));")
rec.write_text(s[:i] + s[j:])

# modal close button only when open
(R / "site/assets/css/fx.css").write_text((R / "site/assets/css/fx.css").read_text() + "\n.modal:not(.on) .x { display: none; }\n")

# RECORD: torch + Dr. Phil + Rickey Smiley films
sub("src/record.html", '<!-- MAP -->', f'''<!-- ON CAMERA -->
<section class="section">
  <span class="secnum">03 — On camera</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">In his own footage</span><h2 class="h-l mt-s">The moments,<br><span class="gold-text">on film.</span></h2></div>
      <a class="btn btn-ghost" href="archive.html#films">All 25 films {{{{arr}}}}</a></div>
    <div class="grid-3">
      <figure style="margin:0">{facade("TReXvx2yseU", "Coach Carter Olympic Torch Relay")}<figcaption class="cap">The Olympic torch relay · 2002</figcaption></figure>
      <figure style="margin:0">{facade("28kzO577IVw", "Coach Ken Carter on Dr. Phil")}<figcaption class="cap">On Dr. Phil · 2005</figcaption></figure>
      <figure style="margin:0">{facade("l-JuG82IsIQ", "Rickey Smiley and Coach Carter")}<figcaption class="cap">With Rickey Smiley</figcaption></figure>
    </div>
  </div>
</section>

<!-- MAP -->''')
sub("src/record.html", '<figure class="gx" data-reveal><div class="room-card" style="min-height:260px"><span class="eyebrow">2002 · Salt Lake City Winter Games</span><strong>Olympic torchbearer</strong><p>He carried the flame for Richmond and the Bay Area — the moment he calls the greatest of his life.</p></div><figcaption class="internal"><b>Photo needed</b><span>Torch-run photo from Coach</span></figcaption></figure>',
    f'<figure class="gx" data-reveal>{facade("PVuW6aQl8YQ", "Coach Carter Olympic Torch 2002")}<figcaption><b>Olympic torchbearer</b><span>Salt Lake City Winter Games relay · 2002</span></figcaption></figure>')
sub("src/record.html", '<a href="https://www.gettyimages.com/detail/110239085" target="_blank" rel="noopener"><span class="yr">2005</span><span class="show">Dr. Phil</span>',
    '<a href="https://www.youtube.com/watch?v=28kzO577IVw" target="_blank" rel="noopener"><span class="yr">2005</span><span class="show">Dr. Phil</span>')
sub("src/record.html", 'Linked to the outlets that ran it.', 'Linked to the outlets that ran it — and to Coach\'s own films.')

# KEYNOTES: speaker reel up front
sub("src/keynotes.html", '<section class="section">\n  <span class="secnum">01 — Signature talks</span>', f'''<section class="section carbon">
  <span class="secnum">Watch Coach work</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Speaker reel</span><h2 class="h-l mt-s">See the room<br><span class="gold-text">change.</span></h2></div>
      <a class="btn btn-ghost" href="archive.html#films">More keynotes {{{{arr}}}}</a></div>
    {facade("VkpVPjp-_F8", "Coach Ken Carter speaker reel")}
  </div>
</section>

<section class="section">
  <span class="secnum">01 — Signature talks</span>''')

# HOME: rail links to Archive
sub("src/index.html", '<a class="btn btn-ghost" href="record.html#room">See the full record {{arr}}</a>', '<a class="btn btn-ghost" href="archive.html">Open the archive {{arr}}</a>')
sub("src/index.html", '<a class="room-card" href="record.html#room"><span class="eyebrow">And more</span><strong>Courtside with Prince. Olympic torch. Dr. Phil.</strong><p>The full record of a life in the room — premieres, stages, studios and sidelines.</p></a>',
    '<a class="room-card" href="archive.html"><span class="eyebrow">120 photographs · 25 films</span><strong>Superman. The Olympic flame. Dr. Phil.</strong><p>Open the full archive — premieres, studios, stages and sidelines.</p></a>')
print("patch_07 ok")
