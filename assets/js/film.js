/* The 2005 film, everywhere it belongs. Data: assets/data/film.json (official uploads only — Movieclips /
   Rotten Tomatoes Classic Trailers, both Fandango; Getty editorial embeds). Nothing is re-hosted.
   Slots: <div data-film="feature|rail|strip|quote|realfilm|premiere" data-ids="id,id" data-q="0,2" data-n="6"></div> */
(() => {
  "use strict";
  const slots = Array.from(document.querySelectorAll("[data-film]"));
  if (!slots.length) return;
  const base = document.querySelector('script[src*="film.js"]').src.replace(/assets\/js\/film\.js.*$/, "");
  const esc = (s) => String(s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const views = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : `${Math.round(n / 1e3)}K`) + " views";
  const PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg>';

  /* ---- player (modal) ---- */
  let player, lastFocus;
  const close = () => { if (!player) return; player.classList.remove("on"); player.querySelector(".fp-box").innerHTML = ""; document.documentElement.classList.remove("fp-lock"); lastFocus && lastFocus.focus(); };
  const play = (id, start = 0, title = "Coach Carter (2005)") => {
    if (!player) {
      player = document.createElement("div"); player.className = "fplayer"; player.setAttribute("role", "dialog"); player.setAttribute("aria-modal", "true"); player.setAttribute("aria-label", "Film clip");
      player.innerHTML = '<div class="fp-in"><button class="fp-x" type="button" aria-label="Close video">×</button><div class="fp-box"></div><p class="fp-cap"></p></div>';
      document.body.appendChild(player);
      player.addEventListener("click", (e) => { if (e.target === player || e.target.closest(".fp-x")) close(); });
      document.addEventListener("keydown", (e) => { if (e.key === "Escape" && player.classList.contains("on")) close(); });
    }
    lastFocus = document.activeElement;
    player.querySelector(".fp-box").innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&modestbranding=1${start ? `&start=${start}` : ""}" title="${esc(title)}" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`;
    player.querySelector(".fp-cap").innerHTML = `${esc(title)} · <span>Official clip via YouTube · © Paramount Pictures</span>`;
    player.classList.add("on"); document.documentElement.classList.add("fp-lock"); player.querySelector(".fp-x").focus();
  };
  document.addEventListener("click", (e) => { const b = e.target.closest("[data-fclip]"); if (!b) return; e.preventDefault(); play(b.dataset.fclip, +b.dataset.start || 0, b.dataset.ftitle); });

  fetch(base + "assets/data/film.json").then((r) => r.json()).then((F) => {
    const stills = F.stills.youtube;
    const still = (id) => { const s = stills.find((x) => x.video_id === id && x.pick) || stills.find((x) => x.video_id === id); return s ? s.url : `https://i.ytimg.com/vi/${id}/hqdefault.jpg`; };
    const fact = (k) => (F.facts.find((x) => x.key === k) || {}).value || "";
    const clipById = Object.fromEntries(F.clips.map((c) => [c.id, c]));
    const T = F.trailer.primary;
    const card = (c) => `<button class="fcard" type="button" data-fclip="${c.id}" data-ftitle="Coach Carter (2005) · ${esc(c.scene)}" aria-label="Play scene: ${esc(c.scene)}">
        <span class="fthumb"><img src="${still(c.id)}" alt="" loading="lazy"><i class="fplay">${PLAY}</i><em>${c.duration}</em></span>
        <span class="fmeta"><small>Scene ${c.order} of ${F.clips.length}</small><b>${esc(c.scene)}</b><span>${esc(c.hook || c.description)}</span><i>${views(c.view_count)}</i></span></button>`;
    const credit = '<p class="fcredit">Scenes play from the official Movieclips channel on YouTube (Fandango). <em>Coach Carter</em> © 2005 Paramount Pictures / MTV Films. Shown for reference; no film footage is hosted on this site.</p>';

    const quote = (q, i) => {
      const c = q.clip && (clipById[q.clip] || (q.clip === T.id ? { scene: "Trailer" } : null));
      const img = q.clip ? `<button class="fq-still" type="button" data-fclip="${q.clip}" data-start="${Math.max(0, (q.t_s || 0) - 3)}" data-ftitle="Coach Carter (2005) · ${esc(c ? c.scene : "")}" aria-label="Play the scene"><img src="${still(q.clip)}" alt="" loading="lazy"><i class="fplay">${PLAY}</i></button>` : "";
      return `<figure class="fq${i ? "" : " on"}${img ? " has-still" : ""}" data-i="${i}">${img}<blockquote>“${esc(q.text)}”</blockquote>
        <figcaption><b>${esc(q.speaker)}</b>${q.actor ? `<span>${esc(q.actor)} · Coach Carter (2005)</span>` : "<span>Coach Carter (2005)</span>"}
        ${/Williamson/.test(q.attribution || "") ? '<span class="fq-attr">Adapted from Marianne Williamson, <em>A Return to Love</em> (1992)</span>' : ""}</figcaption>
        ${c ? `<button class="btn btn-ghost btn-sm" type="button" data-fclip="${q.clip}" data-start="${Math.max(0, (q.t_s || 0) - 3)}" data-ftitle="Coach Carter (2005) · ${esc(c.scene)}">${PLAY}<span>Watch the scene</span></button>` : ""}</figure>`;
    };

    const R = {
      feature(el) {
        el.innerHTML = `<div class="ffeature">
          <button class="ftrailer" type="button" data-fclip="${T.id}" data-ftitle="Coach Carter (2005) · Original trailer" aria-label="Play the original 2005 trailer">
            <img src="${still(T.id)}" alt="Coach Carter, 2005 — still from the official trailer" loading="lazy">
            <span class="ft-over"><span class="eyebrow">Paramount Pictures · MTV Films · January 14, 2005</span><b>Coach Carter</b><span class="ft-cta"><i class="fplay">${PLAY}</i>Watch the original trailer · ${Math.floor(T.duration_s / 60)}:${String(T.duration_s % 60).padStart(2, "0")}</span></span>
          </button>
          <dl class="ffacts">
            <div><dt>Opening</dt><dd>#1 at the U.S. box office</dd></div>
            <div><dt>Starring</dt><dd>Samuel L. Jackson as Coach Ken Carter</dd></div>
            <div><dt>Director</dt><dd>${esc(fact("director"))}</dd></div>
            <div><dt>Cast</dt><dd>Rob Brown, Robert Ri'chard, Rick Gonzalez, Channing Tatum, Ashanti</dd></div>
            <div><dt>Honors</dt><dd>NAACP Image Award, Outstanding Actor · CinemaScore A</dd></div>
          </dl></div>
          <div class="frail" role="list">${F.clips.map((c) => `<div role="listitem">${card(c)}</div>`).join("")}</div>${credit}`;
      },
      rail(el) { el.innerHTML = `<div class="frail" role="list">${F.clips.map((c) => `<div role="listitem">${card(c)}</div>`).join("")}</div>${credit}`; },
      strip(el) {
        const ids = (el.dataset.ids || "").split(",").filter(Boolean); const list = ids.length ? ids.map((i) => clipById[i]).filter(Boolean) : F.clips.filter((c) => c.featured).slice(0, +el.dataset.n || 4);
        el.innerHTML = `<div class="fstrip">${list.map(card).join("")}</div>${credit}`;
      },
      quote(el) {
        const idx = el.dataset.q ? el.dataset.q.split(",").map(Number) : F.quotes.map((_, i) => i).filter((i) => F.quotes[i].verified === true);
        const qs = idx.map((i) => F.quotes[i]).filter(Boolean);
        el.innerHTML = `<div class="fquotes">${qs.map(quote).join("")}</div>${qs.length > 1 ? `<div class="fq-dots">${qs.map((_, i) => `<button type="button" aria-label="Quote ${i + 1}"${i ? "" : ' class="on"'}></button>`).join("")}</div>` : ""}`;
        if (qs.length < 2) return;
        const figs = el.querySelectorAll(".fq"), dots = el.querySelectorAll(".fq-dots button"); let i = 0, timer;
        const go = (n) => { figs[i].classList.remove("on"); dots[i].classList.remove("on"); i = (n + figs.length) % figs.length; figs[i].classList.add("on"); dots[i].classList.add("on"); };
        const auto = () => { clearInterval(timer); if (!matchMedia("(prefers-reduced-motion: reduce)").matches) timer = setInterval(() => go(i + 1), 7000); };
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
  }).catch(() => slots.forEach((el) => el.remove()));
})();
