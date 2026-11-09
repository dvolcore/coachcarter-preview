"""Create original concept flats for the Academy catalog. Run from any directory."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "site"
OUT = ROOT / "academy-studio" / "flats"
OUT.mkdir(exist_ok=True)
BONE, MAROON, INK, GOLD = "#ede0c9", "#5c243a", "#23252a", "#b49158"
PAPER = "#f6f0e7"
ARTWORK = ROOT / "academy-studio" / "artwork"
MASTER_MARK = (ARTWORK / "academy_wordmark_descriptor.svg").read_text()

def recolor_mark(mark, color):
    mark = re.sub(r"<defs>.*?</defs>", "", mark, flags=re.DOTALL)
    return mark.replace('fill="url(#g)"', f'fill="{color}"').replace('fill="#F5F0E8"', f'fill="{color}"')

MARK = MASTER_MARK.split(">", 1)[1].rsplit("</svg>", 1)[0]
(ARTWORK / "academy-wordmark-maroon.svg").write_text(recolor_mark(MASTER_MARK, MAROON))
TEE = "M120 37 L75 52 20 126 61 151 86 119 86 260 Q150 266 214 260 L214 119 239 151 280 126 225 52 180 37 Q150 54 120 37 Z"
COLLAR = "M120 37 Q150 92 180 37 M125 38 Q150 81 175 38"
BALL = "M-31 0H31 M0-31V31 M-26-17Q1 0-26 17 M26-17Q-1 0 26 17"

def path(d, fill="none", stroke=INK, width=1.7, dash=""):
    dashed = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dashed}/>'

def ball(x, y, scale, stroke):
    return (f'<g transform="translate({x} {y}) scale({scale})">'
            f'<circle r="31" fill="none" stroke="{stroke}" stroke-width="2.1"/>'
            + path(BALL, stroke=stroke, width=2.1) + "</g>")

def wordmark(x, y, width, color):
    # Reuse the brand-approved shapes, with a single ink for apparel artwork.
    mark = recolor_mark(MARK, color)
    return f'<g transform="translate({x} {y}) scale({width / 80}) translate(-10 -18)">{mark}</g>'

def tee(base, print_color, back=False, kids=False):
    parts = [path(TEE, base), path(COLLAR if not back else "M120 37Q150 59 180 37 M123 39Q150 63 177 39",
             stroke=print_color, width=1), path("M87 251Q150 258 213 251 M24 121L63 144 M276 121L237 144",
             stroke=print_color, width=.65, dash="3 3")]
    if back and not kids:
        parts += [f'<g transform="translate(94 94) scale(1.12)">{ball(50, 44, 1.29, print_color)}{wordmark(20, 95, 60, print_color)}</g>']
    elif kids and not back:
        parts += [ball(150, 134, 1.04, print_color), wordmark(106, 173, 88, print_color)]
    else:
        parts += [wordmark(102, 106, 96, print_color)]
    return "".join(parts)

def short(base, panel, seam, length, hip, back=False, kids=False, high=False):
    waist = 49 if high else 58
    crotch = length - 30
    hem = length
    # Mirrored side inserts cross the hip and converge as they travel toward the hem.
    shell = f"M66 {waist} Q150 {waist-6} 234 {waist} L{hip} {hem} Q202 {hem+10} 155 {hem} L150 {crotch} 145 {hem} Q98 {hem+10} {300-hip} {hem} Z"
    side = f"M67 {waist+14} Q80 {waist+46} 74 {hem-48} Q66 {hem-20} {300-hip+23} {hem+3} L{300-hip} {hem} Z"
    if high:
        side = f"M66 {waist+29} Q87 118 72 {hem-23} L{300-hip+27} {hem+1} L{300-hip} {hem} Q{300-hip+7} {hem-40} 66 {waist+29} Z"
    parts = [path(shell, base)]
    parts += [f'<g transform="{transform}">' + path(side, panel, seam, 2.4) + "</g>"
              for transform in ("translate(0 0)", "translate(300 0) scale(-1 1)")]
    parts += [path(f"M66 {waist} Q150 {waist-6} 234 {waist} L238 {waist+22} Q150 {waist+16} 62 {waist+22} Z", base),
              path(f"M64 {waist+10} Q150 {waist+4} 236 {waist+10}", stroke=seam, width=.8, dash="3 3"),
              path(f"M150 {waist+22}V{crotch}", stroke=seam, width=.7, dash="4 4")]
    if not back:
        parts += [path(f"M96 {waist+34}L87 {waist+68} M204 {waist+34}L213 {waist+68}", stroke=seam),
                  wordmark(165, hem-31, 56, BONE)]
        if not kids and not high:
            parts += [path(f"M146 {waist+14}Q142 {waist+30} 143 {waist+50} M154 {waist+14}Q158 {waist+30} 157 {waist+50}", stroke=seam, width=2)]
    else:
        parts += [path(f"M64 {waist+27} Q150 {waist+43} 236 {waist+27}", stroke=seam, width=.9, dash="4 4")]
    return "".join(parts)

def jersey(back=False):
    shell = "M92 42L119 35Q150 91 181 35L208 42Q205 95 225 118L218 253Q150 262 82 253L75 118Q95 95 92 42Z"
    base, trim = (MAROON, BONE) if back else (BONE, MAROON)
    return (path(shell, base, trim, 6) + path("M92 114L101 254 M208 114L199 254", stroke=trim, width=1.1)
            + wordmark(104, 112, 92, trim) + ball(150, 174, .69, trim))

def board(filename, title, code, front, back, labels, notes):
    columns = "".join(f'<g transform="translate({x} 109)">{art}</g>' for x, art in [(28, front), (364, back)])
    foot = "".join(f'<text x="28" y="{450+22*i}" font-size="13" fill="#4d4542">{note}</text>' for i, note in enumerate(notes))
    body = f"""<title>{title} garment concept board</title>
