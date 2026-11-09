/* Investor page: hero counters from data, three SVG charts (hover tooltip + table view), testimonials. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const base = document.querySelector('script[src*="investor.js"]').src.replace(/assets\/js\/investor\.js.*$/, "");
  const NS = "http://www.w3.org/2000/svg";
  const GOLD = "#B8822E", CONTEXT = "#3A3E47", GRID = "rgba(245,240,232,.08)", INK2 = "rgba(245,240,232,.62)", INK1 = "#F5F0E8";
  const fmtM = (n) => `$${n >= 100 ? Math.round(n) : n.toFixed(1)}M`;
  const fmtK = (n) => (n >= 1000 ? `$${(n / 1000).toFixed(n % 1000 ? 1 : 0)}M` : `$${n % 1 ? n.toFixed(1) : n}K`);
  const el = (tag, attrs = {}, parent) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); parent && parent.appendChild(e); return e; };
  const rounded = (x, y, w, h, r, dir) => { // round only the data end
    r = Math.min(r, w / 2, h / 2);
    if (dir === "right") return `M${x},${y}h${w - r}a${r},${r} 0 0 1 ${r},${r}v${h - 2 * r}a${r},${r} 0 0 1 -${r},${r}h-${w - r}z`;
    return `M${x},${y + h}v-${h - r}a${r},${r} 0 0 1 ${r},-${r}h${w - 2 * r}a${r},${r} 0 0 1 ${r},${r}v${h - r}z`; // up
  };

  /* tooltip */
  const tip = document.createElement("div"); tip.className = "ctip"; tip.setAttribute("role", "status"); document.body.appendChild(tip);
  const showTip = (e, html) => { tip.innerHTML = html; tip.classList.add("on"); const x = Math.min(innerWidth - tip.offsetWidth - 12, e.clientX + 14); tip.style.transform = `translate(${x}px,${e.clientY - tip.offsetHeight - 14}px)`; };
  const hideTip = () => tip.classList.remove("on");

  const tableToggle = (wrap, rows, head) => {
    const btn = $(".ctoggle", wrap); const tbl = $(".ctable", wrap);
    tbl.innerHTML = `<table><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody></table>`;
    btn && btn.addEventListener("click", () => { const on = wrap.classList.toggle("show-table"); btn.textContent = on ? "Show chart" : "Show table"; btn.setAttribute("aria-pressed", String(on)); });
  };

  /* ---- chart A: horizontal bars, one highlighted ---- */
  function hbar(wrap, data, highlight) {
    const svgBox = $(".cbody", wrap); const W = svgBox.clientWidth || 700; const rowH = 34, padL = Math.min(230, W * 0.38), padR = 64, top = 6;
    const H = top + data.length * rowH + 24; const max = Math.max(...data.map((d) => d.v)) * 1.05;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", height: H, role: "img", "aria-label": wrap.dataset.title || "" }, null);
    const x = (v) => padL + (v / max) * (W - padL - padR);
    [0, 0.25, 0.5, 0.75, 1].forEach((t) => { const gx = x(max * t / 1.05 * 1.0); el("line", { x1: gx, x2: gx, y1: top, y2: H - 22, stroke: GRID }, svg); const tx = el("text", { x: gx, y: H - 6, "text-anchor": "middle", class: "ctick" }, svg); tx.textContent = fmtM(max * t / 1.05); });
    data.forEach((d, i) => {
      const y = top + i * rowH + 7; const isH = d.label === highlight; const bw = Math.max(2, x(d.v) - padL);
      const lbl = el("text", { x: padL - 12, y: y + 14, "text-anchor": "end", class: isH ? "clabel strong" : "clabel" }, svg); lbl.textContent = d.label.length > 30 ? d.label.slice(0, 29) + "…" : d.label;
      const p = el("path", { d: rounded(padL, y, bw, 20, 4, "right"), fill: isH ? GOLD : CONTEXT, class: "cmark" }, svg);
      const val = el("text", { x: padL + bw + 8, y: y + 14, class: isH ? "cvalue strong" : "cvalue" }, svg); val.textContent = fmtM(d.v);
      const hit = el("rect", { x: 0, y: y - 6, width: W, height: rowH, fill: "transparent" }, svg);
      hit.addEventListener("pointermove", (e) => { p.setAttribute("opacity", ".85"); showTip(e, `<b>${d.label}</b>${d.year ? ` (${d.year})` : ""}<br>Domestic gross ${fmtM(d.v)}${d.rank ? `<br>Rank #${d.rank}` : ""}`); });
      hit.addEventListener("pointerleave", () => { p.removeAttribute("opacity"); hideTip(); });
    });
    svgBox.innerHTML = ""; svgBox.appendChild(svg);
  }

  /* ---- chart B: columns per year with breakdown ---- */
  function columns(wrap, rows, keys, notes) {
    const svgBox = $(".cbody", wrap); const W = svgBox.clientWidth || 700; const H = 300, padL = 34, padB = 28, top = 24;
    const max = Math.ceil(Math.max(...rows.map((r) => r.total)) / 5) * 5;
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", height: H, role: "img", "aria-label": wrap.dataset.title || "" });
    const band = (W - padL) / rows.length; const bw = Math.min(16, band - 4);
    const y = (v) => top + (1 - v / max) * (H - top - padB);
    for (let t = 0; t <= max; t += max / 4) { el("line", { x1: padL, x2: W, y1: y(t), y2: y(t), stroke: GRID }, svg); const tx = el("text", { x: padL - 8, y: y(t) + 4, "text-anchor": "end", class: "ctick" }, svg); tx.textContent = Math.round(t); }
    rows.forEach((r, i) => {
      const cx = padL + band * i + band / 2; const h = Math.max(0, H - padB - y(r.total));
      const isPeak = notes[r.year];
      const p = h > 0 ? el("path", { d: rounded(cx - bw / 2, y(r.total), bw, h, 4, "up"), fill: isPeak ? GOLD : "#8A6A3A", class: "cmark" }, svg) : null;
      if (r.year % 3 === 0 || isPeak) { const tx = el("text", { x: cx, y: H - 8, "text-anchor": "middle", class: "ctick" }, svg); tx.textContent = `'${String(r.year).slice(2)}`; }
      if (isPeak) { const t = el("text", { x: cx, y: y(r.total) - 8, "text-anchor": "middle", class: "cvalue strong" }, svg); t.textContent = notes[r.year]; }
      const hit = el("rect", { x: cx - band / 2, y: top, width: band, height: H - top - padB, fill: "transparent" }, svg);
      hit.addEventListener("pointermove", (e) => { p && p.setAttribute("opacity", ".8"); showTip(e, `<b>${r.year}</b> · ${r.total} documented<br>${keys.map((k) => `${k}: ${r[k]}`).join("<br>")}`); });
      hit.addEventListener("pointerleave", () => { p && p.removeAttribute("opacity"); hideTip(); });
    });
    svgBox.innerHTML = ""; svgBox.appendChild(svg);
  }

  /* ---- chart C: range bars (low–high) ---- */
  function ranges(wrap, data) {
    const svgBox = $(".cbody", wrap); const W = svgBox.clientWidth || 700; const rowH = 40, padL = Math.min(250, W * 0.42), padR = 80, top = 6;
    const H = top + data.length * rowH + 24; const max = 500;
    const x = (v) => padL + (Math.min(v, max) / max) * (W - padL - padR);
    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", height: H, role: "img", "aria-label": wrap.dataset.title || "" });
    [0, 100, 200, 300, 400, 500].forEach((t) => { el("line", { x1: x(t), x2: x(t), y1: top, y2: H - 22, stroke: GRID }, svg); const tx = el("text", { x: x(t), y: H - 6, "text-anchor": "middle", class: "ctick" }, svg); tx.textContent = t ? `$${t}K` : "$0"; });
    data.forEach((d, i) => {
      const yy = top + i * rowH + 10; const x0 = x(d.lo), x1 = x(d.hi);
      const lbl = el("text", { x: padL - 12, y: yy + 5, "text-anchor": "end", class: "clabel" }, svg); lbl.textContent = d.label;
      const sub = el("text", { x: padL - 12, y: yy + 19, "text-anchor": "end", class: "ctick" }, svg); sub.textContent = d.unit;
      el("line", { x1: x0, x2: x1, y1: yy + 2, y2: yy + 2, stroke: GOLD, "stroke-width": 6, "stroke-linecap": "round", class: "cmark" }, svg);
      el("circle", { cx: x0, cy: yy + 2, r: 5, fill: GOLD, stroke: "#101216", "stroke-width": 2 }, svg);
      el("circle", { cx: x1, cy: yy + 2, r: 5, fill: GOLD, stroke: "#101216", "stroke-width": 2 }, svg);
      const v = el("text", { x: x1 + 12, y: yy + 6, class: "cvalue" }, svg); v.textContent = `${fmtK(d.lo)}–${fmtK(d.hi)}${d.open ? "+" : ""}`;
      const hit = el("rect", { x: 0, y: yy - 12, width: W, height: rowH, fill: "transparent" }, svg);
      hit.addEventListener("pointermove", (e) => showTip(e, `<b>${d.label}</b><br>${fmtK(d.lo)} – ${fmtK(d.hi)}${d.open ? "+" : ""} ${d.unit}<br><span style="opacity:.7">Estimate · subject to Coach's approval</span>`));
      hit.addEventListener("pointerleave", hideTip);
    });
    svgBox.innerHTML = ""; svgBox.appendChild(svg);
  }

  const REV = [
    { label: "Mainstage keynote", unit: "per event + travel", lo: 15, hi: 30 },
    { label: "Half-day leadership session", unit: "per event", lo: 25, hi: 40 },
    { label: "Virtual keynote", unit: "per event", lo: 7.5, hi: 12 },
    { label: "School visit", unit: "per visit, sponsor-funded", lo: 5, hi: 10 },
    { label: "The Contract program", unit: "per organization", lo: 40, hi: 75 },
    { label: "The Contract, multi-site", unit: "per year", lo: 150, hi: 300 },
    { label: "District curriculum license", unit: "per district per year", lo: 15, hi: 60 },
    { label: "Brand ambassador", unit: "per category per year", lo: 100, hi: 500 },
  ];

  fetch(base + "assets/data/investor.json").then((r) => r.json()).then((d) => {
    const R = d.reach;
    $$("[data-metric]").forEach((n) => { const v = R[n.dataset.metric]; if (v == null) return; n.dataset.count = n.dataset.metric === "video_views" ? (v / 1e6).toFixed(1) : v; });
    // retrigger counters (site.js observes data-count on load; set text for no-JS)
    $$("[data-metric]").forEach((n) => { if (!n.textContent.trim() || n.textContent === "0") n.textContent = n.dataset.count; });

    /* film chart */
    const fw = $("#chart-film");
    const list = (d.film && d.film.basketball_domestic) || [];
    if (fw && list.length) {
      const rows = list.map((x) => ({ label: x.title, v: x.domestic_m, year: x.year, rank: x.rank })).sort((a, b) => b.v - a.v).slice(0, 12);
      const draw = () => hbar(fw, rows, "Coach Carter"); draw(); addEventListener("resize", draw);
      tableToggle(fw, rows.map((r, i) => [i + 1, r.label, r.year || "", fmtM(r.v)]), ["#", "Film", "Year", "Domestic gross"]);
      const src = d.film.basketball_source; if (src) $(".csrc", fw).innerHTML = `Source: <a class="link-u" href="${src}" target="_blank" rel="noopener">${new URL(src).hostname}</a>`;
    } else if (fw) { fw.closest("section") && fw.closest(".chart-card").classList.add("internal"); }

    /* film facts */
    const ff = d.film && d.film.facts;
    if (ff) $$("[data-film]").forEach((n) => { if (ff[n.dataset.film] != null) n.textContent = ff[n.dataset.film]; });

    /* appearances by year */
    const aw = $("#chart-years");
    if (aw) {
      const keys = ["TV & radio", "Press features", "Keynotes & talks", "Podcasts"];
      const notes = { 1999: "The lockout", 2005: "The film", 2023: "SlamBall return" };
      const draw = () => columns(aw, d.by_year, keys, notes); draw(); addEventListener("resize", draw);
      tableToggle(aw, d.by_year.map((r) => [r.year, r.total, ...keys.map((k) => r[k])]), ["Year", "Total", ...keys]);
    }

    /* revenue */
    const rw = $("#chart-rev");
    if (rw) { const draw = () => ranges(rw, REV); draw(); addEventListener("resize", draw); tableToggle(rw, REV.map((r) => [r.label, r.unit, `${fmtK(r.lo)}–${fmtK(r.hi)}`]), ["Offer", "Unit", "Estimated range"]); }

    /* testimonials */
    const tw = $("#testimonials");
    if (tw && d.testimonials.length) {
      tw.innerHTML = d.testimonials.map((t) => `<figure class="tq"><blockquote>“${t.quote}”</blockquote><figcaption><b>${t.person || t.org}</b>${t.person ? `<span>${[t.title, t.org].filter(Boolean).join(", ")}</span>` : ""}</figcaption></figure>`).join("");
    }
  });
})();
