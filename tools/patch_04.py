"""Patch 04: visual QA fixes from the first full-site pass."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent


def sub(path, old, new, count=1):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:70]}"
    p.write_text(s.replace(old, new) if count == 0 else s.replace(old, new, count))


CSS = "site/assets/css/site.css"
FX = "site/assets/css/fx.css"

# 1. archive cards instead of empty dashed boxes
sub(CSS, """.ph {
  aspect-ratio: var(--ar, 4/5); border-radius: 14px; border: 1px dashed rgba(187,149,88,.4);
  background: repeating-linear-gradient(135deg, rgba(187,149,88,.05) 0 12px, transparent 12px 24px), var(--carbon-2);
  display: flex; flex-direction: column; justify-content: flex-end; padding: 22px; gap: 6px;
}
.ph strong { font: 600 22px/1.05 var(--f-head); text-transform: uppercase; }""", """.ph {
  position: relative; overflow: hidden; aspect-ratio: var(--ar, 4/5); border-radius: 14px; border: 1px solid rgba(187,149,88,.28);
  background: radial-gradient(120% 90% at 100% 0%, rgba(84,29,48,.75), transparent 60%), linear-gradient(180deg, #16181D, #0d0e11);
  display: flex; flex-direction: column; justify-content: flex-end; padding: 24px; gap: 8px;
  transition: transform .6s var(--ease), border-color .5s;
}
.ph:hover { transform: translateY(-4px); border-color: rgba(233,207,149,.6); }
.ph::before { content: ""; position: absolute; top: -12%; right: -14%; width: 70%; aspect-ratio: 1; background: url(../brand/crest_white.svg) center / contain no-repeat; opacity: .06; }
.ph::after { content: attr(data-y); position: absolute; top: 18px; left: 24px; font: 700 clamp(46px, 5vw, 76px)/.8 var(--f-head); color: transparent; -webkit-text-stroke: 1px rgba(233,207,149,.45); }
.ph strong { font: 600 clamp(22px, 2vw, 28px)/1.02 var(--f-head); text-transform: uppercase; position: relative; }
.ph span, .ph em { position: relative; }""")

# add years to archive cards
rec = R / "src/record.html"
s = rec.read_text()
for label, year in [("Getty #51962763", "2005"), ("Courtside with Prince", "★"), ("Getty #51962463", "2005"),
                    ("Getty #117809386", "2005"), ("The Best Damn Sports Show", "FSN"), ("Getty #115144906", "2004"),
                    ("Getty #490354626", "2015"), ("Getty #118037718", "2005"), ("Getty #1556033357", "2023")]:
    i = s.find(label)
    assert i > 0, label
    j = s.rfind('<div class="ph"', 0, i)
    s = s[:j] + f'<div class="ph" data-y="{year}"' + s[j + len('<div class="ph"'):]
rec.write_text(s)

# 2. clippings spacing
sub(FX, ".clips { position: relative; min-height: 520px; }", ".clips { position: relative; min-height: 700px; }")
sub(FX, "position: absolute; width: min(400px, 82%); background: #EEE6D6;", "position: absolute; width: min(360px, 72%); background: #EEE6D6;")
sub(FX, ".clip:nth-child(2) { right: 0; top: 70px; transform: rotate(3deg); }", ".clip:nth-child(2) { right: 0; top: 140px; transform: rotate(3deg); }")
sub(FX, ".clip:nth-child(3) { left: 10%; top: 270px; transform: rotate(-1.5deg); }", ".clip:nth-child(3) { left: 4%; top: 330px; transform: rotate(-1.5deg); }")
sub(FX, ".clip:nth-child(4) { right: 6%; top: 330px; transform: rotate(4.5deg); }", ".clip:nth-child(4) { right: 2%; top: 480px; transform: rotate(4.5deg); }")

# 3. compact stats variant
sub(CSS, ".light .stats, .light .stat {", ".stats.mini .stat .n { font-size: clamp(36px, 3.6vw, 58px); white-space: nowrap; }\n.light .stats, .light .stat {")
sub("src/story.html", '<div class="stats mt-m" style="grid-template-columns:repeat(3,1fr)">', '<div class="stats mini mt-m" style="grid-template-columns:repeat(3,1fr)">')

# 4. store hero + product book size
sub("src/store.html", '<video data-auto muted loop playsinline preload="auto" poster="assets/video/outro.jpg" src="assets/video/outro.mp4"></video>',
    '<video data-auto muted loop playsinline preload="auto" poster="assets/video/court.jpg" src="assets/video/court.mp4"></video>')
sub(CSS, ".product .thumb > .book3d { --w: 46%; --d: 20px; }", ".product .thumb > .book3d { --w: clamp(130px, 13vw, 190px); --d: 22px; }")

# 5. keynotes portrait
sub("src/keynotes.html", '<div class="portrait mt-m" style="max-width:360px;aspect-ratio:3/4"><img class="p" src="assets/img/suit_full.jpg" alt="Coach Ken Carter, full-length in a navy suit" loading="lazy" style="object-position:50% 20%"></div>',
    '<div class="portrait mt-m" style="max-width:420px;aspect-ratio:4/3"><img class="p" src="assets/img/s_press.jpg" alt="Coach Carter at a press-conference podium" loading="lazy" style="object-position:70% 30%"></div>')
print("ok")
