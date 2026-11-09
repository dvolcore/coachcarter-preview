// Film v2 QA: every slot renders, every band/still image loads, player plays self-hosted MP4 at the right time.
// node tools/film_test2.mjs [base] [--shots]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const BASE = (process.argv[2] && !process.argv[2].startsWith("--") ? process.argv[2] : "http://localhost:8405/").replace(/\/?$/, "/");
const SHOTS = process.argv.includes("--shots");
const b = await chromium.launch();
const out = { slots: {}, broken_imgs: [], errs: [] };
for (const vp of [{ width: 1440, height: 900, tag: "d" }, { width: 390, height: 844, tag: "m" }]) {
  const p = await b.newPage({ viewport: { width: vp.width, height: vp.height } });
  p.on("pageerror", (e) => out.errs.push(`${vp.tag} ${e.message}`));
  for (const pg of ["index", "story", "archive", "keynotes", "partners", "series", "playbook", "investors", "impact", "record", "brand", "store"]) {
    await p.goto(`${BASE}${pg}.html?qa`); await p.waitForTimeout(1200);
    // scroll through to trigger lazy images
    const h = await p.evaluate(() => document.body.scrollHeight);
    for (let y = 0; y < h; y += 700) { await p.evaluate((yy) => window.scrollTo(0, yy), y); await p.waitForTimeout(60); }
    await p.waitForTimeout(1200);
    if (vp.tag === "d") out.slots[pg] = await p.evaluate(() => [...document.querySelectorAll("[data-film]")].map((e) => `${e.dataset.film}:${e.classList.contains("film-ready") ? "ok" : "NOT"}:${e.querySelectorAll("[data-fclip]").length}`).join(" "));
    const bad = await p.evaluate(() => [...document.querySelectorAll("[data-film] img")].filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.getAttribute("src")));
    bad.forEach((s) => out.broken_imgs.push(`${vp.tag}/${pg}: ${s}`));
    if (SHOTS) {
      const bands = await p.$$(".film-band");
      for (let i = 0; i < bands.length; i++) { await bands[i].scrollIntoViewIfNeeded(); await p.waitForTimeout(400); await bands[i].screenshot({ path: `tracking/shots/film2_${pg}_band${i}_${vp.tag}.png` }); }
    }
  }
  if (vp.tag === "d") {
    // player: band button -> self-hosted video at quote time
    await p.goto(`${BASE}index.html?qa`); await p.waitForTimeout(1500);
    const btn = await p.$(".film-band .fband-play"); await btn.scrollIntoViewIfNeeded(); await btn.click();
    await p.waitForTimeout(6000);
    out.player = await p.evaluate(() => { const v = document.querySelector(".fplayer.on video"); const f = document.querySelector(".fplayer.on iframe"); return v ? { src: v.currentSrc, t: +v.currentTime.toFixed(1), ready: v.readyState, paused: v.paused, w: v.videoWidth } : f ? { iframe: f.src } : "none"; });
    await p.keyboard.press("Escape"); await p.waitForTimeout(400);
    out.closed = await p.evaluate(() => !document.querySelector(".fplayer.on") && !document.querySelector(".fplayer video"));
    await p.goto(`${BASE}archive.html?qa`); await p.waitForTimeout(1500);
    out.library_cards = await p.evaluate(() => document.querySelectorAll('[data-film="library"] .fcard').length);
    out.acts = await p.evaluate(() => [...document.querySelectorAll(".flib-head h3")].map((h) => h.textContent));
    if (SHOTS) { const lib = await p.$('[data-film="library"]'); await lib.screenshot({ path: "tracking/shots/film2_library_d.png" }); }
  }
  await p.close();
}
console.log(JSON.stringify(out, null, 1)); await b.close();
