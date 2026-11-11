"""Search layer: canonical + social tags, JSON-LD structured data, FAQ hub, sitemap, robots.

ONE switch decides whether search engines may index the site:

    INDEXABLE = False   -> preview: every page stays  noindex, nofollow  (today)
    INDEXABLE = True    -> launch:  public pages become indexable, sitemap.xml is advertised

Set SITE_URL to the real domain at the same time. Investors and Coach's briefing are never indexable.
Every fact in the FAQ is one the site already states with a source (film.json facts / real-vs-film,
story timeline). Nothing here is new research.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site"

SITE_URL = "https://dvolcore.github.io/coachcarter-preview/"   # change to the real domain at launch
INDEXABLE = False                                             # flip to True at launch (Ralph's call)
NEVER_INDEX = {"investors", "coach"}
SITE_NAME = "The Real Coach Carter"
PERSON_ID = SITE_URL + "#coach-ken-carter"
IMG = SITE_URL + "assets/img/private/coach-portrait.jpg"

PERSON = {
    "@type": "Person", "@id": PERSON_ID, "name": "Ken Carter", "alternateName": ["Coach Carter", "Coach Ken Carter"],
    "jobTitle": "Educator, author, speaker and basketball coach", "birthDate": "1959-02-13",
    "alumniOf": {"@type": "HighSchool", "name": "Richmond High School", "address": "Richmond, California"},
    "description": "The real coach behind the 2005 film Coach Carter. In January 1999 he locked his undefeated Richmond High team out of the gym until they met the academic contract they had signed.",
    "image": IMG, "url": SITE_URL,
    "sameAs": ["https://en.wikipedia.org/wiki/Ken_Carter", "https://www.youtube.com/channel/UCkq8ZF3PXaOsHDjgxggkrBg", "https://www.facebook.com/Coachkcarter"],
}
MOVIE = {
    "@type": "Movie", "@id": SITE_URL + "#coach-carter-2005", "name": "Coach Carter", "datePublished": "2005-01-14", "duration": "PT136M",
    "contentRating": "PG-13", "director": {"@type": "Person", "name": "Thomas Carter"},
    "actor": [{"@type": "Person", "name": "Samuel L. Jackson"}, {"@type": "Person", "name": "Rob Brown"}, {"@type": "Person", "name": "Robert Ri'chard"}, {"@type": "Person", "name": "Rick Gonzalez"}],
    "productionCompany": [{"@type": "Organization", "name": "MTV Films"}, {"@type": "Organization", "name": "Paramount Pictures"}],
    "about": {"@id": PERSON_ID}, "sameAs": ["https://www.imdb.com/title/tt0393162/", "https://en.wikipedia.org/wiki/Coach_Carter"],
}
BOOK = {
    "@type": "Book", "name": "Yes Ma'am, No Sir: The 12 Essential Steps for Success in Life", "author": {"@id": PERSON_ID}, "isbn": "9781455502349",
    "publisher": {"@type": "Organization", "name": "Business Plus (Hachette Book Group)"}, "bookFormat": "https://schema.org/Hardcover",
    "url": "https://www.hachettebookgroup.com/titles/coach-carter/yes-maam-no-sir/9781455502349/",
}
SERIES = {
    "@type": "TVSeries", "name": "Coach Carter Academy", "description": "A series in development from Studio405 with Coach Ken Carter as executive producer. A free 60-second preview is available.",
    "productionCompany": {"@type": "Organization", "name": "Studio405"}, "about": {"@id": PERSON_ID},
}
SERVICE = {
    "@type": "Service", "name": "Coach Carter keynotes", "serviceType": "Keynote speaking", "provider": {"@id": PERSON_ID},
    "description": "Five signature talks on accountability, discipline, respect and education, tailored to corporate, education, conference, faith and youth events.",
    "areaServed": "United States",
}

S_CNN = ("CNN, January 7, 1999", "https://www.cnn.com/US/9901/07/team.lockout/")
S_SFG = ("San Francisco Chronicle / SFGate, January 1999", "https://www.sfgate.com/news/article/Coach-scores-points-for-academics-3240562.php")
S_BOM = ("Box Office Mojo", "https://www.boxofficemojo.com/title/tt0393162/")
S_WIK = ("Wikipedia: Coach Carter", "https://en.wikipedia.org/wiki/Coach_Carter")
S_SND = ("Wikipedia: Coach Carter (soundtrack)", "https://en.wikipedia.org/wiki/Coach_Carter_(soundtrack)")
FAQ = [  # question, answer (plain text), [(source label, url)], optional (link label, href)
    ("Is Coach Carter a true story?",
     "Yes. Ken Carter coached the Richmond High Oilers in Richmond, California. In early January 1999, with the team 13–0, he padlocked the gym and cancelled practices and games because players had broken the academic contract they signed. The 2005 film is based on that season.",
     [S_CNN, S_SFG], ("Read the full story", "story.html")),
    ("Who is the real Coach Carter?",
     "Ken Carter, born February 13, 1959. He is a 1977 Richmond High graduate who held the school's scoring record and owned a sporting-goods store before he came back to coach. Today he is an educator, author and speaker.",
     [S_SFG], ("See the record", "record.html")),
    ("Why did Coach Carter lock the gym?",
     "Fifteen of the program's 45 players (varsity, junior varsity and freshman) had broken the contract: tardiness, missing homework, or a grade point average under 2.3. He locked out the whole program until every player met the terms.",
     [S_SFG, S_CNN], None),
    ("What was in the Coach Carter contract?",
     "A 2.3 grade point average, attending every class and sitting in the front row, and ten hours of study a week. CNN described it as a 19-point pledge. Its principle: basketball is the hook and education is the goal.",
     [S_SFG, S_CNN], ("See the contract", "story.html#original-contract")),
    ("How long did the lockout last? Did Richmond forfeit games?",
     "About a week. On January 11, 1999 school officials announced that all 45 players had met the criteria, and the season resumed without forfeits.",
     [S_SFG], None),
    ("What did the movie change from real life?",
     "In the film the school board votes to end the lockout over Carter's objection and the team chooses to keep studying. In 1999 the lockout ended when officials announced every player had met the contract. The film compresses a season into two hours.",
     [S_SFG, S_WIK], ("Real life vs. the film", "story.html#real-vs-film")),
    ("Was Coach Carter's son really on the team?",
     "Yes. His son Damien Carter was on the 1999 team and was quoted by CNN at the time. In the film Damien is played by Robert Ri'chard.",
     [S_CNN], None),
    ("Who played Coach Carter in the movie?",
     "Samuel L. Jackson. The film was directed by Thomas Carter and written by Mark Schwahn and John Gatins, with Rob Brown, Robert Ri'chard and Rick Gonzalez in the cast. It was produced by MTV Films and Tollin/Robbins Productions and distributed by Paramount Pictures.",
     [S_WIK], ("Watch the scenes", "archive.html#the-2005-film")),
    ("When did Coach Carter come out, and how did it do?",
     "It opened in the United States on January 14, 2005 and was number one at the box office that weekend with $24,182,961 from 2,524 theaters. It went on to $67.26 million in the U.S. and $76.67 million worldwide.",
     [S_BOM], None),
    ("How long is Coach Carter, and what is it rated?",
     "136 minutes (2 hours 16 minutes), rated PG-13.", [S_BOM], None),
    ("Where was Coach Carter filmed?",
     "In Los Angeles and Long Beach, California, including the gym at St. Anthony High School.", [S_WIK], None),
    ("Did Coach Carter win any awards?",
     "Samuel L. Jackson won the NAACP Image Award for Outstanding Actor in a Motion Picture for the role. Audiences gave the film a CinemaScore of A, and Roger Ebert gave it three stars out of four.",
     [S_WIK], None),
    ("Who did the music for Coach Carter?",
     "The score is by Trevor Rabin. The soundtrack, Coach Carter: Music from the Motion Picture, was released by Capitol Records on January 11, 2005 and reached number 25 on the Billboard 200 and number 3 on the Soundtrack Albums chart.",
     [S_SND], None),
    ("What happened to the players Coach Carter locked out?",
     "Two years later the Los Angeles Times reported that all fifteen who had fallen short of the contract were in higher education.",
     [("Los Angeles Times, 2001 (as cited on The Story)", "story.html#from-richmond-to-the-world")], None),
    ("Did Coach Carter write a book?",
     "Yes. Yes Ma'am, No Sir: The 12 Essential Steps for Success in Life, published by Business Plus (Hachette Book Group) in 2012, with an audio edition read by Coach Carter and Vince Bailey.",
     [("Hachette Book Group", "https://www.hachettebookgroup.com/titles/coach-carter/yes-maam-no-sir/9781455502349/")], ("See the editions", "store.html#dept-books")),
    ("What is Coach Carter Academy?",
     "A series in development from Studio405 with Coach Ken Carter as executive producer. A free 60-second preview is on this site.",
     [], ("Watch the preview", "series.html")),
    ("How do I book Coach Carter to speak?",
     "Through the keynotes page: choose the kind of event, give a date and a city, and the booking desk replies with availability.",
     [], ("Check availability", "keynotes.html#book")),
]


def faq_html():
    items = []
    for i, (q, a, sources, more) in enumerate(FAQ):
        src = " · ".join(f'<a href="{escape(u)}"{"" if not u.startswith("http") else " target=_blank rel=noopener"}>{escape(n)}</a>' for n, u in sources)
        src = f'<p class="faq-src">Source: {src}</p>' if src else ""
        link = f'<a class="link-u" href="{more[1]}">{escape(more[0])}</a>' if more else ""
        items.append(f'<article class="faq-item" id="q{i + 1}"><h2>{escape(q)}</h2><p>{escape(a)}</p>{src}{link}</article>')
    return '<div class="faq-list">' + "".join(items) + "</div>"


def _crumbs(name, label, world):
    items = [("Home", SITE_URL)]
    if world:
        items.append((world["label"], SITE_URL + world["pages"][0][1].split("#")[0]))
    if name != "index.html":
        items.append((label, SITE_URL + name))
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def apply(html, meta, name, nav, label, world, share_image):
    url = SITE_URL + ("" if name == "index.html" else name)
    title, desc = meta["title"], meta.get("desc", "")
    graph = [
        {"@type": "WebSite", "@id": SITE_URL + "#website", "url": SITE_URL, "name": SITE_NAME, "publisher": {"@id": PERSON_ID}, "inLanguage": "en-US"},
        PERSON,
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc, "isPartOf": {"@id": SITE_URL + "#website"},
         "about": {"@id": PERSON_ID}, "primaryImageOfPage": {"@type": "ImageObject", "url": share_image}, "inLanguage": "en-US"},
        _crumbs(name, label, world),
    ]
    if nav in ("home", "story", "archive", "faq"):
        graph.append(MOVIE)
    if nav in ("home", "store"):
        graph.append(BOOK)
    if nav in ("home", "series"):
        graph.append(SERIES)
    if nav == "keynotes":
        graph.append(SERVICE)
    if nav == "faq":
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a, _, _ in FAQ]})
    if nav == "archive":
        import private
        graph.append({"@type": "ImageGallery", "name": "From Coach Carter's private collection", "about": {"@id": PERSON_ID}, "image": [
            {"@type": "ImageObject", "contentUrl": SITE_URL + private.DIR + f + ".jpg", "name": t, "caption": f"{t}. {line}.", "width": w, "height": h}
            for f, w, h, t, line, _ in private.PRIVATE]})
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tags = (f'<link rel="canonical" href="{url}">\n<meta property="og:url" content="{url}">\n<meta property="og:type" content="{"profile" if nav == "home" else "article"}">\n'
            f'<meta property="og:site_name" content="{SITE_NAME}">\n<meta property="og:locale" content="en_US">\n<meta property="og:image:alt" content="{escape(title)}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{escape(title)}">\n'
            f'<meta name="twitter:description" content="{escape(desc)}">\n<meta name="twitter:image" content="{share_image}">\n'
            f'<script type="application/ld+json">{ld}</script>\n')
    html = html.replace("</head>", tags + "</head>", 1)
    if INDEXABLE and nav not in NEVER_INDEX:
        html = html.replace('<meta name="robots" content="noindex, nofollow">', '<meta name="robots" content="index, follow, max-image-preview:large">', 1)
    return html


def write_site_files(pages):
    """sitemap.xml + robots.txt. `pages` = [(file name, nav key)] in build order."""
    public = [n for n, nav in pages if nav not in NEVER_INDEX]
    urls = "".join(f"<url><loc>{SITE_URL}{'' if n == 'index.html' else n}</loc><priority>{'1.0' if n == 'index.html' else '0.8'}</priority></url>" for n in public)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    block = "".join(f"Disallow: /{n}\n" for n, nav in pages if nav in NEVER_INDEX)
    if INDEXABLE:
        robots = f"User-agent: *\nAllow: /\n{block}\nSitemap: {SITE_URL}sitemap.xml\n"
    else:
        robots = "# Preview: pages carry noindex. Flip INDEXABLE in tools/seo.py at launch.\nUser-agent: *\nAllow: /\n"
    (OUT / "robots.txt").write_text(robots)
    print("seo: sitemap", len(public), "urls · indexable =", INDEXABLE)
