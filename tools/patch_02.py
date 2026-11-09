"""Patch 02: zoom through the 'I' of WIN, chapter-4 media swap, book contrast."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:70]}"
    p.write_text(s.replace(old, new))


# zoom target = the letter I
sub("src/index.html", '<div class="zt-mask" aria-hidden="true"><span>WE WIN</span></div>',
    '<div class="zt-mask" aria-hidden="true"><span>WE W<b class="zt-i">I</b>N</span></div>')
sub("site/assets/js/site.js", '''    const mask = $(".zt-mask", sec); const after = $(".zt-after", sec);
    scrollers.push(() => {''', '''    const mask = $(".zt-mask", sec); const after = $(".zt-after", sec); const target = $(".zt-i", sec);
    const aim = () => {
      if (!target) return;
      mask.style.transform = "none";
      const m = mask.getBoundingClientRect(); const t = target.getBoundingClientRect();
      mask.style.transformOrigin = `${t.left + t.width / 2 - m.left}px ${t.top + t.height * 0.55 - m.top}px`;
    };
    aim(); addEventListener("resize", aim); document.fonts && document.fonts.ready.then(aim);
    scrollers.push(() => {''')
sub("site/assets/css/fx.css", ".zt-mask span { color: #fff;", ".zt-mask b { font-weight: inherit; }\n.zt-mask span { color: #fff;")

# chapter 4 (2005 film) gets the gold-lights plate; chapter 5 (next) gets CC2 title art
sub("src/index.html",
    '''      <video muted loop playsinline preload="metadata" poster="assets/video/title.jpg" src="assets/video/title.mp4"></video>
      <video muted loop playsinline preload="metadata" poster="assets/video/drive.jpg" src="assets/video/drive.mp4"></video>''',
    '''      <video muted loop playsinline preload="metadata" poster="assets/video/outro.jpg" src="assets/video/outro.mp4"></video>
      <video muted loop playsinline preload="metadata" poster="assets/video/title.jpg" src="assets/video/title.mp4"></video>''')

# book: carbon cover with gold foil on maroon section
sub("src/index.html", '''        <div class="book3d" data-tilt style="--w:min(340px,64vw)">
          <div class="face front"><div class="cover c1">''', '''        <div class="book3d" data-tilt style="--w:min(340px,64vw)">
          <div class="face front"><div class="cover c2 foil">''')
sub("src/index.html", "<div><b>Hardcover</b><small>ISBN 978-1-4555-0234-9</small></div>",
    "<div><b>Hardcover</b><small>Business Plus · 2012</small></div>")
sub("site/assets/css/site.css", ".cover.c2 { background: linear-gradient(160deg, #15171c, #08090b); }",
    ".cover.c2 { background: linear-gradient(160deg, #1b1d23, #08090b); }\n"
    ".cover.foil .ct-title { background: var(--gold-sheen); background-size: 250% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; animation: sheen 7s var(--ease-io) infinite; }\n"
    ".cover.foil::before { content: \"\"; position: absolute; inset: 5%; border: 1px solid rgba(233,207,149,.35); pointer-events: none; }\n"
    ".book-stage { filter: drop-shadow(0 50px 60px rgba(0,0,0,.55)); }")
print("patched")
