#!/usr/bin/env python3
"""alamy_search.py — query Alamy's public search JSON (same endpoint its search page uses)
for Coach Ken Carter photos. Metadata only (thumb URL, page, caption, date, supplier); no image downloads.

Output: tracking/investigation/alamy_hits.json
"""
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tracking/investigation/alamy_hits.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
QUERIES = ["ken carter torch", "ken carter coach", "coach ken carter", "ken carter richmond",
           "ken carter richmond high", "ken carter basketball", "ken carter samuel l jackson",
           "ken carter premiere", "coach carter premiere ken carter", "ken carter slamball",
           "ken carter 2005", "ken carter speaker", "kenneth carter coach", "ken carter oilers",
           "ken carter 1999", "ken carter 2002", "ken carter 2024", "real coach carter",
           "ken carter award", "ken carter book", "ken carter dr phil", "ken carter benched",
           "richmond high basketball 1999", "richmond oilers basketball",
           "richmond high school basketball carter", "former richmond high school basketball coach",
           "ken carter students", "ken carter speaks", "ken carter hank aaron", "ken carter palm springs",
           "coach carter richmond high", "ken carter 2004", "ken carter 2003", "ken carter 2006"]
GEOS = ["us", "gb"]  # AP (Associated Press) items only surface for non-US geo (AP licenses US directly)
KEEP = re.compile(r"ken(neth)? carter|coach carter", re.I)
NEG = re.compile(r"movie title|release date:|film still|studio: (mtv|paramount)", re.I)


def search(q, geo="us"):
    url = ("https://www.alamy.com/search-api/v2/search/?qt=" + urllib.parse.quote_plus(q)
           + "&sort=_score:desc&langCode=en&geoLocations=" + geo + "&pageNumber=1&pageSize=100"
           "&allowProhibited=false&public=true&isBot=false&count=true&lexical=true")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.alamy.com/"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    hits = {}
    for q, geo in [(q, g) for q in (sys.argv[1:] or QUERIES) for g in GEOS]:
        try:
            d = search(q, geo)
        except Exception as e:
            print(f"fail {q}: {e}", file=sys.stderr); continue
        items = d.get("items", [])
        n = 0
        for it in items:
            cap = it.get("caption", "") or ""
            if not KEEP.search(cap): continue
            ref = it["altids"]["ref"]
            if ref in hits:
                hits[ref]["queries"].append(q); continue
            rend = it.get("renditions", {})
            hits[ref] = {"alamy_ref": ref, "alamy_seq": it["altids"].get("seq"),
                         "page": it.get("uri"), "caption": cap,
                         "date": (it.get("firstcreated") or "")[:10],
                         "supplier": (it.get("pseudo") or {}).get("name"),
                         "license": it.get("license"), "collection": it.get("collectionType"),
                         "thumb": (rend.get("450v") or rend.get("thumb") or {}).get("href"),
                         "is_film_still": bool(NEG.search(cap)), "queries": [q]}
            n += 1
        print(f"{q} [{geo}]: {len(items)} items, {n} new carter hits", file=sys.stderr)
        time.sleep(1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(sorted(hits.values(), key=lambda h: h["date"]), indent=1))
    print(f"{len(hits)} hits -> {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
