/* Investor memo charts. Every chart: hover tooltip + table view. Data: assets/data/memo.json + investor.json */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const base = document.querySelector('script[src*="investor.js"]').src.replace(/assets\/js\/investor\.js.*$/, "");
  const NS = "http://www.w3.org/2000/svg";
  const GOLD = "#B8822E", CONTEXT = "#3A3E47", GRID = "rgba(245,240,232,.08)";
  const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent && parent.appendChild(e); return e; };
  const txt = (parent, x, y, s, cls, anchor = "start") => { const t = el("text", { x, y, class: cls, "text-anchor": anchor }, parent); t.textContent = s; return t; };
  const barR = (x, y, w, h, r) => { r = Math.min(r, w / 2, h / 2); return `M${x},${y}h${w - r}a${r},${r} 0 0 1 ${r},${r}v${h - 2 * r}a${r},${r} 0 0 1 -${r},${r}h-${w - r}z`; };
  const colR = (x, y, w, h, r) => { r = Math.min(r, w / 2, h / 2); return `M${x},${y + h}v-${h - r}a${r},${r} 0 0 1 ${r},-${r}h${w - 2 * r}a${r},${r} 0 0 1 ${r},${r}v${h - r}z`; };
  const M = (v) => (v === 0 ? "$0" : v >= 1000 ? `$${(v / 1000).toFixed(v % 1000 ? 2 : 0).replace(/\.?0+$/, "")}B` : v >= 1 ? `$${v % 1 ? v.toFixed(1) : v}M` : `$${Math.round(v * 1000)}K`);
  const K = (v) => `$${v}K`;

  const tip = document.createElement("div"); tip.className = "ctip"; tip.setAttribute("role", "status"); document.body.appendChild(tip);
  const show = (e, html) => { tip.innerHTML = html; tip.classList.add("on"); const x = Math.min(innerWidth - tip.offsetWidth - 12, e.clientX + 14); tip.style.transform = `translate(${x}px,${Math.max(8, e.clientY - tip.offsetHeight - 14)}px)`; };
  const hide = () => tip.classList.remove("on");
  const hover = (node, html, mark) => { node.addEventListener("pointermove", (e) => { mark && mark.setAttribute("opacity", ".8"); show(e, html); }); node.addEventListener("pointerleave", () => { mark && mark.removeAttribute("opacity"); hide(); }); };
  const table = (wrap, head, rows) => {
    const btn = $(".ctoggle", wrap); const t = $(".ctable", wrap); if (!t) return;
    t.innerHTML = `<table><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    if (btn && !btn.dataset.bound) { btn.dataset.bound = 1; btn.addEventListener("click", () => { const on = wrap.classList.toggle("show-table"); btn.textContent = on ? "Show chart" : "Show table"; btn.setAttribute("aria-pressed", String(on)); }); }
  };
  const mount = (wrap, H) => { const box = $(".cbody", wrap); const W = Math.max(320, box.clientWidth || 700); const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", height: H, role: "img", "aria-label": wrap.dataset.title || "" }); box.innerHTML = ""; box.appendChild(svg); return { svg, W }; };
  const redraw = (fn) => { fn(); let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(fn, 150); }); };

  /* narrow screens: labels sit above the marks, alternate tick labels hidden */
  const narrow = (wrap) => ($(".cbody", wrap).clientWidth || 700) < 560;
  const tickLbl = (nar, i) => !nar || i % 2 === 0;

  /* horizontal bars with highlight */
  function hbars(wrap, rows, { fmt = M, highlight, step }) {
    const nar = narrow(wrap); const lab = nar ? 16 : 0; const rowH = 32 + lab, top = 6, padR = 70; const H = top + rows.length * rowH + 26;
    const { svg, W } = mount(wrap, H); const padL = nar ? 2 : Math.min(230, W * 0.36);
    const max = Math.ceil(Math.max(...rows.map((r) => r.v)) / step) * step; const x = (v) => padL + (v / max) * (W - padL - padR);
    for (let v = 0, i = 0; v <= max; v += step, i++) { el("line", { x1: x(v), x2: x(v), y1: top, y2: H - 22, stroke: GRID }, svg); tickLbl(nar, i) && txt(svg, x(v), H - 6, v ? fmt(v) : "$0", "ctick", "middle"); }
    rows.forEach((r, i) => {
      const y = top + i * rowH + 6 + lab; const hl = r.label === highlight || r.hl; const w = Math.max(2, x(r.v) - padL);
      if (nar) txt(svg, padL, y - 5, r.label, hl ? "clabel strong" : "clabel");
      else txt(svg, padL - 12, y + 14, r.label.length > 30 ? r.label.slice(0, 29) + "…" : r.label, hl ? "clabel strong" : "clabel", "end");
      const p = el("path", { d: barR(padL, y, w, 20, 4), fill: hl ? GOLD : CONTEXT, class: "cmark" }, svg);
      txt(svg, padL + w + 8, y + 14, fmt(r.v), hl ? "cvalue strong" : "cvalue");
      hover(el("rect", { x: 0, y: y - 6 - lab, width: W, height: rowH, fill: "transparent" }, svg), r.tip || `<b>${r.label}</b><br>${fmt(r.v)}`, p);
    });
  }

  /* range bars (lo–hi), optional log scale */
  function ranges(wrap, rows, { fmt = M, max, min = 0, log = false, ticks, highlight }) {
    const nar = narrow(wrap); const hasSub = rows.some((r) => r.sub);
    const lab = nar ? (hasSub ? 32 : 18) : 0; const rowH = (hasSub && !nar ? 44 : 36) + lab, top = 8, padR = nar ? 92 : 96; const H = top + rows.length * rowH + 26;
    const { svg, W } = mount(wrap, H); const padL = nar ? 8 : Math.min(260, W * 0.4);
    const x = log ? (v) => padL + (Math.log10(Math.max(v, min)) - Math.log10(min)) / (Math.log10(max) - Math.log10(min)) * (W - padL - padR)
                  : (v) => padL + (Math.min(v, max) / max) * (W - padL - padR);
    ticks.forEach((t, i) => { el("line", { x1: x(t), x2: x(t), y1: top, y2: H - 22, stroke: GRID }, svg); tickLbl(nar, i) && txt(svg, x(t), H - 6, t ? fmt(t) : "$0", "ctick", "middle"); });
    rows.forEach((r, i) => {
      const y = top + i * rowH + 12 + lab; const hl = r.hl || r.label === highlight; const c = hl ? GOLD : r.muted ? "#5A5E66" : "#8A6A3A";
      if (nar) { txt(svg, 0, y - lab + 2, r.label, hl ? "clabel strong" : "clabel"); r.sub && txt(svg, 0, y - lab + 17, r.sub, "ctick"); }
      else { txt(svg, padL - 12, y + 4, r.label, hl ? "clabel strong" : "clabel", "end"); r.sub && txt(svg, padL - 12, y + 19, r.sub, "ctick", "end"); }
      const x0 = x(r.lo), x1 = x(r.hi);
      if (x1 - x0 > 1) el("line", { x1: x0, x2: x1, y1: y, y2: y, stroke: c, "stroke-width": 6, "stroke-linecap": "round" }, svg);
      el("circle", { cx: x0, cy: y, r: 5, fill: c, stroke: "#14161b", "stroke-width": 2 }, svg); if (x1 - x0 > 1) el("circle", { cx: x1, cy: y, r: 5, fill: c, stroke: "#14161b", "stroke-width": 2 }, svg);
      txt(svg, x1 + 12, y + 4, r.lo === r.hi ? fmt(r.lo) : `${fmt(r.lo)}–${fmt(r.hi)}`, hl ? "cvalue strong" : "cvalue");
      hover(el("rect", { x: 0, y: y - rowH / 2, width: W, height: rowH, fill: "transparent" }, svg), r.tip || `<b>${r.label}</b><br>${r.lo === r.hi ? fmt(r.lo) : fmt(r.lo) + " – " + fmt(r.hi)}`);
    });
  }

  /* paired then/now bars */
  function pairs(wrap, rows) {
    const nar = narrow(wrap); const lab = nar ? 18 : 0; const rowH = 54 + lab, top = 6, padR = nar ? 110 : 70; const H = top + rows.length * rowH + 26;
    const { svg, W } = mount(wrap, H); const padL = nar ? 2 : Math.min(210, W * 0.34); const max = Math.ceil(Math.max(...rows.map((r) => r.today)) / 25) * 25;
    const x = (v) => padL + (v / max) * (W - padL - padR);
    for (let v = 0, i = 0; v <= max; v += 25, i++) { el("line", { x1: x(v), x2: x(v), y1: top, y2: H - 22, stroke: GRID }, svg); tickLbl(nar, i) && txt(svg, x(v), H - 6, v ? M(v) : "$0", "ctick", "middle"); }
    rows.forEach((r, i) => {
      const y = top + i * rowH + 4 + lab; nar ? txt(svg, padL, y - 4, r.label, "clabel strong") : txt(svg, padL - 12, y + 24, r.label, "clabel", "end");
      const a = el("path", { d: barR(padL, y + 2, x(r.nominal) - padL, 16, 4), fill: CONTEXT }, svg); txt(svg, x(r.nominal) + 8, y + 15, `${M(r.nominal)} in 2005`, "cvalue");
      const b = el("path", { d: barR(padL, y + 22, x(r.today) - padL, 16, 4), fill: GOLD }, svg); txt(svg, x(r.today) + 8, y + 35, `${M(r.today)} today`, "cvalue strong");
      hover(el("rect", { x: 0, y, width: W, height: rowH - 6, fill: "transparent" }, svg), `<b>${r.label}</b><br>2005: ${M(r.nominal)}<br>Today's dollars: ${M(r.today)}`);
    });
  }

  /* dot plot: years since original */
  function gaps(wrap, rows) {
    const nar = narrow(wrap); const lab = nar ? 16 : 0; const rowH = 30 + lab, top = 8, padR = 40; const H = top + rows.length * rowH + 28;
    const { svg, W } = mount(wrap, H); const padL = nar ? 6 : Math.min(220, W * 0.38); const min = 15, max = 40;
    const x = (v) => padL + (v - min) / (max - min) * (W - padL - padR);
    el("rect", { x: x(29), y: top - 4, width: x(39) - x(29), height: H - top - 26, fill: "rgba(184,130,46,.08)" }, svg);
    for (let v = 15, i = 0; v <= 40; v += 5, i++) { el("line", { x1: x(v), x2: x(v), y1: top, y2: H - 22, stroke: GRID }, svg); tickLbl(nar, i) && txt(svg, x(v), H - 6, `${v} yrs`, "ctick", "middle"); }
    rows.forEach((r, i) => {
      const y = top + i * rowH + 12 + lab; nar ? txt(svg, 0, y - 10, r.label, r.hl ? "clabel strong" : "clabel") : txt(svg, padL - 12, y + 4, r.label, r.hl ? "clabel strong" : "clabel", "end");
      el("line", { x1: padL, x2: x(r.gap), y1: y, y2: y, stroke: r.hl ? GOLD : CONTEXT, "stroke-width": 2 }, svg);
      el("circle", { cx: x(r.gap), cy: y, r: 6, fill: r.hl ? GOLD : "#8A8E97", stroke: "#14161b", "stroke-width": 2 }, svg);
      txt(svg, x(r.gap) + 12, y + 4, `${r.gap}`, r.hl ? "cvalue strong" : "cvalue");
      hover(el("rect", { x: 0, y: y - rowH / 2, width: W, height: rowH, fill: "transparent" }, svg), `<b>${r.label}</b><br>${r.gap} years after the original${r.how ? "<br>" + r.how : ""}`);
    });
  }

  /* columns per year */
  function columns(wrap, rows, keys, notes) {
    const H = 300, padL = 34, padB = 28, top = 24; const { svg, W } = mount(wrap, H);
    const max = Math.ceil(Math.max(...rows.map((r) => r.total)) / 5) * 5; const band = (W - padL) / rows.length; const bw = Math.min(16, band - 4);
    const y = (v) => top + (1 - v / max) * (H - top - padB);
    for (let t = 0; t <= max; t += max / 4) { el("line", { x1: padL, x2: W, y1: y(t), y2: y(t), stroke: GRID }, svg); txt(svg, padL - 8, y(t) + 4, Math.round(t), "ctick", "end"); }
    rows.forEach((r, i) => {
      const cx = padL + band * i + band / 2; const h = Math.max(0, H - padB - y(r.total)); const peak = notes[r.year];
      const p = h ? el("path", { d: colR(cx - bw / 2, y(r.total), bw, h, 4), fill: peak ? GOLD : "#8A6A3A" }, svg) : null;
      if (r.year % 3 === 0 || peak) txt(svg, cx, H - 8, `'${String(r.year).slice(2)}`, "ctick", "middle");
      if (peak) txt(svg, cx, y(r.total) - 8, peak, "cvalue strong", "middle");
      hover(el("rect", { x: cx - band / 2, y: top, width: band, height: H - top - padB, fill: "transparent" }, svg), `<b>${r.year}</b> · ${r.total} documented<br>${keys.map((k) => `${k}: ${r[k]}`).join("<br>")}`, p);
    });
  }

  Promise.all([fetch(base + "assets/data/memo.json").then((r) => r.json()), fetch(base + "assets/data/investor.json").then((r) => r.json())]).then(([m, d]) => {
    let w;
    if ((w = $("#chart-money"))) { redraw(() => pairs(w, m.film_money)); table(w, ["Measure", "2005", "Today's dollars"], m.film_money.map((r) => [r.label, M(r.nominal), M(r.today)])); }
    if ((w = $("#chart-film"))) {
      let mode = "today";
      const draw = () => { const rows = m.basketball.map((b) => ({ label: b.title, v: b[mode], tip: `<b>${b.title}</b> (${b.year})<br>${M(b.nominal)} at release · ${M(b.today)} in today's dollars` })).sort((a, b) => b.v - a.v).slice(0, 12); hbars(w, rows, { highlight: "Coach Carter", step: mode === "today" ? 50 : 25 }); const rank = rows.findIndex((r) => r.label === "Coach Carter") + 1; $("[data-film-rank]").textContent = `#${rank}`; $("[data-film-mode]").textContent = mode === "today" ? "in today's dollars" : "at release (not adjusted)"; };
      $$(".seg button", w).forEach((b) => b.addEventListener("click", () => { mode = b.dataset.mode; $$(".seg button", w).forEach((x) => { x.classList.toggle("on", x === b); x.setAttribute("aria-pressed", String(x === b)); }); draw(); }));
      redraw(draw);
      table(w, ["Film", "Year", "At release", "Today's dollars"], [...m.basketball].sort((a, b) => b.today - a.today).slice(0, 12).map((b) => [b.title, b.year, M(b.nominal), M(b.today)]));
    }
    if ((w = $("#chart-fees"))) { const rows = m.fee_comps.map((r) => ({ ...r, sub: r.film, tip: `<b>${r.label}</b> · ${r.film}<br>Keynote fee ${K(r.lo)}–${K(r.hi)}` })); redraw(() => ranges(w, rows, { fmt: K, max: 220, ticks: [0, 50, 100, 150, 200] })); table(w, ["Speaker", "Story", "Keynote fee"], m.fee_comps.map((r) => [r.label, r.film, `${K(r.lo)}–${K(r.hi)}`])); }
    if ((w = $("#chart-rev"))) { const rows = m.revenue_lines.map((r) => ({ ...r, tip: `<b>${r.label}</b><br>${M(r.lo)}–${M(r.hi)} (planning assumption)${r.note ? "<br>" + r.note : ""}` })); redraw(() => ranges(w, rows, { fmt: M, max: 5.5, ticks: [0, 1, 2, 3, 4, 5] })); const t = m.revenue_total; table(w, ["Revenue line", "Year-3 range (assumption)", "Note"], m.revenue_lines.map((r) => [r.label, `${M(r.lo)}–${M(r.hi)}`, r.note || ""]).concat([["Sum of the ten rows", `${M(t.lo)}–${M(t.hi)}`, "Not an annual run rate: mixes one-time, personal-fee and recurring receipts"]])); }
    if ((w = $("#chart-ladder"))) { const val = (r) => (r.lo === r.hi ? M(r.lo) : M(r.lo) + "–" + M(r.hi)); const rows = m.ladder.map((r, i) => ({ ...r, sub: r.odds ? `${r.basis} · odds ${r.odds.replace(/ in .*/, "")}*` : r.basis, hl: i === 0 || i === 2, tip: `<b>${r.label}</b><br>${r.what}<br>Revenue ${r.rev} · value ${val(r)}${r.odds ? `<br>Independent review's subjective odds: ${r.odds} (not a forecast)` : ""}` })); redraw(() => ranges(w, rows, { fmt: M, log: true, min: 0.8, max: 1400, ticks: [1, 10, 100, 1000] })); table(w, ["Scenario", "What has to be true", "Revenue/yr", "Basis", "Company value", "Review's subjective odds"], m.ladder.map((r) => [r.label, r.what, r.rev, r.basis, val(r), r.odds || "None given"])); }
    if ((w = $("#chart-stack"))) { const v = (r) => (r.lo === r.hi ? M(r.lo) : `${M(r.lo)}–${M(r.hi)}`); const rows = m.stack.map((r) => ({ ...r, muted: r.hi === 0, sub: r.scale, tip: `<b>${r.label}</b><br>${v(r)} · scale assumed: ${r.scale}<br>Must be shown: ${r.prove}` })); redraw(() => ranges(w, rows, { fmt: M, max: 500, ticks: [0, 100, 200, 300, 400, 500] })); table(w, ["Asset", "Value range (review's assumption)", "Scale assumed", "What must be demonstrated"], m.stack.map((r) => [r.label, v(r), r.scale, r.prove]).concat([["Stated sum", "$605M–$1.45B", "—", "Not additive: assets overlap and are alternative paths"]])); }
    if ((w = $("#chart-revival"))) { const rows = [...m.revivals].sort((a, b) => b.gap - a.gap); redraw(() => gaps(w, rows)); table(w, ["Title", "Years after original", "How it worked"], rows.map((r) => [r.label, r.gap, r.how || ""])); const rn = $("#revival-notes"); if (rn) rn.innerHTML = rows.filter((r) => r.how).map((r) => `<li><b>${r.label}.</b> ${r.how}</li>`).join(""); }
    if ((w = $("#chart-cost"))) { const rows = m.cost_per_hour.map((r, i) => ({ label: r.label, v: r.v, hl: i === 1, tip: `<b>${r.label}</b><br>~$${r.range || r.v}K per finished hour` })); redraw(() => hbars(w, rows, { fmt: K, step: 50 })); table(w, ["Production mode", "Cost per finished hour"], m.cost_per_hour.map((r) => [r.label, `$${r.range || r.v}K`])); }
    if ((w = $("#chart-years"))) { const keys = ["TV & radio", "Press features", "Keynotes & talks", "Podcasts"]; redraw(() => columns(w, d.by_year, keys, { 1999: "The lockout", 2005: "The film", 2023: "SlamBall return" })); table(w, ["Year", "Total", ...keys], d.by_year.map((r) => [r.year, r.total, ...keys.map((k) => r[k])])); }
    const cw = $("#comps");
    if (cw && m.comps) cw.innerHTML = m.comps.map((c) => `<a class="comp" href="${c.url}" target="_blank" rel="noopener"><b>${c.name}</b><span>${c.value}</span></a>`).join("");
    const tw = $("#testimonials");
    if (tw && d.testimonials.length) tw.innerHTML = d.testimonials.map((t) => `<figure class="tq"><blockquote>“${t.quote}”</blockquote><figcaption><b>${t.person || t.org}</b>${t.person ? `<span>${[t.title, t.org].filter(Boolean).join(", ")}</span>` : ""}</figcaption></figure>`).join("");
  });
})();
