"""Patch 08: investor fact numbers full size; box-office chart on clean $25M ticks."""
from pathlib import Path

R = Path(__file__).resolve().parent.parent
css = R / "site/assets/css/fx.css"
c = css.read_text()
if ".facts b span" not in c:
    css.write_text(c + "\n.facts b span { font: inherit; color: inherit; display: inline; }\n")

p = R / "site/assets/js/investor.js"
s = p.read_text()
old = "const H = top + data.length * rowH + 24; const max = Math.max(...data.map((d) => d.v)) * 1.05;"
new = "const H = top + data.length * rowH + 24; const step = 25; const max = Math.ceil(Math.max(...data.map((d) => d.v)) / step) * step;"
assert old in s
s = s.replace(old, new)
old2 = ('[0, 0.25, 0.5, 0.75, 1].forEach((t) => { const gx = x(max * t / 1.05 * 1.0); el("line", { x1: gx, x2: gx, y1: top, y2: H - 22, stroke: GRID }, svg); '
        'const tx = el("text", { x: gx, y: H - 6, "text-anchor": "middle", class: "ctick" }, svg); tx.textContent = fmtM(max * t / 1.05); });')
new2 = ('for (let v = 0; v <= max; v += step) { const gx = x(v); el("line", { x1: gx, x2: gx, y1: top, y2: H - 22, stroke: GRID }, svg); '
        'const tx = el("text", { x: gx, y: H - 6, "text-anchor": "middle", class: "ctick" }, svg); tx.textContent = v ? "$" + v + "M" : "$0"; }')
assert old2 in s
s = s.replace(old2, new2)
p.write_text(s)
print("patch_08 ok")
