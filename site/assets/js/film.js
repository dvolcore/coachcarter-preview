/* The 2005 film, everywhere it belongs. Data: assets/data/film.json.
   Scenes play from self-hosted MP4s (media repo, no ads); YouTube is the fallback when a file is missing.
   Slots: <div data-film="feature|rail|strip|library|realcarter|stills|band|loop|quote|realfilm|premiere"
               data-ids="slug-or-youtube-id,…" data-q="0,2" data-n="6" data-still="key" data-loop="key"></div> */
(() => {
  "use strict";
  const slots = Array.from(document.querySelectorAll("[data-film]"));
  if (!slots.length) return;
  const base = document.querySelector('script[src*="film.js"]').src.replace(/assets\/js\/film\.js.*$/, "");
  const esc = (s) => String(s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const mmss = (s) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`;
  const PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>';
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  let F, byKey = {};

  /* ---- player (modal) ---- */
  let player, lastFocus;
  const close = () => { if (!player) return; player.classList.remove("on"); player.querySelector(".fp-box").innerHTML = ""; document.documentElement.classList.remove("fp-lock"); lastFocus && lastFocus.focus(); };
  const play = (key, start = 0, title) => {
    const c = byKey[key] || {};
    title = title || `Coach Carter (2005) · ${c.scene || ""}`;
    if (!player) {
      player = document.createElement("div"); player.className = "fplayer"; player.setAttribute("role", "dialog"); player.setAttribute("aria-modal", "true"); player.setAttribute("aria-label", "Film scene");
      player.innerHTML = '<div class="fp-in"><button class="fp-x" type="button" aria-label="Close video">×</button><div class="fp-box"></div><p class="fp-cap"></p></div>';
      document.body.appendChild(player);
      player.addEventListener("click", (e) => { if (e.target === player || e.target.closest(".fp-x")) close(); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape" && player.classList.contains("on")) close(); });
    }
    lastFocus = document.activeElement;
    const box = player.querySelector(".fp-box");
    box.style.aspectRatio = c.aspect ? String(c.aspect) : "16 / 9";
    if (c.src) {
      box.innerHTML = `<video controls autoplay playsinline preload="auto" poster="${base + c.poster}"><source src="${c.src}" type="video/mp4"></video>`;
      const v = box.querySelector("video");
      if (start) v.addEventListener("loadedmetadata", () => { v.currentTime = start; }, { once: true });
      v.addEventListener("error", () => yt(box, c, start, title), true);
    } else yt(box, c, start, title);
    player.querySelector(".fp-cap").innerHTML = `${esc(title)} · <span>Coach Carter © 2005 Paramount Pictures / MTV Films</span>`;
    player.classList.add("on"); document.documentElement.classList.add("fp-lock"); player.querySelector(".fp-x").focus();
  };
  const yt = (box, c, start, title) => {
    if (!c.yt) return;
    box.style.aspectRatio = "16 / 9";
    box.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${c.yt}?autoplay=1&rel=0&modestbranding=1${start ? `&start=${start}` : ""}" title="${esc(title)}" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`;
  };
  document.addEventListener("click", (e) => { const b = e.target.closest("[data-fclip]"); if (!b) return; e.preventDefault(); play(b.dataset.fclip, +b.dataset.start || 0, b.dataset.ftitle); });

  fetch(base + "assets/data/film.json").then((r) => r.json()).then((data) => {
    F = data;
    const media = F.media_base || "";
    const all = [F.trailer.primary, ...F.clips, ...(F.real_carter || [])];
    all.forEach((c) => {
      if (c.file && media) c.src = media + c.file;
      [c.slug, c.id, c.yt].filter(Boolean).forEach((k) => (byKey[k] = c));
    });
    const T = F.trailer.primary;
    const scenes = F.clips.slice().sort((a, b) => a.order - b.order);
    const stillBy = Object.fromEntries((F.bands || []).map((s) => [s.key, s]));
    const poster = (c) => (c.poster ? base + c.poster : `https://i.ytimg.com/vi/${c.yt || c.id}/hqdefault.jpg`);
    const credit = '<p class="fcredit"><em>Coach Carter</em> © 2005 Paramount Pictures / MTV Films. Scenes included for private client review.</p>';

    const card = (c) => `<button class="fcard" type="button" data-fclip="${c.slug}" aria-label="Play scene: ${esc(c.scene)}">
        <span class="fthumb"><img src="${poster(c)}" alt="" loading="lazy"><i class="fplay">${PLAY}</i><em>${c.duration}</em></span>
        <span class="fmeta"><small>${c.act_label ? esc(c.act_label) + " · " : ""}Scene ${c.order} of ${scenes.length}</small><b>${esc(c.scene)}</b><span>${esc(c.hook || c.description)}</span></span></button>`;

    const quote = (q, i) => {
      const c = q.clip && byKey[q.clip];
      const st = Math.max(0, (q.t_s || 0) - 3);
      const img = c ? `<button class="fq-still" type="button" data-fclip="${c.slug}" data-start="${st}" aria-label="Play the scene"><img src="${q.still ? base + stillBy[q.still].src_sm : poster(c)}" alt="" loading="lazy"><i class="fplay">${PLAY}</i></button>` : "";
      return `<figure class="fq${i ? "" : " on"}${img ? " has-still" : ""}" data-i="${i}">${img}<blockquote>“${esc(q.text)}”</blockquote>
        <figcaption><b>${esc(q.speaker)}</b><span>${q.actor ? esc(q.actor) + " · " : ""}Coach Carter (2005)</span>
        ${/Williamson/.test(q.attribution || "") ? '<span class="fq-attr">Adapted from Marianne Williamson, <em>A Return to Love</em> (1992)</span>' : ""}</figcaption>
        ${c ? `<button class="btn btn-ghost btn-sm" type="button" data-fclip="${c.slug}" data-start="${st}">${PLAY}<span>Watch the scene</span></button>` : ""}</figure>`;
    };

    const R = {
      feature(el) {
        el.innerHTML = `<div class="ffeature">
          <button class="ftrailer" type="button" data-fclip="trailer" data-ftitle="Coach Carter (2005) · Original trailer" aria-label="Play the original 2005 trailer">
            <img src="${base + (stillBy["team-lineup"] ? stillBy["team-lineup"].src : T.poster)}" alt="Coach Carter, 2005: the Richmond team lines up on day one" loading="lazy">
            <span class="ft-over"><span class="eyebrow">Paramount Pictures · MTV Films · January 14, 2005</span><b>Coach Carter</b><span class="ft-cta"><i class="fplay">${PLAY}</i>Watch the original trailer · ${mmss(T.duration_s)}</span></span>
          </button>
          <dl class="ffacts">
            <div><dt>Opening</dt><dd>#1 at the U.S. box office</dd></div>
            <div><dt>Starring</dt><dd>Samuel L. Jackson as Coach Ken Carter</dd></div>
            <div><dt>Director</dt><dd>${esc((F.facts.find((x) => x.key === "director") || {}).value)}</dd></div>
            <div><dt>Cast</dt><dd>Rob Brown, Robert Ri'chard, Rick Gonzalez, Channing Tatum, Ashanti</dd></div>
            <div><dt>Honors</dt><dd>NAACP Image Award, Outstanding Actor · CinemaScore A</dd></div>
          </dl></div>
          <div class="frail" role="list">${scenes.map((c) => `<div role="listitem">${card(c)}</div>`).join("")}</div>${credit}`;
      },
      rail(el) { el.innerHTML = `<div class="frail" role="list">${scenes.map((c) => `<div role="listitem">${card(c)}</div>`).join("")}</div>${credit}`; },
      strip(el) {
        const ids = (el.dataset.ids || "").split(",").filter(Boolean);
        const list = ids.length ? ids.map((i) => byKey[i]).filter(Boolean) : scenes.filter((c) => c.featured).slice(0, +el.dataset.n || 4);
        el.innerHTML = `<div class="fstrip">${list.map(card).join("")}</div>${credit}`;
      },
      library(el) {
        el.innerHTML = (F.acts || []).map((a) => `<div class="flib-act"><div class="flib-head"><span class="eyebrow">${esc(a.label)}</span><h3 class="h-m">${esc(a.title)}</h3><p>${esc(a.line)}</p></div>
          <div class="fstrip">${scenes.filter((c) => c.act === a.key).map(card).join("")}</div></div>`).join("") + credit;
      },
      realcarter(el) {
        el.innerHTML = `<div class="freal-two">${(F.real_carter || []).map((c) => `<button class="fcard fcard-doc" type="button" data-fclip="${c.slug}" aria-label="Play: ${esc(c.scene)}">
          <span class="fthumb"><img src="${poster(c)}" alt="" loading="lazy"><i class="fplay">${PLAY}</i><em>${c.duration}</em></span>
          <span class="fmeta"><small>${esc(c.kicker)}</small><b>${esc(c.scene)}</b><span>${esc(c.hook)}</span></span></button>`).join("")}</div>`;
      },
      stills(el) {
        el.innerHTML = `<div class="fstills">${(F.bands || []).map((s) => `<button class="fstill" type="button" data-fclip="${s.scene}" data-start="${s.t}" aria-label="Play: ${esc(s.alt)}">
          <img src="${base + s.src_sm}" alt="${esc(s.alt)}" loading="lazy"><span>${esc(s.alt)}</span></button>`).join("")}</div>`;
      },
      band(el) {
        const s = stillBy[el.dataset.still]; if (!s) return;
        const q = el.dataset.q !== undefined ? F.quotes[+el.dataset.q] : null;
        const c = byKey[(q && q.clip) || s.scene];
        const st = q && q.t_s != null ? Math.max(0, q.t_s - 3) : s.t;
        el.innerHTML = `<figure class="fband-in">
          <img src="${base + s.src}" srcset="${base + s.src_sm} 1200w, ${base + s.src} 2400w" sizes="100vw" alt="${esc(s.alt)}" loading="lazy">
          <figcaption class="wrap">${q ? `<blockquote>“${esc(q.text)}”</blockquote><span class="fband-who"><b>${esc(q.speaker)}</b> · ${q.actor ? esc(q.actor) + " · " : ""}Coach Carter (2005)</span>` : `<span class="fband-who">${esc(s.alt)}</span>`}
          ${c ? `<button class="fband-play" type="button" data-fclip="${c.slug}" data-start="${st}"><i class="fplay">${PLAY}</i><span>${esc(c.scene)}</span></button>` : ""}</figcaption></figure>`;
        if (!reduce && "IntersectionObserver" in window) {
          const io = new IntersectionObserver((en) => en.forEach((x) => x.target.classList.toggle("in", x.isIntersecting)), { threshold: 0.15 });
          io.observe(el);
        } else el.classList.add("in");
      },
      loop(el) {
        const l = (F.loops || []).find((x) => x.key === el.dataset.loop); if (!l) return;
        el.setAttribute("aria-hidden", "true");
        el.innerHTML = reduce ? `<img src="${base + l.poster}" alt="">` : `<video muted loop playsinline autoplay preload="metadata" poster="${base + l.poster}"><source src="${base + l.src}" type="video/mp4"></video>`;
        const v = el.querySelector("video");
        if (v) {
          const io = new IntersectionObserver((en) => en.forEach((x) => (x.isIntersecting ? v.play().catch(() => {}) : v.pause())));
          io.observe(el);
        }
      },
      quote(el) {
        const idx = el.dataset.q ? el.dataset.q.split(",").map(Number) : F.quotes.map((_, i) => i).filter((i) => F.quotes[i].verified === true);
        const qs = idx.map((i) => F.quotes[i]).filter(Boolean);
        el.innerHTML = `<div class="fquotes">${qs.map(quote).join("")}</div>${qs.length > 1 ? `<div class="fq-dots">${qs.map((_, i) => `<button type="button" aria-label="Quote ${i + 1}"${i ? "" : ' class="on"'}></button>`).join("")}</div>` : ""}`;
        if (qs.length < 2) return;
        const figs = el.querySelectorAll(".fq"), dots = el.querySelectorAll(".fq-dots button"); let i = 0, timer;
        const go = (n) => { figs[i].classList.remove("on"); dots[i].classList.remove("on"); i = (n + figs.length) % figs.length; figs[i].classList.add("on"); dots[i].classList.add("on"); };
        const auto = () => { clearInterval(timer); if (!reduce) timer = setInterval(() => go(i + 1), 7000); };
        dots.forEach((d, n) => d.addEventListener("click", () => { go(n); auto(); }));
        el.addEventListener("pointerenter", () => clearInterval(timer)); el.addEventListener("pointerleave", auto); el.addEventListener("focusin", () => clearInterval(timer));
        auto();
      },
      realfilm(el) {
        el.innerHTML = `<div class="freal">${F.real_vs_film.map((r, i) => `<div class="fr-row${r.film ? " has-film" : ""}"><span class="fr-n">${String(i + 1).padStart(2, "0")}</span><div><span class="eyebrow">The record · 1999</span><p>${esc(r.real)}</p>${r.film ? `<p class="fr-film"><b>In the film:</b> ${esc(r.film.replace(/^In the film,?\s*/i, "").replace(/^./, (c) => c.toUpperCase()))}</p>` : ""}</div><nav>${r.sources.map((s) => `<a class="link-u" href="${s}" target="_blank" rel="noopener">${new URL(s).hostname.replace("www.", "")}</a>`).join("")}</nav></div>`).join("")}</div>`;
      },
      premiere(el) {
        const ids = (el.dataset.ids || "").split(",").filter(Boolean);
        const gs = ids.length ? ids.map((i) => F.stills.getty.find((g) => g.getty_id === i)).filter(Boolean) : F.stills.getty.filter((g) => g.pick).slice(0, +el.dataset.n || 6);
        el.innerHTML = `<div class="fprem">${gs.map((g) => `<figure class="gx"><div class="gframe fg" data-fg="${g.getty_id}" style="aspect-ratio:${g.w} / ${g.h + 34}"></div><figcaption><b>${esc(g.label)}</b><span>${esc(g.photographer)} / ${esc(g.collection)} via Getty Images</span></figcaption></figure>`).join("")}</div>`;
        const io = new IntersectionObserver((ents) => ents.forEach((en) => {
          if (!en.isIntersecting) return; io.unobserve(en.target); const g = gs.find((x) => x.getty_id === en.target.dataset.fg);
          const f = document.createElement("iframe"); f.src = `https://embed.gettyimages.com/embed/${g.getty_id}?et=${encodeURIComponent(g.et)}&tld=com&sig=${encodeURIComponent(g.sig)}&caption=false&ver=1`;
          f.title = `${g.label} — Getty Images`; f.loading = "lazy"; f.scrolling = "no"; f.setAttribute("frameborder", "0"); f.addEventListener("load", () => en.target.classList.add("ready")); en.target.appendChild(f);
        }), { rootMargin: "400px 0px" });
        el.querySelectorAll("[data-fg]").forEach((x) => io.observe(x));
      },
    };
    slots.forEach((el) => { const fn = R[el.dataset.film]; fn && fn(el); el.classList.add("film-ready"); });
  }).catch((e) => { console.error("film.js", e); slots.forEach((el) => el.remove()); });
})();
