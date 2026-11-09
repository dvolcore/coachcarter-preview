#!/usr/bin/env python3
"""extract_claims.py — pull evidence-linked claims out of the saved Wayback page texts.

Reads tracking/investigation/wayback_pages/*.txt (written by wayback_dig.py) and writes
tracking/investigation/wayback_claims.json with, for each category, every distinct item plus
the archive URL + timestamp it came from:

  tv_media        sentences like "He has appeared on ..." / "appearances on ..."
  awards          lines under AWARDS & ACKNOWLEDGMENTS (CVs) and "awards: ..." sentences
  clients         the "companies & organizations Coach Carter has presented at" list
  speaking        dated keynote / speaker lines from the CV pages
  testimonials    comments on the WordPress Testimonials page (+ yesmaamnosir Testimonials.php)
  celebrity_photo captions from the 2002 photo album (Photos/list.html, NNphotos.html)
  keyword_hits    first hit per page for Prince / Oprah / Best Damn / torch / Dr. Phil / Today ...

Facebook-widget noise (private people's names in "accepted your friend request" lines) is dropped.
Usage: python3 extract_claims.py
"""
import glob, json, os, re

ROOT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation"
PAGES = os.path.join(ROOT, "wayback_pages")
NOISE = re.compile(r"friend request|commented on|posted something|minutes ago\)|hours, \d+ minutes|tracefusion|\[\[T_F\]\]", re.I)
KW = ["Prince", "Oprah", "Best Damn", "Olympic", "torch", "Dr. Phil", "Today Show", "The View", "Good Morning America",
      "ESPN", "Cold Pizza", "Extra", "Judge Hatchett", "key to the city", "keys to the city", "Hall of Fame",
      "Gray Davis", "Willie Brown", "Jesse Jackson", "Jessie Jackson", "Chris Tucker", "Gladys Knight", "Les Brown",
      "Phil Jackson", "Eric Dickerson", "Samuel L. Jackson", "Ashanti", "Sports Illustrated", "People Magazine"]


def load():
    out = []
    for fp in sorted(glob.glob(os.path.join(PAGES, "*.txt"))):
        raw = open(fp, errors="replace").read()
        src = raw.split("\n", 1)[0].replace("SOURCE: ", "").strip()
        ts = re.search(r"TIMESTAMP: (\d+)", raw)
        body = re.sub(r"\[\[T_F\]\].*?\[\[T_F\]\]", " ", raw, flags=re.S)
        lines = [l.strip() for l in body.split("\n") if l.strip() not in ("", ".", "..") and not NOISE.search(l)]
        out.append({"file": os.path.basename(fp), "source": src, "timestamp": ts.group(1) if ts else "", "lines": lines,
                    "text": "\n".join(lines)})
    return out


def add(bucket, key, item, page):
    k = re.sub(r"\W+", " ", key.lower()).strip()[:160]
    if k in bucket:
        bucket[k]["evidence"].append({"url": page["source"], "timestamp": page["timestamp"]})
        return
    bucket[k] = {**item, "evidence": [{"url": page["source"], "timestamp": page["timestamp"]}]}


def main():
    pages = load()
    tv, awards, clients, speaking, testi, photos, hits = {}, {}, {}, {}, {}, {}, {}
    for p in pages:
        t, L = p["text"], p["lines"]
        for m in re.finditer(r"(He has appeared on[^\n]*?)(?=\n|$)", t):
            add(tv, m.group(1), {"claim": m.group(1).strip()}, p)
        # AWARDS block (CV pages)
        if "AWARDS & ACKNOWLEDGMENTS" in t or "AWARDS &amp; ACKNOWLEDGMENTS" in t:
            i = next(i for i, l in enumerate(L) if l.startswith("AWARDS"))
            for l in L[i + 1:]:
                if l.isupper() and len(l) > 4:
                    break
                l = l.lstrip("*• ").strip()
                if len(l) > 6:
                    add(awards, l, {"award": l}, p)
        for m in re.finditer(r"has to his credit the following awards: ([^\n]+)", t):
            for a in re.split(r", (?:the |and )?|, and ", m.group(1)):
                a = a.strip(" .")
                if len(a) > 6:
                    add(awards, a, {"award": a}, p)
        # client list
        if "list of companies & organizations Coach Carter has presented at" in t:
            i = next(i for i, l in enumerate(L) if "list of companies & organizations" in l)
            for l in L[i + 1:]:
                if l.startswith("To book") or l.startswith("PDF version"):
                    break
                add(clients, l, {"organization": l}, p)
        # dated speaking lines from CVs
        for l in L:
            if re.search(r"(Keynote|Speaker|Presenter|Guest Educator|Torchbearer)", l) and re.search(r"\((?:[A-Z][a-z]+\.? ?)?\d{4}\)|\b(19|20)\d{2}\b", l) and len(l) < 400:
                add(speaking, l, {"engagement": l}, p)
        # testimonials (WordPress comments: "<Name> says:" + date line + body)
        if "Testimonials" in L[0:3] or "Testimonials «" in t[:300] or "Testimonials.php" in p["source"]:
            for i, l in enumerate(L):
                if l.endswith(" says:") and i + 2 < len(L):
                    name, date = l[:-5].strip(), L[i + 1]
                    body = []
                    for nl in L[i + 2:]:
                        if nl.endswith(" says:") or nl.startswith("Leave a Reply") or nl.startswith("Coach Carter |"):
                            break
                        body.append(nl)
                    add(testi, name + date, {"name_as_posted": name, "date": date, "text": " ".join(body)[:1500],
                                             "type": "public blog comment"}, p)
            if "yesmaamnosir" in p["source"]:
                add(testi, p["source"], {"name_as_posted": None, "date": p["timestamp"][:8],
                                         "text": t[:3000], "type": "book-site testimonials page (raw)"}, p)
        # photo album captions
        if "/Photos/" in p["source"]:
            for l in L:
                if re.match(r"\d\d\. ", l) or (p["source"].endswith("photos.html") and "Coach" in l and len(l) < 160 and "[" not in l):
                    add(photos, l, {"caption": l}, p)
        for kw in KW:
            m = re.search(re.escape(kw), t, re.I)
            if m and not (kw == "Prince" and re.search(r"Princeton|princess", t[m.start():m.end() + 3], re.I)):
                ctx = re.sub(r"\s+", " ", t[max(0, m.start() - 160): m.end() + 200])
                add(hits, kw + p["file"], {"keyword": kw, "context": ctx}, p)
    out = {k: list(v.values()) for k, v in
           [("tv_media", tv), ("awards", awards), ("clients", clients), ("speaking", speaking),
            ("testimonials", testi), ("celebrity_photo_captions", photos), ("keyword_hits", hits)]}
    json.dump(out, open(os.path.join(ROOT, "wayback_claims.json"), "w"), indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(f"{k}: {len(v)}")


if __name__ == "__main__":
    main()
