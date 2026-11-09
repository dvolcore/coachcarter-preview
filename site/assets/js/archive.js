/* The Archive: headliners, full Getty photo archive (filterable, paged), video vault. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const base = document.querySelector('script[src*="archive.js"]').src.replace(/assets\/js\/archive\.js.*$/, "");

  const HEAD = {
    "51962763": ["With Samuel L. Jackson", "Hollywood premiere · Jan 13, 2005"],
    "51962765": ["Samuel L. Jackson, Ashanti, Coach & director Thomas Carter", "Hollywood premiere · Jan 13, 2005"],
    "51962845": ["With Samuel L. Jackson and Ashanti", "Hollywood premiere · Jan 13, 2005"],
    "112420039": ["The premiere lineup", "Jackson · Ashanti · Coach · Thomas Carter"],
    "110239085": ["On Dr. Phil with Samuel L. Jackson", "The Dr. Phil Show · Jan 2005"],
    "110239084": ["Dr. Phil, Samuel L. Jackson & Coach", "The Dr. Phil Show · Jan 2005"],
    "117809386": ["His on-screen team", "Channing Tatum, Rick Gonzalez, Antwon Tanner, Nana Gbewony · 2005"],
    "115144906": ["With Dean Cain — TV's Superman", "'Net Gain' celebrity game for L.A. kids · Oct 2004"],
    "51962463": ["With Hall of Famer Hank Aaron", "Premiere celebration · 2005"],
    "51962473": ["With Hall of Famer Ernie Banks", "Premiere celebration · 2005"],
    "51962893": ["With Paramount chair Sherry Lansing", "Hollywood premiere · 2005"],
    "51962885": ["With his wife, Sheila", "Hollywood premiere · 2005"],
    "104862816": ["With NFL All-Star Willie Gault", "Benefit appearance"],
    "118037718": ["With Congresswoman Mary Bono", "Palm Springs Int'l Film Festival · 2005"],
    "117809466": ["Opening the festival", "Palm Springs Int'l Film Festival · 2005"],
    "490354626": ["Main stage, Las Vegas", "Life Is Beautiful Festival · 2015"],
    "1581561726": ["Respect after the buzzer", "SlamBall · Las Vegas · 2023"],
    "1561588922": ["The Rumble huddle", "SlamBall · Las Vegas · 2023"],
  };
  const ORDER = ["51962765", "110239085", "117809386", "115144906", "51962763", "51962845", "51962463", "51962473", "51962893", "490354626", "118037718", "1581561726"];

  const iframe = (g) => `<iframe src="https://embed.gettyimages.com/embed/${g.id}?et=${encodeURIComponent(g.et)}&tld=com&sig=${encodeURIComponent(g.sig)}&caption=false&ver=1" title="${(HEAD[g.id] || [g.caption])[0].replace(/"/g, "&quot;")} — Getty Images" loading="lazy" scrolling="no" frameborder="0"></iframe>`;
  const lazy = new IntersectionObserver((ents) => ents.forEach((en) => {
    if (!en.isIntersecting) return; lazy.unobserve(en.target);
    const el = en.target; el.innerHTML = el.dataset.html; el.querySelector("iframe").addEventListener("load", () => el.classList.add("ready"));
  }), { rootMargin: "500px 0px" });
  const frame = (g) => {
    const d = document.createElement("div"); d.className = "gframe"; d.style.aspectRatio = `${g.w} / ${g.h + 34}`; d.dataset.html = iframe(g); lazy.observe(d); return d;
  };

  fetch(base + "assets/data/getty_all.json").then((r) => r.json()).then(({ photos }) => {
    const byId = Object.fromEntries(photos.map((p) => [p.id, p]));
    $("[data-count-photos]") && ($("[data-count-photos]").textContent = photos.length);

    /* headliners */
    const hl = $("#headliners");
    ORDER.filter((id) => byId[id]).forEach((id, i) => {
      const g = byId[id]; const [t, s] = HEAD[id];
      const fig = document.createElement("figure"); fig.className = "hl" + (i < 3 ? " big" : "");
      fig.appendChild(frame(g));
      fig.insertAdjacentHTML("beforeend", `<figcaption><span class="hl-no">${String(i + 1).padStart(2, "0")}</span><b>${t}</b><span>${s}</span></figcaption>`);
      hl.appendChild(fig);
    });

    /* full archive with filters + paging */
    const grid = $("#archive-grid"); const more = $("#archive-more"); const chips = $$("#archive-filters .chip");
    let filter = "all", shown = 0; const PAGE = 18;
    const list = () => photos.filter((p) => filter === "all" || p.chapter === filter || (filter === "festival" && p.chapter === "cast"));
    const render = (reset) => {
      if (reset) { grid.innerHTML = ""; shown = 0; }
      const items = list(); const next = items.slice(shown, shown + PAGE);
      next.forEach((g) => {
        const fig = document.createElement("figure"); fig.className = "gx";
        fig.appendChild(frame(g));
        const head = HEAD[g.id];
        fig.insertAdjacentHTML("beforeend", `<figcaption><b>${head ? head[0] : g.chapter_label}</b><span>${head ? head[1] : g.caption.replace(/during Palm Springs International Film Festival.*$/, "").slice(0, 110)}</span><span class="credit">${g.photographer ? "Photo: " + g.photographer + " / " : ""}Getty Images</span></figcaption>`);
        grid.appendChild(fig);
      });
      shown += next.length;
      more.hidden = shown >= items.length;
      $("#archive-count").textContent = `${Math.min(shown, items.length)} of ${items.length}`;
    };
    chips.forEach((c) => c.addEventListener("click", () => { chips.forEach((x) => x.classList.toggle("on", x === c)); filter = c.dataset.f; render(true); }));
    more.addEventListener("click", () => render(false));
    render(true);
  });

  /* video vault */
  fetch(base + "assets/data/videos.json").then((r) => r.json()).then(({ videos }) => {
    const vv = $("#vault"); const cats = [...new Set(videos.map((v) => v.cat_label))];
    $("[data-count-videos]") && ($("[data-count-videos]").textContent = videos.length);
    cats.forEach((cl) => {
      const row = document.createElement("div"); row.className = "vrow";
      row.innerHTML = `<header><h3>${cl}</h3></header><div class="vtrack"></div>`;
      const tr = row.querySelector(".vtrack");
      videos.filter((v) => v.cat_label === cl).forEach((v) => {
        tr.insertAdjacentHTML("beforeend", `<button class="vcard" data-yt="${v.id}" data-cursor="Play" aria-label="Play: ${v.title.replace(/"/g, "&quot;")}">
          <span class="vthumb"><img src="https://i.ytimg.com/vi/${v.id}/hqdefault.jpg" alt="" loading="lazy"><i class="vplay"></i>${v.dur ? `<em>${v.dur}</em>` : ""}</span>
          <b>${v.title}</b><span>${v.owner === "own" ? "Coach Ken Carter" : (v.channel || "YouTube")}${v.year ? " · " + v.year : ""}</span></button>`);
      });
      vv.appendChild(row);
    });
    const modal = $("#yt-modal"); const box = $(".ytbox", modal);
    vv.addEventListener("click", (e) => {
      const b = e.target.closest("[data-yt]"); if (!b) return;
      box.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.yt}?autoplay=1&rel=0" title="Video" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`;
      if (window.CC && window.CC.openModal) window.CC.openModal(modal); else modal.classList.add("on");
    });
    modal.addEventListener("click", (e) => { if (e.target === modal || e.target.closest("[data-close]")) box.innerHTML = ""; });
    addEventListener("keydown", (e) => { if (e.key === "Escape") box.innerHTML = ""; });
  });
})();
