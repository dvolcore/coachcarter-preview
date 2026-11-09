/* Store: catalog + cart. Preview build — checkout opens a launch notice.
   At launch, swap `checkout()` for Shopify Storefront / Stripe Checkout. */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const CC = window.CC || { store: { get: (k, d) => d, set() {} }, say() {} };

  const tee = (body, print, ink = "#E9CF95") => `
    <div class="tee"><svg viewBox="0 0 300 300" aria-hidden="true">
      <defs><linearGradient id="sh${body.slice(1)}" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".25"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#000" stop-opacity=".3"/></linearGradient></defs>
      <path d="M95 30 L120 22 Q150 40 180 22 L205 30 L265 70 L240 115 L215 102 L215 275 Q150 285 85 275 L85 102 L60 115 L35 70 Z" fill="${body}"/>
      <path d="M95 30 L120 22 Q150 40 180 22 L205 30 L265 70 L240 115 L215 102 L215 275 Q150 285 85 275 L85 102 L60 115 L35 70 Z" fill="url(#sh${body.slice(1)})"/>
      <path d="M120 22 Q150 46 180 22" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="3"/>
      <g fill="${ink}" font-family="Barlow Condensed, Arial Narrow, sans-serif" font-weight="600" text-anchor="middle">${print}</g>
    </svg></div>`;
  const hoodie = (body, print, ink = "#E9CF95") => `
    <div class="tee"><svg viewBox="0 0 300 300" aria-hidden="true">
      <path d="M100 40 Q150 5 200 40 L262 82 L244 175 L218 165 L218 278 Q150 288 82 278 L82 165 L56 175 L38 82 Z" fill="${body}"/>
      <path d="M112 44 Q150 90 188 44 Q150 70 112 44" fill="#000" fill-opacity=".35"/>
      <path d="M110 215 h80 v40 h-80z" fill="#000" fill-opacity=".14"/>
      <line x1="140" y1="70" x2="138" y2="110" stroke="${ink}" stroke-width="2"/><line x1="160" y1="70" x2="162" y2="110" stroke="${ink}" stroke-width="2"/>
      <g fill="${ink}" font-family="Barlow Condensed, Arial Narrow, sans-serif" font-weight="600" text-anchor="middle">${print}</g>
    </svg></div>`;
  const cap = (body) => `
    <div class="tee"><svg viewBox="0 0 300 300" aria-hidden="true">
      <path d="M60 175 Q60 80 150 75 Q240 80 240 175 Z" fill="${body}"/>
      <path d="M60 175 Q150 160 240 175 Q285 182 290 200 Q200 190 150 192 Q80 192 60 175Z" fill="${body}" opacity=".85"/>
      <path d="M150 75 L150 175" stroke="#000" stroke-opacity=".25"/>
      <image href="assets/brand/monogram_gold.svg" x="110" y="105" width="80" height="80"/>
    </svg></div>`;
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
    { id: "tee-wewin", cat: "apparel", name: "WE WIN Tee", kind: "Heavyweight cotton · Legacy maroon", price: 42, badge: "New", art: () => photo("tee_wewin.jpg", "Maroon WE WIN t-shirt") },
    { id: "tee-ymns", cat: "apparel", name: "Yes Ma'am. No Sir. Tee", kind: "Heavyweight cotton · Carbon", price: 42, art: () => tee("#16181D", `<text x="150" y="118" font-size="24" letter-spacing="2">YES MA'AM.</text><text x="150" y="146" font-size="24" letter-spacing="2">NO SIR.</text>`) },
    { id: "tee-average", cat: "apparel", name: "Average Is Not Good Enough Tee", kind: "Heavyweight cotton · Chalk", price: 42, art: () => tee("#EDE6D9", `<text x="150" y="112" font-size="17" letter-spacing="2">AVERAGE IS JUST</text><text x="150" y="134" font-size="17" letter-spacing="2">NOT GOOD ENOUGH.</text><text x="150" y="156" font-size="22" letter-spacing="4">PERIOD.</text>`, "#541D30") },
    { id: "hoodie-contract", cat: "apparel", name: "The Contract Hoodie", kind: "Brushed fleece · Legacy maroon", price: 88, badge: "Limited", art: () => photo("hoodie_contract.jpg", "Maroon I Signed The Contract hoodie") },
    { id: "cap-crest", cat: "apparel", name: "KC Crest Cap", kind: "Structured wool · Carbon", price: 38, art: () => photo("cap_crest.jpg", "Black cap with gold KC embroidery") },
    { id: "ball-signed", cat: "collectibles", name: "Signed Game Ball", kind: "Full size · signed by Coach Ken Carter", price: 250, badge: "Signed", art: ball },
    { id: "print-contract", cat: "collectibles", name: "The Contract — Framed Print", kind: "Archival print · signed · 18×24", price: 180, art: print },
  ];

  const cart = { items: CC.store.get("cc_cart", {}) };
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
    $$(".filters .chip").forEach((c) => c.addEventListener("click", () => { $$(".filters .chip").forEach((x) => x.classList.toggle("on", x === c)); draw(c.dataset.cat); }));
    const start = new URLSearchParams(location.search).get("cat") || "all";
    $$(".filters .chip").forEach((x) => x.classList.toggle("on", x.dataset.cat === start));
    draw(start);
  }
  render();
})();
