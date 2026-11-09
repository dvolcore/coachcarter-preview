"""Builds the Coach Carter logo system as outlined SVG (no font dependency).

Outputs to site/assets/brand/:
  wordmark_gold.svg / wordmark_white.svg / wordmark_black.svg   primary lockup
  crest_gold.svg / crest_white.svg                                circular seal
  monogram_gold.svg                                               KC mark alone
  appicon.svg                                                     maroon tile + monogram
Fonts (OFL): Cinzel (Trajan-style, matches the CC2 title), Barlow Condensed
(DIN-Condensed stand-in from the CC2 brand sheet).
"""
import math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "site" / "assets" / "brand"
OUT.mkdir(parents=True, exist_ok=True)

cinzel = instantiateVariableFont(TTFont(ROOT / "fonts" / "Cinzel[wght].ttf"), {"wght": 700})
cinzel_reg = instantiateVariableFont(TTFont(ROOT / "fonts" / "Cinzel[wght].ttf"), {"wght": 500})
barlow = TTFont(ROOT / "fonts" / "BarlowCondensed-SemiBold.ttf")

GOLD_DEF = """<linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#F6E3B4"/><stop offset=".45" stop-color="#D4AF6A"/>
<stop offset=".55" stop-color="#BB9558"/><stop offset="1" stop-color="#7E5C2C"/></linearGradient>"""


def text_path(font, text, size, x=0.0, y=0.0, tracking=0.0):
    """Return (svg path d, advance width) for text with baseline at y."""
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    s = size / upm
    pen = SVGPathPen(gs)
    cx = x
    for ch in text:
        name = cmap.get(ord(ch))
        if name is None:
            continue
        g = gs[name]
        tp = TransformPen(pen, (s, 0, 0, -s, cx, y))
        g.draw(tp)
        cx += g.width * s + tracking
    return pen.getCommands(), cx - x - tracking


def width(font, text, size, tracking=0.0):
    return text_path(font, text, size, tracking=tracking)[1]


def glyph_path(font, ch, size, transform):
    gs = font.getGlyphSet()
    name = font.getBestCmap()[ord(ch)]
    pen = SVGPathPen(gs)
    upm = font["head"].unitsPerEm
    s = size / upm
    a, b, c, d, e, f = transform
    # compose glyph scale (s, -s) with given transform
    tp = TransformPen(pen, (a * s, b * s, -c * s, -d * s, e, f))
    gs[name].draw(tp)
    return pen.getCommands(), gs[name].width * s


def svg(w, h, body, fill):
    defs = f"<defs>{GOLD_DEF}</defs>" if fill == "url(#g)" else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}" role="img" aria-label="Coach Carter">{defs}'
            f'<g fill="{fill}">{body}</g></svg>')


# ---------- Primary wordmark ----------
def wordmark(fill):
    W = 1400
    main = "COACH CARTER"
    size = 150
    trk = 10
    mw = width(cinzel, main, size, trk)
    d_main, _ = text_path(cinzel, main, size, (W - mw) / 2, 230, trk)
    top = "THE REAL"
    tsz, ttrk = 34, 18
    tw = width(barlow, top, tsz, ttrk)
    d_top, _ = text_path(barlow, top, tsz, (W - tw) / 2, 90, ttrk)
    sub = "WINNERS DO ONE THING. WE WIN."
    ssz, strk = 30, 12
    sw = width(barlow, sub, ssz, strk)
    d_sub, _ = text_path(barlow, sub, ssz, (W - sw) / 2, 318, strk)
    # flanking rules beside THE REAL
    ry = 78
    gap = 26
    rules = (f'<rect x="{(W - mw) / 2:.1f}" y="{ry}" width="{(W - tw) / 2 - gap - (W - mw) / 2:.1f}" height="3"/>'
             f'<rect x="{(W + tw) / 2 + gap:.1f}" y="{ry}" width="{(W - tw) / 2 - gap - (W - mw) / 2:.1f}" height="3"/>')
    body = f'<path d="{d_top}"/>{rules}<path d="{d_main}"/><path d="{d_sub}"/>'
    return svg(W, 350, body, fill)


# ---------- Monogram KC split by a court center line ----------
def monogram_body(cx, cy, size, fill_line=True):
    kw = width(cinzel, "K", size)
    cw = width(cinzel, "C", size)
    gap = size * 0.16
    total = kw + gap + cw
    x0 = cx - total / 2
    base = cy + size * 0.35
    dk, _ = text_path(cinzel, "K", size, x0, base)
    dc, _ = text_path(cinzel, "C", size, x0 + kw + gap, base)
    lx = x0 + kw + gap / 2
    line = f'<rect x="{lx - size * 0.012:.1f}" y="{cy - size * 0.62:.1f}" width="{size * 0.024:.1f}" height="{size * 1.24:.1f}"/>' if fill_line else ""
    return f'<path d="{dk}"/><path d="{dc}"/>{line}'


def monogram(fill):
    return svg(400, 400, monogram_body(200, 200, 230), fill)


