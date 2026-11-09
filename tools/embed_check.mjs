// Checks each film.json video plays inside the site's own player (iframe on a real page, so YouTube gets a referrer).
// Usage: node tools/embed_check.mjs [baseUrl]
import { createRequire } from "module"; import fs from "fs";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://localhost:8405/";
const f = JSON.parse(fs.readFileSync(new URL("../site/assets/data/film.json", import.meta.url)));
const ids = [f.trailer.primary.id, ...f.clips.map((c) => c.id)];
const b = await chromium.launch(); const p = await b.newPage();
await p.goto(base + "archive.html?qa"); await p.waitForTimeout(2000);
for (const id of ids) {
  await p.evaluate((id) => { const x = document.createElement("button"); x.dataset.fclip = id; x.dataset.ftitle = id; document.body.appendChild(x); x.click(); x.remove(); }, id);
  await p.waitForTimeout(3500);
  const fr = p.frames().find((fr) => fr.url().includes(`/embed/${id}`));
  const t = fr ? await fr.evaluate(() => document.body.innerText.slice(0, 200).replace(/\s+/g, " ")) : "NO FRAME";
  const bad = !fr || /unavailable|disabled|configuration error|not available/i.test(t);
  console.log(bad ? "FAIL" : "OK  ", id, "|", t.slice(0, 80));
  await p.keyboard.press("Escape"); await p.waitForTimeout(300);
}
await b.close();
