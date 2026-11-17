// Checks the three-plane hero keeps its motion and content. node tools/planes_test.mjs [base] [page]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://localhost:8431/";
const page = process.argv[3] || "keynotes.html";
const out = []; const ok = (n, c, x = "") => out.push(`${c ? "PASS" : "FAIL"}  ${n}${x ? "  — " + x : ""}`);
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
  const c = await b.newContext({ viewport: vp }); const p = await c.newPage();
  const errs = []; p.on("pageerror", (e) => errs.push(e.message));
  await p.goto(base + page + "?qa", { waitUntil: "load" });
  const early = await p.evaluate(() => document.querySelector(".planes").getAnimations({ subtree: true }).length);
  await p.waitForTimeout(4000);
  const r = await p.evaluate(async () => {
    const q = (s) => document.querySelector(s); const v = q(".pl-back video");
    const t0 = v.currentTime; await new Promise((res) => setTimeout(res, 700));
    const rect = (s) => q(s).getBoundingClientRect();
    const sub = rect(".pl-subject"), type = rect(".pl-type b"), bar = rect(".pl-book");
    const y0 = rect(".pl-type b").top + scrollY; window.scrollTo(0, 400); await new Promise((res) => setTimeout(res, 400));
    const y1 = rect(".pl-type b").top + scrollY; window.scrollTo(0, 0);
    return {
      videoPlaying: v.currentTime > t0, lines: [...document.querySelectorAll(".planes h1 .split-line")].map((e) => e.classList.contains("in") || getComputedStyle(e.firstElementChild).transform === "none"),
      h1: q(".planes h1").textContent.trim(), lede: q(".planes .lede").textContent.length, overlap: sub.left < type.right && sub.right > type.left && sub.top < type.bottom,
      barOnTop: document.elementFromPoint(bar.left + 20, bar.top + bar.height / 2)?.closest(".pl-book") != null, magnetic: q(".pl-book").hasAttribute("data-magnetic"),
      links: [q(".pl-book").getAttribute("href"), q(".pl-more").getAttribute("href")], drift: Math.round(y1 - y0), imgOk: q(".pl-subject img").naturalWidth > 0,
      sw: document.documentElement.scrollWidth, marquee: !!document.querySelector(".marquee"),
    };
  });
  const w = vp.width;
  ok(`${w} entrance animations start without script delay`, early >= 4, `${early} running at load`);
  ok(`${w} film still plays (inside the letters)`, r.videoPlaying);
  ok(`${w} headline lines rise in`, r.lines.length === 2 && r.lines.every(Boolean));
  ok(`${w} headline and lede text kept`, /Your team is 13–0\.\s*Is it keeping its contract\?/.test(r.h1) && r.lede > 150, r.h1);
  ok(`${w} subject overlaps the back type`, r.overlap);
  ok(`${w} booking bar is on top and tappable`, r.barOnTop);
  ok(`${w} magnetic hover kept on the booking bar`, r.magnetic);
  ok(`${w} both hero links kept`, r.links[0] === "#book" && r.links[1] === "record.html", r.links.join(" "));
  ok(`${w} planes separate on scroll`, r.drift > 20, `type moved ${r.drift}px over 400px scroll`);
  ok(`${w} cut-out loaded`, r.imgOk);
  ok(`${w} no sideways scroll`, r.sw <= w, `scrollWidth=${r.sw}`);
  ok(`${w} stages marquee still on the page`, r.marquee);
  ok(`${w} no page errors`, errs.length === 0, errs.join(" | "));
  await c.close();
}
await b.close();
console.log(out.join("\n")); console.log(`${out.filter((l) => l.startsWith("PASS")).length}/${out.length} pass`);
process.exit(out.some((l) => l.startsWith("FAIL")) ? 1 : 0);
