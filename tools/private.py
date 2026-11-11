"""Coach's private collection — the photographs he supplied on 2026-11-10.

Restored by tools/private_photos/restore.sh (orient, crop to the print, remove screen moire,
level, sharpen; nothing generated). Names appear only where Ralph supplied them or the photograph
itself says so (jersey lettering, set signage). `ask` = what Coach still has to tell us; it shows
in review mode only.
"""
from html import escape

DIR = "assets/img/private/"
PRIVATE = [  # file, w, h, title, line, ask
    ("courtside-prince-jackson", 1800, 1241, "Courtside with Samuel L. Jackson and Prince", "Front row · AI-enhanced from the original", "date, arena, photo credit"),
    ("with-usher", 1500, 1006, "With Usher", "From his own album", "year, occasion"),
    ("drphil-jackson", 1800, 1182, "With Samuel L. Jackson and Dr. Phil", "On the Dr. Phil set", ""),
    ("all-stars-24", 1350, 1800, "No. 24", "Contra Costa All Stars", "year"),
    ("drphil-set", 1800, 1158, "On Dr. Phil", "On air with Samuel L. Jackson", ""),
    ("coach-portrait", 1350, 1800, "Coach Ken Carter", "Portrait", "year, place"),
    ("oilers-team", 1800, 1213, "The Oilers", "Richmond High", "year, names"),
    ("on-the-floor", 1300, 1560, "On the floor", "From his own album", "who, where"),
    ("in-the-hallway", 2000, 1333, "In the hallway", "With students", "school, year"),
    ("huddle", 1800, 1244, "In the huddle", "From his own album", "team, year"),
    ("by-the-trailer", 1092, 1800, "By the trailers", "From his own album", "who, where"),
    ("portrait-pair", 1800, 1260, "In good company", "From his own album", "who, occasion"),
    ("courtside-prince-jackson-2", 1500, 1114, "Courtside, second frame", "Same night", ""),
    ("on-location", 1800, 1423, "On location", "From his own album", "who, where"),
    ("team-jackets", 1800, 1258, "The team", "From his own album", "team, year"),
    ("handshake", 1350, 1800, "Good to see you", "From his own album", "who, when"),
    ("five-men", 1600, 1199, "Five across", "From his own album", "who"),
    ("on-set", 1100, 1817, "On set", "Richmond colors", "who, photo credit"),
    ("three-men", 1600, 1120, "Three across", "From his own album", "who, occasion"),
    ("in-the-gym", 1100, 1677, "Still in the gym", "Today", ""),
]


def _fig(i, cls):
    f, w, h, title, line, ask = PRIVATE[i]
    note = f'<small class="internal">Caption needed from Coach: {escape(ask)}</small>' if ask else ""
    return (f'<figure class="{cls}" style="--i:{i}"><a href="{DIR}{f}.jpg" data-lb data-cap="{escape(title)} · {escape(line)}">'
            f'<img src="{DIR}{f}-900.jpg" alt="{escape(title)}. {escape(line)}." width="{w}" height="{h}" loading="lazy" decoding="async"></a>'
            f'<figcaption><b>{escape(title)}</b><span>{escape(line)}</span>{note}</figcaption></figure>')


def collection():
    lead = _fig(0, "pc-lead") + '<div class="pc-side">' + _fig(1, "pc-print") + _fig(2, "pc-print") + "</div>"
    rest = "".join(_fig(i, "pc-print") for i in range(3, len(PRIVATE)))
    return (
        '<section class="pc" id="private-collection" aria-labelledby="pc-title" data-rail="Private collection">\n'
        '  <div class="wrap">\n'
        '    <header class="pc-head"><div><span class="eyebrow">Never published</span>'
        '<h2 class="h-l mt-s" id="pc-title">From Coach&#39;s<br><span class="gold-text">private collection.</span></h2></div>\n'
        f'      <p class="lede">{len(PRIVATE)} photographs from his own albums and phone. Courtside, on set, on air, '
        'and back when he wore the jersey himself.</p></header>\n'
        f'    <div class="pc-top">{lead}</div>\n'
        f'    <div class="pc-wall">{rest}</div>\n'
        '    <p class="credit">Photographs from Coach Ken Carter&#39;s private collection, restored for this archive. '
        'Select any photograph to see it full size.</p>\n'
        '  </div>\n'
        '</section>\n'
    )
