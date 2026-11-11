/* Coach's Briefing (coach.html only): sticky position bar, Index sheet, fold/unfold of the "In full" detail.
   Markup comes from tools/build.py coach_sections(). All content stays in the DOM; <details> only folds it. */
(() => {
  const bar = document.querySelector(".ch-bar");
  if (!bar) return;
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const secs = $$(".ch-sec");
  const parts = $$(".ch-part");
  const mores = $$("details.ch-more");
  const hero = document.querySelector(".ch-hero");
  const end = document.querySelector(".ch-end");
  const sheet = document.getElementById("ch-sheet");
  const idxBtn = bar.querySelector(".ch-bar-idx");
  const allBtn = bar.querySelector(".ch-bar-all");
  const elPart = bar.querySelector(".ch-bar-part");
  const elN = bar.querySelector(".ch-bar-n b");
  const elT = bar.querySelector(".ch-bar-t");
  const line = bar.querySelector(".ch-bar-line i");
  const root = document.documentElement;
  const barBottom = () => bar.getBoundingClientRect().bottom;

  /* ---------- where am I ---------- */
  let cur = null, ticking = false;
  const frame = () => {
    ticking = false;
    const vh = innerHeight, probe = Math.max(barBottom() + 8, vh * 0.32);
    bar.classList.toggle("on", hero ? hero.getBoundingClientRect().bottom < barBottom() : scrollY > 400);
    let s = null;
    for (const el of secs) { if (el.getBoundingClientRect().top <= probe) s = el; else break; }
    let p = null;
    for (const el of parts) { if (el.getBoundingClientRect().top <= probe) p = el; else break; }
    if (s && p && !p.contains(s)) s = null;            // inside a part opener, before its first section
    const key = s ? s.id : p ? p.id : "idx";
    if (key !== cur) {
      cur = key;
      if (s) {
        elPart.textContent = `Part ${s.dataset.part}`;
        elN.textContent = String(s.dataset.n).padStart(2, "0");
        elT.textContent = s.dataset.title;
      } else if (p) {
        elPart.textContent = `Part ${p.id.split("-")[1]}`;
        const ns = $$(".ch-sec", p).map((x) => String(x.dataset.n).padStart(2, "0"));
        elN.textContent = ns.length > 1 ? ns[0] + "–" + ns[ns.length - 1] : (ns[0] || "");
        elT.textContent = p.dataset.title;
      } else {
        elPart.textContent = "Index";
        elN.textContent = "00";
        elT.textContent = "What this covers";
      }
      $$("a[aria-current]", sheet).forEach((a) => a.removeAttribute("aria-current"));
      if (s) { const a = sheet.querySelector(`a[href="#${s.id}"]`); a && a.setAttribute("aria-current", "location"); }
    }
    // progress through the briefing body (part 1 start → end note)
    const a0 = parts.length ? parts[0].getBoundingClientRect().top + scrollY : 0;
    const a1 = end ? end.getBoundingClientRect().top + scrollY - vh : root.scrollHeight - vh;
    const f = Math.min(1, Math.max(0, (scrollY - a0 + vh * 0.32) / Math.max(1, a1 - a0 + vh * 0.32)));
    line.style.transform = `scaleX(${f.toFixed(4)})`;
  };
  const onScroll = () => { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);

  /* ---------- expand / collapse all ---------- */
  const syncAll = () => {
    const all = mores.length && mores.every((d) => d.open);
    allBtn.setAttribute("aria-pressed", String(all));
  };
  const keepPlace = (fn, collapsing) => {
    // keep the section being read in the same place; if collapsing from deep inside it, land on its head
    const anchor = (cur && document.getElementById(cur)) || null;
    const before = anchor ? anchor.getBoundingClientRect().top : 0;
    root.classList.add("ch-instant");
    fn();
    requestAnimationFrame(() => {
      if (anchor) {
        const top = anchor.getBoundingClientRect().top;
        const want = collapsing && before < 0 ? barBottom() + 12 : before;
        window.scrollTo(0, scrollY + top - want);
      }
      requestAnimationFrame(() => root.classList.remove("ch-instant"));
      onScroll();
    });
  };
  allBtn.addEventListener("click", () => {
    const open = allBtn.getAttribute("aria-pressed") !== "true";
    keepPlace(() => mores.forEach((d) => { d.open = open; }), !open);
    allBtn.setAttribute("aria-pressed", String(open));
  });
  mores.forEach((d) => d.addEventListener("toggle", () => { syncAll(); onScroll(); }));

  /* "Close … in full" at the bottom of a long detail: fold it and return to its summary */
  $$(".ch-more-close").forEach((b) => b.addEventListener("click", () => {
    const d = b.closest("details"), sum = d.querySelector("summary");
    root.classList.add("ch-instant");
    d.open = false;
    requestAnimationFrame(() => {
      const top = d.closest(".ch-sec").getBoundingClientRect().top;
      window.scrollTo(0, scrollY + top - barBottom() - 12);
      sum.focus({ preventScroll: true });
      requestAnimationFrame(() => root.classList.remove("ch-instant"));
    });
  }));

  /* ---------- hash targets: open the fold that holds (or belongs to) the target ---------- */
  const reveal = (hash, jump) => {
    if (!hash || hash.length < 2) return;
    let el = null;
    try { el = document.getElementById(decodeURIComponent(hash.slice(1))); } catch (e) { return; }
    if (!el) return;
    let opened = false;
    for (let d = el.closest("details"); d; d = d.parentElement && d.parentElement.closest("details")) {
      if (!d.open) { root.classList.add("ch-instant"); d.open = true; opened = true; }
    }
    if (el.classList.contains("ch-sec")) {
      const d = el.querySelector(":scope > details.ch-more");
      if (d && !d.open) { root.classList.add("ch-instant"); d.open = true; }
    }
    if (opened || jump) requestAnimationFrame(() => { el.scrollIntoView({ block: "start" }); requestAnimationFrame(() => root.classList.remove("ch-instant")); });
    else requestAnimationFrame(() => root.classList.remove("ch-instant"));
  };
  addEventListener("hashchange", () => reveal(location.hash, false));
  // same-hash clicks fire no hashchange: catch them too
  document.addEventListener("click", (e) => {
    const a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute("href") === location.hash) reveal(location.hash, true);
  });
  if (location.hash) reveal(location.hash, true);

  /* find-in-page: Chromium opens <details> itself; keep the bar state in step */
  document.addEventListener("beforematch", onScroll, true);

  /* print: everything open, then restore */
  let printed = null;
  addEventListener("beforeprint", () => { printed = mores.map((d) => d.open); mores.forEach((d) => { d.open = true; }); });
  addEventListener("afterprint", () => { if (printed) mores.forEach((d, i) => { d.open = printed[i]; }); printed = null; });

  /* ---------- Index sheet ---------- */
  if (sheet && sheet.showModal) {
    const open = () => {
      sheet.showModal();
      idxBtn.setAttribute("aria-expanded", "true");
      root.classList.add("ch-sheet-open");
      const here = sheet.querySelector("a[aria-current]");
      if (here) here.scrollIntoView({ block: "center" });
      (here || sheet.querySelector("a")).focus({ preventScroll: true });
    };
    idxBtn.addEventListener("click", open);
    sheet.querySelector(".ch-sheet-x").addEventListener("click", () => sheet.close());
    sheet.addEventListener("close", () => { idxBtn.setAttribute("aria-expanded", "false"); root.classList.remove("ch-sheet-open"); if (!sheet.dataset.go) idxBtn.focus({ preventScroll: true }); delete sheet.dataset.go; });
    sheet.addEventListener("click", (e) => {
      if (e.target === sheet) { sheet.close(); return; }           // backdrop
      const a = e.target.closest("a[href^='#']");
      if (a) { sheet.dataset.go = "1"; sheet.close(); }            // let the link navigate natively
    });
  } else if (idxBtn) {
    idxBtn.addEventListener("click", () => { location.hash = "covers"; });
  }

  /* ---------- wide tables that still scroll (641px and up) get a keyboard stop ---------- */
  const tabs = $$(".ch-table");
  const tabStops = () => tabs.forEach((t) => {
    if (t.offsetParent === null) return;
    if (t.scrollWidth > t.clientWidth + 1) t.setAttribute("tabindex", "0"); else t.removeAttribute("tabindex");
    t.classList.toggle("is-scroll", t.scrollWidth > t.clientWidth + 1);
  });
  mores.forEach((d) => d.addEventListener("toggle", () => d.open && tabStops()));
  addEventListener("resize", () => { clearTimeout(tabStops.t); tabStops.t = setTimeout(tabStops, 150); });

  syncAll();
  frame();
})();
