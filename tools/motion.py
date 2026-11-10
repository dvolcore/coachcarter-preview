"""Motion plates — code-authored motion graphics (SVG + CSS, no video files).

A plate is a dark title card that opens a store department: kinetic type on the left,
an animated scene on the right, and the department's section links underneath.
Scenes play when scrolled into view and pause off screen (assets/js/motion.js).

Used by shell.py: `plate(key, no, title_lines, blurb, links)` returns the markup.
"""
from html import escape

# --------------------------------------------------------------------------- scenes
# Every scene is a 640x400 SVG. Classes: d = stroke draws in, p = pops in, f = fades in.
# --i sets the order (each step = 90 ms).

SEAL = '''<svg viewBox="0 0 640 400" class="sc sc-seal">
  <defs><path id="seal-ring" d="M320 200 m-128 0 a128 128 0 1 1 256 0 a128 128 0 1 1 -256 0"/></defs>
  <g class="tape">
    <path class="d" style="--i:0;--t:1.6s" pathLength="1" d="M24 356 H616"/>
    <g class="ticks f" style="--i:6"><path d="M40 356v-10M80 356v-16M120 356v-10M160 356v-16M200 356v-10M240 356v-16M280 356v-10M320 356v-16M360 356v-10M400 356v-16M440 356v-10M480 356v-16M520 356v-10M560 356v-16M600 356v-10"/></g>
    <g class="marker"><path d="M0 338 l7 -12 h-14z"/></g>
  </g>
  <circle class="d" style="--i:1;--t:1.5s" pathLength="1" cx="320" cy="200" r="150"/>
  <circle class="stitch spin-slow" cx="320" cy="200" r="139"/>
  <g class="spin-rev"><text class="ring-text"><textPath href="#seal-ring" startOffset="0" textLength="796" lengthAdjust="spacing">COACH CARTER ACADEMY  ·  CLASS IS IN SESSION  ·  FRONT ROW  ·  RICHMOND  ·  </textPath></text></g>
  <circle class="d" style="--i:4;--t:1.2s" pathLength="1" cx="320" cy="200" r="104"/>
  <image class="p" style="--i:7" href="assets/brand/monogram_gold.svg" x="250" y="130" width="140" height="140"/>
  <g class="pennant" style="--i:9">
    <path class="pole d" style="--i:3" pathLength="1" d="M92 70 V250"/>
    <g class="flag f" style="--i:8"><path d="M94 78 L214 106 L94 134 Z"/><text x="104" y="112">FRONT ROW</text></g>
  </g>
  <g class="chev">
    <path class="p" style="--i:10" d="M508 96 l22 22 -22 22"/><path class="p" style="--i:11" d="M534 96 l22 22 -22 22"/><path class="p" style="--i:12" d="M560 96 l22 22 -22 22"/>
  </g>
  <g class="star p" style="--i:13"><path d="M545 268 l6 14 15 1 -12 10 4 15 -13 -8 -13 8 4 -15 -12 -10 15 -1z"/></g>
</svg>'''

COURT = '''<svg viewBox="0 0 640 400" class="sc sc-court">
  <rect class="d" style="--i:0;--t:1.8s" pathLength="1" x="30" y="30" width="580" height="340"/>
  <path class="d" style="--i:3" pathLength="1" d="M30 152 A48 48 0 0 1 30 248"/>
  <path class="d" style="--i:4;--t:1.6s" pathLength="1" d="M610 62 H520 A138 138 0 0 0 520 338 H610"/>
  <rect class="d" style="--i:6" pathLength="1" x="450" y="152" width="160" height="96"/>
  <circle class="d" style="--i:8" pathLength="1" cx="450" cy="200" r="48"/>
  <path class="d board" style="--i:10" pathLength="1" d="M576 174 V226"/>
  <circle class="d rim" style="--i:11" pathLength="1" cx="560" cy="200" r="10"/>
  <circle class="swish" cx="560" cy="200" r="10"/>
  <path class="run d" style="--i:16;--t:1s" pathLength="1" d="M372 296 C 440 300, 480 250, 540 210"/>
  <path class="arrow p" style="--i:22" d="M528 206 l14 3 -9 11z"/>
  <path class="pass d" style="--i:18;--t:.7s" pathLength="1" d="M162 240 L290 120"/>
  <path class="pass d" style="--i:21;--t:.9s" pathLength="1" d="M312 114 Q 440 110 548 194"/>
  <g class="o"><circle class="p" style="--i:12" cx="150" cy="250" r="13"/><circle class="p" style="--i:13" cx="300" cy="110" r="13"/><circle class="p" style="--i:14" cx="360" cy="300" r="13"/></g>
  <g class="x"><path class="p" style="--i:13" d="M202 227 l16 16 m0 -16 l-16 16"/><path class="p" style="--i:14" d="M324 144 l16 16 m0 -16 l-16 16"/><path class="p" style="--i:15" d="M472 207 l16 16 m0 -16 l-16 16"/></g>
  <circle class="ball" r="7.5"/>
  <g class="board-score f" style="--i:5">
    <rect x="52" y="52" width="150" height="62" rx="4"/>
    <text class="lb" x="68" y="72">HOME</text><text class="lb" x="150" y="72">AWAY</text>
    <svg x="62" y="76" width="62" height="34" viewBox="0 0 62 34"><g class="roll"><text x="4" y="27">11</text><text x="4" y="61">12</text><text x="4" y="95">13</text></g></svg>
    <text class="n" x="124" y="103">–</text><text class="n" x="156" y="103">0</text>
  </g>
</svg>'''

