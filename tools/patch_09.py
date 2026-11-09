"""Patch 09: Coach's own scrapbook (recovered from his archived sites), client wall, TV credits from his CV."""
import json
import shutil
from pathlib import Path

from PIL import Image

R = Path(__file__).resolve().parent.parent
SRC = R / "tracking/investigation/wayback_assets/coachcarter.com"
OUT = R / "site/assets/img/own"
OUT.mkdir(parents=True, exist_ok=True)


def find(suffix, prefix):
    hits = sorted(SRC.glob(f"{prefix}*_{suffix}"))
    assert hits, (prefix, suffix)
    return hits[0]


# (album file, out name, caption, chapter)  — captions are Coach's own 2002 album captions
ITEMS = [
    ("20061012", "025.jpg", "torch_raised", "Torch raised in Richmond", "torch"),
    ("20061012", "023.jpg", "torch_relay", "Carrying the Olympic torch through Richmond", "torch"),
    ("20061012", "024.jpg", "torch_welcome", "City of Richmond welcomes the 2002 Olympic Torch Relay", "torch"),
    ("20061012", "027.jpg", "torch_pass", "Passing the flame", "torch"),
    ("20061012", "026.jpg", "torch_cauldron", "The torch ceremony at Richmond City Hall", "torch"),
    ("20061012", "001.jpg", "jesse_jackson", "With Rev. Jesse Jackson", "leaders"),
    ("20061012", "002.jpg", "gray_davis", "With Governor Gray Davis", "leaders"),
    ("20061012", "004.jpg", "chris_tucker", "With Chris Tucker", "leaders"),
    ("20061012", "006.jpg", "gladys_knight_les_brown", "With Gladys Knight and Les Brown", "leaders"),
    ("20061012", "007.jpg", "julie_brown", "With Downtown Julie Brown", "leaders"),
    ("20061012", "008.jpg", "eric_dickerson", "With Eric Dickerson", "leaders"),
    ("20061012", "010.jpg", "phil_jackson", "With Coach Phil Jackson", "leaders"),
    ("20061012", "012.jpg", "willie_brown_team", "Mayor Willie Brown with the Richmond High team", "leaders"),
    ("20061012", "005.jpg", "george_miller_damien", "Congressman George Miller with Damien Carter", "leaders"),
    ("20061012", "014.jpg", "team_trophy", "The Richmond High team with the trophy", "richmond"),
    ("20061012", "013.jpg", "team", "The Richmond High team", "richmond"),
    ("20061012", "021.jpg", "as_player", "Ken Carter as a Richmond High player", "richmond"),
    ("20061012", "022.jpg", "as_player_2", "On the court for Richmond High", "richmond"),
    ("20061012", "015.jpg", "old_team", "The Richmond High team when Coach was a player", "richmond"),
    ("20061012", "009.jpg", "business_award", "African American Excellence in Business Award", "richmond"),
    ("20061012", "018.jpg", "lottery", "At the California Lottery Big Spin", "richmond"),
    ("2006102", "001.jpg", "drphil_jackson", "Coach Ken Carter · Samuel L. Jackson · Dr. Phil", "drphil"),
    ("2006102", "002.jpg", "drphil_set", "On the Dr. Phil set", "drphil"),
    ("2006102", "003.jpg", "drphil_set_2", "Dr. Phil Show taping", "drphil"),
    ("2006102", "004.jpg", "drphil_solo", "Dr. Phil Show", "drphil"),
    ("2006102", "006.jpg", "premiere_jackson", "Paramount premiere", "drphil"),
    ("2006102", "005.jpg", "premiere_lineup", "Paramount premiere", "drphil"),
]
data = []
for prefix, suffix, name, cap, ch in ITEMS:
    f = find(suffix, prefix)
    im = Image.open(f).convert("RGB")
    im.save(OUT / f"{name}.jpg", quality=88)
    data.append({"src": f"assets/img/own/{name}.jpg", "caption": cap, "chapter": ch, "w": im.width, "h": im.height})
(R / "site/assets/data/scrapbook.json").write_text(json.dumps({"photos": data}, indent=0))
print("exported", len(data))


def sub(path, old, new):
    p = R / path
    s = p.read_text()
    assert old in s, f"missing in {path}: {old[:80]}"
    p.write_text(s.replace(old, new, 1))


def polaroid(name, cap, tilt):
    return (f'<figure class="pol" style="--t:{tilt}deg" data-reveal><img src="assets/img/own/{name}.jpg" alt="{cap}" loading="lazy">'
            f'<figcaption>{cap}</figcaption></figure>')


