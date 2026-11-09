#!/usr/bin/env python3
"""Fetch full YouTube metadata (no download) + oEmbed embeddability for a list of IDs.

Run: python3 enrich.py ids.txt      (one ID per line; '#' comments allowed)
Writes OUT/meta/<id>.json (cached) and prints a one-line summary per ID.
"""
import json, os, subprocess, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

YTDLP = "/opt/homebrew/bin/yt-dlp"
OUT = "/Users/ralphd/Desktop/COACH_CARTER_PLATFORM/tracking/investigation/meta"
KEEP = ["id", "title", "channel", "channel_id", "channel_url", "uploader", "upload_date", "duration", "view_count",
        "description", "tags", "categories", "webpage_url", "availability", "playable_in_embed", "license"]


def oembed(vid):
    u = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
    try:
        with urllib.request.urlopen(u, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None


def fetch(vid):
    path = os.path.join(OUT, f"{vid}.json")
    if os.path.exists(path):
        return json.load(open(path))
    p = subprocess.run([YTDLP, "-j", "--skip-download", "--no-warnings", "--no-playlist",
                        f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=180)
    m = {"id": vid}
    try:
        d = json.loads(p.stdout.splitlines()[0])
        m.update({k: d.get(k) for k in KEEP})
        m["description"] = (m.get("description") or "")[:1500]
    except Exception:
        m["error"] = (p.stderr or "")[-300:]
    m["oembed_status"] = oembed(vid)
    m["embeddable"] = m["oembed_status"] == 200 and m.get("playable_in_embed") is not False
    json.dump(m, open(path, "w"), indent=1)
    return m


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ids = []
    for line in open(sys.argv[1]):
        line = line.split("#")[0].strip()
        if line and line not in ids:
            ids.append(line)
    with ThreadPoolExecutor(8) as ex:
        for m in ex.map(fetch, ids):
            print(f"{m['id']} | {m.get('upload_date')} | {m.get('channel')} | emb={m['embeddable']}({m['oembed_status']}) "
                  f"| {m.get('title')} || {(m.get('description') or m.get('error') or '')[:260].replace(chr(10),' ')}")
