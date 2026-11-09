#!/usr/bin/env python3
"""Fetch specific URLs from the Wayback Machine (earliest/latest 200 capture) and
save plain text next to wayback_coachcarter.py output.

Run: python3 wayback_fetch.py URL [URL ...]   (bare paths are joined to www.coachcarter.com/)
"""
import json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wayback_coachcarter import get, text_of, DEFAULT_OUT  # noqa: E402

OD = os.path.join(DEFAULT_OUT, "wayback")


def snapshot(url):
    q = urllib.parse.quote(url, safe="")
    rows = json.loads(get(f"https://web.archive.org/cdx/search/cdx?url={q}&output=json&fl=timestamp,original&filter=statuscode:200&limit=1"))
    return rows[1] if len(rows) > 1 else None


def main(urls):
    os.makedirs(OD, exist_ok=True)
    for u in urls:
        if not u.startswith("http"):
            u = "www.coachcarter.com/" + u.lstrip("/")
        try:
            snap = snapshot(u)
        except Exception as e:
            print("ERR", u, e); time.sleep(10); continue
        if not snap:
            print("NONE", u)
            continue
        t, o = snap
        slug = re.sub(r"[^A-Za-z0-9]+", "_", re.sub(r"^https?://(www\.)?", "", o)).strip("_")[:120]
        path = os.path.join(OD, f"x_{slug}.txt")
        if not os.path.exists(path):
            try:
                txt, links = text_of(get(f"https://web.archive.org/web/{t}id_/{o}"))
            except Exception as e:
                print("ERR", o, e); time.sleep(10); continue
            with open(path, "w") as f:
                f.write(f"SOURCE: https://web.archive.org/web/{t}/{o}\n\n{txt}\n")
            time.sleep(4)
        print("ok", t, o, "->", path)


if __name__ == "__main__":
    main(sys.argv[1:])
