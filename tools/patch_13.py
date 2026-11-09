"""Patch 13: film polish — quote band gets the scene still, real-life rows tightened, curated premiere photos."""
from pathlib import Path
R = Path(__file__).resolve().parent.parent
C = R / "site/assets/css/fx.css"
css = C.read_text()
M = "/* ---- the 2005 film · polish ---- */"
if M not in css:
    css += "\n" + M + r"""
.fq.has-still { grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr); column-gap: clamp(28px, 5vw, 80px); align-items: center; }
.fq.has-still > :not(.fq-still) { grid-column: 1; }
.fq-still { grid-column: 2; grid-row: 1 / span 3; position: relative; width: 100%; padding: 0; border: 1px solid var(--line); border-radius: 18px; overflow: hidden; aspect-ratio: 2.38 / 1; background: #000; cursor: pointer; box-shadow: 0 30px 80px -30px rgba(0,0,0,.8); }
.fq-still img { width: 100%; height: 100%; object-fit: cover; transform: scale(1.04); transition: transform 7s linear; }
.fq.on .fq-still img { transform: scale(1.12); }
.fq-still .fplay { position: absolute; left: 16px; bottom: 14px; }
@media (max-width: 860px) { .fq.has-still { grid-template-columns: 1fr; } .fq-still { grid-column: 1; grid-row: auto; } }
@media (prefers-reduced-motion: reduce) { .fq-still img, .fq.on .fq-still img { transition: none; transform: none; } }
.fr-row { grid-template-columns: 52px 1fr auto; }
.fr-n { font: 600 28px/1 var(--f-head); color: var(--gold); padding-top: 2px; }
.fr-row p { max-width: 70ch; }
.fr-film { color: var(--slate) !important; font-size: 14.5px; }
.fr-film b { color: var(--gold-hi); font-weight: 600; }
@media (max-width: 800px) { .fr-row { grid-template-columns: 40px 1fr; } .fr-row nav { grid-column: 2; } }
.ft-over .eyebrow { margin-bottom: 4px; }
"""
M2 = "/* ---- the 2005 film · mobile trailer ---- */"
if M2 not in css:
    css += "\n" + M2 + r"""
@media (max-width: 900px) { .ftrailer { aspect-ratio: 2.39 / 1; } }
@media (max-width: 600px) { .ft-over .eyebrow { display: none; } .ft-over { padding: 14px 16px; gap: 2px; } .ft-over b { font-size: 30px; } .ft-cta { font-size: 11px; gap: 8px; letter-spacing: .14em; } .ft-cta .fplay { width: 34px; height: 34px; } }
"""
    C.write_text(css)

a = R / "src/archive.html"; s = a.read_text()
s = s.replace('data-film="premiere" data-n="9"', 'data-film="premiere" data-ids="108766375,109967051,51962764,51962751,524780360,51962883"')
a.write_text(s)
print("patch_13 ok")
