#!/usr/bin/env python3
"""wayback_dig.py — list + harvest Coach Ken Carter's own archived web content.

Public Wayback Machine data only. No logins, no access-control bypass.
Stages (run all by default, or pick with --stage):
  cdx       list every capture per domain (CDX API, collapse=urlkey) -> wayback_cdx/<domain>.json
  assets    download Coach's own images / PDFs / video from captures -> wayback_assets/<domain>/
  pages     save cleaned text of key pages (home/about/bio/speaking/...) -> wayback_pages/
  contact   PIL contact sheet(s) of downloaded images -> wayback_contact_sheet*.jpg
  summary   write wayback.json (captures, assets, pages, keyword hits)

Usage:
  python3 wayback_dig.py                       # everything
  python3 wayback_dig.py --stage cdx
  python3 wayback_dig.py --stage assets --cap 400
  python3 wayback_dig.py --domains coachcarter.com yesmaamnosir.com
"""
import argparse, hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request
from collections import defaultdict

ROOT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"
CDX_DIR = os.path.join(ROOT, "wayback_cdx")
ASSET_DIR = os.path.join(ROOT, "wayback_assets")
PAGE_DIR = os.path.join(ROOT, "wayback_pages")
UA = "Mozilla/5.0 (Macintosh) CoachCarterPlatform-archivist/1.0 (public Wayback research)"

DEFAULT_DOMAINS = [
    "coachcarter.com", "coachkencarter.com", "coachcarterimpactacademy.com",
    "coachcarterimpactacademy.org", "kencarterfoundation.org", "coachkencarterfoundation.org",
    "therealcoachcarter.com", "yesmaamnosir.com", "primetimepublishing.com",
    "coachcarterfoundation.org", "coachcarter.org", "kencarter.com",
]

IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")
DOC_EXT = (".pdf", ".doc", ".docx", ".ppt", ".pptx")
VID_EXT = (".mp4", ".mov", ".m4v", ".flv", ".wmv", ".avi", ".mp3", ".wav", ".m4a")
SKIP_PATH = re.compile(r"/(wp-includes|wp-admin|plugins|themes/[^/]+/(images|img|assets|js|css)|"
                       r"cgi-bin|_vti|icons?|smilies|emoji|spacer|pixel|gravatar|captcha)/|"
                       r"(spacer|blank|pixel|bullet|arrow|btn_|button|bg_|_bg\.|shim|clear\.gif|"
                       r"favicon|loading|ajax-loader|rss|facebook-icon|twitter-icon|social)", re.I)
KEY_PAGE = re.compile(r"(index|home|about|bio|speak|testimon|client|media|press|event|store|shop|book|"
                      r"foundation|academy|news|tv|video|photo|gallery|contact|program|camp|award|"
                      r"appear|kit|one.?sheet|booking|keynote|seminar|workshop|school|endorse|praise)", re.I)
KEYWORDS = ["Best Damn Sports Show", "Oprah", "Prince", "Today Show", "Good Morning America", "GMA",
            "Dr. Phil", "Olympic", "torch", "award", "key to the city", "keys to the city", "ESPN",
            "Samuel L. Jackson", "Paramount", "MTV", "CNN", "Fox", "NBC", "ABC", "CBS", "BET",
            "Ellen", "Larry King", "60 Minutes", "Tavis", "Jay Leno", "Tonight Show", "Nightline",
            "Hall of Fame", "honor", "Richmond High", "Fortune 500", "NFL", "NBA", "Microsoft",
            "Coca-Cola", "testimonial", "Yes Ma'am", "Life Is a Contact Sport", "Impact Academy"]


