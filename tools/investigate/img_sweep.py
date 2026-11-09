#!/usr/bin/env python3
"""img_sweep.py — sweep Bing Images + DuckDuckGo Images for public photos of Coach Ken Carter.

Read-only metadata sweep: records thumbnail URL, image URL, source page, title. Never downloads
stock/news images. Output: tracking/investigation/raw_sweep.json (deduped by source page).

Usage: python3 img_sweep.py [--out PATH] [--queries "q1|q2"]
"""
import argparse, html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tracking/investigation/raw_sweep.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")

QUERIES = [
    "Coach Ken Carter", "Ken Carter Olympic torch 2002", "Ken Carter Prince courtside",
    "Ken Carter Richmond High 1999 lockout", "Ken Carter Samuel L Jackson", "Ken Carter Dr Phil",
    "Ken Carter Oprah", "Ken Carter Best Damn Sports Show", "Ken Carter keynote speaker stage",
    "Coach Carter Impact Academy Marlin Texas", "Ken Carter SlamBall Rumble",
    "Ken Carter Richmond Oilers 1999 team", "Ken Carter book signing Yes Ma'am No Sir",
    "Ken Carter award", "Ken Carter NAACP", "Ken Carter Guatemala", "Ken Carter Rickey Smiley",
    "Ken Carter celebrity", "Ken Carter red carpet", "Ken Carter President",
    "real Coach Carter Richmond", "Coach Carter premiere 2005 Ken Carter",
    "Ken Carter Richmond High 2024", "Ken Carter motivational speaker",
    "Coach Ken Carter torchbearer", "Ken Carter Richmond Oilers basketball coach",
    "Coach Ken Carter Foundation", "Ken Carter Sports Illustrated", "Ken Carter coach portrait",
    "Ken Carter SlamBall 2023", "Ken Carter Contra Costa", "Ken Carter Gigantic Sporting Goods",
]

# Relevance: must mention carter AND some context word; exclude obvious other Ken Carters.
CTX = re.compile(r"coach|richmond|oilers|slamball|torch|samuel|jackson|basketball|speaker|"
                 r"keynote|yes ma.?am|impact academy|marlin|premiere|real coach", re.I)
NEG = re.compile(r"kenny carter|ken carter.*(guitar|band|realtor|dentist|attorney|md\b|nfl draft)|"
                 r"jimmy carter|rosalynn|carter (center|family)|nick carter|aaron carter|"
                 r"vince carter|kenneth carter.*(author|professor)", re.I)


def fetch(url, headers=None, timeout=20):
    h = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def bing(q):
    url = ("https://www.bing.com/images/async?q=" + urllib.parse.quote(q)
           + "&first=0&count=150&adlt=moderate&mmasync=1")
    out = []
    try:
        body = fetch(url)
    except Exception as e:
        print(f"  bing fail {q}: {e}", file=sys.stderr); return out
    for m in re.finditer(r'\bm="([^"]+)"', body):
        try:
            d = json.loads(html.unescape(m.group(1)))
        except Exception:
            continue
        if "murl" not in d: continue
        out.append({"engine": "bing", "query": q, "image_url": d.get("murl"),
                    "thumb_url": d.get("turl"), "source_page": d.get("purl"),
                    "title": html.unescape(d.get("t", "") or "").replace("\ue000","").replace("\ue001",""), "desc": (d.get("desc", "") or "").replace("\ue000","").replace("\ue001","")})
    return out


def ddg(q):
    out = []
    try:
        page = fetch("https://duckduckgo.com/?q=" + urllib.parse.quote(q) + "&iax=images&ia=images")
        m = re.search(r"vqd=[\"']?([\d-]+)", page)
        if not m:
            print(f"  ddg no vqd {q}", file=sys.stderr); return out
        vqd = m.group(1)
        api = ("https://duckduckgo.com/i.js?l=us-en&o=json&q=" + urllib.parse.quote(q)
               + "&vqd=" + vqd + "&f=,,,&p=1")
        data = json.loads(fetch(api, {"Referer": "https://duckduckgo.com/"}))
    except Exception as e:
        print(f"  ddg fail {q}: {e}", file=sys.stderr); return out
    for r in data.get("results", []):
        out.append({"engine": "ddg", "query": q, "image_url": r.get("image"),
                    "thumb_url": r.get("thumbnail"), "source_page": r.get("url"),
                    "title": r.get("title", ""), "desc": r.get("source", "")})
    return out


def relevant(r):
    blob = " ".join(str(r.get(k, "")) for k in ("title", "source_page", "desc"))
    if not re.search(r"carter", blob, re.I): return False
    if NEG.search(blob) and not re.search(r"coach|richmond|slamball", blob, re.I): return False
    return bool(CTX.search(blob))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--queries", default="")
    a = ap.parse_args()
    qs = a.queries.split("|") if a.queries else QUERIES
    seen, keep, total = {}, [], 0
    for q in qs:
        print(f"[q] {q}", file=sys.stderr)
        for fn in (bing, ddg):
            res = fn(q); total += len(res)
            for r in res:
                if not relevant(r): continue
                key = (r.get("source_page") or r.get("image_url") or "").split("#")[0].rstrip("/")
                if key in seen:
                    seen[key]["queries"] = sorted(set(seen[key]["queries"] + [q])); continue
                r["queries"] = [q]; seen[key] = r; keep.append(r)
            time.sleep(1.2)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps({"total_raw": total, "kept": len(keep), "results": keep}, indent=1))
    print(f"raw={total} kept={len(keep)} -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
