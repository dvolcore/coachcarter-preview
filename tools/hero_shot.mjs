// First-screen capture at desktop and phone width. node tools/hero_shot.mjs <page.html> <outPrefix> [base]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const [, , page = "keynotes.html", out = "hero", base = "http://localhost:8431/"] = process.argv;
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const [tag, vp] of [["desktop", { width: 1440, height: 900 }], ["phone", { width: 390, height: 844 }]]) {
  const c = await b.newContext({ viewport: vp, deviceScaleFactor: tag === "phone" ? 2 : 1 });
  const p = await c.newPage();
  const errs = []; p.on("pageerror", (e) => errs.push(e.message));
  await p.goto(base + page + "?qa", { waitUntil: "load" });
  await p.waitForTimeout(3500);
  await p.screenshot({ path: `${out}_${tag}.png` });
  const o = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, vw: innerWidth }));
  console.log(tag, JSON.stringify(o), errs.length ? "ERRORS " + errs.join(" | ") : "no page errors");
  await c.close();
}
await b.close();
