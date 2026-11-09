/* COACH CARTER platform — interaction engine.
   No build step. Optional libs (GSAP, ScrollTrigger, Lenis) load from CDN;
   everything degrades to native scroll + IntersectionObserver if they fail. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* private mode */ } },
  };

  /* ---------------- loader + smooth scroll ---------------- */
  const curtain = $(".curtain");
  const reveal = () => {
    document.documentElement.classList.add("loaded");
    curtain && curtain.classList.add("up");
  };
  // lift as soon as fonts are ready (never wait on video); hard cap 1.6 s
  (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => setTimeout(reveal, 250));
  setTimeout(reveal, 1600);

  let lenis = null;
  if (!reduce && window.Lenis && !/[?&]qa\b/.test(location.search)) {
    lenis = new window.Lenis({ duration: 1.15, smoothWheel: true, wheelMultiplier: 0.95 });
    const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
  }
  const gsap = window.gsap;
  const ST = window.ScrollTrigger;
  if (gsap && ST) {
    gsap.registerPlugin(ST);
    if (lenis) lenis.on("scroll", ST.update);
  }
  const scrollTo = (y) => (lenis ? lenis.scrollTo(y) : window.scrollTo(0, y));

  /* ---------------- nav ---------------- */
  const nav = $(".nav");
  let lastY = 0;
  const onScroll = () => {
    const y = scrollY;
    if (nav) {
      nav.classList.toggle("solid", y > 40);
      nav.classList.toggle("hide", y > 500 && y > lastY + 4 && !document.body.classList.contains("menu-open"));
      if (y < lastY - 4) nav.classList.remove("hide");
    }
    lastY = y;
  };
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  const menu = $(".menu");
  const menuBtn = $(".menu-btn");
  const setMenu = (open) => {
    if (!menu) return;
    menu.classList.toggle("open", open); menu.inert = !open;
    document.body.classList.toggle("menu-open", open);
    $$("[data-menu]").forEach((x) => x.setAttribute("aria-expanded", String(open)));
    if (lenis) open ? lenis.stop() : lenis.start();
    if (open) { const f = menu.querySelector("a"); f && setTimeout(() => f.focus(), 300); } else if (menuBtn) menuBtn.focus({ preventScroll: true });
  };
  $$("[data-menu]").forEach((b) => b.addEventListener("click", () => setMenu(!menu.classList.contains("open"))));

  /* page wipe on internal navigation */
  const wipe = $(".wipe");
  $$("a[href]").forEach((a) => {
    const href = a.getAttribute("href");
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:") || a.target === "_blank" || /^https?:/.test(href) || a.hasAttribute("download")) return;
    a.addEventListener("click", (e) => {
      if (e.metaKey || e.ctrlKey || e.shiftKey || reduce || !wipe) return;
      if (a.pathname === location.pathname) return; // same page (anchor) — let it scroll
      e.preventDefault();
      wipe.classList.add("go");
      setTimeout(() => { location.href = href; }, 620);
    });
  });
  addEventListener("pageshow", (e) => { if (e.persisted && wipe) wipe.classList.remove("go"); });

  /* ---------------- reveal on scroll ---------------- */
  const io = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
  }), { rootMargin: "0px 0px -10% 0px", threshold: 0.08 });
  $$("[data-reveal], .split, .split-line").forEach((el) => io.observe(el));
  // stagger children
  $$("[data-stagger]").forEach((wrap) => {
    $$(":scope > *", wrap).forEach((c, i) => {
      c.setAttribute("data-reveal", c.getAttribute("data-reveal") || "");
      c.style.transitionDelay = `${i * 0.08}s`;
      io.observe(c);
    });
  });

  /* split headline into words for kinetic reveal */
  $$("[data-words]").forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.innerHTML = words.map((w, i) => `<span class="w"><span style="transition-delay:${i * 0.06}s">${w}</span></span>`).join(" ");
    io.observe(el);
  });

  /* ---------------- counters ---------------- */
  const cio = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return;
    const el = en.target; cio.unobserve(el);
    const to = parseFloat(el.dataset.count); const dec = (el.dataset.count.split(".")[1] || "").length;
    const pre = el.dataset.pre || ""; const suf = el.dataset.suf || "";
    if (reduce) { el.textContent = pre + to.toFixed(dec) + suf; return; }
    const t0 = performance.now(); const dur = 1800;
    const tick = (t) => {
      const p = clamp((t - t0) / dur, 0, 1); const e = 1 - Math.pow(1 - p, 4);
      el.textContent = pre + (to * e).toFixed(dec) + suf;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }), { threshold: 0.4 });
  $$("[data-count]").forEach((el) => cio.observe(el));

  /* ---------------- videos: play only when visible ---------------- */
  const vio = new IntersectionObserver((ents) => ents.forEach((en) => {
    const v = en.target;
    if (en.isIntersecting) { if (v.dataset.src && !v.src) { v.src = v.dataset.src; } const p = v.play(); p && p.catch(() => {}); }
    else v.pause();
  }), { threshold: 0.05 });
  $$("video[data-auto]").forEach((v) => {
    v.muted = true; v.playsInline = true;
    if (v.dataset.mobile && innerWidth < 760) { v.src = v.dataset.mobile; }
    vio.observe(v);
  });

  /* ---------------- cursor + glow + magnetic ---------------- */
  if (fine && !reduce) {
    const dot = document.createElement("div"); dot.className = "cur-dot";
    const ring = document.createElement("div"); ring.className = "cur-ring";
    document.body.append(dot, ring);
    let mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my;
    addEventListener("pointermove", (e) => { document.body.classList.add("cur-on"); mx = e.clientX; my = e.clientY; dot.style.transform = `translate(${mx}px,${my}px)`; }, { passive: true });
    const loop = () => { rx += (mx - rx) * 0.16; ry += (my - ry) * 0.16; ring.style.transform = `translate(${rx}px,${ry}px)`; requestAnimationFrame(loop); };
    loop();
    document.addEventListener("pointerover", (e) => {
      const t = e.target.closest("a, button, [data-cursor], input, select, textarea, .sigpad");
      ring.classList.toggle("big", !!t && !t.matches("input, textarea, select, .sigpad"));
      ring.dataset.label = t && t.dataset.cursor ? t.dataset.cursor : "";
      ring.classList.toggle("label", !!(t && t.dataset.cursor));
    });
    document.documentElement.addEventListener("pointerleave", () => document.body.classList.remove("cur-on"));

    $$("[data-magnetic]").forEach((el) => {
      el.addEventListener("pointermove", (e) => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) * 0.25; const y = (e.clientY - r.top - r.height / 2) * 0.35;
        el.style.transform = `translate(${x}px,${y}px)`;
      });
      el.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });
    $$("[data-tilt]").forEach((el) => {
      const base = el.style.transform;
      el.parentElement.addEventListener("pointermove", (e) => {
        const r = el.parentElement.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5; const y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = `rotateY(${-18 + x * 30}deg) rotateX(${4 - y * 16}deg)`;
      });
      el.parentElement.addEventListener("pointerleave", () => { el.style.transform = base; });
    });
  }
  $$(".glow").forEach((el) => el.addEventListener("pointermove", (e) => {
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", `${e.clientX - r.left}px`); el.style.setProperty("--my", `${e.clientY - r.top}px`);
  }));

  /* ---------------- gold dust + light cone (canvas) ---------------- */
  $$("canvas.dust").forEach((cv) => {
    if (reduce) return;
    const ctx = cv.getContext("2d");
    let w, h, dpr, parts = [], px = -9999, py = -9999, visible = true;
    const N = innerWidth < 700 ? 70 : 150;
    const size = () => {
      dpr = Math.min(devicePixelRatio || 1, 2);
      w = cv.clientWidth; h = cv.clientHeight; cv.width = w * dpr; cv.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    size(); addEventListener("resize", size);
    const spawn = (init) => ({
      x: w * (0.25 + Math.random() * 0.5), y: init ? Math.random() * h : h + 10,
      r: Math.random() * 1.7 + 0.3, vy: -(Math.random() * 0.35 + 0.08), vx: (Math.random() - 0.5) * 0.15,
      a: Math.random() * 0.7 + 0.15, tw: Math.random() * Math.PI * 2,
    });
    for (let i = 0; i < N; i++) parts.push(spawn(true));
    cv.parentElement.addEventListener("pointermove", (e) => { const r = cv.getBoundingClientRect(); px = e.clientX - r.left; py = e.clientY - r.top; });
    cv.parentElement.addEventListener("pointerleave", () => { px = py = -9999; });
    new IntersectionObserver(([en]) => { visible = en.isIntersecting; }).observe(cv);
    const cone = cv.dataset.cone !== "off";
    let t = 0;
    const draw = () => {
      requestAnimationFrame(draw);
      if (!visible) return;
      t += 0.004;
      ctx.clearRect(0, 0, w, h);
      if (cone) {
        const sway = Math.sin(t) * w * 0.02;
        const g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, "rgba(255,236,190,0.16)"); g.addColorStop(0.7, "rgba(233,207,149,0.04)"); g.addColorStop(1, "rgba(233,207,149,0)");
        ctx.fillStyle = g; ctx.beginPath();
        ctx.moveTo(w / 2 - w * 0.03 + sway, 0); ctx.lineTo(w / 2 + w * 0.03 + sway, 0);
        ctx.lineTo(w / 2 + w * 0.34, h); ctx.lineTo(w / 2 - w * 0.34, h); ctx.closePath(); ctx.fill();
      }
      for (const p of parts) {
        p.tw += 0.03; p.x += p.vx + Math.sin(p.tw * 0.5) * 0.08; p.y += p.vy;
        const dx = p.x - px, dy = p.y - py, d2 = dx * dx + dy * dy;
        if (d2 < 14000) { const f = (14000 - d2) / 14000; p.x += (dx / Math.sqrt(d2 + 1)) * f * 2.4; p.y += (dy / Math.sqrt(d2 + 1)) * f * 2.4; }
        if (p.y < -10 || p.x < -10 || p.x > w + 10) Object.assign(p, spawn(false));
        const a = p.a * (0.55 + Math.sin(p.tw) * 0.45);
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(246,227,180,${a})`; ctx.shadowColor = "rgba(233,207,149,.9)"; ctx.shadowBlur = p.r * 6; ctx.fill();
      }
      ctx.shadowBlur = 0;
    };
    draw();
  });

  /* ---------------- scroll engine helpers ---------------- */
  const progressOf = (el) => {
    const r = el.getBoundingClientRect();
    const total = r.height - innerHeight;
    return clamp(-r.top / (total || 1), 0, 1);
  };
  const scrollers = [];
  const onFrame = () => { scrollers.forEach((fn) => fn()); };
  addEventListener("scroll", () => requestAnimationFrame(onFrame), { passive: true });
  addEventListener("resize", onFrame);

  /* pinned chapters */
  $$(".story").forEach((story) => {
    const chs = $$(".chapter", story); const media = $$(".story-media > *", story);
    const bars = $$(".story-progress b", story); const yearEl = $(".story-year", story);
    let cur = -1;
    scrollers.push(() => {
      const p = progressOf(story);
      const i = Math.min(chs.length - 1, Math.floor(p * chs.length * 0.999));
      bars.forEach((b, k) => { b.classList.toggle("on", k <= i); });
      if (i === cur) return; cur = i;
      chs.forEach((c, k) => c.classList.toggle("on", k === i));
      const mi = chs[i].dataset.media ? +chs[i].dataset.media : i;
      media.forEach((m, k) => {
        const on = k === mi; m.classList.toggle("on", on);
        if (m.tagName === "VIDEO") { if (on) { const pr = m.play(); pr && pr.catch(() => {}); } else m.pause(); }
      });
      if (yearEl) yearEl.textContent = chs[i].dataset.year || "";
    });
  });

  /* scroll-scrubbed video (all-intra encode → smooth seeking) */
  $$(".scrub").forEach((sec) => {
    const v = $("video", sec); const caps = $$(".scrub-cap", sec);
    if (!v) return;
    v.muted = true;
    let target = 0;
    // load the whole clip as a blob so every frame is seekable on any host
    new IntersectionObserver(([en], ob) => {
      if (!en.isIntersecting) return; ob.disconnect();
      fetch(v.dataset.src).then((r) => { if (!r.ok) throw new Error(r.status); return r.blob(); })
        .then((blob) => { v.src = URL.createObjectURL(blob); v.load(); })
        .catch(() => { v.src = v.dataset.src; v.preload = "auto"; v.load(); });
    }, { rootMargin: "150% 0px" }).observe(sec);
    scrollers.push(() => {
      const p = progressOf(sec);
      progress = p;
      caps.forEach((c) => { const a = +c.dataset.from, b = +c.dataset.to; c.classList.toggle("on", p >= a && p < b); });
      sec.style.setProperty("--p", p.toFixed(4));
    });
    let last = 0, progress = 0;
    const seek = () => {
      requestAnimationFrame(seek);
      if (v.readyState < 1 || !v.duration) return;
      target = progress * (v.duration - 0.05);
      if (Math.abs(target - last) > 0.01 && !v.seeking) { last += (target - last) * 0.3; if (Math.abs(target - last) < 0.02) last = target; v.currentTime = last; }
    };
    seek();
  });

  /* video-through-type zoom */
  $$(".zoomtype").forEach((sec) => {
    const mask = $(".zt-mask", sec); const after = $(".zt-after", sec); const target = $(".zt-i", sec);
    const aim = () => {
      if (!target) return;
      mask.style.transform = "none";
      const m = mask.getBoundingClientRect(); const t = target.getBoundingClientRect();
      mask.style.transformOrigin = `${t.left + t.width / 2 - m.left}px ${t.top + t.height * 0.55 - m.top}px`;
    };
    aim(); addEventListener("resize", aim); document.fonts && document.fonts.ready.then(aim);
    if (reduce) { mask.style.display = "none"; if (after) after.style.opacity = "1"; return; }
    scrollers.push(() => {
      const p = progressOf(sec);
      const s = 1 + Math.pow(p, 2.6) * 38;
      mask.style.transform = `scale(${s})`;
      mask.style.opacity = String(1 - clamp((p - 0.82) / 0.12, 0, 1));
      if (after) after.style.opacity = String(clamp((p - 0.86) / 0.1, 0, 1));
    });
  });

  /* horizontal pinned reel */
  $$(".hreel").forEach((sec) => {
    const track = $(".hreel-track", sec);
    const setH = () => { sec.style.height = `${track.scrollWidth - innerWidth + innerHeight * 1.2}px`; };
    setH(); addEventListener("resize", setH); addEventListener("load", setH);
    scrollers.push(() => {
      const p = progressOf(sec);
      track.style.transform = `translate3d(${-p * (track.scrollWidth - innerWidth + 40)}px,0,0)`;
      const bar = $(".hreel-bar i", sec); if (bar) bar.style.transform = `scaleX(${p})`;
    });
  });

  /* lightweight parallax */
  $$("[data-parallax]").forEach((el) => {
    const amt = parseFloat(el.dataset.parallax) || 0.15;
    scrollers.push(() => {
      const r = el.parentElement.getBoundingClientRect();
      const c = r.top + r.height / 2 - innerHeight / 2;
      el.style.transform = `translate3d(0,${c * -amt}px,0) scale(${1 + amt * 0.6})`;
    });
  });
  onFrame();

  /* ---------------- scoreboard flip digits ---------------- */
  $$(".scoreboard").forEach((sb) => {
    const digits = $$(".flip", sb);
    const sio = new IntersectionObserver(([en]) => {
      if (!en.isIntersecting) return; sio.disconnect();
      digits.forEach((d, i) => {
        const to = d.dataset.to; let n = 0; const steps = 8 + i * 3;
        const tick = () => {
          d.classList.remove("f"); void d.offsetWidth; d.classList.add("f");
          d.textContent = n >= steps ? to : String(Math.floor(Math.random() * 10));
          if (n++ < steps) setTimeout(tick, 70 + n * 6);
        };
        setTimeout(tick, i * 120);
      });
      setTimeout(() => sb.classList.add("final"), 1900);
    }, { threshold: 0.5 });
    sio.observe(sb);
  });

  /* ---------------- toast ---------------- */
  const toast = $(".toast");
  let tT;
  const say = (msg) => { if (!toast) return; $("span", toast).textContent = msg; toast.classList.add("on"); clearTimeout(tT); tT = setTimeout(() => toast.classList.remove("on"), 3200); };
  window.CC = { say, store, scrollTo };

  /* ---------------- modals ---------------- */
  const scrim = $(".scrim");
  let lastFocus = null;
  const layers = $$(".modal, .drawer, .menu");
  layers.forEach((l) => { l.inert = true; });
  const focusIn = (el) => { const f = el.querySelector("button, a[href], input, select, textarea, video[controls]"); f && setTimeout(() => f.focus({ preventScroll: true }), 60); };
  const openModal = (m) => {
    lastFocus = document.activeElement; m.inert = false; m.classList.add("on"); scrim.classList.add("on"); lenis && lenis.stop(); focusIn(m);
  };
  const closeAll = () => {
    $$(".modal.on, .drawer.on").forEach((m) => { m.classList.remove("on"); m.inert = true; });
    scrim && scrim.classList.remove("on");
    $$(".modal video").forEach((v) => v.pause());
    lenis && lenis.start();
    if (lastFocus && lastFocus.focus) { lastFocus.focus({ preventScroll: true }); lastFocus = null; }
  };
  $$(".modal").forEach((m) => m.addEventListener("click", (e) => { if (e.target === m) closeAll(); }));
  window.CC_layers = { openModal };
  window.CC.openModal = openModal; window.CC.closeAll = closeAll;
  scrim && scrim.addEventListener("click", closeAll);
  $$("[data-close]").forEach((b) => b.addEventListener("click", closeAll));
  addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (menu && menu.classList.contains("open")) { setMenu(false); return; }
    closeAll();
  });
  $$("[data-video]").forEach((b) => b.addEventListener("click", () => {
    const m = $("#video-modal"); const v = $("video", m);
    if (v.getAttribute("src") !== b.dataset.video) { v.src = b.dataset.video; if (b.dataset.poster) v.poster = b.dataset.poster; }
    openModal(m); v.currentTime = 0; const p = v.play(); p && p.catch(() => {});
  }));
  $$("[data-modal]").forEach((b) => b.addEventListener("click", () => openModal($(b.dataset.modal))));

  /* ---------------- signature contract ---------------- */
  $$(".sigpad").forEach((pad) => {
    const cv = $("canvas", pad); const ctx = cv.getContext("2d"); const hint = $(".hint", pad);
    const wrap = pad.closest(".contract"); const stamp = $(".stamp", wrap); const out = $("[data-signed]", wrap);
    let drawing = false, lx = 0, ly = 0, ink = 0;
    const fit = () => { const r = cv.getBoundingClientRect(); const d = Math.min(devicePixelRatio || 1, 2); cv.width = r.width * d; cv.height = r.height * d; ctx.setTransform(d, 0, 0, d, 0, 0); ctx.lineCap = "round"; ctx.lineJoin = "round"; ctx.strokeStyle = "#1a1530"; };
    fit(); addEventListener("resize", fit);
    const pos = (e) => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
    cv.addEventListener("pointerdown", (e) => { drawing = true; [lx, ly] = pos(e); cv.setPointerCapture(e.pointerId); hint && (hint.style.opacity = 0); });
    cv.addEventListener("pointermove", (e) => {
      if (!drawing) return; const [x, y] = pos(e); const d = Math.hypot(x - lx, y - ly);
      ctx.lineWidth = clamp(3.2 - d * 0.08, 1.1, 3.2); ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(x, y); ctx.stroke();
      ink += d; lx = x; ly = y;
    });
    const end = () => {
      if (!drawing) return; drawing = false;
      if (ink > 140 && stamp && !stamp.classList.contains("on")) {
        stamp.classList.add("on"); out && (out.textContent = new Date().toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" }));
        say("Contract signed. Welcome to the team.");
        if (navigator.vibrate) navigator.vibrate(30);
      }
    };
    cv.addEventListener("pointerup", end); cv.addEventListener("pointercancel", end);
    const clr = $("[data-clear]", wrap);
    clr && clr.addEventListener("click", () => { ctx.clearRect(0, 0, cv.width, cv.height); ink = 0; stamp && stamp.classList.remove("on"); hint && (hint.style.opacity = 1); out && (out.textContent = "________"); });
  });

  /* ---------------- multi-step forms ---------------- */
  $$("[data-wizard]").forEach((form) => {
    const steps = $$(".step", form); const bars = $$(".steps b", form);
    let i = 0;
    const show = () => { steps.forEach((s, k) => s.classList.toggle("on", k === i)); bars.forEach((b, k) => b.classList.toggle("on", k <= i)); };
    form.addEventListener("click", (e) => {
      const nx = e.target.closest("[data-next]"); const pv = e.target.closest("[data-prev]");
      if (nx) {
        const req = $$("[required]", steps[i]).filter((f) => !f.checkValidity());
        if (req.length) { req[0].reportValidity(); return; }
        i = Math.min(steps.length - 1, i + 1); show();
      }
      if (pv) { i = Math.max(0, i - 1); show(); }
    });
    form.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" || e.target.tagName === "TEXTAREA" || e.target.tagName === "BUTTON") return;
      const nx = steps[i] && steps[i].querySelector("[data-next]");
      if (nx) { e.preventDefault(); nx.click(); }
    });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const log = store.get("cc_inquiries", []); log.push({ at: new Date().toISOString(), form: form.dataset.wizard, ...data }); store.set("cc_inquiries", log);
      form.innerHTML = `<div class="sent"><img src="assets/brand/crest_gold.svg" alt="" width="120" height="120"><h3 class="h-m">Request received.</h3><p class="body-mute">Coach Carter's team will be in touch within two business days.</p><p class="body-mute internal" style="font-size:13px">Review note: preview saves inquiries on this device only; connect to the booking inbox before launch.</p></div>`;
      say("Request received");
    });
    show();
  });

  $$("form[data-simple]").forEach((f) => f.addEventListener("submit", (e) => {
    e.preventDefault(); f.reset(); say(f.dataset.simple || "Thank you");
  }));

  /* ---------------- partner package builder ---------------- */
  $$(".builder").forEach((b) => {
    const out = $(".b-out", b);
    const calc = () => {
      const goal = ($("input[name=goal]:checked", b) || {}).value || "culture";
      const size = +($("input[name=size]", b) || { value: 500 }).value;
      const reach = $$("input[name=reach]:checked", b).map((x) => x.value);
      $(".b-size", b).textContent = size >= 10000 ? "10,000+" : size.toLocaleString();
      let pkg, desc, items;
      if (reach.includes("license") || reach.includes("series")) {
        pkg = "Legacy Partner"; desc = "Brand licensing and the Coach Carter Academy series under one agreement.";
        items = ["Co-branded campaign rights", "Series integration", "2 keynotes per year", "Foundation impact report"];
      } else if (size > 2500 || reach.includes("content")) {
        pkg = "Championship Series"; desc = "A keynote tour across your offices plus content your teams keep.";
        items = ["Up to 4 keynotes", "Filmed session + cut-downs", "Signed books for leadership", "Accountability workshop"];
      } else {
        pkg = "Locker Room Keynote"; desc = "One keynote and a leadership session built around your goal.";
        items = ["Keynote (45–60 min)", "Q&A with leadership", "Signed copies of Yes Ma'am, No Sir", "Pre-event discovery call"];
      }
      const goals = { culture: "Accountability culture", sales: "Sales performance", youth: "Youth & community", diversity: "Leadership pipeline" };
      out.innerHTML = `<div class="tag">Recommended</div><h4 class="h-m" style="margin:16px 0 8px">${pkg}</h4><p class="body-mute" style="margin:0 0 18px">${desc}</p><ul>${items.map((x) => `<li>${x}</li>`).join("")}</ul><div class="b-goal">Built for: <b>${goals[goal]}</b> · ${$(".b-size", b).textContent} people</div>`;
      out.classList.remove("pop"); void out.offsetWidth; out.classList.add("pop");
    };
    b.addEventListener("input", calc); calc();
  });

  /* ---------------- Getty editorial embeds (official embed player, lazy) ---------------- */
  const gSlots = $$("[data-getty]");
  if (gSlots.length) {
    const base = document.querySelector('script[src*="site.js"]').src.replace(/assets\/js\/site\.js.*$/, "");
    fetch(base + "assets/data/getty.json").then((r) => r.json()).then((list) => {
      const byId = Object.fromEntries(list.map((g) => [g.id, g]));
      const gio = new IntersectionObserver((ents) => ents.forEach((en) => {
        if (!en.isIntersecting) return; gio.unobserve(en.target);
        const el = en.target; const g = byId[el.dataset.getty]; if (!g) return;
        const f = document.createElement("iframe");
        f.src = `https://embed.gettyimages.com/embed/${g.id}?et=${encodeURIComponent(g.et)}&tld=com&sig=${encodeURIComponent(g.sig)}&caption=false&ver=1`;
        f.title = `${g.title} — Getty Images`; f.loading = "lazy"; f.scrolling = "no"; f.setAttribute("frameborder", "0");
        f.addEventListener("load", () => el.classList.add("ready"));
        el.appendChild(f);
      }), { rootMargin: "400px 0px" });
      gSlots.forEach((el) => {
        const g = byId[el.dataset.getty]; if (!g) { el.closest(".gx") && el.closest(".gx").remove(); return; }
        el.style.aspectRatio = `${g.w} / ${g.h + 34}`;
        const cap = el.parentElement.querySelector("figcaption");
        if (cap && !cap.textContent.trim()) cap.innerHTML = `<b>${g.title}</b><span>${g.where}</span>`;
        gio.observe(el);
      });
    }).catch(() => {});
  }

  /* ---------------- YouTube click-to-load ---------------- */
  document.addEventListener("click", (e) => {
    const b = e.target.closest(".cinema [data-yt]"); if (!b) return;
    const box = b.closest(".cinema");
    box.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.yt}?autoplay=1&rel=0" title="Coach Ken Carter video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen style="position:absolute;inset:0;width:100%;height:100%;border:0"></iframe>`;
  });

  /* ---------------- countdowns ---------------- */
  $$("[data-countdown]").forEach((el) => {
    const t = new Date(el.dataset.countdown).getTime();
    const tick = () => {
      const d = Math.max(0, t - Date.now());
      const v = { d: Math.floor(d / 864e5), h: Math.floor(d / 36e5) % 24, m: Math.floor(d / 6e4) % 60 };
      $$("[data-u]", el).forEach((b) => { b.textContent = String(v[b.dataset.u]).padStart(b.dataset.u === "d" ? 1 : 2, "0"); });
    };
    tick(); setInterval(tick, 30000);
  });

  /* ---------------- year in footer ---------------- */
  $$("[data-curyear]").forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