STRIP_IMAGES = [
    "assets/img/academy/campaign/signature-court.webp",
    "assets/img/academy/campaign/team-off-the-bus.webp",
    "assets/img/academy/campaign/front-row-opening-night.webp",
    "assets/img/academy/campaign/signature-library.webp",
    "assets/img/academy/campaign/after-hours-stage.webp",
    "assets/img/academy/campaign/warm-up-court.webp",
]


def _strip():
    frames, holes = [], []
    for i, src in enumerate(STRIP_IMAGES):
        x = 20 + i * 172
        frames.append(f'<g class="fr"><image data-href="{src}" x="{x}" y="118" width="156" height="164" preserveAspectRatio="xMidYMid slice"/>'
                      f'<rect x="{x}" y="118" width="156" height="164"/><text x="{x + 6}" y="300">{i + 1:02d}A</text></g>')
    for i in range(40):
        x = 14 + i * 26.6
        holes.append(f'<rect x="{x:.1f}" y="92" width="14" height="12" rx="2.5"/><rect x="{x:.1f}" y="308" width="14" height="12" rx="2.5"/>')
    return f'''<svg viewBox="0 0 640 400" class="sc sc-strip">
  <g class="tilt"><g class="drift">
    <rect class="film" x="-40" y="84" width="1140" height="244"/>
    <g class="holes">{"".join(holes)}</g>
    {"".join(frames)}
    <path class="grease d" style="--i:10;--t:1s" pathLength="1" d="M356 108 C 420 96, 536 104, 534 198 C 532 300, 420 304, 366 292 C 330 282, 330 132, 372 112"/>
    <path class="grease d" style="--i:18;--t:.5s" pathLength="1" d="M420 62 l12 14 l28 -30"/>
    <text class="sel f" style="--i:20" x="470" y="72">SELECT</text>
  </g></g>
</svg>'''


CONTRACT = '''<svg viewBox="0 0 640 400" class="sc sc-contract">
  <g class="sheet">
    <rect class="paper f" style="--i:0" x="150" y="26" width="340" height="348" rx="3"/>
    <text class="h f" style="--i:3" x="320" y="76">THE CONTRACT</text>
    <path class="rule d" style="--i:4" pathLength="1" d="M190 92 H450"/>
    <g class="terms">
      <g class="f" style="--i:6"><rect x="190" y="116" width="15" height="15"/><text x="218" y="129">2.3 GPA, EVERY SEMESTER</text></g>
      <path class="tick d" style="--i:9;--t:.35s" pathLength="1" d="M192 123 l5 6 l10 -13"/>
      <g class="f" style="--i:8"><rect x="190" y="148" width="15" height="15"/><text x="218" y="161">FRONT ROW, EVERY CLASS</text></g>
      <path class="tick d" style="--i:12;--t:.35s" pathLength="1" d="M192 155 l5 6 l10 -13"/>
      <g class="f" style="--i:10"><rect x="190" y="180" width="15" height="15"/><text x="218" y="193">TEN HOURS OF STUDY A WEEK</text></g>
      <path class="tick d" style="--i:15;--t:.35s" pathLength="1" d="M192 187 l5 6 l10 -13"/>
      <g class="f" style="--i:12"><rect x="190" y="212" width="15" height="15"/><text x="218" y="225">COAT AND TIE ON GAME DAY</text></g>
      <path class="tick d" style="--i:18;--t:.35s" pathLength="1" d="M192 219 l5 6 l10 -13"/>
    </g>
    <path class="rule d" style="--i:16" pathLength="1" d="M190 318 H380"/>
    <text class="lbl f" style="--i:17" x="190" y="336">SIGNED</text>
    <path class="sig d" style="--i:21;--t:1.9s" pathLength="1" d="M198 300 c 6 -30 14 -44 20 -44 c 8 0 -10 52 -14 56 c 14 -30 30 -40 34 -30 c 4 10 -14 22 -18 22 c 16 2 22 10 34 8 c 12 -2 18 -22 30 -22 c -10 0 -16 20 -6 22 c 10 2 16 -18 22 -20 c -2 10 2 20 10 18 c 10 -2 12 -18 20 -18 c 6 0 2 18 10 18 c 10 0 14 -30 20 -44 c -6 20 -6 44 6 44 c 8 0 12 -8 20 -12"/>
    <g class="seal p" style="--i:36"><circle cx="430" cy="300" r="40"/><circle class="in" cx="430" cy="300" r="32"/><text x="430" y="297">WE</text><text x="430" y="315">WIN</text></g>
  </g>
</svg>'''

