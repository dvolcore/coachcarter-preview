// Motion plates + product page checks.  node tools/motion_test.mjs [baseUrl] [screenshotDir]
// A: plates readable with JavaScript off   B: no overlap / overflow at 8 widths   C: product page shares the shell
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const pw = require("/opt/homebrew/lib/node_modules/playwright");
const base = (process.argv[2] || "http://127.0.0.1:8431/").replace(/\/?$/, "/");
const out = process.argv[3] || "/tmp";
const R = {}; const errs = [];
const watch = (p, tag) => { p.on("pageerror", (e) => errs.push(tag + " pageerror: " + e.message)); p.on("console", (m) => { if (m.type() === "error" && !/ERR_CONNECTION_RESET/.test(m.text())) errs.push(tag + " console: " + m.text()); }); };
const KEYS = ["campus", "basketball", "collections", "watch", "books", "team"];
const chromium = await pw.chromium.launch();

// A. no JavaScript: every plate readable
{ const p = await (await chromium.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false })).newPage();
  await p.goto(base + "store.html"); await p.waitForTimeout(800);
  R.noJS = await p.evaluate((KEYS) => KEYS.map((k) => { const el = document.getElementById("dept-" + k); const vis = (n) => { const cs = getComputedStyle(n); return cs.opacity !== "0" && cs.visibility !== "hidden"; };
    const t = el.querySelector(".plate-t .w i"); const tr = getComputedStyle(t).transform;
    return { k, title: tr === "none" || tr === "matrix(1, 0, 0, 1, 0, 0)", blurb: vis(el.querySelector(".plate-d")), links: vis(el.querySelector(".plate-links")), undrawn: [...el.querySelectorAll(".sc .d")].filter((d) => parseFloat(getComputedStyle(d).strokeDashoffset) > 0.01).length, hidden: [...el.querySelectorAll(".sc .p, .sc .f")].filter((n) => getComputedStyle(n).opacity === "0").length }; }), KEYS);
  await p.locator("#dept-books").screenshot({ path: out + "/nojs_books.jpg", type: "jpeg", quality: 75 }); await p.context().close(); }

// B. widths: scene stays inside its box, title not covered
R.widths = {};
for (const w of [1440, 1100, 861, 860, 760, 700, 600, 390]) {
  const p = await (await chromium.newContext({ viewport: { width: w, height: 900 } })).newPage(); watch(p, "w" + w);
  await p.goto(base + "store.html?qa", { waitUntil: "domcontentloaded" }); await p.waitForTimeout(900);
  R.widths[w] = await p.evaluate((KEYS) => { const bad = []; for (const k of KEYS) { const el = document.getElementById("dept-" + k); const art = el.querySelector(".plate-art").getBoundingClientRect(); const svg = el.querySelector(".sc").getBoundingClientRect(); const copy = el.querySelector(".plate-copy").getBoundingClientRect(); const title = el.querySelector(".plate-t").getBoundingClientRect();
      const stacked = copy.top >= art.bottom - 2; if (stacked && svg.bottom > title.top + 1) bad.push(k + " svg over title by " + Math.round(svg.bottom - title.top));
      if (svg.height < 60) bad.push(k + " art collapsed " + Math.round(svg.height)); const wds = [...el.querySelectorAll(".plate-t .w i")].map((i) => i.scrollWidth); if (Math.max(...wds) > copy.width - 30) bad.push(k + " title too wide " + Math.max(...wds) + ">" + Math.round(copy.width)); }
    const lefts = KEYS.map((k) => Math.round(document.getElementById("dept-" + k).getBoundingClientRect().left)); return { overflowX: document.documentElement.scrollWidth - innerWidth, bad, lefts: [...new Set(lefts)] }; }, KEYS);
  if (w === 760) { await p.evaluate(() => document.getElementById("dept-basketball").scrollIntoView({ block: "center" })); await p.waitForTimeout(4500); await p.locator("#dept-basketball").screenshot({ path: out + "/bb_760.jpg", type: "jpeg", quality: 75 }); }
  await p.context().close(); }

