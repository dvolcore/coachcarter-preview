// Three-rule design audit (planes, signal colour, type scale). node tools/design_audit.mjs [baseUrl] [page ...]
// Reports per page: the type sizes in use (px -> characters), how much gold sits on things
// you cannot tap vs. things you can, and whether the hero stacks type / subject / action.
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://localhost:8431/";
const pages = process.argv.slice(3).length ? process.argv.slice(3)
  : ["index", "story", "record", "faq", "archive", "keynotes", "teams", "partners", "playbook", "series", "gallery", "store", "brand", "impact", "investors"];
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  console.log(`\n===== ${vp.width}px =====`);
  for (const name of pages) {
    const c = await b.newContext({ viewport: vp });
    const p = await c.newPage();
    await p.goto(`${base}${name}.html?qa`, { waitUntil: "domcontentloaded" });
    await p.waitForTimeout(1200);
    const r = await p.evaluate(() => {
      const isGold = (s) => {
        const m = s.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?/); if (!m) return false;
        const [r, g, bl, a] = [+m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4]];
        return a > 0.5 && r > 150 && g > 110 && g < r && bl < g - 25 && r - bl > 60;
      };
      const tappable = (el) => !!el.closest("a, button, summary, label, input, select, [role=button], [tabindex]");
      const sizes = {}; let goldTap = 0, goldDeco = 0; const decoEx = {};
      const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      while (tw.nextNode()) {
        const t = tw.currentNode.textContent.trim(); if (!t) continue;
        const el = tw.currentNode.parentElement; if (!el || el.closest("script, style, noscript, svg, [hidden], .sr")) continue;
        const cs = getComputedStyle(el); if (cs.display === "none" || cs.visibility === "hidden") continue;
        const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
        const px = Math.round(parseFloat(cs.fontSize)); sizes[px] = (sizes[px] || 0) + t.length;
        const gold = isGold(cs.color) || (cs.webkitTextFillColor === "rgba(0, 0, 0, 0)" && /gradient/.test(cs.backgroundImage)) || (cs.color === "rgba(0, 0, 0, 0)" && /gradient/.test(cs.backgroundImage));
        if (gold) { if (tappable(el)) goldTap += t.length; else { goldDeco += t.length; const k = (el.className && String(el.className).split(" ")[0]) || el.tagName.toLowerCase(); decoEx[k] = (decoEx[k] || 0) + t.length; } }
      }
      const h1 = document.querySelector("h1"); let hero = null;
      if (h1) {
        const hr = h1.getBoundingClientRect(); const sec = h1.closest("section, header") || document.body;
        const media = [...sec.querySelectorAll("img, video, picture, canvas")].filter((m) => { const q = m.getBoundingClientRect(); return q.width > 80 && q.height > 80; });
        const over = media.filter((m) => { const q = m.getBoundingClientRect(); return q.left < hr.right && q.right > hr.left && q.top < hr.bottom && q.bottom > hr.top; }).length;
        const cta = [...sec.querySelectorAll("a.btn, button.btn, .btn")].length;
        hero = { h1px: Math.round(parseFloat(getComputedStyle(h1).fontSize)), media: media.length, mediaOverType: over, cta };
      }
      return { sizes, goldTap, goldDeco, decoEx, hero };
    });
    const sz = Object.entries(r.sizes).map(([k, v]) => [+k, v]).sort((a, b2) => a[0] - b2[0]);
    const total = sz.reduce((s, x) => s + x[1], 0); const max = sz.length ? sz[sz.length - 1][0] : 0;
    const mid = sz.filter(([px]) => px >= 22 && px < max * 0.6).reduce((s, x) => s + x[1], 0);
    const top = Object.entries(r.decoEx).sort((a, b2) => b2[1] - a[1]).slice(0, 6).map(([k, v]) => `${k}:${v}`).join(" ");
    console.log(`\n${name}  sizes=${sz.length}  max=${max}px  mid-size text=${(100 * mid / total).toFixed(1)}%  gold tap/deco=${r.goldTap}/${r.goldDeco}`);
    console.log(`  px: ${sz.map(([k, v]) => `${k}(${v})`).join(" ")}`);
    console.log(`  gold on untappable: ${top}`);
    console.log(`  hero: ${JSON.stringify(r.hero)}`);
    await c.close();
  }
}
await b.close();
