// Self-check before publishing: how alike is the local build to the live site, page by page?
// Borrowed from the "build, compare with the original, grade, loop" idea (Craft Anything).
// node tools/visual_diff.mjs [liveBase] [localBase] [page ...]
// Prints a likeness score per page at three widths and saves side-by-side sheets for pages that changed.
import { createRequire } from "module";
import { execFileSync } from "child_process";
import { mkdirSync, readdirSync, rmSync } from "fs";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const A = process.argv[2] || "https://dvolcore.github.io/coachcarter-preview/";
const B = process.argv[3] || "http://localhost:8431/";
const pages = process.argv.slice(4).length ? process.argv.slice(4) : readdirSync(new URL("../site/", import.meta.url)).filter((f) => f.endsWith(".html")).sort();
const widths = [1440, 820, 390];
const out = new URL("../tracking/visual_diff/", import.meta.url).pathname;
rmSync(out, { recursive: true, force: true }); mkdirSync(out, { recursive: true });
// Freeze what moves, so a difference means the page changed, not the clock.
const freeze = `*,*::before,*::after{animation:none!important;transition:none!important;caret-color:transparent!important}
video,canvas{visibility:hidden!important}.curtain,.progress{display:none!important}
.reveal,.split-line>span,[data-reveal],.m-world{opacity:1!important;transform:none!important}`;
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const shot = async (base, pg, w, file) => {
  const c = await b.newContext({ viewport: { width: w, height: 900 }, reducedMotion: "reduce", isMobile: w < 500, hasTouch: w < 500 });
  const p = await c.newPage();
  await p.goto(base + pg, { waitUntil: "load" }); await p.addStyleTag({ content: freeze });
  await p.evaluate(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += 700) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); } scrollTo(0, 0); await document.fonts.ready; });
  await p.waitForTimeout(500);
  const h = await p.evaluate(() => document.documentElement.scrollHeight);
  await p.screenshot({ path: file, fullPage: true }); await c.close(); return h;
};
const rows = []; let changed = 0;
const views = pages.flatMap((pg) => widths.map((w) => [pg, w]));
for (const [pg, w] of views) { let row, same; for (let tryNo = 0; tryNo < 3 && !same; tryNo++) { // a view that differs is shot again: slow images are not a change
  const n = pg.replace(".html", "") + "_" + w, fa = `${out}${n}_live.png`, fb = `${out}${n}_local.png`;
  let ha, hb;
  try { ha = await shot(A, pg, w, fa); hb = await shot(B, pg, w, fb); } catch (e) { row = `ERROR ${pg} ${w}  ${String(e.message).split("\n")[0]}`; continue; }
  const dim = (f) => execFileSync("magick", ["identify", "-format", "%w %h", f]).toString().split(" ").map(Number);
  const [wa, haPx] = dim(fa), [, hbPx] = dim(fb); const H = Math.max(haPx, hbPx);
  for (const f of [fa, fb]) execFileSync("magick", [f, "-background", "#ff00ff", "-extent", `${wa}x${H}`, f]);
  // Judge the page in 300 px strips: a small thing lost on a long page still fails its strip.
  const mask = `${out}${n}_mask.png`;
  try { execFileSync("magick", ["compare", "-metric", "AE", "-fuzz", "4%", "-highlight-color", "white", "-lowlight-color", "black", "-compose", "src", fa, fb, mask], { stdio: "ignore" }); } catch {}
  const bands = execFileSync("magick", [mask, "-colorspace", "Gray", "-crop", "x300", "+repage", "-format", "%[fx:mean]\n", "info:"]).toString().trim().split("\n").map(Number);
  const bad = bands.map((m, i) => [i * 300, m]).filter(([, m]) => m > 0.004);
  const like = 100 * (1 - bands.reduce((x, y) => x + y, 0) / bands.length);
  same = bad.length === 0 && ha === hb;
  const where = bad.length ? `  differs at y=${bad.slice(0, 6).map(([y]) => y).join(",")}${bad.length > 6 ? "…" : ""}` : "";
  execFileSync("magick", [fa, fb, "-compose", "difference", "-composite", "-auto-level", `${out}${n}_diff.png`]); rmSync(mask, { force: true });
  if (same) for (const s of ["_live.png", "_local.png", "_diff.png", "_SHEET.jpg"]) rmSync(`${out}${n}${s}`, { force: true });
  else { try { execFileSync("magick", [fa, fb, `${out}${n}_diff.png`, "+append", "-resize", "2400x30000>", "-quality", "82", `${out}${n}_SHEET.jpg`], { stdio: "ignore" }); } catch {} for (const s of ["_live.png", "_local.png", "_diff.png"]) rmSync(`${out}${n}${s}`, { force: true }); }
  row = `${same ? "SAME   " : "CHANGED"} ${pg.padEnd(26)} ${String(w).padStart(4)}  ${like.toFixed(2)}% alike  height ${ha} -> ${hb}${where}${same ? "" : `  sheet: tracking/visual_diff/${n}_SHEET.jpg`}`; }
  rows.push(row); if (!same) changed++; }
await b.close();
console.log(rows.join("\n"));
console.log(`${rows.length - changed}/${rows.length} views identical to live; ${changed} changed. Each changed view should be one you meant to change.`);
