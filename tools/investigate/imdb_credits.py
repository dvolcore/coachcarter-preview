#!/usr/bin/env python3
"""List IMDb credits (incl. "Self" appearances) for Coach Ken Carter.

Uses IMDb's public suggestion endpoint to find candidate name IDs and the
caching GraphQL endpoint for credits. Research/limited non-commercial use only
(per IMDb's API disclaimer) -- record findings, link to imdb.com, don't republish data.

Run: python3 imdb_credits.py [nmID ...]   (default nm1939736 = Coach Ken Carter)
Writes tracking/investigation/imdb_credits.json
"""
import json, sys, urllib.request

OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation/imdb_credits.json"
Q = ('{ name(id:"%s"){ nameText{text} credits(first:250){ total edges{ node{ category{text} '
     'title{ id titleText{text} titleType{text} releaseYear{year} '
     'series{ series{ id titleText{text} } } } } } } } }')


def credits(nm):
    req = urllib.request.Request(
        "https://caching.graphql.imdb.com/", data=json.dumps({"query": Q % nm}).encode(),
        headers={"content-type": "application/json", "User-Agent": "Mozilla/5.0",
                 "x-imdb-client-name": "imdb-web-next-localized"})
    d = json.load(urllib.request.urlopen(req, timeout=30))["data"]["name"]
    rows = []
    for e in d["credits"]["edges"]:
        n, t = e["node"], e["node"]["title"]
        rows.append({"category": n["category"]["text"], "title": t["titleText"]["text"],
                     "type": t["titleType"]["text"], "year": (t.get("releaseYear") or {}).get("year"),
                     "series": ((t.get("series") or {}).get("series") or {}).get("titleText", {}).get("text"),
                     "url": f"https://www.imdb.com/title/{t['id']}/"})
    return {"id": nm, "name": d["nameText"]["text"], "url": f"https://www.imdb.com/name/{nm}/", "credits": rows}


if __name__ == "__main__":
    ids = sys.argv[1:] or ["nm1939736"]
    res = [credits(i) for i in ids]
    json.dump(res, open(OUT, "w"), indent=1)
    for r in res:
        print(r["id"], r["name"])
        for c in r["credits"]:
            print("  ", c["category"], "|", c["title"], c["year"], c["type"], c["series"] or "", c["url"])