LEADER = '''<svg viewBox="0 0 640 400" class="sc sc-leader">
  <rect class="gate d" style="--i:0;--t:1.4s" pathLength="1" x="60" y="30" width="520" height="340"/>
  <path class="cross d" style="--i:2" pathLength="1" d="M60 200 H580"/><path class="cross d" style="--i:3" pathLength="1" d="M320 30 V370"/>
  <circle class="wedge" cx="320" cy="200" r="74"/>
  <circle class="d" style="--i:4;--t:1.2s" pathLength="1" cx="320" cy="200" r="148"/>
  <circle class="d" style="--i:6;--t:1.2s" pathLength="1" cx="320" cy="200" r="126"/>
  <g class="count"><text class="n n3" x="320" y="246">3</text><text class="n n2" x="320" y="246">2</text><text class="n n1" x="320" y="246">1</text>
    <g class="play"><circle class="pulse" cx="320" cy="200" r="60"/><path d="M298 164 v72 l62 -36z"/></g></g>
  <g class="scratch"><path d="M148 30 V370"/><path d="M471 30 V370"/><path d="M233 30 V370"/></g>
  <text class="slate f" style="--i:8" x="76" y="56">SEASON ONE</text><text class="slate f r" style="--i:9" x="564" y="56">FREE PREVIEW · 0:60</text>
  <text class="slate f" style="--i:10" x="76" y="354">COACH CARTER ACADEMY</text><text class="slate f r" style="--i:11" x="564" y="354">REEL 01</text>
</svg>'''


def _cards():
    out = []
    for r in range(5):
        for c in range(5):
            i = r * 5 + c
            x, y = 96 + c * 92, 22 + r * 58
            out.append(f'<g class="card p" style="--i:{i}"><rect x="{x}" y="{y}" width="80" height="46" rx="3"/>'
                       f'<path class="ln" d="M{x + 10} {y + 13} h34 M{x + 10} {y + 23} h46 M{x + 10} {y + 33} h26"/></g>'
                       f'<path class="ck d" style="--i:{i + 14};--t:.3s" pathLength="1" d="M{x + 56} {y + 28} l5 6 l11 -15"/>')
    return f'''<svg viewBox="0 0 640 400" class="sc sc-cards">
  {"".join(out)}
  <path class="bar d" style="--i:16;--t:2.6s" pathLength="1" d="M96 340 H544"/>
  <text class="tl f" style="--i:10" x="96" y="376">COMMITMENT CARDS SIGNED</text>
  <text class="tn f" style="--i:10" x="544" y="384"><tspan data-tally="25">25</tspan><tspan class="of"> / 25</tspan></text>
</svg>'''


SCENES = {"seal": SEAL, "court": COURT, "strip": _strip(), "contract": CONTRACT, "leader": LEADER, "cards": _cards()}


def plate(key, scene, no, lines, blurb, links, label):
    """One department title plate. `lines` = the title, one string per line (last line goes gold)."""
    words = "".join(f'<span class="w{" gold" if i == len(lines) - 1 and len(lines) > 1 else ""}" style="--i:{i}"><i>{escape(l)}</i></span>'
                    for i, l in enumerate(lines))
    chips = "".join(f'<a href="{href}">{escape(text)}</a>' for text, href in links)
    return f'''<div class="plate plate--{scene}" id="dept-{key}" data-plate>
  <div class="plate-fx" aria-hidden="true"></div>
  <div class="plate-copy">
    <p class="plate-k"><span>Department {no}</span></p>
    <h2 class="plate-t"><span class="sr">{escape(label)}</span><span aria-hidden="true">{words}</span></h2>
    <p class="plate-d">{escape(blurb)}</p>
    <nav class="plate-links" aria-label="{escape(label)} sections">{chips}</nav>
  </div>
  <div class="plate-art" aria-hidden="true">{SCENES[scene]}</div>
</div>'''
