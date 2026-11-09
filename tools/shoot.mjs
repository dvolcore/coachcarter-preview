// Visual QA: node tools/shoot.mjs <page> <outdir> [width] [height]
// Scrolls to each section and saves a screenshot. Uses global playwright.
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");

const [, , page = "index.html", out = "/tmp/shots", w = "1440", h = "900"] = process.argv;
const fs = await import("fs");
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: +w, height: +h }, deviceScaleFactor: 1 });
const p = await ctx.newPage();
const errors = [];
p.on("pageerror", (e) => errors.push("pageerror: " + e.message));
p.on("console", (m) => { if (m.type() === "error") errors.push("console: " + m.text()); });
p.on("requestfailed", (r) => errors.push("failed: " + r.url()));
p.on("response", (r) => { if (r.status() >= 400) errors.push(`${r.status()}: ${r.url()}`); });
await p.goto(`http://localhost:8405/${page}${page.includes("?") ? "&" : "?"}qa`, { waitUntil: "domcontentloaded" });
await p.waitForTimeout(3200);
const total = await p.evaluate(() => document.documentElement.scrollHeight);
const step = +h * 0.9;
let i = 0;
for (let y = 0; y < total - 10 && i < 40; y += step, i++) {
  await p.evaluate((yy) => window.scrollTo(0, yy), y);
  await p.waitForTimeout(+(process.env.WAIT||1300));
  await p.screenshot({ path: `${out}/${String(i).padStart(2, "0")}.jpg`, quality: 60, type: "jpeg" });
}
console.log(JSON.stringify({ shots: i, total, errors: [...new Set(errors)] }, null, 1));
await browser.close();