# ---------- ARCHIVE: scrapbook section ----------
groups = [("torch", "Olympic torch · Richmond · January 19, 2002"), ("leaders", "Leaders & legends"),
          ("richmond", "Richmond High"), ("drphil", "Dr. Phil & the premiere · 2005")]
tilts = [-2.5, 1.8, -1.2, 2.4, -1.8, 1.2]
html = ""
for key, label in groups:
    items = [d for d in data if d["chapter"] == key]
    html += f'<div class="sgroup"><header><h3>{label}</h3></header><div class="scrap">' + "".join(
        polaroid(Path(d["src"]).stem, d["caption"], tilts[i % len(tilts)]) for i, d in enumerate(items)) + "</div></div>"
sub("src/archive.html", '<section class="section" id="films">', f'''<section class="section light" id="scrapbook">
  <span class="secnum">02 — The scrapbook</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">From Coach's own photo album</span><h2 class="h-l mt-s">In his own<br>photographs.</h2></div>
      <p class="lede" style="max-width:40ch">Recovered from the photo albums Coach published on coachcarter.com from 2002 to 2006 — the Olympic torch run, governors and legends, and the Richmond High teams, in his own captions.</p></div>
    {html}
    <p class="body-mute internal mt-m" style="font-size:14px">Review note: these are the web-size copies (400×300) recovered from the Internet Archive. Ask Coach for the original prints/files; photographer releases needed for any paid campaign.</p>
  </div>
</section>

<section class="section" id="films">''')
sub("src/archive.html", '<span class="secnum">02 — The films</span>', '<span class="secnum">03 — The films</span>')
sub("src/archive.html", '<span class="secnum">03 — Every photograph</span>', '<span class="secnum">04 — Every photograph</span>')
sub("src/archive.html", "<p class=\"lede\">Red carpets with Samuel L. Jackson and Ashanti. Dr. Phil. Hall of Famers. The Olympic flame. The SlamBall sideline.",
    "<p class=\"lede\">Red carpets with Samuel L. Jackson and Ashanti. Dr. Phil. Chris Tucker, Jesse Jackson and Gladys Knight. Hall of Famers. The Olympic flame. The SlamBall sideline.")

# ---------- HOME rail: lead with his own torch + legends photos ----------
sub("src/index.html", '<div class="room-rail">', '<div class="room-rail">' + "".join(
    f'<figure class="gx pol-rail"><img src="assets/img/own/{n}.jpg" alt="{c}" loading="lazy"><figcaption><b>{c}</b><span>{w}</span></figcaption></figure>'
    for n, c, w in [("torch_raised", "Olympic torchbearer", "Richmond · Jan 19, 2002 · from Coach's album"),
                    ("chris_tucker", "With Chris Tucker", "From Coach's album"),
                    ("jesse_jackson", "With Rev. Jesse Jackson", "From Coach's album")]))

# ---------- RECORD: own collection gets torch + legends; Prince card → review only ----------
sub("src/record.html", '<figure class="gx" data-reveal><div class="room-card" style="min-height:260px"><span class="eyebrow">Courtside</span><strong>Front row with Prince</strong><p>From Coach\'s personal collection.</p></div><figcaption class="internal"><b>Photo needed</b><span>Ask Coach for the original</span></figcaption></figure>',
    '<figure class="gx internal" data-reveal><div class="room-card" style="min-height:260px"><span class="eyebrow">Courtside</span><strong>Front row with Prince</strong><p>Not found in any public record or on Coach\'s own sites — photo needed from Coach.</p></div></figure>'
    + "".join(f'<figure class="gx" data-reveal><div class="media-frame"><img src="assets/img/own/{n}.jpg" alt="{c}" loading="lazy"></div><figcaption><b>{c}</b><span>{w}</span></figcaption></figure>'
              for n, c, w in [("torch_raised", "Olympic torchbearer", "Richmond · January 19, 2002"), ("chris_tucker", "With Chris Tucker", "Coach's photo album"),
                              ("gray_davis", "With Governor Gray Davis", "Coach's photo album"), ("gladys_knight_les_brown", "With Gladys Knight and Les Brown", "Coach's photo album")]))
sub("src/record.html", '<header><h3>From Coach\'s own collection</h3><span>Coachcarter.com archive</span></header>', '<header><h3>From Coach\'s own collection</h3><span>His photo albums, 2002–2006</span></header>')
# extra TV credits his own sites list
sub("src/record.html", '<div class="r"><span class="yr">2005</span><span class="show">Dr. Phil</span>', '<div class="r"><span class="yr">2005</span><span class="show">Dr. Phil</span>', ) if False else None
tv_rows = ''.join(f'<div class="r"><span class="yr">{y}</span><span class="show">{s}</span><span class="what">{w}</span><span class="go">{{{{out}}}}</span></div>'
                  for y, s, w in [("2005", "The View", "With Barbara Walters, during the film's release — as listed on Coach's 2005 site."),
                                  ("2005", "Extra · The Entertainers", "Entertainment-news coverage of the film — as listed on Coach's 2005 site."),
                                  ("2005", "ESPN · Cold Pizza", "ESPN morning show — as listed on Coach's 2005 site."),
                                  ("2000s", "Judge Hatchett", "Syndicated TV — on Coach's 2009 client list.")])
