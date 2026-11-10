// Regression checks for the review findings. node tools/verify.mjs [baseUrl]
import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/homebrew/lib/node_modules/playwright");
const base = process.argv[2] || "http://localhost:8405/";
const out = [];
const ok = (name, cond, extra = "") => out.push(`${cond ? "PASS" : "FAIL"}  ${name}${extra ? "  — " + extra : ""}`);
const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
const errors = [];
const mk = async (opts = {}) => { const c = await b.newContext({ viewport: { width: 1440, height: 900 }, ...opts }); const p = await c.newPage(); p.on("pageerror", (e) => errors.push(e.message)); return p; };

// 1. sticky pinning on index (story, scrub, zoom, reel)
let p = await mk();
await p.goto(base + "index.html?qa"); await p.waitForTimeout(1500);
for (const [sec, stage] of [[".story", ".story-stage"], [".scrub", ".scrub-stage"], [".zoomtype", ".zt-stage"], [".hreel", ".hreel-stage"]]) {
  const top = await p.evaluate(([s, st]) => { const el = document.querySelector(s); window.scrollTo(0, el.offsetTop + el.offsetHeight * 0.45); return new Promise((r) => setTimeout(() => r(document.querySelector(st).getBoundingClientRect().top), 400)); }, [sec, stage]);
  ok(`sticky ${sec}`, Math.abs(top) < 2, `stage top=${top.toFixed(1)}`);
}
const ch = await p.evaluate(() => { const s = document.querySelector(".story"); window.scrollTo(0, s.offsetTop + s.offsetHeight * 0.7); return new Promise((r) => setTimeout(() => r(document.querySelector(".chapter.on")?.dataset.year), 500)); });
ok("story chapter advances", /Paramount|Now/.test(ch || ""), ch);
const sw = await p.evaluate(() => document.documentElement.scrollWidth);
ok("no horizontal overflow desktop", sw <= 1440, `scrollWidth=${sw}`);

// 2. same-page link: no stuck page-transition overlay (old .wipe removed; view transitions now)
await p.goto(base + "keynotes.html?qa"); await p.waitForTimeout(1500);
await p.evaluate(() => window.scrollTo(0, 0));
await p.click(".nav .btn-book"); await p.waitForTimeout(900);
const wipe = await p.evaluate(() => { const e = document.elementFromPoint(720, 450); return { hash: location.hash, stuck: !!(e && e.closest(".curtain, .wipe")), hasWipe: !!document.querySelector(".wipe") }; });
ok("same-page anchor does not leave a blocking transition overlay", !wipe.stuck && !wipe.hasWipe && wipe.hash === "#book", JSON.stringify(wipe));

// 3. modal backdrop click closes + pauses
await p.goto(base + "index.html?qa"); await p.waitForTimeout(1500);
await p.click(".hero-ctas [data-video]"); await p.waitForTimeout(700);
await p.mouse.click(20, 450); await p.waitForTimeout(500);
const modalOn = await p.evaluate(() => document.querySelector("#video-modal").classList.contains("on"));
ok("backdrop click closes video modal", !modalOn);
const tabbable = await p.evaluate(() => [...document.querySelectorAll(".menu a")].some((a) => !a.closest("[inert]")));
ok("closed menu links not tabbable (inert)", !tabbable);

// 4. wizard Enter advances one step (partner)
await p.goto(base + "partners.html?qa#inquire"); await p.waitForTimeout(1500);
await p.fill("#p-name", "Test Person"); await p.fill("#p-org", "Test Co"); await p.fill("#p-email", "test@example.com");
await p.focus("#p-email"); await p.keyboard.press("Enter"); await p.waitForTimeout(400);
const stepIdx = await p.evaluate(() => [...document.querySelectorAll('[data-wizard="partner"] .step')].findIndex((s) => s.classList.contains("on")));
const sent = await p.evaluate(() => !!document.querySelector('[data-wizard="partner"] .sent'));
ok("Enter moves partner wizard to step 2 (not submit)", stepIdx === 1 && !sent, `step=${stepIdx}`);

