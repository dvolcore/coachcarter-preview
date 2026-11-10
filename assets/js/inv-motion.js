/* Investor memo motion layer: hero data graphic, figure ticker, chart draw-ins,
   count-up tiles, memo reading progress. Business-only — no film footage. */
(() => {
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const GOLD = "#D3A24F", GOLD_LO = "rgba(184,130,46,", CHALK = "rgba(245,240,232,";

  /* ---------- 1. Hero: a living market graph ---------- */
  const cv = document.querySelector(".inv-graph");
  if (cv) {
    const ctx = cv.getContext("2d");
    // story of the asset: index of attention over time (shape, not a data series — labels carry the facts)
    const pts = [
      { x: 0.06, y: 0.58, label: "2005", sub: "#1 opening · $24.2M" },
      { x: 0.20, y: 0.40, label: "2005", sub: "$76.7M worldwide" },
      { x: 0.36, y: 0.62, label: "2010s", sub: "TV · DVD · classrooms" },
      { x: 0.54, y: 0.46, label: "2022", sub: "Netflix Global Top 10" },
      { x: 0.72, y: 0.30, label: "2025", sub: "16.9M Netflix views" },
      { x: 0.90, y: 0.16, label: "Next", sub: "Capture the attention" },
    ];
    let W = 0, H = 0, dpr = 1, t0 = performance.now(), running = true, raf;
    const size = () => {
      dpr = Math.min(2, devicePixelRatio || 1);
      W = cv.clientWidth; H = cv.clientHeight;
      cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const ease = (p) => 1 - Math.pow(1 - Math.min(1, Math.max(0, p)), 3);
    // desktop: graph lives in the empty lower-right of the hero; phones: faint full-width backdrop, no labels
    const R = () => (W < 900 ? { x0: 0.04, x1: 0.96, y0: 0.30, y1: 0.62 } : { x0: 0.55, x1: 0.95, y0: 0.50, y1: 0.86 });
    const P = (p) => { const r = R(); return { x: (r.x0 + (p.x - 0.06) / 0.84 * (r.x1 - r.x0)) * W, y: (r.y0 + (p.y - 0.16) / 0.46 * (r.y1 - r.y0)) * H }; };
    const draw = (now) => {
      const t = (now - t0) / 1000;
      ctx.clearRect(0, 0, W, H);
      const fade = W < 900 ? 0.45 : 1; ctx.globalAlpha = fade;
      // perspective floor grid, drifting
      const hz = H * (R().y1 + 0.06), drift = reduce ? 0 : (t * 18) % 60;
      ctx.lineWidth = 1;
      for (let i = 0; i < 14; i++) {
        const y = hz + Math.pow(i / 13, 2) * (H - hz) + (i ? drift * (i / 13) : 0);
        if (y > H) continue;
        ctx.strokeStyle = GOLD_LO + (0.04 + 0.1 * (i / 13)) + ")";
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }
      for (let i = -12; i <= 12; i++) {
        ctx.strokeStyle = GOLD_LO + "0.07)";
        ctx.beginPath(); ctx.moveTo(W / 2 + i * 26, hz); ctx.lineTo(W / 2 + i * W * 0.16, H); ctx.stroke();
      }
      // background columns rising and breathing
      const reg = R(), cx0 = reg.x0 * W, cw = (reg.x1 - reg.x0) * W;
      const cols = Math.max(8, Math.round(cw / 60));
      for (let i = 0; i < cols; i++) {
        const cx = cx0 + (i + 0.5) * (cw / cols);
        const base = 0.15 + 0.55 * (i / cols);
        const h = (base + 0.06 * Math.sin(t * 0.9 + i * 0.7)) * H * 0.42 * ease(t / 1.6 - i * 0.04);
        const g = ctx.createLinearGradient(0, hz - h, 0, hz);
        g.addColorStop(0, GOLD_LO + "0.22)"); g.addColorStop(1, GOLD_LO + "0)");
        ctx.fillStyle = g; ctx.fillRect(cx - 9, hz - h, 18, h);
      }
      // the line, drawn on, then holding with a travelling pulse
      const prog = reduce ? 1 : ease((t - 0.4) / 2.6);
      const xy = pts.map(P);
      const total = xy.length - 1, upto = prog * total;
      ctx.lineJoin = "round"; ctx.lineCap = "round";
      // area under the line
      ctx.beginPath(); ctx.moveTo(xy[0].x, hz);
      for (let i = 0; i <= Math.floor(upto); i++) ctx.lineTo(xy[i].x, xy[i].y);
      let tip = xy[Math.floor(upto)];
      if (upto < total) { const a = xy[Math.floor(upto)], b = xy[Math.floor(upto) + 1], f = upto - Math.floor(upto); tip = { x: a.x + (b.x - a.x) * f, y: a.y + (b.y - a.y) * f }; ctx.lineTo(tip.x, tip.y); }
      ctx.lineTo(tip.x, hz); ctx.closePath();
      const ag = ctx.createLinearGradient(0, H * 0.15, 0, hz); ag.addColorStop(0, GOLD_LO + "0.20)"); ag.addColorStop(1, GOLD_LO + "0)");
      ctx.fillStyle = ag; ctx.fill();
      // line glow + core
      for (const [w, a] of [[10, 0.10], [4, 0.35], [2, 1]]) {
        ctx.strokeStyle = w === 2 ? GOLD : GOLD_LO + a + ")"; ctx.lineWidth = w;
        ctx.beginPath(); ctx.moveTo(xy[0].x, xy[0].y);
        for (let i = 1; i <= Math.floor(upto); i++) ctx.lineTo(xy[i].x, xy[i].y);
        ctx.lineTo(tip.x, tip.y); ctx.stroke();
      }
      // nodes + callouts
      const narrow = W < 900;
      xy.forEach((p, i) => {
        if (i > upto + 0.001) return;
        const pop = reduce ? 1 : ease((upto - i) * 2.5);
        ctx.fillStyle = "#0b0d10"; ctx.strokeStyle = GOLD; ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(p.x, p.y, 5 * pop, 0, 7); ctx.fill(); ctx.stroke();
        if (!reduce) { const r = 6 + ((t * 22 + i * 9) % 22); ctx.strokeStyle = GOLD_LO + (0.5 * (1 - (r - 6) / 22)) + ")"; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 7); ctx.stroke(); }
        if (narrow) return;
        ctx.globalAlpha = pop * fade;
        ctx.textAlign = i === xy.length - 1 ? "right" : "left";
        const lx = i === xy.length - 1 ? p.x + 6 : p.x + 12;
        ctx.font = "600 11px 'Barlow Condensed', sans-serif"; ctx.fillStyle = GOLD;
        ctx.fillText(pts[i].label.toUpperCase(), lx, p.y - 16);
        ctx.font = "500 13px Inter, sans-serif"; ctx.fillStyle = CHALK + "0.82)";
        ctx.fillText(pts[i].sub, lx, p.y + 24);
        ctx.globalAlpha = fade;
      });
      // travelling pulse once drawn
      if (!reduce && prog >= 1) {
        const q = ((t * 0.18) % 1) * total, k = Math.floor(q), f = q - k, a = xy[k], b = xy[k + 1] || a;
        const px = a.x + (b.x - a.x) * f, py = a.y + (b.y - a.y) * f;
        const rg = ctx.createRadialGradient(px, py, 0, px, py, 26); rg.addColorStop(0, GOLD_LO + "0.9)"); rg.addColorStop(1, GOLD_LO + "0)");
        ctx.fillStyle = rg; ctx.beginPath(); ctx.arc(px, py, 26, 0, 7); ctx.fill();
      }
      if (running && !reduce) raf = requestAnimationFrame(draw);
    };
    size(); addEventListener("resize", () => { size(); if (reduce) draw(performance.now()); });
    new IntersectionObserver(([e]) => { running = e.isIntersecting; cancelAnimationFrame(raf); if (running) raf = requestAnimationFrame(draw); }).observe(cv);
    if (reduce) draw(performance.now() + 9000);
  }

  /* ---------- 2. Count-up tiles ---------- */
  const fmt = (v, d) => v.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  const countUp = (el) => {
    const to = parseFloat(el.dataset.to), d = (el.dataset.to.split(".")[1] || "").length;
    if (reduce) { el.textContent = fmt(to, d); return; }
    const t0 = performance.now(), dur = 1600;
    const step = (now) => { const p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 4); el.textContent = fmt(to * e, d); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  };
  const io = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return; io.unobserve(en.target);
    const n = en.target;
    n.classList.add("in");
    n.querySelectorAll("[data-to]").forEach(countUp);
  }), { rootMargin: "0px 0px -12% 0px" });
  document.querySelectorAll(".im-tiles, .im-close, .im-meter").forEach((n) => io.observe(n));

  /* ---------- 3. Charts draw in when they enter ---------- */
  const animateChart = (card) => {
    const svg = card.querySelector(".cbody svg"); card.classList.add("seen");
    if (!svg || reduce || !svg.animate) return;
    let i = 0;
    svg.querySelectorAll("path[fill], line[stroke-width], circle").forEach((m) => {
      const fill = m.getAttribute("fill");
      if (fill === "transparent" || m.closest("defs")) return;
      const b = m.getBBox(); const delay = 80 + (i++) * 45;
      m.style.transformBox = "fill-box";
      if (m.tagName === "circle") {
        m.style.transformOrigin = "center";
        m.animate([{ transform: "scale(0)", opacity: 0 }, { transform: "scale(1)", opacity: 1 }], { duration: 500, delay: delay + 500, easing: "cubic-bezier(.2,.9,.3,1.3)", fill: "backwards" });
      } else if (b.width >= b.height) {
        m.style.transformOrigin = "left center";
        m.animate([{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { duration: 900, delay, easing: "cubic-bezier(.16,1,.3,1)", fill: "backwards" });
      } else {
        m.style.transformOrigin = "center bottom";
        m.animate([{ transform: "scaleY(0)" }, { transform: "scaleY(1)" }], { duration: 900, delay, easing: "cubic-bezier(.16,1,.3,1)", fill: "backwards" });
      }
    });
    svg.querySelectorAll("text").forEach((tx, k) => tx.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, delay: 300 + k * 12, fill: "backwards" }));
  };
  const cio = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return;
    const card = en.target;
    const go = () => { cio.unobserve(card); animateChart(card); };
    if (card.querySelector(".cbody svg")) go(); else setTimeout(go, 400);
  }), { rootMargin: "0px 0px -18% 0px" });
  document.querySelectorAll(".chart-card").forEach((c) => cio.observe(c));

  /* ---------- 4. Reading progress on the memo nav ---------- */
  const nav = document.querySelector(".inv-nav");
  if (nav) {
    const bar = document.createElement("i"); bar.className = "im-progress"; bar.setAttribute("aria-hidden", "true"); nav.appendChild(bar);
    const links = [...nav.querySelectorAll("a[href^='#']")], secs = links.map((a) => document.querySelector(a.getAttribute("href")));
    const tick = () => {
      const doc = document.documentElement, max = doc.scrollHeight - innerHeight;
      bar.style.transform = `scaleX(${Math.min(1, scrollY / max)})`;
      let cur = 0; secs.forEach((s, k) => { if (s && s.getBoundingClientRect().top < innerHeight * 0.35) cur = k; });
      links.forEach((a, k) => a.classList.toggle("on", k === cur));
    };
    addEventListener("scroll", tick, { passive: true }); tick();
  }
})();
