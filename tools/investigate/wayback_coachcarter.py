#!/usr/bin/env python3
"""Pull archived pages of Coach Carter's own site (coachcarter.com, 2000-2011)
from the Wayback Machine and save plain text for review.

Coach's old site carried media lists, CV, testimonials and event calendars
that are no longer online. Public archive only (no login).

Run: python3 wayback_coachcarter.py [--out DIR] [--grep REGEX]
Writes OUT/wayback/<slug>.txt and OUT/wayback/index.json
"""
import argparse, html, json, os, re, time, urllib.request

DEFAULT_OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"
CDX = ("https://web.archive.org/cdx/search/cdx?url=coachcarter.com*&output=json"
       "&fl=original,timestamp&collapse=urlkey&limit=3000&filter=statuscode:200")
KEEP = re.compile(r"media|press|news|abcnews|cnn|mtv|vitae|bio|about|testimon|calendar|events?|speaker|award|gallery|photo",
                  re.I)
SKIP = re.compile(r"\.(jpg|jpeg|png|gif|css|js|swf|xml|ico)(\?|$)|/feed/?$|utm_", re.I)
UA = {"User-Agent": "Mozilla/5.0 research-sweep"}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            err = e
            time.sleep(3 * (i + 1))
    raise err


def text_of(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?is)<!--.*?-->", " ", h)
    links = re.findall(r'(?is)<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', h)
    t = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>|</h\d>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t).strip()
    lk = [(re.sub(r"<[^>]+>", "", a).strip(), u) for u, a in links]
    return t, lk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--grep", default=None, help="only fetch originals matching this regex")
    a = ap.parse_args()
    od = os.path.join(a.out, "wayback")
    os.makedirs(od, exist_ok=True)
    rows = json.loads(get(CDX))[1:]
    pick = [(o, t) for o, t in rows if KEEP.search(o) and not SKIP.search(o)
            and (not a.grep or re.search(a.grep, o, re.I))]
    print(f"{len(rows)} archived URLs; fetching {len(pick)}")
    index = []
    for o, t in pick:
        slug = re.sub(r"[^A-Za-z0-9]+", "_", re.sub(r"^https?://(www\.)?coachcarter\.com(:80)?", "", o)).strip("_") or "root"
        path = os.path.join(od, f"{slug}.txt")
        url = f"https://web.archive.org/web/{t}id_/{o}"
        if not os.path.exists(path):
            try:
                txt, links = text_of(get(url))
            except Exception as e:
                print("ERR", o, e)
                continue
            with open(path, "w") as f:
                f.write(f"SOURCE: https://web.archive.org/web/{t}/{o}\n\n{txt}\n\nLINKS:\n")
                f.writelines(f"- {a_} -> {u}\n" for a_, u in links if a_)
            time.sleep(1.2)
        index.append({"original": o, "timestamp": t, "wayback": f"https://web.archive.org/web/{t}/{o}", "file": path})
        print("ok", t, o)
    json.dump(index, open(os.path.join(od, "index.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
