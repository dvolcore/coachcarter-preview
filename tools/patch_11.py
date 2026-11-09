"""Patch 11: investor memo v2 — JS fixes (comps list, revival band 29–39, seg aria) + CSS for memo components."""
from pathlib import Path
R = Path(__file__).resolve().parent.parent
J = R / "site/assets/js/investor.js"
s = J.read_text()
old_band = 'el("rect", { x: x(22), y: top - 4, width: x(39) - x(22), height: H - top - 26, fill: "rgba(184,130,46,.08)" }, svg);\n    txt(svg, (x(22) + x(39)) / 2, H - 30 + 0, "", "ctick", "middle");'
if old_band in s:
    s = s.replace(old_band, 'el("rect", { x: x(29), y: top - 4, width: x(39) - x(29), height: H - top - 26, fill: "rgba(184,130,46,.08)" }, svg);')
old_seg = '$$(".seg button", w).forEach((x) => x.classList.toggle("on", x === b)); draw();'
if old_seg in s:
    s = s.replace(old_seg, '$$(".seg button", w).forEach((x) => { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", String(x === b)); }); draw();')
old_tw = '    const tw = $("#testimonials");'
if 'const cw = $("#comps")' not in s:
    assert old_tw in s
    s = s.replace(old_tw, '''    const cw = $("#comps");
    if (cw && m.comps) cw.innerHTML = m.comps.map((c) => `<a class="comp" href="${c.url}" target="_blank" rel="noopener"><b>${c.name}</b><span>${c.value}</span></a>`).join("");
    const tw = $("#testimonials");''', 1)
J.write_text(s)

