"""Patch 12: the 2005 film throughout the site (official Movieclips/Fandango YouTube embeds, verified quotes,
Getty premiere embeds) via site/assets/js/film.js + film.json. Idempotent: skips any page already patched."""
from pathlib import Path
R = Path(__file__).resolve().parent.parent


def ins(path, anchor, block, before=True, count=1):
    p = R / "src" / path
    s = p.read_text()
    if 'data-film="' in block and block.split("\n")[1] in s:
        return
    assert s.count(anchor) == count, f"{path}: anchor count {s.count(anchor)} != {count}: {anchor[:60]}"
    i = s.index(anchor)
    s = s[:i] + block + s[i:] if before else s[:i + len(anchor)] + block + s[i + len(anchor):]
    p.write_text(s)


def qband(qs, label="From the film", cls="carbon"):
    return f"""<section class="section tight {cls} film-qband">
<!-- film-quote {qs} -->
  <div class="wrap"><span class="eyebrow">{label}</span><div class="mt-m" data-film="quote" data-q="{qs}"></div></div>
</section>

"""


FEATURE = """<!-- THE FILM -->
<section class="section carbon" id="film">
  <span class="secnum">The film</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Paramount Pictures · MTV Films · 2005</span><h2 class="h-l mt-s">The film that<br><span class="gold-text">made the name.</span></h2></div>
      <p class="lede" style="max-width:42ch">Samuel L. Jackson played him. America made it the #1 movie in the country. Twenty-one years later it's still in Netflix's Global Top 10 — and every scene below started with one coach and one padlock in Richmond.</p></div>
    <div data-film="feature"></div>
  </div>
</section>

"""
ins("index.html", "<!-- CARTER CODE -->", FEATURE)
ins("index.html", '<section class="section maroon">\n', qband("0,2,5,10,9,4"), count=1)

STORY = """<section class="section carbon" id="real-vs-film">
<!-- film-realfilm -->
  <span class="secnum">The real story</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">What happened · what Hollywood made of it</span><h2 class="h-l mt-s">Real life,<br><span class="gold-text">then the movie.</span></h2></div>
      <p class="lede" style="max-width:42ch">The film compressed a season into two hours. Here is what the 1999 reporting says happened — and the scenes it became.</p></div>
    <div data-film="realfilm"></div>
    <div class="mt-l" data-film="strip" data-ids="V1wAemvxNaM,2FKPDOpKzDo,2_fDhqRk_Ro,eSBnFu1YnrU"></div>
  </div>
</section>

"""
ins("story.html", '<section class="section tight light">', STORY)

ins("keynotes.html", '<section class="section">\n  <span class="secnum">01 — Signature talks</span>', qband("10,9,0", "The lines audiences still quote", "light"))

PARTNERS = """<section class="section" id="the-film">
<!-- film-strip partners -->
  <span class="secnum">The story you attach to</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Tens of millions of plays on the official clips alone</span><h2 class="h-l mt-s">Partners don't buy a name.<br><span class="gold-text">They buy these scenes.</span></h2></div>
      <a class="btn btn-ghost" href="index.html#film">The film {{arr}}</a></div>
    <div data-film="strip" data-n="4"></div>
  </div>
</section>

"""
ins("partners.html", '<section class="section">\n  <span class="secnum">02 — Models</span>', PARTNERS)

SERIES = """<section class="section carbon" id="where-it-began">
<!-- film-feature series -->
  <span class="secnum">Where it began</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Coach Carter · 2005</span><h2 class="h-l mt-s">Twenty-one years ago,<br><span class="gold-text">the whole country watched.</span></h2></div>
      <p class="lede" style="max-width:42ch">Coach Carter II picks up where the 2005 film left off — with the real Coach Carter on screen and behind it.</p></div>
    <div data-film="feature"></div>
  </div>
</section>

"""
ins("series.html", '<section class="section light">\n  <span class="secnum">02 — Format</span>', SERIES)

ARCHIVE = """<section class="section carbon" id="the-2005-film">
<!-- film-archive -->
  <span class="secnum">The 2005 film</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Every official scene · premiere night</span><h2 class="h-l mt-s">Coach Carter,<br><span class="gold-text">the movie.</span></h2></div>
      <p class="lede" style="max-width:42ch">All nine official scenes, in story order, and the night the cast and the real coach walked the carpet at Grauman's Chinese Theatre.</p></div>
    <div data-film="rail"></div>
    <h3 class="h-m mt-l">Premiere &amp; awards</h3>
    <div class="mt-m" data-film="premiere" data-n="9"></div>
  </div>
</section>

"""
ins("archive.html", '<section class="section" id="films">', ARCHIVE)

ins("playbook.html", '<section class="section" id="plays">', qband("9,5,2"))

# investors: the empty slot becomes the featured-scene strip
p = R / "src/investors.html"; s = p.read_text()
s = s.replace('<div class="film-slot" data-film-slot="investors"></div>', '<div class="film-slot" data-film="strip" data-n="4"></div>')
p.write_text(s)

# build.py: load film.js site-wide; footer rights line
b = R / "tools/build.py"; s = b.read_text()
if "film.js" not in s:
    s = s.replace('<script defer src="assets/js/site.js"></script>', '<script defer src="assets/js/site.js"></script>\n<script defer src="assets/js/film.js"></script>', 1)
s = s.replace("No film footage is used on this site.", "Film scenes play from official Movieclips (Fandango) uploads on YouTube; no film footage is hosted here.")
b.write_text(s)
print("patch_12 ok")
