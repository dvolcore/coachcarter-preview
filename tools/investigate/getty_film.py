#!/usr/bin/env python3
"""getty_film.py — resolve Coach Carter (2005) film-event Getty IDs (premiere, screenings, NAACP Image Award,
Paramount press day) via the public Getty embed oEmbed endpoint. Input = getty_film_candidates.json
(harvested in-browser 2026-11-09 from Getty editorial searches; IDs already in site getty_all.json removed).
Note: Getty had NO actual film/production stills for Coach Carter in these searches.
Output: tracking/investigation/film/getty_film_oembed.json (id, title, caption, w, h, et, sig, landscape)."""
import json, re, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[2]
IN = ROOT / "tracking/investigation/film/getty_film_candidates.json"
OUT = ROOT / "tracking/investigation/film/getty_film_oembed.json"

def one(gid):
    url = f"https://embed.gettyimages.com/oembed?url=https://gty.im/{gid}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25) as r:
            d = json.loads(r.read())
    except Exception as e:
        return {"id": gid, "error": str(e)}
    html = d.get("html") or ""
    et = re.search(r"widgets.load\({id:'([^']+)'", html); sig = re.search(r"sig:\s*'([^']+)'", html)
    w = re.search(r"w:\s*'(\d+)px'", html); h = re.search(r"h:\s*'(\d+)px'", html)
    w = int(w.group(1)) if w else d.get("width"); h = int(h.group(1)) if h else d.get("height")
    return {"id": gid, "title": d.get("title"), "caption": d.get("caption"), "photographer": d.get("photographer"),
            "collection": d.get("collection"), "w": w, "h": h, "landscape": bool(w and h and w > h),
            "et": et.group(1) if et else None, "sig": sig.group(1) if sig else None,
            "thumb": d.get("thumbnail_url"), "page": f"https://www.gettyimages.com/detail/{gid}",
            "embed_ok": "gie-single" in html}

ids = list(json.loads(IN.read_text()).keys())
with ThreadPoolExecutor(6) as ex:
    out = list(ex.map(one, ids))
OUT.write_text(json.dumps(out, indent=1))
print(len(out), "resolved;", sum(1 for o in out if o.get("embed_ok")), "embeddable;",
      sum(1 for o in out if o.get("landscape") and o.get("embed_ok")), "landscape+embeddable")