# ---------- Circular crest ----------
def ring_text(text, cx, cy, r, size, start_deg, sweep_deg, font):
    """Place glyphs along a circle (top arc, reading clockwise)."""
    widths = [width(font, ch, size) for ch in text]
    total = sum(widths)
    spacing = sweep_deg  # fixed tracking in px (sweep_deg reused as tracking)
    arc = total + spacing * (len(text) - 1)
    start_deg = -math.degrees(arc / r) / 2
    out = []
    pos = 0.0
    for ch, w in zip(text, widths):
        mid = pos + w / 2
        ang = math.radians(start_deg) + mid / r  # angle from 12 o'clock clockwise
        px = cx + r * math.sin(ang)
        py = cy - r * math.cos(ang)
        ca, sa = math.cos(ang), math.sin(ang)
        # glyph local origin: baseline at radius, centered horizontally
        ox = px - ca * (w / 2)
        oy = py - sa * (w / 2)
        if ch != " ":
            d, _ = glyph_path(font, ch, size, (ca, sa, -sa, ca, ox, oy))
            out.append(f'<path d="{d}"/>')
        pos += w + spacing
    return "".join(out)


def ring_text_bottom(text, cx, cy, r, size, font):
    """Bottom arc text that reads left-to-right (upright)."""
    widths = [width(font, ch, size) for ch in text]
    total = sum(widths) + 6 * (len(text) - 1)
    out = []
    pos = -total / 2
    for ch, w in zip(text, widths):
        mid = pos + w / 2
        ang = mid / r  # 0 at 6 o'clock, positive to the right
        px = cx + r * math.sin(ang)
        py = cy + r * math.cos(ang)
        ca, sa = math.cos(-ang), math.sin(-ang)
        ox = px - ca * (w / 2)
        oy = py - sa * (w / 2)
        if ch != " ":
            d, _ = glyph_path(font, ch, size, (ca, sa, -sa, ca, ox, oy + size * 0.72 * ca))
            out.append(f'<path d="{d}"/>')
        pos += w + 6
    return "".join(out)


def _top_half_deg():
    t = "THE REAL COACH CARTER"
    tot = sum(width(barlow, ch, 54) for ch in t) + 9 * (len(t) - 1)
    return math.degrees(tot / 312) / 2


def crest(fill):
    S = 800
    c = S / 2
    rings = (f'<path fill-rule="evenodd" d="M{c},{c - 392}a392,392 0 1,1 -0.01,0zM{c},{c - 384}a384,384 0 1,0 0.01,0z"/>'
             f'<path fill-rule="evenodd" d="M{c},{c - 290}a290,290 0 1,1 -0.01,0zM{c},{c - 286}a286,286 0 1,0 0.01,0z"/>')
    top = ring_text("THE REAL COACH CARTER", c, c, 312, 54, 0, 9, barlow)
    bottom = ring_text_bottom("WE WIN", c, c, 308, 50, barlow)
    # small stars at 9 and 3 o'clock between the texts
    def star(x, y, r):
        pts = []
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.42
            pts.append(f"{x + rr * math.cos(a):.1f},{y - rr * math.sin(a):.1f}")
        return f'<polygon points="{" ".join(pts)}"/>'
    half = math.radians(_top_half_deg() + 9)
    stars = star(c - 330 * math.sin(half), c - 330 * math.cos(half) - 0, 13) + star(c + 330 * math.sin(half), c - 330 * math.cos(half), 13)
    mono = monogram_body(c, c - 18, 250)
    est_w = width(barlow, "RICHMOND · 1999", 30, 8)
    d_est, _ = text_path(barlow, "RICHMOND · 1999", 30, c - est_w / 2, c + 205, 8)
    # court arc under monogram
    arc = f'<path d="M{c - 150},{c + 150} Q{c},{c + 112} {c + 150},{c + 150}" fill="none" stroke="{fill}" stroke-width="5"/>'
    body = rings + top + bottom + stars + mono + arc + f'<path d="{d_est}"/>'
    return svg(S, S, body, fill)


def appicon():
    body = monogram_body(256, 262, 190)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            f'<defs>{GOLD_DEF}</defs><rect width="512" height="512" rx="112" fill="#3B1222"/>'
            f'<rect x="10" y="10" width="492" height="492" rx="104" fill="none" stroke="url(#g)" stroke-width="4"/>'
            f'<g fill="url(#g)">{body}</g></svg>')


files = {
    "wordmark_gold.svg": wordmark("url(#g)"),
    "wordmark_white.svg": wordmark("#F5F0E8"),
    "wordmark_black.svg": wordmark("#101216"),
    "crest_gold.svg": crest("url(#g)"),
    "crest_white.svg": crest("#F5F0E8"),
    "monogram_gold.svg": monogram("url(#g)"),
    "monogram_white.svg": monogram("#F5F0E8"),
    "appicon.svg": appicon(),
}
for name, data in files.items():
    (OUT / name).write_text(data)
    print(name, len(data))
