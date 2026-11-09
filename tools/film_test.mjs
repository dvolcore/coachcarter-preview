import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
const errs = []; p.on("pageerror", (e) => errs.push(e.message));
const out = {};
for (const pg of ["index", "story", "archive", "keynotes", "partners", "series", "playbook", "investors"]) {
  await p.goto(`http://localhost:8405/${pg}.html?qa`); await p.waitForTimeout(1800);
  out[pg] = await p.evaluate(() => [...document.querySelectorAll("[data-film]")].map((e) => `${e.dataset.film}:${e.classList.contains("film-ready")}:${e.querySelectorAll("[data-fclip]").length}:${e.querySelectorAll(".fg,.fr-row").length}`).join(" "));
}
await p.goto("http://localhost:8405/index.html?qa"); await p.waitForTimeout(1500);
await p.click("#film .ftrailer"); await p.waitForTimeout(800);
out.player = await p.evaluate(() => { const f = document.querySelector(".fplayer.on iframe"); return f ? f.src : "none"; });
await p.keyboard.press("Escape"); await p.waitForTimeout(500);
out.closed = await p.evaluate(() => !document.querySelector(".fplayer.on") && !document.querySelector(".fplayer iframe"));
await p.click(".film-qband .fq.on .btn"); await p.waitForTimeout(600);
out.quoteplay = await p.evaluate(() => (document.querySelector(".fplayer.on iframe") || {}).src || "none");
out.errs = errs; console.log(JSON.stringify(out, null, 1)); await b.close();
