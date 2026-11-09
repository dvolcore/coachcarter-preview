#!/usr/bin/env python3
"""Podcast sweep for public episodes featuring the real Coach Ken Carter.

Uses the public iTunes Search API (no key, no login). Runs several query
variants, de-duplicates by episode URL/trackId, scores relevance, and writes
OUT/podcasts_itunes.json (all hits + score) for review.

Run: python3 podcast_sweep.py [--out DIR]
"""
import argparse, json, os, re, time, urllib.parse, urllib.request

DEFAULT_OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"
QUERIES = [
    "Ken Carter coach", "Coach Ken Carter", "real Coach Carter", "Coach Carter Richmond",
    "Ken Carter Richmond High", "Coach Carter lockout", "Ken Carter Yes Ma'am No Sir",
    "the real coach carter interview", "Coach Ken Carter interview", "Ken Carter basketball coach",
]
POS = [r"\bken carter\b", r"coach carter", r"richmond", r"lockout", r"yes ma.?am", r"13-0", r"oilers", r"samuel l"]
NEG = [r"\bmovie review\b", r"rewatch", r"film review", r"\bkenneth carter\b.*(congress|politic)"]


def fetch(term, entity="podcastEpisode", limit=200):
    q = urllib.parse.urlencode({"term": term, "entity": entity, "limit": limit, "country": "US"})
    url = f"https://itunes.apple.com/search?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-sweep"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("results", [])


def score(rec):
    text = " ".join(str(rec.get(k, "")) for k in ("trackName", "collectionName", "description", "shortDescription")).lower()
    s = sum(2 if p in (r"\bken carter\b", r"coach carter") else 1 for p in POS if re.search(p, text))
    if re.search(r"\bken carter\b", text) and re.search(r"coach", text):
        s += 3
    if re.search(r"(real|actual|the) coach carter|coach ken carter", text):
        s += 3
    s -= sum(2 for p in NEG if re.search(p, text))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    seen = {}
    for term in QUERIES:
        try:
            res = fetch(term)
        except Exception as e:  # network hiccup: keep going
            print("ERR", term, e)
            continue
        for r in res:
            key = r.get("trackId") or r.get("episodeUrl") or r.get("trackViewUrl")
            if key in seen:
                seen[key]["queries"].append(term)
                continue
            seen[key] = {
                "show": r.get("collectionName"), "title": r.get("trackName"),
                "date": (r.get("releaseDate") or "")[:10],
                "url": r.get("trackViewUrl"), "audio": r.get("episodeUrl"),
                "description": (r.get("description") or r.get("shortDescription") or "")[:600],
                "queries": [term],
            }
        print(f"{term!r}: {len(res)} results")
        time.sleep(1.5)
    out = []
    for v in seen.values():
        v["score"] = score(v)
        out.append(v)
    out.sort(key=lambda x: (-x["score"], x["date"]))
    path = os.path.join(a.out, "podcasts_itunes.json")
    json.dump(out, open(path, "w"), indent=1)
    print(f"{len(out)} unique episodes -> {path}; score>=6: {sum(1 for x in out if x['score']>=6)}")


if __name__ == "__main__":
    main()