sub("src/record.html", '<a href="https://christianitytoday.com/ct/2005/januaryweb-only/kencarter.html"', tv_rows + '\n      <a href="https://christianitytoday.com/ct/2005/januaryweb-only/kencarter.html"')
sub("src/record.html", '<span class="what">Fox Sports Net studio appearance. <em class="internal" style="color:var(--gold)">Archive pending — clip and date from Coach.</em></span>',
    '<span class="what">Fox Sports Net studio appearance — as listed on Coach\'s 2005 and 2009 sites. <em class="internal" style="color:var(--gold)">Clip and exact date from Coach.</em></span>')

# ---------- CLIENT WALL (keynotes + investors) ----------
CLIENTS = ["FedEx", "Wells Fargo", "Chevron", "Shell", "Bank of America", "Ameriprise", "TD AmeriTrade", "Caterpillar", "Ortho-McNeil",
           "Synovus", "Georgia Tech", "UNC", "UC Berkeley", "Kansas State", "Mississippi State", "Tennessee", "Virginia Tech",
           "San José State", "Cal Poly Pomona", "L.A. County Board of Supervisors", "U.S. Embassy", "National Assn. of Black Journalists",
           "Delta Sigma Theta", "Athene · Chase summit", "NAI Global", "Boys & Girls Clubs", "My Brother's Keeper", "Petfood Forum"]
wall = ('<div class="clients" data-reveal>' + "".join(f"<span>{c}</span>" for c in CLIENTS) + '</div>'
        '<p class="credit mt-s">From Coach\'s published client list and documented engagements. Names shown as text; no endorsement implied.</p>')
sub("src/keynotes.html", '<section class="section light">\n  <span class="secnum">02 — Formats</span>', f'''<section class="section carbon">
  <span class="secnum">Who has booked Coach</span>
  <div class="wrap">
    <div class="sec-head"><div><span class="eyebrow">Corporations · universities · government · community</span><h2 class="h-l mt-s">In the room<br><span class="gold-text">for the best.</span></h2></div></div>
    {wall}
  </div>
</section>

<section class="section light">
  <span class="secnum">02 — Formats</span>''')
sub("src/investors.html", '<h3 class="h-m mt-l">What hosts say</h3>', f'<h3 class="h-m mt-l">Organizations served</h3><div class="mt-m">{wall}</div>\n    <h3 class="h-m mt-l">What hosts say</h3>')

css = R / "site/assets/css/fx.css"
css.write_text(css.read_text() + """
/* scrapbook polaroids */
.sgroup { margin-top: clamp(48px, 6vw, 80px); }
.sgroup:first-of-type { margin-top: 0; }
.sgroup > header { border-top: 1px solid rgba(16,18,22,.14); padding-top: 16px; margin-bottom: 28px; }
.sgroup h3 { margin: 0; font: 600 clamp(24px, 2.4vw, 34px)/1 var(--f-head); text-transform: uppercase; }
.scrap { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 34px 26px; }
.pol { margin: 0; background: #fff; padding: 12px 12px 16px; box-shadow: 0 18px 40px -18px rgba(16,18,22,.45), 0 2px 6px rgba(16,18,22,.08); transform: rotate(var(--t, 0deg)); transition: transform .6s var(--ease), box-shadow .6s; }
.pol:hover { transform: rotate(0deg) translateY(-6px) scale(1.03); box-shadow: 0 30px 60px -20px rgba(16,18,22,.55); z-index: 2; position: relative; }
.pol img { width: 100%; aspect-ratio: 4/3; object-fit: cover; filter: saturate(.95) contrast(1.02); }
.pol figcaption { margin-top: 12px; font: 500 italic 18px/1.25 var(--f-quote); color: #2a2a2e; }
.pol-rail img { width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: 14px; border: 1px solid var(--line); }
.clients { display: flex; flex-wrap: wrap; gap: 10px; }
.clients span { padding: 12px 18px; border-radius: 999px; border: 1px solid var(--line-strong); font: 600 13px/1 var(--f-head); letter-spacing: .14em; text-transform: uppercase; color: rgba(245,240,232,.82); transition: all .3s; }
.clients span:hover { border-color: var(--gold); color: var(--gold-hi); }
""")
print("patch_09 ok")
