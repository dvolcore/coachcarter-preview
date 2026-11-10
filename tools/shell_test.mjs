// Sitewide shell QA. node tools/shell_test.mjs [baseUrl] [screenshotDir]
// Prints FAIL lines only (plus INFO for context) and a per-check tally.
import { createRequire } from "module";
import fs from "fs";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://127.0.0.1:8431/";
const shotDir = process.argv[3] || "";
if (shotDir) fs.mkdirSync(shotDir, { recursive: true });
const ALL = ["index", "story", "record", "archive", "impact", "keynotes", "teams", "partners", "playbook", "series", "gallery", "store", "investors", "brand", "coach"];
const PAGES = process.env.SHELL_PAGES ? process.env.SHELL_PAGES.split(",") : ALL;
const fails = [], info = [], tally = {};
const T = (k, pass) => { (tally[k] ||= { pass: 0, fail: 0 })[pass ? "pass" : "fail"]++; };
const fail = (chk, page, vp, detail) => { fails.push({ chk, page, vp, detail }); };
const check = (chk, page, vp, cond, detail) => { T(chk, !!cond); if (!cond) fail(chk, page, vp, detail); };
const r1 = (n) => Math.round(n * 10) / 10;
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const url = (pg, extra = "") => `${base}${pg}.html?qa${extra}`;

async function settle(p) { await p.waitForTimeout(2200); }

// ---------- in-page helpers (serialised) ----------
const EXCL = [".nav2", ".localnav", ".progress", ".rail", ".curtain"];
function overlapScan() {
  const EX = [".nav2", ".localnav", ".progress", ".rail", ".curtain"];
  const vis = (e) => { const s = getComputedStyle(e), r = e.getBoundingClientRect(); return s.display !== "none" && s.visibility !== "hidden" && +s.opacity > 0.01 && r.width > 0 && r.height > 0 && !e.closest("[inert]"); };
  const bars = [".nav2", ".localnav"].map((s) => [s, document.querySelector(s)]).filter(([, e]) => e && vis(e)).map(([s, e]) => [s, e.getBoundingClientRect()]);
  const hits = [];
  const name = (e) => e.tagName.toLowerCase() + (e.id ? "#" + e.id : "") + (typeof e.className === "string" && e.className.trim() ? "." + e.className.trim().split(/\s+/).slice(0, 3).join(".") : "");
  for (const e of document.body.querySelectorAll("*")) {
    const s = getComputedStyle(e);
    if (s.position !== "fixed" && s.position !== "sticky") continue;
    if (EX.some((x) => e.matches(x) || e.closest(x))) continue;
    if (e.closest(".menu:not(.open), .pal:not(.open), .mega, .megas")) continue;
    if (!vis(e)) continue;
    const r = e.getBoundingClientRect();
    for (const [bn, br] of bars) {
      const ix = Math.min(r.right, br.right) - Math.max(r.left, br.left), iy = Math.min(r.bottom, br.bottom) - Math.max(r.top, br.top);
      if (ix > 1 && iy > 1) hits.push({ sel: name(e), pos: s.position, vs: bn, rect: [r.left, r.top, r.right, r.bottom].map(Math.round).join(",") + " bar=" + [br.top, br.bottom].map(Math.round).join("-") });
    }
  }
  return hits;
}
function widest() {
  const iw = innerWidth; let best = null;
  for (const e of document.querySelectorAll("body *")) { const r = e.getBoundingClientRect(); if (r.width && r.right > iw + 1 && (!best || r.right > best.right)) best = { right: Math.round(r.right), sel: e.tagName.toLowerCase() + (typeof e.className === "string" && e.className ? "." + e.className.trim().split(/\s+/).slice(0, 2).join(".") : ""), w: Math.round(r.width) }; }
  return best;
}

const nextMap = {};

