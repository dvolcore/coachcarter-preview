/* Store: catalog + cart. Preview build — checkout opens a launch notice.
   At launch, swap `checkout()` for Shopify Storefront / Stripe Checkout. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const CC = window.CC || { store: { get: (k, d) => d, set() {} }, say() {} };

  const ball = () => `
    <div class="tee"><svg viewBox="0 0 300 300" aria-hidden="true">
      <defs><radialGradient id="bg1" cx=".35" cy=".3"><stop offset="0" stop-color="#E8823A"/><stop offset="1" stop-color="#8A3C12"/></radialGradient></defs>
      <circle cx="150" cy="150" r="110" fill="url(#bg1)"/>
      <g fill="none" stroke="#1d0d05" stroke-width="3"><path d="M40 150 H260"/><path d="M150 40 V260"/><path d="M72 72 Q150 150 72 228"/><path d="M228 72 Q150 150 228 228"/></g>
      <text x="150" y="190" text-anchor="middle" font-family="Cormorant Garamond, serif" font-style="italic" font-size="44" fill="#fff" fill-opacity=".85" transform="rotate(-12 150 180)">Coach Carter</text>
    </svg></div>`;
  const print = () => `
    <div class="tee"><svg viewBox="0 0 300 300" aria-hidden="true">
      <rect x="62" y="30" width="176" height="240" fill="#2b2016"/><rect x="72" y="40" width="156" height="220" fill="#F3EDE1"/>
      <text x="150" y="70" text-anchor="middle" font-family="Cinzel, serif" font-weight="700" font-size="13" fill="#1b1b1b">THE CONTRACT</text>
      <g stroke="#541D30" stroke-opacity=".25">${Array.from({ length: 9 }, (_, i) => `<line x1="86" x2="214" y1="${92 + i * 16}" y2="${92 + i * 16}"/>`).join("")}</g>
      <path d="M92 236 q20 -18 34 0 t36 -4 t30 6" stroke="#1a1530" stroke-width="2" fill="none"/>
      <circle cx="196" cy="214" r="16" fill="none" stroke="#541D30" stroke-width="2"/>
    </svg></div>`;
  const film = () => `
    <div class="cover c2" style="--w:220px;border-radius:6px;box-shadow:0 30px 60px -20px #000;width:62%;height:auto;aspect-ratio:2/3;margin:auto">
      <div class="ct-top">The 2005 film</div>
      <div><div class="ct-title" style="font-size:22px;letter-spacing:.08em">INSPIRED BY<br>HIS TRUE STORY</div></div>
      <div class="ct-author" style="font-size:11px">Blu-ray · DVD · Digital</div>
    </div>`;
  const book = (cls = "c1", extra = "") => `
    <div class="book3d" data-tilt><div class="face front"><div class="cover ${cls}">
      <div class="ct-top">The 12 Essential Steps for Success in Life</div>
      <div><div class="ct-title">YES MA'AM,<br>NO SIR</div><div class="ct-rule" style="margin-top:12%"></div></div>
      <div class="ct-author">Coach Ken Carter</div>${extra}
    </div></div><div class="face spine"></div><div class="face pages"></div><div class="face back"></div></div>`;

  const photo = (src, alt) => `<img src="assets/img/products/${src}" alt="${alt}" loading="lazy">`;
  const P = [
    { id: "ymns-hc", cat: "books", name: "Yes Ma'am, No Sir", kind: "Hardcover · Business Plus / Hachette, 2012", price: 27, badge: "Hardcover", art: () => book("c1") },
    { id: "ymns-signed", cat: "books", name: "Yes Ma'am, No Sir — Signed", kind: "Hardcover, signed by Coach", price: 49, badge: "Signed", art: () => photo("book_signed.jpg", "Signed hardcover copies of Yes Ma'am, No Sir") },
    { id: "ymns-audio", cat: "books", name: "Yes Ma'am, No Sir — Audiobook", kind: "Hachette Audio · read by Coach Carter", price: 20, art: () => book("c2") },
    { id: "ymns-ebook", cat: "books", name: "Yes Ma'am, No Sir — eBook", kind: "Kindle · Apple Books · Nook", price: 15, art: () => book("c1") },
    { id: "team-pack", cat: "books", name: "Team Pack — 25 Books", kind: "For schools, teams & companies · with contract cards", price: 525, badge: "Bulk", art: () => photo("team_pack.jpg", "Team Pack box with books and contract cards") },
    { id: "film", cat: "film", name: "Coach Carter (2005)", kind: "The 2005 film · Blu-ray / DVD / Digital", price: 15, art: film },
    { id: "ball-signed", cat: "collectibles", name: "Signed Game Ball", kind: "Full size · signed by Coach Ken Carter", price: 250, badge: "Signed", art: ball },
    { id: "print-contract", cat: "collectibles", name: "The Contract — Framed Print", kind: "Archival print · signed · 18×24", price: 180, art: print },
  ];

  const storedCart = CC.store.get("cc_cart", {});
  const validIds = new Set(P.map((p) => p.id));
  const cart = { items: Object.fromEntries(Object.entries(storedCart || {}).filter(([id, qty]) => validIds.has(id) && Number(qty) > 0).map(([id, qty]) => [id, Number(qty)])) };
  const save = () => { CC.store.set("cc_cart", cart.items); render(); };
  const count = () => Object.values(cart.items).reduce((a, b) => a + b, 0);
  const money = (n) => `$${n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;

  const add = (id) => {
    cart.items[id] = (cart.items[id] || 0) + 1; save();
    const p = P.find((x) => x.id === id); CC.say(`${p.name} added`);
    $$(".icon-btn.cart").forEach((b) => { b.animate([{ transform: "scale(1)" }, { transform: "scale(1.25)" }, { transform: "scale(1)" }], { duration: 450, easing: "cubic-bezier(.3,1.6,.5,1)" }); });
  };

  function render() {
    const n = count();
    $$(".cart-count").forEach((c) => { c.textContent = n; c.classList.toggle("on", n > 0); });
    const list = $(".drawer .items"); if (!list) return;
    const ids = Object.keys(cart.items).filter((k) => cart.items[k] > 0 && P.find((p) => p.id === k));
    if (!ids.length) { list.innerHTML = `<div class="empty"><p>Your bag is empty.</p><a class="link-u" href="store.html">Visit the store</a></div>`; $(".drawer .total b").textContent = "$0"; return; }
    let total = 0;
    list.innerHTML = ids.map((id) => {
      const p = P.find((x) => x.id === id); const q = cart.items[id]; total += p.price * q;
      return `<div class="line-item"><div class="li-thumb">${p.art()}</div>
        <div><h6>${p.name}</h6><div class="qty"><button aria-label="Decrease" data-dec="${id}">−</button><span>${q}</span><button aria-label="Increase" data-inc="${id}">+</button></div></div>
        <div style="font:600 17px var(--f-head)">${money(p.price * q)}</div></div>`;
    }).join("");
    $(".drawer .total b").textContent = money(total);
  }

  document.addEventListener("click", (e) => {
    const a = e.target.closest("[data-add]"); if (a) { add(a.dataset.add); }
    const inc = e.target.closest("[data-inc]"); if (inc) { cart.items[inc.dataset.inc]++; save(); }
    const dec = e.target.closest("[data-dec]"); if (dec) { cart.items[dec.dataset.dec] = Math.max(0, cart.items[dec.dataset.dec] - 1); if (!cart.items[dec.dataset.dec]) delete cart.items[dec.dataset.dec]; save(); }
    const open = e.target.closest("[data-cart]"); if (open) { const d = $(".drawer"); d.inert = false; d.classList.add("on"); $(".scrim").classList.add("on"); const f = d.querySelector("button"); f && setTimeout(() => f.focus(), 80); }
    const co = e.target.closest("[data-checkout]"); if (co) { CC.closeAll && CC.closeAll(); CC.openModal && CC.openModal($("#checkout-modal")); }
  });

  /* grid on store page */
  const grid = $("#product-grid");
  if (grid) {
    const draw = (cat) => {
      grid.innerHTML = P.filter((p) => cat === "all" || p.cat === cat).map((p) => `
        <article class="product" data-reveal>
          <div class="thumb glow">${p.badge ? `<span class="tag badge">${p.badge}</span>` : ""}${p.art()}
            <div class="quick"><button class="btn btn-gold btn-sm" data-add="${p.id}">Add to bag <span class="arr">→</span></button></div></div>
          <div class="meta"><h5>${p.name}</h5><span class="price">${money(p.price)}</span></div>
          <div class="kind">${p.kind}</div>
        </article>`).join("");
      requestAnimationFrame(() => $$(".product", grid).forEach((el, i) => setTimeout(() => el.classList.add("in"), 60 * i)));
      $$(".glow", grid).forEach((el) => el.addEventListener("pointermove", (ev) => { const r = el.getBoundingClientRect(); el.style.setProperty("--mx", `${ev.clientX - r.left}px`); el.style.setProperty("--my", `${ev.clientY - r.top}px`); }));
    };
    const chips = $$(".filters .chip");
    const select = (category) => {
      chips.forEach((chip) => {
        const active = chip.dataset.cat === category;
        chip.classList.toggle("on", active);
        chip.setAttribute("aria-pressed", String(active));
      });
      draw(category);
    };
    chips.forEach((chip) => chip.addEventListener("click", () => select(chip.dataset.cat)));
    const category = new URLSearchParams(location.search).get("cat");
    select(chips.some((chip) => chip.dataset.cat === category) ? category : "all");
    const section = ["academy", "apparel"].includes(category)
      ? $("#academy-store-title")
      : chips.some((chip) => chip.dataset.cat === category && category !== "all") ? $("#editions") : null;
    if (section && !location.hash) section.scrollIntoView();
  }
  render();
})();