def fetch(url, tries=4, timeout=90, binary=True):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
                return (data if binary else data.decode("utf-8", "replace")), r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 404, 410):
                break
            time.sleep(3 * (i + 1))
        except Exception as e:  # timeouts, IA "temporarily offline" etc.
            last = e
            time.sleep(4 * (i + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def cdx(domain, limit=10000):
    """Return list of dict captures for domain/* (both bare and www via matchType=domain)."""
    q = urllib.parse.urlencode({
        "url": domain, "matchType": "domain", "output": "json",
        "fl": "timestamp,original,mimetype,statuscode,length", "collapse": "urlkey",
        "limit": str(limit), "from": "1999", "to": "2026",
    })
    url = "https://web.archive.org/cdx/search/cdx?" + q
    body, _ = fetch(url, binary=False, timeout=180)
    body = body.strip()
    if not body or body.startswith("<"):
        raise RuntimeError("CDX returned non-JSON (IA offline?)")
    rows = json.loads(body)
    if not rows:
        return []
    hdr = rows[0]
    return [dict(zip(hdr, r)) for r in rows[1:]]


def cdx_all_versions(url_exact, limit=60):
    """All captures of one exact URL (no collapse) — used to pick best/varied page versions."""
    q = urllib.parse.urlencode({"url": url_exact, "output": "json", "fl": "timestamp,original,statuscode,length",
                                "filter": "statuscode:200", "limit": str(limit)})
    body, _ = fetch("https://web.archive.org/cdx/search/cdx?" + q, binary=False, timeout=120)
    rows = json.loads(body) if body.strip().startswith("[") else []
    return [dict(zip(rows[0], r)) for r in rows[1:]] if rows else []


def stage_cdx(domains):
    os.makedirs(CDX_DIR, exist_ok=True)
    out = {}
    for d in domains:
        path = os.path.join(CDX_DIR, d + ".json")
        try:
            caps = cdx(d)
        except Exception as e:
            print(f"[cdx] {d}: ERROR {e}")
            out[d] = {"error": str(e)}
            continue
        json.dump(caps, open(path, "w"), indent=0)
        years = sorted({c["timestamp"][:4] for c in caps})
        print(f"[cdx] {d}: {len(caps)} unique urls, years {years[:1]}..{years[-1:]}")
        out[d] = {"unique_urls": len(caps), "years": years}
        time.sleep(1.5)
    return out


def load_caps(d):
    p = os.path.join(CDX_DIR, d + ".json")
    return json.load(open(p)) if os.path.exists(p) else []


def classify(c):
    o = c["original"].lower().split("?")[0]
    m = (c.get("mimetype") or "").lower()
    if o.endswith(IMG_EXT) or m.startswith("image/"):
        return "image"
    if o.endswith(DOC_EXT) or "pdf" in m or "msword" in m or "powerpoint" in m:
        return "doc"
    if o.endswith(VID_EXT) or m.startswith("video/") or m.startswith("audio/") or "flash-video" in m:
        return "video"
    if m.startswith("text/html") or o.endswith((".htm", ".html", ".php", ".asp", ".aspx", "/")):
        return "page"
    return "other"


def safe_name(c):
    p = urllib.parse.urlparse(c["original"]).path
    base = os.path.basename(p) or "index"
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", urllib.parse.unquote(base))[:80]
    h = hashlib.md5(c["original"].encode()).hexdigest()[:6]
    return f"{c['timestamp'][:8]}_{h}_{base}"


def stage_assets(domains, cap=400, min_bytes=8000):
    manifest = []
    total = 0
    for d in domains:
        caps = [c for c in load_caps(d) if c.get("statuscode") == "200"]
        cand = []
        for c in caps:
            k = classify(c)
            if k not in ("image", "doc", "video"):
                continue
            if SKIP_PATH.search(c["original"]):
                continue
            try:
                ln = int(c.get("length") or 0)
            except ValueError:
                ln = 0
            # CDX length = compressed WARC record; use loose threshold, re-check real size after download
            if k == "image" and ln and ln < min_bytes * 0.6:
                continue
            cand.append((k, ln, c))
        # docs + video first, then biggest images
        cand.sort(key=lambda t: ({"doc": 0, "video": 1, "image": 2}[t[0]], -t[1]))
        ddir = os.path.join(ASSET_DIR, d)
        os.makedirs(ddir, exist_ok=True)
        print(f"[assets] {d}: {len(cand)} candidates")
        for k, ln, c in cand:
            if total >= cap:
                break
            if k == "video" and ln > 150_000_000:
                manifest.append({"domain": d, "kind": k, "skipped": "too large", **c})
                continue
            fn = safe_name(c)
            fp = os.path.join(ddir, fn)
            rec = {"domain": d, "kind": k, "file": os.path.relpath(fp, ROOT), **c,
                   "wayback": f"https://web.archive.org/web/{c['timestamp']}/{c['original']}"}
            if os.path.exists(fp) and os.path.getsize(fp) >= (min_bytes if k == "image" else 1):
                rec["bytes"] = os.path.getsize(fp)
                manifest.append(rec); total += 1
                continue
            url = f"https://web.archive.org/web/{c['timestamp']}id_/{c['original']}"
            try:
                data, ctype = fetch(url, tries=3)
            except Exception as e:
                rec["error"] = str(e)[:200]
                manifest.append(rec)
                continue
            if data[:15].lower().startswith((b"<!doctype", b"<html")):
                rec["error"] = "html instead of asset"
                manifest.append(rec); continue
            if k == "image" and len(data) < min_bytes:
                rec["skipped"] = f"tiny {len(data)}B"
                manifest.append(rec); continue
            open(fp, "wb").write(data)
            rec["bytes"] = len(data)
            manifest.append(rec)
            total += 1
            time.sleep(0.4)
        print(f"[assets] running total {total}")
    json.dump(manifest, open(os.path.join(ROOT, "wayback_assets_manifest.json"), "w"), indent=1)
    return manifest


def html_to_text(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?is)<!--.*?-->", " ", h)
    # strip wayback toolbar remnants
    h = re.sub(r"(?is)BEGIN WAYBACK TOOLBAR INSERT.*?END WAYBACK TOOLBAR INSERT", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", h)
    imgs = re.findall(r'(?i)<img[^>]+alt="([^"]{3,})"', h)
    t = re.sub(r"(?s)<[^>]+>", " ", h)
    t = html.unescape(t)
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t).strip()
    if imgs:
        t += "\n\n[img alts] " + " | ".join(dict.fromkeys(imgs))
    return t


def stage_pages(domains, per_domain=60):
    os.makedirs(PAGE_DIR, exist_ok=True)
    saved = []
    for d in domains:
        caps = [c for c in load_caps(d) if c.get("statuscode") == "200" and classify(c) == "page"]
        # key pages: path matches KEY_PAGE, or is root
        def is_key(c):
            p = urllib.parse.urlparse(c["original"]).path
            return p in ("", "/", "/index.html", "/index.htm", "/index.php") or KEY_PAGE.search(p)
        keys = [c for c in caps if is_key(c)]
        # de-dupe by normalized path
        seen = set(); picked = []
        for c in keys:
            p = urllib.parse.urlparse(c["original"]).path.lower().rstrip("/") or "/"
            if p in seen:
                continue
            seen.add(p); picked.append(c)
        picked = picked[:per_domain]
        # Root page: also grab several eras (homepage changes over 25 years)
        roots = []
        try:
            vers = cdx_all_versions(d + "/", limit=2000)
            by_year = {}
            for v in vers:
                by_year.setdefault(v["timestamp"][:4], v)
            roots = list(by_year.values())
        except Exception as e:
            print(f"[pages] root versions {d}: {e}")
        todo = [("era", c) for c in roots] + [("key", c) for c in picked]
        print(f"[pages] {d}: {len(roots)} homepage eras + {len(picked)} key pages")
        for kind, c in todo:
            p = urllib.parse.urlparse(c["original"]).path.strip("/").replace("/", "__") or "home"
            fn = f"{d}__{c['timestamp'][:8]}__{re.sub(r'[^A-Za-z0-9._-]+', '_', p)[:70]}.txt"
            fp = os.path.join(PAGE_DIR, fn)
            src = f"https://web.archive.org/web/{c['timestamp']}/{c['original']}"
            if not os.path.exists(fp):
                try:
                    body, _ = fetch(f"https://web.archive.org/web/{c['timestamp']}id_/{c['original']}", binary=False, tries=3)
                except Exception as e:
                    print(f"   x {c['original']}: {str(e)[:80]}")
                    continue
                txt = html_to_text(body)
                if len(txt) < 40:
                    continue
                open(fp, "w").write(f"SOURCE: {src}\nTIMESTAMP: {c['timestamp']}\n\n{txt}\n")
                time.sleep(0.4)
            saved.append({"domain": d, "kind": kind, "file": os.path.relpath(fp, ROOT), "wayback": src,
                          "timestamp": c["timestamp"], "original": c["original"]})
    json.dump(saved, open(os.path.join(ROOT, "wayback_pages_manifest.json"), "w"), indent=1)
    return saved


def keyword_hits():
    hits = defaultdict(list)
    if not os.path.isdir(PAGE_DIR):
        return {}
    for fn in sorted(os.listdir(PAGE_DIR)):
        t = open(os.path.join(PAGE_DIR, fn), errors="replace").read()
        src = t.split("\n", 1)[0].replace("SOURCE: ", "")
        for kw in KEYWORDS:
            for m in re.finditer(re.escape(kw), t, re.I):
                s = t[max(0, m.start() - 160): m.end() + 160].replace("\n", " ")
                hits[kw].append({"source": src, "file": fn, "context": s.strip()})
                break
    return hits


def stage_contact(thumb=200, cols=8, rows=8):
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    imgs = []
    for d in sorted(os.listdir(ASSET_DIR)) if os.path.isdir(ASSET_DIR) else []:
        dd = os.path.join(ASSET_DIR, d)
        for f in sorted(os.listdir(dd)):
            if f.lower().endswith(IMG_EXT):
                imgs.append((d, os.path.join(dd, f)))
    per = cols * rows
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()
    sheets = []
    lab = 28
    for si in range(0, len(imgs), per):
        chunk = imgs[si:si + per]
        nrows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (thumb + 8) + 8, nrows * (thumb + lab + 8) + 8), (24, 24, 24))
        dr = ImageDraw.Draw(sheet)
        for i, (d, fp) in enumerate(chunk):
            x = 8 + (i % cols) * (thumb + 8); y = 8 + (i // cols) * (thumb + lab + 8)
            try:
                im = Image.open(fp)
                im.seek(0)
                im = ImageOps.exif_transpose(im.convert("RGB"))
                w, h = im.size
                im.thumbnail((thumb, thumb))
                sheet.paste(im, (x + (thumb - im.width) // 2, y + (thumb - im.height) // 2))
                dim = f"{w}x{h}"
            except Exception:
                dr.rectangle([x, y, x + thumb, y + thumb], outline=(120, 0, 0)); dim = "unreadable"
            name = os.path.basename(fp)
            dr.text((x, y + thumb + 2), (d.split(".")[0] + "/" + name)[:34], fill=(230, 230, 230), font=font)
            dr.text((x, y + thumb + 14), (name[34:60] + " " + dim)[:34], fill=(170, 170, 170), font=font)
        n = si // per + 1
        out = os.path.join(ROOT, "wayback_contact_sheet.jpg" if n == 1 else f"wayback_contact_sheet_{n}.jpg")
        sheet.save(out, quality=85)
        sheets.append(out)
    print(f"[contact] {len(imgs)} images -> {len(sheets)} sheet(s)")
    return sheets


def stage_summary(domains, cdx_info=None):
    summ = {"generated": time.strftime("%Y-%m-%d %H:%M"), "domains": {}}
    for d in domains:
        caps = load_caps(d)
        kinds = defaultdict(int)
        for c in caps:
            kinds[classify(c)] += 1
        summ["domains"][d] = {"unique_urls": len(caps), "by_kind": dict(kinds),
                              "first": min((c["timestamp"] for c in caps), default=None),
                              "last": max((c["timestamp"] for c in caps), default=None)}
    mp = os.path.join(ROOT, "wayback_assets_manifest.json")
    pp = os.path.join(ROOT, "wayback_pages_manifest.json")
    summ["assets"] = [a for a in json.load(open(mp)) if a.get("bytes")] if os.path.exists(mp) else []
    summ["pages"] = json.load(open(pp)) if os.path.exists(pp) else []
    summ["keyword_hits"] = keyword_hits()
    json.dump(summ, open(os.path.join(ROOT, "wayback.json"), "w"), indent=1)
    print(f"[summary] assets {len(summ['assets'])}, pages {len(summ['pages'])}, keywords {len(summ['keyword_hits'])}")
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["cdx", "assets", "pages", "contact", "summary", "all"], default="all")
    ap.add_argument("--domains", nargs="*", default=None)
    ap.add_argument("--cap", type=int, default=400)
    a = ap.parse_args()
    os.makedirs(ROOT, exist_ok=True)
    doms = a.domains or DEFAULT_DOMAINS
    if a.stage in ("cdx", "all"):
        stage_cdx(doms)
    live = [d for d in doms if load_caps(d)]
    if a.stage in ("assets", "all"):
        stage_assets(live, cap=a.cap)
    if a.stage in ("pages", "all"):
        stage_pages(live)
    if a.stage in ("contact", "all"):
        stage_contact()
    if a.stage in ("summary", "all"):
        stage_summary(doms)