// C. product page with the shared header
for (const [tag, w, h] of [["d", 1440, 900], ["m", 390, 844]]) {
  const p = await (await chromium.newContext({ viewport: { width: w, height: h } })).newPage(); watch(p, "product-" + tag);
  await p.goto(base + "academy-product.html?product=front-row-letterman", { waitUntil: "load" }); await p.waitForTimeout(1500);
  const r = await p.evaluate(() => ({ overflowX: document.documentElement.scrollWidth - innerWidth, navH: Math.round(document.querySelector(".nav2").getBoundingClientRect().height), worlds: document.querySelectorAll(".world-btn").length, ln: document.querySelectorAll(".localnav a").length, h1: document.querySelector("h1").textContent.trim(), h1Top: Math.round(document.querySelector("h1").getBoundingClientRect().top), back: Math.round(document.querySelector("#product-back").getBoundingClientRect().top), lnBottom: Math.round(document.querySelector(".localnav").getBoundingClientRect().bottom), productShown: !document.querySelector(".academy-product-layout").hidden, logoW: Math.round(document.querySelector(".nav-logo .wm").getBoundingClientRect().width), font: getComputedStyle(document.querySelector(".world-btn") || document.body).fontFamily.slice(0, 30) }));
  if (tag === "d") { await p.hover('.world-btn[data-world="store"]'); await p.waitForTimeout(700); r.megaOpen = await p.evaluate(() => document.querySelectorAll(".mega.open").length); await p.screenshot({ path: out + "/product_d_mega.jpg", type: "jpeg", quality: 72 }); await p.keyboard.press("Escape"); await p.mouse.move(700, 700); await p.waitForTimeout(400);
    await p.keyboard.press("/"); await p.waitForTimeout(600); await p.keyboard.type("hoodie"); await p.waitForTimeout(500); r.palRows = await p.evaluate(() => document.querySelectorAll(".pal-row").length); await p.keyboard.press("Escape"); await p.waitForTimeout(300);
    await p.screenshot({ path: out + "/product_d.jpg", type: "jpeg", quality: 72 });
    await p.click('.localnav a[href="store.html#dept-basketball"]'); await p.waitForURL(/store\.html#dept-basketball/); await p.waitForTimeout(1200); r.landed = await p.evaluate(() => ({ top: Math.round(document.getElementById("dept-basketball").getBoundingClientRect().top), on: (document.querySelector(".localnav a.on") || {}).textContent })); }
  else { await p.click(".menu-btn"); await p.waitForTimeout(1200); r.menuOpen = await p.evaluate(() => document.querySelector(".menu").classList.contains("open") && !document.querySelector(".menu").inert); await p.screenshot({ path: out + "/product_m_menu.jpg", type: "jpeg", quality: 72 }); await p.click(".menu .close"); await p.waitForTimeout(900); r.menuClosed = await p.evaluate(() => document.querySelector(".menu").inert); await p.screenshot({ path: out + "/product_m.jpg", type: "jpeg", quality: 72 }); }
  R["product_" + tag] = r; await p.context().close(); }
// D. the plate that opens each inner page: readable without JS, fits at 3 widths, chips land on real sections
const PAGES = ["story", "record", "archive", "impact", "keynotes", "teams", "partners", "playbook", "series", "gallery", "investors", "brand", "coach"];
R.pages = [];
{ const nojs = await (await chromium.newContext({ viewport: { width: 1440, height: 900 }, javaScriptEnabled: false })).newPage();
  for (const pg of PAGES) { await nojs.goto(base + pg + ".html"); await nojs.waitForTimeout(250);
    const r = await nojs.evaluate(() => { const el = document.getElementById("chapters"); if (!el) return { missing: true }; const t = getComputedStyle(el.querySelector(".plate-t .w i")).transform;
      return { title: t === "none" || t === "matrix(1, 0, 0, 1, 0, 0)", links: getComputedStyle(el.querySelector(".plate-links")).opacity !== "0", undrawn: [...el.querySelectorAll(".sc .d")].filter((d) => parseFloat(getComputedStyle(d).strokeDashoffset) > 0.01).length, hidden: [...el.querySelectorAll(".sc .p, .sc .f")].filter((n) => getComputedStyle(n).opacity === "0").length }; });
    if (r.missing || !r.title || !r.links || r.undrawn || r.hidden) R.pages.push(pg + " noJS " + JSON.stringify(r)); }
  await nojs.context().close(); }
for (const w of [1440, 760, 390]) { const p = await (await chromium.newContext({ viewport: { width: w, height: 900 } })).newPage(); watch(p, "page-plate w" + w);
  for (const pg of PAGES) { await p.goto(base + pg + ".html?qa", { waitUntil: "domcontentloaded" }); await p.waitForTimeout(500);
    const r = await p.evaluate(() => { const el = document.getElementById("chapters"); const art = el.querySelector(".plate-art").getBoundingClientRect(), svg = el.querySelector(".sc").getBoundingClientRect(), copy = el.querySelector(".plate-copy").getBoundingClientRect(), title = el.querySelector(".plate-t").getBoundingClientRect();
      const bad = []; if (document.documentElement.scrollWidth > innerWidth) bad.push("overflow"); if (copy.top >= art.bottom - 2 && svg.bottom > title.top + 1) bad.push("art over title"); if (svg.height < 60) bad.push("art collapsed");
      if (Math.max(...[...el.querySelectorAll(".plate-t .w i")].map((i) => i.scrollWidth)) > copy.width - 30) bad.push("title too wide");
      el.querySelectorAll('.plate-links a[href^="#"]').forEach((a) => { if (!document.getElementById(a.hash.slice(1))) bad.push("dead chip " + a.hash); }); return bad; });
    if (r.length) R.pages.push(pg + " w" + w + " " + r.join(", ")); }
  await p.context().close(); }
await chromium.close();

const fails = [];
R.noJS.forEach((p) => { if (!(p.title && p.blurb && p.links) || p.undrawn || p.hidden) fails.push("noJS " + JSON.stringify(p)); });
Object.entries(R.widths).forEach(([w, v]) => { if (v.overflowX > 0 || v.bad.length || v.lefts.length !== 1) fails.push("width " + w + " " + JSON.stringify(v)); });
for (const k of ["product_d", "product_m"]) { const v = R[k]; if (v.overflowX > 0 || v.worlds !== 5 || !v.productShown || v.back < v.lnBottom) fails.push(k + " " + JSON.stringify(v)); }
if (R.product_d.megaOpen !== 1 || !R.product_d.palRows || R.product_d.landed.on !== "Basketball") fails.push("product_d interactions " + JSON.stringify(R.product_d));
if (!R.product_m.menuOpen || !R.product_m.menuClosed) fails.push("product_m menu " + JSON.stringify(R.product_m));
R.pages.forEach((x) => fails.push("page plate " + x));
errs.forEach((e) => fails.push("error " + e));
console.log(fails.length ? fails.join("\n") : "motion_test: all checks pass (6 store plates + 13 page plates, no-JS, widths, product page)");
console.log("TOTAL FAILS:", fails.length);
process.exit(fails.length ? 1 : 0);