// 5. record page single copy + tilemap
await p.goto(base + "record.html?qa"); await p.waitForTimeout(1500);
const rc = await p.evaluate(() => ({ heroes: document.querySelectorAll(".page-hero").length, maps: document.querySelectorAll("#tilemap").length, cells: document.querySelectorAll("#tilemap .t").length, lit: document.querySelectorAll("#tilemap [data-lit]").length }));
ok("record page single hero/map", rc.heroes === 1 && rc.maps === 1 && rc.cells === 88, JSON.stringify(rc));
ok("lit states = 19", rc.lit === 19);
await p.click("[data-yt]"); await p.waitForTimeout(800);
ok("youtube click-to-load", await p.evaluate(() => !!document.querySelector(".cinema iframe")));

// 6. store ?cat chip + mobile
await p.goto(base + "store.html?qa&cat=books"); await p.waitForTimeout(1200);
ok("?cat=books highlights Books chip", await p.evaluate(() => document.querySelector(".chip.on")?.dataset.cat === "books"));
ok("book card links to the publisher edition", !!await p.locator('#product-grid a[href$="9781455502349/"]').count());
await p.locator('.filters [data-cat="collectibles"]').click();
ok("collectibles show development status", await p.locator('#product-grid .edition-card').count() === 2
  && (await p.locator('#product-grid .store-label').allTextContents()).every((status) => status === "In development"));
ok("store has no preview checkout", !(await p.locator('[data-add], [data-cart], [data-checkout]').count()));
await p.locator('#team-pack .team-pack-faces').scrollIntoViewIfNeeded();
await p.locator('#team-pack img').evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
ok("both Commitment Card sides display", await p.locator('#team-pack img').count() === 2);

// 7. reduced motion keeps a visible cursor
const pr = await mk({ reducedMotion: "reduce" });
await pr.goto(base + "index.html?qa"); await pr.waitForTimeout(1200);
await pr.mouse.move(400, 400);
const cur = await pr.evaluate(() => getComputedStyle(document.body).cursor);
ok("reduced-motion: system cursor visible", cur !== "none", cur);

// 8. mobile widths
const pm = await mk({ viewport: { width: 390, height: 844 } });
for (const pg of ["index", "store", "series", "record", "partners"]) {
  await pm.goto(base + pg + ".html?qa"); await pm.waitForTimeout(900);
  const w = await pm.evaluate(() => document.documentElement.scrollWidth);
  ok(`mobile ${pg} no overflow`, w <= 390, `w=${w}`);
}
const heroSrc = await (async () => { await pm.goto(base + "index.html?qa"); await pm.waitForTimeout(1200); return pm.evaluate(() => document.querySelector(".hero video").currentSrc); })();
ok("mobile hero uses light encode", /hero_reel_m/.test(heroSrc), heroSrc.split("/").pop());
const textClip = await (async () => { await pm.goto(base + "store.html?qa"); await pm.waitForTimeout(900); return pm.evaluate(() => { const s = [...document.querySelectorAll(".section.maroon .lede, .section.maroon .btn")]; return s.filter((e) => e.getBoundingClientRect().right > 392).length; }); })();
ok("mobile store team-pack text not clipped", textClip === 0, `clipped=${textClip}`);

// 9. no-JS: content visible
const pn = await mk({ javaScriptEnabled: false });
await pn.goto(base + "index.html"); await pn.waitForTimeout(800);
const vis = await pn.evaluate(() => { const c = document.querySelector(".curtain"); return { curtain: getComputedStyle(c).display, h: getComputedStyle(document.querySelector(".hero-meta")).opacity }; });
ok("no-JS: curtain hidden + hero copy visible", vis.curtain === "none" && vis.h === "1", JSON.stringify(vis));

ok("no page errors", errors.length === 0, errors.slice(0, 3).join(" | "));
console.log(out.join("\n"));
await b.close();
if (out.some((line) => line.startsWith("FAIL"))) process.exitCode = 1;
