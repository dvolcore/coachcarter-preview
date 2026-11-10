/* PLATFORM SHELL v2 — worlds mega menu, command palette, chapter rail, local-nav spy,
   home hub, scroll progress, link prefetch. Markup: tools/shell.py. Styles: shell.css.
   Loads after site.js; shares nothing with it except the DOM. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const nav = $(".nav2");

  /* ---------------- scroll: progress, rail, local-nav spy (one rAF) ---------------- */
  const progress = $(".progress");
  const rail = $(".rail");
  const railLinks = rail ? $$("a", rail).map((a) => ({ a, el: document.getElementById(a.hash.slice(1)) })).filter((x) => x.el) : [];
  // local-nav spy: a link owns every section id in data-spy; the list is kept in PAGE order, not link order
  const spy = [];
  $$(".localnav [data-spy]").forEach((a) => (a.dataset.spy || a.hash.slice(1)).split(" ").forEach((id) => {
    const el = id && document.getElementById(id);
    el && spy.push({ a, el });
  }));
  spy.sort((x, y) => (x.el.compareDocumentPosition(y.el) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));
  const lnLinks = $(".ln-links");
  const nextup = $(".nextup");
  let railCur = null, spyCur = null, toneAt = 0, ticking = false;

  const lum = (el) => {
    for (let n = el; n && n !== document.documentElement; n = n.parentElement) {
      const m = getComputedStyle(n).backgroundColor.match(/[\d.]+/g);
      if (m && (m.length < 4 || +m[3] > 0.5)) return (0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2]) / 255;
    }
    return 0;
  };
  const current = (list, line) => {
    let cur = null;
    for (const x of list) { if (x.el.getBoundingClientRect().top <= line) cur = x; else break; }
    return cur;
  };
  const frame = () => {
    ticking = false;
    const y = scrollY, max = document.documentElement.scrollHeight - innerHeight;
    if (rail) {
      rail.classList.toggle("show", y > innerHeight * 0.55 && (!nextup || nextup.getBoundingClientRect().top > innerHeight * 0.7));
      const cur = current(railLinks, innerHeight * 0.42);
      if (cur !== railCur) {
        railCur && railCur.a.classList.remove("on");
        cur && cur.a.classList.add("on");
        railCur = cur;
      }
      const now = performance.now();
      if (now - toneAt > 160) {
        toneAt = now;
        const under = document.elementFromPoint(innerWidth - 96, innerHeight / 2);
        if (under) rail.classList.toggle("on-light", lum(under) > 0.6);
      }
    }
    if (spy.length) {
      const cur = current(spy, 140);
      if ((cur && cur.a) !== (spyCur && spyCur.a)) {
        spyCur && spyCur.a.classList.remove("on");
        if (cur) {
          cur.a.classList.add("on");
          if (lnLinks && lnLinks.scrollWidth > lnLinks.clientWidth) lnLinks.scrollTo({ left: cur.a.offsetLeft - 40, behavior: "smooth" });
        }
        spyCur = cur;
      }
    }
    // the only style write that affects every frame goes last, after all the reads above
    if (progress) progress.style.setProperty("--p", max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  frame();

  /* ---------------- reveal hooks ---------------- */
  const seen = $$(".hub, .nextup, .store-depts");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((ents) => ents.forEach((en) => {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    }), { threshold: 0.12 });
    seen.forEach((el) => io.observe(el));
  } else seen.forEach((el) => el.classList.add("in"));

  /* ---------------- store catalog: cards rise in as they enter ---------------- */
  const cards = $$(".academy-product-card, .edition-card, .store-catalog-section > header, .uniform-group > h3");
  if (cards.length && "IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const cio = new IntersectionObserver((ents) => {
      let n = 0;
      ents.forEach((en) => {
        if (!en.isIntersecting) return;
        en.target.style.transitionDelay = Math.min(n++, 5) * 60 + "ms";
        en.target.classList.add("rise-in");
        cio.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -6% 0px" });
    cards.forEach((c) => { if (c.getBoundingClientRect().top > innerHeight) { c.classList.add("rise"); cio.observe(c); } });
  }

  /* ---------------- worlds mega menu ---------------- */
  const megas = $(".megas");
  const scrim = $(".mega-scrim");
  const btns = $$(".world-btn");
  const panels = $$(".mega");
  let open = null, openT = 0, closeT = 0, hoverAt = 0, openY = 0;
  panels.forEach((m) => { m.inert = true; });

  const pvWide = matchMedia("(min-width: 1241px)"); // the preview column is hidden below this
  const preview = (panel, src, label) => {
    const fig = $(".mega-pv", panel);
    if (!fig || !src || !pvWide.matches) return;
    const imgs = $$("img", fig);
    const on = imgs.find((i) => i.classList.contains("on")) || imgs[0];
    const cap = $("figcaption", fig);
    if (cap && label) cap.textContent = label;
    if (on.getAttribute("src") === src) { on.classList.add("on"); return; }
    const next = imgs.find((i) => i !== on);
    next.onload = () => { next.classList.add("on"); on.classList.remove("on"); };
    next.src = src;
    if (next.complete) next.onload();
  };
  const show = (key) => {
    clearTimeout(closeT);
    if (open === key || !megas) return;
    megas.classList.toggle("swap", !!open);
    panels.forEach((m) => { const on = m.dataset.mega === key; m.classList.toggle("open", on); m.inert = !on; });
    btns.forEach((b) => b.setAttribute("aria-expanded", String(b.dataset.world === key)));
    open = key; openY = scrollY;
    nav.classList.add("mega-open");
    scrim.classList.add("on");
    const panel = panels.find((m) => m.dataset.mega === key);
    const first = $(".mega-link[aria-current]", panel) || $(".mega-link", panel);
    first && preview(panel, first.dataset.pv, $(".ml-t", first).textContent);
  };
  const hide = () => {
    clearTimeout(openT); clearTimeout(closeT);
    if (!open) return;
    megas.classList.remove("swap");
    panels.forEach((m) => { m.classList.remove("open"); m.inert = true; });
    btns.forEach((b) => b.setAttribute("aria-expanded", "false"));
    open = null;
    nav.classList.remove("mega-open");
    scrim.classList.remove("on");
  };
  btns.forEach((b) => {
    const key = b.dataset.world;
    b.addEventListener("pointerenter", (e) => {
      if (e.pointerType !== "mouse") return;
      clearTimeout(closeT); clearTimeout(openT);
      openT = setTimeout(() => { show(key); hoverAt = Date.now(); }, open ? 0 : 60);
    });
    b.addEventListener("pointerleave", () => clearTimeout(openT));
    b.addEventListener("click", (e) => {
      if (open === key && Date.now() - hoverAt > 400) { hide(); return; }
      show(key);
      if (e.detail === 0) { const f = $(`#mega-${key} a`); f && f.focus(); } // keyboard
    });
  });
  if (nav && megas) {
    nav.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") closeT = setTimeout(hide, 200); });
    nav.addEventListener("pointerenter", () => clearTimeout(closeT));
    nav.addEventListener("focusout", (e) => { if (open && e.relatedTarget && !nav.contains(e.relatedTarget)) hide(); });
    scrim.addEventListener("click", hide);
    addEventListener("scroll", () => { if (open && Math.abs(scrollY - openY) > 120) hide(); }, { passive: true });
    $$(".mega-link").forEach((a) => {
      const swap = () => preview(a.closest(".mega"), a.dataset.pv, $(".ml-t", a).textContent);
      a.addEventListener("pointerenter", swap);
      a.addEventListener("focus", swap);
    });
    // warm the preview images once the page is idle so the first hover is instant
    const warm = () => $$(".mega-link[data-pv]").forEach((a) => { const i = new Image(); i.decoding = "async"; i.src = a.dataset.pv; });
    fine && pvWide.matches && ("requestIdleCallback" in window ? requestIdleCallback(warm, { timeout: 4000 }) : setTimeout(warm, 2500));
  }

  /* ---------------- command palette ---------------- */
  const ORDER = ["Action", "Page", "Section", "Product", "Scene"];
  const GROUP = { Action: "Quick actions", Page: "Pages", Section: "On the page", Product: "Store", Scene: "Film scenes" };
  let pal = null, palInput = null, palList = null, data = null, loading = false, rows = [], sel = 0, lastFocus = null;
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  // split the RAW text on one combined pattern, then escape each piece (never run a regex over escaped HTML)
  const mark = (text, tokens) => {
    const ts = tokens.filter((t) => t.length > 1).map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    if (!ts.length) return esc(text);
    return String(text).split(new RegExp("(" + ts.join("|") + ")", "ig")).map((part, i) => (i % 2 ? "<mark>" + esc(part) + "</mark>" : esc(part))).join("");
  };
  const loadIndex = () => {
    if (data || loading) return;
    loading = true;
    fetch("assets/data/search.json").then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then((d) => { data = d; loading = false; render(); })
      .catch(() => { loading = false; palList.innerHTML = '<p class="pal-empty">Search is unavailable right now. Close and try again.</p>'; });
  };
  const render = () => {
    const q = palInput.value.trim().toLowerCase();
    const tokens = q.split(/\s+/).filter(Boolean);
    let hits;
    if (!data) { palList.innerHTML = '<p class="pal-empty">Loading…</p>'; return; }
    if (!tokens.length) hits = data.filter((d) => d.k === "Action" || d.k === "Page").map((d) => ({ d, s: 0 }));
    else {
      hits = [];
      for (const d of data) {
        const t = d.t.toLowerCase(), s = d.s.toLowerCase();
        let score = 0, ok = true;
        for (const tok of tokens) {
          if (t.startsWith(tok)) score += 5; else if (t.includes(" " + tok)) score += 4; else if (t.includes(tok)) score += 3; else if (s.includes(tok)) score += 1; else { ok = false; break; }
        }
        if (ok) hits.push({ d, s: score + (d.k === "Page" ? 2 : d.k === "Action" ? 1 : 0) });
      }
      hits.sort((a, b) => b.s - a.s);
      hits = hits.slice(0, 36);
    }
    rows = [];
    let html = "";
    ORDER.forEach((k) => {
      const g = hits.filter((h) => h.d.k === k);
      if (!g.length) return;
      html += `<div class="pal-group" role="presentation">${GROUP[k]}</div>`;
      g.forEach((h) => {
        html += `<a class="pal-row" id="pal-r-${rows.length}" href="${esc(h.d.u)}" data-i="${rows.length}" role="option" tabindex="-1"><b>${mark(h.d.t, tokens)}</b><small>${mark(h.d.s, tokens)}</small><i>Open ↵</i></a>`;
        rows.push(h.d);
      });
    });
    palList.innerHTML = html || `<p class="pal-empty">Nothing matches “${esc(palInput.value)}”. Try “keynote”, “jersey” or “lockout”.</p>`;
    sel = 0; paint();
  };
  const paint = () => {
    $$(".pal-row", palList).forEach((r, i) => {
      r.classList.toggle("sel", i === sel);
      r.setAttribute("aria-selected", String(i === sel));
      if (i === sel) r.scrollIntoView({ block: "nearest" });
    });
    rows.length ? palInput.setAttribute("aria-activedescendant", "pal-r-" + sel) : palInput.removeAttribute("aria-activedescendant");
  };
  const closePal = () => {
    if (!pal || !pal.classList.contains("open")) return;
    pal.classList.remove("open"); pal.inert = true;
    lastFocus && lastFocus.focus && lastFocus.focus({ preventScroll: true });
  };
  const go = (d) => {
    if (!d) return;
    closePal();
    const [path, hash] = d.u.split("#");
    const here = location.pathname.split("/").pop() || "index.html";
    const target = path === here && hash && document.getElementById(hash);
    if (target) { target.scrollIntoView(); history.replaceState(null, "", "#" + hash); return; }
    location.href = d.u;
  };
  const openPal = () => {
    // remember where focus was BEFORE the mega panel goes inert
    const active = document.activeElement;
    lastFocus = active && active.closest && active.closest(".mega") ? btns.find((b) => b.dataset.world === open) || active : active;
    hide();
    const mclose = $(".menu.open [data-menu]");
    mclose && mclose.click();
    if (!pal) {
      pal = document.createElement("div");
      pal.className = "pal"; pal.setAttribute("role", "dialog"); pal.setAttribute("aria-modal", "true"); pal.setAttribute("aria-label", "Search the platform");
      pal.innerHTML = `<div class="pal-box"><div class="pal-top"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input type="text" role="combobox" aria-expanded="true" aria-controls="pal-list" aria-autocomplete="list" placeholder="Search pages, scenes, products…" aria-label="Search the platform" autocomplete="off" spellcheck="false"><kbd>esc</kbd></div><div class="pal-list" id="pal-list" role="listbox" aria-label="Results" data-lenis-prevent></div><div class="pal-foot"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>↵</kbd> open</span><span><kbd>/</kbd> search from anywhere</span></div></div>`;
      document.body.appendChild(pal);
      palInput = $("input", pal); palList = $(".pal-list", pal);
      pal.addEventListener("pointerdown", (e) => { if (e.target === pal) closePal(); });
      pal.addEventListener("wheel", (e) => { e.stopPropagation(); if (!e.target.closest(".pal-list")) e.preventDefault(); }, { passive: false });
      palInput.addEventListener("input", render);
      palList.addEventListener("pointermove", (e) => { const r = e.target.closest(".pal-row"); if (r && +r.dataset.i !== sel) { sel = +r.dataset.i; paint(); } });
      palList.addEventListener("click", (e) => { const r = e.target.closest(".pal-row"); if (!r || e.metaKey || e.ctrlKey) return; e.preventDefault(); go(rows[+r.dataset.i]); });
      pal.addEventListener("keydown", (e) => {
        if (e.key === "ArrowDown") { e.preventDefault(); sel = Math.min(rows.length - 1, sel + 1); paint(); }
        else if (e.key === "ArrowUp") { e.preventDefault(); sel = Math.max(0, sel - 1); paint(); }
        else if (e.key === "Enter") { e.preventDefault(); go(rows[sel]); }
        else if (e.key === "Tab") { e.preventDefault(); palInput.focus(); }
      });
    }
    pal.inert = false;
    palInput.value = "";
    render();
    loadIndex();
    requestAnimationFrame(() => { pal.classList.add("open"); palInput.focus(); });
  };
  document.addEventListener("click", (e) => { if (e.target.closest("[data-palette]")) { e.preventDefault(); openPal(); } });
  addEventListener("keydown", (e) => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName) || document.activeElement.isContentEditable;
    if ((e.key === "k" && (e.metaKey || e.ctrlKey)) || (e.key === "/" && !typing && !e.metaKey && !e.ctrlKey && !e.altKey)) {
      e.preventDefault();
      pal && pal.classList.contains("open") ? closePal() : openPal();
    } else if (e.key === "Escape") {
      if (pal && pal.classList.contains("open")) { e.stopPropagation(); closePal(); }
      else if (open) { const b = btns.find((x) => x.dataset.world === open); hide(); b && b.focus(); }
    }
  }, true);

  /* ---------------- home hub ---------------- */
  const hub = $(".hub");
  if (hub) {
    const wide = matchMedia("(min-width: 981px)");
    const hp = $$(".hub-panel", hub);
    const media = (x, on) => {
      const v = $("video", x);
      if (!v) return;
      if (on && wide.matches) {
        if (!v.src && v.dataset.src) v.src = v.dataset.src;
        const pr = v.play();
        pr && pr.then(() => v.classList.add("playing")).catch(() => {});
      } else { v.pause(); v.classList.remove("playing"); }
    };
    const activate = (p) => {
      if (p.classList.contains("on")) return;
      hp.forEach((x) => { x.classList.toggle("on", x === p); media(x, x === p); });
    };
    // the panel that starts open plays as soon as the hub is on screen (and stops when it leaves)
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((ents) => {
        const on = hp.find((x) => x.classList.contains("on"));
        on && media(on, ents[0].isIntersecting);
      }, { threshold: 0.25 }).observe(hub);
    }
    hp.forEach((p) => {
      p.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse" && wide.matches) activate(p); });
      p.addEventListener("focusin", () => wide.matches && activate(p));
      p.addEventListener("click", (e) => {
        if (!wide.matches || p.classList.contains("on")) return;
        e.preventDefault(); activate(p);
      });
    });
  }

  /* ---------------- prefetch on intent where speculation rules are missing ---------------- */
  if (!(HTMLScriptElement.supports && HTMLScriptElement.supports("speculationrules"))) {
    const done = new Set();
    const warm = (e) => {
      const a = e.target.closest && e.target.closest("a[href]");
      if (!a || a.target === "_blank" || a.origin !== location.origin || a.pathname === location.pathname) return;
      const url = a.origin + a.pathname;
      if (done.has(url)) return;
      done.add(url);
      const l = document.createElement("link"); l.rel = "prefetch"; l.href = url; document.head.appendChild(l);
    };
    document.addEventListener("pointerover", warm, { passive: true });
    document.addEventListener("touchstart", warm, { passive: true });
  }
})();
