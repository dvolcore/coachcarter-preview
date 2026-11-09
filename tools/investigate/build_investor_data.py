"""Build site/assets/data/investor.json from the investigation outputs (only verified/likely items).
Film comparables come from tracking/investigation/film_stats.json when present."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / "tracking/investigation"


def yr(i):
    m = re.search(r"(19|20)\d\d", str(i.get("date") or i.get("year") or ""))
    return int(m.group(0)) if m else None


app = json.loads((INV / "appearances.json").read_text())
by_year = collections.defaultdict(lambda: collections.Counter())
LAB = {"tv_radio": "TV & radio", "press_features": "Press features", "speaking": "Keynotes & talks", "podcasts": "Podcasts"}
for sec, label in LAB.items():
    for i in app.get(sec, []):
        if not isinstance(i, dict) or i.get("confidence") == "unverified":
            continue
        y = yr(i)
        if y and 1999 <= y <= 2026:
            by_year[y][label] += 1
years = [{"year": y, "total": sum(by_year[y].values()), **{k: by_year[y].get(k, 0) for k in LAB.values()}} for y in range(1999, 2027)]

counts = {k: len([i for i in app.get(k, []) if isinstance(i, dict) and i.get("confidence") != "unverified"]) for k in
          ["tv_radio", "press_features", "speaking", "podcasts", "celebrity_connections", "testimonials", "awards"]}
testimonials = [{"quote": t["quote"], "person": t.get("person", ""), "title": t.get("title", ""), "org": t.get("org", ""), "url": t.get("url", "")}
                for t in app.get("testimonials", []) if isinstance(t, dict) and t.get("confidence") == "verified"
                and "limbaugh" not in (t.get("person", "") + t.get("org", "")).lower()]  # keep investor page non-partisan

vids = json.loads((INV / "videos.json").read_text())["videos"]
okv = [v for v in vids if v.get("verified") in ("yes", "likely")]
views = sum(v.get("view_count") or 0 for v in okv)

getty = json.loads((ROOT / "site/assets/data/getty_all.json").read_text())["photos"]

film = {}
fs = INV / "film_stats.json"
if fs.exists():
    F = json.loads(fs.read_text())
    rows = F["basketball_rank"]["chart_rows"]
    film = {
        "basketball_domestic": [{"title": r["title"], "domestic_m": round(r["domestic_usd"] / 1e6, 1), "year": r["release"][-4:], "rank": r["rank"], "imdb": r.get("imdb_rating")} for r in rows[:12]],
        "basketball_source": F["basketball_rank"]["chart_source"],
        "facts": {"opening_m": "24.2", "theaters": "2,524", "domestic_m": "67.3", "worldwide_m": "76.7",
                  "imdb": f'{F["scores"]["imdb"]["value"]["rating"]}', "rt_audience": f'{F["scores"]["rotten_tomatoes_audience"]["value"]["pct"]}%'},
    }

out = {
    "updated": "2026-11-09",
    "reach": {
        "appearances_total": sum(counts[k] for k in ["tv_radio", "press_features", "speaking", "podcasts"]),
        "tv_radio": counts["tv_radio"], "press": counts["press_features"], "talks": counts["speaking"], "podcasts": counts["podcasts"],
        "celebrity": counts["celebrity_connections"], "awards": counts["awards"], "testimonials": len(testimonials),
        "videos": len(okv), "video_views": views, "photos": len(getty), "states": 19,
    },
    "by_year": years,
    "testimonials": testimonials,
    "film": film,
}
(ROOT / "site/assets/data/investor.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out["reach"]), "| testimonials", len(testimonials), "| film keys", list(film)[:8])