for (const vp of [{ n: "desktop", w: 1440, h: 900 }, { n: "mobile", w: 390, h: 844 }]) {
  const desktop = vp.n === "desktop";
  for (const pg of PAGES) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h }, hasTouch: !desktop, isMobile: false });
    const p = await ctx.newPage();
    const errs = [];
    p.on("pageerror", (e) => errs.push("pageerror: " + e.message));
    p.on("console", (m) => { if (m.type() === "error") errs.push("console: " + m.text().slice(0, 160)); });
    p.on("requestfailed", (r) => { const f = r.failure()?.errorText || ""; if (!/ERR_ABORTED/.test(f)) errs.push(`reqfailed: ${r.url().slice(-80)} ${f}`); });
    p.on("response", (r) => { if (r.status() >= 400) errs.push(`HTTP ${r.status()} ${r.url().slice(-80)}`); });
    await p.goto(url(pg), { waitUntil: "load" }); await settle(p);
    const V = vp.n, id = pg;

    // screenshots (top of page)
    if (shotDir) await p.screenshot({ path: `${shotDir}/${pg}_${desktop ? "d" : "m"}.jpg`, type: "jpeg", quality: 60 });

    // b. overflow
    const sw = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, iw: innerWidth }));
    if (sw.sw > sw.iw) { const w = await p.evaluate(widest); check("2b overflow", id, V, false, `scrollWidth=${sw.sw} > ${sw.iw}; widest=${JSON.stringify(w)}`); } else T("2b overflow", true);

    // c. overlap at y=0 and y=1200 ; d. heading cover
    for (const y of [0, 1200]) {
      await p.evaluate((yy) => window.scrollTo(0, yy), y); await p.waitForTimeout(700);
      const hits = await p.evaluate(overlapScan);
      check("2c overlap", id, `${V}@y${y}`, hits.length === 0, hits.map((h) => `${h.sel}(${h.pos}) vs ${h.vs} rect=${h.rect}`).join(" ; "));
    }
    await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(600);
    const hd = await p.evaluate(() => {
      const ln = document.querySelector(".localnav"), nv = document.querySelector(".nav2");
      const h = document.querySelector("h1") || document.querySelector(".hero h2, .hero [class*=title]");
      if (!h) return { none: true };
      const hr = h.getBoundingClientRect(), bar = ln ? ln.getBoundingClientRect() : nv.getBoundingClientRect();
      const nvr = nv.getBoundingClientRect();
      return { tag: h.tagName, top: hr.top, bottom: hr.bottom, barTop: bar.top, barBottom: bar.bottom, nvBottom: nvr.bottom, hasLn: !!ln, lnVisible: ln ? getComputedStyle(ln).display !== "none" : false };
    });
    if (hd.none) { T("2d h1 cover", true); info.push(`2d ${id} ${V}: no h1 found`); }
    else {
      const bb = Math.max(hd.barBottom, hd.nvBottom);
      const covered = hd.top < bb && hd.bottom > hd.barTop && hd.bottom > 0;
      check("2d h1 cover", id, V, !covered || hd.top >= bb, `h1 top=${r1(hd.top)} bottom=${r1(hd.bottom)} vs bars bottom=${r1(bb)} (localnav bottom=${r1(hd.barBottom)}, nav2 bottom=${r1(hd.nvBottom)})`);
    }

    // j. nextup
    const nu = await p.evaluate(() => { const a = document.querySelector(".nextup .nu-main"); return a ? a.getAttribute("href") : null; });
    if (desktop) {
      if (!nu) check("2j nextup", id, V, false, "no .nextup .nu-main");
      else {
        const target = new URL(nu, base + pg + ".html");
        const res = await p.request.get(target.href.split("#")[0]);
        nextMap[pg] = nu;
        check("2j nextup", id, V, res.status() < 400, `href=${nu} status=${res.status()}`);
      }
    } else {
      check("2j nextup", id, V, !!nu, "missing .nu-main");
    }

    if (desktop) {
      // e. megas
      const btns = await p.locator(".world-btn").count();
      check("2e world-btn count", id, V, btns === 5, `count=${btns}`);
      for (let i = 0; i < btns; i++) {
        const bt = p.locator(".world-btn").nth(i);
        const w = await bt.getAttribute("data-world");
        await p.mouse.move(700, 600); await p.waitForTimeout(300);
        await bt.hover(); await p.waitForTimeout(600);
        const m = await p.evaluate(() => {
          const open = [...document.querySelectorAll(".mega.open")];
          const o = open[0];
          if (!o) return { n: 0 };
          const r = o.getBoundingClientRect(), s = getComputedStyle(o);
          const links = [...o.querySelectorAll("a")];
          const clipped = links.filter((a) => { const q = a.getBoundingClientRect(); return q.width && (q.left < -0.5 || q.right > innerWidth + 0.5 || q.top < -0.5 || q.bottom > innerHeight + 0.5); }).map((a) => `${a.textContent.trim().slice(0, 20)}@${Math.round(a.getBoundingClientRect().left)},${Math.round(a.getBoundingClientRect().top)},${Math.round(a.getBoundingClientRect().right)},${Math.round(a.getBoundingClientRect().bottom)}`);
          return { n: open.length, vis: s.visibility !== "hidden" && s.display !== "none" && +s.opacity > 0.5 && r.width > 0 && r.height > 0, links: links.length, clipped, vh: innerHeight };
        });
        check("2e hover opens one visible panel", id, V, m.n === 1 && m.vis, `world=${w} open=${m.n} visible=${m.vis}`);
        if (m.n) { check("2e panel >=3 links", id, V, m.links >= 3, `world=${w} links=${m.links}`); check("2e links not clipped", id, V, m.clipped.length === 0, `world=${w} clipped=${m.clipped.join(" | ")}`); }
        await p.keyboard.press("Escape"); await p.waitForTimeout(500);
        const after = await p.evaluate(() => document.querySelectorAll(".mega.open").length);
        check("2e Escape closes", id, V, after === 0, `world=${w} still open=${after}`);
      }
      // keyboard open
      await p.mouse.move(700, 600); await p.waitForTimeout(400);
      await p.locator(".world-btn").first().focus(); await p.keyboard.press("Enter"); await p.waitForTimeout(600);
      const kf = await p.evaluate(() => { const a = document.activeElement; return { inMega: !!(a && a.closest(".mega.open")), act: a ? a.tagName + "." + (a.className || "") + ":" + (a.textContent || "").trim().slice(0, 20) : null, open: document.querySelectorAll(".mega.open").length }; });
      check("2e Enter moves focus into panel", id, V, kf.inMega, `open=${kf.open} active=${kf.act}`);
      await p.keyboard.press("Escape"); await p.waitForTimeout(300);

      // h. rail + localnav anchors
      const scrollMax = await p.evaluate(() => document.documentElement.scrollHeight - innerHeight);
      await p.evaluate(() => window.scrollTo(0, Math.max(innerHeight * 0.7, 700))); await p.waitForTimeout(900);
      const hrefs = await p.evaluate(() => ({ rail: [...document.querySelectorAll(".rail a")].map((a) => a.getAttribute("href")), ln: [...document.querySelectorAll('.localnav a[href^="#"]')].map((a) => a.getAttribute("href")) }));
      const railVis = await p.evaluate(() => { const r = document.querySelector(".rail"); if (!r) return "absent"; const s = getComputedStyle(r); return `${s.display}/${s.visibility}/${s.opacity}`; });
      info.push(`rail ${id}: links=${hrefs.rail.length} state=${railVis}; localnav hash links=${hrefs.ln.length}`);
      for (const [kind, list] of [["rail", hrefs.rail], ["localnav", hrefs.ln]]) {
        for (const h of list) {
          const tid = decodeURIComponent(h.replace(/^#/, ""));
          const exists = await p.evaluate((t) => !!document.getElementById(t), tid);
          if (!exists) { check("2h anchor target exists", id, V, false, `${kind} ${h} missing`); continue; }
          T("2h anchor target exists", true);
          await p.evaluate(() => window.scrollTo(0, Math.max(innerHeight * 0.7, 700))); await p.waitForTimeout(250);
          const sel = kind === "rail" ? `.rail a[href="${h}"]` : `.localnav a[href="${h}"]`;
          try { await p.locator(sel).first().click({ timeout: 3000, force: true }); } catch (e) { check("2h anchor click", id, V, false, `${kind} ${h} click error ${String(e.message).split("\n")[0]}`); continue; }
          await p.waitForTimeout(1000);
          const m = await p.evaluate((t) => {
            const e = document.getElementById(t), r = e.getBoundingClientRect();
            const vb = (s) => { const x = document.querySelector(s); if (!x) return 0; const q = x.getBoundingClientRect(); const cs = getComputedStyle(x); return cs.display === "none" || q.bottom <= 0 ? 0 : q.bottom; };
            return { top: r.top, nav: vb(".nav2"), ln: vb(".localnav"), atBottom: scrollY + innerHeight >= document.documentElement.scrollHeight - 2, sy: scrollY };
          }, tid);
          const barsB = Math.max(m.nav, m.ln);
          const okRange = m.top >= -1 && m.top <= 260;
          const okCover = m.top >= barsB - 2;
          if (m.atBottom && !(okRange && okCover)) { info.push(`2h ${id} ${kind} ${h}: bottom-limited top=${r1(m.top)} (page end reached)`); T("2h anchor lands", true); }
          else check("2h anchor lands", id, V, okRange && okCover, `${kind} ${h} target top=${r1(m.top)} barsBottom=${r1(barsB)} (nav2=${r1(m.nav)}, localnav=${r1(m.ln)})`);
        }
      }
      await p.evaluate(() => window.scrollTo(0, 0));
    }

    if (!desktop) {
      // g. mobile menu
      try {
        await p.evaluate(() => window.scrollTo(0, 0)); await p.waitForTimeout(300);
        await p.locator(".menu-btn").first().click({ timeout: 4000 }); await p.waitForTimeout(900);
        const mm = await p.evaluate(() => {
          const m = document.querySelector(".menu.open"); if (!m) return { open: false };
          const sc = m.querySelector(".m-scroll"); const links = [...sc.querySelectorAll("a")];
          const before = { sh: sc.scrollHeight, ch: sc.clientHeight };
          sc.scrollTop = sc.scrollHeight; const sr = sc.getBoundingClientRect();
          const last = links[links.length - 1], lr = last.getBoundingClientRect();
          const over = [...m.querySelectorAll("*")].filter((e) => { const r = e.getBoundingClientRect(); return r.width && (r.right > innerWidth + 1 || r.left < -1) && getComputedStyle(e).visibility !== "hidden"; }).slice(0, 4).map((e) => e.tagName.toLowerCase() + "." + (e.className || "") + "@" + Math.round(e.getBoundingClientRect().left) + "," + Math.round(e.getBoundingClientRect().right));
          return { open: true, ...before, scrollable: sc.scrollHeight > sc.clientHeight, lastBottom: lr.bottom, lastVisible: lr.bottom <= sr.bottom + 1 && lr.top >= sr.top - 1 && getComputedStyle(last).visibility !== "hidden", scBottom: sr.bottom, menuSW: m.scrollWidth, iw: innerWidth, over, nLinks: links.length };
        });
        check("2g menu opens", id, V, mm.open, "no .menu.open after tap");
        if (mm.open) {
          check("2g last link reachable", id, V, mm.lastVisible, `lastBottom=${r1(mm.lastBottom)} scrollBottom=${r1(mm.scBottom)} scrollH=${mm.sh} clientH=${mm.ch}`);
          check("2g menu no horizontal overflow", id, V, mm.over.length === 0 && mm.menuSW <= mm.iw, `menuScrollW=${mm.menuSW} iw=${mm.iw} over=${mm.over.join(" | ")}`);
          const target = await p.evaluate((cur) => { const a = [...document.querySelectorAll(".menu .m-links a")].find((x) => !x.getAttribute("href").startsWith("#") && !x.getAttribute("href").includes(cur + ".html")); return a ? a.getAttribute("href") : null; }, pg);
          await p.evaluate(() => { const sc = document.querySelector(".menu .m-scroll"); sc.scrollTop = 0; });
          const href = target;
          const [nav] = await Promise.all([p.waitForURL((u) => u.href.includes(href.split("#")[0]), { timeout: 8000 }).then(() => true).catch(() => false), p.locator(`.menu .m-links a[href="${href}"]`).first().click({ timeout: 4000 }).catch(() => {})]);
          check("2g tap link navigates", id, V, nav, `href=${href} url=${p.url()}`);
        }
      } catch (e) { check("2g menu", id, V, false, String(e.message).split("\n")[0]); }
    }

    // a. errors
    check("2a errors", id, V, errs.length === 0, errs.slice(0, 4).join(" || "));
    await ctx.close();
  }
}

