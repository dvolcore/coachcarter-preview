"""Print artwork for merch/product references (outlined text, transparent PNG via rsvg-convert).
Usage: python3 tools/make_prints.py <outdir>"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_logos as L  # noqa: E402  (rebuilds logos identically as a side effect)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT.mkdir(parents=True, exist_ok=True)
GOLD = "#D4AF6A"
CHALK = "#F5F0E8"
INK = "#1B1B1F"
MAROON = "#541D30"


def centered(font, text, size, y, W, trk=0):
    w = L.width(font, text, size, trk)
    d, _ = L.text_path(font, text, size, (W - w) / 2, y, trk)
    return d


def write(name, w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{rect}{body}</svg>'
    p = OUT / f"{name}.svg"
    p.write_text(svg)
    subprocess.run(["rsvg-convert", "-w", str(w * 2), str(p), "-o", str(OUT / f"{name}.png")], check=True)
    print("wrote", name)


# 1. WE WIN tee print
W = 1200
body = (f'<g fill="{GOLD}"><path d="{centered(L.barlow, "WE WIN", 300, 300, W, 8)}"/>'
        f'<path d="{centered(L.barlow, "WINNERS DO ONE THING", 64, 420, W, 26)}"/></g>')
write("print_tee_wewin", W, 470, body)

# 2. Hoodie: I SIGNED / THE CONTRACT
body = (f'<g fill="{GOLD}"><path d="{centered(L.barlow, "I SIGNED", 240, 250, W, 10)}"/>'
        f'<path d="{centered(L.barlow, "THE CONTRACT", 96, 380, W, 34)}"/></g>')
write("print_hoodie_contract", W, 420, body)

# 3. Cap: flat gold monogram for embroidery
write("print_cap_monogram", 600, 600, f'<g fill="{GOLD}">{L.monogram_body(300, 300, 340)}</g>')

# 4. Contract card (Team Pack insert), 5x7 at 140 dpi-ish
W, H = 1000, 1400
lines = ["I KEEP MY GRADES ABOVE THE LINE.", "I SIT IN THE FRONT ROW.", "I PUT IN THE HOURS NOBODY SEES.", "I RESPECT MY TEAMMATES, MY TEACHERS AND MYSELF."]
parts = [f'<rect x="40" y="40" width="{W-80}" height="{H-80}" fill="none" stroke="{MAROON}" stroke-width="4"/>',
         f'<rect x="56" y="56" width="{W-112}" height="{H-112}" fill="none" stroke="{MAROON}" stroke-width="1.5"/>',
         f'<g fill="{MAROON}">{L.monogram_body(W/2, 200, 140)}</g>',
         f'<path fill="{INK}" d="{centered(L.cinzel, "THE CONTRACT", 92, 420, W, 6)}"/>',
         f'<path fill="{MAROON}" d="{centered(L.barlow, "BETWEEN ME AND MY STANDARD", 34, 480, W, 12)}"/>']
y = 600
for i, t in enumerate(lines, 1):
    size = 36 if len(t) < 40 else 30
    d, _ = L.text_path(L.barlow, f"{i}.  {t}", size, 110, y, 2)
    parts.append(f'<path fill="{INK}" d="{d}"/>')
    parts.append(f'<rect x="110" y="{y+28}" width="{W-220}" height="1.5" fill="{MAROON}" opacity=".35"/>')
    y += 120
parts.append(f'<rect x="110" y="1180" width="480" height="3" fill="{INK}"/>')
d, _ = L.text_path(L.barlow, "SIGNED", 28, 110, 1225, 8)
parts.append(f'<path fill="{MAROON}" d="{d}"/>')
parts.append(f'<rect x="660" y="1180" width="230" height="3" fill="{INK}"/>')
d, _ = L.text_path(L.barlow, "DATE", 28, 660, 1225, 8)
parts.append(f'<path fill="{MAROON}" d="{d}"/>')
parts.append(f'<path fill="{MAROON}" d="{centered(L.barlow, "COACH KEN CARTER · WE WIN", 26, 1300, W, 10)}"/>')
write("print_contract_card", W, H, "".join(parts), bg=CHALK)