C = R / "site/assets/css/fx.css"
css = C.read_text()
marker = "/* ---- investor memo v2 ---- */"
if marker not in css:
    css += "\n" + marker + r"""
.inv-hero .kpis { max-width: 1100px; }
.thesis { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 22px; overflow: hidden; }
.thesis > div { background: #14161b; padding: 28px 24px 30px; display: grid; align-content: start; gap: 10px; }
.thesis .tn { font: 600 13px/1 var(--f-head); letter-spacing: .22em; color: var(--gold); }
.thesis h4 { margin: 0; font: 600 24px/1.02 var(--f-head); text-transform: uppercase; }
.thesis p { margin: 0; color: rgba(245,240,232,.74); font-size: 14.5px; line-height: 1.55; }
@media (max-width: 1100px) { .thesis { grid-template-columns: repeat(2, 1fr); } .thesis > div:last-child { grid-column: 1 / -1; } }
@media (max-width: 600px) { .thesis { grid-template-columns: 1fr; } }
.seg { display: inline-flex; padding: 3px; border-radius: 999px; border: 1px solid var(--line-strong); background: rgba(8,9,11,.5); }
.seg button { appearance: none; border: 0; background: transparent; color: var(--slate); padding: 8px 14px; border-radius: 999px; font: 600 12px/1 var(--f-head); letter-spacing: .16em; text-transform: uppercase; cursor: pointer; transition: background .25s, color .25s; }
.seg button.on { background: var(--gold); color: #101216; }
.seg button:focus-visible { outline: 2px solid var(--gold-hi); outline-offset: 2px; }
.chart-card header .flex { gap: 10px; align-items: center; }
.ticks { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.ticks li { position: relative; padding-left: 26px; color: rgba(245,240,232,.8); line-height: 1.55; }
.ticks li::before { content: ""; position: absolute; left: 0; top: .7em; width: 12px; height: 2px; background: var(--gold); }
.ticks b { color: var(--chalk); }
.missed { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; }
.mrow { display: grid; grid-template-columns: 1.3fr .6fr 1.3fr 1.5fr; gap: 16px; padding: 15px 22px; border-top: 1px solid var(--line); font-size: 14.5px; color: rgba(245,240,232,.78); }
.mrow span:first-child { color: var(--chalk); font-weight: 600; }
.mrow span:last-child { color: var(--gold-hi); }
.mrow.mhead { border-top: 0; background: rgba(184,130,46,.08); font: 600 11px/1.2 var(--f-head); letter-spacing: .2em; text-transform: uppercase; }
.mrow.mhead span { color: var(--gold) !important; font-weight: 600; }
@media (max-width: 760px) { .mrow { grid-template-columns: 1fr auto; gap: 6px 14px; } .mrow.mhead { display: none; } .mrow span:nth-child(2) { text-align: right; color: var(--slate); } .mrow span:nth-child(3) { grid-column: 1 / -1; color: var(--slate); } .mrow span:last-child { grid-column: 1 / -1; } .mrow span:last-child::before { content: "→ "; } }
.edge-list { display: grid; gap: 0; border-top: 1px solid var(--line); }
.edge-list > div { display: grid; gap: 6px; padding: 18px 0; border-bottom: 1px solid var(--line); }
.edge-list b { font: 600 22px/1 var(--f-head); text-transform: uppercase; color: var(--chalk); }
.edge-list span { color: var(--slate); font-size: 14.5px; }
.engines { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.engines > div { position: relative; padding: 30px 28px; border-radius: 22px; background: linear-gradient(180deg, rgba(184,130,46,.10), rgba(184,130,46,0) 60%), var(--carbon-2); border: 1px solid var(--line); overflow: hidden; }
.engines > div::after { content: ""; position: absolute; inset: 0 0 auto; height: 2px; background: var(--gold-sheen); opacity: .7; }
.engines h4 { margin: 10px 0 14px; font: 600 28px/1 var(--f-head); text-transform: uppercase; }
.engines ul { margin: 0; padding-left: 18px; display: grid; gap: 8px; color: rgba(245,240,232,.8); font-size: 14.5px; }
@media (max-width: 900px) { .engines { grid-template-columns: 1fr; } }
.comps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.comp { display: grid; gap: 6px; align-content: start; padding: 18px 20px; border-radius: 16px; border: 1px solid var(--line); background: var(--carbon-2); transition: border-color .3s, transform .3s; }
.comp:hover { border-color: var(--gold); transform: translateY(-2px); }
.comp b { font: 600 17px/1.1 var(--f-head); letter-spacing: .04em; text-transform: uppercase; color: var(--chalk); }
.comp span { color: var(--gold-hi); font-size: 14px; }
@media (max-width: 1000px) { .comps { grid-template-columns: 1fr 1fr; } }
@media (max-width: 520px) { .comps { grid-template-columns: 1fr; } }
.note-card { padding: 28px; border-radius: 20px; border: 1px solid var(--line); background: var(--carbon-2); }
.note-card h4 { margin: 0 0 10px; font: 600 22px/1 var(--f-head); text-transform: uppercase; color: var(--gold-hi); }
.note-card p { margin: 0; color: rgba(245,240,232,.8); line-height: 1.6; }
.phases { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.phases > div { display: flex; flex-direction: column; padding: 26px 24px; border-radius: 20px; background: #14161b; border: 1px solid var(--line); position: relative; }
.phases > div::before { content: ""; position: absolute; top: 0; left: 24px; right: 24px; height: 2px; background: var(--gold); opacity: .6; }
.phases h4 { margin: 12px 0 12px; font: 600 34px/1 var(--f-head); text-transform: uppercase; }
.phases ul { margin: 0 0 18px; padding-left: 18px; display: grid; gap: 7px; color: rgba(245,240,232,.8); font-size: 14px; }
.phases .gate { margin: auto 0 0; padding-top: 14px; border-top: 1px dashed var(--line-strong); font-size: 13.5px; color: var(--slate); }
.phases .gate b { color: var(--gold-hi); font: 600 12px/1 var(--f-head); letter-spacing: .18em; text-transform: uppercase; margin-right: 4px; }
@media (max-width: 1100px) { .phases { grid-template-columns: 1fr 1fr; } }
@media (max-width: 600px) { .phases { grid-template-columns: 1fr; } }
.risks { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 20px; overflow: hidden; }
.risks > div { background: var(--carbon); padding: 22px 24px; display: grid; gap: 6px; }
.risks b { font: 600 18px/1 var(--f-head); letter-spacing: .06em; text-transform: uppercase; color: var(--gold-hi); }
.risks span { color: rgba(245,240,232,.78); font-size: 14.5px; line-height: 1.55; }
@media (max-width: 760px) { .risks { grid-template-columns: 1fr; } }
.disclaimer { font-size: 12px; line-height: 1.6; color: rgba(245,240,232,.5); max-width: 100ch; border-top: 1px solid var(--line); padding-top: 18px; }
.film-slot:empty { display: none; }
"""
    C.write_text(css)
print("patch_11 ok")