// ---------- desktop-only specials ----------
{
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  // f. palette
  await p.goto(url("index")); await settle(p);
  await p.mouse.click(720, 450); await p.keyboard.press("/"); await p.waitForTimeout(600);
  const open1 = await p.evaluate(() => !!document.querySelector(".pal.open"));
  check("2f '/' opens palette", "index", "desktop", open1, "no .pal.open");
  await p.keyboard.type("keynote", { delay: 40 }); await p.waitForTimeout(500);
  const rows = await p.evaluate(() => document.querySelectorAll(".pal-row").length);
  check("2f 'keynote' gives rows", "index", "desktop", rows >= 1, `rows=${rows}`);
  await p.keyboard.press("Enter"); await p.waitForTimeout(2000);
  check("2f Enter navigates to keynotes", "index", "desktop", /keynotes/.test(p.url()), `url=${p.url()}`);
  // Cmd/Ctrl+K and data-palette
  await p.goto(url("story")); await settle(p);
  await p.keyboard.press("Control+k"); await p.waitForTimeout(500);
  check("2f Ctrl+K opens palette", "story", "desktop", await p.evaluate(() => !!document.querySelector(".pal.open")), "no .pal.open");
  await p.keyboard.press("Escape"); await p.waitForTimeout(400);
  check("2f Escape closes palette", "story", "desktop", await p.evaluate(() => !document.querySelector(".pal.open")), ".pal still open");
  await p.locator("[data-palette]").first().click(); await p.waitForTimeout(500);
  check("2f [data-palette] button opens", "story", "desktop", await p.evaluate(() => !!document.querySelector(".pal.open")), "no .pal.open");
  // input guard
  for (const pg of ["keynotes", "partners"]) {
    await p.goto(url(pg)); await settle(p);
    const sel = await p.evaluate(() => { const i = [...document.querySelectorAll('input:not([type]), input[type=text], input[type=email], input[type=search], textarea')].find((e) => !e.closest(".pal") && getComputedStyle(e).display !== "none"); return i ? (i.id ? "#" + i.id : i.tagName.toLowerCase() + "[name=" + i.name + "]") : null; });
    if (!sel) { info.push(`2f ${pg}: no text input found`); continue; }
    await p.locator(sel).first().focus(); await p.keyboard.press("/"); await p.waitForTimeout(400);
    const g = await p.evaluate((s) => ({ pal: !!document.querySelector(".pal.open"), val: document.querySelector(s).value }), sel);
    check("2f '/' in input does not open palette", pg, "desktop", !g.pal && g.val.includes("/"), `input=${sel} palOpen=${g.pal} value=${JSON.stringify(g.val)}`);
  }
  // i. store spy
  await p.goto(url("store")); await settle(p);
  for (const [id, want] of [["uniforms", "Basketball"], ["editions", "Books & Collectibles"]]) {
    await p.evaluate((t) => { document.getElementById(t).scrollIntoView({ block: "start" }); }, id);
    await p.waitForTimeout(900);
    const on = await p.evaluate(() => [...document.querySelectorAll(".localnav a.on")].map((a) => a.textContent.trim()));
    check("2i store spy", "store", "desktop", on.length === 1 && on[0] === want, `#${id}: a.on=${JSON.stringify(on)} want=${want}`);
  }
  await ctx.close();

  // k. reduced motion
  const rc = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  const rp = await rc.newPage();
  await rp.goto(url("index")); await settle(rp);
  for (const sel of [".hub-panel", ".nextup .nu-title span"]) {
    const els = await rp.locator(sel).count();
    check("2k reduced-motion present", "index", "desktop", els > 0, `${sel} count=${els}`);
    for (let i = 0; i < els; i++) {
      await rp.locator(sel).nth(i).scrollIntoViewIfNeeded(); await rp.waitForTimeout(500);
      const m = await rp.locator(sel).nth(i).evaluate((e) => {
        let op = 1, n = e; while (n && n.nodeType === 1) { op *= +getComputedStyle(n).opacity; n = n.parentElement; }
        const r = e.getBoundingClientRect(), pr = e.parentElement.getBoundingClientRect(), ps = getComputedStyle(e.parentElement);
        const s = getComputedStyle(e);
        const clippedByParent = ps.overflow !== "visible" && (r.top < pr.top - 1 || r.bottom > pr.bottom + 1);
        return { op, w: r.width, h: r.height, clip: s.clipPath, vis: s.visibility, clippedByParent, tf: s.transform };
      });
      check("2k reduced-motion visible", "index", "desktop", m.op > 0.99 && m.w > 0 && m.h > 0 && m.clip === "none" && m.vis === "visible" && !m.clippedByParent, `${sel}[${i}] effectiveOpacity=${r1(m.op)} size=${r1(m.w)}x${r1(m.h)} clip=${m.clip} clippedByParent=${m.clippedByParent} transform=${m.tf}`);
    }
  }
  await rc.close();

  // l. tab order
  const tc = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const tp = await tc.newPage();
  await tp.goto(url("index")); await settle(tp);
  await tp.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
  const order = [], leaks = [];
  for (let i = 0; i < 40; i++) {
    await tp.keyboard.press("Tab");
    const f = await tp.evaluate(() => { const a = document.activeElement; if (!a || a === document.body) return null; return { d: a.tagName.toLowerCase() + (a.className && typeof a.className === "string" ? "." + a.className.trim().split(/\s+/)[0] : "") + " '" + ((a.getAttribute("aria-label") || a.textContent || a.getAttribute("href") || "").trim().replace(/\s+/g, " ").slice(0, 28)) + "'", closed: !!a.closest(".mega:not(.open), .menu:not(.open), .pal:not(.open)") }; });
    if (!f) { order.push("(body)"); continue; }
    order.push(f.d); if (f.closed) leaks.push(`tab#${i + 1}: ${f.d}`);
  }
  info.push("2l first 12 tab stops: " + order.slice(0, 12).map((x, i) => `${i + 1}) ${x}`).join("  "));
  check("2l closed panels not tabbable (40 tabs)", "index", "desktop", leaks.length === 0, leaks.join(" | "));
  await tc.close();
}

await b.close();
console.log("NEXT-UP CHAIN: " + PAGES.map((p) => `${p}->${nextMap[p] || "?"}`).join("  "));
for (const i of info) console.log("INFO " + i);
console.log("TALLY " + JSON.stringify(tally));
for (const f of fails) console.log("FAIL " + JSON.stringify(f));
console.log(`TOTAL FAILS: ${fails.length}`);
