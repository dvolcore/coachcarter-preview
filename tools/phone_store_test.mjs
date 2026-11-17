// Phone visitors can reach the store in one tap from any page. node tools/phone_store_test.mjs [base]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://localhost:8431/";
const pages = ["index.html", "keynotes.html", "story.html", "series.html", "store.html", "academy-product.html", "investors.html"];
const out = []; const ok = (n, c, x = "") => out.push(`${c ? "PASS" : "FAIL"}  ${n}${x ? "  — " + x : ""}`);
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const w of [320, 390]) for (const pg of pages) {
  const c = await b.newContext({ viewport: { width: w, height: 760 }, hasTouch: true, isMobile: true }); const p = await c.newPage();
  await p.goto(base + pg, { waitUntil: "load" }); await p.waitForTimeout(1800);
  const r = await p.evaluate(() => { const a = document.querySelector(".store-btn"); if (!a) return null; const q = a.getBoundingClientRect(); const hit = document.elementFromPoint(q.left + q.width / 2, q.top + q.height / 2); const kids = [...document.querySelector(".nav-actions").children].filter((e) => e.getBoundingClientRect().width > 0).map((e) => e.getBoundingClientRect()); const logo = document.querySelector(".nav-logo").getBoundingClientRect(); return { w: Math.round(q.width), right: Math.round(Math.max(...kids.map((k) => k.right))), gap: Math.round(Math.min(...kids.map((k) => k.left)) - logo.right), hit: !!hit && a.contains(hit), sw: document.documentElement.scrollWidth }; });
  if (!r) { ok(`${w} ${pg} header store button exists`, false); await c.close(); continue; }
  ok(`${w} ${pg} header store button tappable, fits`, r.hit && r.w >= 40 && r.right <= w && r.gap >= 0 && r.sw <= w, JSON.stringify(r));
  if (pg === "keynotes.html") {
    await p.click(".store-btn"); await p.waitForLoadState("load");
    ok(`${w} header bag opens the store`, /store\.html/.test(p.url()), p.url());
    await p.goto(base + pg, { waitUntil: "load" }); await p.waitForTimeout(1500);
    await p.click(".menu-btn"); await p.waitForTimeout(900);
    const q = await p.evaluate(() => { const a = document.querySelector(".m-quick a[href='store.html']"); const r = a.getBoundingClientRect(); const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return { top: Math.round(r.top), hit: a.contains(hit), worlds: document.querySelectorAll(".m-world").length, foot: !!document.querySelector(".m-foot"), home: !!document.querySelector(".m-home") }; });
    ok(`${w} menu: Store pinned on first screen`, q.hit && q.top < 200, JSON.stringify(q));
    ok(`${w} menu: all five sections, Home and footer kept`, q.worlds === 5 && q.foot && q.home);
    await p.click(".m-quick a[href='store.html']"); await p.waitForLoadState("load");
    ok(`${w} menu Store button opens the store`, /store\.html/.test(p.url()));
  }
  await c.close();
}
{ const c = await b.newContext({ viewport: { width: 1440, height: 900 } }); const p = await c.newPage(); await p.goto(base + "keynotes.html", { waitUntil: "load" });
  ok("1440 desktop header unchanged (no bag; Store stays in top nav)", await p.evaluate(() => getComputedStyle(document.querySelector(".store-btn")).display === "none")); await c.close(); }
await b.close();
console.log(out.join("\n")); console.log(`${out.filter((l) => l.startsWith("PASS")).length}/${out.length} pass`);
process.exit(out.some((l) => l.startsWith("FAIL")) ? 1 : 0);