<rect width="700" height="520" fill="{PAPER}"/>
<g font-family="Arial,sans-serif" fill="{INK}">
<text x="28" y="30" font-size="11" font-weight="bold" letter-spacing="2.5" fill="{MAROON}">COACH CARTER ACADEMY · COLLECTION 01</text>
<text x="28" y="73" font-family="Georgia,serif" font-size="37">{title}</text>
<text x="672" y="29" font-size="12" text-anchor="end">{code} · CONCEPT</text>
<path d="M28 95H672 M28 420H672" stroke="#cfc2b3"/>
{columns}
<text x="178" y="402" text-anchor="middle" font-size="12" letter-spacing="2">{labels[0]}</text>
<text x="514" y="402" text-anchor="middle" font-size="12" letter-spacing="2">{labels[1]}</text>
{foot}</g>"""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 520">{body}</svg>'
    (OUT / (filename + ".svg")).write_text(svg + "\n", encoding="utf-8")

board("court-tee", "Court Tee", "CCA-01-T",
      tee(INK, GOLD), tee(INK, GOLD, True), ("FRONT", "BACK"),
      ("220–260 GSM target · rib collar · straight relaxed body", "Chest wordmark · single-ink basketball back graphic · all placement provisional"))
board("court-short", "Court Short", "CCA-01-S",
      short(MAROON, BONE, GOLD, 253, 249), short(MAROON, BONE, GOLD, 253, 249, True), ("FRONT", "BACK"),
      ("7-inch target · lined mesh · Arc insert · tapered piping", "Pocket mouth sits above Arc curve · verify drawcord and pocket access in motion"))
board("arc-05", "Arc 05", "CCA-02-S",
      short(MAROON, BONE, GOLD, 214, 253, high=True), short(MAROON, BONE, GOLD, 214, 253, True, high=True), ("FRONT", "BACK"),
      ("5-inch target · flat high-rise waist · regraded hip and leg opening", "Verify liner coverage, stride clearance and opacity under side light"))
board("next-up-short", "Next Up Short", "CCA-03-S",
      short(INK, MAROON, GOLD, 232, 243), short(INK, MAROON, GOLD, 232, 243, True), ("FRONT", "BACK"),
      ("6-inch target · relaxed through the leg · adjustable waist", "Carbon and maroon · reinforce pocket corners and test youth size steps"))
board("next-up-jersey", "Next Up Jersey", "CCA-03-J",
      jersey(), jersey(True), ("BONE SIDE", "MAROON SIDE"),
      ("Reversible mesh body · wider shoulder and bound armholes", "Wear-test the reversible seam and trim under a backpack"))
board("first-team", "First Team Set", "CCA-04-SET",
      tee(BONE, MAROON, kids=True), short(MAROON, BONE, GOLD, 204, 241, kids=True), ("TEE FRONT", "SHORT FRONT"),
      ("Bone basketball tee · maroon pull-on mesh short", "Soft inner seams · encased elastic waist · no exposed drawcord"))

signature = f'<svg xmlns="http://www.w3.org/2000/svg" width="10in" height="12in" viewBox="0 0 100 120"><title>Court Tee signature basketball back print</title>{ball(50, 44, 1.29, GOLD)}{wordmark(20, 95, 60, GOLD)}</svg>'
(ARTWORK / "court-tee-signature.svg").write_text(signature + "\n", encoding="utf-8")

# First Whistle tailoring. The basketball geometry repeats as a lining yardage tile.
lining = f"""<rect width="144" height="144" fill="{MAROON}"/>
{path("M0 72H144 M72 0V144 M22 0V31H122V0 M22 144V113H122V144 M48 31a24 24 0 0 0 48 0 M48 113a24 24 0 0 1 48 0", stroke=GOLD, width=1.4)}
<circle cx="72" cy="72" r="25" fill="none" stroke="{GOLD}" stroke-width="1.4"/>"""
(ARTWORK / "first-whistle-lining.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="144" height="144" viewBox="0 0 144 144"><title>First Whistle full-court repeat tile</title>{lining}</svg>\n',
    encoding="utf-8")

def blazer(inside=False):
    shell = "M117 37L64 53Q55 56 51 68L27 236L63 243L80 149L76 256Q150 268 224 256L220 149L237 243L273 236L249 68Q245 56 236 53L183 37Z"
    if inside:
        lining_pattern = f'<defs><pattern id="court-lining" width="144" height="144" patternUnits="userSpaceOnUse">{lining}</pattern></defs>'
        return (lining_pattern + path(shell, MAROON) +
                path("M117 37L86 67L80 148L76 256Q150 268 224 256L220 148L214 67L183 37L150 56Z", "url(#court-lining)", GOLD) +
                wordmark(95, 90, 40, BONE))
    return (path(shell, MAROON) +
            path("M117 37L109 77L123 82L111 93L150 157L136 55Z M183 37L191 77L177 82L189 93L150 157L164 55Z", "#743951") +
            path("M150 157V258 M87 181H125V190H86Z M175 181H213L214 190H175Z M180 117H204", stroke=BONE, width=1.15) +
            '<circle cx="147" cy="174" r="3.3" fill="#e9d4ae"/><circle cx="147" cy="200" r="3.3" fill="#e9d4ae"/>')

def trouser(wide=False):
    end = 249 if wide else 242
    spread = 242 if wide else 223
    shell = f"M90 40H210L{spread} {end}L165 {end}L150 118L135 {end}L{300-spread} {end}Z"
    return (path(shell, INK) + path("M88 58H212 M150 59V92 M104 62L92 92 M196 62L208 92",
            stroke=GOLD, width=1.15) + path(f"M119 68L110 {end-4} M181 68L190 {end-4}",
            stroke="#a69e90", width=.75, dash="4 4"))

def oxford(back=False):
    shell = "M120 44L66 59L26 225L60 235L82 149L80 255Q150 274 220 255L218 149L240 235L274 225L234 59L180 44Z"
    return (path(shell, BONE) + path("M120 44L114 67L136 91L150 72L164 91L186 67L180 44L150 57Z", PAPER) +
            path("M82 73Q150 98 218 73" if back else "M150 74V263 M176 107H206V137H176Z M32 212L64 221 M268 212L236 221",
                 stroke=MAROON, width=1.1) +
            ("" if back else "".join(f'<circle cx="153" cy="{y}" r="1.8" fill="{MAROON}"/>' for y in range(98, 246, 24))))

board("first-whistle-blazer", "First Whistle Blazer", "CCA-FW-B", blazer(), blazer(True), ("EXTERIOR", "OPEN INTERIOR"),
      ("Soft two-button sports coat · natural shoulder · working patch pockets", "Court Map lining reveal · wear-test with a backpack and on the team bus"))
board("first-whistle-trouser", "First Whistle Trouser", "CCA-FW-P", trouser(), trouser(True), ("YOUTH STRAIGHT", "TEEN PLEATED WIDE"),
      ("Youth flat-front straight leg · teen easy-rise wide leg with one front pleat", "Hidden waist adjustment · separate inseam fit · hem to skim a court sneaker"))
board("first-whistle-oxford", "First Whistle Oxford", "CCA-FW-O", oxford(), oxford(True), ("FRONT", "BACK"),
      ("Bone cotton oxford · room through shoulder · short curved hem", "Test tucked and untucked · soft collar for optional tie · tone-on-tone cuff mark"))
