// node tools/elshot.mjs <page> <selector> <out.jpg> [width]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const [, , page, sel, out, w = "1440"] = process.argv;
const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: +w, height: 900 } })).newPage();
await p.goto(`http://localhost:8405/${page}?qa`); await p.waitForTimeout(2500);
const el = p.locator(sel).first(); await el.scrollIntoViewIfNeeded(); await p.waitForTimeout(2500);
await el.screenshot({ path: out, quality: 70, type: "jpeg" }); await b.close(); console.log("ok", out);
